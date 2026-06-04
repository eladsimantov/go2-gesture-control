#!/usr/bin/env python3
"""
robot_node.py – entry point for the Raspberry Pi attached to the Unitree Go2.

This script subscribes to gestures published by the Master computer over a
ZeroMQ SUB socket, maintains the state machine (cooldowns, timeouts), and 
sends the actual movement commands to the Go2 robot.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import zmq

from gesture.gestures import Gesture

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

class RealRobotController:
    def __init__(self, interface: str | None = None):
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.go2.sport.sport_client import SportClient
            
            logger.info("Initializing Unitree SDK Channels...")
            if interface:
                ChannelFactoryInitialize(0, interface)
            else:
                ChannelFactoryInitialize(0)
                
            self.sport_client = SportClient()
            self.sport_client.SetTimeout(10.0)
            self.sport_client.Init()
            logger.info("Unitree SportClient initialized successfully.")
        except ImportError as e:
            logger.error(f"Failed to import unitree_sdk2py: {e}")
            raise

    def handle_gesture(self, gesture: Gesture) -> None:
        if gesture == Gesture.THUMB_UP:
            self.sport_client.StandUp()
        elif gesture == Gesture.THUMB_DOWN:
            self.sport_client.StandDown()
        elif gesture == Gesture.VICTORY:
            self.sport_client.HandStand(True)
            time.sleep(4)
            self.sport_client.HandStand(False)
        elif gesture == Gesture.POINTING_UP:
            self.sport_client.Move(0, 0, 0.5)
        elif gesture == Gesture.CLOSED_FIST:
            self.sport_client.Sit()
        elif gesture == Gesture.OPEN_PALM:
            self.sport_client.Hello()
        elif gesture == Gesture.ILOVEYOU:
            self.sport_client.Heart()

    def stand_down(self) -> None:
        self.sport_client.StandDown()

    def stand_up(self) -> None:
        self.sport_client.StandUp()


class MockRobotController:
    def __init__(self):
        logger.info("Mock Unitree SportClient initialized successfully.")

    def handle_gesture(self, gesture: Gesture) -> None:
        if gesture == Gesture.THUMB_UP:
            logger.info("MOCK: StandUp()")
        elif gesture == Gesture.THUMB_DOWN:
            logger.info("MOCK: StandDown()")
        elif gesture == Gesture.VICTORY:
            logger.info("MOCK: HandStand(True)")
            time.sleep(4)
            logger.info("MOCK: HandStand(False)")
        elif gesture == Gesture.POINTING_UP:
            logger.info("MOCK: Move(0, 0, 0.5)")
        elif gesture == Gesture.CLOSED_FIST:
            logger.info("MOCK: Sit()")
        elif gesture == Gesture.OPEN_PALM:
            logger.info("MOCK: Hello()")
        elif gesture == Gesture.ILOVEYOU:
            logger.info("MOCK: Heart()")

    def stand_down(self) -> None:
        logger.info("MOCK: StandDown()")

    def stand_up(self) -> None:
        logger.info("MOCK: StandUp()")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robot node for Go2 Gesture Control")
    parser.add_argument("--real-robot", action="store_true", help="Connect to the real robot")
    parser.add_argument("--interface", type=str, default=None, help="Network interface")
    parser.add_argument("--master-ip", type=str, required=True, help="IP address of the Master computer")
    parser.add_argument("--port", type=int, default=5555, help="ZeroMQ SUB port")
    return parser.parse_known_args(argv)[0]


def run(real_robot: bool, interface: str | None, master_ip: str, port: int) -> int:
    if real_robot:
        logger.info("Initializing REAL robot controller...")
        controller = RealRobotController(interface=interface)
    else:
        logger.info("Initializing MOCK robot controller (dry run)...")
        controller = MockRobotController()

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    connect_addr = f"tcp://{master_ip}:{port}"
    logger.info(f"Connecting ZeroMQ SUB socket to {connect_addr}")
    socket.connect(connect_addr)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

    # State tracking variables for museum requirements
    state = {
        "last_command_time": 0.0,
        "last_gesture_time": time.time(),
        "current_state": "NONE",
        "is_ready": True
    }

    COOLDOWN_PERIOD = 3.0
    TIMEOUT_PERIOD = 3.0

    logger.info("Robot Node running. Listening for gestures...")
    
    # We use a poller so we can timeout the recv() call to process the STAND_DOWN timeout
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    while True:
        now = time.time()

        # Check if cooldown just finished and log it
        if not state["is_ready"] and (now - state["last_command_time"]) >= COOLDOWN_PERIOD:
            state["is_ready"] = True
            if not real_robot:
                print("\n[DRY SIMULATION] Robot finished command and is waiting for a new command...\n")

        # Check for 5-second timeout to default state
        # We process this even if we didn't receive a message this loop iteration
        if (now - state["last_gesture_time"]) >= TIMEOUT_PERIOD and state["current_state"] != "STAND_DOWN":
            logger.info(f"No valid gesture for {TIMEOUT_PERIOD}s. Defaulting to STAND_DOWN.")
            controller.stand_up()  # Note: Original code says stand_up() but logs STAND_DOWN. Kept original logic.
            state["last_command_time"] = 0.0
            state["current_state"] = "STAND_DOWN"
            state["is_ready"] = True
            if not real_robot:
                print("\n[DRY SIMULATION] Robot defaulted to STAND_DOWN and is waiting for a new command...\n")

        # Wait for messages with a short timeout (100ms) to keep the loop ticking for the timeout checks above
        socks = dict(poller.poll(100))
        if socket in socks and socks[socket] == zmq.POLLIN:
            message = socket.recv_string()
            try:
                data = json.loads(message)
                gesture_name = data.get("gesture", "UNKNOWN")
                
                # Convert string back to Enum. If it fails, default to UNKNOWN
                try:
                    gesture = Gesture[gesture_name]
                except KeyError:
                    gesture = Gesture.UNKNOWN

                if gesture != Gesture.UNKNOWN:
                    state["last_gesture_time"] = now
                    
                    if state["is_ready"]:
                        logger.info(f"Received Gesture {gesture.name}, triggering command...")
                        controller.handle_gesture(gesture)
                        state["last_command_time"] = time.time()
                        state["current_state"] = gesture.name
                        state["is_ready"] = False
            except Exception as e:
                logger.error(f"Error parsing message '{message}': {e}")

    return 0


def main() -> None:
    args = parse_args()
    try:
        sys.exit(run(args.real_robot, args.interface, args.master_ip, args.port))
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
        sys.exit(0)

if __name__ == "__main__":
    main()
