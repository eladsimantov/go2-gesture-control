"""
Gesture recognition module for Go2 gesture control.

This module provides hand gesture detection using MediaPipe and OpenCV.

see example in https://github.com/google-ai-edge/mediapipe-samples/tree/main/examples/gesture_recognizer/raspberry_pi. 

The :class:`Gesture` enum is always available.  :class:`GestureDetector`
requires ``opencv-python`` and ``mediapipe`` to be installed; it is
imported lazily so that the rest of the codebase can be loaded without
those dependencies present (e.g. during unit testing).
"""

from .gestures import Gesture

__all__ = ["Gesture", "GestureDetector"]


def __getattr__(name: str):  # noqa: N807
    if name == "GestureDetector":
        from .gesture_detector import GestureDetector  # noqa: PLC0415
        return GestureDetector
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
