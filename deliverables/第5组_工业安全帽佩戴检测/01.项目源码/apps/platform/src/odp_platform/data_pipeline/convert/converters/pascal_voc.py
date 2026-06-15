"""Pascal VOC XML → YOLO txt 转换器。"""

import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from odp_platform.data_pipeline.convert.registry import register, ConvertOptions, ConvertResult

def _parse_voc_xml(xml_path: Path) -> tuple:
    """
    解析单个 VOC XML。返回 (img_width, img_height, [(class_name, xmin,ymin,xmax,ymax), ...])。
    若 XML 格式异常，返回 (0, 0, []) 并记录警告。
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        size = root.find("size")
        w = int(size.find("width").text)
        h = int(size.find("height").text)
        objects = []
        for obj in root.findall("object"):
            name = obj.find("name").text
            bbox = obj.find("bndbox")
            xmin = float(bbox.find("xmin").text)
            ymin = float(bbox.find("ymin").text)
            xmax = float(bbox.find("xmax").text)
            ymax = float(bbox.find("ymax").text)
            objects.append((name, xmin, ymin, xmax, ymax))
        return w, h, objects
    except Exception:
        return 0, 0, []

@register("pascal_voc")
def convert_pascal_voc(options: ConvertOptions) -> ConvertResult:
    """
    将 Pascal VOC XML 标注转为 YOLO txt。
    像素坐标 → 归一化坐标: (x_center/w, y_center/h, bbox_w/w, bbox_h/h)
    类别名从 XML 中收集并编号，若 options.class_names 已提供则直接映射。
    """
    src = Path(options.source_dir)
    tgt = Path(options.target_dir)
    tgt_labels = tgt / "labels"
    tgt_labels.mkdir(parents=True, exist_ok=True)

    total_images = 0
    total_labels = 0
    class_counter = Counter()
    class_to_id = {}
    if options.class_names:
        class_to_id = {n: i for i, n in enumerate(options.class_names)}

    # 收集所有 XML 文件
    xml_files = sorted(src.glob("*.xml"))
    if not xml_files:
        xml_files = sorted(src.rglob("*.xml"))  # 递归查找

    for xml_file in xml_files:
        w, h, objects = _parse_voc_xml(xml_file)
        if w == 0 or h == 0:
            continue
        total_images += 1
        lines = []
        for cls_name, xmin, ymin, xmax, ymax in objects:
            if cls_name not in class_to_id and not options.class_names:
                class_to_id[cls_name] = len(class_to_id)
            cid = class_to_id.get(cls_name)
            if cid is None:
                continue  # 不在类别列表中的跳过
            class_counter[cls_name] += 1
            # 归一化
            x_center = ((xmin + xmax) / 2) / w
            y_center = ((ymin + ymax) / 2) / h
            bw = (xmax - xmin) / w
            bh = (ymax - ymin) / h
            # 裁剪到 [0,1]
            x_center = max(0, min(1, x_center))
            y_center = max(0, min(1, y_center))
            bw = max(0, min(1, bw))
            bh = max(0, min(1, bh))
            lines.append(f"{cid} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}")
        # 写 txt
        out_path = tgt_labels / f"{xml_file.stem}.txt"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        total_labels += 1

    return ConvertResult(
        success=True,
        total_images=total_images,
        total_labels=total_labels,
        class_counts=dict(class_counter),
    )
