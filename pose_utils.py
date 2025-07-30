import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional

class PoseDetector:
    """Core pose detection and landmark extraction class"""
    
    def __init__(self, 
                 static_image_mode=False,
                 model_complexity=1,
                 smooth_landmarks=True,
                 enable_segmentation=False,
                 smooth_segmentation=True,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            smooth_segmentation=smooth_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def detect_pose(self, image):
        """Detect pose landmarks in an image"""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        return results
    
    def get_landmarks(self, results):
        """Extract landmarks from pose detection results"""
        if results.pose_landmarks:
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility])
            return np.array(landmarks)
        return None
    
    def draw_pose(self, image, results):
        """Draw pose landmarks and connections on image"""
        annotated_image = image.copy()
        self.mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
        return annotated_image

def calculate_angle(a: List[float], b: List[float], c: List[float]) -> float:
    """
    Calculate the angle between three points.
    
    Args:
        a: First point [x, y, z]
        b: Middle point (vertex) [x, y, z]
        c: Third point [x, y, z]
    
    Returns:
        Angle in degrees
    """
    # Convert to numpy arrays and extract x, y coordinates
    a = np.array([float(a[0]), float(a[1])])
    b = np.array([float(b[0]), float(b[1])])
    c = np.array([float(c[0]), float(c[1])])
    
    # Calculate vectors
    ba = a - b
    bc = c - b
    
    # Calculate angle using dot product
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)  # Clamp to avoid numerical issues
    
    angle = np.arccos(cosine_angle)
    angle = np.degrees(angle)
    
    return float(angle)

def calculate_3d_angle(a: List[float], b: List[float], c: List[float]) -> float:
    """
    Calculate the 3D angle between three points.
    
    Args:
        a: First point [x, y, z]
        b: Middle point (vertex) [x, y, z]
        c: Third point [x, y, z]
    
    Returns:
        Angle in degrees
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def get_landmark_coordinates(landmarks, landmark_idx):
    """Get coordinates for a specific landmark"""
    if landmarks is not None and landmark_idx < len(landmarks):
        landmark = landmarks[landmark_idx]
        if len(landmark) >= 3:
            return [float(landmark[0]), float(landmark[1]), float(landmark[2])]
    return None

def is_landmark_visible(landmarks, landmark_idx, threshold=0.5):
    """Check if a landmark is visible based on confidence threshold"""
    if landmarks is not None and landmark_idx < len(landmarks):
        return landmarks[landmark_idx][3] > threshold
    return False

# MediaPipe Pose landmark indices
class PoseLandmarks:
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32 