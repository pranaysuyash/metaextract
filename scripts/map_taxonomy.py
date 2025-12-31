#!/usr/bin/env python3
"""Map generated field inventories to the ultimate metadata universe taxonomy (legacy 45K baseline reference)."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

INVENTORY_PATH = Path("dist/field_inventory_comprehensive/field_inventory_summary.json")
OUTPUT_PATH = Path("dist/field_inventory_comprehensive/taxonomy_mapping.json")


def load_inventory(path: Path) -> Dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def map_to_taxonomy(inventory: Dict[str, Any]) -> Dict[str, Any]:
    """Map inventory categories to ultimate taxonomy domains (legacy 45K baseline reference)."""

    by_category = inventory.get("by_category", {})

    taxonomy: Dict[str, Any] = {
        "IMAGE_METADATA": {
            "EXIF_Standard": {
                "name": "EXIF Standard (Core)",
                "target": 1200,
                "mapped": 0,
                "categories": [],
            },
            "MakerNotes": {
                "name": "MakerNotes (Vendor-Specific)",
                "target": 7000,
                "mapped": 0,
                "categories": [],
            },
            "IPTC_Standards": {
                "name": "IPTC Standards",
                "target": 150,
                "mapped": 0,
                "categories": [],
            },
            "XMP_Standards": {
                "name": "XMP Standards",
                "target": 500,
                "mapped": 0,
                "categories": [],
            },
            "Color_Management": {
                "name": "Color Management",
                "target": 200,
                "mapped": 0,
                "categories": [],
            },
        },
        "VIDEO_METADATA": {
            "Container_Formats": {
                "name": "Container Formats",
                "target": 2000,
                "mapped": 0,
                "categories": [],
            },
        },
        "AUDIO_METADATA": {
            "ID3_Standards": {
                "name": "ID3 Standards",
                "target": 1200,
                "mapped": 0,
                "categories": [],
            },
            "Other_Formats": {
                "name": "Other Audio Formats",
                "target": 2300,
                "mapped": 0,
                "categories": [],
            },
        },
        "SCIENTIFIC_MEDICAL": {
            "DICOM": {
                "name": "Medical Imaging (DICOM)",
                "target": 8000,
                "mapped": 0,
                "categories": [],
            },
        },
        "FORENSIC_SECURITY": {
            "File_System_OS": {
                "name": "File System & OS",
                "target": 500,
                "mapped": 0,
                "categories": [],
            },
        },
        "SOCIAL_MOBILE_WEB": {
            "Web_Standards": {
                "name": "Web Standards",
                "target": 500,
                "mapped": 0,
                "categories": [],
            },
        },
    }

    # EXIF Standard
    exif_tags = by_category.get("EXIF", {}).get("tags", 0)
    taxonomy["IMAGE_METADATA"]["EXIF_Standard"]["mapped"] = exif_tags
    taxonomy["IMAGE_METADATA"]["EXIF_Standard"]["categories"].append("EXIF")

    # GPS (part of EXIF)
    gps_tags = 0
    if "EXIF" in by_category:
        gps_table = by_category["EXIF"].get("tags_by_table", {}).get("GPS::Main", 0)
        gps_tags = gps_table

    # MakerNotes
    maker_categories = []
    maker_total = 0
    for cat_name in by_category:
        if cat_name.startswith("MakerNotes:"):
            cat_data = by_category[cat_name]
            vendor = cat_name.split(":", 1)[1] if ":" in cat_name else cat_name
            tags = cat_data.get("tags", 0)
            maker_total += tags
            maker_categories.append({
                "vendor": vendor,
                "tags": tags,
                "tables": cat_data.get("tables", 0),
            })

    taxonomy["IMAGE_METADATA"]["MakerNotes"]["mapped"] = maker_total
    taxonomy["IMAGE_METADATA"]["MakerNotes"]["categories"] = ["MakerNotes"]
    taxonomy["IMAGE_METADATA"]["MakerNotes"]["vendors"] = sorted(
        maker_categories, key=lambda x: x["tags"], reverse=True
    )

    # IPTC
    iptc_tags = by_category.get("IPTC", {}).get("tags", 0)
    taxonomy["IMAGE_METADATA"]["IPTC_Standards"]["mapped"] = iptc_tags
    taxonomy["IMAGE_METADATA"]["IPTC_Standards"]["categories"].append("IPTC")

    # XMP
    xmp_tags = by_category.get("XMP", {}).get("tags", 0)
    taxonomy["IMAGE_METADATA"]["XMP_Standards"]["mapped"] = xmp_tags
    taxonomy["IMAGE_METADATA"]["XMP_Standards"]["categories"].append("XMP")

    # Color Management (ICC Profile)
    icc_tags = 0
    if "Group:ICC_Profile" in by_category:
        icc_tags = by_category["Group:ICC_Profile"].get("tags", 0)
    taxonomy["IMAGE_METADATA"]["Color_Management"]["mapped"] = icc_tags
    taxonomy["IMAGE_METADATA"]["Color_Management"]["categories"].append("ICC_Profile")

    # Video Containers
    video_categories = ["QuickTime", "Matroska", "RIFF", "MXF", "M2TS", "ASF"]
    video_total = 0
    video_details = []

    for cat_name in by_category:
        if cat_name.startswith("Group:") and any(vc in cat_name for vc in video_categories):
            cat_data = by_category[cat_name]
            group_name = cat_name.split(":", 1)[1] if ":" in cat_name else cat_name
            tags = cat_data.get("tags", 0)
            video_total += tags
            video_details.append({
                "group": group_name,
                "tags": tags,
                "tables": cat_data.get("tables", 0),
            })

    taxonomy["VIDEO_METADATA"]["Container_Formats"]["mapped"] = video_total
    taxonomy["VIDEO_METADATA"]["Container_Formats"]["categories"] = [f"Group:{g}" for g in video_categories]
    taxonomy["VIDEO_METADATA"]["Container_Formats"]["groups"] = sorted(
        video_details, key=lambda x: x["tags"], reverse=True
    )

    # Audio Formats
    audio_categories = ["FLAC", "Vorbis", "APE", "AAC", "ID3"]
    audio_total = 0
    audio_details = []

    for cat_name in by_category:
        if cat_name in audio_categories or cat_name.startswith("Group:") and any(ac in cat_name for ac in audio_categories):
            cat_data = by_category[cat_name]
            name = cat_name.split(":", 1)[1] if ":" in cat_name else cat_name
            tags = cat_data.get("tags", 0)
            audio_total += tags
            audio_details.append({
                "group": name,
                "tags": tags,
                "tables": cat_data.get("tables", 0),
            })

    taxonomy["AUDIO_METADATA"]["ID3_Standards"]["mapped"] = by_category.get("id3", {}).get("tags", 0)
    taxonomy["AUDIO_METADATA"]["ID3_Standards"]["categories"].append("id3")
    taxonomy["AUDIO_METADATA"]["Other_Formats"]["mapped"] = audio_total
    taxonomy["AUDIO_METADATA"]["Other_Formats"]["categories"] = audio_details

    # DICOM
    dicom_tags = by_category.get("pydicom", {}).get("tags", 0)
    taxonomy["SCIENTIFIC_MEDICAL"]["DICOM"]["mapped"] = dicom_tags
    taxonomy["SCIENTIFIC_MEDICAL"]["DICOM"]["categories"].append("pydicom")

    # ffprobe (adds to video/audio)
    ffprobe_tags = by_category.get("ffprobe", {}).get("tags", 0)
    taxonomy["VIDEO_METADATA"]["Container_Formats"]["mapped"] += ffprobe_tags

    return taxonomy


def generate_report(taxonomy: Dict[str, Any], inventory: Dict[str, Any]) -> str:
    """Generate human-readable report."""

    lines = []
    lines.append("=" * 70)
    lines.append("METADATA FIELD INVENTORY - ultimate mapping (legacy 45K baseline)")
    lines.append("=" * 70)
    lines.append("")

    inventory_totals = inventory.get("totals", {})
    lines.append(f"Inventory Totals: {inventory_totals.get('tags', 0):,} tags across {inventory_totals.get('categories', 0)} categories")
    lines.append(f"Unique (by category:table:name): {inventory_totals.get('unique_by_category_table_name', 0):,}")
    lines.append("")

    for domain, subdomains in taxonomy.items():
        domain_name = domain.replace("_", " ")
        lines.append(f"## {domain_name}")
        lines.append("")

        for subdomain_name, subdomain in subdomains.items():
            if not isinstance(subdomain, dict):
                continue

            target = subdomain.get("target", 0)
            mapped = subdomain.get("mapped", 0)
            pct = (mapped / target * 100) if target > 0 else 0
            status = "✓" if pct >= 100 else ">" if pct >= 75 else "~" if pct >= 50 else "<"

            lines.append(f"  {status} {subdomain['name']}")
            lines.append(f"      Target: {target:,} | Mapped: {mapped:,} ({pct:.1f}%)")

            if "vendors" in subdomain:
                lines.append("      Top vendors by tags:")
                for v in subdomain["vendors"][:5]:
                    lines.append(f"        - {v['vendor']:20s}: {v['tags']:4,} tags ({v['tables']} tables)")
                if len(subdomain["vendors"]) > 5:
                    lines.append(f"        ... and {len(subdomain['vendors']) - 5} more")

            if "groups" in subdomain:
                lines.append("      Groups:")
                for g in subdomain["groups"][:5]:
                    lines.append(f"        - {g['group']:20s}: {g['tags']:4,} tags ({g['tables']} tables)")
                if len(subdomain["groups"]) > 5:
                    lines.append(f"        ... and {len(subdomain['groups']) - 5} more")

            lines.append("")

    lines.append("=" * 70)
    lines.append("NOT COVERED YET (requires future work):")
    lines.append("")
    lines.append("  - FITS astronomical keywords (requires astropy installation)")
    lines.append("  - GeoTIFF fields")
    lines.append("  - File System & OS metadata (extended attributes, NTFS/HFS/APFS specifics)")
    lines.append("  - Digital signatures & authentication")
    lines.append("  - Network/communication headers")
    lines.append("  - Device & hardware fingerprints")
    lines.append("  - Social media platform metadata (requires API access)")
    lines.append("  - Mobile device metadata (health, location history)")
    lines.append("  - Web standards (Open Graph, Twitter Cards, Schema.org)")
    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def main() -> None:
    inventory = load_inventory(INVENTORY_PATH)
    taxonomy = map_to_taxonomy(inventory)

    # Write JSON
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(taxonomy, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {OUTPUT_PATH}")

    # Generate report
    report = generate_report(taxonomy, inventory)
    report_path = OUTPUT_PATH.parent / "TAXONOMY_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote: {report_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("TAXONOMY MAPPING SUMMARY")
    print("=" * 70)

    grand_target = 0
    grand_mapped = 0

    for domain, subdomains in taxonomy.items():
        for subdomain_name, subdomain in subdomains.items():
            if not isinstance(subdomain, dict):
                continue
            grand_target += subdomain.get("target", 0)
            grand_mapped += subdomain.get("mapped", 0)

    coverage = (grand_mapped / grand_target * 100) if grand_target > 0 else 0

    print(f"Target fields: {grand_target:,}")
    print(f"Mapped fields:  {grand_mapped:,}")
    print(f"Coverage:       {coverage:.1f}%")
    print(f"Gaps:          {grand_target - grand_mapped:,}")


if __name__ == "__main__":
    main()
