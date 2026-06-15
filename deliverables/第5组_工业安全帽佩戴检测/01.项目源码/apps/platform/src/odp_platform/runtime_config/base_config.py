"""配置基类：Pydantic v2 + 字段元数据 + 审计快照 + 下游接口。"""

from enum import Enum
from typing import ClassVar, Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

class ConfigSource(str, Enum):
    DEFAULT = "default"
    YAML = "yaml"
    CLI = "cli"

class BaseConfig(BaseModel):
    model_config = {"extra": "forbid", "validate_assignment": True}

    _source_map: Dict[str, ConfigSource] = {}

    def to_ultralytics_kwargs(self) -> dict:
        """
        转为 ultralytics 训练/验证/推理可消费的关键字参数。
        子类必须重写。只包含非 None 且目标引擎接受的字段。
        """
        raise NotImplementedError

    @classmethod
    def get_field_groups(cls) -> Dict[str, list]:
        """
        通过反射收集字段分组。
        返回 {group_name: [field_name, ...]}。
        基于每个 Field 的 json_schema_extra["group"]。
        """
        groups: Dict[str, list] = {}
        for name, field_info in cls.model_fields.items():
            extra = field_info.json_schema_extra or {}
            group = extra.get("group", "其他")
            groups.setdefault(group, []).append(name)
        return groups

    @classmethod
    def get_field_metadata(cls, field_name: str) -> dict:
        """返回单个字段的元数据（分组、默认值、示例、说明、取值范围）。"""
        field_info: FieldInfo = cls.model_fields.get(field_name)
        if field_info is None:
            return {}
        extra = field_info.json_schema_extra or {}
        return {
            "group": extra.get("group", "其他"),
            "default": field_info.default,
            "type": field_info.annotation.__name__ if hasattr(field_info.annotation, "__name__") else str(field_info.annotation),
            "example": extra.get("example", ""),
            "description": extra.get("description", ""),
            "choices": extra.get("choices", []),
        }

    def to_audit_snapshot(self) -> dict:
        """导出审计快照（含配置值 + 来源映射）。"""
        return {
            "config": self.model_dump(),
            "sources": {k: v.value for k, v in self._source_map.items()},
            "model_class": self.__class__.__name__,
        }

    @classmethod
    def from_audit_snapshot(cls, snapshot: dict) -> "BaseConfig":
        """从审计快照重建配置对象。"""
        return cls(**snapshot["config"])

    def mask_sensitive_dump(self) -> dict:
        """脱敏导出（默认全量导出，子类可重写以隐藏敏感字段）。"""
        return self.model_dump()
