#!/usr/bin/env python3
"""BWF/RF64 Metadata Fields Inventory

Broadcast Wave Format (BWF) is a standardized file format for audio files
based on the WAV format, with additional metadata for broadcasting.
RF64 is an extension of WAV/BWF that supports files larger than 4GB.

Reference:
- EBU Tech 3285 (BWF Specification)
- EBU Tech 3306 (RF64 Specification)
- ITU-R BS.2088
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


BWF_RF64_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "EBU Tech 3285, ITU-R BS.2088",
    "description": "Broadcast Wave Format and RF64 metadata fields",
    "format": "BWF/RF64",
    "categories": {
        "bext_broadcast_extension": {
            "description": "BWF bext chunk (Broadcast Extension) - Core specification",
            "fields": [
                "Description",  # 256 bytes - Description of the sound recording
                "Originator",  # 32 bytes - Name of the originator
                "OriginatorReference",  # 32 bytes - Reference assigned by originator
                "OriginationDate",  # 10 bytes - Date of creation (YYYY-MM-DD)
                "OriginationTime",  # 8 bytes - Time of creation (HH:MM:SS)
                "TimeReference",  # 8 bytes - First sample count since midnight
                "Version",  # 2 bytes - Version of BWF (0-65535)
                "UMID",  # 64 bytes - Unique Material Identifier
                "LoudnessValue",  # 2 bytes - Integrated loudness (LUFS * 100)
                "LoudnessRange",  # 2 bytes - Loudness range (LU * 100)
                "MaxTruePeakLevel",  # 2 bytes - Maximum true peak level (dBTP)
                "MaxMomentaryLoudness",  # 2 bytes - Maximum momentary loudness (LUFS)
                "MaxShortTermLoudness",  # 2 bytes - Maximum short-term loudness (LUFS)
                "Reserved",  # 180 bytes - Reserved for future use
                "CodingHistory",  # Variable - Coding history string
            ],
            "count": 15,
            "reference": "EBU Tech 3285-v1.0"
        },
        "bext_coding_history_enhanced": {
            "description": "Enhanced BWF coding history format",
            "fields": [
                "CodingAlgorithm",  # Audio coding algorithm
                "NumberChannels",  # Number of channels coded
                "SamplingFrequency",  # Sampling frequency in Hz
                "BitDepth",  # Bit depth
                "FrameLength",  # Frame length in samples
                "AudioCoding",  # Audio coding description
                "BitRate",  # Bit rate in kbps
                "PacketLength",  # Packet length in ms
                "Quality",  # Quality indicator
                "Mode",  # Coding mode
                "Emphasis",  # Emphasis
                "BitRateReduction",  # Bit rate reduction method
            ],
            "count": 12,
            "reference": "EBU Tech 3285 Annex D"
        },
        "levl_level_ride": {
            "description": "BWF levl chunk (Level Ride) - Per-channel levels",
            "fields": [
                "PeakEnvelopeVersion",  # Version of peak envelope format
                "LookupFlag",  # Lookup table flag
                "LevelType",  # Type of level measurement
                "PeakEnvelopeStartPosition",  # Start position of peak envelope
                "PeakEnvelopeBlockSize",  # Block size for peak values
                "PeakEnvelopePointsPerValue",  # Points per value
                "PeakEnvelopeTimeStamp",  # Time stamp of peak envelope
                "PeakValue",  # Peak value per channel
                "PeakRatio",  # Peak ratio per channel
                "PeakLevel",  # Peak level per channel
            ],
            "count": 10,
            "reference": "EBU Tech 3285-v1.0 Annex E"
        },
        "link_related_text": {
            "description": "BWF link chunk - Related text information",
            "fields": [
                "LinkedChunkType",  # Type of linked chunk
                "LinkedChunkID",  # ID of linked chunk
                "LinkedChunkDescription",  # Description of linked data
                "LinkedChunkLanguage",  # Language of linked content
                "LinkedChunkURL",  # URL to linked content
            ],
            "count": 5,
            "reference": "EBU Tech 3285-v1.0"
        },
        "axml_associated_xml": {
            "description": "BWF axml chunk - Associated XML data",
            "fields": [
                "XMLContentType",  # Type of XML content
                "XMLContentEncoding",  # Encoding of XML content
                "XMLContent",  # XML content data
                "XMLSchemaLocation",  # Location of XML schema
                "XMLNamespace",  # XML namespace
            ],
            "count": 5,
            "reference": "EBU Tech 3285-v1.0"
        },
        "umid_unique_material": {
            "description": "BWF umid chunk - Unique Material Identifier",
            "fields": [
                "UMIDLength",  # Length of UMID
                "UMIDVersion",  # Version of UMID format
                "UMIDInstance",  # Instance number
                "UMIDMaterialNumber",  # Material number (128-bit UUID)
                "UMIDSourcePackage",  # Source package number
                "UMIDSourceIdentifier",  # Source identifier
                "UMIDTimeStamp",  # Time stamp of UMID
            ],
            "count": 7,
            "reference": "SMPTE ST 330 / ITU-R BS.2088"
        },
        "ds64_data_size_64": {
            "description": "RF64 ds64 chunk - 64-bit data size information",
            "fields": [
                "FileSize64",  # Total file size (64-bit)
                "DataSize64",  # Size of data chunk (64-bit)
                "SampleCount64",  # Sample count (64-bit)
                "TableLength",  # Length of size table
                "ChunkIDList",  # List of chunk IDs > 4GB
                "ChunkSizeList",  # List of chunk sizes > 4GB
            ],
            "count": 6,
            "reference": "EBU Tech 3306"
        },
        "r64_64bit_riff": {
            "description": "RF64 r64 chunk - 64-bit RIFF reference",
            "fields": [
                "RF64Version",  # Version of RF64 format
                "RF64Flags",  # RF64 flags
                "RF64Originator",  # Name of software creating RF64
                "RF64DateTime",  # Date and time of creation
            ],
            "count": 4,
            "reference": "EBU Tech 3306"
        },
        "fmt_wave_format": {
            "description": "Extended wave format fields for BWF",
            "fields": [
                "AudioFormat",  # Audio format (1=PCM, 3=Float, etc.)
                "NumChannels",  # Number of audio channels
                "SampleRate",  # Sample rate in Hz
                "ByteRate",  # Bytes per second
                "BlockAlign",  # Block alignment
                "BitsPerSample",  # Bits per sample
                "FormatTag",  # Format tag
                "ExtensionSize",  # Size of format extension
                "ValidBitsPerSample",  # Valid bits (if different from above)
                "ChannelMask",  # Speaker positioning mask
                "SubFormat",  # GUID for format
                "Waveformatex",  # Extended format structure
            ],
            "count": 12,
            "reference": "EBU Tech 3285"
        },
        "cart_advanced_rewind": {
            "description": "BWF cart chunk - Cart timer for broadcasting",
            "fields": [
                "CartTitle",  # 256 bytes - Title of cart
                "Artist",  # 256 bytes - Artist/creator name
                "CutID",  # 64 bytes - Cut number/ID
                "ClientID",  # 64 bytes - Client ID
                "Category",  # 256 bytes - Category code
                "Classification",  # 256 bytes - Classification
                "Keywords",  # 1024 bytes - Keywords/tags
                "ContentDescription",  # 4096 bytes - Description
                "Originator",  # 256 bytes - Originator name
                "OriginatorReference",  # 256 bytes - Reference
                "OriginationDate",  # 10 bytes - YYYY-MM-DD
                "OriginationTime",  # 8 bytes - HH:MM:SS
                "StartDate",  # 10 bytes - Earliest play date
                "StartTime",  # 8 bytes - Earliest play time
                "EndDate",  # 10 bytes - Latest play date
                "EndTime",  # 8 bytes - Latest play time
                "ProducerAppID",  # 64 bytes - Producer app ID
                "ProducerAppVersion",  # 64 bytes - Producer app version
                "UserDefinedText",  # 1024 bytes - User text
                "DefaultDuration",  # 4 bytes - Default duration in 10ms units
                "TimeStructure",  # 4 bytes - Time structure marker
                "Filesize",  # 4 bytes - File size in 2GB units
                "BlockStart",  # 4 bytes - Block start position
                "BlockEnd",  # 4 bytes - Block end position
                "SampleRate",  # 4 bytes - Sample rate
                "SampleCount",  # 8 bytes - Sample count
                "PojectStart",  # 4 bytes - Project start time
                "ProjectDuration",  # 4 bytes - Project duration
                "ProjectName",  # 64 bytes - Project name
                "NOTE",  # 256 bytes - Note
            ],
            "count": 29,
            "reference": "EBU Tech 3285-v1.0 / AES46"
        },
        "junk_padding": {
            "description": "Junk/Padding chunk variations",
            "fields": [
                "JunkAlignment",  # Padding alignment
                "JunkReserved",  # Reserved bytes
                "JunkData",  # Junk data content
            ],
            "count": 3,
            "reference": "Standard RIFF"
        },
        "wsmp_wavesample": {
            "description": "BWF wsmp chunk - Wave sample information",
            "fields": [
                "SampleLoopCount",  # Number of sample loops
                "SampleLoopType",  # Type of loop (forward, ping-pong, etc.)
                "SampleLoopStart",  # Start position of loop
                "SampleLoopEnd",  # End position of loop
                "SampleLoopFraction",  # Loop fraction
                "SampleLoopRepeatCount",  # Repeat count (0=infinite)
            ],
            "count": 6,
            "reference": "Microsoft Wave Sample Chunk"
        },
        "inst_instrument": {
            "description": "Instrument parameters chunk",
            "fields": [
                "BaseNote",  # Base MIDI note
                "Detune",  # Detune in cents
                "Gain",  # Gain in dB
                "LowNote",  # Low MIDI note range
                "HighNote",  # High MIDI note range
                "LowVelocity",  # Low velocity range
                "HighVelocity",  # High velocity range
            ],
            "count": 7,
            "reference": "Standard RIFF Instrument"
        },
        "fact_fact": {
            "description": "Fact chunk for compressed audio",
            "fields": [
                "SampleCount",  # Total number of samples
                "SampleCountHigh",  # High 32 bits of sample count
                "SampleCountLow",  # Low 32 bits of sample count
                "PacketSize",  # Packet size
                "PacketCount",  # Number of packets
                "DataPadding",  # Padding bytes
                "QualityIndicator",  # Quality indicator
            ],
            "count": 7,
            "reference": "Standard RIFF"
        },
        "list_info": {
            "description": "LIST INFO chunk metadata fields",
            "fields": [
                "Title",  # Title of the work
                "Artist",  # Name of the artist/creator
                "Album",  # Name of the album
                "TrackNumber",  # Track number
                "Genre",  # Genre
                "Comment",  # Comment/description
                "Date",  # Date of creation
                "Copyright",  # Copyright notice
                "Software",  # Software used
                "Engineer",  # Name of engineer
                "Genre",  # Genre
                "Product",  # Product name
                "Subject",  # Subject
                "Creator",  # Creator/author
                "Source",  # Source
                "Software",  # Software
                "Custom1",  # Custom field 1
                "Custom2",  # Custom field 2
                "Custom3",  # Custom field 3
                "Custom4",  # Custom field 4
                "Custom5",  # Custom field 5
            ],
            "count": 21,
            "reference": "RIFF INFO specification"
        },
        "cue_cue_points": {
            "description": "Cue points chunk",
            "fields": [
                "CuePointID",  # Unique ID for cue point
                "CuePointPosition",  # Position in samples
                "CuePointChunkID",  # Chunk containing cue point
                "CuePointChunkStart",  # Start of chunk
                "CuePointBlockStart",  # Block start
                "CuePointSampleOffset",  # Sample offset
            ],
            "count": 6,
            "reference": "Standard RIFF Cue Chunk"
        },
        "smpl_sample": {
            "description": "Sample chunk for sample-based audio",
            "fields": [
                "ManufacturerID",  # Manufacturer ID (0-127)
                "ProductID",  # Product ID
                "SamplePeriod",  # Sample period in nanoseconds
                "MIDIUnityNote",  # MIDI unity note
                "MIDIPitchFraction",  # MIDI pitch fraction
                "SMPTEFormat",  # SMPTE format (24/25/29.97/30)
                "SMPTEOffset",  # SMPTE offset
                "SampleLoopCount",  # Number of loops
                "SampleLoopData",  # Loop data
            ],
            "count": 9,
            "reference": "Standard RIFF Sample Chunk"
        },
        "metadata_enhanced": {
            "description": "Enhanced BWF metadata fields",
            "fields": [
                "EncryptionMethod",  # Encryption method
                "EncryptionKeyID",  # Key identifier
                "CryptographicContext",  # Cryptographic context
                "AuthenticationType",  # Type of authentication
                "AuthenticationData",  # Authentication data
                "CodingHistoryErrors",  # Errors in coding history
                "CodingHistoryQuality",  # Quality indicators
                "CodingHistoryLocation",  # Recording location
                "CodingHistoryOperator",  # Operator name
                "CodingHistoryHardware",  # Hardware info
            ],
            "count": 10,
            "reference": "EBU Tech 3285-v1.0 Annex C"
        },
        "timing_reference": {
            "description": "Timing and synchronization fields",
            "fields": [
                "SMPTE_TimeCode",  # SMPTE time code
                "SMPTE_FrameRate",  # SMPTE frame rate
                "SMPTE_DropFrame",  # Drop frame indicator
                "SampleTimeStamp",  # Sample-level timestamp
                "SampleRate",  # Actual sample rate
                "FrameCount",  # Frame count
                "TimeCodeString",  # Formatted TC string
            ],
            "count": 7,
            "reference": "ITU-R BS.2088"
        }
    },
    "totals": {
        "categories": 20,
        "total_fields": 210
    }
}


def main():
    output_dir = Path("dist/bwf_rf64_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "bwf_rf64_inventory.json"
    output_file.write_text(json.dumps(BWF_RF64_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary = {
        "generated_at": BWF_RF64_INVENTORY["generated_at"],
        "source": BWF_RF64_INVENTORY["source"],
        "format": BWF_RF64_INVENTORY["format"],
        "categories": BWF_RF64_INVENTORY["totals"]["categories"],
        "total_fields": BWF_RF64_INVENTORY["totals"]["total_fields"],
        "field_counts_by_category": {}
    }
    
    for cat, data in BWF_RF64_INVENTORY["categories"].items():
        summary["field_counts_by_category"][cat] = {
            "description": data["description"],
            "count": data["count"],
            "reference": data.get("reference", "N/A")
        }
    
    summary_file = output_dir / "bwf_rf64_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("BWF/RF64 METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {BWF_RF64_INVENTORY['generated_at']}")
    print(f"Format: {BWF_RF64_INVENTORY['format']}")
    print(f"Categories: {BWF_RF64_INVENTORY['totals']['categories']}")
    print(f"Total Fields: {BWF_RF64_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(BWF_RF64_INVENTORY["categories"].items(), key=lambda x: x[1]["count"], reverse=True):
        ref = data.get("reference", "")
        print(f"  {cat:35s}: {data['count']:>3}  [{ref[:30]}]")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
