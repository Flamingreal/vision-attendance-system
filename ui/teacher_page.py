from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt
from ui.manage_face_dialog import ManageFaceDialog


class TeacherPage(QWidget):
    def __init__(self, db, logout_callback=None):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.setWindowTitle("Teacher Dashboard")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Welcome, Teacher"))
        layout.addWidget(QLabel("View and filter student attendance records."))

        manage_button = QPushButton("Manage Faces")
        manage_button.clicked.connect(self.open_manage_faces)
        layout.addWidget(manage_button)

        # Filter input
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter by student name...")
        filter_btn = QPushButton("Apply Filter")
        filter_btn.clicked.connect(self.refresh_table)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(filter_btn)
        layout.addLayout(filter_layout)

        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(2)
        self.attendance_table.setHorizontalHeaderLabels(["Name", "Timestamp"])
        layout.addWidget(self.attendance_table)

        # Logout
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        self.setLayout(layout)
        self.refresh_table()

    def refresh_table(self):
        filter_text = self.filter_input.text().strip().lower()
        all_records = self.db.get_attendance_records()
        filtered = [r for r in all_records if filter_text in r[0].lower()]

        self.attendance_table.setRowCount(len(filtered))
        for row, (name, timestamp) in enumerate(filtered):
            self.attendance_table.setItem(row, 0, QTableWidgetItem(name))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(timestamp))

    def open_manage_faces(self):
        ManageFaceDialog.launch_if_needed(self, self.db)

    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def cleanup(self):
        pass
