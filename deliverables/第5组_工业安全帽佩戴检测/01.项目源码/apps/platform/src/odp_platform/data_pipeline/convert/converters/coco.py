"""COCO JSON → YOLO txt 转换器。"""

import json
from pathlib import Path
from collections import Counter
from odp_platform.data_pipeline.convert.registry import register, ConvertOptions, ConvertResult

@register("coco")
def convert_coco(options: ConvertOptions) -> ConvertResult:
    """
    将 COCO JSON 标注转为 YOLO txt。
    从 JSON 读取 images[].file_name + annotations[].bbox + categories[].name。
    COCO bbox 格式: [x, y, width, height] (像素) → YOLO (x_center, y_center, w, h) (归一化)。
    """
    src = Path(options.source_dir)
    tgt = Path(options.target_dir)
    tgt_labels = tgt / "labels"
    tgt_labels.mkdir(parents=True, exist_ok=True)

    # 查找 JSON 文件
    json_files = list(src.glob("*.json"))
    if not json_files:
        return ConvertResult(success=False, error="找不到 COCO JSON 标注文件")

    coco_json = json.loads(json_files[0].read_text(encoding="utf-8"))

    # 建立映射
    cat_id_to_name = {c["id"]: c["name"] for c in coco_json["categories"]}
    cat_name_to_idx = {c["name"]: i for i, c in enumerate(coco_json["categories"])}
    img_id_to_info = {img["id"]: img for img in coco_json["images"]}

    class_counter = Counter()
    total_labels = 0

    for ann in coco_json["annotations"]:
        img_info = img_id_to_info[ann["image_id"]]
        x, y, bw, bh = ann["bbox"]
        img_w, img_h = img_info["width"], img_info["height"]
        cat_name = cat_id_to_name[ann["category_id"]]
        cid = cat_name_to_idx[cat_name]
        class_counter[cat_name] += 1

        x_center = (x + bw / 2) / img_w
        y_center = (y + bh / 2) / img_h
        nw = bw / img_w
        nh = bh / img_h
        line = f"{cid} {max(0,min(1,x_center)):.6f} {max(0,min(1,y_center)):.6f} {max(0,min(1,nw)):.6f} {max(0,min(1,nh)):.6f}"

        img_name = Path(img_info["file_name"]).stem
        out_path = tgt_labels / f"{img_name}.txt"
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        total_labels += 1

    return ConvertResult(
        success=True,
        total_images=len(coco_json["images"]),
        total_labels=total_labels,
        class_counts=dict(class_counter),
    )
