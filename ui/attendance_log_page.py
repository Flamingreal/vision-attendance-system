from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt
from datetime import datetime

class AttendanceLogPage(QWidget):
    def __init__(self, db, back_callback):
        super().__init__()
        self.db = db
        self.back_callback = back_callback

        self.layout = QVBoxLayout(self)

        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(2)
        self.attendance_table.setHorizontalHeaderLabels(["Name", "Timestamp"])
        self.layout.addWidget(self.attendance_table)

        # Back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_callback)
        self.layout.addWidget(self.back_button)

    def refresh_log_table(self):
        records = self.db.get_attendance_records()
        self.attendance_table.setRowCount(len(records))

        for row, (name, timestamp) in enumerate(records):
            self.attendance_table.setItem(row, 0, QTableWidgetItem(name))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(timestamp))
