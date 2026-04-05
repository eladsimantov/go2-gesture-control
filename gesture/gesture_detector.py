"""
GestureDetector – real-time hand-gesture recognition using MediaPipe Hands.

Usage
-----
>>> detector = GestureDetector()
>>> gesture = detector.detect(frame)          # frame is a BGR numpy array
>>> detector.release()
"""

from __future__ import annotations

import logging
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from .gestures import Gesture

logger = logging.getLogger(__name__)

# MediaPipe landmark indices
_WRIST = 0
_THUMB_CMC = 1
_THUMB_MCP = 2
_THUMB_IP = 3
_THUMB_TIP = 4
_INDEX_MCP = 5
_INDEX_PIP = 6
_INDEX_DIP = 7
_INDEX_TIP = 8
_MIDDLE_MCP = 9
_MIDDLE_PIP = 10
_MIDDLE_DIP = 11
_MIDDLE_TIP = 12
_RING_MCP = 13
_RING_PIP = 14
_RING_DIP = 15
_RING_TIP = 16
_PINKY_MCP = 17
_PINKY_PIP = 18
_PINKY_DIP = 19
_PINKY_TIP = 20


def _finger_extended(landmarks: list, tip: int, pip: int) -> bool:
    """Return True when the fingertip is above its PIP joint (finger pointing upward).

    In MediaPipe's normalised coordinate system the y-axis increases
    downward, so a smaller y value means higher in the image.  Comparing
    tip.y directly against pip.y is the most reliable test for an
    upright, extended finger.
    """
    return landmarks[tip].y < landmarks[pip].y


def _thumb_extended_up(landmarks: list) -> bool:
    """Return True when the thumb tip is clearly above the thumb MCP joint."""
    return landmarks[_THUMB_TIP].y < landmarks[_THUMB_MCP].y


def _thumb_extended_down(landmarks: list) -> bool:
    """Return True when the thumb tip is clearly below the thumb MCP joint."""
    return landmarks[_THUMB_TIP].y > landmarks[_THUMB_MCP].y + 0.05


def _classify(landmarks: list) -> Gesture:
    """Classify a single hand into one of the supported Gesture values."""
    index_up = _finger_extended(landmarks, _INDEX_TIP, _INDEX_PIP)
    middle_up = _finger_extended(landmarks, _MIDDLE_TIP, _MIDDLE_PIP)
    ring_up = _finger_extended(landmarks, _RING_TIP, _RING_PIP)
    pinky_up = _finger_extended(landmarks, _PINKY_TIP, _PINKY_PIP)
    thumb_up = _thumb_extended_up(landmarks)
    thumb_down = _thumb_extended_down(landmarks)

    fingers_up = sum([index_up, middle_up, ring_up, pinky_up])

    # Open palm: all four fingers and thumb extended
    if fingers_up == 4 and thumb_up:
        return Gesture.OPEN_PALM

    # Fist: no fingers extended
    if fingers_up == 0 and not thumb_up:
        return Gesture.FIST

    # Peace sign: index and middle up, ring and pinky down
    if index_up and middle_up and not ring_up and not pinky_up:
        return Gesture.PEACE

    # Thumbs up: only thumb clearly up, all fingers closed
    if thumb_up and fingers_up == 0:
        return Gesture.THUMBS_UP

    # Thumbs down: only thumb clearly down, all fingers closed
    if thumb_down and fingers_up == 0:
        return Gesture.THUMBS_DOWN

    # Pointing left: index extended, tip x < MCP x (pointing leftward in image)
    if index_up and not middle_up and not ring_up and not pinky_up:
        if landmarks[_INDEX_TIP].x < landmarks[_INDEX_MCP].x:
            return Gesture.POINTING_LEFT
        return Gesture.POINTING_RIGHT

    return Gesture.UNKNOWN


class GestureDetector:
    """
    Detects hand gestures from a video stream using MediaPipe Hands.

    Parameters
    ----------
    max_hands:
        Maximum number of hands to detect simultaneously (default: 1).
    detection_confidence:
        Minimum confidence threshold for hand detection (default: 0.7).
    tracking_confidence:
        Minimum confidence threshold for hand tracking (default: 0.6).
    wave_velocity_threshold:
        Horizontal velocity (normalised units / frame) above which the
        current pose is classified as WAVE (default: 0.03).
    """

    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.6,
        wave_velocity_threshold: float = 0.03,
    ) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self._wave_velocity_threshold = wave_velocity_threshold
        self._prev_wrist_x: Optional[float] = None
        logger.debug("GestureDetector initialised (max_hands=%d)", max_hands)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame: np.ndarray) -> Gesture:
        """
        Detect the dominant hand gesture in *frame*.

        Parameters
        ----------
        frame:
            A BGR image captured from cv2.VideoCapture (H × W × 3 uint8).

        Returns
        -------
        Gesture
            The recognised gesture, or ``Gesture.UNKNOWN`` when no hand
            is visible or the pose cannot be classified.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        if not results.multi_hand_landmarks:
            self._prev_wrist_x = None
            return Gesture.UNKNOWN

        landmarks = results.multi_hand_landmarks[0].landmark
        gesture = _classify(list(landmarks))

        # Override with WAVE when rapid horizontal wrist motion is detected
        wrist_x = landmarks[_WRIST].x
        if self._prev_wrist_x is not None:
            velocity = abs(wrist_x - self._prev_wrist_x)
            if velocity >= self._wave_velocity_threshold and gesture == Gesture.OPEN_PALM:
                gesture = Gesture.WAVE
        self._prev_wrist_x = wrist_x

        logger.debug("Detected gesture: %s", gesture)
        return gesture

    def release(self) -> None:
        """Release MediaPipe resources."""
        self._hands.close()
        logger.debug("GestureDetector released")

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "GestureDetector":
        return self

    def __exit__(self, *_: object) -> None:
        self.release()
