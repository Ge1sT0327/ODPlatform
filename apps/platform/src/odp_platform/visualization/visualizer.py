"""检测结果绘制：边界框 + 中文标签 + 置信度。零宿主依赖。"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import cv2

@dataclass
class DrawStyle:
    """绘制样式。"""
    box_thickness: int = 2
    font_scale: float = 0.6
    text_color: Tuple[int, int, int] = (255, 255, 255)
    bg_color: Tuple[int, int, int] = (0, 0, 0)
    bg_alpha: float = 0.6
    # 预定义颜色表（按 class_id 索引）
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
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2)
    class_id: int
    class_name: str
    confidence: float

class BeautifyVisualizer:
    """
    在 BGR 图像上绘制检测结果。
    中文标签使用 Pillow 渲染（若不可用则回退到英文）。
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
        try:
            from PIL import ImageFont, ImageDraw, Image
            self._pil_available = True
        except ImportError:
            pass
    def draw(self, image: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """在 image 上绘制所有检测结果（原地修改 + 返回）。"""
        h, w = image.shape[:2]
        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            color = self.style.get_color(det.class_id)
            # 边界框
            cv2.rectangle(image, (x1, y1), (x2, y2), color, self.style.box_thickness)
            # 标签
            label = f"{det.class_name} {det.confidence:.2f}"
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

    def _draw_label_pil(self, image: np.ndarray, label: str, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """使用 Pillow 渲染标签（支持中文）。"""
        from PIL import ImageFont, ImageDraw, Image
        # 尝试加载中文字体
        font = None
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/System/Library/Fonts/PingFang.ttc",
        ]
        for fp in font_paths:
            try:
                font = ImageFont.truetype(fp, 18)
                break
            except (OSError, IOError):
                continue
        if font is None:
            font = ImageFont.load_default()

        # 使用 Pillow 计算文本尺寸
        temp_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(temp_img)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # 背景
        y1 = max(y - th - 4, 0)
        y2 = y1 + th + 4
        x2 = min(x + tw + 6, image.shape[1] - 1)
        x1 = max(x, 0)
        sub = image[y1:y2, x1:x2].astype(np.float32)
        overlay = np.full_like(sub, self.style.bg_color, dtype=np.float32)
        blended = (sub * (1 - self.style.bg_alpha) + overlay * self.style.bg_alpha).astype(np.uint8)
        image[y1:y2, x1:x2] = blended
        # 转 PIL 绘制文字再转回
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        pil_draw = ImageDraw.Draw(pil_img)
        pil_draw.text((x + 2, y1 + 2), label, font=font, fill=color[::-1])  # BGR→RGB
        image[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
