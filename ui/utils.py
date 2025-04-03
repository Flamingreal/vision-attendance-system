from PyQt5.QtWidgets import QMessageBox, QInputDialog
import cv2
from PyQt5.QtWidgets import QDialog

def show_info_message(parent, title, message):
    """
    Show an information message box.
    """
    QMessageBox.information(parent, title, message)

def show_warning_message(parent, title, message):
    """
    Show a warning message box.
    """
    QMessageBox.warning(parent, title, message)

def show_error_message(parent, title, message):
    """
    Show an error message box.
    """
    QMessageBox.critical(parent, title, message)

def get_text_input(parent, title, label):
    """
    Prompt the user to enter a text input.
    Returns a tuple (text, ok).
    """
    return QInputDialog.getText(parent, title, label)

def get_selection_input(parent, title, label, items):
    item, ok = QInputDialog.getItem(parent, title, label, items, 0, False)
    return item, ok

def load_rgb_image(path: str):
    """
    Load image from disk and convert to RGB.

    Args:
        path (str): File path.

    Returns:
        np.ndarray or None: RGB image if successful, else None.
    """
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        return None
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
