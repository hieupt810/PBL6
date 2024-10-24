import os

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from transformers import PreTrainedModel, ViTForImageClassification, ViTImageProcessor


def load_dataset(
    transform: transforms.Compose,
    root: str = os.path.dirname(os.path.abspath(__file__)),
    batch_size: int = 32,
) -> tuple[DataLoader, DataLoader]:
    """Load the dataset and create the DataLoader"""
    train_dir = os.path.join(root, "train")
    train_dataset = ImageFolder(root=train_dir, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    validate_dir = os.path.join(root, "validate")
    validate_dataset = ImageFolder(root=validate_dir, transform=transform)
    validate_loader = DataLoader(validate_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, validate_loader


def load_model(model_name: str) -> tuple[PreTrainedModel, transforms.Compose]:
    """Load the model and the transform function"""
    model = ViTForImageClassification.from_pretrained(model_name)
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    data_augmentation = transforms.Compose(
        [
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(
                brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2
            ),
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        ]
    )
    transform = transforms.Compose(
        [
            data_augmentation,
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=feature_extractor.image_mean, std=feature_extractor.image_std
            ),
        ]
    )
    print(feature_extractor.image_std)

    return model, transform


root = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(root, "models")
os.makedirs(model_dir, exist_ok=True)

model, transform = load_model(model_name="google/vit-base-patch16-224")
train_loader, validate_loader = load_dataset(transform=transform)

# Define the loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)

# Training loop
NUM_EPOCHS = 20
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

losses = []
accuracies = []
for epoch in range(NUM_EPOCHS):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images).logits
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in validate_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images).logits
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f"Epoch {epoch + 1}/{NUM_EPOCHS}")
    print("- Loss:", running_loss / len(train_loader))
    print(f"- Validation accuracy: {100 * correct / total}%")

    losses.append(running_loss / len(train_loader))
    accuracies.append(100 * correct / total)

    if (epoch + 1) % 5 == 0:
        torch.save(
            model.state_dict(), os.path.join(model_dir, f"model_{epoch + 1}.pth")
        )

plt.plot(losses, label="Training loss")
plt.xlabel("Epoch")
plt.legend()
plt.show()

plt.plot(accuracies, label="Validation accuracy")
plt.xlabel("Epoch")
plt.legend()
plt.show()
