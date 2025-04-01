from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from ui.dashboard_page import DashboardPage
from ui.attendance_log_page import AttendanceLogPage
from database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Attendance System")
        self.db = DatabaseManager()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.dashboard = DashboardPage(self.db, self.show_logs)
        self.logs_page = AttendanceLogPage(self.db, self.show_dashboard)

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.logs_page)

        self.show_dashboard()

    def show_logs(self):
        self.logs_page.refresh_log_table()
        self.stack.setCurrentWidget(self.logs_page)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def closeEvent(self, event):
        self.dashboard.cleanup()
        self.db.close()
        event.accept()
