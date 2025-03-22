import sys
import cv2
import numpy as np
import torch
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QLabel, QFileDialog,
    QVBoxLayout, QWidget, QInputDialog, QMessageBox, QSizePolicy, QPushButton
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from database import add_new_face, delete_face, update_face, view_faces
from match_faces import match_face


class AttendanceUI(QMainWindow):
    """Main UI for Face Attendance System"""

    def __init__(self):
        """Initialize the main UI"""
        super().__init__()
        self.setWindowTitle("Face Attendance System")
        self.resize(900, 700)  # Allow resizing

        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Label for displaying images
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.image_label)

        # Status label for recognition results
        self.status_label = QLabel("Recognition Result: None")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Camera-related variables
        self.cap = None
        self.timer = QTimer(self)

        # Setup toolbar
        self.init_toolbar()

    def init_toolbar(self):
        """Initialize toolbar with actions"""
        toolbar = self.addToolBar("Face Management")

        # Load Image
        load_action = QAction("Load Image", self)
        load_action.triggered.connect(self.load_and_recognize)
        toolbar.addAction(load_action)

        # Open Camera
        camera_action = QAction("Open Camera", self)
        camera_action.triggered.connect(self.start_camera)
        toolbar.addAction(camera_action)

        # Close Camera
        stop_camera_action = QAction("Close Camera", self)
        stop_camera_action.triggered.connect(self.stop_camera)
        toolbar.addAction(stop_camera_action)

        # Manage Faces
        manage_action = QAction("Manage Faces", self)
        manage_action.triggered.connect(self.manage_faces)
        toolbar.addAction(manage_action)

    def load_and_recognize(self):
        """Open file dialog to select an image and perform face recognition"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.load_image(file_name)
            matched_id, distance = match_face(file_name)
            if matched_id:
                self.status_label.setText(f"Recognized: {matched_id} (Distance: {distance:.3f})")
            else:
                self.status_label.setText("No match found.")

    def load_image(self, file_path):
        """Load and display the selected image in the UI"""
        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            QMessageBox.warning(self, "Error", "Failed to load image.")
            return

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        height, width, channel = img_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(
            QPixmap.fromImage(q_img).scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def start_camera(self):
        """Start the camera and continuously capture frames"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "Error", "Cannot access the camera.")
            return

        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)  # Refresh every 30ms

    def update_camera(self):
        """Update camera frame and perform real-time face recognition"""
        ret, frame = self.cap.read()
        if not ret:
            return

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = img_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(
            QPixmap.fromImage(q_img).scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def stop_camera(self):
        """Stop the camera and release resources"""
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.image_label.setText("Camera stopped")

    def manage_faces(self):
        """Open a dialog to manage face entries in the database"""
        dialog = ManageFaceDialog(self)
        dialog.exec_()


class ManageFaceDialog(QInputDialog):
    """Dialog window for managing faces in the database"""

    def __init__(self, parent=None):
        """Initialize the face management dialog"""
        super().__init__(parent)
        self.setWindowTitle("Manage Faces")

        options = ["Add Face", "Delete Face", "Update Face"]
        action, ok = self.getItem(self, "Manage Faces", "Select an action:", options, editable=False)

        if not ok:
            return  # User canceled

        if action == "Add Face":
            self.add_face()
        elif action == "Delete Face":
            self.delete_face()
        elif action == "Update Face":
            self.update_face()

    def add_face(self):
        """Add a new face entry to the database"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_name:
            return

        name, ok = QInputDialog.getText(self, "Enter Name", "Enter the person's name:")
        if not ok or not name.strip():
            return

        add_new_face(file_name, name)
        QMessageBox.information(self, "Success", f"{name} added to database.")

    def delete_face(self):
        """Delete a face entry from the database"""
        names = view_faces()
        if not names:
            QMessageBox.warning(self, "Error", "No faces stored in the database.")
            return

        name, ok = QInputDialog.getItem(self, "Delete Face", "Select a name:", names, editable=False)
        if not ok:
            return

        delete_face(name)
        QMessageBox.information(self, "Success", f"{name} deleted.")

    def update_face(self):
        """Update a stored face entry with a new image"""
        names = view_faces()
        if not names:
            QMessageBox.warning(self, "Error", "No faces stored in the database.")
            return

        name, ok = QInputDialog.getItem(self, "Update Face", "Select a name:", names, editable=False)
        if not ok:
            return

        file_name, _ = QFileDialog.getOpenFileName(self, "Select New Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_name:
            return

        update_face(name, file_name)
        QMessageBox.information(self, "Success", f"{name} updated.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = AttendanceUI()
    ui.show()
    sys.exit(app.exec_())
