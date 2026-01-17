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
    
    if args.output:
        try:
            # Try to parse result as JSON if it is a string
            output_data = result
            if isinstance(result, str):
                try:
                    output_data = json.loads(result)
                except json.JSONDecodeError:
                    pass
            
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
