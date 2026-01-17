import json
import logging
from typing import Any, Dict, Optional

from k3cloud_webapi_sdk.main import K3CloudApiSdk

from config import K3CloudConfig
from utils import decode_app_secret

logger = logging.getLogger(__name__)


class K3CloudClient:
    def __init__(self, config: K3CloudConfig):
        self._config = config
        self._sdk = self._init_sdk()

    @property
    def config(self) -> K3CloudConfig:
        return self._config

    @property
    def sdk(self) -> K3CloudApiSdk:
        return self._sdk

    def _init_sdk(self) -> K3CloudApiSdk:
        sdk = K3CloudApiSdk(self._config.server_url)
        
        # Handle potential encrypted app_secret
        app_secret = decode_app_secret(self._config.app_secret)
        
        # Initialize configuration
        # Based on inspection: (self, acct_id, user_name, app_id, app_secret, server_url, lcid=2052, org_num=0, ...)
        try:
            sdk.InitConfig(
                self._config.acct_id,
                self._config.user_name,
                self._config.app_id,
                app_secret,
                self._config.server_url,
                self._config.lcid,
                self._config.org_num,
            )
        except Exception as e:
            logger.error(f"Failed to initialize SDK config: {e}")
            raise

        return sdk

    def execute_bill_query(self, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        return self._sdk.ExecuteBillQuery(data)

    def bill_query(self, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        return self._sdk.ExecuteBillQuery(data)

    def save(self, form_id: str, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        return self._sdk.Save(form_id, data)

    def submit(self, form_id: str, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        return self._sdk.Submit(form_id, data)

    def audit(self, form_id: str, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        return self._sdk.Audit(form_id, data)

    def flex_save(self, form_id: str, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        return self._sdk.FlexSave(form_id, data)
    
    def get_sys_report_data(self, form_id: str, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        if hasattr(self._sdk, "getSysReportData"):
            return self._sdk.getSysReportData(form_id, data)
        return self._sdk.Execute("Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.GetSysReportData", data)

    def execute_service(self, service_full_name: str, data: Dict[str, Any], timeout_s: Optional[float] = None) -> Any:
        return self._sdk.Execute(service_full_name, data)
