
"""
Test script for voice integration functionality.
This script tests the Faster-Whisper integration without requiring the full app.
"""

import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import faster_whisper
        print(" faster-whisper imported successfully")
    except ImportError as e:
        print(f" faster-whisper import failed: {e}")
        return False
    
    try:
        import torch
        print(" torch imported successfully")
    except ImportError as e:
        print(f" torch import failed: {e}")
        return False
    
    try:
        import soundfile
        print(" soundfile imported successfully")
    except ImportError as e:
        print(f" soundfile import failed: {e}")
        return False
    
    try:
        import numpy
        print(" numpy imported successfully")
    except ImportError as e:
        print(f" numpy import failed: {e}")
        return False
    
    return True

def test_audio_service():
    """Test the audio service initialization."""
    print("\nTesting audio service...")
    
    try:
        from app.audio_service import AudioService
        print(" AudioService imported successfully")
        
    
        print("Initializing audio service (this may take a moment on first run)...")
        audio_service = AudioService(model_size="small")
        print(" AudioService initialized successfully")
        
        return True
        
    except Exception as e:
        print(f" AudioService test failed: {e}")
        return False

def test_fastapi_routes():
    """Test if FastAPI routes can be imported."""
    print("\nTesting FastAPI routes...")
    
    try:
        from app.routes import router
        print(" FastAPI routes imported successfully")
        return True
        
    except Exception as e:
        print(f" FastAPI routes import failed: {e}")
        return False

def main():
    """Run all tests."""
    print(" Voice Integration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("Audio Service", test_audio_service),
        ("FastAPI Routes", test_fastapi_routes),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n Running {test_name} test...")
        if test_func():
            passed += 1
            print(f" {test_name} test passed")
        else:
            print(f" {test_name} test failed")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(" All tests passed! Voice integration is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the backend: uvicorn app.main:app --reload")
        print("3. Start the frontend: streamlit run streamlit_app.py")
        print("4. Test voice commands in the web interface!")
    else:
        print(" Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if you have sufficient disk space (model download requires ~1.5GB)")
        print("3. Ensure you have a stable internet connection for model download")

if __name__ == "__main__":
    main()
