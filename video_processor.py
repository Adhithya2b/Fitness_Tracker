import cv2
import numpy as np
import tempfile
import os
from typing import List, Dict, Tuple, Optional
from pose_utils import PoseDetector
from exercise_analyzer import ExerciseAnalyzer, FormFeedback

class VideoProcessor:
    """Handles video processing and analysis"""
    
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.analyzer = None
        self.processed_frames = []
        self.analysis_results = []
        
    def set_exercise_analyzer(self, analyzer: ExerciseAnalyzer):
        """Set the exercise analyzer for the current video"""
        self.analyzer = analyzer
        if self.analyzer:
            self.analyzer.reset()
    
    def process_video(self, video_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Process a video file and return analysis results
        
        Args:
            video_path: Path to input video file
            output_path: Optional path for processed video output
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.analyzer:
            raise ValueError("Exercise analyzer not set. Call set_exercise_analyzer() first.")
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Initialize video writer if output path is provided
        video_writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        
        frame_count = 0
        self.processed_frames = []
        self.analysis_results = []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                result = self._process_frame(frame, frame_count)
                self.analysis_results.append(result)
                
                # Draw analysis on frame
                annotated_frame = self._draw_analysis_on_frame(frame, result)
                self.processed_frames.append(annotated_frame)
                
                # Write to output video if specified
                if video_writer:
                    video_writer.write(annotated_frame)
                
                frame_count += 1
                
                # Progress update every 30 frames
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Processing: {progress:.1f}% complete")
        
        finally:
            cap.release()
            if video_writer:
                video_writer.release()
        
        # Generate summary
        summary = self._generate_summary()
        
        return {
            "summary": summary,
            "frame_results": self.analysis_results,
            "processed_frames": self.processed_frames,
            "video_info": {
                "fps": fps,
                "frame_count": frame_count,
                "duration": frame_count / fps if fps > 0 else 0,
                "resolution": (frame_width, frame_height)
            }
        }
    
    def _process_frame(self, frame: np.ndarray, frame_number: int) -> Dict:
        """Process a single frame and return analysis results"""
        # Detect pose
        pose_results = self.pose_detector.detect_pose(frame)
        landmarks = self.pose_detector.get_landmarks(pose_results)
        
        # Analyze exercise
        if self.analyzer:
            analysis = self.analyzer.analyze_frame(landmarks)
        else:
            analysis = {"rep_count": 0, "state": "unknown", "angles": {}, "feedback": []}
        
        return {
            "frame_number": frame_number,
            "landmarks": landmarks,
            "pose_results": pose_results,
            "analysis": analysis
        }
    
    def _draw_analysis_on_frame(self, frame: np.ndarray, result: Dict) -> np.ndarray:
        """Draw analysis results on frame"""
        annotated_frame = frame.copy()
        
        # Draw pose landmarks
        if result["pose_results"]:
            annotated_frame = self.pose_detector.draw_pose(annotated_frame, result["pose_results"])
        
        # Draw analysis information
        analysis = result["analysis"]
        
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
        
        # Draw feedback
        feedback_y = frame.shape[0] - 100
        for i, feedback in enumerate(analysis['feedback']):
            if isinstance(feedback, FormFeedback):
                color = (0, 255, 0) if feedback.is_correct else (0, 0, 255)
                cv2.putText(annotated_frame, feedback.message, (10, feedback_y + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return annotated_frame
    
    def _generate_summary(self) -> Dict:
        """Generate summary of analysis results"""
        if not self.analysis_results:
            return {"total_reps": 0, "form_accuracy": 0, "feedback_summary": []}
        
        # Get final rep count
        final_analysis = self.analysis_results[-1]["analysis"]
        total_reps = final_analysis["rep_count"]
        
        # Calculate form accuracy
        total_frames = len(self.analysis_results)
        correct_form_frames = 0
        feedback_summary = {}
        
        for result in self.analysis_results:
            analysis = result["analysis"]
            feedback_list = analysis.get("feedback", [])
            
            # Count frames with correct form
            if not feedback_list or all(f.is_correct for f in feedback_list):
                correct_form_frames += 1
            
            # Aggregate feedback
            for feedback in feedback_list:
                if isinstance(feedback, FormFeedback):
                    if feedback.message not in feedback_summary:
                        feedback_summary[feedback.message] = {
                            "count": 0,
                            "severity": feedback.severity
                        }
                    feedback_summary[feedback.message]["count"] += 1
        
        form_accuracy = (correct_form_frames / total_frames) * 100 if total_frames > 0 else 0
        
        return {
            "total_reps": total_reps,
            "form_accuracy": form_accuracy,
            "total_frames": total_frames,
            "correct_form_frames": correct_form_frames,
            "feedback_summary": feedback_summary
        }
    
    def save_processed_video(self, output_path: str) -> bool:
        """Save processed frames as video"""
        if not self.processed_frames:
            return False
        
        height, width = self.processed_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, 30, (width, height))
        
        for frame in self.processed_frames:
            video_writer.write(frame)
        
        video_writer.release()
        return True

def process_uploaded_video(video_file, exercise_type: str) -> Dict:
    """
    Process an uploaded video file
    
    Args:
        video_file: Uploaded file object (e.g., from Streamlit)
        exercise_type: Type of exercise to analyze
        
    Returns:
        Analysis results dictionary
    """
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(video_file.read())
        temp_video_path = tmp_file.name
    
    try:
        # Create processor and analyzer
        processor = VideoProcessor()
        from exercise_analyzer import create_analyzer
        analyzer = create_analyzer(exercise_type)
        processor.set_exercise_analyzer(analyzer)
        
        # Process video
        results = processor.process_video(temp_video_path)
        
        return results
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path) 