from PyQt5.QtWidgets import QDialog, QFileDialog
from ui.utils import (
    show_info_message,
    show_warning_message,
    get_text_input,
    get_selection_input,
    load_rgb_image
)
from face_models import extract_embedding
from database import DatabaseManager  # for type hint only


class ManageFaceDialog(QDialog):
    def __init__(self, parent=None, db: DatabaseManager = None, action: str = None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Manage Faces")

        if action == "Add Face":
            self.add_face_ui()
        elif action == "Delete Face":
            self.delete_face_ui()
        elif action == "Update Face":
            self.update_face_ui()

    @staticmethod
    def launch_if_needed(parent, db: DatabaseManager):
        """
        Prompt the user to select an action and launch the corresponding dialog.

        Args:
            parent: The parent widget.
            db (DatabaseManager): Shared database instance.
        """
        options = ["Add Face", "Delete Face", "Update Face"]
        action, ok = get_selection_input(parent, "Manage Faces", "Select an action:", options)

        if not ok or not action:
            return

        dialog = ManageFaceDialog(parent, db, action)
        dialog.exec_()

    def add_face_ui(self):
        """Add a new face to the database."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_name:
            return

        img_rgb = load_rgb_image(file_name)
        if img_rgb is None:
            show_warning_message(self, "Error", "Failed to load image.")
            return

        name, ok = get_text_input(self, "Enter Name", "Enter the person's name:")
        if not ok or not name.strip():
            return

        embedding = extract_embedding(img_rgb)
        if embedding is not None:
            success = self.db.add_new_face(name.strip(), embedding.cpu().numpy().tobytes())
            if success:
                show_info_message(self, "Success", f"{name} added to database.")
            else:
                show_warning_message(self, "Duplicate", f"{name} already exists in the database.")
        else:
            show_warning_message(self, "Error", "No face detected in the image.")

    def delete_face_ui(self):
        """Delete an existing face from the database."""
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
        """Update a stored face with a new image."""
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
            show_warning_message(self, "Error", "No face detected in the new image.")
