from pathlib import Path

# locationo of our training data
DATASET_DIR = Path("dataset")

IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"


def validate_dataset():
    """
    Validate the dataset directory structure and contents.
    """
    # Check if the dataset directory exists
    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"Dataset directory '{DATASET_DIR}' does not exist.")

    # Check if the images directory exists
    if not IMAGES_DIR.exists():
        raise FileNotFoundError(f"Images directory '{IMAGES_DIR}' does not exist.")

    # Check if the labels directory exists
    if not LABELS_DIR.exists():
        raise FileNotFoundError(f"Labels directory '{LABELS_DIR}' does not exist.")

    # Check if there are any image files in the images directory
    image_files = list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png"))
    if not image_files:
        raise ValueError(f"No image files found in '{IMAGES_DIR}'.")

    # Check if there are any label files in the labels directory
    label_files = list(LABELS_DIR.glob("*.txt"))
    if not label_files:
        raise ValueError(f"No label files found in '{LABELS_DIR}'.")

    # Check that each image has a corresponding label file
    for image_file in image_files:
        label_file = LABELS_DIR / (image_file.stem + ".txt")
        if not label_file.exists():
            raise ValueError(f"Label file '{label_file}' does not exist for image '{image_file}'.")

    # Validate YOLO annotation format and coordinates
    for label_file in label_files:
        with open(label_file, "r") as file:
            for line_number, line in enumerate(file, start=1):
                values = line.strip().split()

                if not values:
                    continue  # Empty labels are allowed

                if len(values) != 5:
                    raise ValueError(
                        f"Invalid YOLO format in {label_file.name}, line {line_number}"
                    )

                class_id, x, y, width, height = map(float, values)

                if class_id != 0:
                    raise ValueError(f"Invalid class ID in {label_file.name}")

                if not all(0 <= v <= 1 for v in [x, y, width, height]):
                    raise ValueError(
                        f"Coordinates out of range in {label_file.name}"
                    )

                if width <= 0 or height <= 0:
                    raise ValueError(
                        f"Invalid bounding box size in {label_file.name}"
                    )

                if x - width / 2 < 0 or x + width / 2 > 1 or \
                y - height / 2 < 0 or y + height / 2 > 1:
                    raise ValueError(
                        f"Bounding box extends outside image in {label_file.name}"
                    )

    print("Dataset validation successful. All required directories and files are present.")

if __name__ == "__main__":
    validate_dataset()