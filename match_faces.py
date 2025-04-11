import numpy as np
import torch
import cv2
from scipy.spatial.distance import cosine
from face_models import mtcnn, resnet, device
from face_models import extract_embedding
import sqlite3

# Path to the SQLite database
DATABASE_PATH = "attendance_system.db"

THRESHOLD = 0.3  # Distance threshold for face match


def match_face(image_path):
    """
    Detects a face in the given image, extracts its embedding, and compares it
    to stored embeddings in the database to find the best match.

    Args:
        image_path (str): Path to the image to be recognized.

    Returns:
        tuple: (matched_name, distance) if a match is found, otherwise (None, distance)
    """
    # Load image
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print("Error: Cannot read image.")
        return None, None

    # Convert image to RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    embedding = extract_embedding(img_rgb)
    if embedding is None:
        print("[DEBUG] No face detected from input frame.")
        return None, None

    print("[DEBUG] Extracted embedding shape:", embedding.shape)

    # Compare with embeddings in the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, embedding FROM faces")
    best_match = None
    best_distance = float("inf")

    for name, blob in cursor.fetchall():
        stored_embedding = np.frombuffer(blob, dtype=np.float32)
        distance = cosine(embedding.cpu().numpy(), stored_embedding)
        print(f"[DEBUG] Comparing with {name}, distance = {distance:.4f}")
        if distance < best_distance:
            best_distance = distance
            best_match = name

    conn.close()

    if best_distance < THRESHOLD:
        return best_match, best_distance
    else:
        return None, best_distance
