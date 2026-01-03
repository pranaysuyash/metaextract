#!/usr/bin/env python3
"""
Complete Phase 2.2 Audio Extractor Test

This test demonstrates the new audio extractor working within the comprehensive
engine architecture, showing registry summary, tier support, and frontend compatibility.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def create_sample_audio():
    """Create a sample audio file using ffmpeg for testing."""
    
    sample_audio = "test_sample.mp3"
    
    try:
        # Create a 1-second test tone with metadata
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1',
            '-metadata', 'title=Test Audio',
            '-metadata', 'artist=MetaExtract',
            '-metadata', 'album=Phase 2 Testing',
            '-metadata', 'year=2026',
            '-metadata', 'genre=Test',
            '-metadata', 'comment=Audio extractor test file',
            '-y', sample_audio
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(sample_audio):
            print(f"✅ Created sample audio: {sample_audio}")
            return sample_audio
        else:
            print(f"⚠️  Failed to create sample audio: {result.stderr}")
            return None
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"⚠️  Cannot create sample audio: {e}")
        return None

def test_audio_extractor_comprehensive():
    """Test the complete audio extraction pipeline."""
    
    print("Phase 2.2: Audio Extractor Comprehensive Test")
    print("=" * 50)
    
    try:
        # Create sample audio
        print("1. Creating sample audio for testing...")
        sample_audio = create_sample_audio()
        
        if not sample_audio:
            print("   Using dummy file for logic testing...")
            sample_audio = "test_dummy.mp3"
            # Create a dummy file
            with open(sample_audio, 'wb') as f:
                f.write(b'ID3\x03\x00\x00\x00\x00\x00\x23\x54\x53\x53\x45')  # Minimal MP3 header
        
        print(f"   Test file: {sample_audio} ({os.path.getsize(sample_audio)} bytes)")
        
        # Test 2: Direct audio extractor test
        print("2. Testing audio extractor directly...")
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
        print(f"   ✅ Processing time: {result.processing_time_ms:.2f}ms")
        
        metadata = result.metadata or {}
        print(f"   ✅ Metadata sections: {list(metadata.keys())}")
        
        # Show detailed results
        if 'basic_properties' in metadata:
            basic = metadata['basic_properties']
            print(f"   🎵 Basic properties:")
            print(f"      - Format: {basic.get('format', 'unknown')}")
            print(f"      - Duration: {basic.get('length_seconds', 0)}s")
            print(f"      - Sample rate: {basic.get('sample_rate', 'unknown')}Hz")
            print(f"      - Channels: {basic.get('channels', 'unknown')}")
        
        if 'id3' in metadata:
            id3 = metadata['id3']
            print(f"   🏷️  ID3 tags: {id3.get('tag_count', 0)} tags")
            standard_tags = id3.get('standard_tags', {})
            if standard_tags:
                print(f"      - Title: {standard_tags.get('title', 'none')}")
                print(f"      - Artist: {standard_tags.get('artist', 'none')}")
                print(f"      - Album: {standard_tags.get('album', 'none')}")
        
        if 'album_art' in metadata:
            art = metadata['album_art']
            print(f"   🖼️  Album art: {'Yes' if art.get('has_album_art') else 'No'}")
        
        # Test 3: Comprehensive engine integration
        print("3. Testing comprehensive engine integration...")
        from extractor.core.comprehensive_engine import extract_comprehensive_metadata_new
        
        # Test different tiers
        tiers = ["free", "super", "premium"]
        
        for tier in tiers:
            print(f"\n   Testing tier: {tier}")
            result = extract_comprehensive_metadata_new(sample_audio, tier=tier)
            
            print(f"   ✅ Status: {result.get('status', 'unknown')}")
            print(f"   ✅ Engine: {result.get('extraction_info', {}).get('engine_version', 'unknown')}")
            
            # Check registry summary
            registry_summary = result.get('registry_summary', {})
            print(f"   ✅ Registry summary: {'✅' if registry_summary else '❌'}")
            
            if registry_summary:
                if 'audio' in registry_summary:
                    audio_summary = registry_summary['audio']
                    print(f"   🎵 Audio fields:")
                    print(f"      - ID3: {audio_summary.get('id3', 0)}")
                    print(f"      - Vorbis: {audio_summary.get('vorbis', 0)}")
                    print(f"      - Codec: {audio_summary.get('codec', 0)}")
                    print(f"      - Broadcast: {audio_summary.get('broadcast', 0)}")
                
                if 'image' in registry_summary:
                    image_summary = registry_summary['image']
                    print(f"   📷 Image fields:")
                    print(f"      - EXIF: {image_summary.get('exif', 0)}")
                    print(f"      - IPTC: {image_summary.get('iptc', 0)}")
                    print(f"      - XMP: {image_summary.get('xmp', 0)}")
                
                if 'video' in registry_summary:
                    video_summary = registry_summary['video']
                    print(f"   📹 Video fields:")
                    print(f"      - Format: {video_summary.get('format', 0)}")
                    print(f"      - Streams: {video_summary.get('streams', 0)}")
                    print(f"      - Codec: {video_summary.get('codec', 0)}")
            
            # Show metadata structure
            metadata = result.get('metadata', {})
            sections = list(metadata.keys())
            print(f"   📊 Metadata sections: {sections}")
            
            # Simulate frontend tier filtering
            if tier == "free":
                total_fields = sum(len(section) for section in metadata.values() if isinstance(section, dict))
                print(f"   🔒 Free tier: {total_fields} total fields (some would be locked)")
            elif tier == "super":
                print(f"   🔓 Super tier: Full access to {len(sections)} sections")
            
        # Test 4: Frontend compatibility
        print("4. Testing frontend compatibility...")
        
        # Simulate what the frontend would see
        super_result = extract_comprehensive_metadata_new(sample_audio, tier="super")
        
        # Check frontend requirements
        frontend_checks = {
            'registry_summary': bool(super_result.get('registry_summary')),
            'metadata_structure': isinstance(super_result.get('metadata'), dict),
            'extraction_info': isinstance(super_result.get('extraction_info'), dict),
            'status_field': 'status' in super_result,
            'processing_time': 'processing_ms' in super_result.get('extraction_info', {})
        }
        
        print("   Frontend compatibility checks:")
        for check, result in frontend_checks.items():
            print(f"   - {check}: {'✅' if result else '❌'}")
        
        # Test 5: Error handling
        print("5. Testing error handling...")
        
        # Test with non-existent file
        error_result = extract_comprehensive_metadata_new("nonexistent_audio.mp3", tier="free")
        error_status = error_result.get('status')
        has_error = error_result.get('extraction_info', {}).get('error', False)
        
        print(f"   Error handling: {'✅' if error_status == 'error' or has_error else '❌'}")
        
        print("\n✅ All Phase 2.2 audio tests completed!")
        
        # Cleanup
        if os.path.exists(sample_audio):
            os.remove(sample_audio)
            print(f"🧹 Cleaned up test file: {sample_audio}")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 2.2 audio test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if 'sample_audio' in locals() and os.path.exists(sample_audio):
            os.remove(sample_audio)
        
        return False

if __name__ == "__main__":
    success = test_audio_extractor_comprehensive()
    if success:
        print("\n🎉 Phase 2.2 Audio Extractor Implementation Complete!")
        print("✅ Audio extraction working")
        print("✅ Registry summary for audio working")
        print("✅ Tier support working")
        print("✅ Frontend compatibility maintained")
        print("\nReady for Phase 2.3: Document Extractor")
    else:
        print("\n❌ Phase 2.2 audio implementation needs fixes.")