
import json
from pathlib import Path
from PIL import Image, ImageDraw

DATASET_DIR = Path("test-dataset")
IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"
OUTPUT_DIR = DATASET_DIR / "visualized"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for image_path in sorted(IMAGES_DIR.glob("*.png")):
    label_path = LABELS_DIR / f"{image_path.stem}.txt"

    if not label_path.exists():
        print(f"Missing label: {label_path.name}")
        continue

    with open(label_path, "r", encoding="utf-8") as file:
        label = json.load(file)

    with Image.open(image_path) as source:
        image = source.convert("RGB")

    draw = ImageDraw.Draw(image)

    x = label["ball_bounding_box_x"]
    y = label["ball_bounding_box_y"]
    width = label["ball_bounding_box_width"]
    height = label["ball_bounding_box_height"]

    # Draw the bounding box
    draw.rectangle(
        [x, y, x + width, y + height],
        outline="red",
        width=3
    )

    # Draw ball center
    cx = label["ball_center_x"]
    cy = label["ball_center_y"]

    draw.ellipse(
        [cx - 3, cy - 3, cx + 3, cy + 3],
        fill="yellow"
    )

    output_path = OUTPUT_DIR / image_path.name
    image.save(output_path)

    print(f"Visualized: {image_path.name}")

print("Visualization complete!")
