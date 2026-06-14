"""桌面端 GUI 参考前端（PyQt6）。通过 OutputSink 接缝与推理引擎对接。"""

import sys
import cv2
import numpy as np
from pathlib import Path
from threading import Thread

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QFileDialog, QComboBox, QStatusBar,
    )
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtCore import Qt, QTimer
except ImportError:
    print("请安装 PyQt6: pip install PyQt6")
    sys.exit(1)

from odp_platform.inference.service import OutputSink, InferService, CancelToken
from odp_platform.inference.sinks import NoopSink
from odp_platform.frame_source.factory import create_frame_source

class QtDisplaySink(OutputSink):
    """将推理结果桥接到 Qt Widget。"""

    def __init__(self, update_callback):
        self.update_callback = update_callback

    def consume(self, frame, detections: list) -> None:
        img = frame.image.copy()
        # 简单绘制（也可集成 BeautifyVisualizer）
        for d in detections:
            x1, y1, x2, y2 = map(int, d["bbox"])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{d['class_name']} {d['confidence']:.2f}",
                       (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        self.update_callback(img)

    def close(self) -> None:
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ODPlatform - 安全帽检测")
        self.setMinimumSize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 控制栏
        ctrl = QHBoxLayout()
        self.source_combo = QComboBox()
        self.source_combo.addItems(["0 - 摄像头", "选择视频文件...", "选择图片..."])
        ctrl.addWidget(QLabel("输入源:"))
        ctrl.addWidget(self.source_combo)

        self.btn_start = QPushButton("开始推理")
        self.btn_start.clicked.connect(self.toggle_inference)
        ctrl.addWidget(self.btn_start)

        self.btn_weights = QPushButton("选择权重...")
        self.btn_weights.clicked.connect(self.select_weights)
        ctrl.addWidget(self.btn_weights)

        layout.addLayout(ctrl)

        # 显示区
        self.display = QLabel("选择输入源和权重后点击开始")
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setMinimumSize(640, 480)
        self.display.setStyleSheet("background-color: #1a1a1a; color: #888;")
        layout.addWidget(self.display)

        # 状态栏
        self.status = QStatusBar()
        self.status.showMessage("就绪")
        self.setStatusBar(self.status)

        self.weights_path = "yolov8n.pt"
        self.infer_thread: Thread = None
        self.cancel = CancelToken()
        self.running = False

    def select_weights(self):
        f, _ = QFileDialog.getOpenFileName(self, "选择权重", "", "PyTorch (*.pt);;All (*)")
        if f:
            self.weights_path = f
            self.status.showMessage(f"权重: {f}")

    def toggle_inference(self):
        if self.running:
            self.cancel.cancel()
            self.btn_start.setText("开始推理")
            self.running = False
        else:
            self._start_inference()

    def _start_inference(self):
        sel = self.source_combo.currentText()
        if "摄像头" in sel:
            source = "0"
        elif "视频" in sel:
            f, _ = QFileDialog.getOpenFileName(self, "选择视频", "", "Video (*.mp4 *.avi *.mov);;All (*)")
            if not f:
                return
            source = f
        else:
            f, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image (*.jpg *.png);;All (*)")
            if not f:
                return
            source = f

        self.cancel = CancelToken()
        self.sink = QtDisplaySink(self._update_frame)

        def run():
            try:
                fs = create_frame_source(source)
                service = InferService(
                    source=fs,
                    model_path=self.weights_path,
                    sink=self.sink,
                    cancel=self.cancel,
                )
                result = service.run()
                self.status.showMessage(f"完成: {result.frames_processed} 帧, {result.fps:.1f} FPS")
            except Exception as e:
                self.status.showMessage(f"错误: {e}")

        self.infer_thread = Thread(target=run, daemon=True)
        self.infer_thread.start()
        self.btn_start.setText("停止")
        self.running = True
        self.status.showMessage("推理中...")

    def _update_frame(self, img: np.ndarray):
        """从后台线程回调，安全更新 QLabel。"""
        h, w, ch = img.shape
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, w * ch, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(
            self.display.width(), self.display.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.display.setPixmap(pix)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
