# Vision-Based Attendance System

## Overview
This project implements a facial recognition-based attendance system using FaceNet and MTCNN. It matches real-time captured images with a stored reference database of face embeddings.

## Features
- Face detection using MTCNN
- Face recognition using FaceNet (pretrained model)
- Embeddings stored in `face_embeddings.npy`
- Matching captured images with reference images

## Folder Structure
```
vision-attendance-system/
│── data/
│   │── reference_faces/  # Reference images for known individuals
│   │── test_reference_images/  # Used for initial embedding creation
│   │── captured_faces/  # Images captured during attendance
│   │── face_embeddings.npy  # Stored facial embeddings
│── src/
│   │── extract_embeddings.ipynb  # Generates embeddings for reference images
│   │── match_faces.ipynb  # Matches captured images with stored embeddings
│── README.md  # Project documentation
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Flamingreal/vision-attendance-system.git
   cd vision-attendance-system
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download the pretrained FaceNet model:
   ```bash
   # Model will be downloaded automatically when running the code
   ```

## Usage
### 1. Create Embeddings
Run the notebook to generate face embeddings for reference images:
```bash
jupyter notebook src/extract_embeddings.ipynb
```

### 2. Match Captured Faces
Run the notebook to recognize faces from captured images:
```bash
jupyter notebook src/match_faces.ipynb
```

## To-Do List
### Database
- [ ] Optimize storage for embeddings
- [ ] Improve face matching accuracy

### UI
- [ ] Develop a GUI for easy interaction
- [ ] Implement real-time camera feed integration
or easier use
- [ ] Support more real-time image processing techniques
