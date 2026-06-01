"""
Command layer module for Go2 gesture control.

This module maps detected gestures to high-level robot commands and
forwards them to the SDK interface.
"""

from .commands import Command
from .command_router import CommandRouter

__all__ = ["Command", "CommandRouter"]
