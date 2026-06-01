import logging
import sys
from .commands import Command

logger = logging.getLogger(__name__)

class Go2Controller:
    """Real controller that interfaces with Unitree SDK."""
    def __init__(self):
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.go2.sport.sport_client import SportClient
            
            logger.info("Initializing Unitree SDK Channels...")
            if len(sys.argv) > 1:
                ChannelFactoryInitialize(0, sys.argv[1])
            else:
                ChannelFactoryInitialize(0)
                
            self.sport_client = SportClient()
            self.sport_client.SetTimeout(10.0)
            self.sport_client.Init()
            logger.info("Unitree SportClient initialized successfully.")
        except ImportError as e:
            logger.error(f"Failed to import unitree_sdk2py: {e}")
            raise

    def send_command(self, command: Command) -> None:
        logger.info(f"Sending command to robot: {command.name}")
        
        if command == Command.STAND_UP:
            self.sport_client.StandUp()
        elif command == Command.STAND_DOWN:
            self.sport_client.StandDown()
        elif command == Command.HANDSTAND:
            self.sport_client.HandStand(True)
        elif command == Command.ROTATE:
            # Rotate left (yaw)
            self.sport_client.Move(0, 0, 0.5)
        elif command == Command.SIT:
            self.sport_client.Sit()
        elif command == Command.HELLO:
            self.sport_client.Hello()
        elif command == Command.HEART:
            self.sport_client.Heart()
        elif command == Command.NONE:
            pass
        else:
            logger.warning(f"Command {command.name} not implemented in Go2Controller.")
