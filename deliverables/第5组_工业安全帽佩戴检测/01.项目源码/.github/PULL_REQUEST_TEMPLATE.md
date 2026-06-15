## 概述

<!-- 一句话描述这个 PR 做了什么 -->


## 关联子系统

<!-- 勾选影响的子系统 -->
- [ ] common（基础层）
- [ ] data_pipeline（数据流水线）
- [ ] data_validation（数据验证）
- [ ] runtime_config（运行配置）
- [ ] training（训练）
- [ ] evaluation（评估）
- [ ] inference（推理）
- [ ] frame_source（帧源）
- [ ] visualization（可视化）
- [ ] cli（命令行入口）
- [ ] desktop（桌面端）

## 变更类型

- [ ] feat: 新功能
- [ ] fix: 修复
- [ ] docs: 文档
- [ ] test: 测试
- [ ] chore: 工程配置
- [ ] refactor: 重构

## 依赖纪律检查

<!-- 在提交前自行确认以下项 -->

- [ ] 未引入反向依赖（CON-06：只向下依赖 common）
- [ ] 未硬编码路径（CON-05：所有路径走 common.paths）
- [ ] 业务模块无 `print` 调试输出（NFR-OBS-01）
- [ ] 对外 API 已通过 `__all__` 显式声明（NFR-ENG-04）
- [ ] 推理/可视化包内无前端框架依赖（NFR-EXT-03 / CON-08）

## 测试

- [ ] 已添加/更新单元测试
- [ ] 冒烟测试通过

## 交接物影响

<!-- 如果变更涉及冻结的接口契约或交接物，请勾选并说明 -->
- [ ] 本次变更**不影响**已有接口契约
- [ ] 本次变更**修改了**对外接口（需在下游同步）
