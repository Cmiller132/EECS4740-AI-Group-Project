"""Loads Godot frames and labels, optionally with random backgrounds, balls and noise."""

import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFilter
from torch.utils.data import Dataset

IMAGE_SIZE = (288, 162)  # 1/4 Godot window size for early training
BALL_COLORS = [(245, 245, 235), (255, 130, 30)]  # white and orange ping-pong balls(will make tennis balls later)


class BallDataset(Dataset):
    """Items are (3xHxW image in [0, 1], [visible, x, y]) with x and y in [0, 1].

    augment options: None, "random" for training, "fixed" for validation sets.
    """

    def __init__(self, dataset_dir, frame_ids, augment=None):
        dataset_dir = Path(dataset_dir)
        self.augment = augment
        self.images, self.targets, self.radii = [], [], []

        # Load every frame as a small grayscale image along with its label
        for frame_id in frame_ids:
            label = json.loads((dataset_dir / "labels" / f"{frame_id}.txt").read_text())
            with Image.open(dataset_dir / "images" / f"{frame_id}.png") as img:
                width, height = img.size
                self.images.append(np.asarray(img.convert("L").resize(IMAGE_SIZE)))

            # Ball position is stored as a fraction of the image size (0 to 1)
            self.targets.append([float(label["ball_visibility"]),
                                 label["ball_center_x"] / width,
                                 label["ball_center_y"] / height])
            self.radii.append(label["ball_bounding_box_width"] / 2 * IMAGE_SIZE[0] / width)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        visible, x, y = self.targets[index]

        # No augmentation: just copy the gray image into 3 color channels
        if self.augment is None:
            image = np.repeat(self.images[index][..., None], 3, axis=2) / 255
        else:
            # Fixed scenes keep the same look for 30 frames so tracking stays smooth
            rng = np.random.default_rng(index // 30 if self.augment == "fixed" else None)
            width, height = IMAGE_SIZE
            image, (x, y) = augment(self.images[index], (x * width, y * height),
                                    self.radii[index], rng)
            # The ball counts as visible if its center is still in the picture after zooming
            visible =0 <= x < width and 0 <= y < height
            x, y = x / width, y / height

        image = torch.tensor(image, dtype=torch.float32).permute(2, 0, 1)
        return image, torch.tensor([float(visible), x, y], dtype=torch.float32)


def split_frame_ids(dataset_dir, val_fraction=0.2):
    """Split frames into training and validation, using the last frames for validation."""
    frame_ids = sorted(int(p.stem) for p in (Path(dataset_dir) / "labels").glob("*.txt"))
    cut = int(len(frame_ids) * (1 - val_fraction))
    return frame_ids[:cut], frame_ids[cut:]


def load_photo(path):
    """Center crop a real photo to 16:9 and shrink it to the model's input size."""
    with Image.open(path) as img:
        img = img.convert("RGB")
        crop_height = min(img.height, img.width * 9 // 16)
        crop_width = crop_height * 16 // 9
        left, top = (img.width - crop_width) // 2, (img.height - crop_height) // 2
        img = img.resize(IMAGE_SIZE, box=(left, top, left + crop_width, top + crop_height))
    return torch.tensor(np.asarray(img) / 255, dtype=torch.float32).permute(2, 0, 1)


def augment(gray, center, radius, rng):
    """Redraw a frame with a new background, paddle color and ball, then zoom, blur and add noise."""
    width, height = IMAGE_SIZE
    x, y = center

    # Background: usually an off-white whiteboard, sometimes a random color
    whiteboard = rng.random() < 0.7
    image = Image.new("RGB", IMAGE_SIZE, random_color(rng, 215) if whiteboard else random_color(rng))
    draw = ImageDraw.Draw(image)

    # A few random lines(should imitate marker scribbles I guess)
    for _ in range(rng.integers(0, 6)):
        stroke = rng.uniform(0, 1, 2) * IMAGE_SIZE + rng.normal(0, 15, (4, 2)).cumsum(axis=0)
        draw.line([tuple(p) for p in stroke], fill=random_color(rng, 0, 150), width=2)

    # Paddles, net and ground get a random color. the original godot ball is erased
    ys, xs = np.mgrid[0:height, 0:width]
    objects = 255 - gray
    objects[np.hypot(xs - x, ys - y) < radius + 2] = 0
    if rng.random() < 0.6:
        image.paste(random_color(rng), mask=Image.fromarray(objects))

    # Draw a new ball at the same spot with a random color and size
    color = BALL_COLORS[rng.integers(2)] if rng.random() < 0.6 else random_color(rng)
    radius *= rng.uniform(0.5, 2)
    edge = tuple(int(c * 0.7) for c in color)
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color, outline=edge)

    # Random zoom and shift, moving the ball's position along with the picture
    zoom = rng.uniform(1, 1.4)
    left = rng.uniform(0, width - width / zoom)
    top = rng.uniform(0, height - height / zoom)
    image = image.resize(IMAGE_SIZE, box=(left, top, left + width / zoom, top + height / zoom))
    x, y = (x - left) * zoom, (y - top) * zoom

    # Blur, brightness change and noise to look more like a real camera(not sure how real it really is but)
    image = image.filter(ImageFilter.GaussianBlur(rng.uniform(0, 1.5)))
    image = np.asarray(image) / 255 * rng.uniform(0.6, 1.3)
    image = image + rng.normal(0, rng.uniform(0, 0.05), image.shape)
    return np.clip(image, 0, 1), (x, y)


def random_color(rng, low=0, high=256):
    return tuple(rng.integers(low, high, 3).tolist())
