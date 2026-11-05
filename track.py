"""Track the ball through a sequence of frames and save tracking.gif.

Usage: python track.py [folder]
  - a Godot dataset folder: tracks the held-out frames with random looks
  - any folder of .jpg/.png photos: tracks them in filename order
Red ring and trail: prediction. Green dot: true center.
"""

import sys
from pathlib import Path

import torch
from PIL import Image, ImageDraw

from ball_dataset import IMAGE_SIZE, BallDataset, load_photo, split_frame_ids
from train import BallNet, pick_device

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dataset")
SCALE = 2  # draw the GIF at twice the model's input size


def load_frames():
    """Return a list of (image, [visible, x, y] or None)."""
    if (FOLDER / "labels").is_dir():
        _, val_ids = split_frame_ids(FOLDER)
        dataset = BallDataset(FOLDER, val_ids, augment="fixed")
        items = [dataset[i] for i in range(len(dataset))]
        return [(image, target.tolist()) for image, target in items]
    photos = sorted(p for p in FOLDER.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    return [(load_photo(p), None) for p in photos]


def to_pixels(x, y):
    return x * IMAGE_SIZE[0] * SCALE, y * IMAGE_SIZE[1] * SCALE


def main():
    device = pick_device()
    model = BallNet().to(device)
    model.load_state_dict(torch.load("ball_cnn.pt", map_location=device))
    model.eval()

    frames = load_frames()
    with torch.no_grad():
        images = torch.stack([image for image, _ in frames])
        outputs = torch.cat([model(batch.to(device)).cpu() for batch in images.split(64)])
    found = [to_pixels(x, y) if seen > 0 else None for seen, x, y in outputs.tolist()]

    gif, errors = [], []
    for i, (image, target) in enumerate(frames):
        truth = to_pixels(target[1], target[2]) if target is not None and target[0] else None
        if found[i] and truth:
            errors.append(((found[i][0] - truth[0]) ** 2 + (found[i][1] - truth[1]) ** 2) ** 0.5)
        if len(gif) == 300 or (target is not None and not (found[i] or truth)):
            continue  # cap the GIF and skip simulator frames with no ball

        picture = Image.fromarray((image.permute(1, 2, 0).numpy() * 255).astype("uint8"))
        picture = picture.resize((IMAGE_SIZE[0] * SCALE, IMAGE_SIZE[1] * SCALE))
        draw = ImageDraw.Draw(picture)
        trail = [p for p in found[max(0, i - 15):i + 1] if p]
        if len(trail) > 1:
            draw.line(trail, fill="red", width=2)
        if truth:
            draw.ellipse([truth[0] - 3, truth[1] - 3, truth[0] + 3, truth[1] + 3], fill="lime")
        if found[i]:
            x, y = found[i]
            draw.ellipse([x - 14, y - 14, x + 14, y + 14], outline="red", width=2)
        gif.append(picture)

    if errors:
        median = sorted(errors)[len(errors) // 2] * 1152 / (IMAGE_SIZE[0] * SCALE)
        print(f"Median error on {len(errors)} frames: {median:.1f} simulator pixels")
    print(f"Ball found in {sum(p is not None for p in found)} of {len(frames)} frames")
    gif[0].save("tracking.gif", save_all=True, append_images=gif[1:], duration=33, loop=0)


if __name__ == "__main__":
    main()
