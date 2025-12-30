#!/usr/bin/env python3
"""Master inventory summary for MetaExtract 45K+ goal.

This script combines all field inventories and shows total progress
toward the 45,000+ field target.
"""

import json
from pathlib import Path
from typing import Dict, List


INVENTORY_FILES = [
    "dist/field_inventory_comprehensive/field_inventory_summary.json",
    "dist/video_codec_inventory/video_codec_inventory.json",
    "dist/id3_inventory/id3_frames_inventory.json",
    "dist/audio_format_inventory/audio_format_inventory.json",
]


def load_inventory(path: str) -> Dict:
    """Load inventory JSON file."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[skip] {path} (not found)")
        return {}
    except Exception as e:
        print(f"[error] Failed to load {path}: {e}")
        return {}


def summarize_field_inventory(inventory: Dict) -> Dict[str, int]:
    """Summarize field inventory."""

    totals = inventory.get("totals", {})
    return {
        "tags": totals.get("tags", 0),
        "categories": totals.get("categories", 0),
        "unique": totals.get("unique_by_category_table_name", 0),
    }


def summarize_video_codecs(inventory: Dict) -> Dict[str, int]:
    """Summarize video codec inventory."""

    totals = inventory.get("totals", {})
    categories = inventory.get("categories", {})

    total = 0
    for cat, data in categories.items():
        if cat.startswith("Video Codec"):
            total += data.get("tags", 0)

    return {
        "tags": total,
        "categories": len([c for c in categories.keys() if c.startswith("Video Codec")]),
    }


def summarize_id3_frames(inventory: Dict) -> Dict[str, int]:
    """Summarize ID3 frame inventory."""

    totals = inventory.get("totals", {})
    return {
        "total_frames": totals.get("total_frames", 0),
        "total_versions": totals.get("total_versions", 0),
        "total_categories": totals.get("total_categories", 0),
    }


def summarize_audio_formats(inventory: Dict) -> Dict[str, int]:
    """Summarize audio format inventory."""

    totals = inventory.get("totals", {})
    formats = inventory.get("formats", {})

    total = 0
    for fmt, data in formats.items():
        total += data.get("field_count", 0)

    return {
        "total_fields": total,
        "total_formats": len(formats),
    }


def main():
    from datetime import datetime, timezone

    print("=" * 70)
    print("METAFIELD INVENTORY MASTER SUMMARY")
    print("=" * 70)
    print()

    # Load all inventories
    field_inv = load_inventory(INVENTORY_FILES[0])
    video_codec_inv = load_inventory(INVENTORY_FILES[1])
    id3_frames_inv = load_inventory(INVENTORY_FILES[2])
    audio_format_inv = load_inventory(INVENTORY_FILES[3])

    # Summarize
    field_summary = summarize_field_inventory(field_inv)
    video_codec_summary = summarize_video_codecs(video_codec_inv)
    id3_summary = summarize_id3_frames(id3_frames_inv)
    audio_summary = summarize_audio_formats(audio_format_inv)

    # Grand total
    grand_total = (
        field_summary["tags"] +
        video_codec_summary["tags"] +
        id3_summary["total_frames"] +
        audio_summary["total_fields"]
    )

    # 45K target
    target_45k = 45000
    coverage = (grand_total / target_45k) * 100
    remaining = target_45k - grand_total

    print("FIELD INVENTORIES")
    print("-" * 70)
    print()

    print(f"ExifTool Field Inventory:")
    print(f"  Tags: {field_summary['tags']:,}")
    print(f"  Categories: {field_summary['categories']}")
    print()

    print(f"Video Codec Inventory:")
    print(f"  Tags: {video_codec_summary['tags']:,}")
    print(f"  Categories: {video_codec_summary['categories']}")
    print()

    print(f"ID3 Frame Inventory:")
    print(f"  Frames: {id3_summary['total_frames']:,}")
    print(f"  Versions: {id3_summary['total_versions']:,}")
    print()

    print(f"Audio Format Inventory:")
    print(f"  Fields: {audio_summary['total_fields']:,}")
    print(f"  Formats: {audio_summary['total_formats']}")
    print()

    print("=" * 70)
    print("45K+ TARGET PROGRESS")
    print("=" * 70)
    print()

    print(f"Target fields: {target_45k:,}")
    print(f"Current total:  {grand_total:,}")
    print(f"Coverage: {coverage:.1f}%")
    print(f"Remaining: {remaining:,}")
    print()

    print("TOP GAP AREAS (fields needed)")
    print("-" * 70)
    print()

    gap_areas = [
        ("Audio format specifics (APEv2, MP4 atoms, WAV/RIFF, AIFF, Opus, DSD, BWF)", 2315),
        ("FITS/Geospatial (FITS keywords, GeoTIFF, Shapefile, KML)", 3200),
        ("File system/OS metadata (NTFS, APFS/HFS+, extended attributes)", 500),
        ("Network/communication (email, HTTP, DNS, TLS)", 600),
        ("Digital signatures (code signing, PDF, C2PA, blockchain)", 500),
        ("Device/hardware (CPU ID, TPM, MAC, firmware)", 400),
        ("Social media APIs (Instagram, TikTok, YouTube)", 800),
        ("Web standards (Open Graph, Twitter Cards, Schema.org)", 500),
        ("Video codec depth (H.264/HEVC/VP9/AV1 bitstream params, HDR, color space)", 3000),
        ("Full ID3v2.4 registry expansion", 1008),
    ]

    gap_total = sum(g[1] for g in gap_areas)

    for area, count in sorted(gap_areas, key=lambda x: x[1], reverse=True):
        pct = (count / gap_total) * 100
        print(f"  {area}: {count:,} fields ({pct:.1f}%)")

    print()
    print(f"Gap total: {gap_total:,}")
    print(f"Grand total with gaps: {grand_total + gap_total:,}")
    print()

    # Write summary
    from datetime import datetime, timezone
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inventories": {
            "field_inventory": {
                "tags": field_summary["tags"],
                "categories": field_summary["categories"],
            },
            "video_codecs": {
                "tags": video_codec_summary["tags"],
                "categories": video_codec_summary["categories"],
            },
            "id3_frames": {
                "frames": id3_summary["total_frames"],
                "versions": id3_summary["total_versions"],
            },
            "audio_formats": {
                "fields": audio_summary["total_fields"],
                "formats": audio_summary["total_formats"],
            },
        },
        "totals": {
            "current": grand_total,
            "target_45k": target_45k,
            "coverage_pct": coverage,
            "remaining": remaining,
        },
        "gap_areas": [
            {"area": area, "fields_needed": count} for area, count in gap_areas
        ],
    }

    output_dir = Path("dist/inventory_summary")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "master_inventory_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {summary_path}")

    print()
    print("=" * 70)
    print("NEXT PRIORITIES")
    print("=" * 70)
    print()
    print("1. Implement audio format extractors (APEv2, MP4 atoms, WAV/RIFF)")
    print("2. Add FITS keyword inventory")
    print("3. Add file system metadata extraction")
    print("4. Implement network/communication header parsing")
    print("5. Implement digital signature extraction")
    print("6. Add device/hardware fingerprint extraction")
    print("7. Build social media API extractors")
    print("8. Implement web standards parsing")
    print()


if __name__ == "__main__":
    main()
