
import json
from pathlib import Path
from PIL import Image
import math

# Godot dataset folder
DATASET_DIR = Path("dataset")
IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"

REQUIRED_FIELDS = [
    "frame_id",
    "ball_center_x",
    "ball_center_y",
    "ball_bounding_box_x",
    "ball_bounding_box_y",
    "ball_bounding_box_width",
    "ball_bounding_box_height",
    "ball_visibility",
    "simulation_scenario_id",
]


def validate_dataset():
    print("Starting Godot dataset validation...")

    if not IMAGES_DIR.is_dir():
        raise FileNotFoundError("Images directory not found.")

    if not LABELS_DIR.is_dir():
        raise FileNotFoundError("Labels directory not found.")

    images = sorted(IMAGES_DIR.glob("*.png"))

    if not images:
        raise ValueError("No PNG images found.")

    for image in images:
        # Godot exports 0.png with 0.txt, 1.png with 1.txt
        label_path = LABELS_DIR / f"{image.stem}.txt"

        if not label_path.exists():
            raise ValueError(f"Missing label for {image.name}")

        # Read JSON from the .txt file
        try:
            with open(label_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON in {label_path.name}: {error}"
            ) from error

        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object in {label_path.name}")

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(
                    f"Missing '{field}' in {label_path.name}"
                )

        # Check image/frame correspondence
        if data["frame_id"] != int(image.stem):
            raise ValueError(
                f"Frame ID mismatch in {label_path.name}"
            )

        # Check visibility data type
        if not isinstance(data["ball_visibility"], bool):
            raise ValueError("ball_visibility must be true or false")

        # Check bounding-box values
        x = data["ball_bounding_box_x"]
        y = data["ball_bounding_box_y"]
        width = data["ball_bounding_box_width"]
        height = data["ball_bounding_box_height"]

        for value in [x, y, width, height]:
            if type(value) not in (int, float):
                raise ValueError(
                    f"Invalid bounding-box value in {label_path.name}"
                )

        if width <= 0 or height <= 0:
            raise ValueError(
                f"Invalid bounding-box dimensions in {label_path.name}"
            )

        if x < 0 or y < 0:
            raise ValueError(
                f"Negative bounding-box position in {label_path.name}"
            )

        # Check that the bounding box is within the image dimensions
        with Image.open(image) as img:
            img_width, img_height = img.size

        #Verify bounding box are finite
        if not all(math.isfinite(value) for value in [x, y, width, height]):
            raise ValueError(
                f"Bounding box values must be finite in {label_path.name}"
            )
        #Check whether the bounding box fit inside the image
        if x + width > img_width or y + height > img_height:
            raise ValueError(
                f"Bounding box exceeds image dimensions in {label_path.name}"
            )

        print(f"OK: {image.name} and {label_path.name}")

    print(f"Validation successful! Checked {len(images)} frames.")


if __name__ == "__main__":
    validate_dataset()
