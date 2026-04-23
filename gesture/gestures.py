"""
Gesture definitions for the Go2 gesture control system.

Each gesture corresponds to a specific hand pose that is recognised by
GestureDetector and subsequently mapped to a robot command by
CommandRouter.
"""

from enum import Enum, auto


class Gesture(Enum):
    """Supported hand gestures detected by the camera."""

    UNKNOWN = auto()
    """No recognised gesture or ambiguous pose."""

    CLOSED_FIST = auto()
    """All fingers curled into a closed fist."""

    OPEN_PALM = auto()
    """All five fingers extended and spread open."""

    POINTING_UP = auto()
    """Index finger extended and pointing upwards."""

    THUMB_DOWN = auto()
    """Thumb pointing downward – all other fingers closed."""

    THUMB_UP = auto()
    """Thumb pointing upward – all other fingers closed."""

    VICTORY = auto()
    """Index and middle fingers extended in a V shape."""

    ILOVEYOU = auto()
    """Thumb, index, and pinky extended."""
