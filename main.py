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
    parser.add_argument(
        "--network",
        type=str,
        default="",
        help="Network interface name to bind to (e.g., eth0). Optional.",
    )
    return parser.parse_args(argv)


def run(camera_index: int, real_robot: bool, network: str) -> int:
    """
    Main control loop.
    """
    sport_client = None

    if real_robot:
        logger.info("Initializing REAL robot controller via unitree_sdk2py...")
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.go2.sport.sport_client import SportClient
            
            if network:
                ChannelFactoryInitialize(0, network)
            else:
                ChannelFactoryInitialize(0)
                
            sport_client = SportClient()
            sport_client.SetTimeout(10.0)
            sport_client.Init()
            logger.info("Unitree SportClient initialized successfully.")
        except ImportError as e:
            logger.error(f"Failed to import unitree_sdk2py: {e}")
            return 1
    else:
        logger.info("Running in MOCK robot mode (dry run)...")

    pipeline = GesturePipeline(source=camera_index)
    
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

            # For commands that require toggling off after a period, such as HandStand
            if real_robot and sport_client is not None and state["current_state"] == Gesture.VICTORY:
                logger.info("Finishing HandStand")
                sport_client.HandStand(False)

        if gesture != Gesture.UNKNOWN:
            state["last_gesture_time"] = now
            
            if state["is_ready"]:
                logger.info(f"Gesture {gesture.name} triggered.")
                state["last_command_time"] = now
                state["current_state"] = gesture
                state["is_ready"] = False
                
                if real_robot and sport_client is not None:
                    if gesture == Gesture.THUMB_UP:
                        sport_client.StandUp()
                    elif gesture == Gesture.THUMB_DOWN:
                        sport_client.StandDown()
                    elif gesture == Gesture.VICTORY:
                        sport_client.HandStand(True)
                        # We turn it off when cooldown is finished above, instead of blocking time.sleep()
                    elif gesture == Gesture.POINTING_UP:
                        sport_client.Move(0, 0, 0.5)
                    elif gesture == Gesture.CLOSED_FIST:
                        sport_client.Sit()
                    elif gesture == Gesture.OPEN_PALM:
                        sport_client.Hello()
                    elif gesture == Gesture.ILOVEYOU:
                        sport_client.Heart()
        else:
            # Check for 5-second timeout to default state
            if (now - state["last_gesture_time"]) >= TIMEOUT_PERIOD and state["current_state"] != "STAND_DOWN":
                logger.info(f"No gesture for {TIMEOUT_PERIOD}s. Defaulting to STAND_DOWN.")
                
                if real_robot and sport_client is not None:
                    # Turn off HandStand if it was active
                    if state["current_state"] == Gesture.VICTORY:
                        sport_client.HandStand(False)
                        time.sleep(1)
                    sport_client.StandDown()
                    
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
    sys.exit(run(args.camera, args.real_robot, getattr(args, 'network', "")))


if __name__ == "__main__":
    main()
