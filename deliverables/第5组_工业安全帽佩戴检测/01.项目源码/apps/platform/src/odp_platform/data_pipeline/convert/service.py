"""转换服务：根据 ConvertOptions 选择转换器并执行。"""

from odp_platform.data_pipeline.convert.registry import (
    ConvertOptions, ConvertResult, get_converter,
)
# 触发注册
import odp_platform.data_pipeline.convert.converters  # noqa: F401

def convert_data_to_yolo(options: ConvertOptions) -> ConvertResult:
    """根据 options.format 选择转换器执行。"""
    converter = get_converter(options.format)
    return converter(options)
