# go2-gesture-control

A real-time gesture-control system for the **Unitree Go2 EDU** robot.  
An external camera detects hand gestures performed by a human operator and
translates them into high-level motion commands that are sent to the robot
over the network.

---

## Repository structure

```
go2-gesture-control/
├── gesture/                  # Gesture recognition (MediaPipe + OpenCV)
│   ├── __init__.py
│   ├── gestures.py           # Gesture enum definitions
│   └── gesture_detector.py   # GestureDetector class
│
├── command_layer/            # Gesture → Command mapping
│   ├── __init__.py
│   ├── commands.py           # Command enum definitions
│   └── command_router.py     # CommandRouter class
│
├── sdk/                      # Go2 robot interface (unitree_sdk2py)
│   ├── __init__.py
│   └── go2_interface.py      # Go2Interface class
│
├── main.py                   # Entry point
└── requirements.txt
```

---

## Gesture → Command mapping

| Gesture | Command |
|---|---|
| 👍 Thumbs up | Stand up |
| 👎 Thumbs down | Sit down |
| ✋ Open palm | Stop |
| ✊ Fist | Walk forward |
| ✌️ Peace / V sign | Walk backward |
| 👈 Pointing left | Turn left |
| 👉 Pointing right | Turn right |
| 👋 Wave | Robot wave |

---

## Installation

### 1. Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Unitree SDK

```bash
git clone https://github.com/unitreerobotics/unitree_sdk2_python
cd unitree_sdk2_python && pip install -e .
```

---

## Usage

```bash
# Default: webcam at index 0, robot reachable via eth0
python main.py

# Custom network interface and camera index
python main.py --interface enp3s0 --camera 2
```

Press **q** in the preview window to quit.

---

## Architecture

```
Camera frame
     │
     ▼
┌──────────────────┐
│  GestureDetector │  (gesture/)
│  (MediaPipe Hands)│
└────────┬─────────┘
         │  Gesture
         ▼
┌──────────────────┐
│  CommandRouter   │  (command_layer/)
└────────┬─────────┘
         │  Command
         ▼
┌──────────────────┐
│  Go2Interface    │  (sdk/)
│  (unitree_sdk2py)│
└──────────────────┘
         │
         ▼
    Go2 Robot
```
