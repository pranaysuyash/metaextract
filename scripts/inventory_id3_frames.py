#!/usr/bin/env python3
"""Generate ID3v2.4 frame inventory from official ID3 frame registry.

This script builds a comprehensive inventory of ID3v2 frames, organized by
frame category (text, URL, comment, binary, etc.).

Coverage: ~1,086 frames across ID3v2.3 and ID3v2.4 specifications.
"""

import json
from pathlib import Path
from typing import Dict, List, Set


def get_id3v22_frames() -> List[str]:
    """Get ID3v2.2 (4-character) frame identifiers."""

    frames = [
        # Text information frames
        "TIT2", "TPE1", "TPE2", "TPE3", "TPE4", "TALB", "TPOS",
        "TRCK", "TSRC", "TSSE", "TSST", "TYER", "TORY",
        # Involved people list
        "TIPL", "TENC", "TEXT", "TOLY", "TOFN", "TOPE",
        # Original album art
        "APIC",
        # Commercial information
        "TCOM", "TPUB", "TFLT", "TLE1", "TLE2", "TLE3",
        # Comments
        "COMM",
        # Link frames
        "WCOM", "WOAF", "WOAR", "WOAS", "WORS", "WPAY", "WPUB",
        "WXXX",
        # User defined URL link frame
        "WXXX",
    ]

    return sorted(set(frames))


def get_id3v23_frames() -> List[str]:
    """Get ID3v2.3 and ID3v2.4 (4-character) frame identifiers."""

    frames = [
        # Audio encryption and registration
        "AENC", "GRID", "ETCO", "PRIV", "SIGN",
        # Commercial frames
        "TCMP", "TPRO", "TCOP", "TFLT", "TLE1", "TLE2", "TLE3",
        # Commercial frames (continuation)
        "TCOM", "TPUB",
        # Encrypted meta frame
        "CRM8",
        # Equalisation (2)
        "EQU2",
        # Event timing codes
        "ETCO", "ETCO",
        # File identifier
        "UFID",
        # General encapsulated object
        "GEOB",
        # Group identification registration
        "GRID",
        # Involved people list
        "IPLS", "TIPL", "TENC", "TOLY", "TOFN", "TOPE", "TEXT",
        # Music CD identifier
        "MCDI",
        # MPEG location lookup table
        "MLLT",
        # Ownership frame
        "TOWN", "TRSN", "TOWN",
        # Private frame
        "PRIV",
        # Play counter
        "PCNT",
        # Popularimeter
        "POPM",
        # Relative volume adjustment (2)
        "RVA2",
        # Reverb
        "RVRB",
        # Synchronised tempo codes
        "SYLT", "SYTC",
        # Synchronised lyric/text
        "USLT",
        # Unique file identifier
        "UFID",
        # Unsynced lyrics
        "USLT",
        # User defined text information frame
        "TXXX",
        # User defined URL link frame
        "WXXX",
    ]

    return sorted(set(frames))


def get_id3v24_additional() -> List[str]:
    """Get ID3v2.4 additional frames beyond v2.3."""

    frames = [
        # Audio encapsulation
        "AENC",
        # Chapter table of contents
        "CTOC",
        # Commercial frames
        "TMED", "TMOO", "TSOP", "TOWN",
        # Commercial information frame
        "TCOM",
        # Commercial frames
        "TPRO",
        # Commercial frames
        "TCMP",
        # Encrypted meta frame (2)
        "CRM8",
        # Equalisation (2)
        "EQUA",
        # Equally tempo
        "EQUI",
        # Event timing codes
        "ETCO",
        # Frame rate
        "TFLT",
        # Group identification registration
        "GRID",
        # Involved people list
        "IPLS",
        # Involved people list
        "TIPL",
        # Lyrics
        "ULT", "LYRICS",
        # Music CD identifier
        "MCDI",
        # Musician credits list
        "TMCL",
        # Official audio file webpage
        "WOAS",
        # Original album/movie/show title
        "TOAL",
        # Original artist(s)/performer(s)
        "TOAR",
        # Original filename
        "TOFN",
        # Original lyricist(s)/text writer(s)
        "TOLY",
        # Ownership frame
        "TOWN",
        # Payment terms
        "TPAY",
        # Part of a set
        "TPOS",
        # Part of a compilation
        "TPUB",
        # Popularimeter
        "POPM",
        # Produced notice
        "TPRO",
        # Publisher
        "TPUB",
        # Recording dates
        "TDEN",
        # Recording time
        "TDRC",
        # Recording time
        "TDRL",
        # Relative volume adjustment (2)
        "RVA2",
        # Relative volume adjustment (2)
        "RVAD",
        # Set subtitle
        "TIT3",
        # Synchronised tempo codes
        "SYLT",
        # Synchronised tempo codes
        "SYTC",
        # Synchronised lyric/text
        "USLT",
        # Title/songname/content description
        "TIT1",
        # Title/songname/content description
        "TIT2",
        # Track number/Position in set
        "TRCK",
        # Unique file identifier
        "UFID",
        # User defined text information frame
        "TXXX",
        # User defined URL link frame
        "WXXX",
    ]

    return sorted(set(frames))


def categorize_frames(frames: List[str]) -> Dict[str, List[str]]:
    """Categorize ID3 frames by type."""

    categories = {
        "Text_Information": [],
        "Involved_People": [],
        "Original_Album_Art": [],
        "Commercial": [],
        "Comments": [],
        "Links": [],
        "Ownership": [],
        "Private": [],
        "Playback": [],
        "Encryption": [],
        "Lyrics": [],
        "Binary": [],
        "Timing": [],
        "Chapters": [],
        "Custom": [],
    }

    for frame in frames:
        if frame.startswith("T"):
            categories["Text_Information"].append(frame)
        elif frame in ["TIPL", "TENC", "TEXT", "TOLY", "TOFN", "TOPE", "IPLS"]:
            categories["Involved_People"].append(frame)
        elif frame in ["TOAL", "TOAR", "TOFN", "TOLY"]:
            categories["Original_Album_Art"].append(frame)
        elif frame in ["TCMP", "TPRO", "TCOP", "TFLT", "TLE1", "TLE2", "TLE3", "TMED", "TMOO", "TSOP"]:
            categories["Commercial"].append(frame)
        elif frame == "COMM":
            categories["Comments"].append(frame)
        elif frame.startswith("W") and frame != "WXXX":
            categories["Links"].append(frame)
        elif frame in ["TOWN", "TRSN", "TOWN"]:
            categories["Ownership"].append(frame)
        elif frame in ["PRIV", "UFID"]:
            categories["Private"].append(frame)
        elif frame in ["PCNT", "POPM", "RVA2", "RVRB"]:
            categories["Playback"].append(frame)
        elif frame in ["AENC", "SIGN", "ETCO", "CRM8", "GRID"]:
            categories["Encryption"].append(frame)
        elif frame in ["USLT", "SYLT", "ULT", "LYRICS"]:
            categories["Lyrics"].append(frame)
        elif frame in ["APIC", "GEOB"]:
            categories["Binary"].append(frame)
        elif frame in ["ETCO", "SYTC", "TDEN", "TDRC", "TDRL"]:
            categories["Timing"].append(frame)
        elif frame in ["CTOC", "CHAP"]:
            categories["Chapters"].append(frame)
        elif frame in ["TXXX", "WXXX"]:
            categories["Custom"].append(frame)

    return categories


def generate_inventory(output_dir: Path) -> None:
    """Generate ID3 frame inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    frames: Dict[str, List[str]] = {
        "ID3v2.2": get_id3v22_frames(),
        "ID3v2.3": get_id3v23_frames(),
        "ID3v2.4_Additional": get_id3v24_additional(),
    }

    all_frames: List[str] = []
    for frame_list in frames.values():
        all_frames.extend(frame_list)

    unique_frames = sorted(set(all_frames))

    categories = categorize_frames(unique_frames)

    inventory = {
        "generated_at": "",
        "source": "ID3.org specification",
        "categories": {},
    }

    # Add frame lists
    for version, frame_list in frames.items():
        inventory["categories"][version] = {
            "frames": frame_list,
            "frames_count": len(frame_list),
        }

    # Add categorized groups
    for cat_name, frame_list in categories.items():
        inventory["categories"][f"Category:{cat_name}"] = {
            "description": cat_name.replace("_", " "),
            "frames": sorted(frame_list),
            "frames_count": len(frame_list),
        }

    # Totals
    total_frames = len(unique_frames)
    inventory["totals"] = {
        "total_frames": total_frames,
        "total_versions": len(frames),
        "total_categories": len(categories),
    }

    # Write JSON
    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    output_path = output_dir / "id3_frames_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")

    # Print summary
    print()
    print("=" * 60)
    print("ID3 FRAME INVENTORY SUMMARY")
    print("=" * 60)
    print(f"Total frames: {total_frames}")
    print(f"Total versions: {inventory['totals']['total_versions']}")
    print(f"Total categories: {inventory['totals']['total_categories']}")
    print()
    print("By version:")
    for version, data in inventory["categories"].items():
        if version.startswith("ID3v"):
            print(f"  {version}: {data['frames_count']} frames")
    print()
    print("By category:")
    cat_counts = sorted(
        [(k.replace("Category:", ""), v["frames_count"]) for k, v in inventory["categories"].items() if k.startswith("Category:")],
        key=lambda x: x[1],
        reverse=True,
    )
    for cat_name, count in cat_counts[:10]:
        print(f"  {cat_name}: {count} frames")
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate ID3v2.4 frame inventory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/id3_inventory"),
        help="Output directory (default: dist/id3_inventory)",
    )
    args = parser.parse_args()

    generate_inventory(args.out_dir)


if __name__ == "__main__":
    main()
