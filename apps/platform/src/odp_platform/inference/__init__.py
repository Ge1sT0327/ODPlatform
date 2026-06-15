"""inference 子系统对外公共 API。"""

from odp_platform.inference.service import (
    InferService, InferResult, infer_yolo,
)
from odp_platform.inference.sinks import (
    OutputSink, NullSink, LocalFileSink,
    DisplaySink, SaveVideoSink, NoopSink,
)
from odp_platform.inference.cancel import CancelToken, InferenceCancelled
from odp_platform.inference.hooks import InferHooks, FrameEvent, ProgressEvent
from odp_platform.inference.pipeline import ThreadedPipeline
from odp_platform.inference.pipeline_config import PipelineConfig, load_pipeline_config
from odp_platform.inference.overlay import FPSCounter, Metrics, draw_hud, draw_pause

__all__ = [
    "InferService", "InferResult", "infer_yolo",
    "OutputSink", "NullSink", "LocalFileSink",
    "DisplaySink", "SaveVideoSink", "NoopSink",
    "CancelToken", "InferenceCancelled",
    "InferHooks", "FrameEvent", "ProgressEvent",
    "ThreadedPipeline",
    "PipelineConfig", "load_pipeline_config",
    "FPSCounter", "Metrics", "draw_hud", "draw_pause",
]
