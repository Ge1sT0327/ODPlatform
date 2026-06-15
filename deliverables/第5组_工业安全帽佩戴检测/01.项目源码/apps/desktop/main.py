"""桌面端 GUI（tkinter — Windows 原生支持，零额外依赖）。"""

import cv2
import numpy as np
from threading import Thread, Lock
from tkinter import Tk, Frame, Button, Label, filedialog, StringVar, ttk
from tkinter import messagebox
from PIL import Image, ImageTk

from odp_platform.inference.service import OutputSink, InferService, CancelToken
from odp_platform.frame_source.factory import create_frame_source
from odp_platform.visualization.visualizer import BeautifyVisualizer, Detection


class TkDisplaySink(OutputSink):
    """将推理结果桥接到 tkinter，集成 BeautifyVisualizer 绘制，通过 after 投递到主线程。"""

    def __init__(self, root, update_callback):
        self.root = root
        self.update_callback = update_callback
        self.viz = BeautifyVisualizer(class_names=["hat", "person"])
        self._frame_count = 0

    def consume(self, frame, detections: list) -> None:
        self._frame_count += 1
        if self._frame_count % 2 != 0:  # 每 2 帧显示一帧，减少闪烁
            return
        img = frame.image.copy()
        viz_dets = []
        for d in detections:
            viz_dets.append(Detection(
                bbox=tuple(d["bbox"]),
                class_id=d["class_id"],
                class_name=d["class_name"],
                confidence=d["confidence"],
            ))
        self.viz.draw(img, viz_dets)
        self.root.after(0, self.update_callback, img)

    def close(self) -> None:
        pass


class DesktopApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("ODPlatform — 安全帽检测")
        self.root.geometry("960x720")
        self.root.configure(bg="#1e1e1e")

        self.weights_path = StringVar(value="models/checkpoints/exp_20260614_125153_best.pt")
        self.running = False
        self.cancel = CancelToken()
        self.infer_thread: Thread = None
        self._lock = Lock()

        self._build_ui()

    def _build_ui(self):
        # —— 控制栏 ——
        ctrl = Frame(self.root, bg="#2d2d2d", height=40)
        ctrl.pack(fill="x", padx=8, pady=(8, 4))

        Button(ctrl, text="选择权重...", command=self._select_weights,
               bg="#3a3a3a", fg="#e0e0e0", relief="flat", padx=12).pack(side="left", padx=4)

        self.lbl_weights = Label(ctrl, textvariable=self.weights_path, fg="#888",
                                 bg="#2d2d2d", anchor="w", width=50)
        self.lbl_weights.pack(side="left", padx=8)

        self.source_var = StringVar(value="camera")
        src_frame = Frame(ctrl, bg="#2d2d2d")
        src_frame.pack(side="left", padx=12)
        for val, txt in [("camera", "摄像头"), ("video", "视频文件"), ("image", "图片文件")]:
            ttk.Radiobutton(src_frame, text=txt, variable=self.source_var,
                            value=val).pack(side="left", padx=4)

        self.btn_start = Button(ctrl, text="开始推理", command=self._toggle,
                                bg="#007acc", fg="white", relief="flat",
                                padx=20, pady=4, font=("Microsoft YaHei", 10, "bold"))
        self.btn_start.pack(side="right", padx=8)

        # —— 显示区 ——
        self.display = Label(self.root, bg="#0d0d0d", text="加载模型后点击「开始推理」",
                             fg="#666", font=("Microsoft YaHei", 14))
        self.display.pack(fill="both", expand=True, padx=8, pady=4)

        # —— 状态栏 ——
        self.status = Label(self.root, text="就绪 | 模型: exp_20260614_125153_best.pt",
                            fg="#888", bg="#1e1e1e", anchor="w")
        self.status.pack(fill="x", padx=8, pady=(0, 6))

    def _select_weights(self):
        f = filedialog.askopenfilename(
            title="选择模型权重", filetypes=[("PyTorch", "*.pt"), ("All", "*.*")])
        if f:
            self.weights_path.set(f)

    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        source_type = self.source_var.get()
        if source_type == "camera":
            source = "0"
        else:
            ft = [("Video", "*.mp4 *.avi *.mov")] if source_type == "video" else [("Image", "*.jpg *.png")]
            f = filedialog.askopenfilename(title="选择文件", filetypes=ft)
            if not f:
                return
            source = f

        self.cancel = CancelToken()
        self.sink = TkDisplaySink(self.root, self._update_frame)
        self.running = True
        self.btn_start.config(text="停止", bg="#c0392b")
        self.status.config(text="推理中...")

        def run():
            try:
                fs = create_frame_source(source)
                import torch
                device = "0" if torch.cuda.is_available() else "cpu"
                service = InferService(
                    source=fs,
                    model_path=self.weights_path.get(),
                    sink=self.sink,
                    cancel=self.cancel,
                    device=device,
                )
                result = service.run()
                self.root.after(0, lambda: self.status.config(
                    text=f"完成: {result.frames_processed} 帧, {result.fps:.1f} FPS"))
            except Exception as e:
                err_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("错误", err_msg))
            finally:
                self.root.after(0, self._on_finish)

        self.infer_thread = Thread(target=run, daemon=True)
        self.infer_thread.start()

    def _stop(self):
        self.cancel.cancel()
        self.btn_start.config(text="停止中...", state="disabled")

    def _on_finish(self):
        self.running = False
        self.btn_start.config(text="开始推理", bg="#007acc", state="normal")

    def _update_frame(self, img: np.ndarray):
        with self._lock:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            dw = self.display.winfo_width() or 800
            dh = self.display.winfo_height() or 600
            scale = min(dw / w, dh / h, 1.0)
            nw, nh = int(w * scale), int(h * scale)
            rgb = cv2.resize(rgb, (nw, nh))
            pil_img = Image.fromarray(rgb)
            self._tk_img = ImageTk.PhotoImage(pil_img)
            self.display.config(image=self._tk_img, text="")

    def run(self):
        self.root.mainloop()


def main():
    app = DesktopApp()
    app.run()


if __name__ == "__main__":
    main()
