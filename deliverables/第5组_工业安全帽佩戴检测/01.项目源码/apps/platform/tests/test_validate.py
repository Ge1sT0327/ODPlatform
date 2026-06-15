"""测试数据验证检查项。"""
from odp_platform.data_validation.registry import CheckContext, CheckSeverity
from odp_platform.data_validation.checks.yaml_schema import check_yaml_schema

def test_yaml_schema_missing_fields(tmp_path):
    yaml = tmp_path / "bad.yaml"
    yaml.write_text("nc: 0\n", encoding="utf-8")
    ctx = CheckContext(yaml_path=yaml, dataset_name="test")
    result = check_yaml_schema(ctx)
    assert result.severity == CheckSeverity.ERROR
