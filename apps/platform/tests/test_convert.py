"""测试 Pascal VOC → YOLO 转换。"""
import tempfile
from pathlib import Path
from odp_platform.data_pipeline.convert.registry import ConvertOptions
from odp_platform.data_pipeline.convert.converters.pascal_voc import convert_pascal_voc

VOC_XML = """<?xml version="1.0"?>
<annotation>
    <size><width>640</width><height>480</height></size>
    <object><name>hat</name><bndbox><xmin>10</xmin><ymin>20</ymin><xmax>100</xmax><ymax>200</ymax></bndbox></object>
</annotation>"""

def test_convert_pascal_voc(tmp_path):
    xml_dir = tmp_path / "xml"
    xml_dir.mkdir()
    (xml_dir / "test.xml").write_text(VOC_XML, encoding="utf-8")
    out = tmp_path / "out"
    result = convert_pascal_voc(ConvertOptions(source_dir=xml_dir, target_dir=out, format="pascal_voc"))
    assert result.success
    assert result.total_labels == 1
    label_file = out / "labels" / "test.txt"
    assert label_file.exists()
