#!/usr/bin/env python3
"""Generate *actual* metadata field inventories from multiple sources.

Supports:
- ExifTool groups (-listx) with auto-discovery (-listg)
- ffprobe schema
- pydicom dictionary
- astropy FITS keywords
- ID3 frame registry (static list)

Outputs (written to --out-dir):
- field_inventory_<source>.json     (full inventory per source)
- field_inventory_summary.json      (unified counts + rollups)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Set

import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class TagDef:
    name: str
    tag_id: Optional[str] = None
    description: Optional[str] = None


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _run_exiftool_version(exiftool_path: str) -> str:
    try:
        result = subprocess.run([exiftool_path, "-ver"], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return "unknown"
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _discover_exiftool_groups(exiftool_path: str, *, timeout_s: int = 60) -> List[str]:
    """Run `exiftool -listg` and return list of group names."""
    try:
        proc = subprocess.run(
            [exiftool_path, "-listg"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=True,
        )
        lines = proc.stdout.strip().splitlines()
        groups: List[str] = []
        for line in lines:
            if ":" in line and "Groups in family" not in line:
                groups_part = line.split(":", 1)[1].strip()
                groups.extend(groups_part.split())
        return sorted(set(groups))
    except Exception as e:
        print(f"[warning] Failed to discover exiftool groups: {e}", file=sys.stderr)
        return []


def _iter_listx_tables(
    exiftool_path: str,
    selectors: List[str],
    *,
    timeout_s: int = 300,
) -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Run `exiftool -listx ...` and return (tables, tag_count)."""

    cmd = [exiftool_path, "-listx", *selectors]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )
    if proc.stdout is None:
        raise RuntimeError("Failed to open exiftool stdout")

    tables: Dict[str, Dict[str, Any]] = {}
    current_table_name: Optional[str] = None
    current_table_attrs: Dict[str, Any] = {}
    tags_seen = 0

    try:
        for event, elem in ET.iterparse(proc.stdout, events=("start", "end")):
            tag = _strip_ns(elem.tag)

            if event == "start" and tag == "table":
                current_table_name = elem.attrib.get("name") or "__unknown_table__"
                current_table_attrs = dict(elem.attrib)
                if current_table_name not in tables:
                    tables[current_table_name] = {"table": current_table_attrs, "tags": []}
                else:
                    if "table" not in tables[current_table_name]:
                        tables[current_table_name]["table"] = current_table_attrs

            if event == "end" and tag == "tag":
                tag_name = elem.attrib.get("name")
                if tag_name:
                    tag_def: Dict[str, Any] = {"name": tag_name}
                    if "id" in elem.attrib:
                        tag_def["id"] = elem.attrib.get("id")
                    if "desc" in elem.attrib:
                        tag_def["desc"] = elem.attrib.get("desc")

                    table_key = current_table_name or "__root__"
                    if table_key not in tables:
                        tables[table_key] = {"table": {"name": table_key}, "tags": []}
                    tables[table_key]["tags"].append(tag_def)
                    tags_seen += 1

                elem.clear()

            if event == "end" and tag == "table":
                current_table_name = None
                current_table_attrs = {}
                elem.clear()

        try:
            proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise RuntimeError(f"exiftool listx timed out after {timeout_s}s: {' '.join(cmd)}")

        if proc.returncode != 0:
            stderr = (proc.stderr.read() if proc.stderr else b"").decode("utf-8", errors="replace")
            raise RuntimeError(f"exiftool listx failed: selectors={selectors} stderr={stderr.strip()}")

        return tables, tags_seen

    finally:
        try:
            if proc.stdout:
                proc.stdout.close()
        except Exception:
            pass
        try:
            if proc.stderr:
                proc.stderr.close()
        except Exception:
            pass


def _inventory_ffprobe() -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Generate inventory from ffprobe (format + stream fields)."""
    ffprobe_path = shutil.which("ffprobe")
    if not ffprobe_path:
        print("[inventory] ffprobe not found, skipping")
        return {}, 0

    print("[inventory] ffprobe: probing schema")

    tables: Dict[str, Dict[str, Any]] = {
        "Format": {"table": {"name": "Format"}, "tags": []},
        "Stream:Video": {"table": {"name": "Stream:Video"}, "tags": []},
        "Stream:Audio": {"table": {"name": "Stream:Audio"}, "tags": []},
        "Stream:Subtitle": {"table": {"name": "Stream:Subtitle"}, "tags": []},
        "Stream:Data": {"table": {"name": "Stream:Data"}, "tags": []},
    }

    try:
        # Run ffprobe on a known file to capture schema
        # We'll use any jpg from the repo as dummy input
        sample_file = None
        for p in Path(".").rglob("*.jpg"):
            sample_file = str(p)
            break

        if not sample_file:
            sample_file = "/dev/null"

        cmd = [
            ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            sample_file,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {}, 0

        data = json.loads(result.stdout)

        # Format fields
        if "format" in data:
            for k in data["format"].keys():
                tables["Format"]["tags"].append({"name": k})

        # Stream fields by type
        for s in data.get("streams", []):
            stype = s.get("codec_type", "unknown")
            if stype == "video":
                target = tables["Stream:Video"]
            elif stype == "audio":
                target = tables["Stream:Audio"]
            elif stype == "subtitle":
                target = tables["Stream:Subtitle"]
            else:
                target = tables["Stream:Data"]

            seen = {t["name"] for t in target["tags"]}
            for k in s.keys():
                if k not in seen:
                    target["tags"].append({"name": k})
                    seen.add(k)

        total = sum(len(t["tags"]) for t in tables.values())
        print(f"[inventory] ffprobe: {total} fields across {len(tables)} tables")
        return tables, total

    except Exception as e:
        print(f"[warning] ffprobe inventory failed: {e}", file=sys.stderr)
        return {}, 0


def _inventory_pydicom() -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Generate inventory from pydicom dictionary."""
    try:
        from pydicom import dcmread
        from pydicom.datadict import DicomDictionary, RepeatersDictionary
        from pydicom._dicom_dict import DicomDictionary, RepeatersDictionary
    except ImportError:
        print("[inventory] pydicom not installed, skipping DICOM inventory")
        return {}, 0

    print("[inventory] pydicom: enumerating dictionary")

    tables: Dict[str, Dict[str, Any]] = {
        "DicomDictionary": {"table": {"name": "DicomDictionary"}, "tags": []},
        "RepeatersDictionary": {"table": {"name": "RepeatersDictionary"}, "tags": []},
    }

    try:
        for tag, (vr, vm, name, keyword, retired) in DicomDictionary.items():
            tag_hex = f"0x{tag:08X}"
            tables["DicomDictionary"]["tags"].append({
                "name": name,
                "id": tag_hex,
                "keyword": keyword,
                "vr": vr,
                "vm": vm,
                "retired": retired,
            })

        for pattern, (vr, vm, description, retired, keyword) in RepeatersDictionary.items():
            tables["RepeatersDictionary"]["tags"].append({
                "name": description,
                "id": pattern,
                "keyword": keyword,
                "vr": vr,
                "vm": vm,
                "retired": retired,
            })

        total = sum(len(t["tags"]) for t in tables.values())
        print(f"[inventory] pydicom: {total} tags across {len(tables)} tables")
        return tables, total

    except Exception as e:
        print(f"[warning] pydicom inventory failed: {e}", file=sys.stderr)
        return {}, 0


def _inventory_fits() -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Generate FITS keyword inventory (simplified; full list is large)."""
    try:
        from astropy.io import fits
    except ImportError:
        print("[inventory] astropy not installed, skipping FITS inventory")
        return {}, 0

    print("[inventory] FITS: enumerating standard keywords (subset)")

    tables: Dict[str, Dict[str, Any]] = {
        "Standard": {"table": {"name": "Standard Keywords"}, "tags": []},
        "WCS": {"table": {"name": "World Coordinate System"}, "tags": []},
        "Telescope": {"table": {"name": "Telescope/Observatory"}, "tags": []},
    }

    # A curated subset of common FITS keywords
    standard_keywords = [
        "SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "NAXIS3",
        "EXTEND", "GROUPS", "PCOUNT", "GCOUNT", "BSCALE", "BZERO",
        "BUNIT", "BLANK", "DATAMAX", "DATAMIN", "EXTNAME", "EXTVER",
        "EXTLEVEL", "OBJECT", "TELESCOP", "INSTRUME", "OBSERVER",
        "DATE-OBS", "DATE", "MJD-OBS", "EXPTIME", "EXPOSURE",
        "FILTER", "EQUINOX", "RADECSYS", "CTYPE1", "CTYPE2",
        "CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2", "CDELT1", "CDELT2",
        "CD1_1", "CD1_2", "CD2_1", "CD2_2", "WCSNAME",
        "GAIN", "RDNOISE", "SATURATE", "AIRMASS", "FWHM", "SEEING",
    ]

    for kw in standard_keywords:
        tables["Standard"]["tags"].append({"name": kw})

    # WCS-related
    wcs_keywords = [
        "CTYPE1", "CTYPE2", "CTYPE3", "CRVAL1", "CRVAL2", "CRVAL3",
        "CRPIX1", "CRPIX2", "CRPIX3", "CDELT1", "CDELT2", "CDELT3",
        "CUNIT1", "CUNIT2", "CUNIT3", "PC1_1", "PC1_2", "PC2_1", "PC2_2",
        "LONPOLE", "LATPOLE", "RADESYS", "SPECSYS",
    ]

    for kw in wcs_keywords:
        tables["WCS"]["tags"].append({"name": kw})

    # Telescope-related
    telescope_keywords = [
        "TELESCOP", "INSTRUME", "DETECTOR", "OBSERVER", "OBSERVATORY",
        "SITELAT", "SITELONG", "ALTITUDE", "AUTHOR", "PROPOSID",
        "PROPOSER", "PROG_ID", "PI_NAME",
    ]

    for kw in telescope_keywords:
        tables["Telescope"]["tags"].append({"name": kw})

    total = sum(len(t["tags"]) for t in tables.values())
    print(f"[inventory] FITS: {total} keywords across {len(tables)} tables (partial subset)")
    return tables, total


def _inventory_id3() -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Generate ID3 frame inventory (static list of common frames)."""

    print("[inventory] ID3: enumerating common frames")

    tables: Dict[str, Dict[str, Any]] = {
        "ID3v2_2": {"table": {"name": "ID3v2.2 Frames"}, "tags": []},
        "ID3v2_3": {"table": {"name": "ID3v2.3/2.4 Frames"}, "tags": []},
        "ID3v1": {"table": {"name": "ID3v1/v1.1 Fields"}, "tags": []},
    }

    # ID3v2.2 frames (3-char identifiers)
    id3v2_2 = [
        "TT2", "T1", "T2", "T3", "COM", "TAL", "TP1", "TP2", "TP3",
        "TRK", "TYE", "TCO", "TEN", "WAF", "WBP", "WCM", "WCP",
    ]

    for f in id3v2_2:
        tables["ID3v2_2"]["tags"].append({"name": f})

    # ID3v2.3/2.4 frames (4-char identifiers) - common subset
    id3v2_3 = [
        "TIT2", "TPE1", "TALB", "TRCK", "TYER", "TDRC", "TCON", "TPE2",
        "TPE3", "TPE4", "TPOS", "TCOM", "TIT1", "TIT3", "TOLY",
        "TCOP", "TPUB", "WOAR", "WCOM", "WOAF", "TLEN", "TBPM",
        "TKEY", "TLAN", "USLT", "COMM", "TXXX", "WXXX", "UFID",
        "PRIV", "APIC", "GEOB", "PCNT", "POPM", "RVA2", "RBUF",
        "AENC", "ETCO", "MCDI", "MLLT", "SYTC", "UFID", "POSS",
        "OWNE", "COMR", "ENCR", "GRID", "LINK", "POPM", "RVRB",
        "EQUA", "EQU2", "RVAD", "RVA2", "TFLT", "TMED", "TMOO",
        "TCOP", "TPRO", "TCR", "TOWN", "TRSO", "TLEN", "TSIZ",
        "TSRC", "TSSE", "TORY", "TDAT", "TIME", "TORY", "TRDA",
        "TIPL", "TMCL", "IPLS", "MCDI", "ETCO", "MLLT", "SYTC",
        "SST", "ULT", "SLT", "SYLT", "COMR", "UFLT", "GEOB",
    ]

    for f in id3v2_3:
        tables["ID3v2_3"]["tags"].append({"name": f})

    # ID3v1 fields
    id3v1 = ["title", "artist", "album", "year", "comment", "track", "genre"]

    for f in id3v1:
        tables["ID3v1"]["tags"].append({"name": f})

    total = sum(len(t["tags"]) for t in tables.values())
    print(f"[inventory] ID3: {total} frames/fields across {len(tables)} tables")
    return tables, total


def _summarize_inventory(inventory: Dict[str, Any]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "generated_at": inventory.get("generated_at"),
        "sources": inventory.get("sources", {}),
        "totals": {},
        "by_category": {},
    }

    grand_total = 0
    all_unique: set[str] = set()

    for source, source_payload in inventory.get("sources", {}).items():
        summary["sources"][source] = {
            "version": source_payload.get("version", "unknown"),
            "path": source_payload.get("path"),
        }

    for category, cat_payload in inventory.get("categories", {}).items():
        tables: Dict[str, Any] = cat_payload.get("tables", {})
        category_total = 0
        category_unique: set[str] = set()
        per_table: Dict[str, int] = {}

        for table_name, table_payload in tables.items():
            tag_defs: List[Dict[str, Any]] = table_payload.get("tags", [])
            per_table[table_name] = len(tag_defs)
            category_total += len(tag_defs)
            for tag_def in tag_defs:
                name = tag_def.get("name")
                if not isinstance(name, str):
                    continue
                category_unique.add(name)
                all_unique.add(f"{category}:{table_name}:{name}")

        summary["by_category"][category] = {
            "tables": len(tables),
            "tags": category_total,
            "unique_names": len(category_unique),
            "tags_by_table": dict(sorted(per_table.items(), key=lambda kv: kv[1], reverse=True)),
        }
        grand_total += category_total

    summary["totals"] = {
        "tags": grand_total,
        "unique_by_category_table_name": len(all_unique),
        "categories": len(inventory.get("categories", {})),
        "sources": len(inventory.get("sources", {})),
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate comprehensive metadata field inventories from multiple sources",
    )

    parser.add_argument(
        "--out-dir",
        default="dist/field_inventory_comprehensive",
        help="Output directory (default: dist/field_inventory_comprehensive)",
    )

    exif_group = parser.add_argument_group("ExifTool options")
    exif_group.add_argument(
        "--exif",
        action="store_true",
        help="Include EXIF group (-EXIF:All)",
    )
    exif_group.add_argument(
        "--iptc",
        action="store_true",
        help="Include IPTC group (-IPTC:All)",
    )
    exif_group.add_argument(
        "--xmp",
        action="store_true",
        help="Include XMP group (-XMP:All)",
    )
    exif_group.add_argument(
        "--include-groups",
        nargs="+",
        help="Specific ExifTool groups to inventory (e.g., QuickTime Matroska)",
    )
    exif_group.add_argument(
        "--discover-all-groups",
        action="store_true",
        help="Discover and inventory all ExifTool groups (may take a long time)",
    )

    exif_group.add_argument(
        "--vendors",
        nargs="+",
        default=[
            "Canon", "Nikon", "Sony", "Fujifilm", "Olympus", "Panasonic",
            "Pentax", "Leica", "Sigma", "Hasselblad", "PhaseOne", "Ricoh",
            "DJI", "GoPro", "Samsung", "Apple", "Minolta", "Casio",
            "Kodak", "Sanyo", "Xiaomi", "HTC", "LG", "OnePlus",
        ],
        help="MakerNotes vendors for --makernotes",
    )
    exif_group.add_argument(
        "--makernotes",
        action="store_true",
        help="Include MakerNotes vendor groups (--vendors)",
    )

    other_group = parser.add_argument_group("Other sources")
    other_group.add_argument(
        "--ffprobe",
        action="store_true",
        help="Include ffprobe schema",
    )
    other_group.add_argument(
        "--pydicom",
        action="store_true",
        help="Include pydicom dictionary",
    )
    other_group.add_argument(
        "--fits",
        action="store_true",
        help="Include FITS keywords (subset)",
    )
    other_group.add_argument(
        "--id3",
        action="store_true",
        help="Include ID3 frame registry",
    )

    parser.add_argument(
        "--timeout-s",
        type=int,
        default=300,
        help="Timeout per exiftool -listx call (seconds)",
    )

    args = parser.parse_args()

    exiftool_path = shutil.which("exiftool")
    if not exiftool_path:
        print("ERROR: exiftool not found in PATH", file=sys.stderr)
        sys.exit(2)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory: Dict[str, Any] = {
        "generated_at": _utc_iso(),
        "exiftool": {
            "path": exiftool_path,
            "version": _run_exiftool_version(exiftool_path),
        },
        "sources": {},
        "categories": {},
    }

    inventory["sources"]["exiftool"] = {
        "path": exiftool_path,
        "version": inventory["exiftool"]["version"],
    }

    def add_exiftool_category(name: str, selectors: List[str]) -> None:
        print(f"[inventory] {name}: running exiftool {' '.join(selectors)}")
        tables, tags_seen = _iter_listx_tables(exiftool_path, selectors, timeout_s=args.timeout_s)
        inventory["categories"][name] = {
            "selectors": selectors,
            "tags_seen": tags_seen,
            "tables": tables,
        }
        print(f"[inventory] {name}: {tags_seen} tags across {len(tables)} tables")

    def add_other_category(name: str, source: str) -> None:
        print(f"[inventory] {name}: querying {source}")
        if source == "ffprobe":
            tables, tags_seen = _inventory_ffprobe()
        elif source == "pydicom":
            tables, tags_seen = _inventory_pydicom()
        elif source == "fits":
            tables, tags_seen = _inventory_fits()
        elif source == "id3":
            tables, tags_seen = _inventory_id3()
        else:
            return

        if tables:
            inventory["categories"][name] = {
                "source": source,
                "tags_seen": tags_seen,
                "tables": tables,
            }

    # ExifTool core groups
    if args.exif:
        add_exiftool_category("EXIF", ["-EXIF:All"])
    if args.iptc:
        add_exiftool_category("IPTC", ["-IPTC:All"])
    if args.xmp:
        add_exiftool_category("XMP", ["-XMP:All"])

    # ExifTool specific groups
    if args.include_groups:
        for group in args.include_groups:
            add_exiftool_category(f"Group:{group}", [f"-{group}:All"])

    # Discover all ExifTool groups
    if args.discover_all_groups:
        print("[inventory] discovering all exiftool groups via -listg")
        groups = _discover_exiftool_groups(exiftool_path)
        for group in groups:
            if group in ["MakerNotes", "Composite"]:
                continue
            add_exiftool_category(f"Group:{group}", [f"-{group}:All"])

    # MakerNotes vendors
    if args.makernotes:
        for vendor in args.vendors:
            add_exiftool_category(f"MakerNotes:{vendor}", [f"-{vendor}:All"])

    # Other sources
    if args.ffprobe:
        add_other_category("ffprobe", "ffprobe")
        ffprobe_path = shutil.which("ffprobe")
        if ffprobe_path:
            result = subprocess.run([ffprobe_path, "-version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.splitlines()[0].strip()
                inventory["sources"]["ffprobe"] = {"path": ffprobe_path, "version": version}

    if args.pydicom:
        add_other_category("pydicom", "pydicom")
        try:
            from pydicom import __version__
            inventory["sources"]["pydicom"] = {"path": "python", "version": __version__}
        except ImportError:
            pass

    if args.fits:
        add_other_category("fits", "fits")
        try:
            from astropy import __version__
            inventory["sources"]["fits"] = {"path": "python", "version": __version__}
        except ImportError:
            pass

    if args.id3:
        add_other_category("id3", "id3")
        inventory["sources"]["id3"] = {"path": "static", "version": "common_frames"}

    # Write outputs
    inventory_path = out_dir / "field_inventory_comprehensive.json"
    summary_path = out_dir / "field_inventory_summary.json"

    summary = _summarize_inventory(inventory)

    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote: {inventory_path}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
