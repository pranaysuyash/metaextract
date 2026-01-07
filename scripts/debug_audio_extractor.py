#!/usr/bin/env python3
"""
Debug script for the audio extractor.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def debug_audio_extractor():
    """Debug the audio extractor issues."""
    
    print("Debugging Audio Extractor")
    print("=" * 30)
    
    try:
        # Test 1: Check mutagen directly
        print("1. Testing mutagen directly...")
        try:
            import mutagen
            audio = mutagen.File("test_sample.mp3")
            print(f"   Mutagen result: {audio}")
            if audio:
                print(f"   Format: {type(audio).__name__}")
                print(f"   Info: {audio.info}")
                print(f"   Tags: {audio.tags}")
            else:
                print("   Mutagen returned None")
        except Exception as e:
            print(f"   Mutagen error: {e}")
        
        # Test 2: Create a better test audio
        print("2. Creating better test audio...")
        sample_audio = "test_better.mp3"
        
        try:
            # Create a 3-second test tone with better encoding
            cmd = [
                'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=3',
                '-acodec', 'libmp3lame', '-ab', '128k',
                '-metadata', 'title=Test Audio',
                '-metadata', 'artist=MetaExtract',
                '-metadata', 'album=Phase 2 Testing',
                '-y', sample_audio
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(sample_audio):
                print(f"   ✅ Created better audio: {sample_audio}")
                print(f"   Size: {os.path.getsize(sample_audio)} bytes")
                
                # Test mutagen on the new file
                try:
                    import mutagen
                    audio = mutagen.File(sample_audio)
                    print(f"   Mutagen on new file: {audio}")
                    if audio:
                        print(f"   Format: {type(audio).__name__}")
                        print(f"   Has info: {hasattr(audio, 'info')}")
                        print(f"   Has tags: {hasattr(audio, 'tags')}")
                        if hasattr(audio, 'info'):
                            print(f"   Info attributes: {dir(audio.info)}")
                        if hasattr(audio, 'tags') and audio.tags:
                            print(f"   Tags keys: {list(audio.tags.keys())[:5]}")
                except Exception as e:
                    print(f"   Mutagen error on new file: {e}")
                    
                # Test our extractor
                print("3. Testing our extractor...")
                from extractor.extractors.audio_extractor import AudioExtractor
                from extractor.core.base_engine import ExtractionContext
                
                extractor = AudioExtractor()
                context = ExtractionContext(
                    filepath=sample_audio,
                    file_size=os.path.getsize(sample_audio),
                    file_extension=Path(sample_audio).suffix.lower(),
                    mime_type="audio/mpeg",
                    tier="free",
                    processing_options={},
                    execution_stats={}
                )
                
                result = extractor.extract(context)
                print(f"   ✅ Extraction status: {result.status}")
                print(f"   Metadata: {result.metadata}")
                
            else:
                print(f"   ❌ Failed to create better audio: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Error creating better audio: {e}")
        
        # Cleanup
        if os.path.exists(sample_audio):
            os.remove(sample_audio)
            
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_audio_extractor()