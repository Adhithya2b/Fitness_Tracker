import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from PIL import Image
import time
from video_processor import process_uploaded_video
from exercise_analyzer import create_analyzer
from camera_analyzer import create_camera_analyzer

# Page configuration
st.set_page_config(
    page_title="FitAssist",
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto"
)
# Optional: Add CSS to increase main area width and add margins
st.markdown("""
    <style>
    .main .block-container {
        padding-left: 2rem;
    }
    </style>
""", unsafe_allow_html=True)




def main():
    # Header
    st.markdown("# FitAssist")
    st.markdown("Advanced video analysis for exercise form assessment and repetition counting")
    
    # Sidebar for exercise selection
    with st.sidebar:
        st.markdown("### Choose your workout")
        exercise_type = st.selectbox(
            "Select an Exercise",
            ["Push-ups", "Squats"],
            help="Select the type of exercise to analyze"
        )
        with st.expander("Breakdown", expanded=False):
            if exercise_type == "Push-ups":
                st.markdown("""
- Elbow angle tracking
- Body alignment verification
- Shoulder position monitoring
- Form quality assessment
                """)
            else:
                st.markdown("""
- Knee angle measurement
- Hip position tracking
- Heel position verification
- Depth assessment
                """)
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["Live Camera Analysis", "Video Upload Analysis"])
    
    with tab1:
        st.markdown("## Live Camera Analysis")
        st.markdown("Get real-time exercise analysis using your camera")
        
        # Camera controls
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            start_camera_button = st.button("Start Camera")
        with col2:
            stop_camera_button = st.button("Stop Camera")
        # Initialize camera_running in session state if not present
        if 'camera_running' not in st.session_state:
            st.session_state.camera_running = False
        if 'camera_analyzer' not in st.session_state:
            st.session_state.camera_analyzer = None

        if start_camera_button:
            if not st.session_state.camera_running:
                st.session_state.camera_analyzer = create_camera_analyzer(exercise_type)
                st.session_state.camera_analyzer.start_camera() # Ensure this method starts the capture thread
                st.session_state.camera_running = True
                st.success("Camera started successfully!")
            else:
                st.info("Camera is already running.")

        if stop_camera_button:
            if st.session_state.camera_running:
                if st.session_state.camera_analyzer:
                    st.session_state.camera_analyzer.stop_camera() # Ensure this method stops the capture thread
                st.session_state.camera_running = False
                st.session_state['waiting_for_camera_frames_shown'] = False  # Reset waiting message flag
                # Save last session results
                frame, analysis, pose_results = st.session_state.camera_analyzer.get_current_frame_and_analysis() if st.session_state.camera_analyzer else (None, None, None)
                if frame is not None and analysis is not None:
                    st.session_state['last_camera_session_results'] = {
                        'frame': frame,
                        'analysis': analysis,
                        'pose_results': pose_results
                    }
                else:
                    st.session_state['last_camera_session_results'] = None
                st.info("Camera stopped!")
            else:
                st.info("Camera is not active.")
        
        with col3:
            if st.session_state.camera_running:
                st.markdown("Camera Status: Active")
            else:
                st.markdown("Camera Status: Inactive")
        
        # Camera feed and analysis
        if st.session_state.camera_running and st.session_state.camera_analyzer:
            # Create placeholders for camera feed and stats
            camera_placeholder = st.empty()
            stats_placeholder = st.empty()
            
            # Use a while loop to continuously update the feed
            while st.session_state.camera_running:
                try:
                    # Get current frame, analysis, and pose results from the background thread
                    frame, analysis, pose_results = st.session_state.camera_analyzer.get_current_frame_and_analysis()
                    
                    if frame is not None and analysis is not None:
                        # Draw analysis and pose landmarks on frame
                        annotated_frame = st.session_state.camera_analyzer.draw_analysis_on_frame(frame, analysis, pose_results)
                        
                        # Convert BGR to RGB for display
                        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                        
                        # Display camera feed
                        camera_placeholder.image(frame_rgb, caption="Live Camera Feed", use_container_width=True)
                        
                        # Display real-time stats
                        with stats_placeholder.container():
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.markdown(f"Total Reps: {analysis['rep_count']}")
                            
                            with col2:
                                st.markdown(f"Current State: {analysis['state'].upper()}")
                            
                            with col3:
                                if analysis['angles']:
                                    # Ensure analysis['angles'] is not empty before calculating average
                                    angle_values = [angle for angle_key, angle in analysis['angles'].items() if angle is not None]
                                    if angle_values:
                                        avg_angle = sum(angle_values) / len(angle_values)
                                        st.markdown(f"Avg Angle: {avg_angle:.1f}°")
                                    else:
                                        st.markdown("Avg Angle: --")
                                else:
                                    st.markdown("Avg Angle: --")
                            
                            with col4:
                                feedback_count = len(analysis.get('feedback', []))
                                st.markdown(f"Feedback Items: {feedback_count}")
                            
                            # Display feedback
                            if analysis.get('feedback'):
                                st.markdown("### Real-time Feedback")
                                for feedback in analysis['feedback']:
                                    # Ensure feedback has 'severity' and 'message' attributes
                                    if hasattr(feedback, 'severity') and hasattr(feedback, 'message'):
                                        if feedback.severity == "error":
                                            st.markdown(f"Error: {feedback.message}")
                                        elif feedback.severity == "warning":
                                            st.markdown(f"Warning: {feedback.message}")
                                        else:
                                            st.markdown(f"Info: {feedback.message}")
                                    else:
                                        # Handle cases where feedback might not have expected attributes
                                        st.markdown(f"Feedback: {feedback}")
                        # Save last session results for later display
                        st.session_state['last_camera_session_results'] = {
                            'frame': frame,
                            'analysis': analysis,
                            'pose_results': pose_results
                        }
                        # A small sleep to prevent the CPU from running at 100%
                        # and to give Streamlit time to render updates.
                        # Adjust as needed for performance vs. real-time feel.
                        time.sleep(0.05) 
                        
                    else:
                        if 'waiting_for_camera_frames_shown' not in st.session_state or not st.session_state['waiting_for_camera_frames_shown']:
                            st.info("Waiting for camera frames...")
                            st.session_state['waiting_for_camera_frames_shown'] = True
                        time.sleep(0.1) # Wait a bit before trying again
                
                except Exception as e:
                    st.error(f"Camera error: {str(e)}")
                    st.session_state.camera_running = False
                    if st.session_state.camera_analyzer:
                        st.session_state.camera_analyzer.stop_camera()
                    st.error("Live camera analysis stopped due to an error.")
                    break # Exit the loop on error
        elif not st.session_state.camera_running and st.session_state.camera_analyzer:
            # Show session results if available
            if st.session_state.get('last_camera_session_results'):
                st.markdown("## Session Results")
                session = st.session_state['last_camera_session_results']
                analysis = session.get('analysis')
                frame = session.get('frame')
                pose_results = session.get('pose_results')
                if frame is not None and analysis is not None:
                    annotated_frame = st.session_state.camera_analyzer.draw_analysis_on_frame(frame, analysis, pose_results)
                    frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    st.image(frame_rgb, caption="Last Session Frame", use_container_width=True)
                    st.markdown(f"**Total Reps:** {analysis['rep_count']}")
                    st.markdown(f"**Final State:** {analysis['state'].upper()}")
                    if analysis['angles']:
                        angle_values = [angle for angle_key, angle in analysis['angles'].items() if angle is not None]
                        if angle_values:
                            avg_angle = sum(angle_values) / len(angle_values)
                            st.markdown(f"**Avg Angle:** {avg_angle:.1f}°")
                        else:
                            st.markdown("**Avg Angle:** --")
                    else:
                        st.markdown("**Avg Angle:** --")
                    feedback_count = len(analysis.get('feedback', []))
                    st.markdown(f"**Feedback Items:** {feedback_count}")
                    if analysis.get('feedback'):
                        st.markdown("### Feedback")
                        for feedback in analysis['feedback']:
                            if hasattr(feedback, 'severity') and hasattr(feedback, 'message'):
                                if feedback.severity == "error":
                                    st.markdown(f"Error: {feedback.message}")
                                elif feedback.severity == "warning":
                                    st.markdown(f"Warning: {feedback.message}")
                                else:
                                    st.markdown(f"Info: {feedback.message}")
                            else:
                                st.markdown(f"Feedback: {feedback}")
                else:
                    st.info("No session results available.")
            else:
                st.info("Click 'Start Camera' to resume live analysis.")
        else:
            st.info("Click 'Start Camera' to begin live analysis.")
    
    with tab2:
        st.markdown("## Video Upload Analysis")
        st.markdown("Upload and analyze recorded workout videos")
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Select your workout video",
                type=['mp4', 'avi', 'mov', 'mkv'],
                help="Upload a video file of your workout session"
            )
            
            if uploaded_file is not None:
                # Display video info
                file_details = {
                    "Filename": uploaded_file.name,
                    "File size": f"{uploaded_file.size / 1024 / 1024:.2f} MB",
                    "File type": uploaded_file.type
                }
                
                st.markdown("### File Information")
                for key, value in file_details.items():
                    st.markdown(f"{key}: {value}")
                
                # Process button
                if st.button("Analyze Video"):
                    with st.spinner("Processing video... This may take several minutes depending on video length."):
                        try:
                            # Process the video
                            results = process_uploaded_video(uploaded_file, exercise_type)
                            
                            # Store results in session state
                            st.session_state.analysis_results = results
                            st.session_state.processed = True
                            
                            st.success("Video analysis completed successfully!")
                            
                        except Exception as e:
                            st.error(f"Error processing video: {str(e)}")
                            st.session_state.processed = False
        
        with col2:
            st.markdown("## Quick Statistics")
            
            if 'processed' in st.session_state and st.session_state.processed:
                results = st.session_state.analysis_results
                summary = results['summary']
                video_info = results['video_info']
                
                # Display metrics
                st.markdown(f"Total Repetitions: {summary['total_reps']}")
                st.markdown(f"Form Accuracy: {summary['form_accuracy']:.1f}%")
                st.markdown(f"Video Duration: {video_info['duration']:.1f}s")
                st.markdown(f"Total Frames: {video_info['frame_count']}")
            else:
                st.markdown("Upload a video and click 'Analyze Video' to see results")
        
        # Results section for video upload
        if 'processed' in st.session_state and st.session_state.processed:
            st.markdown("---")
            st.markdown("## Analysis Results")
            
            results = st.session_state.analysis_results
            summary = results['summary']
            
            # Detailed metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Repetition Analysis")
                st.markdown(f"Total Repetitions: {summary['total_reps']}")
                st.markdown(f"Correct Form Frames: {summary['correct_form_frames']}")
                st.markdown(f"Total Frames: {summary['total_frames']}")
            
            with col2:
                st.markdown("### Form Quality")
                if summary['form_accuracy'] >= 80:
                    status_text = "Excellent form! Keep it up!"
                elif summary['form_accuracy'] >= 60:
                    status_text = "Good form, but there's room for improvement."
                else:
                    status_text = "Form needs work. Check the feedback below."
                st.markdown(f"Overall Accuracy: {summary['form_accuracy']:.1f}%")
                st.markdown(status_text)
            
            with col3:
                st.markdown("### Video Information")
                video_info = results['video_info']
                st.markdown(f"Duration: {video_info['duration']:.1f} seconds")
                st.markdown(f"Frame Rate: {video_info['fps']} FPS")
                st.markdown(f"Resolution: {video_info['resolution'][0]}x{video_info['resolution'][1]}")
            
            # Feedback summary
            if summary['feedback_summary']:
                st.markdown("### Form Feedback Summary")
                
                for feedback_message, feedback_data in summary['feedback_summary'].items():
                    count = feedback_data['count']
                    severity = feedback_data['severity']
                    
                    if severity == "error":
                        st.markdown(f"Error: {feedback_message} (appeared {count} times)")
                    elif severity == "warning":
                        st.markdown(f"Warning: {feedback_message} (appeared {count} times)")
                    else:
                        st.markdown(f"Info: {feedback_message} (appeared {count} times)")
            
            # Frame-by-frame analysis
            st.markdown("### Frame Analysis Preview")
            
            if results['processed_frames']:
                # Show a few sample frames
                # Ensure there are enough frames before slicing
                num_frames = len(results['processed_frames'])
                if num_frames >= 6:
                    sample_indices = [i * (num_frames // 6) for i in range(6)]
                else:
                    sample_indices = list(range(num_frames)) # Show all if less than 6
                
                cols = st.columns(3)
                for i, idx in enumerate(sample_indices):
                    frame = results['processed_frames'][idx]
                    with cols[i % 3]:
                        # Convert BGR to RGB for display
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        st.image(frame_rgb, caption=f"Frame {idx}", use_container_width=True)
            
            # Download processed video option
            st.markdown("### Download Processed Video")
            if 'processed_frames' in results and results['processed_frames']:
                if st.button("Download Annotated Video"):
                    # Create temporary file for processed video
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        # Save processed frames as video
                        height, width = results['processed_frames'][0].shape[:2]
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        video_writer = cv2.VideoWriter(tmp_file.name, fourcc, video_info['fps'], (width, height)) # Use original FPS
                        
                        for frame in results['processed_frames']:
                            video_writer.write(frame)
                        
                        video_writer.release()
                        
                        # Read the file and provide download
                        with open(tmp_file.name, 'rb') as f:
                            video_data = f.read()
                        
                        st.download_button(
                            label="Click to Download Processed Video", # Changed label for clarity
                            data=video_data,
                            file_name=f"processed_{uploaded_file.name}",
                            mime="video/mp4"
                        )
                        
                        # Clean up
                        os.unlink(tmp_file.name)
            else:
                st.info("No processed video available for download yet.")


if __name__ == "__main__":
    main()