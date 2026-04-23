import logging
import cv2
import numpy as np
from typing import Optional, Tuple, Union

logger = logging.getLogger(__name__)

class CameraStream:
    """
    A modular wrapper around OpenCV's VideoCapture for camera feed handling.
    
    Designed to be easily configurable for different platforms (PC vs. Raspberry Pi)
    by allowing the source index/path and resolution to be injected.
    """
    def __init__(self, source: Union[int, str] = 0, width: int = 640, height: int = 480):
        """
        Initialize the CameraStream configuration.

        Parameters
        ----------
        source : int | str
            The camera index (0 for default webcam) or video stream URL/path.
            On a Raspberry Pi, this might be a specific index or /dev/videoX path.
        width : int
            Desired frame width.
        height : int
            Desired frame height.
        """
        self.source = source
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None

    def start(self) -> bool:
        """
        Initialize the camera hardware and apply configuration settings.
        
        Returns
        -------
        bool
            True if the camera was successfully opened, False otherwise.
        """
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            logger.error(f"Failed to open video source: {self.source}")
            return False
            
        # Attempt to set the desired resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        logger.info(f"Camera started with source: {self.source}")
        return True

    def read_frame(self, flip: bool = True) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a single frame from the camera.

        Parameters
        ----------
        flip : bool
            If True, flips the image horizontally (mirror effect) which is
            usually more intuitive for user-facing gesture control.

        Returns
        -------
        Tuple[bool, Optional[np.ndarray]]
            A tuple of (success_flag, frame). If success_flag is False, frame is None.
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera.")
            return False, None
            
        if flip:
            frame = cv2.flip(frame, 1)
            
        return True, frame

    def stop(self) -> None:
        """Release the camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("Camera stopped.")

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "CameraStream":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

if __name__ == "__main__":
    import os
    import sys
    # Add project root to sys.path so we can import from the package
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from gesture import GestureDetector, Gesture
    from gesture.visualize import draw_overlays

    # Configure basic logging for standalone execution
    logging.basicConfig(level=logging.INFO)
    
    print("Starting camera stream and gesture detector. Press 'q' to exit.")
    
    with CameraStream(source=0) as camera, GestureDetector() as detector:
        prev_gesture = Gesture.UNKNOWN
        
        while True:
            success, frame = camera.read_frame()
            if not success:
                print("Failed to grab frame. Exiting...")
                break
                
            # Detect gesture, landmarks, and confidences
            gesture, landmarks, confidences = detector.detect(frame)
            
            if gesture != Gesture.UNKNOWN and gesture != prev_gesture:
                top_score = confidences[0][1] if confidences else 0.0
                print(f"recognised {gesture.name} with {top_score * 100:.2f}% confidence!")
                if confidences:
                    conf_str = ", ".join([f"{cat}: {score * 100:.2f}%" for cat, score in confidences if cat != "None"])
                    print(conf_str)
            
            prev_gesture = gesture

            # Draw overlays for visual feedback
            frame = draw_overlays(frame, gesture, landmarks, confidences)
            
            # Display the resulting frame
            cv2.imshow("Gesture Control Test", frame)
            
            # Wait for 1 ms and check if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quit signal received.")
                break
                
    cv2.destroyAllWindows()
    cv2.waitKey(1)  # Pump the event loop one last time to ensure window closes
