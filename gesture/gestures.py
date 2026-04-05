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

    THUMBS_UP = auto()
    """Thumb pointing upward – all other fingers closed."""

    THUMBS_DOWN = auto()
    """Thumb pointing downward – all other fingers closed."""

    OPEN_PALM = auto()
    """All five fingers extended and spread open (stop / stay)."""

    FIST = auto()
    """All fingers curled into a closed fist."""

    PEACE = auto()
    """Index and middle fingers extended in a V shape."""

    POINTING_LEFT = auto()
    """Index finger extended and pointing to the left."""

    POINTING_RIGHT = auto()
    """Index finger extended and pointing to the right."""

    WAVE = auto()
    """Open hand moving side-to-side (detected as sustained motion)."""
