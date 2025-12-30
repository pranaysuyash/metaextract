#!/usr/bin/env python3
"""Validate extraction capabilities by running the metadata_engine script.

This script:
1. Runs extraction on sample files using metadata_engine.py
2. Counts how many fields are actually extracted
3. Compares to inventory totals
4. Identifies gaps and missing extractions
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

# Check exiftool availability
EXIFTOOL_PATH = shutil.which("exiftool")
EXIFTOOL_AVAILABLE = EXIFTOOL_PATH is not None

# Check metadata_engine.py availability
METADATA_ENGINE_PATH = Path("server/extractor/metadata_engine.py")
METADATA_ENGINE_AVAILABLE = METADATA_ENGINE_PATH.exists()


def create_test_images(output_dir: Path) -> List[str]:
    """Create test images with embedded metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)

    test_files = []

    # Test 1: Rich EXIF + IPTC + XMP image
    test1_path = output_dir / "test_rich_metadata.jpg"
    print(f"[test] Creating {test1_path.name}")

    if EXIFTOOL_AVAILABLE:
        cmd = [
            EXIFTOOL_PATH,
            "-overwrite_original",
            "-EXIF:Make=TestCamera",
            "-EXIF:Model=TestModel v1.0",
            "-EXIF:ExposureTime=1/125",
            "-EXIF:FNumber=2.8",
            "-EXIF:ISOSpeedRatings=400",
            "-EXIF:FocalLength=50.0",
            "-EXIF:DateTimeOriginal=2024:01:01 12:00:00",
            "-GPS:GPSLatitude=37.7749",
            "-GPS:GPSLatitudeRef=N",
            "-GPS:GPSLongitude=-122.4194",
            "-GPS:GPSLongitudeRef=W",
            "-GPS:GPSAltitude=10",
            "-XMP:dc:title=Test Title",
            "-XMP:dc:creator=Test Creator",
            "-XMP:dc:subject=Test Subject",
            "-XMP:dc:description=Test Description with multiple words",
            "-XMP:photoshop:Headline=Test Headline",
            "-XMP:photoshop:Credit=Test Credit",
            "-IPTC:Headline=IPTC Headline",
            "-IPTC:Caption-Abstract=IPTC Description",
            "-IPTC:Keywords=Test,Metadata,Validation",
            "-IPTC:Creator=Test Creator",
            "-IPTC:City=San Francisco",
            "-IPTC:Country-Name=United States",
            str(test1_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        test_files.append(str(test1_path))

    return test_files


def extract_with_engine(file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract metadata using metadata_engine.py script."""

    if not METADATA_ENGINE_AVAILABLE:
        return {"error": "metadata_engine.py not found", "file": file_path}

    try:
        cmd = [sys.executable, str(METADATA_ENGINE_PATH), file_path, "--tier", "premium"]
        if output_path:
            cmd.extend(["--output", str(output_path)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return {"error": f"Exit code {result.returncode}", "file": file_path}

        # If output_path specified, read from file; otherwise try to parse stdout
        if output_path and os.path.exists(output_path):
            with open(output_path) as f:
                data = json.load(f)
        else:
            output = result.stdout.strip()
            if not output:
                return {"error": "No output", "file": file_path}
            try:
                data = json.loads(output)
            except json.JSONDecodeError as e:
                return {"error": f"JSON decode error: {e}", "file": file_path}

        return data

    except subprocess.TimeoutExpired:
        return {"error": "Timeout after 60s", "file": file_path}
    except Exception as e:
        return {"error": str(e), "file": file_path}


def count_fields(data: Dict[str, Any]) -> tuple[Dict[str, int], int]:

    counts: Dict[str, int] = {}
    total_fields = 0

    def count_dict(d: Dict[str, Any], prefix: str = "") -> int:
        nonlocal total_fields
        count = 0
        for key, value in d.items():
            if isinstance(value, dict):
                count += count_dict(value, f"{prefix}{key}.")
            elif value is None:
                pass
            elif key.startswith("_"):
                pass
            else:
                count += 1
        return count

    # Count top-level sections
    for section in ["exif", "gps", "iptc", "xmp", "video", "audio", "makernote"]:
        if section in data and isinstance(data[section], dict):
            counts[section] = count_dict(data[section], f"{section}.")

    # Check for nested sections (exif_ifd, xmp_namespaces, etc.)
    for section in ["exif_ifd", "xmp_namespaces", "makernote", "image_container", "thumbnail_metadata"]:
        if section in data and isinstance(data[section], dict):
            counts[section] = count_dict(data[section], f"{section}.")

    total_fields = sum(counts.values())

    return counts, total_fields


def load_inventory(path: Path = Path("dist/field_inventory_comprehensive/field_inventory_summary.json")) -> Dict[str, Any]:
    """Load field inventory for comparison."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def compare_actual_to_inventory(
    actual_data: Dict[str, Any],
    inventory: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare actual extraction results to inventory."""

    if not actual_data or "error" in actual_data:
        file_name = "unknown"
    else:
        file_key = actual_data.get("file")
        file_name = Path(str(file_key) if file_key else "").name

    counts, total_fields = count_fields(actual_data)

    comparison = {
        "file": file_name,
        "extracted_fields": total_fields,
        "inventory_available": 0,
        "coverage_pct": 0.0,
        "by_section": {},
        "has_error": "error" in actual_data,
        "error": actual_data.get("error"),
    }

    # Calculate available fields from inventory
    inventory_cats = inventory.get("by_category", {})

    # Image metadata
    image_fields_available = 0
    for cat in ["EXIF", "IPTC"]:
        if cat in inventory_cats:
            image_fields_available += inventory_cats[cat].get("tags", 0)
    image_fields_available += inventory_cats.get("XMP", {}).get("tags", 0)

    # MakerNotes
    makernotes_available = 0
    for cat, data in inventory_cats.items():
        if cat.startswith("MakerNotes:"):
            makernotes_available += data.get("tags", 0)

    # Video containers
    video_available = 0
    for cat, data in inventory_cats.items():
        if cat.startswith("Group:") and any(vc in cat for vc in ["QuickTime", "Matroska", "MXF", "RIFF"]):
            video_available += data.get("tags", 0)

    # DICOM
    dicom_available = inventory_cats.get("pydicom", {}).get("tags", 0)

    comparison["inventory_available"] = (
        image_fields_available + makernotes_available + video_available + dicom_available
    )

    if comparison["inventory_available"] > 0:
        comparison["coverage_pct"] = (total_fields / comparison["inventory_available"]) * 100

    # By section coverage
    for section, count in counts.items():
        if count == 0:
            continue

        target = 0
        if section in ["exif", "exif_ifd"]:
            target = inventory_cats.get("EXIF", {}).get("tags", 0)
        elif section in ["gps"]:
            target = inventory_cats.get("EXIF", {}).get("tags_by_table", {}).get("GPS::Main", 0)
        elif section in ["iptc"]:
            target = inventory_cats.get("IPTC", {}).get("tags", 0)
        elif section in ["xmp", "xmp_namespaces"]:
            target = inventory_cats.get("XMP", {}).get("tags", 0)
        elif section in ["makernote"]:
            target = makernotes_available
        elif section in ["video", "video"]:
            target = video_available
        elif section in ["audio", "audio"]:
            target = 35  # ffprobe audio fields (approximate)
        elif section in ["dicom", "dicom"]:
            target = dicom_available

        if target > 0:
            comparison["by_section"][section] = {
                "extracted": count,
                "available": target,
            }

    return comparison


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate extraction capabilities on real files",
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("dist/validation_test"),
        help="Directory for test files (default: dist/validation_test)",
    )
    parser.add_argument(
        "--use-existing",
        action="store_true",
        help="Use existing test files instead of creating new ones",
    )
    parser.add_argument(
        "--tier",
        default="premium",
        choices=["free", "starter", "premium", "super"],
        help="Extraction tier (default: premium)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist/validation_test"),
        help="Output directory for extraction JSON files",
    )
    args = parser.parse_args()

    if not METADATA_ENGINE_AVAILABLE:
        print("ERROR: metadata_engine.py not found")
        sys.exit(1)

    if not EXIFTOOL_AVAILABLE:
        print("WARNING: exiftool not available - some tests may be limited")

    # Load inventory for comparison
    inventory = load_inventory()

    # Create or use test files
    if args.use_existing:
        test_files = []
        for ext in ["*.jpg", "*.mp4", "*.dcm", "*.pdf"]:
            test_files.extend([str(p) for p in Path(".").glob(ext)])
        if not test_files:
            test_files = [str(Path("sample_with_meta.jpg"))]
    else:
        print(f"[setup] Creating test files in {args.test_dir}")
        test_files = create_test_images(args.test_dir)

    print()
    print("=" * 70)
    print("EXTRACTION VALIDATION TEST")
    print("=" * 70)
    print()

    results = []
    total_extracted = 0

    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"[skip] {file_path} (not found)")
            continue

        # Determine output file path for extraction result
        output_path = args.output_dir / f"{Path(file_path).stem}_metadata.json"

        print(f"[test] Extracting from {Path(file_path).name}")
        result = extract_with_engine(file_path, output_path=str(output_path))

        if "error" in result:
            print(f"  ERROR: {result.get('error')}")
            results.append({
                "file": file_path,
                "error": result.get("error"),
                "extracted_fields": 0,
            })
            continue

        counts, fields = count_fields(result)
        total_extracted += fields

        # Compare to inventory
        if inventory:
            comparison = compare_actual_to_inventory(result, inventory)
            print(f"  Extracted: {fields} fields")
            print(f"  Inventory available: {comparison['inventory_available']} fields")
            print(f"  Coverage: {comparison['coverage_pct']:.1f}%")

            results.append({
                "file": file_path,
                "extracted_fields": fields,
                "inventory_available": comparison["inventory_available"],
                "coverage_pct": comparison["coverage_pct"],
                "by_section": comparison["by_section"],
                "has_error": False,
            })

    # Summary
    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print()

    print(f"Total files tested: {len(results)}")
    print(f"Total fields extracted: {total_extracted}")

    if inventory:
        inventory_totals = inventory.get("totals", {})
        print(f"Inventory total tags: {inventory_totals.get('tags', 0)}")
        print(f"Inventory categories: {inventory_totals.get('categories', 0)}")

        success_results = [r for r in results if not r.get("has_error")]
        if success_results:
            avg_fields = sum(r.get("extracted_fields", 0) for r in success_results) / len(success_results)
            avg_coverage = sum(r.get("coverage_pct", 0) for r in success_results) / len(success_results)
            print(f"Average extraction: {avg_fields:.1f} fields/file")
            print(f"Average coverage: {avg_coverage:.1f}%")

    print()
    print("Section-by-section results:")
    for r in results:
        if r.get("has_error"):
            continue

        file_name = Path(r["file"]).name
        print(f"\n{file_name}:")
        for section, data in r.get("by_section", {}).items():
            if data["extracted"] > 0:
                print(f"  {section}: {data['extracted']} fields")

    # Write results
    output_dir = Path("dist/validation_results")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "validation_results.json"
    results_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote: {results_path}")


if __name__ == "__main__":
    main()
