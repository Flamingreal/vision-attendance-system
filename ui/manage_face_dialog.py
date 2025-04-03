from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from ui.utils import (
    show_info_message,
    show_warning_message,
    get_text_input,
    get_selection_input,
    load_rgb_image
)
from face_models import extract_embedding
from database import DatabaseManager
from ui.custom_selection_dialog import ActionSelectionDialog
from ui.capture_face_dialog import CaptureFaceDialog


class ManageFaceDialog(QDialog):
    def __init__(self, parent=None, db: DatabaseManager = None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Manage Faces")
        self.embedding = None

    @staticmethod
    def launch_if_needed(parent, db):
        """
        Safe launch: Only open real dialog if user made valid selection.
        """
        dialog = ActionSelectionDialog(parent)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_action:
            print(f"[DEBUG] User selected: {dialog.selected_action}")
            logic_dialog = ManageFaceDialog(parent, db)
            logic_dialog.exec_dialog(dialog.selected_action)
        else:
            print("[DEBUG] User canceled or closed the action selection.")

    def exec_dialog(self, action):
        """
        Execute dialog logic based on action, and manage window visibility manually.
        """
        if action == "Add Face":
            self.add_face_ui()
        elif action == "Delete Face":
            self.delete_face_ui()
        elif action == "Update Face":
            self.update_face_ui()

    def add_face_ui(self):
        method, ok = get_selection_input(self, "Add Face", "Select input method:", ["From Image File", "From Camera"])
        if not ok:
            return

        if method == "From Image File":
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
            if not file_name:
                return

            img_rgb = load_rgb_image(file_name)
            if img_rgb is None:
                show_warning_message(self, "Error", "Failed to load image.")
                return

            self.embedding = extract_embedding(img_rgb)

        else:  # From Camera
            capture_dialog = CaptureFaceDialog(self)
            if capture_dialog.exec_() != QDialog.Accepted:
                return

            self.embedding = capture_dialog.get_embedding()
            if self.embedding is None:
                show_warning_message(self, "Error", "No face detected.")
                return

        name, ok = get_text_input(self, "Enter Name", "Enter the person's name:")
        if not ok or not name.strip():
            return

        if self.embedding is not None:
            success = self.db.add_new_face(name.strip(), self.embedding.cpu().numpy().tobytes())
            if success:
                show_info_message(self, "Success", f"{name} added to database.")
            else:
                show_warning_message(self, "Duplicate", f"{name} already exists.")

    def delete_face_ui(self):
        names = self.db.view_faces()
        if not names:
            show_warning_message(self, "Error", "No faces stored in the database.")
            return

        name, ok = get_selection_input(self, "Delete Face", "Select a name:", names)
        if not ok:
            return

        self.db.delete_face(name)
        show_info_message(self, "Success", f"{name} deleted.")

    def update_face_ui(self):
        names = self.db.view_faces()
        if not names:
            show_warning_message(self, "Error", "No faces stored in the database.")
            return

        name, ok = get_selection_input(self, "Update Face", "Select a name:", names)
        if not ok:
            return

        file_name, _ = QFileDialog.getOpenFileName(self, "Select New Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_name:
            return

        img_rgb = load_rgb_image(file_name)
        if img_rgb is None:
            show_warning_message(self, "Error", "Failed to load image.")
            return

        new_embedding = extract_embedding(img_rgb)
        if new_embedding is not None:
            self.db.update_face(name, new_embedding.tobytes())
            show_info_message(self, "Success", f"{name} updated.")
        else:
            show_warning_message(self, "Error", "No face detected.")
