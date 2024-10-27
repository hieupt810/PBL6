import os

import torch
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from tqdm import tqdm
from transformers import ViTForImageClassification, ViTImageProcessor


def load_test_dataset(
    transform: transforms.Compose, root: str = "/content", batch_size: int = 32
):
    def load_dataset(folder: str, shuffle: bool = False):
        dir = os.path.join(root, "dataset", folder)
        dataset = ImageFolder(root=dir, transform=transform)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
        return loader

    return load_dataset("test")


def load_trained_model(filename: str, name: str, root: str = "/content"):
    dir = os.path.join(root, filename)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load the model
    model = ViTForImageClassification.from_pretrained(name)
    processor = ViTImageProcessor.from_pretrained(name)

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
root = os.path.abspath(os.path.dirname(__file__))
model, transform, device = load_trained_model(
    filename="checkpoint6.pth", name="google/vit-base-patch16-224", root=root
)
test_loader = load_test_dataset(transform=transform, root=root)

# Test the model
correct, total = 0, 0
with torch.no_grad():
    for images, labels in tqdm(test_loader, desc="Testing"):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images).logits
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

# Print the accuracy
print(f"Accuracy: {100 * correct / total:.2f}%")
