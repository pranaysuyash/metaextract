
"""
Audio ID3 Complete Registry
Standard: ID3v2.3, ID3v2.4
Extracts Complete ID3 Frames including Private and Experimental.
Target: ~1,500 fields
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

ID3_FRAME_REGISTRY = {
    # Text Information
    "TIT1": "ContentGroupDescription", "TIT2": "Title", "TIT3": "Subtitle",
    "TALB": "Album", "TOAL": "OriginalAlbum", "TRCK": "TrackNumber",
    "TPOS": "PartNumber", "TSST": "SetSubtitle", "TSRC": "ISRC",
    # People
    "TPE1": "LeadArtist", "TPE2": "Band", "TPE3": "Conductor", "TPE4": "Remixer",
    "TOPE": "OriginalArtist", "TEXT": "Lyricist", "TOLY": "Lyricist",
    "TCOM": "Composer", "TMCL": "MusicianCredits", "TIPL": "InvolvedPeople",
    "TENC": "EncodedBy",
    # Dates
    "TYER": "Year", "TDAT": "Date", "TIME": "Time", "TORY": "OriginalReleaseYear",
    "TRDA": "RecordingDates", "TDOR": "OriginalReleaseTime", "TDRC": "RecordingTime",
    "TDRL": "ReleaseTime", "TDTG": "TaggingTime",
    # Abstract & Links
    "WOAF": "OfficialAudioFileWebpage", "WOAR": "OfficialArtistWebpage",
    "WOAS": "OfficialAudioSourceWebpage", "WORS": "OfficialInternetRadioStationWebpage",
    "WPAY": "PaymentWebpage", "WPUB": "PublishersOfficialWebpage",
    # Images & Objects
    "APIC": "AttachedPicture", "PIC": "Picture",
    "GEOB": "GeneralEncapsulatedObject",
    # Lyrics & Text
    "USLT": "UnsynchronizedLyrics", "SYLT": "SynchronizedLyrics",
    "COMM": "Comments", "USER": "TermsOfUse",
    # Technical
    "MCDI": "MusicCDIdentifier", "ETCO": "EventTimingCodes",
    "MLLT": "MPEGLocationLookupTable", "SYTC": "SynchronizedTempoCodes",
    "RVA2": "RelativeVolumeAdjustment2", "EQU2": "Equalization2",
    "RVRB": "Reverb", "ENCR": "EncryptionMethodRegistration",
    "GRID": "GroupIdentificationRegistration", "PRIV": "PrivateFrame",
    "SIGN": "Signature", "SEEK": "SeekFrame", "ASPI": "AudioSeekPointIndex",
    # Podcast & Sorting
    "PCST": "Podcast", "TCAT": "PodcastCategory", "TDES": "PodcastDescription",
    "TGID": "PodcastGlobalUniqueID", "TKWD": "PodcastKeywords",
    "TSOT": "TitleSortOrder", "TSOA": "AlbumSortOrder", "TSOP": "PerformerSortOrder",
    "TSOC": "ComposerSortOrder",
}

try:
    from .id3_frames_complete import (
        ID3V2_TEXT_FRAMES,
        ID3V2_URL_FRAMES,
        ID3V2_OTHER_FRAMES,
        AUDIO_STREAMING_TAGS,
        get_all_audio_extension_tags,
        VORBIS_COMMENT_FIELDS,
        APE_TAG_FIELDS,
        MP4_TAG_FIELDS,
    )

    extra_frames = {**ID3V2_TEXT_FRAMES, **ID3V2_URL_FRAMES, **ID3V2_OTHER_FRAMES}
    for frame_id, name in extra_frames.items():
        ID3_FRAME_REGISTRY.setdefault(frame_id, name)
    AUDIO_EXTENSION_TAGS = get_all_audio_extension_tags()
    for frame_id, name in AUDIO_EXTENSION_TAGS.items():
        ID3_FRAME_REGISTRY.setdefault(frame_id, name)
except Exception:
    AUDIO_STREAMING_TAGS = {}
    AUDIO_EXTENSION_TAGS = {}
    VORBIS_COMMENT_FIELDS = {}
    APE_TAG_FIELDS = {}
    MP4_TAG_FIELDS = {}

def get_audio_id3_complete_registry_field_count() -> int:
    return (
        len(ID3_FRAME_REGISTRY) +
        len(VORBIS_COMMENT_FIELDS) +
        len(APE_TAG_FIELDS) +
        len(MP4_TAG_FIELDS)
    )

def extract(filepath: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {v: None for v in ID3_FRAME_REGISTRY.values()}
    registry = {
        "available": False,
        "fields_extracted": 0,
        "tags": {},
        "unknown_tags": {},
    }

    try:
        from mutagen.id3 import ID3, ID3NoHeaderError
        from mutagen import File as MutagenFile
    except Exception:
        result["registry"] = registry
        return result

    def _frame_value(frame) -> Any:
        if hasattr(frame, "text"):
            if len(frame.text) == 1:
                return frame.text[0]
            return list(frame.text)
        if hasattr(frame, "url"):
            return frame.url
        if frame.FrameID == "APIC":
            return {
                "mime": getattr(frame, "mime", None),
                "type": getattr(frame, "type", None),
                "description": getattr(frame, "desc", None),
                "size_bytes": len(getattr(frame, "data", b"") or b""),
            }
        if frame.FrameID == "COMM":
            return {
                "lang": getattr(frame, "lang", None),
                "description": getattr(frame, "desc", None),
                "text": list(getattr(frame, "text", []) or []),
            }
        if frame.FrameID == "USLT":
            return {
                "lang": getattr(frame, "lang", None),
                "description": getattr(frame, "desc", None),
                "text": getattr(frame, "text", None),
            }
        if frame.FrameID == "PRIV":
            return {
                "owner": getattr(frame, "owner", None),
                "size_bytes": len(getattr(frame, "data", b"") or b""),
            }
        if frame.FrameID == "GEOB":
            return {
                "mime": getattr(frame, "mime", None),
                "filename": getattr(frame, "filename", None),
                "description": getattr(frame, "desc", None),
                "size_bytes": len(getattr(frame, "data", b"") or b""),
            }
        return str(frame)

    registry["available"] = True

    try:
        tags = ID3(filepath)
    except ID3NoHeaderError:
        tags = None
    except Exception:
        tags = None

    if tags is not None:
        for frame_id in tags.keys():
            frames = tags.getall(frame_id)
            values = [_frame_value(frame) for frame in frames]
            value: Any = values[0] if len(values) == 1 else values
            name = ID3_FRAME_REGISTRY.get(frame_id, frame_id)
            entry = {"name": name, "value": value}
            registry["tags"][frame_id] = entry
            if frame_id not in ID3_FRAME_REGISTRY:
                registry["unknown_tags"][frame_id] = entry
            if name in result:
                result[name] = value
            if frame_id == "TXXX":
                for frame in frames:
                    desc = getattr(frame, "desc", None)
                    if not desc:
                        continue
                    extended_id = f"TXXX:{desc}"
                    extended_name = AUDIO_EXTENSION_TAGS.get(extended_id, desc)
                    extended_value = _frame_value(frame)
                    registry["tags"][extended_id] = {
                        "name": extended_name,
                        "value": extended_value,
                    }
                    if extended_name in result:
                        result[extended_name] = extended_value

    try:
        audio = MutagenFile(filepath)
    except Exception:
        audio = None

    if audio is not None and getattr(audio, "tags", None):
        ext = Path(filepath).suffix.lower()
        if ext in {".flac", ".ogg", ".oga", ".opus"}:
            mapping = VORBIS_COMMENT_FIELDS
            prefix = "vorbis"
        elif ext in {".ape"}:
            mapping = APE_TAG_FIELDS
            prefix = "ape"
        elif ext in {".m4a", ".m4b", ".m4p", ".mp4"}:
            mapping = MP4_TAG_FIELDS
            prefix = "mp4"
        else:
            mapping = {}
            prefix = "tags"
        try:
            for raw_key, raw_value in audio.tags.items():
                if isinstance(raw_value, list):
                    value = [str(v) for v in raw_value]
                else:
                    value = str(raw_value)
                lookup_key = raw_key.upper() if mapping is VORBIS_COMMENT_FIELDS else raw_key
                mapped_name = mapping.get(lookup_key)
                entry_key = f"{prefix}:{raw_key}"
                entry = {"name": mapped_name or raw_key, "value": value}
                registry["tags"][entry_key] = entry
                if mapped_name:
                    result[mapped_name] = value
                else:
                    registry["unknown_tags"][entry_key] = entry
        except Exception:
            pass

    registry["fields_extracted"] = len(registry["tags"])
    result["registry"] = registry
    return result
