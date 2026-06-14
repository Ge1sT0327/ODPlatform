"""odp-infer 命令入口。"""

import sys
import argparse
from odp_platform.inference.service import infer_yolo
from odp_platform.inference.sinks import DisplaySink, SaveVideoSink
from odp_platform.common.constants import ExitCode

def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description="实时目标检测推理")
    parser.add_argument("--source", required=True, help="输入源: 0=摄像头, path/to/img, path/to/video, rtsp://...")
    parser.add_argument("--weights", default="yolov8n.pt", help="模型权重")
    parser.add_argument("--conf", type=float, default=0.25, help="置信度阈值")
    parser.add_argument("--iou", type=float, default=0.7, help="IoU 阈值")
    parser.add_argument("--imgsz", type=int, default=640, help="输入尺寸")
    parser.add_argument("--device", default="auto", help="设备")
    parser.add_argument("--show", action="store_true", help="实时显示")
    parser.add_argument("--save", type=str, default=None, help="保存视频路径")
    args = parser.parse_args(argv)

    sink = None
    if args.save:
        sink = SaveVideoSink(args.save)
    elif args.show:
        sink = DisplaySink()

    try:
        result = infer_yolo(
            source=args.source,
            model_path=args.weights,
            sink=sink,
            conf=args.conf,
            iou=args.iou,
            imgsz=args.imgsz,
            device=args.device,
            show=args.show,
        )
        print(f"推理完成: {result.frames_processed} 帧, FPS={result.fps:.1f}")
        return ExitCode.SUCCESS
    except KeyboardInterrupt:
        print("推理被用户中断。")
        return ExitCode.SUCCESS
    except Exception as e:
        print(f"推理失败: {e}", file=sys.stderr)
        return ExitCode.SYSTEM_ERROR

if __name__ == "__main__":
    sys.exit(main())
