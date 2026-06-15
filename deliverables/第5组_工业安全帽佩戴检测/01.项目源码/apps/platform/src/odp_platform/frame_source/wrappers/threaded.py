"""后台线程采集包装：采集与处理解耦。"""

import logging
import threading
import queue
from typing import Optional
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.core.types import Frame, SourceType

logger = logging.getLogger(__name__)


class ThreadedSource(FrameSource):
    """
    将底层 FrameSource 的 _read() 放到后台线程执行。
    通过 Queue 传递给主线程，解耦采集与处理。
    max_queue 控制最大缓冲帧数。
    warmup_frames 预热采集帧数（给摄像头自动曝光稳定用）。
    """

    def __init__(self, source: FrameSource, max_queue: int = 32, warmup_frames: int = 0):
        super().__init__()
        self._source = source
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue)
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._warmup = warmup_frames
        if warmup_frames > 0 and hasattr(source, '_open'):
            source._open()
            for _ in range(warmup_frames):
                source._read()

    @property
    def source_type(self) -> SourceType:
        return self._source.source_type

    def _open(self) -> bool:
        if not self._source._open():
            return False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        return True

    def _worker(self) -> None:
        try:
            while not self._stop_event.is_set():
                frame = self._source._read()
                if frame is None:
                    break
                self._queue.put(frame)
        finally:
            self._queue.put(None)  # 哨兵

    def _read(self) -> Optional[Frame]:
        try:
            frame = self._queue.get(timeout=0.1)
            return frame
        except queue.Empty:
            return Frame(image=None)  # 空帧，调用方自行处理

    def _close(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._source._close()


def create_threaded_source(source, camera_config=None, warmup_frames=30):
    """创建线程化帧源 (兼容 teacher 接口)。"""
    from odp_platform.frame_source.factory import create_frame_source
    src = create_frame_source(source, camera_config=camera_config)
    return ThreadedSource(src, warmup_frames=warmup_frames)
