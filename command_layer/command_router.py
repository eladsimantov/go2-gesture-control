"""
CommandRouter – maps detected gestures to high-level Go2 commands.

Usage
-----
>>> router = CommandRouter()
>>> command = router.route(Gesture.THUMBS_UP)   # → Command.STAND_UP
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from gesture.gestures import Gesture
from .commands import Command

logger = logging.getLogger(__name__)

# Default gesture → command mapping.
_DEFAULT_MAPPING: Dict[Gesture, Command] = {
    Gesture.THUMBS_UP: Command.STAND_UP,
    Gesture.THUMBS_DOWN: Command.SIT_DOWN,
    Gesture.OPEN_PALM: Command.STOP,
    Gesture.FIST: Command.WALK_FORWARD,
    Gesture.PEACE: Command.WALK_BACKWARD,
    Gesture.POINTING_LEFT: Command.TURN_LEFT,
    Gesture.POINTING_RIGHT: Command.TURN_RIGHT,
    Gesture.WAVE: Command.WAVE,
    Gesture.UNKNOWN: Command.NONE,
}


class CommandRouter:
    """
    Translates a :class:`~gesture.gestures.Gesture` into a
    :class:`~command_layer.commands.Command`.

    Parameters
    ----------
    mapping:
        Optional custom ``{Gesture: Command}`` dictionary that overrides
        (or extends) the default mapping.
    """

    def __init__(self, mapping: Optional[Dict[Gesture, Command]] = None) -> None:
        self._mapping: Dict[Gesture, Command] = {**_DEFAULT_MAPPING}
        if mapping:
            self._mapping.update(mapping)
        logger.debug("CommandRouter initialised with %d entries", len(self._mapping))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(self, gesture: Gesture) -> Command:
        """
        Return the :class:`Command` that corresponds to *gesture*.

        Unknown or unmapped gestures are silently translated to
        ``Command.NONE``.

        Parameters
        ----------
        gesture:
            The gesture produced by :class:`~gesture.gesture_detector.GestureDetector`.

        Returns
        -------
        Command
            The high-level command to send to the robot.
        """
        command = self._mapping.get(gesture, Command.NONE)
        logger.debug("Routed %s → %s", gesture, command)
        return command

    def update_mapping(self, gesture: Gesture, command: Command) -> None:
        """
        Override the command associated with a specific gesture at runtime.

        Parameters
        ----------
        gesture:
            The gesture whose mapping should be updated.
        command:
            The new command to associate with *gesture*.
        """
        self._mapping[gesture] = command
        logger.info("Updated mapping: %s → %s", gesture, command)
