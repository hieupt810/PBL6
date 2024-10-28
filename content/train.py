import os

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from tqdm import tqdm
from transformers import ViTForImageClassification, ViTImageProcessor


class ViTImageModel:
    epoch = 1
    batch_size = 32
    accuracies, losses = [], []
    loss_fn = nn.CrossEntropyLoss()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def __init__(self, model_name: str, path: str = "/content") -> None:
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
        self.root = os.path.join(path, "dataset")
        self.model = ViTForImageClassification.from_pretrained(
            model_name, local_files_only=True
        )
        self.processor = ViTImageProcessor.from_pretrained(model_name)
        self.transform = transforms.Compose(
            [
                data_augmentation,
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=self.processor.image_mean, std=self.processor.image_std
                ),
            ]
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0001)
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer, step_size=5, gamma=0.1
        )

    def load_dataset(self, folder: str, shuffle: bool = False):
        dataset = ImageFolder(
            root=os.path.join(self.root, folder), transform=self.transform
        )
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=shuffle)
        return loader

    def load_datasets(self):
        return self.load_dataset("train", shuffle=True), self.load_dataset("validate")

    def load_checkpoint(self, filename: str):
        path = os.path.join(self.root, "checkpoint", filename)
        checkpoint = torch.load(path, map_location=self.device, weights_only=True)

        self.epoch = checkpoint["epoch"]
        self.losses.append(checkpoint["loss"])
        self.accuracies.append(checkpoint["accuracy"])
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

    def train(self, target_epoch: int):
        train_loader, validate_loader = self.load_datasets()
        for epoch in range(self.epoch, target_epoch + 1):
            self.epoch = epoch
            print(f"Epoch {epoch}/{target_epoch}")
            self.losses.append(self.train_step(train_loader))
            self.accuracies.append(self.validate(validate_loader))

            print(f"- Loss      : {self.losses[-1]:.4f}")
            print(f"- Accuracy  : {self.accuracies[-1]:.4f}%")
            self.scheduler.step()
            if self.losses[-1] < 0.5 and self.accuracies[-1] > 90.0:
                self.save_checkpoint()

    def train_step(self, dataloader: DataLoader):
        self.model.train()
        running_loss = 0.0
        for images, labels in tqdm(dataloader, desc="- Training  "):
            images, labels = images.to(self.device), labels.to(self.device)
            self.optimizer.zero_grad()
            outputs = self.model(images).logits
            loss = self.loss_fn(outputs, labels)
            loss.backward()
            self.optimizer.step()
            running_loss += loss.item()

        return running_loss / len(dataloader)

    def validate(self, dataloader: DataLoader, desc: str = "- Validating"):
        self.model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for images, labels in tqdm(dataloader, desc=desc):
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images).logits
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        return 100 * correct / total

    def test(self):
        test_loader = self.load_dataset("test")
        print(f"Testing accuracy: {self.validate(test_loader, desc="Testing"):.4f}%")

    def save_checkpoint(self):
        path = os.path.join(self.root, "checkpoint")
        os.makedirs(path, exist_ok=True)
        torch.save(
            {
                "epoch": self.epoch,
                "loss": self.losses[-1],
                "accuracy": self.accuracies[-1],
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict(),
            },
            os.path.join(path, f"checkpoint{self.epoch}.pth"),
        )

    def plot_metrics(self):
        _, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(self.losses, color="r")
        ax2.plot(self.accuracies, color="b")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss", color="r")
        ax2.set_ylabel("Accuracy", color="b")
        plt.show()


model = ViTImageModel(
    model_name="google/vit-base-patch16-224",
    path=os.path.abspath(os.path.dirname(__file__)),
)
model.train(5)
model.plot_metrics()
model.test()
