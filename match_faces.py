#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import cv2
from scipy.spatial.distance import cosine
import os

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load FaceNet and MTCNN models
model = InceptionResnetV1(pretrained="vggface2").to(device).eval()
mtcnn = MTCNN(keep_all=False, device=device)

# Path to stored embeddings
embeddings_path = r"C:\Code\vision-attendance-system\face_embeddings.npy"

# Load stored embeddings if exists, else create an empty dictionary
if os.path.exists(embeddings_path):
    face_embeddings = np.load(embeddings_path, allow_pickle=True).item()
else:
    face_embeddings = {}

# Threshold
THRESHOLD = 0.3  

def match_face(image_path):
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return "Error: Cannot read image.", None

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    face = mtcnn(img_rgb)
    if face is None:
        return "No face detected.", None

    # Extract embedding
    with torch.no_grad():
        embedding = model(face.unsqueeze(0).to(device)).cpu().numpy().flatten()

    # Find the best match
    best_match = None
    min_distance = float("inf")

    for person_id, stored_embedding in face_embeddings.items():
        distance = cosine(embedding, stored_embedding)
        if distance < min_distance:
            min_distance = distance
            best_match = person_id

    if min_distance < THRESHOLD:
        return best_match, min_distance
    else:
        return "Unknown", min_distance

def add_new_face(image_path, person_id):
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return "Error: Cannot read image."

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    face = mtcnn(img_rgb)
    if face is None:
        return "No face detected."

    # Extract embedding
    with torch.no_grad():
        embedding = model(face.unsqueeze(0).to(device)).cpu().numpy().flatten()

    # Store new embedding
    face_embeddings[person_id] = embedding
    np.save(embeddings_path, face_embeddings)
    return f"New face added: {person_id}"


# In[ ]:




