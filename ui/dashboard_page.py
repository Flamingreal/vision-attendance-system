import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFileDialog, QPushButton, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from ui.camera import Camera
from match_faces import match_face
from ui.utils import show_warning_message
import time


class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.last_signed_time = {}

        self.camera = Camera()
        self.camera.frame_signal.connect(self.update_camera_frame)
        self.camera.start()

        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)

        # Left side: Camera or Image
        self.image_label = QLabel("No image/camera feed")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.image_label)

        # Right side: Control Panel
        self.control_panel = QVBoxLayout()

        self.result_label = QLabel("Recognition Result: None")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.control_panel.addWidget(self.result_label)

        # self.load_button = QPushButton("Load Image")  # Temporarily removed
        # self.load_button.clicked.connect(self.load_and_recognize)
        # self.control_panel.addWidget(self.load_button)

        self.layout.addLayout(self.control_panel)

    def update_camera_frame(self, frame):
        if frame is not None:
            qt_frame = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qt_frame)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

            cv2.imwrite("temp.jpg", frame)
            matched_id, distance = match_face("temp.jpg")

            if matched_id:
                now = time.time()
                last_time = self.last_signed_time.get(matched_id, 0)

                if now - last_time >= 30:
                    self.db.add_attendance_record(matched_id)
                    self.last_signed_time[matched_id] = now
                    print(f"[DEBUG] Signed: {matched_id}")
                    self.result_label.setText(f"Recognition Result: {matched_id} (Signed)")
                else:
                    #print(f"[DEBUG] Skipped duplicate sign-in for {matched_id}")
                    self.result_label.setText(f"Already Signed Recently: {matched_id}")

    def load_and_recognize(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.display_image(file_name)
            try:
                matched_id, distance = match_face(file_name)
                if matched_id:
                    self.result_label.setText(f"Recognized: {matched_id} (Distance: {distance:.3f})")
                    self.db.add_attendance_record(matched_id)
                else:
                    self.result_label.setText("No match found.")
            except Exception as e:
                show_warning_message(self, "Error", f"Recognition failed: {e}")

    def display_image(self, file_path):
        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            show_warning_message(self, "Error", "Could not load image.")
            return
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        height, width, channel = img_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(
            self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def cleanup(self):
        self.camera.stop()
