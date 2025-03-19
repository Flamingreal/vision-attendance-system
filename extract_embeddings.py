import torch
import numpy as np
import sqlite3
import os
import cv2
from facenet_pytorch import InceptionResnetV1, MTCNN

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load FaceNet model
model = InceptionResnetV1(pretrained="vggface2").to(device).eval()
mtcnn = MTCNN(keep_all=False, device=device)

# SQLite database path
DB_PATH = "data/attendance.db"


def add_student(name, embedding):
    """Inserts new student face embeddings into the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        embedding_bytes = embedding.tobytes()
        cursor.execute("INSERT INTO students (name, embedding) VALUES (?, ?)", (name, embedding_bytes))
        conn.commit()
        print(f"Student {name} added successfully.")
    except sqlite3.IntegrityError:
        print(f"Student {name} already exists in the database.")

    conn.close()


# Set dataset path
dataset_path = "data/reference_faces"

# Iterate through reference faces
for file_name in os.listdir(dataset_path):
    file_path = os.path.join(dataset_path, file_name)

    # Read image
    img = cv2.imread(file_path)
    if img is None:
        print(f"Warning: Could not read {file_name}. Skipping...")
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect face
    face = mtcnn(img_rgb)
    if face is None:
        print(f"Warning: No face detected in {file_name}. Skipping...")
        continue

    # Extract embedding
    with torch.no_grad():
        embedding = model(face.unsqueeze(0).to(device)).cpu().numpy().flatten()

    # Store in database
    person_id = os.path.splitext(file_name)[0]  # Use filename as ID
    add_student(person_id, embedding)
