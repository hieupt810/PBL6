import timm
import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import ResNet101_Weights, resnet101

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
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def predict_ResNet(image):
    model = resnet101(weights=ResNet101_Weights.DEFAULT)
    model.fc = torch.nn.Linear(model.fc.in_features, 10)
    model = model.to(device).eval()

    weights = torch.load("", map_location=device, weights_only=True)
    model.load_state_dict(weights["model"])

    preprocess = transforms.Compose(
        [
            transforms.Resize((224, 224), antialias=True),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    image = Image.open(image)
    batch = preprocess(image).unsqueeze(0).to(device)
    with torch.inference_mode():
        output = model(batch)

    probs = torch.nn.functional.softmax(output[0], dim=0)
    return CLASSES[probs.argmax().item()], probs.max().item()


def predict_ViT(image):
    model = timm.create_model("vit_base_patch16_224.augreg_in21k", pretrained=True)
    model.head = torch.nn.Linear(model.head.in_features, 10)
    model = model.to(device).eval()

    weights = torch.load("", map_location=device, weights_only=True)
    model.load_state_dict(weights)

    preprocess = transforms.Compose(
        [
            transforms.Resize((224, 224), antialias=True),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    image = Image.open(image)
    batch = preprocess(image).unsqueeze(0).to(device)
    with torch.inference_mode():
        output = model(batch)

    probs = torch.nn.functional.softmax(output[0], dim=0)
    return CLASSES[probs.argmax().item()], probs.max().item()
