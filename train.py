"""Train a small CNN to find the ball in each frame.

Usage: python train.py [dataset_dir]
Saves the trained weights to ball_cnn.pt
"""

import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader

from ball_dataset import BallDataset, split_frame_ids

DATASET_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dataset")
MODEL_PATH = Path("ball_cnn.pt")
EPOCHS = 20
BATCH_SIZE = 32
SIM_SIZE = torch.tensor([1152.0, 648.0])  # Godot window size


def pick_device():
    """Use a GPU if there is one, otherwise the CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def conv(in_channels, out_channels, stride):
    """One conv layer with batch norm and ReLU."""
    return nn.Sequential(nn.Conv2d(in_channels, out_channels, 3, stride, padding=1),
                         nn.BatchNorm2d(out_channels), nn.ReLU())


class BallNet(nn.Module):
    """Small CNN that outputs [visible, x, y] for the ball in each image."""

    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(conv(3, 16, 2), conv(16, 32, 2), conv(32, 32, 1),
                                      conv(32, 64, 2), conv(64, 64, 1))
        self.score = nn.Conv2d(64, 1, 1)

    def forward(self, images):
        # Score every spot in the image for how likely the ball is there
        scores = self.score(self.features(images))
        height, width = scores.shape[2:]
        scores = scores.flatten(1)

        # Position of each spot, from 0 to 1
        ys = (torch.arange(height, device=images.device) + 0.5) / height
        xs = (torch.arange(width, device=images.device) + 0.5) / width
        grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")

        # Ball center is the average spot weighted by score, the top score says if it's visible
        weights = scores.softmax(dim=1)
        x = (weights * grid_x.flatten()).sum(dim=1)
        y = (weights * grid_y.flatten()).sum(dim=1)
        return torch.stack([scores.amax(dim=1), x, y], dim=1)


def ball_loss(output, target):
    """Loss for guessing visibility plus loss for the ball position."""
    visible = target[:, 0]
    visibility_loss = F.binary_cross_entropy_with_logits(output[:, 0], visible)

    # Only score the position when the ball is on screen
    position_error = (output[:, 1:] - target[:, 1:]).abs().sum(dim=1)
    position_loss = (position_error * visible).sum() / visible.sum().clamp(min=1)
    return visibility_loss + 10 * position_loss


@torch.no_grad()
def evaluate(model, dataset, device):
    """Return visibility accuracy and median position error in pixels."""
    model.eval()
    outputs, targets = [], []
    for images, target in DataLoader(dataset, batch_size=BATCH_SIZE):
        outputs.append(model(images.to(device)).cpu())
        targets.append(target)
    output, target = torch.cat(outputs), torch.cat(targets)

    visible = target[:, 0] == 1
    accuracy = ((output[:, 0] > 0) == visible).float().mean().item()
    errors = ((output[visible, 1:] - target[visible, 1:]) * SIM_SIZE).norm(dim=1)
    return accuracy, errors.median().item()


def main():
    device = pick_device()
    train_ids, val_ids = split_frame_ids(DATASET_DIR)
    print(f"Loading {len(train_ids)} training and {len(val_ids)} validation frames...")

    # Training frames get random augmentation, validation is checked with and without the aug
    train_set = BallDataset(DATASET_DIR, train_ids, augment="random")
    val_set = BallDataset(DATASET_DIR, val_ids, augment="fixed")
    clean_val_set = BallDataset(DATASET_DIR, val_ids)

    model = BallNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Train, and log validation at each epoch
    for epoch in range(1, EPOCHS + 1):
        model.train()
        for images, targets in DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True):
            loss = ball_loss(model(images.to(device)), targets.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        accuracy, error = evaluate(model, val_set, device)
        print(f"epoch {epoch:2d}  val visibility acc {accuracy:.1%}  median error {error:.1f}px")

    accuracy, error = evaluate(model, clean_val_set, device)
    print(f"clean frames: visibility acc {accuracy:.1%}  median error {error:.1f}px")
    torch.save(model.state_dict(), MODEL_PATH)


if __name__ == "__main__":
    main()
