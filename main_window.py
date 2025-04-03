from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QDialog
from ui.dashboard_page import DashboardPage
from ui.login_dialog import LoginDialog
from ui.student_page import StudentPage
from ui.teacher_page import TeacherPage
from ui.admin_page import AdminPage
from ui.developer_page import DeveloperPage
from database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Attendance System")
        self.db = DatabaseManager()

        # QStackedWidget to switch between dashboard and role pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initial dashboard (no login required)
        self.dashboard = DashboardPage(self.db, self.request_login)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)

        # LoginDialog is modal, no need to add to stack
        self.login_dialog = LoginDialog(self.db, self.handle_login_success)

        # Role pages
        self.student_page = None
        self.teacher_page = None
        self.admin_page = None
        self.developer_page = None

    def request_login(self):
        """
        Triggered from DashboardPage when user clicks login.
        Shows modal login dialog.
        """
        self.login_dialog.username_input.clear()
        self.login_dialog.password_input.clear()
        result = self.login_dialog.exec_()
        if result != QDialog.Accepted:
            return  # Cancelled = stay on dashboard

    def handle_login_success(self, username: str, role: str):
        """
        Switch to role-specific page after successful login.
        """
        role = role.lower()
        if role == "student":
            if not self.student_page:
                self.student_page = StudentPage(username, self.db, self.logout)
                self.stack.addWidget(self.student_page)
            self.stack.setCurrentWidget(self.student_page)

        elif role == "teacher":
            if not self.teacher_page:
                self.teacher_page = TeacherPage(self.db, self.logout)
                self.stack.addWidget(self.teacher_page)
            self.stack.setCurrentWidget(self.teacher_page)

        elif role == "admin":
            if not self.admin_page:
                self.admin_page = AdminPage(self.db, self.logout)
                self.stack.addWidget(self.admin_page)
            self.stack.setCurrentWidget(self.admin_page)

        elif role == "developer":
            if not self.developer_page:
                self.developer_page = DeveloperPage(self.db, self.logout)
                self.stack.addWidget(self.developer_page)
            self.stack.setCurrentWidget(self.developer_page)

    def logout(self):
        """
        Called from role pages to logout.
        Clears widgets and returns to dashboard.
        """
        if self.student_page:
            self.student_page.cleanup()
            self.stack.removeWidget(self.student_page)
            self.student_page = None
        if self.teacher_page:
            self.teacher_page.cleanup()
            self.stack.removeWidget(self.teacher_page)
            self.teacher_page = None
        if self.admin_page:
            self.stack.removeWidget(self.admin_page)
            self.admin_page = None
        if self.developer_page:
            self.stack.removeWidget(self.developer_page)
            self.developer_page = None

        self.request_login()

    def closeEvent(self, event):
        if self.student_page:
            self.student_page.cleanup()
        if self.teacher_page:
            self.teacher_page.cleanup()
        self.db.close()
        event.accept()
