import sqlite3
import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
import cv2

# Database file path
DATABASE_PATH = "face_database.db"

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load models
mtcnn = MTCNN(keep_all=False, device=device)
resnet = InceptionResnetV1(pretrained="vggface2").eval().to(device)


def initialize_database():
    """Create the face database if it does not exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            embedding BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_new_face(image_path, name):
    """Extracts face embedding and stores it in the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Cannot read image.")
        return

    # Convert color and detect face
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face = mtcnn(img_rgb)
    if face is None:
        print("Error: No face detected.")
        return

    # Extract embedding
    with torch.no_grad():
        embedding = resnet(face.unsqueeze(0).to(device)).cpu().numpy().flatten()

    # Insert into database
    try:
        cursor.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", (name, embedding.tobytes()))
        conn.commit()
        print(f"Added {name} to database.")
    except sqlite3.IntegrityError:
        print(f"Error: The name '{name}' already exists in the database.")

    conn.close()


def delete_face(name):
    """Deletes a face entry from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faces WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    print(f"Deleted {name} from database.")


def update_face(name, new_image_path):
    """Updates an existing face's embedding with a new image."""
    delete_face(name)  # Delete old entry
    add_new_face(new_image_path, name)  # Add updated face
    print(f"Updated {name}'s face in database.")


def view_faces():
    """Returns a list of all stored names in the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM faces")
    faces = [row[0] for row in cursor.fetchall()]
    conn.close()
    return faces


def match_face(image_path):
    """Compares a given image with stored embeddings to find the closest match."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, embedding FROM faces")
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("No faces stored in the database.")
        return None, None

    # Read input image
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print("Error: Cannot read image.")
        return None, None

    # Convert color and detect face
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    face = mtcnn(img_rgb)
    if face is None:
        print("Error: No face detected.")
        return None, None

    # Extract embedding
    with torch.no_grad():
        embedding = resnet(face.unsqueeze(0).to(device)).cpu().numpy().flatten()

    best_match = None
    min_distance = float("inf")
    THRESHOLD = 0.3  # Set recognition threshold

    # Compare with stored embeddings
    for name, stored_embedding in data:
        stored_embedding = np.frombuffer(stored_embedding, dtype=np.float32)
        distance = np.linalg.norm(embedding - stored_embedding)
        if distance < min_distance:
            min_distance = distance
            best_match = name

    if min_distance < THRESHOLD:
        return best_match, min_distance
    else:
        return None, min_distance


# Initialize database when script is run
initialize_database()
