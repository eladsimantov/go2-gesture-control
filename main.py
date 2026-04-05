#!/usr/bin/env python3
"""
main.py – entry point for the Go2 gesture-control system.

This script opens the default camera, detects hand gestures in real time,
maps each gesture to a robot command and dispatches it to the Go2 robot
over the configured network interface.

Usage
-----
    python main.py [--interface <network-interface>] [--camera <device-index>]

Examples
--------
    # Use the default webcam and eth0 network interface
    python main.py

    # Use /dev/video2 and a specific network interface
    python main.py --interface enp3s0 --camera 2
"""

from __future__ import annotations

import argparse
import logging
import sys

import cv2

from gesture import GestureDetector
from command_layer import CommandRouter
from sdk import Go2Interface

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
        "--interface",
        default="eth0",
        help="Network interface connected to the Go2 robot (default: eth0)",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera device index passed to cv2.VideoCapture (default: 0)",
    )
    return parser.parse_args(argv)


def run(network_interface: str, camera_index: int) -> int:
    """
    Main control loop.

    Returns
    -------
    int
        Exit code: 0 on clean exit, 1 on error.
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        logger.error("Cannot open camera (device index %d)", camera_index)
        return 1

    logger.info("Camera opened (device index %d)", camera_index)

    try:
        with GestureDetector() as detector, Go2Interface(network_interface) as robot:
            router = CommandRouter()
            logger.info("Starting gesture control loop – press 'q' to quit")

            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    continue

                gesture = detector.detect(frame)
                command = router.route(gesture)
                robot.send_command(command)

                # Overlay the current gesture on the preview window
                cv2.putText(
                    frame,
                    f"Gesture: {gesture.name}  Command: {command.name}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("Go2 Gesture Control", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Quit signal received")
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


def main() -> None:
    args = parse_args()
    sys.exit(run(args.interface, args.camera))


if __name__ == "__main__":
    main()
