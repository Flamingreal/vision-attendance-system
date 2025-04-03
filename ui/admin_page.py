from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox
from ui.manage_face_dialog import ManageFaceDialog

class AdminPage(QWidget):
    def __init__(self, db, logout_callback=None):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.setWindowTitle("Admin Dashboard")

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Welcome, Admin"))
        self.layout.addWidget(QLabel("Here you can manage user roles."))

        manage_button = QPushButton("Manage Faces")
        manage_button.clicked.connect(self.open_manage_faces)
        self.layout.addWidget(manage_button)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        refresh_btn = QPushButton("Refresh User List")
        refresh_btn.clicked.connect(self.load_user_data)
        self.layout.addWidget(refresh_btn)

        update_btn = QPushButton("Update Roles")
        update_btn.clicked.connect(self.update_roles)
        self.layout.addWidget(update_btn)

        back_button = QPushButton("Logout")
        back_button.clicked.connect(self.logout)
        self.layout.addWidget(back_button)

        self.setLayout(self.layout)
        self.load_user_data()

    def load_user_data(self):
        users = self.db.get_all_users()
        self.table.setRowCount(len(users))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Username", "Role"])

        for row, (username, role) in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(username))
            combo = QComboBox()
            combo.addItems(["Student", "Teacher", "Admin", "Developer"])
            combo.setCurrentText(role)
            self.table.setCellWidget(row, 1, combo)

    def update_roles(self):
        for row in range(self.table.rowCount()):
            username = self.table.item(row, 0).text()
            role_widget = self.table.cellWidget(row, 1)
            new_role = role_widget.currentText()
            self.db.update_user_role(username, new_role)
        QMessageBox.information(self, "Success", "User roles updated.")

    def open_manage_faces(self):
        ManageFaceDialog.launch_if_needed(self, self.db)

    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def cleanup(self):
        pass
