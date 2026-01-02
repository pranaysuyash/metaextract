#!/usr/bin/env python3
"""
Unit tests for Audio Analysis Plugin
"""

import pytest
import tempfile
import os
from plugins.audio_analysis_plugin import (
    extract_audio_metadata,
    analyze_audio_quality,
    detect_audio_features,
    get_plugin_metadata
)


class TestAudioPlugin:
    """Test suite for Audio Analysis Plugin"""
    
    def test_get_plugin_metadata(self):
        """Test plugin metadata function"""
        metadata = get_plugin_metadata()
        
        # Verify metadata structure
        assert isinstance(metadata, dict)
        assert "version" in metadata
        assert "author" in metadata
        assert "description" in metadata
        assert "license" in metadata
        
        # Verify metadata values
        assert metadata["version"] == "1.0.0"
        assert metadata["author"] == "MetaExtract Team"
        assert "audio" in metadata["description"].lower()
        assert metadata["license"] == "MIT"
    
    def test_extract_audio_metadata_mp3(self):
        """Test MP3 metadata extraction"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            # Write MP3 header
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)
            test_file = f.name
        
        try:
            result = extract_audio_metadata(test_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "audio_analysis" in result
            
            # Verify required fields
            analysis = result["audio_analysis"]
            assert analysis["processed"] is True
            assert "timestamp" in analysis
            assert "file_size" in analysis
            assert "file_extension" in analysis
            assert "file_name" in analysis
            assert "plugin_version" in analysis
            
            # Verify MP3-specific fields
            assert analysis["audio_format"] == "MPEG Audio Layer III"
            assert "mp3_specific" in analysis
            assert analysis["mp3_specific"]["likely_has_id3_tags"] is True
            
        finally:
            os.unlink(test_file)
    
    def test_extract_audio_metadata_wav(self):
        """Test WAV metadata extraction"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # Write WAV header
            f.write(b'RIFF\x00\x00\x00\x00WAVEfmt ' + b'\x00' * 100)
            test_file = f.name
        
        try:
            result = extract_audio_metadata(test_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "audio_analysis" in result
            
            # Verify WAV-specific fields
            analysis = result["audio_analysis"]
            assert analysis["audio_format"] == "Waveform Audio File Format"
            assert "wav_specific" in analysis
            assert analysis["wav_specific"]["likely_has_RIFF_header"] is True
            
        finally:
            os.unlink(test_file)
    
    def test_extract_audio_metadata_flac(self):
        """Test FLAC metadata extraction"""
        with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as f:
            # Write FLAC header
            f.write(b'fLaC\x00\x00\x00\x22' + b'\x00' * 100)
            test_file = f.name
        
        try:
            result = extract_audio_metadata(test_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "audio_analysis" in result
            
            # Verify FLAC-specific fields
            analysis = result["audio_analysis"]
            assert analysis["audio_format"] == "Free Lossless Audio Codec"
            assert "flac_specific" in analysis
            assert analysis["flac_specific"]["likely_has_vorbis_comments"] is True
            
        finally:
            os.unlink(test_file)
    
    def test_extract_audio_metadata_unknown(self):
        """Test unknown format handling"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b'test content')
            test_file = f.name
        
        try:
            result = extract_audio_metadata(test_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "audio_analysis" in result
            
            # Verify unknown format handling
            analysis = result["audio_analysis"]
            assert analysis["audio_format"] == "unknown"
            
        finally:
            os.unlink(test_file)
    
    def test_analyze_audio_quality_large_file(self):
        """Test quality analysis with large file"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            # Write large MP3 file
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 10000)  # ~10KB
            test_file = f.name
        
        try:
            result = analyze_audio_quality(test_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "audio_quality" in result
            
            # Verify quality metrics
            quality = result["audio_quality"]
            assert "quality_score" in quality
            assert "bitrate_estimate" in quality
            assert "sample_rate_estimate" in quality
            assert "channels_estimate" in quality
            assert "compression_quality" in quality
            
            # Verify large file gets higher quality score
            assert quality["quality_score"] >= 0.7
            assert quality["bitrate_estimate"] in ["medium", "high"]
            
        finally:
            os.unlink(test_file)
    
    def test_analyze_audio_quality_small_file(self):
        """Test quality analysis with small file"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            # Write small MP3 file
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)  # ~100B
            test_file = f.name
        
        try:
            result = analyze_audio_quality(test_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "audio_quality" in result
            
            # Verify quality metrics for small file
            quality = result["audio_quality"]
            assert quality["quality_score"] <= 0.8
            assert quality["bitrate_estimate"] in ["low", "medium"]
            
        finally:
            os.unlink(test_file)
    
    def test_analyze_audio_quality_lossless(self):
        """Test quality analysis with lossless format"""
        with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as f:
            f.write(b'fLaC\x00\x00\x00\x22' + b'\x00' * 1000)
            test_file = f.name
        
        try:
            result = analyze_audio_quality(test_file)
            
            # Verify lossless format gets high quality score
            quality = result["audio_quality"]
            assert quality["quality_score"] >= 0.9
            assert quality["compression_quality"] == "lossless"
            
        finally:
            os.unlink(test_file)
    
    def test_detect_audio_features_music(self):
        """Test feature detection with music file"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)
            test_file = f.name
        
        try:
            # Create a test file with music in the name
            music_file = test_file.replace('.mp3', '_music_song.mp3')
            os.rename(test_file, music_file)
            test_file = music_file
            
            result = detect_audio_features(test_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "audio_features" in result
            
            # Verify music detection
            features = result["audio_features"]
            assert "likely_contains" in features
            assert "music" in features["likely_contains"]
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_detect_audio_features_speech(self):
        """Test feature detection with speech file"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)
            test_file = f.name
        
        try:
            # Create a test file with speech in the name
            speech_file = test_file.replace('.mp3', '_speech_podcast.mp3')
            os.rename(test_file, speech_file)
            test_file = speech_file
            
            result = detect_audio_features(test_file)
            
            # Verify speech detection
            features = result["audio_features"]
            assert "speech" in features["likely_contains"]
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_detect_audio_features_format_specific(self):
        """Test format-specific feature detection"""
        # Test MP3
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)
            mp3_file = f.name
        
        try:
            result = detect_audio_features(mp3_file)
            features = result["audio_features"]
            
            # Verify MP3-specific features
            assert "format_specific" in features
            assert features["format_specific"]["supports_id3_tags"] is True
            assert features["format_specific"]["supports_cover_art"] is True
            
        finally:
            os.unlink(mp3_file)
        
        # Test WAV
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b'RIFF\x00\x00\x00\x00WAVEfmt ' + b'\x00' * 100)
            wav_file = f.name
        
        try:
            result = detect_audio_features(wav_file)
            features = result["audio_features"]
            
            # Verify WAV-specific features
            assert "format_specific" in features
            assert features["format_specific"]["supports_RIFF_metadata"] is True
            assert features["format_specific"]["supports_cover_art"] is False
            
        finally:
            os.unlink(wav_file)
    
    def test_error_handling_nonexistent_file(self):
        """Test error handling for nonexistent file"""
        result = extract_audio_metadata("/nonexistent/path/file.mp3")
        
        # Verify error response
        assert isinstance(result, dict)
        assert "audio_analysis" in result
        assert result["audio_analysis"]["processed"] is False
        assert "error" in result["audio_analysis"]
    
    def test_error_handling_permission_error(self):
        """Test error handling for permission issues"""
        # Create a file and make it unreadable (simulated)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)
            test_file = f.name
        
        try:
            # Change permissions to make file unreadable
            os.chmod(test_file, 0o000)
            
            result = extract_audio_metadata(test_file)
            
            # On some systems, permission changes might not work as expected
            # So we check both cases: actual permission error or successful read
            if result["audio_analysis"]["processed"] is False:
                # Permission error was properly caught
                assert "error" in result["audio_analysis"]
                assert result["audio_analysis"]["error_type"] == "PermissionError"
            else:
                # File was still readable (common on some systems)
                # This is acceptable - the important thing is no crash
                assert result["audio_analysis"]["processed"] is True
                print("Note: Permission test - file was still readable (system-dependent)")
            
        finally:
            # Restore permissions and clean up
            try:
                os.chmod(test_file, 0o644)
                os.unlink(test_file)
            except:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
