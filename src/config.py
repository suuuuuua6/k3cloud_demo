import configparser
import os
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class K3CloudConfig:
    server_url: str
    acct_id: str
    app_id: str
    app_secret: str
    user_name: str
    lcid: int = 2052
    org_num: int = 0


def default_config_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "config.ini")


def _get_case_insensitive(mapping: Dict[str, str], key: str) -> Optional[str]:
    target = key.strip().lower()
    for k, v in mapping.items():
        if k.strip().lower() == target:
            return str(v).strip()
    return None


def load_config(config_path: str, section: str = "k3cloud") -> K3CloudConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")

    parser = configparser.ConfigParser()
    with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
        parser.read_file(f)

    if section not in parser:
        raise RuntimeError(f"配置节点不存在: {section}")

    raw = dict(parser[section])

    server_url = _get_case_insensitive(raw, "server_url") or _get_case_insensitive(
        raw, "X-KDApi-ServerUrl"
    )
    acct_id = _get_case_insensitive(raw, "acct_id") or _get_case_insensitive(raw, "X-KDApi-AcctID")
    app_id = _get_case_insensitive(raw, "app_id") or _get_case_insensitive(raw, "X-KDApi-AppID")
    app_secret = (
        _get_case_insensitive(raw, "app_secret")
        or _get_case_insensitive(raw, "app_sec")
        or _get_case_insensitive(raw, "X-KDApi-AppSec")
    )
    user_name = _get_case_insensitive(raw, "user_name") or _get_case_insensitive(
        raw, "X-KDApi-UserName"
    )
    lcid_raw = _get_case_insensitive(raw, "lcid") or _get_case_insensitive(raw, "X-KDApi-LCID") or "2052"
    org_num_raw = _get_case_insensitive(raw, "org_num") or _get_case_insensitive(raw, "X-KDApi-OrgNum") or "0"

    missing = []
    if not server_url: missing.append("server_url")
    if not acct_id: missing.append("acct_id")
    if not app_id: missing.append("app_id")
    if not app_secret: missing.append("app_secret")
    if not user_name: missing.append("user_name")

    if missing:
        raise RuntimeError(f"配置缺少字段: {', '.join(missing)}")

    try:
        lcid = int(lcid_raw) # type: ignore
    except Exception as e:
        raise RuntimeError("lcid 必须是整数") from e

    try:
        org_num = int(org_num_raw)
    except Exception as e:
        raise RuntimeError("org_num 必须是整数") from e

    return K3CloudConfig(
        server_url=server_url, # type: ignore
        acct_id=acct_id, # type: ignore
        app_id=app_id, # type: ignore
        app_secret=app_secret, # type: ignore
        user_name=user_name, # type: ignore
        lcid=lcid,
        org_num=org_num,
    )
