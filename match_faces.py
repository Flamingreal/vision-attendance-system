import numpy as np
import torch
import sqlite3
from facenet_pytorch import MTCNN, InceptionResnetV1
import cv2
from scipy.spatial.distance import cosine

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load FaceNet model
model = InceptionResnetV1(pretrained="vggface2").to(device).eval()
mtcnn = MTCNN(keep_all=False, device=device)

# SQLite database path
DB_PATH = "data/attendance.db"

# Load stored embeddings from database
def get_all_students():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, embedding FROM students")
    students = cursor.fetchall()
    conn.close()

    student_dict = {}
    for name, embedding_bytes in students:
        embedding = np.frombuffer(embedding_bytes, dtype=np.float32)  # Decode numpy array
        student_dict[name] = embedding
    return student_dict

THRESHOLD = 0.3  # Recommended threshold

def match_face(image_path):
    """Detects a face from the image and matches it against stored embeddings"""
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print("Cannot read image.")
        return None, None

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    face = mtcnn(img_rgb)
    if face is None:
        print("No face detected.")
        return None, None

    with torch.no_grad():
        embedding = model(face.unsqueeze(0)).cpu().numpy().flatten()

    # Load database embeddings
    face_embeddings = get_all_students()

    best_match = None
    min_distance = float("inf")

    for person_id, stored_embedding in face_embeddings.items():
        distance = cosine(embedding, stored_embedding)
        if distance < min_distance:
            min_distance = distance
            best_match = person_id

    if min_distance < THRESHOLD:
        record_attendance(best_match)
        return best_match, min_distance
    else:
        return None, min_distance

def record_attendance(student_name):
    """Records attendance for the recognized student"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance_records (student_name) VALUES (?)", (student_name,))
    conn.commit()
    conn.close()
    print(f"Attendance recorded for {student_name}.")
