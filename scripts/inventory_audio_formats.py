#!/usr/bin/env python3
"""Generate audio format-specific field inventories.

This script inventories detailed audio metadata fields that are not exposed
through basic ffprobe but are available in various audio formats:

- APEv2 Tags (Monkey's Audio)
- MP4/iTunes atoms
- WAV/RIFF chunks
- AIFF markers
- Opus header fields
- DSD/DSF fields
- BWF/RF64 broadcast audio
"""

import json
from pathlib import Path
from typing import Dict, List


def get_apev2_tags() -> List[str]:
    """Get APEv2 (Monkey's Audio) tag inventory."""

    tags = [
        # Header
        "MAC", "DURATION", "SAMPLE_RATE", "CHANNELS", "BITS_PER_SAMPLE",
        "SHOULDER_PEAK", "SHOULDER_PEAK_RIGHT", "SHOULDER_PEAK_LEFT",
        "OVERALL_PEAK", "OVERALL_PEAK_RIGHT", "OVERALL_PEAK_LEFT",
        "GAIN_HEADROOM_DB", "GAIN_HEADROOM_DB_RIGHT", "GAIN_HEADROOM_DB_LEFT",
        "OVERALL_BITRATE", "FRAME_FLAGS",

        # Standard APE tags
        "TITLE", "SUBTITLE", "ARTIST", "ALBUM", "ALBUM ARTIST", "TRACK",
        "COMPOSER", "COMMENT", "YEAR", "GENRE", "TRACK NUMBER",
        "DISC NUMBER", "ISRC", "CATALOG NUMBER",
        "COVER ART (FRONT)", "COVER ART (BACK)",

        # ReplayGain
        "REPLAYGAIN_ALBUM_GAIN", "REPLAYGAIN_ALBUM_PEAK", "REPLAYGAIN_TRACK_GAIN",
        "REPLAYGAIN_TRACK_PEAK", "REPLAYGAIN_ALBUM_MIN_MAX",

        # APE specific
        "APE_VERSION", "APE_DESCRIPTION", "APE_FLAGS", "APE_COMPRESSION_LEVEL",
        "APE_HEADER", "APE_FILE",

        # Extended tags
        "MEDIATYPE", "INDEX", "PART", "TOTAL PARTS", "TAGS",
    ]

    return sorted(tags)


def get_mp4_itunes_atoms() -> List[str]:
    """Get MP4/iTunes atom inventory."""

    atoms = [
        # Box structure
        "ftyp", "free", "skip", "wide", "mdat", "moov", "moof", "mfra",

        # Metadata boxes
        "mvhd", "tkhd", "mdhd", "hdlr", "vmhd", "stbl", "stsd", "stts", "stsc",
        "stsz", "stco", "co64", "ctts", "stss", "sdtp", "sbgp",
        "sgpd", "avcC", "btrt", "esds", "avc1", "hev1",

        # iTunes/Apple specific
        "ilst", "meta", "udta", "uuid", "covr",

        # Sample description
        "esds", "avcC", "hev1", "dvcC",

        # Chapter/edition boxes
        "chpl", "edts", "elst", "tref", "cslg",

        # DRM (deprecated)
        "pssh", "sinf",

        # Other
        "pasp", "clap", "colr", "smhd", "gmhd", "mdia", "minf", "dinf", "stbl",
    ]

    return sorted(atoms)


def get_wav_riff_chunks() -> List[str]:
    """Get WAV/RIFF chunk inventory."""

    chunks = [
        # RIFF structure
        "RIFF", "WAVE", "fmt ", "data",

        # Format chunk
        "FormatTag", "Channels", "SamplesPerSec", "AvgBytesPerSec", "BlockAlign",
        "BitsPerSample", "cbSize",

        # Fact chunk
        "SamplesLength",

        # Cue points
        "cue",
        # Playlist
        "plst",

        # Labels
        "labl",

        # Associated data
        "adtl",

        # Broadcast audio extension
        "bext",

        # Cart chunk
        "cart",

        # Display info
        "disp",

        # LIST chunks
        "INFO", "LIST-adtl", "LIST-INFO",

        # Padding
        "pad",

        # MPEXT (MIDI Polyphonic Expression)
        "smpl",

        # Unknown/specific
        "dm", "ds64",
    ]

    return sorted(chunks)


def get_aiff_markers() -> List[str]:
    """Get AIFF marker/instrument chunk inventory."""

    markers = [
        # Form chunk
        "FormType", "NumChannels", "NumSampleFrames", "SampleSize", "SampleRate",
        "CompressionType", "SampleFrames", "Offset", "BlockSize",

        # Common chunk
        "Common", "SampleRate", "NumChannels",

        # Marker chunk
        "Marker", "Offset", "Size", "Text",

        # Instrument chunk
        "InstrumentName", "DataOffset", "DataSize", "LoopMode", "LoopBegin",
        "LoopEnd", "LoopCount", "LoopType", "MIDIUnityNote", "MIDIPitchFraction",

        # Comment chunk
        "Comment", "Timestamp", "Marker",

        # Audio recording chunk
        "Name", "Data", "Annotation",

        # Name chunk (alternative)
        "Author", "Copyright",

        # MIDI chunk
        "NumTimbres", "NumChannels", "Channel1", "Channel2", "Channel3", "Channel4",
    ]

    return sorted(markers)


def get_opus_fields() -> List[str]:
    """Get Opus codec header field inventory."""

    fields = [
        # Identification header
        "OpusHead", "Version", "Channel Count", "Pre-skip", "Input Sample Rate",

        # Comment header
        "OpusTags", "Vendor",

        # Packet configuration
        "Granule Position", "Packet Duration", "Packet Position",

        # Padding
        "Padding",

        # Codec delay
        "Pre-skip Samples", "Encoder Delay",
    ]

    return sorted(fields)


def get_dsd_fields() -> List[str]:
    """Get DSD/DSF field inventory."""

    fields = [
        # DSD chunk
        "ID", "Format Version", "Channel Type", "Channel Num", "Sample Frequency",
        "Bits Per Sample", "Sample Count",

        # DSF chunk
        "Metadata Chunk", "File Size", "File Offset",

        # Compression
        "Compression", "Compression Name", "Compression Value",

        # Padding
        "Padding",

        # ID tags
        "Album", "Title", "Artist",
    ]

    return sorted(fields)


def get_bwf_rf64_fields() -> List[str]:
    """Get BWF/RF64 broadcast audio field inventory."""

    fields = [
        # Basic WAV
        "FormatTag", "Channels", "SamplesPerSec", "AvgBytesPerSec", "BlockAlign",
        "BitsPerSample",

        # Broadcast Wave Format (bext)
        "Description", "Originator", "OriginatorReference", "OriginationDate",
        "OriginationTime", "TimeReference", "BextVersion", "History",
        "Timecode", "SampleRate", "TimecodeLow",
        "Reserved", "CodingHistory", "UMID", "LoudnessValue",
        "LoudnessRange", "MaxTruePeakLevel", "MaxTruePeakLevelPos",
        "MaxMomentaryLoudness", "MaxMomentaryLoudnessPos", "MaxLoudness", "MaxLoudnessPos",
        "MaxShortTermLoudness", "MaxShortTermLoudnessPos", "LoudnessRange",
        "MaxTPM", "MaxTPMPos", "MaxMomentaryTPM", "MaxTPM", "MaxTPMPos",
        "MSSourceType", "MSSource", "MSChannel", "MSMatrixCoefficients",
        "Reserved",

        # RF64
        "RF64", "RF64Data",

        # iXML (Broadcast metadata)
        "iXMLData",
    ]

    return sorted(fields)


def generate_inventory(output_dir: Path) -> None:
    """Generate audio format-specific field inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "generated_at": "",
        "source": "specification",
        "formats": {},
        "totals": {},
    }

    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # APEv2
    ape_tags = get_apev2_tags()
    inventory["formats"]["APEv2"] = {
        "format": "APEv2 (Monkey's Audio)",
        "fields": ape_tags,
        "field_count": len(ape_tags),
    }

    # MP4/iTunes
    mp4_atoms = get_mp4_itunes_atoms()
    inventory["formats"]["MP4_iTunes"] = {
        "format": "MP4/iTunes",
        "fields": mp4_atoms,
        "field_count": len(mp4_atoms),
    }

    # WAV/RIFF
    wav_chunks = get_wav_riff_chunks()
    inventory["formats"]["WAV_RIFF"] = {
        "format": "WAV/RIFF",
        "fields": wav_chunks,
        "field_count": len(wav_chunks),
    }

    # AIFF
    aiff_markers = get_aiff_markers()
    inventory["formats"]["AIFF"] = {
        "format": "AIFF",
        "fields": aiff_markers,
        "field_count": len(aiff_markers),
    }

    # Opus
    opus_fields = get_opus_fields()
    inventory["formats"]["Opus"] = {
        "format": "Opus",
        "fields": opus_fields,
        "field_count": len(opus_fields),
    }

    # DSD
    dsd_fields = get_dsd_fields()
    inventory["formats"]["DSD_DSF"] = {
        "format": "DSD/DSF",
        "fields": dsd_fields,
        "field_count": len(dsd_fields),
    }

    # BWF/RF64
    bwf_fields = get_bwf_rf64_fields()
    inventory["formats"]["BWF_RF64"] = {
        "format": "BWF/RF64",
        "fields": bwf_fields,
        "field_count": len(bwf_fields),
    }

    # Totals
    total_fields = (
        len(ape_tags) + len(mp4_atoms) + len(wav_chunks) +
        len(aiff_markers) + len(opus_fields) + len(dsd_fields) + len(bwf_fields)
    )

    inventory["totals"] = {
        "formats": len(inventory["formats"]),
        "total_fields": total_fields,
    }

    # Write JSON
    output_path = output_dir / "audio_format_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")
    print(f"Total fields: {total_fields}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate audio format-specific field inventory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/audio_format_inventory"),
        help="Output directory (default: dist/audio_format_inventory)",
    )
    args = parser.parse_args()

    generate_inventory(args.out_dir)


if __name__ == "__main__":
    main()
