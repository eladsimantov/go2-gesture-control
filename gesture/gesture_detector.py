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
import os
import urllib.request
from typing import Optional, Tuple, List

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.processors import classifier_options
import numpy as np

from .gestures import Gesture

logger = logging.getLogger(__name__)

# Map MediaPipe gesture category names to our Gesture enum
_CATEGORY_TO_GESTURE = {
    "None": Gesture.UNKNOWN,
    "Closed_Fist": Gesture.CLOSED_FIST,
    "Open_Palm": Gesture.OPEN_PALM,
    "Pointing_Up": Gesture.POINTING_UP,
    "Thumb_Down": Gesture.THUMB_DOWN,
    "Thumb_Up": Gesture.THUMB_UP,
    "Victory": Gesture.VICTORY,
    "ILoveYou": Gesture.ILOVEYOU,
}


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
    """

    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.6,
    ) -> None:
        model_path = os.path.join(os.path.dirname(__file__), "gesture_recognizer.task")
        if not os.path.exists(model_path):
            logger.info("Downloading MediaPipe gesture recognizer model...")
            urllib.request.urlretrieve(
                "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task",
                model_path
            )

        base_options = python.BaseOptions(model_asset_path=model_path)
        
        # Configure classifier to return all categories (-1) to expose their confidence scores
        canned_options = classifier_options.ClassifierOptions(max_results=-1)
        
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
            canned_gesture_classifier_options=canned_options,
            running_mode=vision.RunningMode.IMAGE
        )
        self._detector = vision.GestureRecognizer.create_from_options(options)

        logger.debug("GestureDetector initialised (max_hands=%d)", max_hands)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame: np.ndarray) -> Tuple[Gesture, Optional[list], Optional[List[Tuple[str, float]]]]:
        """
        Detect the dominant hand gesture in *frame*.

        Parameters
        ----------
        frame:
            A BGR image captured from cv2.VideoCapture (H × W × 3 uint8).

        Returns
        -------
        Tuple[Gesture, Optional[list], Optional[List[Tuple[str, float]]]]
            A tuple containing the recognised gesture (or ``Gesture.UNKNOWN`` 
            when no hand is visible or the pose cannot be classified), 
            the list of landmarks (if detected), and a list of category 
            confidences (name, score).
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self._detector.recognize(mp_image)

        if not results.hand_landmarks:
            return Gesture.UNKNOWN, None, None

        landmarks = results.hand_landmarks[0]
        
        gesture = Gesture.UNKNOWN
        confidences = None
        
        if results.gestures and results.gestures[0]:
            categories = sorted(results.gestures[0], key=lambda c: c.score, reverse=True)
            top_cat = categories[0]
            
            if top_cat.category_name != "None" and top_cat.score > 0.4:
                gesture = _CATEGORY_TO_GESTURE.get(top_cat.category_name, Gesture.UNKNOWN)
                
            confidences = [(cat.category_name, cat.score) for cat in categories]

        logger.debug("Detected gesture: %s", gesture)
        return gesture, list(landmarks), confidences

    def release(self) -> None:
        """Release MediaPipe resources."""
        self._detector.close()
        logger.debug("GestureDetector released")

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "GestureDetector":
        return self

    def __exit__(self, *_: object) -> None:
        self.release()
