#!/usr/bin/env python3
"""
Test script to verify the AI Fitness Tracker system components
"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported successfully"""
    print("🧪 Testing module imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    return True

def test_custom_modules():
    """Test that our custom modules can be imported"""
    print("\n🧪 Testing custom modules...")
    
    try:
        from pose_utils import PoseDetector, calculate_angle, PoseLandmarks
        print("✅ pose_utils imported successfully")
    except ImportError as e:
        print(f"❌ pose_utils import failed: {e}")
        return False
    
    try:
        from exercise_analyzer import PushUpAnalyzer, SquatAnalyzer, create_analyzer
        print("✅ exercise_analyzer imported successfully")
    except ImportError as e:
        print(f"❌ exercise_analyzer import failed: {e}")
        return False
    
    try:
        from video_processor import VideoProcessor, process_uploaded_video
        print("✅ video_processor imported successfully")
    except ImportError as e:
        print(f"❌ video_processor import failed: {e}")
        return False
    
    return True

def test_pose_detector():
    """Test pose detector initialization"""
    print("\n🧪 Testing pose detector...")
    
    try:
        from pose_utils import PoseDetector
        detector = PoseDetector()
        print("✅ PoseDetector initialized successfully")
        return True
    except Exception as e:
        print(f"❌ PoseDetector initialization failed: {e}")
        return False

def test_exercise_analyzers():
    """Test exercise analyzer creation"""
    print("\n🧪 Testing exercise analyzers...")
    
    try:
        from exercise_analyzer import create_analyzer
        
        # Test push-up analyzer
        pushup_analyzer = create_analyzer("push-ups")
        print("✅ Push-up analyzer created successfully")
        
        # Test squat analyzer
        squat_analyzer = create_analyzer("squats")
        print("✅ Squat analyzer created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Exercise analyzer creation failed: {e}")
        return False

def test_video_processor():
    """Test video processor initialization"""
    print("\n🧪 Testing video processor...")
    
    try:
        from video_processor import VideoProcessor
        processor = VideoProcessor()
        print("✅ VideoProcessor initialized successfully")
        return True
    except Exception as e:
        print(f"❌ VideoProcessor initialization failed: {e}")
        return False

def test_angle_calculation():
    """Test angle calculation functionality"""
    print("\n🧪 Testing angle calculations...")
    
    try:
        from pose_utils import calculate_angle
        import numpy as np
        
        # Test with simple coordinates
        a = [0, 0]
        b = [1, 0]
        c = [1, 1]
        
        angle = calculate_angle(a, b, c)
        expected_angle = 90.0
        
        if abs(angle - expected_angle) < 1.0:
            print(f"✅ Angle calculation correct: {angle:.1f}° (expected ~{expected_angle}°)")
            return True
        else:
            print(f"❌ Angle calculation incorrect: {angle:.1f}° (expected ~{expected_angle}°)")
            return False
            
    except Exception as e:
        print(f"❌ Angle calculation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Fitness Tracker System Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Custom Modules", test_custom_modules),
        ("Pose Detector", test_pose_detector),
        ("Exercise Analyzers", test_exercise_analyzers),
        ("Video Processor", test_video_processor),
        ("Angle Calculations", test_angle_calculation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the application, run:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 