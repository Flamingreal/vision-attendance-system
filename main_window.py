from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QToolBar, QAction
from ui.dashboard_page import DashboardPage
from ui.admin_page import AdminPage
from database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Attendance System")
        self.resize(1000, 600)

        self.db = DatabaseManager()

        # QStackedWidget to manage different views
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.dashboard = DashboardPage(self.db)
        self.admin_page = AdminPage(self.db)

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.admin_page)
        self.stack.setCurrentWidget(self.dashboard)

        # Top toolbar for switching modes
        self.init_toolbar()

    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        recording_action = QAction("Recording Mode", self)
        recording_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.dashboard))
        toolbar.addAction(recording_action)

        admin_action = QAction("Admin Mode", self)
        admin_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.admin_page))
        toolbar.addAction(admin_action)

    def closeEvent(self, event):
        # Cleanup if needed (e.g. stop camera, save state)
        if hasattr(self.dashboard, "cleanup"):
            self.dashboard.cleanup()
        if hasattr(self.admin_page, "cleanup"):
            self.admin_page.cleanup()
        self.db.close()
        event.accept()
