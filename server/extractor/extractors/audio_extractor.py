"""
Audio metadata extractor for MetaExtract.

Specialized extractor for audio file formats including MP3, WAV, FLAC,
AAC, OGG, and other audio formats. Handles ID3 tags, Vorbis comments,
codec information, and advanced audio properties using mutagen.
"""

import logging
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

from ..core.base_engine import BaseExtractor, ExtractionContext, ExtractionResult, ExtractionStatus

logger = logging.getLogger(__name__)

# Availability flags for optional libraries
try:
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    from mutagen.oggvorbis import OggVorbis
    from mutagen.oggopus import OggOpus
    from mutagen.wave import WAVE
    from mutagen.aiff import AIFF
    # APE format is optional - don't fail if not available
    try:
        from mutagen.ape import APE
    except ImportError:
        pass  # APE format not available, but that's okay
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


class AudioExtractor(BaseExtractor):
    """
    Specialized extractor for audio file formats.
    
    Supports MP3, WAV, FLAC, AAC, OGG, M4A, and other common audio formats.
    Extracts ID3 tags, Vorbis comments, codec information, album art,
    and advanced audio metadata using mutagen.
    """
    
    def __init__(self):
        """Initialize the audio extractor."""
        supported_formats = [
            '.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.opus',
            '.wma', '.ape', '.aiff', '.aif', '.au', '.ra', '.mid',
            '.midi', '.wv', '.tak', '.dsf', '.dff'
        ]
        super().__init__("audio_extractor", supported_formats)
        self.logger = logging.getLogger(__name__)
    
    def _extract_metadata(self, context: ExtractionContext) -> Dict[str, Any]:
        """
        Extract metadata from an audio file.
        
        Args:
            context: Extraction context containing file information
            
        Returns:
            Dictionary containing extracted audio metadata
        """
        filepath = context.filepath
        metadata = {}
        
        try:
            if not MUTAGEN_AVAILABLE:
                metadata["error"] = "Mutagen library not available"
                return metadata
            
            # Basic audio properties
            basic_properties = self._extract_basic_properties(filepath)
            if basic_properties:
                metadata["basic_properties"] = basic_properties
            
            # Format-specific metadata
            format_info = self._extract_format_info(filepath)
            if format_info:
                metadata["format_info"] = format_info
            
            # ID3 tags (for MP3 files)
            id3_tags = self._extract_id3_tags(filepath)
            if id3_tags:
                metadata["id3"] = id3_tags
            
            # Vorbis comments (for OGG/FLAC files)
            vorbis_comments = self._extract_vorbis_comments(filepath)
            if vorbis_comments:
                metadata["vorbis"] = vorbis_comments
            
            # Album art
            album_art = self._extract_album_art(filepath)
            if album_art:
                metadata["album_art"] = album_art
            
            # Advanced audio properties
            advanced_properties = self._extract_advanced_properties(filepath)
            if advanced_properties:
                metadata["advanced"] = advanced_properties
            
            # Add extraction statistics
            metadata["extraction_stats"] = {
                "mutagen_available": MUTAGEN_AVAILABLE,
                "basic_properties": bool(basic_properties),
                "format_info": bool(format_info),
                "id3_tags": bool(id3_tags),
                "vorbis_comments": bool(vorbis_comments),
                "album_art": bool(album_art),
                "advanced_properties": bool(advanced_properties)
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Audio extraction failed for {filepath}: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _extract_basic_properties(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract basic audio properties using mutagen."""
        try:
            audio = mutagen.File(filepath)
            if not audio:
                return None
            
            result = {
                "format": type(audio).__name__,
                "length_seconds": round(audio.info.length, 2) if hasattr(audio.info, "length") else None,
                "bitrate": getattr(audio.info, "bitrate", None),
                "sample_rate": getattr(audio.info, "sample_rate", None),
                "channels": getattr(audio.info, "channels", None),
                "bits_per_sample": getattr(audio.info, "bits_per_sample", None),
            }
            
            # Human-readable length
            length_seconds = result.get("length_seconds")
            if isinstance(length_seconds, (int, float)):
                mins = int(length_seconds // 60)
                secs = int(length_seconds % 60)
                result["length_human"] = f"{mins}:{secs:02d}"
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Basic audio properties extraction failed for {filepath}: {e}")
            return None
    
    def _extract_format_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract format-specific information."""
        try:
            audio = mutagen.File(filepath)
            if not audio:
                return None
            
            ext = Path(filepath).suffix.lower()
            result = {
                "file_format": ext,
                "mutagen_format": type(audio).__name__,
                "info_available": hasattr(audio, 'info'),
                "tags_available": hasattr(audio, 'tags'),
            }
            
            # Format-specific details
            if ext == '.mp3':
                result.update(self._extract_mp3_specific(audio))
            elif ext == '.flac':
                result.update(self._extract_flac_specific(audio))
            elif ext in ['.m4a', '.aac']:
                result.update(self._extract_m4a_specific(audio))
            elif ext == '.ogg':
                result.update(self._extract_ogg_specific(audio))
            elif ext == '.wav':
                result.update(self._extract_wav_specific(audio))
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Format info extraction failed for {filepath}: {e}")
            return None
    
    def _extract_mp3_specific(self, audio) -> Dict[str, Any]:
        """Extract MP3-specific metadata."""
        result = {}
        
        if isinstance(audio, mutagen.mp3.MP3):
            result["mp3_specific"] = {
                "version": getattr(audio.info, "version", None),
                "layer": getattr(audio.info, "layer", None),
                "mode": getattr(audio.info, "mode", None),
                "emphasis": getattr(audio.info, "emphasis", None),
                "copyright": getattr(audio.info, "copyright", None),
                "original": getattr(audio.info, "original", None),
            }
        
        return result
    
    def _extract_flac_specific(self, audio) -> Dict[str, Any]:
        """Extract FLAC-specific metadata."""
        result = {}
        
        if isinstance(audio, mutagen.flac.FLAC):
            result["flac_specific"] = {
                "total_samples": getattr(audio.info, "total_samples", None),
                "bits_per_sample": getattr(audio.info, "bits_per_sample", None),
                "md5_signature": getattr(audio.info, "md5_signature", None),
                "min_blocksize": getattr(audio.info, "min_blocksize", None),
                "max_blocksize": getattr(audio.info, "max_blocksize", None),
            }
            
            # FLAC metadata blocks
            if hasattr(audio, 'metadata_blocks'):
                result["metadata_blocks"] = len(audio.metadata_blocks)
        
        return result
    
    def _extract_m4a_specific(self, audio) -> Dict[str, Any]:
        """Extract M4A/AAC-specific metadata."""
        result = {}
        
        if isinstance(audio, mutagen.mp4.MP4):
            result["m4a_specific"] = {
                "codec": getattr(audio.info, "codec", None),
                "bitrate": getattr(audio.info, "bitrate", None),
                "sample_rate": getattr(audio.info, "sample_rate", None),
                "channels": getattr(audio.info, "channels", None),
            }
        
        return result
    
    def _extract_ogg_specific(self, audio) -> Dict[str, Any]:
        """Extract OGG-specific metadata."""
        result = {}
        
        if isinstance(audio, (mutagen.oggvorbis.OggVorbis, mutagen.oggopus.OggOpus)):
            result["ogg_specific"] = {
                "vendor": getattr(audio.info, "vendor", None),
                "version": getattr(audio.info, "version", None),
            }
        
        return result
    
    def _extract_wav_specific(self, audio) -> Dict[str, Any]:
        """Extract WAV-specific metadata."""
        result = {}
        
        if isinstance(audio, mutagen.wave.WAVE):
            result["wav_specific"] = {
                "sample_width": getattr(audio.info, "sample_width", None),
                "frame_rate": getattr(audio.info, "frame_rate", None),
                "frame_count": getattr(audio.info, "n_frames", None),
                "compression_type": getattr(audio.info, "compression_type", None),
                "compression_name": getattr(audio.info, "compression_name", None),
            }
        
        return result
    
    def _extract_id3_tags(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract ID3 tags (primarily for MP3 files)."""
        try:
            audio = mutagen.File(filepath)
            if not audio or not audio.tags:
                return None
            
            ext = Path(filepath).suffix.lower()
            if ext != '.mp3':
                return None
            
            # Extract all ID3 tags
            id3_tags = {}
            for key, value in audio.tags.items():
                try:
                    if hasattr(value, "text"):
                        id3_tags[key] = str(value.text[0]) if value.text else None
                    elif isinstance(value, list):
                        id3_tags[key] = str(value[0]) if value else None
                    else:
                        id3_tags[key] = str(value)
                except (IndexError, AttributeError, TypeError):
                    continue
            
            # Standard ID3 tags mapping
            standard_tags = {
                "title": id3_tags.get("TIT2") or id3_tags.get("TITLE"),
                "artist": id3_tags.get("TPE1") or id3_tags.get("ARTIST"),
                "album": id3_tags.get("TALB") or id3_tags.get("ALBUM"),
                "year": id3_tags.get("TDRC") or id3_tags.get("DATE"),
                "genre": id3_tags.get("TCON") or id3_tags.get("GENRE"),
                "track_number": id3_tags.get("TRCK") or id3_tags.get("TRACKNUMBER"),
                "composer": id3_tags.get("TCOM") or id3_tags.get("COMPOSER"),
                "album_artist": id3_tags.get("TPE2") or id3_tags.get("ALBUMARTIST"),
                "comment": id3_tags.get("COMM") or id3_tags.get("COMMENT"),
                "lyrics": id3_tags.get("USLT") or id3_tags.get("LYRICS"),
                "publisher": id3_tags.get("TPUB") or id3_tags.get("PUBLISHER"),
                "bpm": id3_tags.get("TBPM") or id3_tags.get("BPM"),
                "copyright": id3_tags.get("TCOP") or id3_tags.get("COPYRIGHT"),
            }
            
            return {
                "all_tags": id3_tags,
                "standard_tags": {k: v for k, v in standard_tags.items() if v},
                "tag_count": len(id3_tags),
                "has_album_art": "APIC" in id3_tags or any("APIC" in str(k) for k in audio.tags.keys())
            }
            
        except Exception as e:
            self.logger.warning(f"ID3 tags extraction failed for {filepath}: {e}")
            return None
    
    def _extract_vorbis_comments(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract Vorbis comments (for OGG/FLAC files)."""
        try:
            audio = mutagen.File(filepath)
            if not audio or not audio.tags:
                return None
            
            ext = Path(filepath).suffix.lower()
            if ext not in ['.ogg', '.flac', '.opus']:
                return None
            
            # Extract Vorbis comments
            vorbis_comments = {}
            for key, value in audio.tags.items():
                try:
                    if isinstance(value, list):
                        vorbis_comments[key] = [str(v) for v in value]
                    else:
                        vorbis_comments[key] = str(value)
                except (AttributeError, TypeError):
                    continue
            
            # Standard Vorbis comment mapping
            standard_comments = {
                "title": vorbis_comments.get("TITLE"),
                "artist": vorbis_comments.get("ARTIST"),
                "album": vorbis_comments.get("ALBUM"),
                "year": vorbis_comments.get("DATE"),
                "genre": vorbis_comments.get("GENRE"),
                "track_number": vorbis_comments.get("TRACKNUMBER"),
                "composer": vorbis_comments.get("COMPOSER"),
                "album_artist": vorbis_comments.get("ALBUMARTIST"),
                "comment": vorbis_comments.get("COMMENT"),
                "description": vorbis_comments.get("DESCRIPTION"),
                "version": vorbis_comments.get("VERSION"),
            }
            
            return {
                "all_comments": vorbis_comments,
                "standard_comments": {k: v for k, v in standard_comments.items() if v},
                "comment_count": len(vorbis_comments),
            }
            
        except Exception as e:
            self.logger.warning(f"Vorbis comments extraction failed for {filepath}: {e}")
            return None
    
    def _extract_album_art(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract album art information."""
        try:
            audio = mutagen.File(filepath)
            if not audio:
                return None
            
            album_art_info = {
                "has_album_art": False,
                "art_count": 0,
                "art_types": [],
                "mime_types": [],
                "descriptions": []
            }
            
            # Check for album art in different formats
            if hasattr(audio, "pictures") and audio.pictures:
                album_art_info["has_album_art"] = True
                album_art_info["art_count"] = len(audio.pictures)
                album_art_info["art_types"] = [getattr(pic, 'type', 'unknown') for pic in audio.pictures]
                album_art_info["mime_types"] = [getattr(pic, 'mime', 'unknown') for pic in audio.pictures]
                album_art_info["descriptions"] = [getattr(pic, 'desc', '') for pic in audio.pictures]
            
            # Check for ID3 album art (APIC frames)
            elif hasattr(audio, 'tags') and audio.tags:
                apic_frames = [k for k in audio.tags.keys() if "APIC" in str(k)]
                if apic_frames:
                    album_art_info["has_album_art"] = True
                    album_art_info["art_count"] = len(apic_frames)
                    album_art_info["art_types"] = ["APIC" for _ in apic_frames]
            
            return album_art_info if album_art_info["has_album_art"] else None
            
        except Exception as e:
            self.logger.warning(f"Album art extraction failed for {filepath}: {e}")
            return None
    
    def _extract_advanced_properties(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract advanced audio properties."""
        try:
            audio = mutagen.File(filepath)
            if not audio:
                return None
            
            advanced = {}
            
            # Audio fingerprinting (if available)
            if hasattr(audio, 'fingerprint'):
                advanced["fingerprint"] = str(audio.fingerprint)
            
            # ReplayGain information
            replaygain = {}
            for key, value in (audio.tags or {}).items():
                if "replaygain" in str(key).lower():
                    replaygain[key] = str(value)
            if replaygain:
                advanced["replaygain"] = replaygain
            
            # Encoding information
            encoding = {}
            encoding_keys = ["TENC", "encoded_by", "ENCODER", "ENCODING"]
            for key, value in (audio.tags or {}).items():
                if any(enc_key in str(key).upper() for enc_key in encoding_keys):
                    encoding[key] = str(value)
            if encoding:
                advanced["encoding"] = encoding
            
            # Technical specifications
            technical = {}
            if hasattr(audio.info, 'bitrate_mode'):
                technical["bitrate_mode"] = audio.info.bitrate_mode
            if hasattr(audio.info, 'codec_name'):
                technical["codec_name"] = audio.info.codec_name
            if hasattr(audio.info, 'profile'):
                technical["profile"] = audio.info.profile
            if technical:
                advanced["technical"] = technical
            
            return advanced if advanced else None
            
        except Exception as e:
            self.logger.warning(f"Advanced properties extraction failed for {filepath}: {e}")
            return None
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get information about this extractor."""
        return {
            "name": self.name,
            "supported_formats": self.supported_formats,
            "capabilities": {
                "basic_properties": True,
                "format_info": True,
                "id3_tags": True,
                "vorbis_comments": True,
                "album_art": True,
                "advanced_properties": True,
                "mutagen": MUTAGEN_AVAILABLE
            },
            "version": "1.0.0"
        }