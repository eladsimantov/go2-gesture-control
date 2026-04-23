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
sudo apt update
sudo apt install python3
sudo apt install python3-pip
python3 --version
sudo apt install python3-venv
sudo apt install git 
cd ~
git clone https://github.com/eladsimantov/go2-gesture-control
cd ~/go2-gesture-control/
python -m venv go2env
pip install -r requirements.txt
source go2env/bin/activate
```

### Unitree SDK
To install Unitree's python SDK follow the guides in - https://github.com/unitreerobotics/unitree_sdk2_python.

The SDK should be installed into the go2env virtual environment, using the editable install method.

Install system dependencies:
```bash
sudo apt update
sudo apt install git build-essential cmake libboost-all-dev
```

Install CycloneDDS inside the project directory:
```bash
git clone https://github.com/eclipse-cyclonedds/cyclonedds.git -b releases/0.10.x
cd cyclonedds
mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
cmake --build . --target install
```

Make the SDK aware of CycloneDDS when activating the virtual environment:
```bash
echo 'export CYCLONEDDS_HOME="$(pwd)/cyclonedds/install"' >> go2env/bin/activate
echo 'export LD_LIBRARY_PATH="$CYCLONEDDS_HOME/lib:$LD_LIBRARY_PATH"' >> go2env/bin/activate
```

Install the SDK in editable mode:
```bash 
cd ~/go2-gesture-control/
source go2env/bin/activate
git clone https://github.com/unitreerobotics/unitree_sdk2_python

cd unitree_sdk2_python
pip install -e .
```
---

## Usage
TODO

---

## Architecture

<img width="905" height="582" alt="image" src="https://github.com/user-attachments/assets/fc627fd4-72f6-42ba-93e0-e33e6a0555e7" />

## WiFi Setup
1. Go to the **Unitree Go2 App**.
2. Turn on Bluetooth and WiFi on your phone.
3. Connect your phone to the designated WiFi network. 
4. In the App, navigate to the WiFi mode and activate internet remote connection. If connection fails, use without internet. 
5. Connect the Raspberry Pi to the same WiFi network. 
6. In the App, navigate to Device > Data > Network Information, and write down the wlan0 IP address of the Go2 robot (e.g., 10.26.162.112)
7. Enable CycloneDDS in bash via wifi:
```bash 
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="wlan0"/></Interfaces></General></Domain></CycloneDDS>'
```

<!-- 6. Finally, find the Go2's IP address using the app and update `GO2_IP` in `main.py` accordingly. -->



