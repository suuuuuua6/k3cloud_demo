import argparse
import json
import time
from typing import Any, Dict
from client import K3CloudClient
from logger import get_logger

COMMAND_HELP_MAP = {
    "inventory": "即时库存",
    "purchase-order":"采购订单",
    "purchase-in":"采购入库单",
    "sales-order":"销售订单",
    "sales-out":"销售出库单",
}

def register_commands(subparsers) -> None:
    # Inventory Query
    parser_inventory = subparsers.add_parser("inventory", help=COMMAND_HELP_MAP["inventory"])
    parser_inventory.add_argument("--form-id", default="STK_Inventory")
    parser_inventory.add_argument(
        "--field-keys",
        default="FProjectNo,FMtoNo,FOwnerName,FOwnerid,FKeeperId,FStockOrgid,FBaseUnitId,FSecUnitId,FStockUnitId,FStoreurNum,FStoreurNom,FLot,FLotProduceDate,FKFPeriod,FLockQty,FSecLockQty,FBaseQty,FQty,FBaseLockQty,FProduceDate,FAuxPropId,FStockStatusId,FSecQty,FLotExpiryDate,FExpiryDate,FBomId,FKFPeriodUnit,FUnitRoundType,FBaseProperty,FAVBQty,FBaseAVBQty,FSecAVBQty,FKeeperName,FKeeperTypeId,FOwnerTypeId,FModel,FStockId,FMaterialid,FCMKBarcode,FMaterialName,FStockLocId,FStockName,FUpdateTime,F_ora_BaseProperty",
    )
    parser_inventory.add_argument("--filter-string", default="fbaseqty > 0")
    parser_inventory.add_argument("--limit", type=int, default=0, help="Limit number of records, 0 for all")
    parser_inventory.set_defaults(handler=cmd_bill_query)

    # Purchase Order Query
    parser_purchase_order = subparsers.add_parser("purchase-order", help=COMMAND_HELP_MAP["purchase-order"])
    parser_purchase_order.add_argument("--form-id", default="PUR_PurchaseOrder")
    parser_purchase_order.add_argument(
        "--field-keys",
        default="FBillTypeID,FBillNo,FBusinessType,FDate,FSupplierId,FDocumentStatus,FPurchaseOrgid,FPurchaseDeptId,FPurchaserGroupId,FPurchaserid,FProviderId,FProviderContactId,FProviderJob,FProviderPhone,FProviderAddress,FSettleId,FChargeId,FCreatorId,FCreateDate,FModifierId,FModifyDate,FApproverId,FApproveDate,FMaterialId,FMaterialName,FQty,FPrice,FAmount",
    )
    parser_purchase_order.add_argument("--filter-string", default="")
    parser_purchase_order.add_argument("--limit", type=int, default=0, help="Limit number of records, 0 for all")
    parser_purchase_order.set_defaults(handler=cmd_bill_query)

    # Purchase In Query
    parser_purchase_in = subparsers.add_parser("purchase-in", help=COMMAND_HELP_MAP["purchase-in"])
    parser_purchase_in.add_argument("--form-id", default="STK_InStock")
    parser_purchase_in.add_argument(
        "--field-keys",
        default="FBillTypeID,FBusinessType,FBillNo,FDate,FDocumentStatus,FStockOrgId,FStockDeptId,FStockerGroupId,FStockerId,FDemandOrgId,FPurchaseOrgId,FTransferBizType,FCorrespondOrgId,FPurchaseDeptId,FPurchaserGroupId,FPurchaserId,FSupplierId,FDeliveryBill,FAPSTATUS,FSupplyId,FSupplyContact,FSupplyAddress,FSettleId,FChargeId,FOwnerTypeIdHead,FOwnerIdHead,FCreatorId,FCreateDate,FModifierId,FModifyDate,FApproverId,FApproveDate",
    )
    parser_purchase_in.add_argument("--filter-string", default="")
    parser_purchase_in.add_argument("--limit", type=int, default=0, help="Limit number of records, 0 for all")
    parser_purchase_in.set_defaults(handler=cmd_bill_query)

    # Sales Order Query
    parser_sales_order = subparsers.add_parser("sales-order", help=COMMAND_HELP_MAP["sales-order"])
    parser_sales_order.add_argument("--form-id", default="SAL_SaleOrder")
    parser_sales_order.add_argument(
        "--field-keys",
        default="FDate,FCorrespondOrgid,FBillTypeID,FBillNo,FBusinessType,FDocumentStatus,FCustId,FHeadDeliveryWay,FHEADLOCID,FSaleOrgId,FSaleDeptId,FSaleGroupId,FSalerId,FReceiveId,F_Rz_KaiFa,FReceiveContact,FSettleId,FLinkMan,FReceiveAddress,FChargeId,FLinkPhone,FCreditCheckResult,FCreatorId,FCreateDate,FModifierId,FModifyDate,FApproverId,FApproveDate,FUnitID,FQty,F_Rz_Jskc,FPriceUnitId,FPriceUnitQty,FBomId,FPrice",
    )
    parser_sales_order.add_argument("--filter-string", default="")
    parser_sales_order.add_argument("--limit", type=int, default=0, help="Limit number of records, 0 for all")
    parser_sales_order.set_defaults(handler=cmd_bill_query)

    # Sales out Query
    parser_sales_out = subparsers.add_parser("sales-out", help=COMMAND_HELP_MAP["sales-out"])
    parser_sales_out.add_argument("--form-id", default="SAL_OUTSTOCK")
    parser_sales_out.add_argument(
        "--field-keys",
        default="FDate,FBillNo,FCustomerID,F_Rz_BaseProperty,FStockOrgId,FDocumentStatus,FBillTypeID,FSaleOrgId,FBranchId,FSaleDeptID,FNote,FReceiverID,FReceiverContactID,FLinkPhone,FReceiveAddress,FSettleID,FPayerID,FTransferBizType,FCorrespondOrgId,FCreatorId,FCreateDate,FBillTaxAmount,FBillAmount,FBillAllAmount,FExchangeTypeID,FExchangeRate,FIsIncludedTax,FBillTaxAmount_LC,FBillAmount_LC,FBillAllAmount_LC,FBillCostAmount,FBillCostAmount_LC,FSETTLECustomerID,FOwnerSupplierID,FISGENFORIOS,FCustMatID,FCustMatName,FMaterialID,FMaterialName,FMateriaModel,FEntryTaxAmount,FAmount,FAllAmount,FSalCostPrice,FCostPrice",
    )
    parser_sales_out.add_argument("--filter-string", default="")
    parser_sales_out.add_argument("--limit", type=int, default=0, help="Limit number of records, 0 for all")
    parser_sales_out.set_defaults(handler=cmd_bill_query)


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
        "Limit": args.limit,
    }
    return client.bill_query(data)
