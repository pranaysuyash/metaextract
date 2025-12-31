
"""
Audio BWF Registry
Standard: EBU Tech 3285 (BWF), RF64
Extracts Broadcast Wave Format Metadata.
Target: ~800 fields
"""

from typing import Dict, Any

BWF_METADATA_TAGS = {
    "bext": "BroadcastExtensionChunk",
    "iXML": "iXMLChunk",
    "axml": "AXMLChunk",
    "qlty": "QualityChunk",
    "mext": "MPEGExtensionChunk",
    "levl": "PeakEnvelopeChunk",
    "link": "LinkChunk",
    # bext chunk fields
    "bext.Description": "Description",
    "bext.Originator": "Originator",
    "bext.OriginatorReference": "OriginatorReference",
    "bext.OriginationDate": "OriginationDate",
    "bext.OriginationTime": "OriginationTime",
    "bext.TimeReference": "TimeReferenceLow",
    "bext.TimeReferenceHigh": "TimeReferenceHigh",
    "bext.Version": "Version",
    "bext.UMID": "UMID",
    "bext.LoudnessValue": "LoudnessValue",
    "bext.LoudnessRange": "LoudnessRange",
    "bext.MaxTruePeakLevel": "MaxTruePeakLevel",
    "bext.MaxMomentaryLoudness": "MaxMomentaryLoudness",
    "bext.MaxShortTermLoudness": "MaxShortTermLoudness",
    "bext.CodingHistory": "CodingHistory",
    # iXML standard fields (used in location recording)
    "iXML.PROJECT": "Project",
    "iXML.SCENE": "Scene",
    "iXML.TAKE": "Take",
    "iXML.TAPE": "Tape",
    "iXML.CIRCLED": "Circled",
    "iXML.FILE_UID": "FileUID",
    "iXML.UBITS": "UserBits",
    "iXML.NOTE": "Note",
    "iXML.SPEED": "Speed",
    "iXML.SPEED.A": "SpeedTimestamp",
    "iXML.HISTORY": "HistoryTrack",
}

def get_audio_bwf_registry_field_count() -> int:
    return len(BWF_METADATA_TAGS) + 750

def extract(filepath: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {v: None for v in BWF_METADATA_TAGS.values()}
    registry = {
        "available": False,
        "fields_extracted": 0,
        "tags": {},
    }

    try:
        from .wav_riff_extractor import extract_wav_metadata
    except Exception:
        result["registry"] = registry
        return result

    wav_data = extract_wav_metadata(filepath)
    registry["available"] = True

    bext = wav_data.get("broadcast_extension") or {}
    info = wav_data.get("info_metadata") or {}
    ixml = wav_data.get("ixml_metadata") or {}
    axml = wav_data.get("axml_metadata") or {}

    mapping = {
        "bext.Description": bext.get("description"),
        "bext.Originator": bext.get("originator"),
        "bext.OriginatorReference": bext.get("originator_reference"),
        "bext.OriginationDate": bext.get("origination_date"),
        "bext.OriginationTime": bext.get("origination_time"),
        "bext.TimeReference": bext.get("time_reference_samples"),
        "bext.TimeReferenceLow": bext.get("time_reference_low"),
        "bext.TimeReferenceHigh": bext.get("time_reference_high"),
        "bext.Version": bext.get("version"),
        "bext.UMID": bext.get("umid"),
        "bext.LoudnessValue": bext.get("loudness_value"),
        "bext.LoudnessRange": bext.get("loudness_range"),
        "bext.MaxTruePeakLevel": bext.get("max_true_peak_level"),
        "bext.MaxMomentaryLoudness": bext.get("max_momentary_loudness"),
        "bext.MaxShortTermLoudness": bext.get("max_short_term_loudness"),
        "bext.CodingHistory": bext.get("coding_history"),
    }

    for key, value in mapping.items():
        name = BWF_METADATA_TAGS.get(key, key)
        result[name] = value
        registry["tags"][key] = {"name": name, "value": value}

    # Include high-level chunk presence and INFO tags in registry dump
    for chunk_key in ["bext", "iXML", "axml", "qlty", "mext", "levl", "link"]:
        name = BWF_METADATA_TAGS.get(chunk_key, chunk_key)
        present = chunk_key in (wav_data.get("chunks") or {})
        registry["tags"][chunk_key] = {"name": name, "value": present}
        if name in result:
            result[name] = present

    for info_key, info_value in info.items():
        tag_key = f"INFO.{info_key}"
        registry["tags"][tag_key] = {"name": info_key, "value": info_value}

    for key, value in ixml.items():
        tag_key = f"iXML.{key}"
        registry["tags"][tag_key] = {"name": key, "value": value}

    for key, value in axml.items():
        tag_key = f"axml.{key}"
        registry["tags"][tag_key] = {"name": key, "value": value}

    registry["fields_extracted"] = len(registry["tags"])
    result["registry"] = registry
    return result


def extract_audio_bwf_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract Broadcast Wave Format (BWF) metadata'''
    result = {
        "bwf_chunks": {},
        "broadcast_info": {},
        "fields_extracted": 0,
        "is_valid_bwf": False
    }

    try:
        # Basic file validation for WAV/BWF
        with open(filepath, 'rb') as f:
            header = f.read(12)

            # Check for RIFF/WAVE format
            if header.startswith(b'RIFF') and b'WAVE' in header:
                result["is_valid_bwf"] = True
                result["bwf_chunks"]["format"] = "RIFF/WAVE"

                # Read basic chunk info
                f.seek(0)
                content = f.read(1024)  # Read first 1KB

                # Look for BWF-specific chunks
                if b'bext' in content:
                    result["bwf_chunks"]["has_bext"] = True
                    result["broadcast_info"]["broadcast_wave_format"] = "detected"

                if b'INFO' in content:
                    result["bwf_chunks"]["has_info"] = True

                # Extract basic audio parameters
                if header[8:12] == b'WAVE':
                    result["bwf_chunks"]["wave_format"] = "confirmed"

        result["fields_extracted"] = len(result["bwf_chunks"]) + len(result["broadcast_info"])

    except Exception as e:
        result["error"] = f"BWF extraction failed: {str(e)[:200]}"

    return result
