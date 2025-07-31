import cv2
import numpy as np
import streamlit as st
from typing import Dict, Optional
from pose_utils import PoseDetector
from exercise_analyzer import ExerciseAnalyzer, create_analyzer
import threading
import time

class CameraAnalyzer:
    """Real-time camera analysis for live exercise tracking"""
    
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.analyzer = None
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.current_analysis = None
        self.frame_lock = threading.Lock()
        
    def set_exercise_analyzer(self, analyzer: ExerciseAnalyzer):
        """Set the exercise analyzer for real-time analysis"""
        self.analyzer = analyzer
        if self.analyzer:
            self.analyzer.reset()
    
    def start_camera(self, camera_index: int = 0):
        """Start the camera capture"""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera at index {camera_index}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_running = True
        
        # Start frame capture thread
        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()
    
    def _capture_frames(self):
        """Background thread for continuous frame capture"""
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                        # Process frame for analysis
                        analysis, pose_results = self.process_frame(frame)
                        self.current_analysis = analysis
                        self.current_pose_results = pose_results
            time.sleep(0.033)  # ~30 FPS
    
    def stop_camera(self):
        """Stop the camera capture"""
        self.is_running = False
        if self.cap:
            self.cap.release()
    
    def process_frame(self, frame: np.ndarray):
        """Process a single frame and return analysis results and pose results"""
        if not self.is_running or frame is None:
            return {"rep_count": 0, "state": "unknown", "angles": {}, "feedback": []}, None
        
        # Detect pose
        pose_results = self.pose_detector.detect_pose(frame)
        landmarks = self.pose_detector.get_landmarks(pose_results)
        
        # Analyze exercise
        if self.analyzer:
            analysis = self.analyzer.analyze_frame(landmarks)
        else:
            analysis = {"rep_count": 0, "state": "unknown", "angles": {}, "feedback": []}
        
        return analysis, pose_results
    
    def draw_analysis_on_frame(self, frame: np.ndarray, analysis: Dict, pose_results=None) -> np.ndarray:
        """Draw analysis results and pose landmarks on frame"""
        annotated_frame = frame.copy()
        
        # Draw pose landmarks (if pose detected)
        if pose_results:
            annotated_frame = self.pose_detector.draw_pose(annotated_frame, pose_results)
        
        # Draw analysis information
        # Rep counter
        rep_text = f"Reps: {analysis['rep_count']}"
        cv2.putText(annotated_frame, rep_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Current state
        state_text = f"State: {analysis['state'].upper()}"
        cv2.putText(annotated_frame, state_text, (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Draw angles
        y_offset = 110
        for angle_name, angle_value in analysis['angles'].items():
            angle_text = f"{angle_name}: {angle_value:.1f}°"
            cv2.putText(annotated_frame, angle_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
        
        return annotated_frame
    
    def get_current_frame_and_analysis(self):
        """Get the current frame, analysis, and pose results with thread safety"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy(), self.current_analysis, getattr(self, 'current_pose_results', None)
        return None, None, None
    
    def get_frame(self):
        """Get a frame from the camera (legacy method)"""
        if self.cap and self.is_running:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

def create_camera_analyzer(exercise_type: str) -> CameraAnalyzer:
    """Factory function to create camera analyzer with exercise type"""
    analyzer = CameraAnalyzer()
    exercise_analyzer = create_analyzer(exercise_type)
    analyzer.set_exercise_analyzer(exercise_analyzer)
    return analyzer 