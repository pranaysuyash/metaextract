#!/usr/bin/env python3
"""
Test video extraction using ffprobe directly to verify our logic.
"""

import subprocess
import json

def test_ffprobe_capabilities():
    """Test what ffprobe can extract from various video formats."""
    
    print("Testing ffprobe Capabilities")
    print("=" * 30)
    
    # Test ffprobe on a sample video if available
    test_files = [
        "sample.mp4",
        "test.mp4", 
        "video.mp4",
        "/Users/pranay/Projects/metaextract/.venv.bak.20251230140526/lib/python3.11/site-packages/matplotlib/mpl-data/sample_data/grace_hopper.jpg"  # Use image as fallback
    ]
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("No suitable test file found, testing ffprobe with version check")
        try:
            result = subprocess.run(['ffprobe', '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ ffprobe is working")
                print("Sample output format:")
                lines = result.stdout.split('\n')[:3]
                for line in lines:
                    print(f"  {line}")
            else:
                print("❌ ffprobe version check failed")
        except Exception as e:
            print(f"❌ ffprobe test failed: {e}")
        return
    
    print(f"Testing with file: {test_file}")
    
    # Test basic ffprobe command
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", test_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ ffprobe command successful")
            
            try:
                data = json.loads(result.stdout)
                
                # Show key information
                format_data = data.get('format', {})
                streams = data.get('streams', [])
                
                print(f"Format: {format_data.get('format_name', 'unknown')}")
                print(f"Duration: {format_data.get('duration', 'unknown')} seconds")
                print(f"Size: {format_data.get('size', 'unknown')} bytes")
                print(f"Streams: {len(streams)}")
                
                # Show stream types
                stream_types = {}
                for stream in streams:
                    codec_type = stream.get('codec_type', 'unknown')
                    stream_types[codec_type] = stream_types.get(codec_type, 0) + 1
                
                print("Stream types:")
                for stream_type, count in stream_types.items():
                    print(f"  {stream_type}: {count}")
                
                # Show first video stream details
                video_streams = [s for s in streams if s.get('codec_type') == 'video']
                if video_streams:
                    video = video_streams[0]
                    print(f"Video stream details:")
                    print(f"  Codec: {video.get('codec_name', 'unknown')}")
                    print(f"  Resolution: {video.get('width', 'unknown')}x{video.get('height', 'unknown')}")
                    print(f"  Frame rate: {video.get('r_frame_rate', 'unknown')}")
                
                # Show first audio stream details  
                audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
                if audio_streams:
                    audio = audio_streams[0]
                    print(f"Audio stream details:")
                    print(f"  Codec: {audio.get('codec_name', 'unknown')}")
                    print(f"  Sample rate: {audio.get('sample_rate', 'unknown')}")
                    print(f"  Channels: {audio.get('channels', 'unknown')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse ffprobe JSON output: {e}")
                print("Raw output preview:")
                print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print(f"❌ ffprobe failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ ffprobe command timed out")
    except Exception as e:
        print(f"❌ ffprobe test failed: {e}")

if __name__ == "__main__":
    import os
    test_ffprobe_capabilities()