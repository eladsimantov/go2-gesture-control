"""
High-level command definitions for the Unitree Go2 robot.

Commands are produced by CommandRouter from detected gestures and consumed
by Go2Interface, which translates them into SDK calls.
"""

from enum import Enum, auto


class Command(Enum):
    """High-level motion/action commands for the Go2 robot."""

    NONE = auto()
    """No-operation – do not change the robot's current state."""

    STAND_UP = auto()
    """Transition the robot from a resting pose to a standing pose."""

    STAND_DOWN = auto()
    """Lower the robot into a resting / lying down pose."""

    HANDSTAND = auto()
    """Perform a handstand."""

    ROTATE = auto()
    """Rotate the robot."""

    SIT = auto()
    """Sit down."""

    HELLO = auto()
    """Trigger the robot's built-in wave / greeting action."""
    
    HEART = auto()
    """Trigger the robot's heart / I Love You action."""
