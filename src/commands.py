import argparse
import json
import time
from typing import Any, Dict
from client import K3CloudClient

COMMAND_HELP_MAP = {
    "inventory": "即时库存",
}

def register_commands(subparsers) -> None:
    # Inventory Query
    parser_inventory = subparsers.add_parser("inventory", help=COMMAND_HELP_MAP["inventory"])
    parser_inventory.add_argument("--form-id", default="STK_Inventory")
    parser_inventory.add_argument(
        "--field-keys",
        default="FmaterialID.Fnumber,FmaterialID.FName,FStockID.Fnumber,FStockID.Fname,fbaseqty,FModel",
    )
    parser_inventory.add_argument("--filter-string", default="fbaseqty > 0")
    parser_inventory.add_argument("--limit", type=int, default=0, help="Limit number of records, 0 for all")
    parser_inventory.add_argument("--top-row-count", type=int, default=0)
    parser_inventory.add_argument("--start-row", type=int, default=0)
    parser_inventory.add_argument("--order-string", default="")
    parser_inventory.set_defaults(handler=cmd_bill_query)

import json
import logging

from logger import get_logger

logger = get_logger(__name__)

def cmd_bill_query(client: K3CloudClient, args: argparse.Namespace) -> Any:
    """
    Generic bill query handler that supports pagination (when limit=0)
    and standard single-page query.
    """
    
    form_id = getattr(args, 'form_id', '')
    
    # Special case: map command names to FormId if not explicitly provided or generic
    if not form_id and hasattr(args, 'command'):
        if args.command == 'material-bill-query' or args.command == 'material-execute-bill-query':
            form_id = 'BD_MATERIAL'
            
    if not form_id:
        # Fallback or error if FormId is missing
        # For 'inventory', form_id is usually set by default in parser
        pass

    # If limit is 0, we imply "fetch all" (using pagination)
    if args.limit <= 0:
        all_results = []
        start_row = args.start_row
        batch_size = 2000 # K3Cloud standard limit
        
        logger.info(f"Fetching all records for {form_id} with filter: {args.filter_string}")
        
        while True:
            data = {
                "FormId": form_id,
                "FieldKeys": args.field_keys,
                "FilterString": args.filter_string,
                "OrderString": getattr(args, 'order_string', ''),
                "TopRowCount": getattr(args, 'top_row_count', 0),
                "StartRow": start_row,
                "Limit": batch_size
            }
            
            result_str = client.bill_query(data)
            
            try:
                batch_result = json.loads(result_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON response: {result_str}")
                if not all_results:
                    return result_str
                break
            
            # Check for error in response structure
            if isinstance(batch_result, dict) and not batch_result.get('Result', {}).get('ResponseStatus', {}).get('IsSuccess', True):
                 if not all_results:
                     return batch_result
                 logger.error(f"Error during pagination: {batch_result}")
                 break

            if isinstance(batch_result, list):
                if not batch_result:
                    break
                all_results.extend(batch_result)
                
                if len(batch_result) < batch_size:
                    break
                
                start_row += batch_size
                logger.info(f"Fetched {len(all_results)} records so far...")
            else:
                if not all_results:
                    return result_str
                break
                
        logger.info(f"Total records fetched: {len(all_results)}")
        return all_results

    # Standard behavior if limit is set
    data = {
        "FormId": form_id,
        "FieldKeys": args.field_keys,
        "FilterString": args.filter_string,
        "OrderString": getattr(args, 'order_string', ''),
        "TopRowCount": getattr(args, 'top_row_count', 0),
        "StartRow": args.start_row,
        "Limit": args.limit,
    }
    return client.bill_query(data)
