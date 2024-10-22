import json
import os


def load_json(website: str):
    __basedir = os.path.abspath(os.path.dirname(__file__))
    __dirname = os.path.join(__basedir, "json", f"{website.lower()}.json")

    if not os.path.exists(__dirname):
        raise FileNotFoundError(f"File {__dirname} not found")

    with open(__dirname, "r") as file:
        text = file.read()

        return json.loads(text)
