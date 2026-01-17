import json
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from client import K3CloudClient
from config import default_config_path, load_config

# Initialize the MCP server
mcp = FastMCP("k3cloud")


def get_client() -> K3CloudClient:
    """Helper to get initialized client using default config path or environment variables."""
    # This loads from config.ini in src/ or defined by env vars
    cfg = load_config(default_config_path())
    return K3CloudClient(cfg)


@mcp.tool()
def query_inventory(
    form_id: str = "STK_Inventory",
    field_keys: str = "FmaterialID.Fnumber,FmaterialID.FName,FStockID.Fnumber,FStockID.Fname,fbaseqty",
    filter_string: str = "",
    limit: int = 20,
    start_row: int = 0,
) -> str:
    """
    Query inventory data from K3 Cloud.

    Args:
        form_id: The form ID (default: STK_Inventory)
        field_keys: Comma separated fields to return
        filter_string: Filter criteria (e.g. "FStockID.Fnumber='CK001'")
        limit: Number of records to return
        start_row: Start row for pagination
    """
    client = get_client()
    data = {
        "FormId": form_id,
        "FieldKeys": field_keys,
        "FilterString": filter_string,
        "Limit": limit,
        "StartRow": start_row,
        "TopRowCount": 0,
        "OrderString": "",
        "SubSystemId": "",
    }
    result = client.execute_bill_query(data)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def query_bill(
    form_id: str,
    field_keys: str,
    filter_string: str = "",
    limit: int = 20,
    start_row: int = 0,
) -> str:
    """
    General bill query for any form (e.g., BD_MATERIAL, SAL_SaleOrder).

    Args:
        form_id: The form ID (e.g. BD_MATERIAL)
        field_keys: Comma separated fields to return
        filter_string: Filter criteria
        limit: Number of records to return
        start_row: Start row
    """
    client = get_client()
    data = {
        "FormId": form_id,
        "FieldKeys": field_keys,
        "FilterString": filter_string,
        "Limit": limit,
        "StartRow": start_row,
        "TopRowCount": 0,
        "OrderString": "",
        "SubSystemId": "",
    }
    result = client.execute_bill_query(data)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def save_bill(form_id: str, model_json: str) -> str:
    """
    Save a bill/entity.

    Args:
        form_id: The form ID
        model_json: JSON string representing the Model data structure
    """
    client = get_client()
    try:
        model = json.loads(model_json)
    except json.JSONDecodeError:
        return json.dumps({"Result": {"ResponseStatus": {"IsSuccess": False, "Errors": [{"Message": "Invalid JSON in model_json"}]}}})

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
    result = client.save(form_id, data)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def submit_bill(form_id: str, numbers: str) -> str:
    """
    Submit bill(s) by number.

    Args:
        form_id: The form ID
        numbers: Comma separated list of bill numbers
    """
    client = get_client()
    nums = [n.strip() for n in numbers.split(",") if n.strip()]
    data = {
        "CreateOrgId": 0,
        "Numbers": nums,
        "Ids": "",
        "SelectedPostId": 0,
        "NetworkCtrl": "",
        "IgnoreInterationFlag": "",
    }
    result = client.submit(form_id, data)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def audit_bill(form_id: str, numbers: str) -> str:
    """
    Audit (approve) bill(s) by number.

    Args:
        form_id: The form ID
        numbers: Comma separated list of bill numbers
    """
    client = get_client()
    nums = [n.strip() for n in numbers.split(",") if n.strip()]
    data = {
        "CreateOrgId": 0,
        "Numbers": nums,
        "Ids": "",
        "SelectedPostId": 0,
        "NetworkCtrl": "",
        "IgnoreInterationFlag": "",
        "IsVerifyProcInst": "",
    }
    result = client.audit(form_id, data)
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
