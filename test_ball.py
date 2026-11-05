"""Quick checks for the training pipeline. Run with: pytest test_ball.py"""

import json

import pytest
import torch
from PIL import Image, ImageDraw

from ball_dataset import BallDataset, split_frame_ids
from train import BallNet


@pytest.fixture
def dataset_dir(tmp_path):
    """Five fake frames, each a black ball on white like the simulator."""
    (tmp_path / "images").mkdir()
    (tmp_path / "labels").mkdir()
    for i in range(5):
        x, y = 200 + 100 * i, 300
        image = Image.new("RGB", (1152, 648), "white")
        ImageDraw.Draw(image).ellipse([x - 24, y - 24, x + 24, y + 24], fill="black")
        image.save(tmp_path / "images" / f"{i}.png")
        label = {"ball_visibility": True, "ball_center_x": x, "ball_center_y": y,
                 "ball_bounding_box_width": 48}
        (tmp_path / "labels" / f"{i}.txt").write_text(json.dumps(label))
    return tmp_path


def test_split_holds_out_last_frames(dataset_dir):
    train_ids, val_ids = split_frame_ids(dataset_dir)
    assert train_ids == [0, 1, 2, 3] and val_ids == [4]


@pytest.mark.parametrize("augment", [None, "random", "fixed"])
def test_dataset_items(dataset_dir, augment):
    image, target = BallDataset(dataset_dir, range(5), augment)[0]
    assert image.shape == (3, 162, 288)
    assert 0 <= image.min() and image.max() <= 1
    if target[0] == 1:
        assert 0 <= target[1] <= 1 and 0 <= target[2] <= 1


def test_model_output():
    output = BallNet()(torch.rand(2, 3, 162, 288))
    assert output.shape == (2, 3)
    assert ((0 <= output[:, 1:]) & (output[:, 1:] <= 1)).all()
