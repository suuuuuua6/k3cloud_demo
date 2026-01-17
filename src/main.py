import argparse
import logging
import os
import sys
from typing import List, Optional

import json
from client import K3CloudClient
from commands import register_commands
from config import default_config_path, load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_command(client: K3CloudClient, args: argparse.Namespace) -> int:
    if not hasattr(args, "handler"):
        raise RuntimeError("未选择命令")
    result = args.handler(client, args)
    
    # Parse result data
    output_data = result
    if isinstance(result, str):
        try:
            output_data = json.loads(result)
        except json.JSONDecodeError:
            pass

    # Automatic Excel Export for List data (Query results)
    # Check if it's a list of dictionaries OR a list of lists (typical query result)
    if isinstance(output_data, list) and len(output_data) > 0:
        is_list_of_dicts = isinstance(output_data[0], dict)
        is_list_of_lists = isinstance(output_data[0], list)
        
        if is_list_of_dicts or is_list_of_lists:
            try:
                import pandas as pd
                import time
                
                # Use provided output filename or generate one
                if args.output and args.output.endswith('.xlsx'):
                    filename = args.output
                else:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    command_name = args.command if hasattr(args, 'command') else 'query'
                    
                    # Determine output directory
                    # Default to 'excel' subdirectory in project root, or current directory
                    # Project root assumption: parent of src (where main.py is)
                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    output_dir = os.path.join(project_root, 'excel')
                    
                    # Ensure directory exists
                    if not os.path.exists(output_dir):
                        try:
                            os.makedirs(output_dir)
                        except Exception:
                            # Fallback to current directory if creation fails
                            output_dir = os.getcwd()
                    
                    filename = os.path.join(output_dir, f"{command_name}_{timestamp}.xlsx")
                
                if is_list_of_dicts:
                    df = pd.DataFrame(output_data)
                else:
                    # It is list of lists, try to find headers from args
                    columns = None
                    if hasattr(args, 'field_keys') and args.field_keys:
                        # Split keys by comma and clean up
                        columns = [k.strip() for k in args.field_keys.split(',') if k.strip()]
                        
                        # Handle case where field_keys might not match column count exactly
                        # But typically for K3Cloud ExecuteBillQuery, they match.
                        # If mismatch, pandas handles it (either ignores extra names or creates NaN for missing)
                        
                    df = pd.DataFrame(output_data, columns=columns)

                # index=False: Do not write row numbers
                # startrow=0: Header at row 0 (Excel line 1), Data starts at row 1 (Excel line 2)
                df.to_excel(filename, index=False)
                logger.info(f"Result automatically saved to Excel: {filename}")
            except ImportError:
                logger.warning("pandas or openpyxl not installed. Skipping automatic Excel export.")
            except Exception as e:
                logger.error(f"Failed to save Excel file: {e}")

    # Manual output to JSON (only if --output is specified and not .xlsx)
    if args.output and not args.output.endswith('.xlsx'):
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Result saved to {args.output}")
        except Exception as e:
            logger.error(f"Failed to save output to file: {e}")

    from commands import _print_result
    _print_result(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="k3cloud")
    parser.add_argument("--config", default=os.getenv("K3CLOUD_CONF") or default_config_path())
    parser.add_argument("--section", default=os.getenv("K3CLOUD_SECTION") or "k3cloud")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--output", help="Save output to a JSON file")
    subparsers = parser.add_subparsers(dest="command", required=True)
    register_commands(subparsers)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        cfg = load_config(args.config, args.section)
        client = K3CloudClient(cfg)
        return run_command(client, args)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            logger.exception("Traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
