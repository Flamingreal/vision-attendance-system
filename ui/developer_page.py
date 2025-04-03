from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox
)
from database import DatabaseManager
from ui.manage_face_dialog import ManageFaceDialog

class DeveloperPage(QWidget):
    def __init__(self, db: DatabaseManager, logout_callback=None):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.setWindowTitle("Developer Dashboard")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Welcome, Developer"))
        layout.addWidget(QLabel("Use this area to test developer tools or diagnostics."))

        manage_button = QPushButton("Manage Faces")
        manage_button.clicked.connect(self.open_manage_faces)
        layout.addWidget(manage_button)

        # Show face count button
        face_count_button = QPushButton("Show Face Count")
        face_count_button.clicked.connect(self.show_face_count)
        layout.addWidget(face_count_button)

        # Test feature button
        test_btn = QPushButton("Run Test Feature")
        test_btn.clicked.connect(self.test_feature)
        layout.addWidget(test_btn)

        # Logout button
        back_button = QPushButton("Logout")
        back_button.clicked.connect(self.logout)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def show_face_count(self):
        """
        Count number of face entries in the database.
        """
        all_faces = self.db.view_faces()
        QMessageBox.information(self, "Face Count", f"Total faces stored: {len(all_faces)}")

    def test_feature(self):
        """
        Placeholder for any internal developer test.
        """
        QMessageBox.information(self, "Test Feature", "This is a placeholder for developer testing.")

    def open_manage_faces(self):
        ManageFaceDialog.launch_if_needed(self, self.db)

    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def cleanup(self):
        pass
