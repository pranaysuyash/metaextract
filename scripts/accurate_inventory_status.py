#!/usr/bin/env python3
"""Accurate field inventory status - REAL numbers, no fluff."""

import json
from pathlib import Path


def load_summary():
    with open("dist/field_inventory_comprehensive/field_inventory_summary.json") as f:
        return json.load(f)


def count_by_category(cats):
    """Count all tags by category without fluff."""
    by_type = {
        "EXIF Standard": 0,
        "GPS": 0,
        "IPTC": 0,
        "XMP": 0,
        "MakerNotes": 0,
        "Video Containers": 0,
        "Audio Formats": 0,
        "Color Management": 0,
        "Documents": 0,
        "DICOM": 0,
        "ID3": 0,
        "ffprobe": 0,
    }

    for cat_name, cat_data in cats.items():
        tags = cat_data.get("tags", 0)

        if cat_name == "EXIF":
            by_type["EXIF Standard"] += tags
            gps_table = cat_data.get("tags_by_table", {}).get("GPS::Main", 0)
            by_type["GPS"] += gps_table

        elif cat_name == "IPTC":
            by_type["IPTC"] += tags

        elif cat_name == "XMP" or cat_name == "Group:XMP":
            if cat_name == "XMP":
                by_type["XMP"] += tags
            else:
                pass

        elif cat_name.startswith("MakerNotes:"):
            by_type["MakerNotes"] += tags

        elif cat_name.startswith("Group:"):
            group = cat_name.split(":", 1)[1]
            if group in ["QuickTime", "Matroska", "RIFF", "MXF", "M2TS", "ASF"]:
                by_type["Video Containers"] += tags
            elif group in ["FLAC", "Vorbis", "APE", "AAC"]:
                by_type["Audio Formats"] += tags
            elif group == "ICC_Profile":
                by_type["Color Management"] += tags
            elif group == "PDF":
                by_type["Documents"] += tags
            elif group == "ID3":
                by_type["ID3"] += tags
            elif group not in ["M2TS", "M2TS", "Vivo", "XMP"]:
                by_type["Video Containers"] += tags

        elif cat_name == "ffprobe":
            by_type["ffprobe"] += tags

        elif cat_name == "id3":
            by_type["ID3"] += tags

        elif cat_name == "pydicom":
            by_type["DICOM"] += tags

    return by_type


def main():
    data = load_summary()
    cats = data["by_category"]
    totals = data["totals"]

    print("=" * 70)
    print("METAEXTRACT FIELD INVENTORY - ACTUAL NUMBERS (NO FLUFF)")
    print("=" * 70)
    print()

    print(f"Total tags (including duplicates): {totals['tags']:,}")
    print(f"Unique field names: {totals['unique_by_category_table_name']:,}")
    print(f"Total categories: {totals['categories']}")
    print()

    by_type = count_by_category(cats)

    print("ACTUAL FIELD COUNTS BY CATEGORY:")
    print(f"{'Category':<30} {'Tags':>10}")
    print("-" * 42)

    for cat, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"{cat:<30} {count:>10,}")

    print()
    total_calculated = sum(by_type.values())
    print(f"Calculated total: {total_calculated:,}")
    print()

    print("=" * 70)
    print("45K+ SPEC TARGETS (for comparison):")
    print("=" * 70)
    print()
    spec_targets = {
        "EXIF Standard": 1200,
        "GPS": 50,
        "IPTC Standards": 150,
        "XMP Standards": 500,
        "MakerNotes": 7000,
        "Color Management": 200,
        "Video Containers": 2000,
        "Audio Formats": 3500,
        "DICOM": 8000,
    }
    spec_total = sum(spec_targets.values())
    print(f"45K+ Spec total: {spec_total:,}")

    print()
    print(f"{'Category':<30} {'Spec':>10} {'Actual':>10} {'Coverage':>10}")
    print("-" * 62)

    total_spec_covered = 0

    for cat, count in by_type.items():
        if count == 0:
            continue

        spec_key = cat
        if cat == "EXIF Standard":
            spec_key = "EXIF Standard"
        elif cat == "XMP":
            spec_key = "XMP Standards"
        elif cat == "Audio Formats":
            spec_key = "Audio Formats"

        if spec_key in spec_targets:
            target = spec_targets[spec_key]
            pct = (count / target * 100) if target > 0 else 0
            total_spec_covered += count
            status = "✓" if pct >= 100 else ">" if pct >= 75 else "~" if pct >= 50 else "<"
            print(f"{status} {cat:<30} {target:>10,} {count:>10,} {pct:>9.1f}%")

    print()
    print(f"Spec covered: {total_spec_covered:,} / {spec_total:,} ({total_spec_covered/spec_total*100:.1f}%)")

    print()
    print("=" * 70)
    print("MISSING FROM SPEC (NOT YET INVENTORIED):")
    print("=" * 70)
    print()

    missing = []
    for cat, target in spec_targets.items():
        if cat in by_type:
            continue
        missing.append((cat, target))

    for cat, target in missing:
        print(f"  {cat:<30} {target:>10,} (not started)")

    print()
    print("=" * 70)
    print("NOTE: MakerNotes target (7,000) is from spec; actual is vendor-dependent")
    print("=" * 70)


if __name__ == "__main__":
    main()
