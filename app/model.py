import numpy as np
import cv2
from tensorflow.keras.models import load_model

# Load the trained smile classifier model
model = load_model("models/smile_classifier_cnn.h5")

def preprocess_image(image_bytes):
    """
    Preprocess the raw image bytes for model prediction.

    Args:
        image_bytes (bytes): The raw bytes of the image.

    Returns:
        np.ndarray: Preprocessed image suitable for model input.
    """
    try:
        # Decode the image bytes into a NumPy array
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Resize the image to the required input shape of the model (e.g., 32x32)
        image_resized = cv2.resize(image, (32, 32))
        image_resized = image_resized / 255.0  # Normalize pixel values to [0, 1]
        image_resized = np.expand_dims(image_resized, axis=0)  # Add batch dimension
        return image_resized
    except Exception as e:
        raise RuntimeError(f"Error during image preprocessing: {e}")

def predict_smile(file_location):
    """
    Read the file, preprocess the image, and make a prediction.

    Args:
        file_location (str): The file path of the image.

    Returns:
        str: "Smiling" if the model predicts a smile, otherwise "Not Smiling".
    """
    try:
        # Read the image as bytes
        with open(file_location, "rb") as f:
            image_bytes = f.read()

        # Preprocess the image
        preprocessed_image = preprocess_image(image_bytes)

        # Predict using the model
        prediction = model.predict(preprocessed_image)
        print(f"Prediction output: {prediction}, Type: {type(prediction)}")

        predicted_class = 1 if prediction[0][0] > 0.5 else 0
        return "Smiling" if predicted_class == 1 else "Not Smiling"
    except Exception as e:
        raise RuntimeError(f"Error during prediction: {e}")


