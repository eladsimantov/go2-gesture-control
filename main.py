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
        "--real-robot",
        action="store_true",
        help="Connect to the real robot. Without this flag, it runs in dry simulation mode.",
    )
    return parser.parse_args(argv)


def run(camera_index: int, real_robot: bool) -> int:
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

    pipeline = GesturePipeline(source=camera_index)
    
    # State tracking variables for museum requirements
    state = {
        "last_command_time": 0.0,
        "last_gesture_time": time.time(),
        "current_state": Command.NONE
    }

    COOLDOWN_PERIOD = 10.0
    TIMEOUT_PERIOD = 5.0

    def on_gesture(gesture: Gesture):
        now = time.time()
        
        if gesture != Gesture.UNKNOWN:
            state["last_gesture_time"] = now
            command = router.route(gesture)
            
            if command != Command.NONE and (now - state["last_command_time"]) >= COOLDOWN_PERIOD:
                logger.info(f"Gesture {gesture.name} triggered command {command.name}")
                controller.send_command(command)
                state["last_command_time"] = now
                state["current_state"] = command
        else:
            # Check for 5-second timeout to default state
            if (now - state["last_gesture_time"]) >= TIMEOUT_PERIOD and state["current_state"] != Command.STAND_DOWN:
                logger.info(f"No gesture for {TIMEOUT_PERIOD}s. Defaulting to STAND_DOWN.")
                controller.send_command(Command.STAND_DOWN)
                state["last_command_time"] = now
                state["current_state"] = Command.STAND_DOWN

    logger.info("Starting GesturePipeline...")
    pipeline.run(on_gesture)
    return 0


def main() -> None:
    args = parse_args()
    sys.exit(run(args.camera, args.real_robot))


if __name__ == "__main__":
    main()
