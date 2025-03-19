import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QLabel, QFileDialog,
    QVBoxLayout, QWidget, QInputDialog, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
from database import add_new_face, delete_face, update_face, view_faces
from match_faces import match_face

class AttendanceUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Attendance System")
        self.resize(800, 600)  # Allow resizing

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Image Display
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow resizing
        self.layout.addWidget(self.image_label)

        # Status Label
        self.status_label = QLabel("Recognition Result: None")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Toolbar Setup
        self.init_toolbar()

    def init_toolbar(self):
        """Setup the toolbar with face management options."""
        toolbar = self.addToolBar("Face Management")

        # Load Image
        load_action = QAction("Load Image", self)
        load_action.triggered.connect(self.load_and_recognize)
        toolbar.addAction(load_action)

        # Manage Faces (Opens Dialog)
        manage_action = QAction("Manage Faces", self)
        manage_action.triggered.connect(self.manage_faces)
        toolbar.addAction(manage_action)

    def load_and_recognize(self):
        """Opens a file dialog to select an image and perform face recognition."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.load_image(file_name)
            matched_id, distance = match_face(file_name)
            if matched_id:
                self.status_label.setText(f"Recognized: {matched_id} (Distance: {distance:.3f})")
            else:
                self.status_label.setText("No match found.")

    def load_image(self, file_path):
        """Loads and displays the selected image in the UI."""
        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            QMessageBox.warning(self, "Error", "Failed to load image.")
            return

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        height, width, channel = img_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def manage_faces(self):
        """Opens a dialog for face management options."""
        dialog = ManageFaceDialog(self)
        dialog.exec_()

class ManageFaceDialog(QInputDialog):
    """Dialog window for managing faces in the database."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Faces")

        options = ["Add Face", "Delete Face", "Update Face"]
        action, ok = self.getItem(self, "Manage Faces", "Select an action:", options, editable=False)

        if not ok:  # 如果用户点了取消，则退出
            return

        if action == "Add Face":
            self.add_face()
        elif action == "Delete Face":
            self.delete_face()
        elif action == "Update Face":
            self.update_face()

    def add_face(self):
        """Handles adding a new face to the database."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_name:
            return  # 用户点了取消

        name, ok = QInputDialog.getText(self, "Enter Name", "Enter the person's name:")
        if not ok or not name.strip():
            return  # 用户点了取消或未输入有效名称

        add_new_face(file_name, name)
        QMessageBox.information(self, "Success", f"{name} added to database.")

    def delete_face(self):
        """Handles deleting a face from the database."""
        names = view_faces()
        if not names:
            QMessageBox.warning(self, "Error", "No faces stored in the database.")
            return

        name, ok = QInputDialog.getItem(self, "Delete Face", "Select a name:", names, editable=False)
        if not ok:
            return  # 用户点了取消

        delete_face(name)
        QMessageBox.information(self, "Success", f"{name} deleted.")

    def update_face(self):
        """Handles updating an existing face in the database."""
        names = view_faces()
        if not names:
            QMessageBox.warning(self, "Error", "No faces stored in the database.")
            return

        name, ok = QInputDialog.getItem(self, "Update Face", "Select a name:", names, editable=False)
        if not ok:
            return  # 用户点了取消

        file_name, _ = QFileDialog.getOpenFileName(self, "Select New Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_name:
            return  # 用户点了取消

        update_face(name, file_name)
        QMessageBox.information(self, "Success", f"{name} updated.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = AttendanceUI()
    ui.show()
    sys.exit(app.exec_())
