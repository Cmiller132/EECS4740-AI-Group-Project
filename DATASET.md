# Training Dataset Specification

## Purpose

Define how the Godot simulation will generate training
data for our table-tennis ball detection models.

## Dataset Structure

dataset/

- images/
- labels/
- metadata.csv

## Ball Annotations

Each frame should include:

- Frame ID
- Ball center (X, Y)
- Ball bounding box (X, Y, width, height)
- Ball visibility
- Simulation scenario ID

## YOLO Label Format

class_id center_x center_y width height

- Class 0 represents the ball.
- Bounding-box coordinates are normalized from 0 to 1.
- Frames without a visible ball use empty label files.

## Data Augmentation

We plan to test:

- Different ball speeds
- Motion blur
- Lighting changes
- Background variations
- Image noise

## Dataset Validation

Before training:

1. Verify each image has a matching label.
2. Validate bounding-box coordinates.
3. Identify missing or invalid annotations.
4. Separate training, validation, and test data
   by rally to avoid data leakage.

## Future Work

- Connect the dataset exporter to Godot.
- Train a custom CNN using PyTorch.
- Compare CNN performance against YOLO.
- Evaluate accuracy, latency, and FPS.
