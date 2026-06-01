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
from command_layer.command_router import CommandRouter
from command_layer.commands import Command

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


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
    return parser.parse_args(argv)


def run(camera_index: int, real_robot: bool, width: int, height: int, frame_skip: int, headless: bool) -> int:
    """
    Main control loop.
    """
    logger.info("Initializing CommandRouter...")
    router = CommandRouter()

    if real_robot:
        logger.info("Initializing REAL robot controller...")
        from command_layer.go2_controller import Go2Controller
        controller = Go2Controller()
    else:
        logger.info("Initializing MOCK robot controller (dry run)...")
        from command_layer.mock_go2_controller import MockGo2Controller
        controller = MockGo2Controller()

    pipeline = GesturePipeline(source=camera_index, width=width, height=height, frame_skip=frame_skip, headless=headless)
    
    # State tracking variables for museum requirements
    state = {
        "last_command_time": 0.0,
        "last_gesture_time": time.time(),
        "current_state": Command.NONE,
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
            command = router.route(gesture)
            
            if command != Command.NONE and state["is_ready"]:
                logger.info(f"Gesture {gesture.name} triggered command {command.name}")
                controller.send_command(command)
                state["last_command_time"] = now
                state["current_state"] = command
                state["is_ready"] = False
        else:
            # Check for 5-second timeout to default state
            if (now - state["last_gesture_time"]) >= TIMEOUT_PERIOD and state["current_state"] != Command.STAND_DOWN:
                logger.info(f"No gesture for {TIMEOUT_PERIOD}s. Defaulting to STAND_DOWN.")
                controller.send_command(Command.STAND_DOWN)
                # Reset cooldown immediately so it can receive the next command without waiting 10s
                state["last_command_time"] = 0.0
                state["current_state"] = Command.STAND_DOWN
                state["is_ready"] = True
                if not real_robot:
                    print("\n[DRY SIMULATION] Robot defaulted to STAND_DOWN and is waiting for a new command...\n")

    logger.info("Starting GesturePipeline...")
    pipeline.run(on_gesture)
    return 0


def main() -> None:
    args = parse_args()
    try:
        sys.exit(run(args.camera, args.real_robot, args.width, args.height, args.frame_skip, args.headless))
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
        sys.exit(0)


if __name__ == "__main__":
    main()
