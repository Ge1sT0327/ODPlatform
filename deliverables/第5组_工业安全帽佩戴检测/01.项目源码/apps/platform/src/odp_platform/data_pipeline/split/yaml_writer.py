"""生成 data.yaml 配置文件。"""

from pathlib import Path
import yaml
from odp_platform.common.paths import dataset_yaml_path, DATA_DIR

def write_dataset_yaml(
    dataset_name: str,
    class_names: list,
    path_override: Path = None,
) -> Path:
    """
    生成 configs/datasets/<dataset_name>.yaml。
    内容: path, train, val, test, nc, names
    """
    data_path = str(path_override or DATA_DIR)
    config = {
        "path": data_path,
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "nc": len(class_names),
        "names": {i: name for i, name in enumerate(class_names)},
    }
    out = dataset_yaml_path(dataset_name)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.dump(config, allow_unicode=True, default_flow_style=False), encoding="utf-8")
    return out
