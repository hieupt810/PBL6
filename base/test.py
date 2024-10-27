import os

import torch
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from transformers import ViTForImageClassification, ViTImageProcessor


def load_test_dataset(
    transform: transforms.Compose,
    root: str = "/",
    folder: str = "test",
    batch_size: int = 32,
):
    """Load the test dataset and create the DataLoader"""
    dir = os.path.join(root, "dataset", folder)
    dataset = ImageFolder(root=dir, transform=transform)
    loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=False)

    return loader


def load_trained_model(filename: str, model: str, root: str = "/"):
    """Load the model and the transform function"""
    dir = os.path.join(root, filename)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load the model
    model = ViTForImageClassification.from_pretrained(model)
    processor = ViTImageProcessor.from_pretrained(model)

    # Load the weights
    model.load_state_dict(torch.load(dir, map_location=device, weights_only=True))

    # Transform function
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=processor.image_mean, std=processor.image_std),
        ]
    )

    return model, transform, device


# Load the model and the test dataset
model, transform, device = load_trained_model(
    filename="model_5.pth", model="google/vit-base-patch16-224"
)
test_loader = load_test_dataset(transform, folder="train")

# Test the model
correct, total = 0, 0
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images).logits
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

# Print the accuracy
print(f"Accuracy: {100 * correct / total:.2f}%")
