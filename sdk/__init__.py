"""
SDK interface module for the Unitree Go2 robot.

This module wraps the unitree_sdk2py library to expose a clean, high-level
interface for sending motion commands to the Go2 EDU robot.
"""

from .go2_interface import Go2Interface

__all__ = ["Go2Interface"]
