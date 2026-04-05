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

    SIT_DOWN = auto()
    """Lower the robot into a resting / sitting pose."""

    WALK_FORWARD = auto()
    """Move the robot forward at a default walking speed."""

    WALK_BACKWARD = auto()
    """Move the robot backward at a default walking speed."""

    TURN_LEFT = auto()
    """Rotate the robot counter-clockwise (yaw left)."""

    TURN_RIGHT = auto()
    """Rotate the robot clockwise (yaw right)."""

    STOP = auto()
    """Immediately halt all motion and hold position."""

    WAVE = auto()
    """Trigger the robot's built-in wave / greeting action."""
