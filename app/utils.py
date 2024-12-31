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

from app.resnet import ResNet101


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
        image = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            },
        ).content
        with open(path, "wb") as f:
            f.write(image)
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


def predict(
    filename,
    model_type: Literal["resnet", "vit", "resnet_self"] = "resnet",
    base_directory=os.getcwd(),
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        image_path = os.path.join(os.getcwd(), "images", filename)
        image = Image.open(image_path)
    except Exception:
        raise ValueError("Invalid image path.")

    if model_type == "resnet":
        model = resnet101(weights=ResNet101_Weights.DEFAULT)
        model.fc = torch.nn.Linear(model.fc.in_features, len(CLASSES))
        model.to(device).eval()

        # Load the weights
        weights_path = os.path.join(
            base_directory, "weights", "resnet_tuning_weights.pth"
        )
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
        return CLASSES[probs.argmax().item()], format(probs.max().item() * 100, ".2f")
    elif model_type == "vit":
        model = timm.create_model("vit_base_patch16_224.augreg_in21k")
        model.head = torch.nn.Linear(model.head.in_features, len(CLASSES))
        model.to(device).eval()

        # Load the weights
        weights_path = os.path.join(base_directory, "weights", "vit_weights.pth")
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
        return CLASSES[probs.argmax().item()], format(probs.max().item() * 100, ".2f")
    elif model_type == "resnet_self":
        model = ResNet101(num_classes=len(CLASSES))
        model.to(device).eval()

        # Load the weights
        weights_path = os.path.join(base_directory, "weights", "resnet_weights.pth")
        weights = torch.load(weights_path, map_location=device, weights_only=True)
        model.load_state_dict(weights)

        # Preprocess the image
        preprocess = transforms.Compose(
            [
                transforms.Resize((224, 224), antialias=True),
                transforms.ToTensor(),
                transforms.Normalize(
                    [0.7037, 0.6818, 0.6685], [0.2739, 0.2798, 0.2861]
                ),
            ]
        )
        batch = preprocess(image).unsqueeze(0).to(device)
        with torch.inference_mode():
            output = model(batch)

        probs = softmax(output[0], dim=0)
        return CLASSES[probs.argmax().item()], format(probs.max().item() * 100, ".2f")
    else:
        raise ValueError("Invalid model type.")
