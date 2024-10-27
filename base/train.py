import os

import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from transformers import ViTForImageClassification, ViTImageProcessor


def load_datasets(transform: transforms.Compose, root: str = "/", batch_size: int = 32):
    def load_dataset(folder: str, shuffle: bool = False):
        dir = os.path.join(root, "dataset", folder)
        dataset = ImageFolder(root=dir, transform=transform)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
        return loader

    return load_dataset("train", shuffle=True), load_dataset("validate")


def load_model(name: str):
    model = ViTForImageClassification.from_pretrained(name)
    processor = ViTImageProcessor.from_pretrained(name)
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
            transforms.Normalize(mean=processor.image_mean, std=processor.image_std),
        ]
    )
    return model, transform


root = os.path.dirname(os.path.abspath(__file__))
checkpoints_dir = os.path.join(root, "checkpoints")
os.makedirs(checkpoints_dir, exist_ok=True)

model, transform = load_model("google/vit-base-patch16-224")
train_loader, validate_loader = load_datasets(root=root, transform=transform)

epochs = 10
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

losses, accuracies = [], []
for epoch in range(epochs):
    print(f"Epoch {epoch + 1}/{epochs}")

    # Training
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images).logits
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    print("- Loss:", format(running_loss / len(train_loader), ".4f"))

    # Validation
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in validate_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images).logits
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f"- Validation accuracy: {100 * correct / total:.2f}%")
    losses.append(running_loss / len(train_loader))
    accuracies.append(100 * correct / total)
    scheduler.step()

    # Save the model every 5 epochs
    if (epoch + 1) % 5 == 0:
        torch.save(
            model.state_dict(),
            os.path.join(checkpoints_dir, f"checkpoint{epoch + 1}.pth"),
        )

# Plot the training loss
plt.plot(losses, label="Training loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.xticks(np.arange(0, epochs, step=1))
plt.show()

# Plot the validation accuracy
plt.plot(accuracies, label="Validation accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.xticks(np.arange(0, epochs, step=1))
plt.yticks(np.arange(0, 100, step=10))
plt.show()
