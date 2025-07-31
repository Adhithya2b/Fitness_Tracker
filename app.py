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
    page_title="AI Fitness Tracker",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for elegant styling
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        color: #1a1a1a;
        margin-bottom: 1.5rem;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.4rem;
        color: #2c3e50;
        margin-bottom: 1rem;
        font-weight: 600;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
    
    .section-header {
        font-size: 1.2rem;
        color: #34495e;
        margin-bottom: 0.8rem;
        font-weight: 500;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 0.8rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Feedback styling */
    .feedback-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(255, 193, 7, 0.1);
    }
    
    .feedback-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #dc3545;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(220, 53, 69, 0.1);
    }
    
    .feedback-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #17a2b8;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(23, 162, 184, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 12px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #dc3545;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Info box styling */
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #17a2b8;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Divider styling */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 2rem 0;
        border-radius: 1px;
    }
    
    /* Status indicators */
    .status-excellent {
        color: #28a745;
        font-weight: 600;
    }
    
    .status-good {
        color: #ffc107;
        font-weight: 600;
    }
    
    .status-needs-work {
        color: #dc3545;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px 8px 0px 0px;
        border: 1px solid #e9ecef;
        padding: 12px 24px;
        font-weight: 600;
        color: #6c757d;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">AI Fitness Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #6c757d; margin-bottom: 2rem;">Advanced video analysis for exercise form assessment and repetition counting</p>', unsafe_allow_html=True)
    
    # Sidebar for exercise selection
    with st.sidebar:
        st.markdown('<h3 class="section-header">Exercise Selection</h3>', unsafe_allow_html=True)
        exercise_type = st.selectbox(
            "Choose Exercise Type",
            ["Push-ups", "Squats"],
            help="Select the type of exercise to analyze"
        )
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Supported Exercises</h3>', unsafe_allow_html=True)
        
        if exercise_type == "Push-ups":
            st.markdown("**Push-up Analysis:**")
            st.markdown("• Elbow angle tracking")
            st.markdown("• Body alignment verification")
            st.markdown("• Shoulder position monitoring")
            st.markdown("• Form quality assessment")
        else:
            st.markdown("**Squat Analysis:**")
            st.markdown("• Knee angle measurement")
            st.markdown("• Hip position tracking")
            st.markdown("• Heel position verification")
            st.markdown("• Depth assessment")
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["Live Camera Analysis", "Video Upload Analysis"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Live Camera Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #6c757d; margin-bottom: 1.5rem;">Get real-time exercise analysis using your camera</p>', unsafe_allow_html=True)
        
        # Camera controls
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            start_camera_button = st.button("Start Camera", type="primary")
        
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
                st.info("Camera stopped!")
            else:
                st.info("Camera is not active.")
        
        with col3:
            if st.session_state.camera_running:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div style="color: #28a745; font-weight: 600;">Camera Status: Active</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div style="color: #6c757d;">Camera Status: Inactive</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
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
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-value">{analysis['rep_count']}</div>
                                    <div class="metric-label">Total Reps</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-value">{analysis['state'].upper()}</div>
                                    <div class="metric-label">Current State</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                if analysis['angles']:
                                    # Ensure analysis['angles'] is not empty before calculating average
                                    angle_values = [angle for angle_key, angle in analysis['angles'].items() if angle is not None]
                                    if angle_values:
                                        avg_angle = sum(angle_values) / len(angle_values)
                                        st.markdown(f"""
                                        <div class="metric-card">
                                            <div class="metric-value">{avg_angle:.1f}°</div>
                                            <div class="metric-label">Avg Angle</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                        <div class="metric-card">
                                            <div class="metric-value">--</div>
                                            <div class="metric-label">Avg Angle</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div class="metric-card">
                                        <div class="metric-value">--</div>
                                        <div class="metric-label">Avg Angle</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col4:
                                feedback_count = len(analysis.get('feedback', []))
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-value">{feedback_count}</div>
                                    <div class="metric-label">Feedback Items</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Display feedback
                            if analysis.get('feedback'):
                                st.markdown('<h3 class="section-header">Real-time Feedback</h3>', unsafe_allow_html=True)
                                for feedback in analysis['feedback']:
                                    # Ensure feedback has 'severity' and 'message' attributes
                                    if hasattr(feedback, 'severity') and hasattr(feedback, 'message'):
                                        if feedback.severity == "error":
                                            st.markdown(f'<div class="feedback-error">', unsafe_allow_html=True)
                                            st.markdown(f"**{feedback.message}**")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        elif feedback.severity == "warning":
                                            st.markdown(f'<div class="feedback-warning">', unsafe_allow_html=True)
                                            st.markdown(f"**{feedback.message}**")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        else:
                                            st.markdown(f'<div class="feedback-info">', unsafe_allow_html=True)
                                            st.markdown(f"**{feedback.message}**")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                    else:
                                        # Handle cases where feedback might not have expected attributes
                                        st.markdown(f'<div class="feedback-info">', unsafe_allow_html=True)
                                        st.markdown(f"**Generic Feedback: {feedback}**")
                                        st.markdown('</div>', unsafe_allow_html=True)
        
                        # A small sleep to prevent the CPU from running at 100%
                        # and to give Streamlit time to render updates.
                        # Adjust as needed for performance vs. real-time feel.
                        time.sleep(0.05) 
                        
                    else:
                        st.info("Waiting for camera frames...")
                        time.sleep(0.1) # Wait a bit before trying again
                
                except Exception as e:
                    st.error(f"Camera error: {str(e)}")
                    st.session_state.camera_running = False
                    if st.session_state.camera_analyzer:
                        st.session_state.camera_analyzer.stop_camera()
                    st.error("Live camera analysis stopped due to an error.")
                    break # Exit the loop on error
        elif not st.session_state.camera_running and st.session_state.camera_analyzer:
            st.info("Click 'Start Camera' to resume live analysis.")
        else:
            st.info("Click 'Start Camera' to begin live analysis.")
    
    with tab2:
        st.markdown('<h2 class="sub-header">Video Upload Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #6c757d; margin-bottom: 1.5rem;">Upload and analyze recorded workout videos</p>', unsafe_allow_html=True)
        
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
                
                st.markdown('<h3 class="section-header">File Information</h3>', unsafe_allow_html=True)
                for key, value in file_details.items():
                    st.markdown(f"**{key}:** {value}")
                
                # Process button
                if st.button("Analyze Video", type="primary"):
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
            st.markdown('<h2 class="sub-header">Quick Statistics</h2>', unsafe_allow_html=True)
            
            if 'processed' in st.session_state and st.session_state.processed:
                results = st.session_state.analysis_results
                summary = results['summary']
                video_info = results['video_info']
                
                # Display metrics in elegant cards
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{summary['total_reps']}</div>
                    <div class="metric-label">Total Repetitions</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{summary['form_accuracy']:.1f}%</div>
                    <div class="metric-label">Form Accuracy</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{video_info['duration']:.1f}s</div>
                    <div class="metric-label">Video Duration</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{video_info['frame_count']}</div>
                    <div class="metric-label">Total Frames</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <div style="text-align: center; color: #6c757d; padding: 2rem;">
                        Upload a video and click "Analyze Video" to see results
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Results section for video upload
        if 'processed' in st.session_state and st.session_state.processed:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<h2 class="sub-header">Analysis Results</h2>', unsafe_allow_html=True)
            
            results = st.session_state.analysis_results
            summary = results['summary']
            
            # Detailed metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<h3 class="section-header">Repetition Analysis</h3>', unsafe_allow_html=True)
                st.markdown(f"**Total Repetitions:** {summary['total_reps']}")
                st.markdown(f"**Correct Form Frames:** {summary['correct_form_frames']}")
                st.markdown(f"**Total Frames:** {summary['total_frames']}")
            
            with col2:
                st.markdown('<h3 class="section-header">Form Quality</h3>', unsafe_allow_html=True)
                
                if summary['form_accuracy'] >= 80:
                    status_class = "status-excellent"
                    status_text = "Excellent form! Keep it up!"
                elif summary['form_accuracy'] >= 60:
                    status_class = "status-good"
                    status_text = "Good form, but there's room for improvement."
                else:
                    status_class = "status-needs-work"
                    status_text = "Form needs work. Check the feedback below."
                
                st.markdown(f"**Overall Accuracy:** <span class='{status_class}'>{summary['form_accuracy']:.1f}%</span>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin-top: 0.5rem;'>{status_text}</p>", unsafe_allow_html=True)
            
            with col3:
                st.markdown('<h3 class="section-header">Video Information</h3>', unsafe_allow_html=True)
                video_info = results['video_info']
                st.markdown(f"**Duration:** {video_info['duration']:.1f} seconds")
                st.markdown(f"**Frame Rate:** {video_info['fps']} FPS")
                st.markdown(f"**Resolution:** {video_info['resolution'][0]}x{video_info['resolution'][1]}")
            
            # Feedback summary
            if summary['feedback_summary']:
                st.markdown('<h3 class="section-header">Form Feedback Summary</h3>', unsafe_allow_html=True)
                
                for feedback_message, feedback_data in summary['feedback_summary'].items():
                    count = feedback_data['count']
                    severity = feedback_data['severity']
                    
                    if severity == "error":
                        st.markdown(f'<div class="feedback-error">', unsafe_allow_html=True)
                        st.markdown(f"**{feedback_message}** (appeared {count} times)")
                        st.markdown('</div>', unsafe_allow_html=True)
                    elif severity == "warning":
                        st.markdown(f'<div class="feedback-warning">', unsafe_allow_html=True)
                        st.markdown(f"**{feedback_message}** (appeared {count} times)")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="feedback-info">', unsafe_allow_html=True)
                        st.markdown(f"**{feedback_message}** (appeared {count} times)")
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # Frame-by-frame analysis
            st.markdown('<h3 class="section-header">Frame Analysis Preview</h3>', unsafe_allow_html=True)
            
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
            st.markdown('<h3 class="section-header">Download Processed Video</h3>', unsafe_allow_html=True)
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