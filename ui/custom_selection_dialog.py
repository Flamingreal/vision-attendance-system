from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class ActionSelectionDialog(QDialog):
    def __init__(self, parent=None, options=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Faces")
        self.setMinimumWidth(300)
        self.selected_action = None

        if options is None:
            options = ["Add Face", "Delete Face", "Update Face"]

        layout = QVBoxLayout()

        label = QLabel("Select an action:")
        layout.addWidget(label)

        # Buttons for each option
        btn_layout = QHBoxLayout()
        self.buttons = []
        for option in options:
            btn = QPushButton(option)
            btn.clicked.connect(lambda checked, opt=option: self.select(opt))
            self.buttons.append(btn)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        # Cancel button at bottom
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)

    def select(self, option):
        self.selected_action = option
        self.accept()  # close dialog and return QDialog.Accepted
