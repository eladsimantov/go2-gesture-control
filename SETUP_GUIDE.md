# MadaTech Gesture Control Setup Guide

This guide explains how to set up the decoupled ZeroMQ Publisher/Subscriber architecture for the Unitree Go2 gesture control system.

## Overview
The system is divided into two nodes:
1. **Master Node (Publisher):** A PC or Raspberry Pi running MediaPipe. It captures the camera feed, detects hand gestures, and broadcasts them over the local Wi-Fi.
2. **Robot Node (Subscriber):** A Raspberry Pi physically attached to the Unitree Go2. It receives the gestures and converts them into actual movement commands using the Unitree SDK.

---

## 1. Network Configuration

Both the Master Node and the Robot Node must be connected to the **same local Wi-Fi network**.
- Identify the IP address of the Master Node (e.g., `192.168.1.100`).
- Ensure port `5555` is open and not blocked by the firewall on the Master Node.

---

## 2. Setting Up the Master Node (PC or Pi)

The Master Node requires a camera and handles the heavy computer vision tasks.

### Installation
1. Clone the repository to the Master Node.
2. Install the required dependencies. If you are on Windows:
   ```powershell
   pip install -r requirements-windows.txt
   ```
   If you are using a Raspberry Pi as the Master:
   ```bash
   pip install -r requirements-pi.txt
   ```

### Running the Master Node
Run `master.py` to start broadcasting gestures.
```bash
python master.py --port 5555
```
*Optional Arguments:*
- `--camera X`: Set the camera index (default `0`).
- `--headless`: Run without showing the camera preview (useful if using a Pi).

You should see logs indicating that the camera has started and gestures are being published.

---

## 3. Setting Up the Robot Node (Raspberry Pi on the Go2)

The Robot Node must be physically connected to the Unitree Go2 robot (typically via the Ethernet port `eth0`).

### Installation
1. SSH into the Robot Raspberry Pi.
2. Clone the repository.
3. Install the specific Raspberry Pi dependencies:
   ```bash
   pip install -r requirements-pi.txt
   ```

### Running the Robot Node
Run `robot_node.py` to listen for gestures and send commands to the Go2.
*Replace `192.168.1.100` with the actual IP address of your Master Node.*

**Dry Run (Simulation Mode):**
To test communication without moving the actual robot:
```bash
python robot_node.py --master-ip 192.168.1.100
```

**Real Robot Mode:**
To send live commands to the Go2:
```bash
python robot_node.py --master-ip 192.168.1.100 --real-robot --interface eth0
```

---

## 4. Testing & Verification
1. Start the Master Node and ensure the camera is active.
2. Start the Robot Node in **Dry Run** mode.
3. Perform a gesture (e.g., `THUMB_UP`) in front of the Master Node.
4. Watch the terminal on the Robot Node. You should see logs like:
   ```
   Received Gesture THUMB_UP, triggering command...
   MOCK: StandUp()
   ```
5. If the Dry Run succeeds, restart the Robot Node in **Real Robot** mode to control the physical Unitree Go2.
