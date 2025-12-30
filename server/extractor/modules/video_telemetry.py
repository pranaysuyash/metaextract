"""
Video Telemetry Extraction
Extract GoPro/DJI/GPMF telemetry summaries via ExifTool.
"""

from typing import Any, Dict, Iterable, Optional
import json
import logging
import re
import shutil
import subprocess


logger = logging.getLogger(__name__)

EXIFTOOL_PATH = shutil.which("exiftool")
EXIFTOOL_AVAILABLE = EXIFTOOL_PATH is not None

_NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _iter_numbers(value: Any) -> Iterable[float]:
    if value is None:
        return
    if isinstance(value, (int, float)):
        yield float(value)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            for number in _iter_numbers(item):
                yield number
        return
    if isinstance(value, str):
        for match in _NUMBER_RE.findall(value):
            try:
                yield float(match)
            except ValueError:
                continue


def _summarize_numbers(values: Iterable[float]) -> Optional[Dict[str, float]]:
    count = 0
    total = 0.0
    min_val = None
    max_val = None
    first = None
    last = None

    for num in values:
        if first is None:
            first = num
        last = num
        total += num
        count += 1
        if min_val is None or num < min_val:
            min_val = num
        if max_val is None or num > max_val:
            max_val = num

    if count == 0:
        return None

    return {
        "count": count,
        "min": min_val,
        "max": max_val,
        "avg": total / count,
        "first": first,
        "last": last,
    }


def _summarize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _summarize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        numbers = list(_iter_numbers(value))
        if numbers:
            summary = _summarize_numbers(numbers)
            if summary:
                return summary
        return {"count": len(value)}
    return value


def _init_stats() -> Dict[str, Any]:
    return {"count": 0, "sum": 0.0, "min": None, "max": None, "first": None, "last": None}


def _update_stats(stats: Dict[str, Any], value: Any) -> None:
    for num in _iter_numbers(value):
        if stats["first"] is None:
            stats["first"] = num
        stats["last"] = num
        stats["count"] += 1
        stats["sum"] += num
        if stats["min"] is None or num < stats["min"]:
            stats["min"] = num
        if stats["max"] is None or num > stats["max"]:
            stats["max"] = num


def _finalize_stats(stats: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if stats["count"] == 0:
        return None
    return {
        "count": stats["count"],
        "min": stats["min"],
        "max": stats["max"],
        "avg": stats["sum"] / stats["count"],
        "first": stats["first"],
        "last": stats["last"],
    }


def _is_latitude_key(tag: str) -> bool:
    lowered = tag.lower()
    if "latitude" not in lowered:
        return False
    return "ref" not in lowered


def _is_longitude_key(tag: str) -> bool:
    lowered = tag.lower()
    if "longitude" not in lowered:
        return False
    return "ref" not in lowered


def _is_altitude_key(tag: str) -> bool:
    lowered = tag.lower()
    if "altitude" not in lowered:
        return False
    return "ref" not in lowered


def _parse_telemetry(raw: Dict[str, Any]) -> Dict[str, Any]:
    telemetry = {
        "telemetry_present": False,
        "sources": [],
        "field_counts": {},
        "gpmf": {},
        "gopro": {},
        "dji": {},
        "quicktime": {},
        "tracks": {},
        "gps": {},
        "errors": [],
    }

    if not raw:
        return telemetry

    sources = set()
    gps_stats = {
        "latitude": _init_stats(),
        "longitude": _init_stats(),
        "altitude": _init_stats(),
    }

    for full_key, value in raw.items():
        if ":" in full_key:
            group, tag = full_key.split(":", 1)
        else:
            group, tag = "", full_key

        group_lower = group.lower()
        if group_lower in ("gpmf", "gopro", "dji", "quicktime"):
            target = group_lower
        elif group_lower.startswith("track"):
            target = "tracks"
        else:
            continue

        telemetry[target][tag] = _summarize_value(value)
        if target in ("gpmf", "gopro", "dji"):
            sources.add(target)

        if _is_latitude_key(tag):
            _update_stats(gps_stats["latitude"], value)
        if _is_longitude_key(tag):
            _update_stats(gps_stats["longitude"], value)
        if _is_altitude_key(tag):
            _update_stats(gps_stats["altitude"], value)

    telemetry["sources"] = sorted(sources)
    telemetry["field_counts"] = {
        key: len(telemetry[key])
        for key in ["gpmf", "gopro", "dji", "quicktime", "tracks"]
    }

    gps_summary = {}
    lat_summary = _finalize_stats(gps_stats["latitude"])
    lon_summary = _finalize_stats(gps_stats["longitude"])
    alt_summary = _finalize_stats(gps_stats["altitude"])
    if lat_summary:
        gps_summary["latitude"] = lat_summary
    if lon_summary:
        gps_summary["longitude"] = lon_summary
    if alt_summary:
        gps_summary["altitude"] = alt_summary
    if lat_summary and lon_summary:
        gps_summary["bounds"] = {
            "min_lat": lat_summary["min"],
            "max_lat": lat_summary["max"],
            "min_lon": lon_summary["min"],
            "max_lon": lon_summary["max"],
        }
        if alt_summary:
            gps_summary["bounds"]["min_alt"] = alt_summary["min"]
            gps_summary["bounds"]["max_alt"] = alt_summary["max"]

    telemetry["gps"] = gps_summary

    telemetry["telemetry_present"] = any(
        telemetry[key] for key in ["gpmf", "gopro", "dji", "quicktime", "tracks"]
    ) or bool(gps_summary)

    return telemetry


def _run_exiftool(filepath: str) -> Optional[Dict[str, Any]]:
    if not EXIFTOOL_AVAILABLE:
        return None

    cmd = [
        EXIFTOOL_PATH,
        "-j",
        "-n",
        "-G1",
        "-s",
        "-a",
        "-u",
        "-f",
        "-api",
        "LargeFileSupport=1",
        "-ee",
        "-GPMF:all",
        "-GoPro:all",
        "-DJI:all",
        "-QuickTime:all",
        filepath,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception as exc:
        logger.warning(f"ExifTool telemetry failed: {exc}")
        return None

    if result.returncode != 0 or not result.stdout.strip():
        return None

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    return data[0] if data else None


def extract_video_telemetry(filepath: str) -> Dict[str, Any]:
    if not EXIFTOOL_AVAILABLE:
        return {"available": False, "reason": "exiftool not installed"}

    raw = _run_exiftool(filepath)
    if not raw:
        return {
            "available": True,
            "telemetry_present": False,
            "sources": [],
            "field_counts": {},
            "gpmf": {},
            "gopro": {},
            "dji": {},
            "quicktime": {},
            "tracks": {},
            "gps": {},
            "errors": [],
        }

    telemetry = _parse_telemetry(raw)
    telemetry["available"] = True
    return telemetry
