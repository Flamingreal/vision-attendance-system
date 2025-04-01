import cv2
from facenet_pytorch import MTCNN
import numpy as np
import threading
import time
from PyQt5.QtCore import pyqtSignal, QObject

class Camera(QObject):
    frame_signal = pyqtSignal(np.ndarray)  # Signal emitted to update UI with frame

    def __init__(self, device=0):
        super().__init__()
        self.device = device
        self.capture = cv2.VideoCapture(self.device)
        self.mtcnn = MTCNN()
        self.running = False
        self.thread = None

    def start(self):
        if not self.capture.isOpened():
            print(f"Error: Could not open camera {self.device}")
            return
        self.running = True
        self.thread = threading.Thread(target=self.capture_frames)
        self.thread.daemon = True
        self.thread.start()

    def capture_frames(self):
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Prepare RGB image for face detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = self.mtcnn.detect(rgb_frame)[0]  # Only take the boxes

            # Draw bounding boxes on the BGR frame
            if faces is not None:
                for bbox in faces:
                    if bbox is None or len(bbox) != 4:
                        continue
                    x1, y1, x2, y2 = [int(v) for v in bbox]
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(frame.shape[1], x2)
                    y2 = min(frame.shape[0], y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Emit the processed frame
            self.frame_signal.emit(frame)

            # Optional: limit FPS to ~30
            time.sleep(1 / 30)

    def stop(self):
        self.running = False
        if self.capture.isOpened():
            self.capture.release()

    def is_running(self):
        return self.running
