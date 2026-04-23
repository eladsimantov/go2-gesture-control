import cv2
import numpy as np

# MediaPipe hand connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), 
    (5, 6), (6, 7), (7, 8), 
    (9, 10), (10, 11), (11, 12), 
    (13, 14), (14, 15), (15, 16), 
    (17, 18), (18, 19), (19, 20), 
    (0, 5), (5, 9), (9, 13), (13, 17), (0, 17)
]

def draw_overlays(frame: np.ndarray, gesture, hand_landmarks, confidences=None) -> np.ndarray:
    """
    Draw hand landmarks and gesture text onto the frame.
    
    Parameters
    ----------
    frame : np.ndarray
        The BGR image frame.
    gesture : Gesture
        The detected gesture enum.
    hand_landmarks : Any
        The MediaPipe hand landmarks object.
    confidences: List[Tuple[str, float]], optional
        The gesture confidences to display.
        
    Returns
    -------
    np.ndarray
        The frame with overlays drawn.
    """
    if hand_landmarks:
        h, w = frame.shape[:2]
        for connection in HAND_CONNECTIONS:
            pt1 = hand_landmarks[connection[0]]
            pt2 = hand_landmarks[connection[1]]
            cv2.line(frame, (int(pt1.x * w), int(pt1.y * h)), (int(pt2.x * w), int(pt2.y * h)), (255, 255, 255), 2)
            
        for landmark in hand_landmarks:
            cv2.circle(frame, (int(landmark.x * w), int(landmark.y * h)), 5, (0, 0, 255), -1)
    
    if gesture and gesture.name != "UNKNOWN":
        cv2.putText(
            frame, 
            f"Gesture: {gesture.name}", 
            (10, 40), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 255, 0), 
            2, 
            cv2.LINE_AA
        )
        
    if confidences:
        y_offset = 80
        cv2.putText(frame, "Confidences:", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_offset += 25
        for category_name, score in confidences:
            text = f"{category_name}: {score:.2f}"
            cv2.putText(frame, text, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            y_offset += 20
            
    return frame
