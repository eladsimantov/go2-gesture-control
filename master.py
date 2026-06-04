#!/usr/bin/env python3
"""
master.py – entry point for the "Master" computer running MediaPipe.

This script opens the default camera, detects hand gestures in real time,
and publishes the detected gestures over a ZeroMQ PUB socket.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import zmq

from gesture.camera import GesturePipeline
from gesture.gestures import Gesture

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Master node for Go2 Gesture Control")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index")
    parser.add_argument("--width", type=int, default=640, help="Camera width")
    parser.add_argument("--height", type=int, default=480, help="Camera height")
    parser.add_argument("--frame-skip", type=int, default=2, help="Number of frames to skip")
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    parser.add_argument("--port", type=int, default=5555, help="ZeroMQ PUB port")
    return parser.parse_known_args(argv)[0]

def run(camera_index: int, width: int, height: int, frame_skip: int, headless: bool, port: int) -> int:
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    bind_addr = f"tcp://*:{port}"
    logger.info(f"Binding ZeroMQ PUB socket to {bind_addr}")
    socket.bind(bind_addr)

    pipeline = GesturePipeline(source=camera_index, width=width, height=height, frame_skip=frame_skip, headless=headless)
    
    def on_gesture(gesture: Gesture):
        now = time.time()
        # Even if the gesture is UNKNOWN, we publish it so the subscriber knows we are still alive
        # and can apply timeouts appropriately.
        payload = {
            "gesture": gesture.name,
            "timestamp": now
        }
        try:
            message = json.dumps(payload)
            socket.send_string(message)
        except Exception as e:
            logger.error(f"Failed to publish gesture: {e}")

    logger.info("Starting GesturePipeline...")
    pipeline.run(on_gesture)
    return 0

def main() -> None:
    args = parse_args()
    try:
        sys.exit(run(args.camera, args.width, args.height, args.frame_skip, args.headless, args.port))
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
        sys.exit(0)

if __name__ == "__main__":
    main()
