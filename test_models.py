#!/usr/bin/env python3
"""
Quick test script for Coqui TTS and Whisper integration
"""

import torch
from TTS.api import TTS
import whisper
from pathlib import Path
import time

def test_models():
    print("🔍 Testing Local TTS and STT Models")
    print("=" * 50)
    
    # Test device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"📱 Using device: {device}")
    
    # Test Whisper
    print("\n🎤 Testing Whisper STT...")
    try:
        whisper_model = whisper.load_model("base")
        print("✅ Whisper model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading Whisper: {e}")
        return
    
    # Test TTS
    print("\n🔊 Testing Coqui TTS...")
    try:
        # Try different models for speed comparison
        models_to_try = [
            "tts_models/en/ljspeech/fast_pitch",
            "tts_models/en/ljspeech/tacotron2-DDC",
            "tts_models/en/ljspeech/glow-tts"
        ]
        
        tts_model = None
        for model_name in models_to_try:
            try:
                print(f"🔄 Trying model: {model_name}")
                start_time = time.time()
                tts_model = TTS(model_name).to(device)
                load_time = time.time() - start_time
                print(f"✅ {model_name} loaded in {load_time:.2f}s")
                break
            except Exception as e:
                print(f"❌ Failed to load {model_name}: {e}")
                continue
        
        if tts_model is None:
            print("❌ No TTS model could be loaded")
            return
            
    except Exception as e:
        print(f"❌ Error with TTS: {e}")
        return
    
    # Test TTS generation
    print("\n🎵 Testing TTS generation...")
    try:
        test_text = "Hello, this is a test of the local text to speech system."
        output_path = Path(__file__).parent / "test_output.wav"
        
        start_time = time.time()
        tts_model.tts_to_file(text=test_text, file_path=str(output_path))
        generation_time = time.time() - start_time
        
        print(f"✅ TTS generation completed in {generation_time:.2f}s")
        print(f"📁 Audio saved to: {output_path}")
        
        if output_path.exists():
            file_size = output_path.stat().st_size / 1024  # KB
            print(f"📊 File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error generating TTS: {e}")
        return
    
    # Performance summary
    print("\n📈 Performance Summary:")
    print(f"  • Device: {device}")
    print(f"  • TTS Model: {tts_model.model_name}")
    print(f"  • TTS Generation Time: {generation_time:.2f}s")
    print(f"  • Text Length: {len(test_text)} characters")
    print(f"  • Speed: {len(test_text)/generation_time:.1f} chars/sec")
    
    print("\n🎉 All tests completed successfully!")
    print("\n💡 Tips for optimization:")
    print("  • Use GPU if available for faster processing")
    print("  • Consider FastPitch or GlowTTS for lower latency")
    print("  • Keep models loaded in memory to avoid reload time")

if __name__ == "__main__":
    test_models()
