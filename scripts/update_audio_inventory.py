#!/usr/bin/env python3
"""Add APEv2 to audio format inventory and regenerate master summary."""

import json
from pathlib import Path

INVENTORY_FILES = [
    "dist/field_inventory_comprehensive/field_inventory_summary.json",
    "dist/video_codec_inventory/video_codec_inventory.json",
    "dist/id3_inventory/id3_frames_inventory.json",
    "dist/audio_format_inventory/audio_format_inventory.json",
    "dist/inventory_summary/master_inventory_summary.json",
]


def update_audio_format_inventory() -> None:
    """Add APEv2 to audio format inventory and regenerate master summary."""
    audio_file = Path("dist/audio_format_inventory/audio_format_inventory.json")

    if not audio_file.exists():
        print(f"[create] Creating empty {audio_file.name}")

        empty_inventory = {
            "generated_at": "",
            "source": "specification",
            "formats": {
                "APEv2": {
                    "format": "APEv2 (Monkey's Audio)",
                    "fields": [
                        {"name": "MAC", "section": "Header"},
                        {"name": "DURATION", "section": "Header"},
                        {"name": "SAMPLE_RATE", "section": "Header"},
                        {"name": "CHANNELS", "section": "Header"},
                        {"name": "TAG_VERSION", "section": "Header"},
                        {"name": "HEADER_SIZE", "section": "Header"},
                        {"name": "FLAGS", "section": "Header"},
                        {"name": "DESCRIPTION", "section": "Header"},
                    ],
                    "field_count": 5,
                }
            }
        }

        audio_file.write_text(json.dumps(empty_inventory, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote: {audio_file}")

    # Regenerate master summary
    master_inventory_path = Path("dist/inventory_summary/master_inventory_summary.json")
    generate_master_summary()


def generate_master_summary() -> None:
    """Regenerate master inventory summary with all audio formats included."""

    from master_inventory_summary import INVENTORY_FILES

    summary = {
        "generated_at": "",
        "inventories": {
            "field_inventory": load_inventory(INVENTORY_FILES[0]),
            "video_codecs": load_inventory(INVENTORY_FILES[1]),
            "id3_frames": load_inventory(INVENTORY_FILES[2]),
            "audio_formats": load_inventory(INVENTORY_FILES[3]),
        },
        "totals": {
            "current": 0,
            "target_45k": 45000,
            "coverage_pct": 0.0,
            "gap_areas": [
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
            ],
        },
        "gap_areas": [
            {"area": area, "fields_needed": count} for area, count in [
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
            ],
    }

    # Calculate totals
    current_total = 0
    field_inv = summary["inventories"]["field_inventory"]
    video_codec_inv = summary["inventories"]["video_codecs"]
    id3_inv = summary["inventories"]["id3_frames"]
    audio_formats_inv = summary["inventories"]["audio_formats"]

    if "totals" in field_inv:
        current_total += field_inv["totals"]["tags"]

    if "totals" in video_codec_inv:
        current_total += video_codec_inv["totals"]["tags"]

    if "totals" in id3_inv:
        current_total += id3_inv["totals"]["total_frames"]

    if "totals" in audio_formats_inv:
        current_total += audio_formats_inv["totals"]["total_fields"]

    summary["totals"]["current"] = current_total
    summary["totals"]["target_45k"] = 45000
    summary["totals"]["coverage_pct"] = (current_total / 45000) * 100
    summary["totals"]["remaining"] = 45000 - current_total

    # Update gap areas
    audio_fmt_count = 2315
    if "field_inv" in audio_formats_inv and "formats" in field_inv["formats"]:
        audio_fmt_count = field_inv["formats"]["total_fields"]

    gap_areas[0]["fields_needed"] = audio_fmt_count

    # Write
    from datetime import datetime, timezone
    summary["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    master_inventory_path = Path("dist/inventory_summary/master_inventory_summary.json")
    master_inventory_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {master_inventory_path}")

    print()
    print("=" * 60)
    print("MASTER INVENTORY SUMMARY (After APEv2 addition)")
    print("=" * 60)
    print()

    if "totals" in field_inv:
        print(f"ExifTool Fields: {field_inv['totals']['tags']}")

    if "totals" in video_codec_inv:
        print(f"Video Codec Fields: {video_codec_inv['totals']['tags']}")

    if "totals" in id3_inv:
        print(f"ID3 Frames: {id3_inv['totals']['total_frames']}")

    if "totals" in audio_formats_inv:
        print(f"Audio Format Fields: {audio_formats_inv['totals']['total_fields']}")

    print()
    print(f"TOTAL CURRENT: {current_total:,} fields")
    print(f"Cov: {summary['totals']['coverage_pct']:.1f}%")
    print(f"Remaining: {summary['totals']['remaining']:,}")

    if audio_formats_inv and "formats" in audio_formats_inv:
        print(f"Audio formats: {len(audio_formats_inv['formats']):,} formats")

    print()
    print("=" * 60)
    print("NEXT PRIORITIES")
    print("=" * 60)
    print()

    # Show gap areas
    gap_items = summary["gap_areas"][:8]
    for gap in gap_items:
        print(f"{gap['area']: {gap['fields_needed']:,} fields needed")
    print(f"Percent of gap filled: {(gap['fields_needed'] / 2315 * 100:.1f}%")

    print()
    print("1. Implement audio format extractors (APEv2, MP4 atoms, WAV/RIFF, AIFF, Opus, DSD, BWF)")
    print("2. Implement FITS keyword inventory")
    print("3. Add file system metadata extraction")
    print("4. Implement network/communication header parsing")
    print("5. Implement digital signature extraction")
    print("6. Add device/hardware fingerprint extraction")
    print("7. Build social media API extractors")
    print("8. Implement web standards parsing")
    print("9. Expand video codec depth extractors")
    print("10. Expand ID3 frame registry (full ID3v2.4 list)")


if __name__ == "__main__":
    main()
