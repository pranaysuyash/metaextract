#!/usr/bin/env python3
"""Master inventory summary for MetaExtract 45K+ goal.

This script combines all field inventories and shows total progress
toward the 45,000+ field target.
"""

import json
from pathlib import Path
from typing import Dict


INVENTORY_DIRS = [
    ("field_inventory_comprehensive", "field_inventory_summary.json"),
    ("video_codec_inventory", "video_codec_inventory.json"),
    ("id3_inventory", "id3_frames_inventory.json"),
    ("audio_format_inventory", "audio_format_inventory.json"),
    ("fits_inventory", "fits_inventory.json"),
    ("filesystem_inventory", "filesystem_inventory.json"),
    ("network_inventory", "network_inventory.json"),
    ("web_standards_inventory", "web_standards_inventory.json"),
    ("device_hardware_inventory", "device_hardware_inventory.json"),
    ("social_media_inventory", "social_media_summary.json"),
    ("bwf_rf64_inventory", "bwf_rf64_summary.json"),
    ("pdf_inventory", "pdf_summary.json"),
    ("signature_inventory", "signature_summary.json"),
    ("dicom_extended_inventory", "dicom_extended_summary.json"),
    ("geospatial_inventory", "geospatial_summary.json"),
    ("office_inventory", "office_summary.json"),
    ("forensic_inventory", "forensic_summary.json"),
    ("mobile_inventory", "mobile_summary.json"),
    ("font_inventory", "font_summary.json"),
    ("database_inventory", "database_summary.json"),
    ("containers_inventory", "containers_summary.json"),
    ("scientific_inventory", "scientific_summary.json"),
    ("email_inventory", "email_summary.json"),
    ("archive_inventory", "archive_summary.json"),
]


def load_inventory(dir_name: str, filename: str) -> Dict:
    """Load inventory JSON file."""
    dir_path = Path("dist") / dir_name
    summary_file = dir_path / filename
    if summary_file.exists():
        try:
            with open(summary_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"[warn] Failed to load {dir_path}/{filename}: {e}")
    return {}


def main():
    from datetime import datetime, timezone

    print("=" * 70)
    print("METAFIELD INVENTORY MASTER SUMMARY (EXPANDED)")
    print("=" * 70)
    print()

    # Load all inventories
    inventories = {}
    totals_by_source = {}

    for dir_name, filename in INVENTORY_DIRS:
        inv = load_inventory(dir_name, filename)
        if inv:
            inventories[dir_name] = inv

            # Extract totals - check multiple locations
            totals = inv.get("totals", {})
            source_name = dir_name.replace("_inventory", "").replace("_comprehensive", "")

            if "tags" in totals:
                totals_by_source[source_name] = ("tags", totals["tags"])
            elif "total_fields" in totals:
                totals_by_source[source_name] = ("fields", totals["total_fields"])
            elif "total_keywords" in totals:
                totals_by_source[source_name] = ("keywords", totals["total_keywords"])
            elif "total_frames" in totals:
                totals_by_source[source_name] = ("frames", totals["total_frames"])
            elif "total_fields" in inv:  # Check top level for some inventories
                totals_by_source[source_name] = ("fields", inv["total_fields"])
            elif "total" in inv:  # Check top level for some inventories
                total_val = inv["total"]
                if isinstance(total_val, int):
                    totals_by_source[source_name] = ("fields", total_val)

    # Calculate grand total
    grand_total = sum(count for _, count in totals_by_source.values())

    # 45K target
    target_45k = 45000
    coverage = (grand_total / target_45k) * 100
    remaining = target_45k - grand_total

    print("FIELD INVENTORIES")
    print("-" * 70)
    print()

    for source_name, (unit, count) in sorted(totals_by_source.items(), key=lambda x: x[1][1], reverse=True):
        print(f"  {source_name:35s}: {count:>8,} {unit}")

    print()
    print("=" * 70)
    print("45K+ TARGET PROGRESS")
    print("=" * 70)
    print()

    print(f"  Target fields: {target_45k:,}")
    print(f"  Current total:  {grand_total:,}")
    print(f"  Coverage: {coverage:.1f}%")
    print(f"  Remaining: {remaining:,}")

    print()
    print("=" * 70)
    print("INVENTORY BREAKDOWN")
    print("=" * 70)
    print()

    # Show category breakdown
    all_categories = []
    for dir_name, inv in inventories.items():
        source = dir_name.replace("_inventory", "").replace("_comprehensive", "")
        categories = inv.get("categories", {})
        
        if isinstance(categories, dict):
            for cat_name, cat_data in categories.items():
                if isinstance(cat_data, dict):
                    count = cat_data.get("count", cat_data.get("tags", cat_data.get("fields", 0)))
                    if isinstance(count, list):
                        count = len(count)
                    if count > 0:
                        all_categories.append((f"{source}/{cat_name}", count))
        elif isinstance(categories, int):
            pass  # Skip if categories is just a count

    all_categories.sort(key=lambda x: x[1], reverse=True)

    for cat_name, count in all_categories[:25]:
        pct = (count / grand_total * 100) if grand_total > 0 else 0
        print(f"  {cat_name:50s}: {count:>6,} ({pct:5.1f}%)")

    if len(all_categories) > 25:
        print(f"  ... and {len(all_categories) - 25} more categories")

    print()
    print("=" * 70)
    print("NEXT IMPLEMENTATION STEPS")
    print("=" * 70)
    print()
    print("  1. Implement audio format extractors (APEv2, MP4 atoms, WAV/RIFF, AIFF, Opus, DSD, BWF)")
    print("  2. Implement social media API extractors (Instagram, TikTok, YouTube)")
    print("  3. Implement digital signature extraction (code signing, PDF, C2PA, blockchain)")
    print("  4. Expand video codec depth extractors")
    print("  5. Expand ID3 frame registry (full ID3v2.4 list)")
    print()

    # Write summary
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "totals_by_source": {k: {"unit": v[0], "count": v[1]} for k, v in totals_by_source.items()},
        "categories": all_categories,
        "totals": {
            "current": grand_total,
            "target_45k": target_45k,
            "coverage_pct": coverage,
            "remaining": remaining,
        },
    }

    output_dir = Path("dist/inventory_summary")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "master_inventory_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"  Wrote: {summary_path}")


if __name__ == "__main__":
    main()
