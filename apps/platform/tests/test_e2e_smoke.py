"""端到端冒烟测试（不需 GPU）。"""
import pytest

def test_import_all_subsystems():
    """验证所有子系统可导入。"""
    import odp_platform.common
    import odp_platform.data_pipeline
    import odp_platform.data_validation
    import odp_platform.runtime_config
    import odp_platform.training
    import odp_platform.evaluation
    import odp_platform.frame_source
    import odp_platform.inference
    import odp_platform.visualization

def test_config_generator():
    from odp_platform.runtime_config.generator import ConfigGenerator
    yaml_text = ConfigGenerator.generate("train")
    assert "epochs" in yaml_text
    assert "model" in yaml_text
