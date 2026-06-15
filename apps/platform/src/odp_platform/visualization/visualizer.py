"""检测结果绘制：边界框 + 中文标签 + 置信度 + 霞鹜文楷字体。零宿主依赖。"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import cv2
import pathlib
import logging

logger = logging.getLogger(__name__)

@dataclass
class DrawStyle:
    """绘制样式。"""
    box_thickness: int = 2
    font_scale: float = 0.6
    text_color: Tuple[int, int, int] = (255, 255, 255)
    bg_color: Tuple[int, int, int] = (0, 0, 0)
    bg_alpha: float = 0.6
    palette: List[Tuple[int, int, int]] = None

    def __post_init__(self):
        if self.palette is None:
            self.palette = [
                (0, 255, 0),     # 绿色
                (0, 0, 255),     # 红色
                (255, 255, 0),   # 青色
                (255, 0, 255),   # 品红
                (0, 255, 255),   # 黄色
                (255, 128, 0),   # 橙色
                (128, 0, 255),   # 紫色
                (0, 128, 255),   # 天蓝
            ]

    def get_color(self, class_id: int) -> Tuple[int, int, int]:
        return self.palette[class_id % len(self.palette)]

@dataclass
class Detection:
    """检测结果。"""
    bbox: Tuple[float, float, float, float]
    class_id: int
    class_name: str
    confidence: float


def _resolve_bundled_font(font_path: str = None) -> Optional[str]:
    """返回已存在的字体文件路径。优先用户指定 > 捆绑字体 > 系统字体。"""
    if font_path and pathlib.Path(font_path).exists():
        return font_path
    bundled = pathlib.Path(__file__).resolve().parent / "assets" / "LXGWWenKai-Bold.ttf"
    if bundled.exists():
        return str(bundled)
    for sys_font in [
        "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]:
        if pathlib.Path(sys_font).exists():
            return sys_font
    return None


class BeautifyVisualizer:
    """
    在 BGR 图像上绘制检测结果。
    优先使用捆绑的霞鹜文楷字体渲染中文标签（Pillow），回退到 OpenCV。
    零宿主依赖——不 import odp_platform.*。
    """

    def __init__(self, class_names=None, labels=None, style=None,
                 label_mapping=None, color_mapping=None,
                 default_color=(180,180,180), font_path=None):
        names = class_names or labels or ['unknown']
        self.class_names = names
        self._cached_names = names if isinstance(names, (list, tuple)) else list(names) if hasattr(names, 'values') else ['unknown']
        self.label_mapping = label_mapping or {}
        self.color_mapping = color_mapping or {}
        self.default_color = default_color
        self.style = style or DrawStyle()
        self.font_path = font_path
        self._pil_available = False
        self._font = None
        try:
            from PIL import ImageFont, ImageDraw, Image
            self._pil_available = True
            resolved = _resolve_bundled_font(font_path)
            if resolved:
                self.font_path = resolved
        except ImportError:
            pass
    @classmethod
    def from_yolo_results(cls, boxes, confidences, labels, color_mapping=None):
        """从 YOLO 推理结果构造 Detection 列表 (兼容 teacher 接口)。"""
        detections = []
        for i in range(len(boxes)):
            name = labels[i] if i < len(labels) else 'unknown'
            detections.append(Detection(
                bbox=tuple(boxes[i].tolist()),
                class_name=name,
                class_id=i,
                confidence=float(confidences[i]),
            ))
        return detections

    def draw(self, image: np.ndarray, detections: List[Detection], style=None, use_label_mapping: bool = True) -> np.ndarray:
        """在 image 上绘制所有检测结果（原地修改 + 返回）。"""
        h, w = image.shape[:2]
        s = style or self.style
        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            color = self.color_mapping.get(det.class_name, s.get_color(det.class_id))
            # 边界框
            cv2.rectangle(image, (x1, y1), (x2, y2), color, s.box_thickness)
            # 标签 — 支持中文映射
            label_name = self.label_mapping.get(det.class_name, det.class_name) if use_label_mapping and self.label_mapping else det.class_name
            label = f"{label_name} {det.confidence:.2f}"
            self._draw_label(image, label, x1, y1 - 4, color)
        return image

    def _draw_label(self, image: np.ndarray, label: str, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """在 (x,y) 上方绘制带背景的标签。支持 CJK。"""
        if self._pil_available:
            self._draw_label_pil(image, label, x, y, color)
        else:
            # 回退：OpenCV 原生（不支持中文）
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, self.style.font_scale, 1)
            y1 = max(y - th - 4, 0)
            cv2.rectangle(image, (x, y1), (x + tw + 4, y1 + th + 4), self.style.bg_color, -1)
            cv2.putText(image, label, (x + 2, y1 + th + 2),
                       cv2.FONT_HERSHEY_SIMPLEX, self.style.font_scale, self.style.text_color, 1)

    def _draw_label_pil(self, image: np.ndarray, label: str, x: int, y: int,
                        color: Tuple[int, int, int]) -> None:
        """使用 Pillow + 捆绑字体渲染标签（支持中文）。"""
        from PIL import ImageFont, ImageDraw, Image

        # 字体缓存：首次加载，后续复用
        if self._font is None:
            resolved = self.font_path or _resolve_bundled_font()
            if resolved:
                try:
                    self._font = ImageFont.truetype(resolved, 16)
                except (OSError, IOError):
                    self._font = ImageFont.load_default()
            else:
                self._font = ImageFont.load_default()

        font = self._font
        # 文本尺寸
        temp_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(temp_img)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # 半透明背景块
        y1 = max(y - th - 4, 0)
        y2 = min(y1 + th + 4, image.shape[0] - 1)
        x2 = min(x + tw + 6, image.shape[1] - 1)
        x1 = max(x, 0)
        sub = image[y1:y2, x1:x2].astype(np.float32)
        overlay = np.full_like(sub, color, dtype=np.float32)  # 用检测框颜色做背景
        blended = (sub * 0.4 + overlay * 0.6).astype(np.uint8)
        image[y1:y2, x1:x2] = blended

        # Pillow 绘制文字 (全程不转换颜色空间)
        pil_img = Image.fromarray(image)
        pil_draw = ImageDraw.Draw(pil_img)
        text_color_rgb = tuple(int(c) for c in (255, 255, 255))  # 白字
        pil_draw.text((x + 2, y1 + 1), label, font=font, fill=text_color_rgb)
        image[:] = np.array(pil_img)
