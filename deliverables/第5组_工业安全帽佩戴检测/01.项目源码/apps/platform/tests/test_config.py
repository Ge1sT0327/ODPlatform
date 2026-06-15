from odp_platform.runtime_config.train_config import YOLOTrainConfig

def test_train_config_defaults():
    cfg = YOLOTrainConfig()
    assert cfg.task == "detect"
    assert cfg.epochs == 100
    assert cfg.model == "yolov8n.pt"

def test_train_config_fail_fast():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        YOLOTrainConfig(epochs=0)  # epochs >= 1

def test_to_ultralytics_kwargs():
    cfg = YOLOTrainConfig()
    kw = cfg.to_ultralytics_kwargs()
    assert "epochs" in kw
    assert kw["epochs"] == 100
