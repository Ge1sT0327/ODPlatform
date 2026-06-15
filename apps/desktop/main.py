"""桌面端 GUI（tkinter + HUD 信息面板）。"""

import cv2
import numpy as np
import time
from collections import deque
from threading import Thread, Lock
from tkinter import Tk, Frame, Button, Label, filedialog, StringVar, ttk
from tkinter import messagebox
from PIL import Image, ImageTk

from odp_platform.inference.service import OutputSink, InferService, CancelToken
from odp_platform.frame_source.factory import create_frame_source
from odp_platform.visualization.visualizer import BeautifyVisualizer, Detection


class TkDisplaySink(OutputSink):
    def __init__(self, root, update_callback):
        self.root = root
        self.update_callback = update_callback
        self.viz = BeautifyVisualizer(class_names=["hat", "person"])
        self._frame_count = 0
        self._infer_times = deque(maxlen=30)
        self._last_time = time.perf_counter()
        self._n_dets = 0
        self._counts = {}

    def consume(self, frame, detections: list) -> None:
        now = time.perf_counter()
        dt = (now - self._last_time) * 1000
        self._last_time = now
        self._frame_count += 1
        self._infer_times.append(dt)
        self._n_dets = len(detections)
        self._counts = {}
        for d in detections:
            n = d["class_name"]
            self._counts[n] = self._counts.get(n, 0) + 1
        if self._frame_count % 2 != 0:
            return
        img = frame.image.copy()
        viz_dets = [Detection(bbox=tuple(d["bbox"]), class_id=d["class_id"], class_name=d["class_name"], confidence=d["confidence"]) for d in detections]
        self.viz.draw(img, viz_dets)
        avg_infer = sum(self._infer_times)/len(self._infer_times) if self._infer_times else 0
        fps_now = 1000/dt if dt>0 else 0
        _draw_hud(img, fps=fps_now, infer_ms=avg_infer, frame_idx=self._frame_count, n_dets=self._n_dets, counts=self._counts, resolution=(frame.info.original_width, frame.info.original_height) if frame.info else (0,0))
        self.root.after(0, self.update_callback, img)

    def close(self) -> None:
        pass


def _draw_hud(img, *, fps, infer_ms, frame_idx, n_dets, counts, resolution):
    h, w = img.shape[:2]
    rows = [("FPS",f"{fps:5.1f}",(0,255,0)),("Infer",f"{infer_ms:4.0f}ms",(0,220,255)),("Frame",f"#{frame_idx}",(220,220,220)),("Objects",f"{n_dets}",(255,200,0))]
    for cls,cnt in sorted(counts.items()):
        rows.append((cls,f"{cnt}",(0,230,0) if cls=="hat" else (100,180,255)))
    font=cv2.FONT_HERSHEY_SIMPLEX; fs,th,lh=0.45,1,20; pad,label_w,panel_w=8,72,195
    panel_h=pad*2+lh*len(rows)+6; x0,y0=10,10
    overlay=img.copy(); cv2.rectangle(overlay,(x0,y0),(x0+panel_w,y0+panel_h),(15,15,15),-1)
    cv2.addWeighted(overlay,0.5,img,0.5,0,img)
    cv2.rectangle(img,(x0,y0),(x0+3,y0+panel_h),(0,200,255),-1)
    y=y0+pad+14
    for label,value,color in rows:
        cv2.putText(img,label,(x0+pad+8,y),font,fs,(180,180,180),th,cv2.LINE_AA)
        cv2.putText(img,value,(x0+pad+label_w,y),font,fs,color,th,cv2.LINE_AA)
        y+=lh


class DesktopApp:
    def __init__(self):
        self.root=Tk(); self.root.title("ODPlatform — 安全帽检测"); self.root.geometry("960x720"); self.root.configure(bg="#1e1e1e")
        self.weights_path=StringVar(value="models/checkpoints/yolov8n_safety_helmet_best.pt")
        self.running=False; self.cancel=CancelToken(); self.infer_thread=None; self._lock=Lock()
        self._build_ui()

    def _build_ui(self):
        ctrl=Frame(self.root,bg="#2d2d2d",height=40); ctrl.pack(fill="x",padx=8,pady=(8,4))
        Button(ctrl,text="选择权重...",command=self._select_weights,bg="#3a3a3a",fg="#e0e0e0",relief="flat",padx=12).pack(side="left",padx=4)
        self.lbl_weights=Label(ctrl,textvariable=self.weights_path,fg="#888",bg="#2d2d2d",anchor="w",width=50); self.lbl_weights.pack(side="left",padx=8)
        self.source_var=StringVar(value="camera")
        sf=Frame(ctrl,bg="#2d2d2d"); sf.pack(side="left",padx=12)
        for v,t in [("camera","摄像头"),("video","视频文件"),("image","图片文件")]:
            ttk.Radiobutton(sf,text=t,variable=self.source_var,value=v).pack(side="left",padx=4)
        self.btn_start=Button(ctrl,text="开始推理",command=self._toggle,bg="#007acc",fg="white",relief="flat",padx=20,pady=4,font=("Microsoft YaHei",10,"bold")); self.btn_start.pack(side="right",padx=8)
        self.display=Label(self.root,bg="#0d0d0d",text="加载模型后点击「开始推理」",fg="#666",font=("Microsoft YaHei",14)); self.display.pack(fill="both",expand=True,padx=8,pady=4)
        self.status=Label(self.root,text="就绪 | 模型: yolov8n_safety_helmet_best.pt",fg="#888",bg="#1e1e1e",anchor="w"); self.status.pack(fill="x",padx=8,pady=(0,6))

    def _select_weights(self):
        f=filedialog.askopenfilename(title="选择模型权重",filetypes=[("PyTorch","*.pt"),("All","*.*")])
        if f: self.weights_path.set(f)

    def _toggle(self):
        if self.running: self._stop()
        else: self._start()

    def _start(self):
        st=self.source_var.get()
        if st=="camera": source="0"
        else:
            ft=[("Video","*.mp4 *.avi *.mov")] if st=="video" else [("Image","*.jpg *.png")]
            f=filedialog.askopenfilename(title="选择文件",filetypes=ft)
            if not f: return
            source=f
        self.cancel=CancelToken(); self.sink=TkDisplaySink(self.root,self._update_frame)
        self.running=True; self.btn_start.config(text="停止",bg="#c0392b"); self.status.config(text="推理中...")
        def run():
            try:
                fs=create_frame_source(source); import torch; device="0" if torch.cuda.is_available() else "cpu"
                service=InferService(source=fs,model_path=self.weights_path.get(),sink=self.sink,cancel=self.cancel,device=device)
                result=service.run()
                self.root.after(0,lambda: self.status.config(text=f"完成: {result.frames_processed} 帧, {result.fps:.1f} FPS"))
            except Exception as e:
                self.root.after(0,lambda: messagebox.showerror("错误",str(e)))
            finally:
                self.root.after(0,self._on_finish)
        self.infer_thread=Thread(target=run,daemon=True); self.infer_thread.start()

    def _stop(self):
        self.cancel.cancel(); self.btn_start.config(text="停止中...",state="disabled")

    def _on_finish(self):
        self.running=False; self.btn_start.config(text="开始推理",bg="#007acc",state="normal")

    def _update_frame(self,img):
        with self._lock:
            rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB); h,w=rgb.shape[:2]
            dw=self.display.winfo_width() or 800; dh=self.display.winfo_height() or 600
            scale=min(dw/w,dh/h,1.0); nw,nh=int(w*scale),int(h*scale)
            rgb=cv2.resize(rgb,(nw,nh)); pil_img=Image.fromarray(rgb)
            self._tk_img=ImageTk.PhotoImage(pil_img); self.display.config(image=self._tk_img,text="")

    def run(self):
        self.root.mainloop()

def main():
    DesktopApp().run()

if __name__=="__main__":
    main()
