import json
import os


def load_json(website: str):
    root = os.path.abspath(os.path.dirname(__file__))
    dir = os.path.join(root, "resources", f"{website.lower()}.json")

    if not os.path.exists(dir):
        raise FileNotFoundError(f"File {dir} not found")

    with open(dir, "r") as file:
        text = file.read()

        return json.loads(text)
