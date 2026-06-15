"""给 trtexec 产出的裸 .engine 补上 ultralytics 元数据头, 使 YOLO() 能直接加载.

用法:
    python scripts/wrap_trt_engine.py --pt best.pt --raw best.engine --out best_wrapped.engine

背景: YOLO export 导出的引擎自带元数据头(类别名/stride/task/imgsz),
       trtexec 或 Python API 自建的没有 —— YOLO() 加载会崩。此脚本补上。
"""
import argparse, json
from pathlib import Path
from ultralytics import YOLO

def main():
    ap = argparse.ArgumentParser(description="给裸 TensorRT 引擎补 ultralytics 元数据头")
    ap.add_argument("--pt", required=True, help="原始训练权重 .pt (取 names/stride/task)")
    ap.add_argument("--raw", required=True, help="trtexec/Python 产出的裸引擎 .engine")
    ap.add_argument("--out", required=True, help="输出可被 YOLO() 加载的 .engine")
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=1, help="导出一致的 batch (动态 batch 填 opt batch)")
    args = ap.parse_args()

    m = YOLO(args.pt)
    stride = int(max(m.model.stride)) if hasattr(m.model, "stride") else 32
    meta = {
        "description": f"wrapped from {args.raw}", "author": "odp",
        "stride": stride, "task": m.task, "batch": args.batch,
        "imgsz": [args.imgsz, args.imgsz], "names": m.names,
    }
    engine_bytes = Path(args.raw).read_bytes()
    with open(args.out, "wb") as f:
        blob = json.dumps(meta).encode("utf-8")
        f.write(len(blob).to_bytes(4, "little", signed=True))
        f.write(blob)
        f.write(engine_bytes)
    print(f"OK -> {args.out}  names={list(m.names.values())}")

if __name__ == "__main__":
    main()
