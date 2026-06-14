import os
import platform
import sys
from typing import Optional

def get_system_info() -> dict:
    """
    返回系统信息快照。
    { "os": str, "python_version": str, "cpu_count": int, "gpus": list, ... }
    """
    info = {
        "os": platform.platform(),
        "python_version": sys.version,
        "cpu_count": os.cpu_count(),
        "gpus": [],
        "cuda_available": False,
    }
    try:
        import torch
        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            info["gpus"] = [
                {"index": i, "name": torch.cuda.get_device_name(i)}
                for i in range(torch.cuda.device_count())
            ]
    except ImportError:
        pass
    return info
