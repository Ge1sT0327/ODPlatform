"""图片源：单图片 → 单帧、图片目录 → 多帧。"""

from pathlib import Path
from typing import Optional, List
import cv2
import numpy as np
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.core.types import Frame, FrameInfo, SourceType
from odp_platform.frame_source.constants import IMAGE_EXTENSIONS

class ImageSource(FrameSource):
    """单图片源：只产出一帧。"""

    def __init__(self, path: str | Path):
        super().__init__()
        self.path = Path(path)
        self._image: Optional[np.ndarray] = None
        self._consumed = False

    @property
    def source_type(self) -> SourceType:
        return SourceType.IMAGE

    def _open(self) -> bool:
        if not self.path.exists():
            raise ValueError(f"图片不存在: {self.path}")
        self._image = cv2.imread(str(self.path))
        return self._image is not None

    def _read(self) -> Optional[Frame]:
        if self._consumed or self._image is None:
            return None
        self._consumed = True
        h, w = self._image.shape[:2]
        return Frame(
            image=self._image.copy(),
            info=FrameInfo(original_width=w, original_height=h, source_type=SourceType.IMAGE),
        )

    def _close(self) -> None:
        self._image = None

class ImageFolderSource(FrameSource):
    """图片目录源：遍历目录下所有图片，每张一帧。"""

    def __init__(self, path: str | Path):
        super().__init__()
        self.path = Path(path)
        self._files: List[Path] = []
        self._idx = 0

    @property
    def source_type(self) -> SourceType:
        return SourceType.IMAGE_FOLDER

    def _open(self) -> bool:
        if not self.path.is_dir():
            raise ValueError(f"目录不存在: {self.path}")
        self._files = sorted(
            f for f in self.path.iterdir()
            if f.suffix.lower() in IMAGE_EXTENSIONS
        )
        if not self._files:
            raise ValueError(f"目录中无图片: {self.path}")
        return True

    def _read(self) -> Optional[Frame]:
        if self._idx >= len(self._files):
            return None
        img = cv2.imread(str(self._files[self._idx]))
        self._idx += 1
        if img is None:
            return self._read()  # 跳过损坏图片
        h, w = img.shape[:2]
        return Frame(
            image=img,
            info=FrameInfo(original_width=w, original_height=h, source_type=SourceType.IMAGE_FOLDER),
        )

    def _close(self) -> None:
        self._files.clear()
        self._idx = 0
