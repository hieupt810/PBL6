import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from transformers import ViTForImageClassification


def load_trained_model(num_classes: int = 10):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load the pre-trained ViT model and replace the head classifier
    model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224").to(
        device
    )
    model.classifier = nn.Sequential(
        nn.Linear(in_features=768, out_features=512),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(in_features=512, out_features=256),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(in_features=256, out_features=num_classes, bias=False),
    )

    # Load the trained weights
    checkpoint = torch.load("app/model.pt", map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model"])

    return model


def predict(image_path: str):
    model = load_trained_model()
    model.eval()

    # Load and preprocess the image
    image = Image.open(image_path)
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.transpose(image, (2, 0, 1))
    image = torch.tensor(image, dtype=torch.float).unsqueeze(0)

    # Make a prediction
    with torch.no_grad():
        logits = model(image)["logits"]
        probabilities = torch.softmax(logits, dim=-1).squeeze(0)

    return probabilities
