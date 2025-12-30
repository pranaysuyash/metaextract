#!/usr/bin/env python3
"""APEv2 (Monkey's Audio) tag extraction.

This module parses APEv2 tags from audio files and extracts
detailed metadata that is not exposed through standard tools.

APEv2 supports:
- Header fields (MAC, DURATION, SAMPLE_RATE, CHANNELS)
- Standard tags (TITLE, ARTIST, ALBUM, etc.)
- Binary tags
- Item lists

Reference: http://www.monkeysaudio.com/ape.html
"""

import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# APEv2 header structure
APE_HEADER = b"APETAGEX"
APE_HEADER_FOOTER = b"APETAGEX200"
APE_VERSION_2_0 = 2000
APE_TAG_VERSION_1_0 = 1000


# Standard APEv2 tag types
APE_TAGS = {
    "Title": str,
    "Subtitle": str,
    "Artist": str,
    "Album": str,
    "Publisher": str,
    "Conductor": str,
    "Track": str,
    "Genre": str,
    "Year": str,
    "Copyright": str,
    "PublicationRight": str,
    "AlbumArtist": str,
    "TrackNumber": str,
    "RecordLocation": str,
    "ISRC": str,
    "EAN/UPC": str,
    "CatalogNumber": str,
    "Media": str,
    "Index": str,
    "Lyrics": str,
    "Mood": str,
    "Rating": str,
    "CoverArt (Front)": str,
    "CoverArt (Back)": str,
    "CoverArt (File)": str,
    "CoverArt (URL)": str,
    "BPM": str,
    "BPM (Q&A)": str,
    "CopyrightURL": str,
    "Abstract": str,
    "Language": str,
    "PlayCounter": str,

    # Binary fields
    "Binary": bytes,
    "Binary (LE)": bytes,
}


def read_ape_header(filepath: Path) -> Optional[Dict[str, Any]]:
    """Read and parse APEv2 header."""

    try:
        with open(filepath, "rb") as f:
            header = f.read(32)

            if not header.startswith(APE_HEADER):
                return None

            version = struct.unpack("<I", header[12:16])[0]
            tag_count = struct.unpack("<I", header[16:20])[0]
            flags = struct.unpack("<I", header[20:24])[0]

            return {
                "format": "APEv2",
                "version": version,
                "tag_count": tag_count,
                "flags": flags,
                "header_size": 32,
            }

    except Exception as e:
        return {"error": str(e)}


def parse_ape_tags(filepath: Path) -> Dict[str, Any]:
    """Parse APEv2 tags from file.

    This is a simplified parser that reads the tag items and extracts
    supported field values. A full parser would handle item lists,
    binary data, and all tag types.
    """

    result = {
        "format": "APEv2",
        "tags": {},
        "items": [],
        "errors": [],
    }

    try:
        with open(filepath, "rb") as f:
            header = f.read(32)

            if not header.startswith(APE_HEADER):
                result["errors"].append("Not an APEv2 file")
                return result

            version = struct.unpack("<I", header[12:16])[0]
            tag_count = struct.unpack("<I", header[16:20])[0]
            flags = struct.unpack("<I", header[20:24])[0]
            footer = struct.unpack("<I", header[28:32])[0]

            if footer != APE_HEADER_FOOTER and footer != APE_VERSION_2_0:
                result["errors"].append("Invalid APEv2 footer")
                return result

            # Skip to start of tags
            f.seek(32)

            # Parse tag items (simplified - skip binary tags for now)
            for _ in range(min(tag_count, 1000)):  # Limit to prevent infinite loops
                item_header = f.read(4)
                if len(item_header) < 4:
                    break

                size = struct.unpack("<I", item_header)[0]

                # Skip to tag name (null-terminated string)
                tag_name = []
                while True:
                    char_byte = f.read(1)
                    if char_byte == 0:
                        break
                    tag_name.append(char_byte.decode("latin-1"))
                    if len(tag_name) > 255:
                        tag_name = "".join(tag_name[:255])
                        result["errors"].append(f"Tag name too long at offset {f.tell()}")
                        break

                if not tag_name:
                    break

                tag_name_str = "".join(tag_name)

                # Determine tag type and parse value
                # APE tag values are encoded, but for now we'll just store the tag name
                tag_type = "unknown"

                if size > 0:
                    tag_type = "binary"
                    # Skip binary data
                    f.seek(size - 1)
                else:
                    tag_type = "text"
                    # Text values are stored as UTF-8
                    # This is where we'd parse the actual value
                    f.seek(0)

                result["tags"][tag_name_str] = {
                    "type": tag_type,
                    "size": size,
                }

                result["items"].append({
                    "name": tag_name_str,
                    "type": tag_type,
                })

            f.close()

    except Exception as e:
        result["errors"].append(str(e))

    return result


def extract_apev2_metadata(filepath: str) -> Dict[str, Any]:
    """Extract APEv2 metadata from audio file."""

    path = Path(filepath)
    if not path.exists():
        return {"error": "File not found", "file": filepath}

    hdr = read_ape_header(path)
    result = {
        "file": filepath,
        "format": "APEv2",
        "header": hdr,
        "tags": parse_ape_tags(path),
    }

    if hdr and isinstance(hdr, dict) and "error" in hdr:
        result["error"] = hdr["error"]
        return result

    return result


def get_apev2_field_count() -> int:
    """Get the number of APEv2 fields we support."""

    # Count standard text tags
    text_tags = [k for k, v in APE_TAGS.items() if v is str]
    return len(text_tags)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_apev2_metadata(filepath)

        print("=" * 60)
        print("APEv2 EXTRACTION TEST")
        print("=" * 60)
        print()
        print(f"File: {result.get('file')}")
        print()

        if header and isinstance(header, dict):
            hdr = header
            print(f"Header: Version {hdr.get('version')}, Tags: {hdr.get('tag_count')}, Flags: {hdr.get('flags')}")
            print()

        tags = result.get("tags", {})
        if tags and isinstance(tags, dict):
            print(f"Tags found: {len(tags)}")
            print()

            for name, value in list(tags.items())[:20]:
                print(f"  {name}: {value['type']} (size: {value['size']})")

        errors = result.get("errors", [])
        if errors:
            print(f"Errors: {errors}")

        print()
        print(f"Total fields supported: {get_apev2_field_count()}")
    else:
        print("Usage: python3 apev2_extractor.py <audio.ape>")
        sys.exit(1)
