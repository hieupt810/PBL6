import os

import torch
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from transformers import ViTForImageClassification, ViTImageProcessor


def load_test_dataset(
    transform: transforms.Compose,
    folder: str = "test",
    root: str = os.path.dirname(os.path.abspath(__file__)),
    batch_size: int = 32,
):
    """Load the test dataset and create the DataLoader"""
    dir = os.path.join(root, folder)
    dataset = ImageFolder(root=dir, transform=transform)
    loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=False)

    return loader


def load_trained_model(
    model_name: str,
    base_model: str,
    root: str = os.path.dirname(os.path.abspath(__file__)),
):
    """Load the model and the transform function"""
    dir = os.path.join(root, model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load the model
    model = ViTForImageClassification.from_pretrained(base_model)
    feature_extractor = ViTImageProcessor.from_pretrained(base_model)

    # Load the weights
    model.load_state_dict(torch.load(dir, map_location=device, weights_only=True))

    # Transform function
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=feature_extractor.image_mean, std=feature_extractor.image_std
            ),
        ]
    )

    return model, transform, device


model, transform, device = load_trained_model(
    model_name="checkpoints/model_10.pth", base_model="google/vit-base-patch16-224"
)
test_loader = load_test_dataset(transform, folder="train")

correct, total = 0, 0
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images).logits
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f"Accuracy: {100 * correct / total:.2f}%")
