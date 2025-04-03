from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

class StudentPage(QWidget):
    def __init__(self, username, db, logout_callback=None):
        super().__init__()
        self.username = username
        self.db = db
        self.logout_callback = logout_callback
        self.setWindowTitle("Student Dashboard")

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Welcome, {self.username}"))
        layout.addWidget(QLabel("This is your personal information panel."))

        # Table showing student's attendance records
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(2)
        self.attendance_table.setHorizontalHeaderLabels(["Name", "Timestamp"])
        layout.addWidget(self.attendance_table)

        self.refresh_attendance()

        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        self.setLayout(layout)

    def refresh_attendance(self):
        records = self.db.get_attendance_records()
        student_records = [r for r in records if r[0] == self.username]
        self.attendance_table.setRowCount(len(student_records))

        for row, (name, timestamp) in enumerate(student_records):
            self.attendance_table.setItem(row, 0, QTableWidgetItem(name))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(timestamp))

    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def cleanup(self):
        pass  # add cleanup logic later if needed
