"""cli（命令行入口层）—— 薄包装，核心能力以库 API 形式提供。

职责：各 CLI 入口（odp-init/reset/transform/validate/train/eval/infer），
     仅做参数解析与薄包装，核心逻辑在对应子系统中。

主责角色：架构师（init/reset）+ 各子系统负责人
"""
__all__ = []
