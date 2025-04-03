from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from database import DatabaseManager


class LoginDialog(QDialog):
    def __init__(self, db: DatabaseManager, login_callback):
        super().__init__()
        self.db = db
        self.login_callback = login_callback

        self.setWindowTitle("Login")
        self.setMinimumWidth(300)

        # Username and password input
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Buttons
        button_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.setDefault(True)
        login_btn.clicked.connect(self.handle_login)
        button_layout.addWidget(login_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_login)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        role = self.db.get_user_role(username, password)
        if role:
            self.login_callback(username, role)
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")

    def cancel_login(self):
        self.reject()

    def get_credentials(self):
        return self.username_input.text().strip(), self.password_input.text().strip()
