# EECS 4740 AI Group Project

Ball tracking for a simulated table tennis game. Godot makes labeled frames, then a small PyTorch CNN learns to find the ball. The end goal is to compare our CNN against YOLO for accuracy vs. speed on low-power hardware.

## Files
- `gravity-pong-generator/` - Godot sim with AI paddles; saves a screenshot and a JSON label (ball position, box, visibility) every frame
- `validate_dataset.py` - checks every image has a valid label
- `visualize_labels.py` - draws the label boxes on images so we can eyeball them
- `ball_dataset.py` - loads frames for PyTorch and adds random backgrounds, ball colors/sizes, zoom, blur and noise
- `train.py` - trains the model and saves `ball_cnn.pt`
- `track.py` - runs the model on held-out frames (or a folder of photos) and saves `tracking.gif`
- `test_ball.py` - a few basic tests

## Training (Windows)
1. Open `gravity-pong-generator` in Godot 4.7 and run it for a while. Keep the window visible or frames get skipped.
2. Copy `%APPDATA%\Godot\app_userdata\gravity-pong-generator\dataset` into this folder.
3. Run:
```
pip install torch pillow numpy pytest
pytest
python train.py
python track.py
```
To try real photos: `python track.py path\to\photos`

## Team Roles
| Area | Work |
|---|---|
| Simulation and Data | Godot sim, exporter, randomization |
| Dataset | Validation, augmentation |
| Models | Custom CNN, YOLO baseline |
| Evaluation | Accuracy, latency/FPS, edge hardware testing |

Everyone can help across areas.

## Roadmap
- [x] Godot sim and data exporter
- [x] Dataset validator
- [x] Small CNN that finds the ball in sim frames
- [ ] Test on real whiteboard photos/video
- [ ] YOLO baseline
- [ ] Compare accuracy and FPS on edge hardware
- [ ] Track the ball across frames (trajectory, bounces)
