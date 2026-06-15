"""异步迭代器包装。"""

import asyncio
from typing import Optional
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.core.types import Frame, SourceType

class AsyncSource:
    """将 FrameSource 包装为 async iterator。"""

    def __init__(self, source: FrameSource):
        self._source = source
        self._opened = False

    @property
    def source_type(self) -> SourceType:
        return self._source.source_type

    async def __aenter__(self):
        self._opened = self._source._open()
        if not self._opened:
            raise RuntimeError(f"帧源打开失败")
        return self

    async def __aexit__(self, *args):
        self._source._close()
        self._opened = False

    async def __aiter__(self):
        return self

    async def __anext__(self) -> Frame:
        frame = await asyncio.to_thread(self._source._read)
        if frame is None:
            raise StopAsyncIteration
        return frame
