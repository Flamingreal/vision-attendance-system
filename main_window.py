from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QToolBar, QAction
from ui.dashboard_page import DashboardPage
from ui.admin_page import AdminPage
from database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Attendance System")
        self.resize(1000, 600)

        # Initialize database manager
        self.db = DatabaseManager()

        # Stack for switching between dashboard and admin pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create the main pages
        self.dashboard = DashboardPage(self.db)
        self.admin_page = AdminPage(self.db)

        # Add pages to the stack
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.admin_page)
        self.stack.setCurrentWidget(self.dashboard)

        # Initialize toolbar for mode switching
        self.init_toolbar()

    def init_toolbar(self):
        """Creates the top toolbar with navigation actions."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Action for switching to recording mode (dashboard)
        recording_action = QAction("Recording Mode", self)
        recording_action.triggered.connect(self.switch_to_recording_mode)
        toolbar.addAction(recording_action)

        # Action for switching to admin mode
        admin_action = QAction("Admin Mode", self)
        admin_action.triggered.connect(self.switch_to_admin_mode)
        toolbar.addAction(admin_action)

    def switch_to_recording_mode(self):
        """Switch to the dashboard and clean up admin state if needed."""
        if hasattr(self.admin_page, "cleanup"):
            self.admin_page.cleanup()

        self.stack.setCurrentWidget(self.dashboard)

    def switch_to_admin_mode(self):
        """Switch to the admin page and stop the camera if running."""
        if hasattr(self.dashboard, "camera") and self.dashboard.camera is not None:
            self.dashboard.camera.stop()

        self.stack.setCurrentWidget(self.admin_page)

    def closeEvent(self, event):
        """Handle application close: stop camera and close database."""
        if hasattr(self.dashboard, "cleanup"):
            self.dashboard.cleanup()
        if hasattr(self.admin_page, "cleanup"):
            self.admin_page.cleanup()
        self.db.close()
        event.accept()
