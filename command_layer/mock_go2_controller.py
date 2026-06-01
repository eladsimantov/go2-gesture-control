import logging
from .commands import Command

logger = logging.getLogger(__name__)

class MockGo2Controller:
    """Mock controller for dry simulation without the physical robot."""
    def __init__(self):
        self.current_state = Command.NONE
        logger.info("MockGo2Controller initialized. Running in DRY SIMULATION mode.")

    def send_command(self, command: Command) -> None:
        if command == Command.NONE:
            return
            
        self.current_state = command
        # Dry simulation text output
        print(f"\n[DRY SIMULATION] Robot is currently doing: {command.name}\n")
