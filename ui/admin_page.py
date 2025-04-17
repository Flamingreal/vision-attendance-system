from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem
)
from ui.utils import load_rgb_image, show_info_message, show_warning_message
from face_models import extract_embedding
from ui.capture_face_dialog import CaptureFaceDialog
from database import DatabaseManager
from PyQt5.QtWidgets import QDateEdit
import csv


class AdminPage(QWidget):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.setWindowTitle("Admin Mode")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Top-level buttons
        self.manage_btn = QPushButton("Manage Faces")
        self.manage_btn.clicked.connect(self.show_manage_faces)
        self.layout.addWidget(self.manage_btn)

        self.list_btn = QPushButton("List Attendance")
        self.list_btn.clicked.connect(self.show_attendance)
        self.layout.addWidget(self.list_btn)

        # Sub-buttons for face management
        self.sub_button_layout = QHBoxLayout()
        self.layout.addLayout(self.sub_button_layout)

        self.add_btn = QPushButton("Add Face")
        self.add_btn.clicked.connect(lambda: self.show_manage_faces('add'))
        self.sub_button_layout.addWidget(self.add_btn)
        self.add_btn.hide()

        self.del_btn = QPushButton("Delete Face")
        self.del_btn.clicked.connect(lambda: self.show_manage_faces('delete'))
        self.sub_button_layout.addWidget(self.del_btn)
        self.del_btn.hide()

        self.update_btn = QPushButton("Update Face")
        self.update_btn.clicked.connect(lambda: self.show_manage_faces('update'))
        self.sub_button_layout.addWidget(self.update_btn)
        self.update_btn.hide()

        self.view_btn = QPushButton("View Face List")
        self.view_btn.clicked.connect(lambda: self.show_manage_faces('view'))
        self.sub_button_layout.addWidget(self.view_btn)
        self.view_btn.hide()

        self.control_layout = QVBoxLayout()
        self.layout.addLayout(self.control_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Names"])
        self.layout.addWidget(self.table)

        self.pending_embedding = None

    def clear_controls(self):
        for i in reversed(range(self.control_layout.count())):
            item = self.control_layout.itemAt(i)
            if item.layout():
                while item.layout().count():
                    w = item.layout().takeAt(0).widget()
                    if w:
                        w.setParent(None)
            elif item.widget():
                item.widget().setParent(None)

    def show_manage_faces(self, mode=None):
        self.add_btn.show()
        self.del_btn.show()
        self.update_btn.show()
        self.view_btn.show()
        self.clear_controls()
        self.table.clearContents()
        self.table.setRowCount(0)

        # Reset table structure
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Names"])
        self.table.setColumnHidden(0, False)

        if mode == 'add':
            self.show_add_face()
        elif mode == 'delete':
            self.show_delete_face()
        elif mode == 'update':
            self.show_update_face()
        elif mode == 'view':
            self.show_face_list()

    def show_attendance(self):
        # Hide face management buttons
        self.add_btn.hide()
        self.del_btn.hide()
        self.update_btn.hide()
        self.view_btn.hide()
        self.clear_controls()

        # Filter section layout
        filter_layout = QHBoxLayout()

        # Name filter input
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name")
        filter_layout.addWidget(name_input)

        # Date filter input
        date_input = QDateEdit()
        date_input.setDisplayFormat("yyyy-MM-dd")
        date_input.setCalendarPopup(True)
        filter_layout.addWidget(date_input)

        # Search button
        search_btn = QPushButton("Search")
        filter_layout.addWidget(search_btn)

        # Export button
        export_btn = QPushButton("Export CSV")
        filter_layout.addWidget(export_btn)

        # Delete button
        delete_btn = QPushButton("Delete Selected")
        filter_layout.addWidget(delete_btn)

        self.control_layout.addLayout(filter_layout)

        # Table setup
        records = self.db.get_attendance_records()
        self.table.clearContents()
        self.table.setRowCount(len(records))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Timestamp"])
        self.table.setColumnHidden(0, True)

        for row, (id_, name, timestamp) in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(str(id_)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(timestamp))

        # Search logic
        def apply_filters():
            name = name_input.text().strip()
            date = date_input.date().toString("yyyy-MM-dd")
            if not name:
                name = None
            if not date_input.date().isValid():
                date = None
            filtered = self.db.get_attendance_records(name=name, date=date)

            self.table.setRowCount(len(filtered))
            for row, (id_, name, timestamp) in enumerate(filtered):
                self.table.setItem(row, 0, QTableWidgetItem(str(id_)))
                self.table.setItem(row, 1, QTableWidgetItem(name))
                self.table.setItem(row, 2, QTableWidgetItem(timestamp))

        search_btn.clicked.connect(apply_filters)

        # Export logic
        def export_csv():
            path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
            if path:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name", "Timestamp"])
                    for row in range(self.table.rowCount()):
                        row_data = [self.table.item(row, col).text() for col in range(3)]
                        writer.writerow(row_data)
                show_info_message(self, "Exported", f"File saved to {path}")

        export_btn.clicked.connect(export_csv)

        # Delete logic
        def delete_selected():
            selected = self.table.currentRow()
            if selected < 0:
                show_info_message(self, "Error", "Please select a row to delete.")
                return
            record_id = self.table.item(selected, 0).text()
            confirm = QMessageBox.question(self, "Confirm", f"Delete record ID {record_id}?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.db.cursor.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
                self.db.conn.commit()
                apply_filters()

        delete_btn.clicked.connect(delete_selected)

    def show_add_face(self):
        self.clear_controls()
        self.pending_embedding = None

        row_layout = QHBoxLayout()
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name")
        row_layout.addWidget(name_input)

        upload_btn = QPushButton("Upload Image")
        capture_btn = QPushButton("Capture from Camera")
        confirm_btn = QPushButton("Confirm")

        row_layout.addWidget(upload_btn)
        row_layout.addWidget(capture_btn)
        row_layout.addWidget(confirm_btn)

        self.control_layout.addLayout(row_layout)

        def prepare_embedding(img):
            if img is None:
                show_warning_message(self, "Error", "No face detected.")
                return
            self.pending_embedding = extract_embedding(img)
            show_info_message(self, "Ready", "Embedding ready. Click Confirm to save.")

        def confirm_add():
            name = name_input.text().strip()
            if not name:
                show_warning_message(self, "Error", "Name cannot be empty.")
                return
            if self.pending_embedding is None:
                show_warning_message(self, "Error", "No image uploaded or captured.")
                return
            success = self.db.add_new_face(name, self.pending_embedding.cpu().numpy().tobytes())
            if success:
                show_info_message(self, "Success", f"{name} added.")
            else:
                show_warning_message(self, "Duplicate", f"{name} already exists.")
            self.show_face_list()

        upload_btn.clicked.connect(lambda: self.load_image_for_embedding(prepare_embedding))
        capture_btn.clicked.connect(lambda: self.capture_image_for_embedding(prepare_embedding))
        confirm_btn.clicked.connect(confirm_add)
        self.show_face_list()

    def show_delete_face(self):
        self.clear_controls()
        self.show_face_list()

        delete_btn = QPushButton("Delete Selected")
        self.control_layout.addWidget(delete_btn)

        def delete():
            selected = self.table.currentRow()
            if selected >= 0:
                name = self.table.item(selected, 0).text()
                self.db.delete_face(name)
                show_info_message(self, "Deleted", f"{name} removed.")
                self.show_face_list()
            else:
                show_warning_message(self, "Error", "No selection.")

        delete_btn.clicked.connect(delete)

    def show_update_face(self):
        self.clear_controls()
        self.pending_update_embedding = None

        names = self.db.view_faces()
        if not names:
            show_warning_message(self, "Error", "No faces to update.")
            return

        input_layout = QHBoxLayout()

        new_name_input = QLineEdit()
        new_name_input.setPlaceholderText("Enter new name (optional)")
        input_layout.addWidget(new_name_input)

        upload_btn = QPushButton("Upload New Image")
        confirm_btn = QPushButton("Confirm Update")
        input_layout.addWidget(upload_btn)
        input_layout.addWidget(confirm_btn)

        self.control_layout.addLayout(input_layout)

        def prepare_embedding(img):
            if img is None:
                show_warning_message(self, "Error", "No face detected.")
                return
            self.pending_update_embedding = extract_embedding(img)
            show_info_message(self, "Ready", "Image loaded.")

        def confirm_update():
            selected = self.table.currentRow()
            if selected < 0:
                show_warning_message(self, "Error", "No selection.")
                return

            old_name = self.table.item(selected, 0).text()
            new_name = new_name_input.text().strip() or old_name
            has_new_name = new_name != old_name
            has_new_image = self.pending_update_embedding is not None

            if not has_new_name and not has_new_image:
                show_warning_message(self, "Error", "No changes to update.")
                return

            if has_new_name:
                if not self.db.rename_face(old_name, new_name):
                    show_warning_message(self, "Error", f"Name '{new_name}' already exists.")
                    return
            if has_new_image:
                self.db.update_face(new_name, self.pending_update_embedding.cpu().numpy().tobytes())

            show_info_message(self, "Updated", f"{old_name} updated.")
            self.show_face_list()

        upload_btn.clicked.connect(lambda: self.load_image_for_embedding(prepare_embedding))
        confirm_btn.clicked.connect(confirm_update)
        self.show_face_list()

    def show_face_list(self):
        names = self.db.view_faces()
        self.table.clearContents()
        self.table.setRowCount(len(names))
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Names"])
        for i, name in enumerate(names):
            self.table.setItem(i, 0, QTableWidgetItem(name))

    def load_image_for_embedding(self, callback):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            img = load_rgb_image(file_name)
            callback(img)

    def capture_image_for_embedding(self, callback):
        dialog = CaptureFaceDialog(self)
        if dialog.exec_():
            img = dialog.get_captured_image()
            if hasattr(dialog, 'camera'):
                dialog.camera.stop()
            callback(img)

    def set_selected_name(self, name):
        self.selected_name = name
        show_info_message(self, "Selected", f"Selected for update: {name}")

    def cleanup(self):
        pass
