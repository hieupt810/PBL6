from app.utils import predict, save_image

if __name__ == "__main__":
    imageUrl = input("Enter the image URL: ")

    filename = save_image(imageUrl)
    for model in ["resnet", "vit", "resnet_self"]:
        category, probs = predict(filename, model_type=model, base_directory="./app")
        print(f"Model: {model}, Category: {category}, Probability: {probs}%")
