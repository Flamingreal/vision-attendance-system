import torch
from facenet_pytorch import MTCNN, InceptionResnetV1

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load MTCNN and ResNet models
mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20,
              thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True, device=device)
resnet = InceptionResnetV1(pretrained="vggface2").eval().to(device)


def extract_embedding(image_rgb):
    """
    Extract facial embedding from an RGB image using MTCNN and ResNet.

    Args:
        image_rgb (np.ndarray): Input RGB image.

    Returns:
        torch.Tensor or None: Facial embedding tensor, or None if no face detected.
    """
    #print("[DEBUG] extract_embedding called with:", type(image_rgb))

    # Detect face
    face = mtcnn(image_rgb)
    if face is None:
        print("No face detected.")
        return None

    face = face.to(device)
    with torch.no_grad():
        embedding = resnet(face.unsqueeze(0)).squeeze(0)

    #print("[DEBUG] embedding shape:", embedding.shape)
    return embedding
