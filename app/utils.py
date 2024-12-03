import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification, ViTImageProcessor


def load_trained_model(num_classes: int, device: torch.device):
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

    # Load the image processor
    processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
    transform = transforms.Compose(
        [
            transforms.Resize(size=(224, 224), antialias=True),
            transforms.ToTensor(),
            transforms.Normalize(mean=processor.image_mean, std=processor.image_std),
        ]
    )

    # Load the trained weights
    checkpoint = torch.load("app/model.pt", map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])

    return model, transform


def predict(path: str):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, transform = load_trained_model(num_classes=10, device=device)
    model.eval()

    image = transform(Image.open(path)).unsqueeze(0).to(device)
    outputs = model(image).logits
    _, predicted = torch.max(outputs, 1)

    return predicted.item()
