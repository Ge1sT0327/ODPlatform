"""evaluation（评估）—— 训练子系统的镜像，复用 common 工具评估模型。

职责：加载训练归档权重，计算 mAP / Precision / Recall。
     对外仅暴露 4 个符号：ValService / ValResult / ValMetrics / evaluate_yolo。
     不 import training，不设 archive。

主责角色：算法工程师 B
里程碑：M4（训练与评估）
"""
__all__ = []
