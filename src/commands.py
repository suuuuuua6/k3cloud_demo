import argparse
import json
import time
from typing import Any, Dict

from client import K3CloudClient


def _print_result(value: Any) -> None:
    if isinstance(value, str):
        try:
            obj = json.loads(value)
            print(json.dumps(obj, ensure_ascii=False, indent=2))
            return
        except Exception:
            print(value)
            return
    print(json.dumps(value, ensure_ascii=False, indent=2))


def register_commands(subparsers) -> None:
    # Inventory Query
    parser_inventory = subparsers.add_parser("inventory", help="查询库存")
    parser_inventory.add_argument("--form-id", default="STK_Inventory")
    parser_inventory.add_argument(
        "--field-keys",
        default="FmaterialID.Fnumber,FmaterialID.FName,FStockID.Fnumber,FStockID.Fname,fbaseqty",
    )
    parser_inventory.add_argument("--filter-string", default="FStockID.Fnumber='CK0201'")
    parser_inventory.add_argument("--limit", type=int, default=2)
    parser_inventory.add_argument("--top-row-count", type=int, default=0)
    parser_inventory.add_argument("--start-row", type=int, default=0)
    parser_inventory.add_argument("--order-string", default="")
    parser_inventory.add_argument("--subsystem-id", default="")
    parser_inventory.add_argument("--timeout-s", type=float, default=0)
    parser_inventory.set_defaults(handler=cmd_inventory_execute_bill_query)

    # Material Execute Bill Query
    parser_mat_query = subparsers.add_parser("material-execute-bill-query", help="物料单据查询")
    parser_mat_query.add_argument("--field-keys", default="FName,FNumber")
    parser_mat_query.add_argument("--filter-string", default="FNumber=''")
    parser_mat_query.add_argument("--top-row-count", type=int, default=100)
    parser_mat_query.add_argument("--start-row", type=int, default=0)
    parser_mat_query.add_argument("--limit", type=int, default=2000)
    parser_mat_query.set_defaults(handler=cmd_material_execute_bill_query)

    # Material Bill Query
    parser_mat_bill = subparsers.add_parser("material-bill-query", help="物料查询")
    parser_mat_bill.add_argument("--field-keys", default="FName,FNumber,FCreateOrgId,FUseOrgId,")
    parser_mat_bill.add_argument("--filter-string", default="FNumber=''")
    parser_mat_bill.add_argument("--top-row-count", type=int, default=100)
    parser_mat_bill.add_argument("--start-row", type=int, default=0)
    parser_mat_bill.add_argument("--limit", type=int, default=2000)
    parser_mat_bill.set_defaults(handler=cmd_material_bill_query)

    # Material Save
    parser_mat_save = subparsers.add_parser("material-save", help="保存物料")
    parser_mat_save.add_argument("--number", default="")
    parser_mat_save.add_argument("--name", default="")
    parser_mat_save.add_argument("--create-org-number", default=100, type=int)
    parser_mat_save.add_argument("--use-org-number", default=100, type=int)
    parser_mat_save.set_defaults(handler=cmd_material_save)

    # Material Submit
    parser_mat_submit = subparsers.add_parser("material-submit", help="提交物料")
    parser_mat_submit.add_argument("--number", required=True)
    parser_mat_submit.set_defaults(handler=cmd_material_submit)

    # Material Audit
    parser_mat_audit = subparsers.add_parser("material-audit", help="审核物料")
    parser_mat_audit.add_argument("--number", required=True)
    parser_mat_audit.set_defaults(handler=cmd_material_audit)

    # Material Flex Save
    parser_mat_flex = subparsers.add_parser("material-flex-save", help="保存核算维度")
    parser_mat_flex.add_argument("--number", required=True)
    parser_mat_flex.set_defaults(handler=cmd_material_flex_save)

    # GL Account Balance
    parser_gl = subparsers.add_parser("gl-accountbalance", help="科目余额表查询")
    parser_gl.add_argument("--scheme-id", default="97ffa1271acc4846b209ea05ac8dec9c")
    parser_gl.add_argument(
        "--field-keys",
        default="FBALANCEID,FBALANCENAME,FACCTTYPE,FACCTGROUP,FDETAILNUMBER,FDETAILNAME,FCyName",
    )
    parser_gl.add_argument("--start-row", type=int, default=0)
    parser_gl.add_argument("--limit", type=int, default=2000)
    parser_gl.add_argument("--acctbook-number", default="001")
    parser_gl.add_argument("--currency", default="1")
    parser_gl.add_argument("--start-year", default="2021")
    parser_gl.add_argument("--start-period", default="12")
    parser_gl.add_argument("--end-year", default="2021")
    parser_gl.add_argument("--end-period", default="12")
    parser_gl.add_argument("--balance-level", default="1")
    parser_gl.set_defaults(handler=cmd_gl_account_balance)

    # Stock Report
    parser_stock = subparsers.add_parser("stock-report", help="库存报表查询")
    parser_stock.add_argument("--form-id", default="STK_StockQueryRpt")
    parser_stock.add_argument("--scheme-id", default="6760e3871be1c2")
    parser_stock.add_argument("--start-row", type=int, default=0)
    parser_stock.add_argument("--limit", type=int, default=2000)
    parser_stock.set_defaults(handler=cmd_stock_report)

    # Generic Execute
    parser_exec = subparsers.add_parser("execute", help="执行任意服务")
    parser_exec.add_argument("--service-url", required=True)
    parser_exec.add_argument("--payload-json", default="")
    parser_exec.set_defaults(handler=cmd_execute)


def run_command(client: K3CloudClient, args: argparse.Namespace) -> int:
    if not hasattr(args, "handler"):
        raise RuntimeError("未选择命令")
    result = args.handler(client, args)
    _print_result(result)
    return 0


def cmd_inventory_execute_bill_query(client: K3CloudClient, args: argparse.Namespace) -> Dict[str, Any]:
    timeout_s = args.timeout_s if args.timeout_s and args.timeout_s > 0 else None
    data = {
        "FormId": args.form_id,
        "FieldKeys": args.field_keys,
        "FilterString": args.filter_string,
        "OrderString": args.order_string,
        "TopRowCount": args.top_row_count,
        "StartRow": args.start_row,
        "Limit": args.limit,
        "SubSystemId": args.subsystem_id,
    }
    return client.execute_bill_query(data, timeout_s=timeout_s)


def cmd_material_execute_bill_query(client: K3CloudClient, args: argparse.Namespace) -> str:
    data = {
        "FormId": "BD_MATERIAL",
        "FieldKeys": args.field_keys,
        "FilterString": args.filter_string,
        "OrderString": "",
        "TopRowCount": args.top_row_count,
        "StartRow": args.start_row,
        "Limit": args.limit,
        "SubSystemId": "",
    }
    return client.execute_bill_query(data)


def cmd_material_bill_query(client: K3CloudClient, args: argparse.Namespace) -> str:
    data = {
        "FormId": "BD_MATERIAL",
        "FieldKeys": args.field_keys,
        "FilterString": args.filter_string,
        "OrderString": "",
        "TopRowCount": args.top_row_count,
        "StartRow": args.start_row,
        "Limit": args.limit,
        "SubSystemId": "",
    }
    return client.bill_query(data)


def cmd_material_save(client: K3CloudClient, args: argparse.Namespace) -> str:
    current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    number = args.number or f"xtwl{current_time}10001"
    name = args.name or f"物料名称{current_time}10001"
    model = {
        "FCreateOrgId": {"FNumber": args.create_org_number},
        "FUserOrgId": {"FNumber": args.use_org_number},
        "FNumber": number,
        "FName": name,
    }
    data = {
        "NeedUpDateFields": [],
        "NeedReturnFields": [],
        "IsDeleteEntry": "True",
        "SubSystemId": "",
        "IsVerifyBaseDataField": "False",
        "IsEntryBatchFill": "True",
        "ValidateFlag": "True",
        "NumberSearch": "True",
        "IsAutoAdjustField": "False",
        "InterationFlags": "",
        "IgnoreInterationFlag": "",
        "IsControlPrecision": "False",
        "Model": model,
    }
    return client.save("BD_Material", data)


def cmd_material_submit(client: K3CloudClient, args: argparse.Namespace) -> str:
    data = {
        "CreateOrgId": 0,
        "Numbers": [args.number],
        "Ids": "",
        "SelectedPostId": 0,
        "NetworkCtrl": "",
        "IgnoreInterationFlag": "",
    }
    return client.submit("BD_Material", data)


def cmd_material_audit(client: K3CloudClient, args: argparse.Namespace) -> str:
    data = {
        "CreateOrgId": 0,
        "Numbers": [args.number],
        "Ids": "",
        "SelectedPostId": 0,
        "NetworkCtrl": "",
        "IgnoreInterationFlag": "",
        "IsVerifyProcInst": "",
    }
    return client.audit("BD_Material", data)


def cmd_material_flex_save(client: K3CloudClient, args: argparse.Namespace) -> str:
    data = {"Model": [{"FFLEX8": {"FNumber": args.number}}]}
    return client.flex_save("BD_FLEXITEMDETAILV", data)


def cmd_gl_account_balance(client: K3CloudClient, args: argparse.Namespace) -> str:
    data = {
        "FieldKeys": args.field_keys,
        "SchemeId": args.scheme_id,
        "StartRow": args.start_row,
        "Limit": args.limit,
        "IsVerifyBaseDataField": "false",
        "Model": {
            "FACCTBOOKID": {"FNumber": args.acctbook_number},
            "FCURRENCY": args.currency,
            "FSTARTYEAR": args.start_year,
            "FSTARTPERIOD": args.start_period,
            "FENDYEAR": args.end_year,
            "FBALANCELEVEL": args.balance_level,
            "FENDPERIOD": args.end_period,
            "FFORBIDBALANCE": True,
            "FBALANCEZERO": True,
            "FPERIODNOBALANCE": True,
            "FYEARNOBALANCE": True,
        },
        "PkEntryIds": [],
    }
    return client.get_sys_report_data("GL_RPT_AccountBalance", data)


def cmd_stock_report(client: K3CloudClient, args: argparse.Namespace) -> str:
    data = {
        "parameters": [
            {
                "FORMID": args.form_id,
                "FSCHEMEID": args.scheme_id,
                "StartRow": str(args.start_row),
                "Limit": str(args.limit),
                "CurQueryId": "",
                "FieldKeys": "",
            }
        ]
    }
    # Explicit service URL from original code
    url = "Kingdee.K3.SCM.WebApi.ServicesStub.StockReportQueryService.GetReportData"
    return client.execute_service(url, data)


def cmd_execute(client: K3CloudClient, args: argparse.Namespace) -> str:
    payload = json.loads(args.payload_json) if args.payload_json else {}
    return client.execute_service(args.service_url, payload)
