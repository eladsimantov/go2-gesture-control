#!/usr/bin/env python3
"""
main.py – entry point for the Go2 gesture-control system.

This script opens the default camera, detects hand gestures in real time,
maps each gesture to a robot command and dispatches it to the Go2 robot.
Includes museum exhibit features: 5-second timeout to STAND_DOWN, and 
10-second command cooldown.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from gesture.camera import GesturePipeline
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gesture-controlled Unitree Go2 robot demo"
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera device index passed to cv2.VideoCapture (default: 0)",
    )
    parser.add_argument(
        "--width", type=int, default=320, help="Camera width resolution (default: 320)"
    )
    parser.add_argument(
        "--height", type=int, default=240, help="Camera height resolution (default: 240)"
    )
    parser.add_argument(
        "--frame-skip", type=int, default=2, help="Number of frames to skip before running detection (default: 2)"
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run without GUI / imshow (useful for Raspberry Pi)"
    )
    parser.add_argument(
        "--real-robot",
        action="store_true",
        help="Connect to the real robot. Without this flag, it runs in dry simulation mode.",
    )
    parser.add_argument(
        "--interface",
        type=str,
        default=None,
        help="Network interface to use for the robot connection (e.g. eth0).",
    )
    return parser.parse_known_args(argv)[0]


def run(camera_index: int, real_robot: bool, interface: str | None, width: int, height: int, frame_skip: int, headless: bool) -> int:
    """
    Main control loop.
    """
    if real_robot:
        logger.info("Initializing REAL robot controller...")
        controller = RealRobotController(interface=interface)
    else:
        logger.info("Initializing MOCK robot controller (dry run)...")
        controller = MockRobotController()

    pipeline = GesturePipeline(source=camera_index, width=width, height=height, frame_skip=frame_skip, headless=headless)
    
    # State tracking variables for museum requirements
    state = {
        "last_command_time": 0.0,
        "last_gesture_time": time.time(),
        "current_state": "NONE",
        "is_ready": True
    }

    COOLDOWN_PERIOD = 10.0
    TIMEOUT_PERIOD = 5.0

    def on_gesture(gesture: Gesture):
        now = time.time()
        
        # Check if cooldown just finished and log it
        if not state["is_ready"] and (now - state["last_command_time"]) >= COOLDOWN_PERIOD:
            state["is_ready"] = True
            if not real_robot:
                print("\n[DRY SIMULATION] Robot finished command and is waiting for a new command...\n")

        if gesture != Gesture.UNKNOWN:
            state["last_gesture_time"] = now
            
            if state["is_ready"]:
                logger.info(f"Gesture {gesture.name} triggered command")
                controller.handle_gesture(gesture)
                state["last_command_time"] = time.time()  # refresh time after command (useful for blocking commands like HandStand)
                state["current_state"] = gesture.name
                state["is_ready"] = False
        else:
            # Check for 5-second timeout to default state
            if (now - state["last_gesture_time"]) >= TIMEOUT_PERIOD and state["current_state"] != "STAND_DOWN":
                logger.info(f"No gesture for {TIMEOUT_PERIOD}s. Defaulting to STAND_DOWN.")
                controller.stand_down()
                # Reset cooldown immediately so it can receive the next command without waiting 10s
                state["last_command_time"] = 0.0
                state["current_state"] = "STAND_DOWN"
                state["is_ready"] = True
                if not real_robot:
                    print("\n[DRY SIMULATION] Robot defaulted to STAND_DOWN and is waiting for a new command...\n")

    logger.info("Starting GesturePipeline...")
    pipeline.run(on_gesture)
    return 0


def main() -> None:
    args = parse_args()
    try:
        sys.exit(run(args.camera, args.real_robot, args.interface, args.width, args.height, args.frame_skip, args.headless))
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
        sys.exit(0)


if __name__ == "__main__":
    main()

