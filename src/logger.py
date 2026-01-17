import logging
import sys
from typing import Optional

def setup_logging(debug: bool = False) -> logging.Logger:
    """
    配置并返回 logger 实例
    
    Args:
        debug: 是否开启调试模式
    """
    level = logging.DEBUG if debug else logging.INFO
    
    # 清除现有的 handlers
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
            
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("k3cloud")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取 logger 实例
    
    Args:
        name: logger 名称，如果不传则返回 root logger
    """
    if name:
        return logging.getLogger(f"k3cloud.{name}")
    return logging.getLogger("k3cloud")
