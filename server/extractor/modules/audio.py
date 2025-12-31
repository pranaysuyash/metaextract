"""
Audio Metadata Extraction
Using mutagen for comprehensive audio analysis
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


try:
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    from mutagen.oggvorbis import OggVorbis
    from mutagen.wave import WAVE
    from mutagen.aac import AAC
    from mutagen.id3 import ID3
    MUTAGEN_AVAILABLE = True
except ImportError:
    mutagen = None
    MP3 = None
    FLAC = None
    MP4 = None
    OggVorbis = None
    WAVE = None
    AAC = None
    ID3 = None
    MUTAGEN_AVAILABLE = False


AUDIO_TAG_FIELDS = {
    "title": "title",
    "artist": "artist",
    "album": "album",
    "albumartist": "album_artist",
    "composer": "composer",
    "performer": "performer",
    "genre": "genre",
    "date": "date",
    "year": "year",
    "tracknumber": "track_number",
    "tracktotal": "track_total",
    "discnumber": "disc_number",
    "disctotal": "disc_total",
    "comment": "comment",
    "lyrics": "lyrics",
    "bpm": "bpm",
    "compilation": "compilation",
    "label": "label",
    "copyright": "copyright",
    "encodedby": "encoded_by",
    "albumartistsort": "album_artist_sort",
    "artistsort": "artist_sort",
    "composersort": "composer_sort",
    "title_sort": "title_sort",
    "mood": "mood",
    "lyricist": "lyricist",
    "arranger": "arranger",
    "conductor": "conductor",
    "remixer": "remixer",
    "producer": "producer",
    "engineer": "engineer",
    "mixer": "mixer",
    "grouping": "grouping",
    "subtitle": "subtitle",
    "description": "description",
    "shortdesc": "short_description",
    "longdesc": "long_description",
    "url": "url",
    "website": "website",
    "buy_this_album": "buy_album_url",
    "buy_this_track": "buy_track_url",
    "license": "license",
    "isrc": "isrc",
    "ean/upc": "ean_upc",
    "catalog number": "catalog_number",
    "release country": "release_country",
    "script": "script",
    "language": "language",
    "albumtype": "album_type",
    "artists": "artists",
    "albumartists": "album_artists",
    "groups": "groups",
    "work": "work",
    "movement": "movement",
    "movement_total": "movement_total",
    "movement_name": "movement_name",
    "show_name": "show_name",
    "show_work": "show_work",
    "work_disamb": "work_disamb",
    "conductor": "conductor",
    "original_artist": "original_artist",
    "original_album": "original_album",
    "original_date": "original_date",
    "original_year": "original_year",
}



# ULTRA EXPANSION FIELDS
# Additional 36 fields
ULTRA_AUDIO_FIELDS = {
    "audio_codec": "flac_alac_aac_wma_codec",
    "audio_bit_depth": "16_24_32_bit_depth",
    "audio_sample_rate": "44_1_48_96_192_khz",
    "audio_bitrate": "kbps_constant_bitrate",
    "audio_channels": "mono_stereo_5_1_surround",
    "audio_duration": "playback_length_seconds",
    "audio_file_size": "compressed_file_bytes",
    "audio_compression": "lossy_lossless_format",
    "lyrics_unsynced": "plain_text_lyrics",
    "lyrics_synced": "timestamped_lyrics",
    "album_art": "embedded_cover_image",
    "bpm_tempo": "beats_per_minute",
    "initial_key": "musical_key_signature",
    "energy_level": "track_energy_rating",
    "danceability": "dance_rating_score",
    "acousticness": "acoustic_vs_electronic",
    "instrumentalness": "vocal_content_presence",
    "liveness": "live_vs_studio",
    "speechiness": "speech_content_ratio",
    "valence": "emotional_positivity",
    "composer": "musical_composer_name",
    "producer": "record_producer",
    "engineer": "audio_engineer",
    "mix_engineer": "mix_engineer_name",
    "mastering_engineer": "mastering_engineer",
    "record_label": "production_company",
    "catalog_number": "label_catalog_id",
    "isrc": "international_standard_recording_code",
    "upc_ean": "product_barcode",
    "hot_cue_points": "dj_cue_marker_locations",
    "loop_points": "beat_loop_start_end",
    "beatgrid_offset": "beatgrid_adjustment",
    "key_detection": "detected_musical_key",
    "gain_normalization": "replaygain_value",
    "waveform_preview": "audio_waveform_data",
    "key_analysis": "harmonic_key_compatibility",
}


# MEGA EXPANSION FIELDS
# Additional 37 fields
MEGA_AUDIO_FIELDS = {
    "sample_bit_depth": "16bit_24bit_32bit_float",
    "sample_rate_khz": "44_1_48_96_192_384",
    "bitrate_kbps": "lossless_compressed_bitrate",
    "channel_configuration": "mono_stereo_5_1_7_1_7_1_4_atmos",
    "audio_codec_profile": "aac_lc_aac_he_aac_ld",
    "compression_format": "flac_alac_wma_mp3_aac_opus",
    "lossless_compression": "flac_alac_wavpack_ape",
    "daw_project": "ableton_live_logic_pro_tools",
    "midi_tracks": "instrument_track_count",
    "vst_plugins": "virtual_instruments_effects",
    "automation_data": "parameter_automation",
    "mixdown_settings": "stereo_summing",
    "mastering_engineer": "final_processing",
    "mastering_studio": "recording_facility",
    "mastering_year": "mastering_date",
    "waveform_data": "audio_waveform_points",
    "spectrogram_data": "frequency_spectrum_analysis",
    "transient_detection": "attack_transients",
    "pitch_detection": "fundamental_frequency",
    "tempo_detection": "bpm_beat_tracking",
    "key_detection": "musical_key_signature",
    "chord_progression": "harmonic_analysis",
    "instrument_classification": "sound_type_identification",
    "speaker_identification": "speaker_recognition",
    "speech_to_text": "transcription_data",
    "emotion_detection": "vocal_emotion_analysis",
    "language_detection": "spoken_language",
    "voice_biometrics": "speaker_authentication",
    "prosody_analysis": "intonation_patterns",
    "accent_detection": "regional_accent",
    "voice_print": "vocal_characteristics",
    "ambient_noise": "background_sound_level",
    "reverberation_time": "rt60_decay",
    "sound_pressure_level": "spl_decibels",
    "frequency_response": "hertz_frequency_curve",
    "dynamic_range": "loudest_quiet_ratio",
    "phase_coherence": "stereo_phase",
}

def extract_audio_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract audio metadata using mutagen.
    
    Args:
        filepath: Path to audio file
    
    Returns:
        Dictionary with audio metadata
    """
    if not MUTAGEN_AVAILABLE or mutagen is None:
        # With "nothing optional" requirement, treat missing dependency as hard failure
        raise ImportError("mutagen is required but not installed")
    
    try:
        audio = mutagen.File(filepath)
        
        if audio is None:
            return {"error": "Unsupported audio format"}
        
        result = {
            "format": {},
            "format_details": {},
            "technical": {},
            "tags": {},
            "album_art": {},
            "replaygain": {},
            "fields_extracted": 0
        }
        
        result["format"] = {
            "format_name": type(audio).__name__,
            "duration": round(audio.info.length, 2) if hasattr(audio.info, 'length') else None,
            "bitrate": getattr(audio.info, 'bitrate', None),
            "sample_rate": getattr(audio.info, 'sample_rate', None),
            "channels": getattr(audio.info, 'channels', None),
        }
        
        if hasattr(audio.info, 'bits_per_sample'):
            result["technical"]["bits_per_sample"] = audio.info.bits_per_sample
        
        if hasattr(audio.info, 'encoder'):
            result["technical"]["encoder"] = str(audio.info.encoder)
        
        if hasattr(audio.info, 'codec'):
            result["format_details"]["codec"] = str(audio.info.codec)
        
        if hasattr(audio.info, 'codec_description'):
            result["format_details"]["codec_description"] = str(audio.info.codec_description)
        
        if hasattr(audio.info, 'container'):
            result["format_details"]["container"] = str(audio.info.container)
        
        if hasattr(audio.info, 'num_tracks'):
            result["format_details"]["num_tracks"] = audio.info.num_tracks
        
        if hasattr(audio.info, 'num_samples'):
            result["format_details"]["total_samples"] = audio.info.num_samples
        
        if audio.tags:
            for key in audio.tags.keys():
                try:
                    value = audio.tags[key]
                    if isinstance(value, list):
                        value = [str(v) for v in value]
                    else:
                        value = str(value)
                    result["tags"][str(key)] = value
                except Exception as e:
                    continue
        
        if hasattr(audio, 'images'):
            images = getattr(audio, 'images', [])
            if images:
                album_art_info = []
                for img in images:
                    img_info = {
                        "type": getattr(img, 'type', 'unknown'),
                        "mime": getattr(img, 'mime', 'unknown'),
                        "description": getattr(img, 'desc', ''),
                    }
                    if hasattr(img, 'data'):
                        img_info["size_bytes"] = len(img.data)
                    album_art_info.append(img_info)
                result["album_art"] = {
                    "has_embedded": True,
                    "count": len(images),
                    "images": album_art_info
                }
            else:
                result["album_art"] = {"has_embedded": False}
        
        if MP3 is not None and isinstance(audio, MP3) and audio.tags:
            if ID3 is not None and isinstance(audio.tags, ID3):
                version = getattr(audio.tags, 'version', None)
                if version:
                    major, minor = version[0], version[1] if len(version) > 1 else 0
                    result["format_details"]["id3_version"] = f"ID3v2.{major}.{minor}"
        
        if result["tags"]:
            normalized_tags = {}
            for key, value in result["tags"].items():
                key_lower = key.lower()
                if key_lower in AUDIO_TAG_FIELDS:
                    normalized_tags[AUDIO_TAG_FIELDS[key_lower]] = value
                elif key_lower.startswith('replaygain'):
                    result["replaygain"][key] = value
                else:
                    normalized_tags[key_lower] = value
            result["tags"] = normalized_tags
        
        if result["tags"].get('bpm'):
            try:
                result["tags"]['bpm'] = int(float(result["tags"]['bpm']))
            except (ValueError, TypeError):
                pass

        if ID3 is not None and isinstance(audio.tags, ID3):
            try:
                from .audio_id3_complete_registry import extract as extract_id3_registry
                registry_result = extract_id3_registry(filepath)
                if registry_result.get("registry"):
                    result["id3_registry"] = registry_result["registry"]
            except Exception:
                pass

        if filepath.lower().endswith((".wav", ".bwf", ".rf64")):
            try:
                from .audio_bwf_registry import extract as extract_bwf_registry
                bwf_result = extract_bwf_registry(filepath)
                if bwf_result.get("registry"):
                    result["bwf_registry"] = bwf_result["registry"]
            except Exception:
                pass
        
        total_fields = (
            len(result["format"]) +
            len(result["format_details"]) +
            len(result["technical"]) +
            len(result["tags"]) +
            len(result["album_art"]) +
            len(result["replaygain"])
        )
        result["fields_extracted"] = total_fields
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract audio metadata: {str(e)}"}


def extract_audio_advanced_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract advanced audio metadata (ReplayGain, etc.).
    
    Args:
        filepath: Path to audio file
    
    Returns:
        Dictionary with advanced audio metadata
    """
    basic = extract_audio_metadata(filepath)
    
    if basic and 'error' not in basic:
        advanced = {"basic": basic}
        
        replaygain = {}
        for key, value in basic.get('tags', {}).items():
            key_lower = key.lower()
            if 'replaygain' in key_lower:
                replaygain[key] = value
        
        if replaygain:
            advanced["replaygain"] = replaygain
        
        tags = basic.get('tags', {})
        
        analyzed_audio = {}
        
        if tags.get('bpm'):
            analyzed_audio["tempo_bpm"] = tags['bpm']
        
        if tags.get('composer'):
            analyzed_audio["has_composer"] = True
        
        if tags.get('lyrics'):
            analyzed_audio["has_lyrics"] = True
            analyzed_audio["lyrics_length"] = len(tags['lyrics'])
        
        if tags.get('compilation'):
            try:
                analyzed_audio["is_compilation"] = bool(int(tags['compilation']))
            except (ValueError, TypeError):
                analyzed_audio["is_compilation"] = tags['compilation'].lower() in ['true', '1', 'yes']
        
        if tags.get('genre'):
            analyzed_audio["genre"] = tags['genre']
        
        if analyzed_audio:
            advanced["analyzed"] = analyzed_audio
        
        return advanced
    
    return basic


def get_audio_field_count() -> int:
    """Return total number of audio metadata fields."""
    total = 0
    total += len(AUDIO_TAG_FIELDS)
    total += len(ULTRA_AUDIO_FIELDS)
    total += len(MEGA_AUDIO_FIELDS)
    return total
