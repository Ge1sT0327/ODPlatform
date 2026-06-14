"""内置 OutputSink 实现。"""

import cv2
from pathlib import Path
from datetime import datetime
from odp_platform.inference.service import OutputSink
from odp_platform.frame_source.core.types import Frame

class DisplaySink(OutputSink):
    """cv2.imshow 实时显示。"""
    def __init__(self, window_name: str = "ODPlatform Inference"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def consume(self, frame: Frame, detections: list) -> None:
        # 假定 frame.image 已有绘制内容（由 visualize 绘制或此处做最简绘制）
        cv2.imshow(self.window_name, frame.image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            raise KeyboardInterrupt("用户按 q 退出")
        if key == ord(" "):  # 空格暂停
            cv2.waitKey(0)

    def close(self) -> None:
        cv2.destroyWindow(self.window_name)

class SaveVideoSink(OutputSink):
    """保存输出为视频文件。"""
    def __init__(self, output_path: str = None, fps: float = 30.0):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = Path(output_path or f"output_{ts}.mp4")
        self.fps = fps
        self._writer = None

    def consume(self, frame: Frame, detections: list) -> None:
        if self._writer is None:
            h, w = frame.image.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self._writer = cv2.VideoWriter(str(self.output_path), fourcc, self.fps, (w, h))
        self._writer.write(frame.image)

    def close(self) -> None:
        if self._writer is not None:
            self._writer.release()

class NoopSink(OutputSink):
    """不做任何输出（纯推理基准测试用）。"""
    def consume(self, frame: Frame, detections: list) -> None:
        pass

    def close(self) -> None:
        pass
