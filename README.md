# EECS 4740  AI Group Project
## Vision Models on Edge Hardware: Accuracy-Latency Tradeoff Analysis

### 1. Project Overview

Our project aims to develop a computer vision system capable of detecting and eventually tracking a ball in a simulated table tennis environment.

We plan to develop a custom Convolutional Neural Network (CNN) and compare its performance against a YOLO object detection model.

The primary research objective is to evaluate the **tradeoff between detection accuracy and processing latency** when running vision models on resource constrained hardware.

### 2. Project Goals

- Generate synthetic training images with automatically labeled ball positions.
- Train a custom CNN to detect the ball in individual images.
- Use YOLO as a baseline for comparison.
- Evaluate detection accuracy, inference latency, and FPS.
- Investigate how image quality, noise, and background variation affect model performance.
- Eventually expand into ball tracking, trajectory prediction, and scoring.

### 3. Proposed System Architecture

**Phase 1: Synthetic Data Generation (Current Focus)**

Use a simplified Godot scene to generate individual training images containing objects at randomized positions and sizes.

Initially, objects do not need to move or follow game physics. Each generated image will include annotations identifying the ball's location.

We will introduce different backgrounds and visual conditions, with noise and blur added during later data augmentation.

The existing Gravity Pong simulation may be used in a later phase for sequential-frame tracking, trajectory prediction, and scoring.

**Phase 2: Dataset Preparation and Validation**

Before training, generated data will pass through a Python validation script.

The validator checks:

- Image and label file correspondence
- YOLO-compatible annotation formatting
- Normalized bounding-box coordinates
- Invalid bounding boxes

Future data processing may include noise, blur, and additional image augmentations.

**Phase 3: Model Development**

Train a custom CNN using the generated dataset.

Use a YOLO model as a comparison baseline.

Both models should perform the same ball-detection task and be evaluated using the same held-out test data.

**Phase 4: Performance Evaluation**

Measure:

- Detection precision and recall
- Inference latency in milliseconds
- Frames processed per second (FPS)
- Model size and resource usage

Compare the models under identical testing conditions to analyze the accuracy-latency tradeoff.

The specific edge hardware has not yet been finalized.

**Phase 5 — Future Extensions**

After establishing reliable single-frame detection:

- Process consecutive video frames.
- Track the ball's movement over time.
- Predict ball trajectories.
- Detect bounce events.
- Investigate automatic scoring.

These features are future goals and are not required for the initial CNN training pipeline.

### 4. Current Project Progress

**Implemented or started:**
- Initial Godot Gravity Pong simulation
- Ball physics and AI-controlled paddles
- Ball-position retrieval in Godot
- Initial dataset specification (`DATASET.md`)
- Python dataset validator (`validate_dataset.py`), tested using sample data

**In progress or planned:**
- Godot synthetic image and label exporter
- Dataset randomization
- Image augmentation
- Custom CNN implementation
- YOLO baseline implementation
- Edge-hardware benchmarking

Note: The current dataset validator has not yet been integrated with Godot-generated training data.

### 5. Proposed Dataset Structure

```text
dataset/
├── images/
│   ├── frame_0001.png
│   └── frame_0002.png
├── labels/
│   ├── frame_0001.txt
│   └── frame_0002.txt
└── metadata.csv
```

YOLO annotation format:

```text
class_id center_x center_y width height
```

Coordinates are normalized between 0 and 1.

Class `0` represents the ball.

The same annotations can be converted or loaded for training and evaluating the custom CNN.

See `DATASET.md` for additional information.

### 6. Technologies

| Technology | Purpose |
|---|---|
| Godot | Synthetic image and gameplay generation |
| Python | Dataset processing, validation, and evaluation |
| PyTorch | Custom CNN development |
| YOLO | Object detection baseline |
| OpenCV | Image and video processing |
| Git/GitHub | Version control and collaboration |

### 7. Team Responsibilities

Responsibilities will be finalized by the group.

Proposed work areas:

| Area | Responsibilities |
|---|---|
| Simulation and Data Generation | Godot exporter, image randomization, annotations |
| Dataset Preparation | Validation, augmentation, and dataset organization |
| Model Development | Custom CNN training and YOLO baseline |
| Evaluation and Integration | Performance benchmarking, testing, and result analysis |

Team members may contribute across multiple areas.

### 8. Development Roadmap

- [x] Establish initial project direction
- [x] Develop initial Godot simulation
- [x] Define dataset annotation requirements
- [x] Implement initial dataset validator
- [ ] Finalize synthetic image export format
- [ ] Generate and validate the first training dataset
- [ ] Add optional noise and visual augmentation
- [ ] Implement and train the custom CNN
- [ ] Establish YOLO detection baseline
- [ ] Compare detection accuracy
- [ ] Benchmark processing latency and FPS
- [ ] Evaluate performance on approved edge hardware
- [ ] Investigate multi-frame tracking and scoring

### 9. Research Questions

1. Can a custom CNN provide comparable detection accuracy to YOLO while requiring fewer computational resources?
2. How do image resolution and model complexity affect inference latency?
3. Does synthetic training data generalize to real table-tennis footage?
4. How do noise, lighting, and background variation influence detection accuracy?

### 10. Collaboration Guidelines

- Create separate Git branches for new features.
- Document new scripts and their dependencies.
- Coordinate changes to shared Godot files.
- Keep generated training datasets separate from source code unless explicitly needed.
- Test scripts.

**Overall Project Goal:** Build and evaluate a lightweight ball-detection system, using synthetic training data and comparing a custom CNN against YOLO to determine the best balance between accuracy and latency on constrained hardware.
