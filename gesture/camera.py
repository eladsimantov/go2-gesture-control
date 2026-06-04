import logging
# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
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

class GesturePipeline:
    """
    A pipeline that ties together the camera stream and gesture detector.
    It runs an infinite loop processing frames and calls a callback function
    with the detected gesture.
    """
    def __init__(self, source: Union[int, str] = 0, width: int = 640, height: int = 480, frame_skip: int = 2, headless: bool = False, fullscreen: bool = True):
        self.source = source
        self.width = width
        self.height = height
        self.frame_skip = frame_skip
        self.headless = headless
        self.fullscreen = fullscreen

    def run(self, on_gesture_callback: callable) -> None:
        """
        Run the camera pipeline.
        
        Parameters
        ----------
        on_gesture_callback : callable
            A function that takes a `Gesture` enum as an argument. It is called
            every frame.
        """
        from gesture import GestureDetector, Gesture
        from gesture.visualize import draw_overlays
        
        logger.info("Starting GesturePipeline...")
        
        if not self.headless:
            # Set up the window for fullscreen mode
            cv2.namedWindow("Gesture Control", cv2.WINDOW_NORMAL)
            if self.fullscreen:
                cv2.setWindowProperty("Gesture Control", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        with CameraStream(source=self.source, width=self.width, height=self.height) as camera, GestureDetector() as detector:
            frame_count = 0
            last_gesture = Gesture.UNKNOWN
            last_landmarks = None
            last_confidences = None
            
            while True:
                success, frame = camera.read_frame()
                if not success:
                    logger.warning("Failed to grab frame. Exiting pipeline...")
                    break
                    
                # Frame skipping logic
                if frame_count % (self.frame_skip + 1) == 0:
                    gesture, landmarks, confidences = detector.detect(frame)
                    last_gesture = gesture
                    last_landmarks = landmarks
                    last_confidences = confidences
                else:
                    gesture = last_gesture
                    landmarks = last_landmarks
                    confidences = last_confidences
                
                frame_count += 1
                
                # Call the callback every frame to allow time-based logic (timeouts, etc.)
                on_gesture_callback(gesture)
                
                if not self.headless:
                    # Draw overlays for visual feedback
                    frame = draw_overlays(frame, gesture, landmarks, confidences)
                    
                    # Display the resulting frame
                    cv2.imshow("Gesture Control", frame)
                    
                    # Wait for 1 ms and check if 'q' is pressed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Quit signal received.")
                        break
                    
        if not self.headless:
            cv2.destroyAllWindows()
            cv2.waitKey(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from gesture.gestures import Gesture
    
    def dummy_callback(gesture):
        if gesture != Gesture.UNKNOWN:
            print(f"Detected: {gesture.name}")
            
    pipeline = GesturePipeline(source=0)
    pipeline.run(dummy_callback)
