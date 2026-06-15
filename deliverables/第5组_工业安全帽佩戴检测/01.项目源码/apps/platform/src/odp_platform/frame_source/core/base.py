"""FrameSource 抽象基类：迭代器 + 上下文管理器。"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional
from odp_platform.frame_source.core.types import Frame, FrameInfo, SourceType

class FrameSource(ABC, Iterator[Frame]):
    """
    统一帧源抽象。
    既是迭代器（for frame in source），也是上下文管理器（with）。
    子类必须实现: _open(), _read(), _close(), source_type 属性。
    """

    def __init__(self):
        self._opened = False
        self._frame_index = 0

    @property
    @abstractmethod
    def source_type(self) -> SourceType: ...

    @abstractmethod
    def _open(self) -> bool: ...

    @abstractmethod
    def _read(self) -> Optional[Frame]: ...

    @abstractmethod
    def _close(self) -> None: ...

    def __enter__(self):
        self._opened = self._open()
        if not self._opened:
            raise RuntimeError(f"帧源打开失败: {self}")
        self._frame_index = 0
        return self

    def __exit__(self, *args):
        self._close()
        self._opened = False
        return False

    def __next__(self) -> Frame:
        if not self._opened:
            raise StopIteration("帧源未打开")
        frame = self._read()
        if frame is None:
            self._close()
            self._opened = False
            raise StopIteration
        if frame.info.frame_index == 0:
            frame.info = FrameInfo(
                frame_index=self._frame_index,
                timestamp=frame.info.timestamp,
                source_type=self.source_type,
                original_width=frame.info.original_width,
                original_height=frame.info.original_height,
            )
        self._frame_index += 1
        return frame
