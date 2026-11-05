"""Checks that every Godot frame has a valid label.

Usage: python validate_dataset.py [dataset_dir]
"""

import json
import sys
from pathlib import Path

from PIL import Image

DATASET_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dataset")
REQUIRED_FIELDS = [
    "frame_id", "ball_center_x", "ball_center_y",
    "ball_bounding_box_x", "ball_bounding_box_y",
    "ball_bounding_box_width", "ball_bounding_box_height",
    "ball_visibility", "simulation_scenario_id",
]


def check_frame(image_path):
    """Return the problem with this frame's label, or None."""
    label_path = DATASET_DIR / "labels" / f"{image_path.stem}.txt"
    if not label_path.exists():
        return "missing label"

    try:
        label = json.loads(label_path.read_text())
    except json.JSONDecodeError:
        return "label is not valid JSON"

    missing = [field for field in REQUIRED_FIELDS if field not in label]
    if missing:
        return f"missing {', '.join(missing)}"
    if label["frame_id"] != int(image_path.stem):
        return "frame_id doesn't match the file name"

    # Only check the box when the ball is on screen
    if label["ball_visibility"]:
        with Image.open(image_path) as img:
            image_width, image_height = img.size
        x, y = label["ball_bounding_box_x"], label["ball_bounding_box_y"]
        width, height = label["ball_bounding_box_width"], label["ball_bounding_box_height"]
        if width <= 0 or height <= 0:
            return "ball box has no size"
        if x < 0 or y < 0 or x + width > image_width or y + height > image_height:
            return "ball box is outside the image"

    return None


def main():
    images = sorted((DATASET_DIR / "images").glob("*.png"))
    if not images:
        sys.exit(f"No images found in {DATASET_DIR / 'images'}")

    problems = 0
    for image_path in images:
        problem = check_frame(image_path)
        if problem:
            print(f"{image_path.name}: {problem}")
            problems += 1

    print(f"Checked {len(images)} frames, found {problems} problems")
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
