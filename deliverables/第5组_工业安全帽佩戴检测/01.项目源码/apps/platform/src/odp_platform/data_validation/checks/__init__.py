"""自动导入所有检查模块以触发 @check 注册。"""
from odp_platform.data_validation.checks import yaml_schema
from odp_platform.data_validation.checks import pair_existence
from odp_platform.data_validation.checks import label_format
from odp_platform.data_validation.checks import split_uniqueness
