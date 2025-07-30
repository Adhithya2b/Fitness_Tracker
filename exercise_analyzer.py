import numpy as np
from typing import Dict, List, Tuple, Optional
from pose_utils import PoseLandmarks, calculate_angle, get_landmark_coordinates, is_landmark_visible

class ExerciseState:
    """Exercise state enumeration"""
    UP = "up"
    DOWN = "down"
    TRANSITION = "transition"

class FormFeedback:
    """Form feedback data structure"""
    def __init__(self, is_correct: bool, message: str, severity: str = "info"):
        self.is_correct = is_correct
        self.message = message
        self.severity = severity  # "info", "warning", "error"

class ExerciseAnalyzer:
    """Base class for exercise analysis"""
    
    def __init__(self):
        self.rep_count = 0
        self.current_state = ExerciseState.UP
        self.state_history = []
        self.angle_history = []
        self.feedback_history = []
        
    def analyze_frame(self, landmarks) -> Dict:
        """Analyze a single frame and return results"""
        raise NotImplementedError
        
    def get_form_feedback(self, landmarks) -> List[FormFeedback]:
        """Get form feedback for current frame"""
        raise NotImplementedError
        
    def reset(self):
        """Reset analyzer state"""
        self.rep_count = 0
        self.current_state = ExerciseState.UP
        self.state_history = []
        self.angle_history = []
        self.feedback_history = []

class PushUpAnalyzer(ExerciseAnalyzer):
    """Push-up exercise analyzer"""
    
    def __init__(self):
        super().__init__()
        self.elbow_angle_threshold = 90  # degrees
        self.shoulder_angle_threshold = 45  # degrees
        self.hip_angle_threshold = 160  # degrees
        
    def analyze_frame(self, landmarks) -> Dict:
        """Analyze push-up form and count reps"""
        if landmarks is None:
            return {"rep_count": self.rep_count, "state": self.current_state, "angles": {}, "feedback": []}
        
        # Calculate key angles
        angles = self._calculate_angles(landmarks)
        
        # Determine state
        new_state = self._determine_state(angles)
        
        # Count reps
        if self._is_rep_complete(new_state):
            self.rep_count += 1
            
        self.current_state = new_state
        self.state_history.append(new_state)
        self.angle_history.append(angles)
        
        # Get form feedback
        feedback = self.get_form_feedback(landmarks)
        self.feedback_history.append(feedback)
        
        return {
            "rep_count": self.rep_count,
            "state": self.current_state,
            "angles": angles,
            "feedback": feedback
        }
    
    def _calculate_angles(self, landmarks) -> Dict[str, float]:
        """Calculate key angles for push-up analysis"""
        angles = {}
        
        # Right arm angles (assuming right arm is primary)
        right_shoulder = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_SHOULDER)
        right_elbow = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_ELBOW)
        right_wrist = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_WRIST)
        right_hip = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_HIP)
        
        if right_shoulder is not None and right_elbow is not None and right_wrist is not None:
            angles['elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        if right_elbow is not None and right_shoulder is not None and right_hip is not None:
            angles['shoulder'] = calculate_angle(right_elbow, right_shoulder, right_hip)
        
        # Body alignment (shoulder to hip to knee)
        right_knee = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_KNEE)
        if right_shoulder is not None and right_hip is not None and right_knee is not None:
            angles['body_alignment'] = calculate_angle(right_shoulder, right_hip, right_knee)
        
        return angles
    
    def _determine_state(self, angles: Dict[str, float]) -> str:
        """Determine current exercise state based on angles"""
        elbow_angle = angles.get('elbow', 180)
        
        if elbow_angle < self.elbow_angle_threshold:
            return ExerciseState.DOWN
        else:
            return ExerciseState.UP
    
    def _is_rep_complete(self, new_state: str) -> bool:
        """Check if a complete rep has been performed"""
        if len(self.state_history) < 2:
            return False
            
        # Rep is complete when we go from UP -> DOWN -> UP
        if (self.state_history[-1] == ExerciseState.DOWN and 
            new_state == ExerciseState.UP):
            return True
        return False
    
    def get_form_feedback(self, landmarks) -> List[FormFeedback]:
        """Get form feedback for push-up"""
        feedback = []
        
        if landmarks is None:
            return feedback
            
        angles = self._calculate_angles(landmarks)
        
        # Check elbow angle
        elbow_angle = angles.get('elbow', 180)
        if self.current_state == ExerciseState.DOWN and elbow_angle > 100:
            feedback.append(FormFeedback(
                is_correct=False,
                message="Go deeper - elbows should bend past 90 degrees",
                severity="warning"
            ))
        
        # Check shoulder angle (elbow position)
        shoulder_angle = angles.get('shoulder', 90)
        if shoulder_angle > 90:
            feedback.append(FormFeedback(
                is_correct=False,
                message="Keep elbows closer to body - don't flare them out",
                severity="warning"
            ))
        
        # Check body alignment
        body_angle = angles.get('body_alignment', 180)
        if body_angle < 160:
            feedback.append(FormFeedback(
                is_correct=False,
                message="Keep body straight - avoid hip sagging",
                severity="error"
            ))
        
        return feedback

class SquatAnalyzer(ExerciseAnalyzer):
    """Squat exercise analyzer"""
    
    def __init__(self):
        super().__init__()
        self.knee_angle_threshold = 110  # degrees (parallel to ground)
        self.hip_angle_threshold = 45  # degrees
        self.ankle_angle_threshold = 70  # degrees
        
    def analyze_frame(self, landmarks) -> Dict:
        """Analyze squat form and count reps"""
        if landmarks is None:
            return {"rep_count": self.rep_count, "state": self.current_state, "angles": {}, "feedback": []}
        
        # Calculate key angles
        angles = self._calculate_angles(landmarks)
        
        # Determine state
        new_state = self._determine_state(angles)
        
        # Count reps
        if self._is_rep_complete(new_state):
            self.rep_count += 1
            
        self.current_state = new_state
        self.state_history.append(new_state)
        self.angle_history.append(angles)
        
        # Get form feedback
        feedback = self.get_form_feedback(landmarks)
        self.feedback_history.append(feedback)
        
        return {
            "rep_count": self.rep_count,
            "state": self.current_state,
            "angles": angles,
            "feedback": feedback
        }
    
    def _calculate_angles(self, landmarks) -> Dict[str, float]:
        """Calculate key angles for squat analysis"""
        angles = {}
        
        # Right leg angles
        right_hip = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_HIP)
        right_knee = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_KNEE)
        right_ankle = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_ANKLE)
        right_shoulder = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_SHOULDER)
        
        if right_hip is not None and right_knee is not None and right_ankle is not None:
            angles['knee'] = calculate_angle(right_hip, right_knee, right_ankle)
        
        if right_shoulder is not None and right_hip is not None and right_knee is not None:
            angles['hip'] = calculate_angle(right_shoulder, right_hip, right_knee)
        
        # Ankle angle (for heel position check)
        right_foot = get_landmark_coordinates(landmarks, PoseLandmarks.RIGHT_FOOT_INDEX)
        if right_knee is not None and right_ankle is not None and right_foot is not None:
            angles['ankle'] = calculate_angle(right_knee, right_ankle, right_foot)
        
        return angles
    
    def _determine_state(self, angles: Dict[str, float]) -> str:
        """Determine current exercise state based on angles"""
        knee_angle = angles.get('knee', 180)
        
        if knee_angle < self.knee_angle_threshold:
            return ExerciseState.DOWN
        else:
            return ExerciseState.UP
    
    def _is_rep_complete(self, new_state: str) -> bool:
        """Check if a complete rep has been performed"""
        if len(self.state_history) < 2:
            return False
            
        # Rep is complete when we go from UP -> DOWN -> UP
        if (self.state_history[-1] == ExerciseState.DOWN and 
            new_state == ExerciseState.UP):
            return True
        return False
    
    def get_form_feedback(self, landmarks) -> List[FormFeedback]:
        """Get form feedback for squat"""
        feedback = []
        
        if landmarks is None:
            return feedback
            
        angles = self._calculate_angles(landmarks)
        
        # Check squat depth
        knee_angle = angles.get('knee', 180)
        if self.current_state == ExerciseState.DOWN and knee_angle > 120:
            feedback.append(FormFeedback(
                is_correct=False,
                message="Go deeper - thighs should be parallel to ground",
                severity="warning"
            ))
        
        # Check hip angle (back position)
        hip_angle = angles.get('hip', 180)
        if hip_angle < 45:
            feedback.append(FormFeedback(
                is_correct=False,
                message="Keep chest up - maintain proud posture",
                severity="warning"
            ))
        
        # Check ankle angle (heel position)
        ankle_angle = angles.get('ankle', 90)
        if ankle_angle < 60:
            feedback.append(FormFeedback(
                is_correct=False,
                message="Keep heels on the ground",
                severity="error"
            ))
        
        return feedback

def create_analyzer(exercise_type: str) -> ExerciseAnalyzer:
    """Factory function to create appropriate exercise analyzer"""
    if exercise_type.lower() == "pushup" or exercise_type.lower() == "push-ups":
        return PushUpAnalyzer()
    elif exercise_type.lower() == "squat" or exercise_type.lower() == "squats":
        return SquatAnalyzer()
    else:
        raise ValueError(f"Unsupported exercise type: {exercise_type}") 