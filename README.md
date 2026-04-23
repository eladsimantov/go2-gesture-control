# go2-gesture-control

A real-time gesture-control system for the **Unitree Go2 EDU** robot.  
An external camera detects hand gestures performed by a human operator and
translates them into high-level motion commands that are sent to the robot
over the network.

---
## Credit 

This project is funded by **MadaTech**, Israel's National Museum of Science, Technology and Space, and developed in collaboration with the **Technion** – Israel Institute of Technology.

| Name  | Credit |
|---|---|
| Elad Siman Tov  | Project Management, Integration of Unitree SDK with Raspberry Pi |
| Lior Ravina |  Integration of Gesture Recognition with Raspberry Pi |
| Tal Nesher | Project Advisor |
---

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
│   └── go2_interface.py      # Go2Interface based on high_level_example.
│
├── main.py                   # Entry point
└── requirements.txt
```

---

## Gesture → Command mapping

| Gesture | Command |
|---|---|
| 👍 Thumbs up | Stand Up |
| 👎 Thumbs down | Lie Down |
| ✌️ Peace / V sign | Handstand |
| ☝️ Pointing up | Rotate |
| ✊ Fist | Sit |
| ✋ Open palm | Say Hi |
| 🤟 I Love You | I Love You |
---

## Installation (Raspberry Pi)

### Python dependencies

Assume we install in the Raspberry Pi home directory, from scratch.
```bash
sudo apt install python3
sudo apt install python3-pip
python3 --version
sudo apt install python3-venv
cd ~
git clone https://github.com/eladsimantov/go2-gesture-control
cd ~/go2-gesture-control/
python -m venv go2env
source go2env/bin/activate
```

### Unitree SDK
To install Unitree's python SDK follow the guides in - https://github.com/unitreerobotics/unitree_sdk2_python.

---

## Usage
TODO

---

## Architecture

<img width="905" height="582" alt="image" src="https://github.com/user-attachments/assets/fc627fd4-72f6-42ba-93e0-e33e6a0555e7" />

