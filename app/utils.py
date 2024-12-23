import os
import random
import string
from typing import Literal

import requests
import timm
import torch
from PIL import Image
from torch.nn.functional import softmax
from torchvision import transforms
from torchvision.models import ResNet101_Weights, resnet101


def generate_id():
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )


def save_image(url):
    dir = os.path.join(os.getcwd(), "images")
    if not os.path.exists(dir):
        os.makedirs(dir)

    filename = f"{generate_id()}.jpg"
    path = os.path.join(dir, filename)

    # Download the image
    try:
        image = Image.open(requests.get(url, stream=True).raw)
        image.save(path)
    except Exception:
        raise ValueError("Invalid image URL.")

    return filename


CLASSES = [
    "beauty_products",
    "electronics",
    "fashion",
    "fitness_equipments",
    "furniture",
    "home_appliances",
    "kitchenware",
    "musical_instruments",
    "study_things",
    "toys",
]


def predict(filename, model_type: Literal["ResNet", "ViT"] = "ViT"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        image_path = os.path.join(os.getcwd(), "images", filename)
        image = Image.open(image_path)
    except Exception:
        raise ValueError("Invalid image path.")

    if model_type == "ResNet":
        model = resnet101(weights=ResNet101_Weights.DEFAULT)
        model.fc = torch.nn.Linear(model.fc.in_features, 10)
        model.to(device).eval()

        # Load the weights
        weights_path = os.path.join(os.getcwd(), "weights", "resnet_weights.pth")
        weights = torch.load(weights_path, map_location=device, weights_only=True)
        model.load_state_dict(weights["model"])

        # Preprocess the image
        preprocess = transforms.Compose(
            [
                transforms.Resize((224, 224), antialias=True),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        batch = preprocess(image).unsqueeze(0).to(device)
        with torch.inference_mode():
            output = model(batch)

        probs = torch.nn.functional.softmax(output[0], dim=0)
        return CLASSES[probs.argmax().item()], probs.max().item()
    elif model_type == "ViT":
        model = timm.create_model("vit_base_patch16_224.augreg_in21k", pretrained=True)
        model.head = torch.nn.Linear(model.head.in_features, 10)
        model.to(device).eval()

        # Load the weights
        weights_path = os.path.join(os.getcwd(), "weights", "vit_weights.pth")
        weights = torch.load(weights_path, map_location=device, weights_only=True)
        model.load_state_dict(weights)

        # Preprocess the image
        preprocess = transforms.Compose(
            [
                transforms.Resize((224, 224), antialias=True),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        batch = preprocess(image).unsqueeze(0).to(device)
        with torch.inference_mode():
            output = model(batch)

        probs = softmax(output[0], dim=0)
        return CLASSES[probs.argmax().item()], probs.max().item()
    else:
        raise ValueError("Invalid model type.")
