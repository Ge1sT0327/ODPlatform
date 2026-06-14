"""inference 子系统对外公共 API。"""

from odp_platform.inference.service import (
    InferService, InferResult, infer_yolo,
    OutputSink, InferHooks, CancelToken,
)
from odp_platform.inference.sinks import DisplaySink, SaveVideoSink, NoopSink

__all__ = [
    "InferService", "InferResult", "infer_yolo",
    "OutputSink", "InferHooks", "CancelToken",
    "DisplaySink", "SaveVideoSink", "NoopSink",
]
