import argparse
import logging
import os
import sys
from typing import List, Optional

import json
from client import K3CloudClient
import commands
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
                
                # Determine sheet name
                command_name = args.command if hasattr(args, 'command') else 'query'
                sheet_name = commands.COMMAND_HELP_MAP.get(command_name, command_name)
                
                # Determine output filename
                if client.config.excel_file:
                    filename = client.config.excel_file
                    # Ensure directory exists if path contains directory
                    output_dir = os.path.dirname(filename)
                    if output_dir and not os.path.exists(output_dir):
                        try:
                            os.makedirs(output_dir)
                        except Exception:
                            pass
                elif args.output and args.output.endswith('.xlsx'):
                    filename = args.output
                else:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    
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

                # Write to Excel
                if client.config.excel_file and os.path.exists(filename):
                     # Append mode
                     try:
                        with pd.ExcelWriter(filename, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                        logger.info(f"Result appended to Excel: {filename} (Sheet: {sheet_name})")
                     except Exception as e:
                        logger.error(f"Failed to append to Excel file (trying overwrite/create): {e}")
                        # Fallback to write if append fails (e.g. file corrupted or locked?) 
                        # Or maybe just try creating new one? 
                        # Let's try to write as new if it failed, but that might overwrite.
                        # Safe bet: just log error. But if file exists but is not valid excel, maybe we should overwrite?
                        # For now, let's just log.
                else:
                    # Create new file
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    logger.info(f"Result saved to Excel: {filename} (Sheet: {sheet_name})")

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

    if not args.quiet:
        from commands import _print_result
        _print_result(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="k3cloud")
    parser.add_argument("--config", default=os.getenv("K3CLOUD_CONF") or default_config_path())
    parser.add_argument("--section", default=os.getenv("K3CLOUD_SECTION") or "k3cloud")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--output", help="Save output to a JSON file")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")
    subparsers = parser.add_subparsers(dest="command", required=True)
    commands.register_commands(subparsers)
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
