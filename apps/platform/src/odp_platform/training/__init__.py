"""training（训练编排）—— 不发明新方法，编排已有工具完成训练。

职责：串联配置→校验→日志→训练引擎→权重归档→审计快照。
     对外仅暴露 4 个符号：TrainService / TrainResult / TrainMetrics / train_yolo。

主责角色：算法工程师 A
里程碑：M4（训练与评估）
"""
__all__ = []
