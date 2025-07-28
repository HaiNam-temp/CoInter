#!/usr/bin/env python3
"""
Simple test script to debug the process_audio_local endpoint
"""
import requests
import os
from pathlib import Path

def test_audio_endpoint():
    url = "http://localhost:5000/process_audio_local"
    
    # Create a simple test audio file (empty for testing)
    test_audio_path = Path(__file__).parent / "test_audio.webm"
    
    # Create an empty file for testing
    with open(test_audio_path, 'wb') as f:
        f.write(b'fake audio data for testing')
    
    try:
        # Test the endpoint
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio': ('test_audio.webm', audio_file, 'audio/webm')}
            
            print("Sending request to /process_audio_local...")
            response = requests.post(url, files=files)
            
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Flask server. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up test file
        if test_audio_path.exists():
            test_audio_path.unlink()

if __name__ == "__main__":
    test_audio_endpoint()
