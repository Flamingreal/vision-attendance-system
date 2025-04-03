import cv2
import numpy as np
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from ui.camera import Camera
from face_models import extract_embedding

class CaptureFaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capture Face from Camera")
        self.setMinimumSize(480, 400)

        self.camera = Camera()
        self.camera.frame_signal.connect(self.update_frame)

        self.captured_image = None

        self.init_ui()
        self.camera.start()

    def init_ui(self):
        layout = QVBoxLayout()

        self.image_label = QLabel("Camera feed will appear here")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        btn_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture")
        self.capture_btn.clicked.connect(self.capture_image)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_frame(self, frame):
        if frame is not None:
            self.current_frame = frame.copy()
            qt_img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qt_img)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def capture_image(self):
        if hasattr(self, "current_frame"):
            rgb_image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            embedding = extract_embedding(rgb_image)
            if embedding is not None:
                self.captured_image = embedding
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No face detected in the captured image.")

    def get_embedding(self):
        return self.captured_image

    def closeEvent(self, event):
        self.camera.stop()
        event.accept()
