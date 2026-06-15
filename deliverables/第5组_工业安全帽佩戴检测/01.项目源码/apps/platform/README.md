# ODPlatform — 安全帽检测引擎

通用目标检测工程平台。V1.0 演示场景：安全帽检测。

## 快速开始

\`\`\`bash
pip install -e .
odp-init
odp-transform --dataset safety_helmet --format pascal_voc
odp-validate --dataset safety_helmet
odp-gen-config train
odp-train --config train.yaml
odp-eval --weights best.pt
odp-infer --source 0 --show
\`\`\`
