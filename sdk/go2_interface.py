"""
Go2Interface – high-level wrapper around the unitree_sdk2py SDK.

This module translates :class:`~command_layer.commands.Command` values into
concrete SDK calls, shielding the rest of the application from the details
of the Unitree Go2 Python SDK.

References
----------
* https://github.com/unitreerobotics/unitree_sdk2_python
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from command_layer.commands import Command

logger = logging.getLogger(__name__)

# Default motion parameters
_DEFAULT_WALK_SPEED_MPS = 0.4    # m/s forward/backward
_DEFAULT_TURN_SPEED_RADPS = 0.6  # rad/s yaw
_MOTION_DURATION = 0.5           # seconds to apply a velocity command before stopping


class Go2Interface:
    """
    Provides a clean interface to the Unitree Go2 EDU robot via the
    ``unitree_sdk2py`` library.

    Parameters
    ----------
    network_interface:
        Name of the network interface connected to the robot
        (e.g. ``"eth0"``).  Passed directly to the SDK's
        ``ChannelFactory``.
    walk_speed:
        Forward/backward speed in m/s (default: 0.4).
    turn_speed:
        Yaw rotation speed in rad/s (default: 0.6).

    Notes
    -----
    The ``unitree_sdk2py`` package must be installed separately.  The SDK
    is imported lazily so that the rest of the codebase can be tested
    without the hardware dependencies present.
    """

    def __init__(
        self,
        network_interface: str = "eth0",
        walk_speed: float = _DEFAULT_WALK_SPEED_MPS,
        turn_speed: float = _DEFAULT_TURN_SPEED_RADPS,
    ) -> None:
        self._network_interface = network_interface
        self._walk_speed = walk_speed
        self._turn_speed = turn_speed
        self._sport_client: Optional[object] = None
        self._connected = False
        logger.debug(
            "Go2Interface created (interface=%s, walk_speed=%.2f, turn_speed=%.2f)",
            network_interface,
            walk_speed,
            turn_speed,
        )

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Initialise the SDK channel and connect to the robot.

        This must be called before :meth:`send_command`.

        Raises
        ------
        ImportError
            If the ``unitree_sdk2py`` package is not installed.
        RuntimeError
            If the SDK fails to initialise.
        """
        try:
            from unitree_sdk2py.core.channel import ChannelFactory
            from unitree_sdk2py.go2.sport.sport_client import SportClient
        except ImportError as exc:
            raise ImportError(
                "unitree_sdk2py is not installed. "
                "Install it from https://github.com/unitreerobotics/unitree_sdk2_python"
            ) from exc

        logger.info("Initialising SDK channel on interface '%s'", self._network_interface)
        ChannelFactory.Instance().Init(0, self._network_interface)

        self._sport_client = SportClient()
        self._sport_client.SetTimeout(10.0)
        self._sport_client.Init()

        self._connected = True
        logger.info("Connected to Go2 robot")

    def disconnect(self) -> None:
        """Release SDK resources and mark the interface as disconnected."""
        self._sport_client = None
        self._connected = False
        logger.info("Disconnected from Go2 robot")

    # ------------------------------------------------------------------
    # Command dispatch
    # ------------------------------------------------------------------

    def send_command(self, command: Command) -> None:
        """
        Translate *command* into one or more SDK calls.

        Parameters
        ----------
        command:
            A high-level :class:`~command_layer.commands.Command` produced
            by :class:`~command_layer.command_router.CommandRouter`.

        Raises
        ------
        RuntimeError
            If :meth:`connect` has not been called successfully.
        """
        if command == Command.NONE:
            return

        if not self._connected or self._sport_client is None:
            raise RuntimeError("Not connected to the robot. Call connect() first.")

        logger.info("Sending command: %s", command)

        handlers = {
            Command.STAND_UP: self._stand_up,
            Command.SIT_DOWN: self._sit_down,
            Command.WALK_FORWARD: self._walk_forward,
            Command.WALK_BACKWARD: self._walk_backward,
            Command.TURN_LEFT: self._turn_left,
            Command.TURN_RIGHT: self._turn_right,
            Command.STOP: self._stop,
            Command.WAVE: self._wave,
        }

        handler = handlers.get(command)
        if handler is not None:
            handler()
        else:
            logger.warning("No handler registered for command: %s", command)

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "Go2Interface":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.disconnect()

    # ------------------------------------------------------------------
    # Private motion helpers
    # Note: the helpers that call time.sleep() block the calling thread
    # for _MOTION_DURATION seconds.  For a simple demo this is acceptable;
    # a production implementation should run the robot interface in a
    # dedicated thread or use the SDK's async/non-blocking APIs.
    # ------------------------------------------------------------------

    def _stand_up(self) -> None:
        self._sport_client.StandUp()

    def _sit_down(self) -> None:
        self._sport_client.StandDown()

    def _walk_forward(self) -> None:
        self._sport_client.Move(self._walk_speed, 0.0, 0.0)
        time.sleep(_MOTION_DURATION)
        self._sport_client.Move(0.0, 0.0, 0.0)

    def _walk_backward(self) -> None:
        self._sport_client.Move(-self._walk_speed, 0.0, 0.0)
        time.sleep(_MOTION_DURATION)
        self._sport_client.Move(0.0, 0.0, 0.0)

    def _turn_left(self) -> None:
        self._sport_client.Move(0.0, 0.0, self._turn_speed)
        time.sleep(_MOTION_DURATION)
        self._sport_client.Move(0.0, 0.0, 0.0)

    def _turn_right(self) -> None:
        self._sport_client.Move(0.0, 0.0, -self._turn_speed)
        time.sleep(_MOTION_DURATION)
        self._sport_client.Move(0.0, 0.0, 0.0)

    def _stop(self) -> None:
        self._sport_client.Move(0.0, 0.0, 0.0)

    def _wave(self) -> None:
        self._sport_client.Hello()
