#!/usr/bin/env python3
"""
Extraction Observability Utilities

Provides provenance tracking, sensitive field detection, and shadow mode
infrastructure for the comprehensive metadata engine.

This module is instrumentation-only: it adds data to extraction_info but
never modifies client-facing metadata or fails the main extraction path.

SECURITY INVARIANTS:
- Diff logs NEVER contain raw values, only paths/keys and counts
- Sensitive field detection reports paths only, not the actual values
- All list outputs are capped to prevent payload bloat

Author: MetaExtract Team
Version: 1.0.0
"""

import os
import re
import time
import random
import logging
from typing import Dict, Any, List, Optional, Tuple, Set

logger = logging.getLogger(__name__)

# Observability schema version - increment when format changes
OBSERVABILITY_VERSION = 1

# Maximum list lengths to prevent payload bloat
MAX_PROVENANCE_CONFLICTS = 50
MAX_SENSITIVE_FIELDS = 200
MAX_DIFF_ENTRIES = 100
MAX_SAMPLE_KEYS = 20

# ============================================================================
# Provenance Tracking
# ============================================================================

def record_top_level_provenance(
    *,
    module_name: str,
    module_output: Optional[Dict[str, Any]],
    provenance: Dict[str, str],
    conflicts: List[Dict[str, str]]
) -> None:
    """
    Record which module introduced each top-level key in the result.
    
    If a later module writes the same key, record a conflict.
    Only tracks top-level keys to avoid explosion in provenance data size.
    
    Args:
        module_name: Name of the module that produced the output
        module_output: The dict this module contributes to the final result
        provenance: Mutable dict mapping key -> first module that introduced it
        conflicts: Mutable list of conflict records
    """
    if not module_output or not isinstance(module_output, dict):
        return
    
    for k in module_output.keys():
        # Skip extraction_info and performance keys (internal)
        if k in ("extraction_info", "performance", "_locked"):
            continue
        
        prev = provenance.get(k)
        if prev is None:
            provenance[k] = module_name
        elif prev != module_name:
            conflicts.append({
                "key": k,
                "first_module": prev,
                "second_module": module_name,
            })


def build_provenance_summary(
    provenance: Dict[str, str],
    conflicts: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Build a summary of module provenance for extraction_info.
    
    Returns:
        Dict with module_provenance and provenance_conflicts
    """
    return {
        "module_provenance": provenance.copy(),
        "provenance_conflicts": conflicts[:MAX_PROVENANCE_CONFLICTS],
        "conflict_count": len(conflicts),
        "truncated": len(conflicts) > MAX_PROVENANCE_CONFLICTS,
    }


# ============================================================================
# Sensitive Field Detection
# ============================================================================

SENSITIVE_RULES: List[Tuple[str, re.Pattern]] = [
    ("gps", re.compile(r"(?i)\bgps\b|latitude|longitude|altitude|coord|geotag|location|GPSLatitude|GPSLongitude")),
    ("device_id", re.compile(r"(?i)serial|bodyserial|lensserial|cameraid|uniqueid|uuid|udid|imei|meid|InternalSerialNumber")),
    ("person", re.compile(r"(?i)owner|author|artist|creator|copyright|byline|username|account|CameraOwnerName")),
    ("network", re.compile(r"(?i)\bmac\b|ip\b|ssid|bluetooth|wifi|MacAddress")),
    ("contact", re.compile(r"(?i)email|phone|address")),
]


def detect_sensitive_fields(
    obj: Any,
    prefix: str = "",
    max_depth: int = 10
) -> List[Dict[str, str]]:
    """
    Detect presence of likely PII and fingerprinting fields.
    
    This is heuristic-based detection using key name matching.
    It does NOT redact or modify any data - only reports what was found.
    
    Args:
        obj: The object to scan (typically the extraction result)
        prefix: Current path prefix for nested keys
        max_depth: Maximum recursion depth to prevent stack overflow
        
    Returns:
        List of {"path": "...", "kind": "gps|device_id|person|network|contact|other"}
    """
    if max_depth <= 0:
        return []
    
    hits: List[Dict[str, str]] = []
    
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Skip internal/meta keys
            if str(k).startswith("_"):
                continue
            
            path = f"{prefix}.{k}" if prefix else str(k)
            key_str = str(k)
            
            # Check key name against sensitive patterns
            matched = False
            for kind, rx in SENSITIVE_RULES:
                if rx.search(key_str):
                    hits.append({"path": path, "kind": kind})
                    matched = True
                    break
            
            # Recurse into nested structures
            if len(hits) < MAX_SENSITIVE_FIELDS:
                hits.extend(detect_sensitive_fields(v, path, max_depth - 1))
                
    elif isinstance(obj, list):
        # Only sample first few items of large lists
        sample_size = min(len(obj), 10)
        for i in range(sample_size):
            if len(hits) >= MAX_SENSITIVE_FIELDS:
                break
            path = f"{prefix}[{i}]"
            hits.extend(detect_sensitive_fields(obj[i], path, max_depth - 1))
    
    return hits[:MAX_SENSITIVE_FIELDS]


def build_sensitive_fields_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a summary of sensitive fields detected in the extraction result.
    
    Args:
        result: The full extraction result dict
        
    Returns:
        Dict with sensitive_fields_detected list and summary counts
    """
    hits = detect_sensitive_fields(result)
    
    # Group by kind for summary
    by_kind: Dict[str, int] = {}
    for hit in hits:
        kind = hit.get("kind", "other")
        by_kind[kind] = by_kind.get(kind, 0) + 1
    
    return {
        "sensitive_fields_detected": hits,
        "sensitive_fields_count": len(hits),
        "sensitive_fields_by_kind": by_kind,
        "truncated": len(hits) >= MAX_SENSITIVE_FIELDS,
    }


# ============================================================================
# Shadow Mode Infrastructure
# ============================================================================

# Environment variable controls
SHADOW_IMAGE_MASTER_ENABLED = os.environ.get("IMAGE_MVP_SHADOW_IMAGE_MASTER", "0") == "1"
SHADOW_SAMPLE_PCT = int(os.environ.get("IMAGE_MVP_SHADOW_SAMPLE_PCT", "100"))
SHADOW_TIMEOUT_SECONDS = float(os.environ.get("IMAGE_MVP_SHADOW_TIMEOUT", "2.0"))


def flatten_dict(obj: Any, prefix: str = "") -> Dict[str, Any]:
    """
    Flatten a nested dict/list structure to path -> value mapping.
    
    Args:
        obj: The object to flatten
        prefix: Current path prefix
        
    Returns:
        Dict mapping dotted paths to leaf values
    """
    out: Dict[str, Any] = {}
    
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Skip internal keys
            if str(k).startswith("_"):
                continue
            p = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten_dict(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            out.update(flatten_dict(v, p))
    else:
        out[prefix] = obj
        
    return out


def diff_extraction_results(
    main_result: Dict[str, Any],
    shadow_result: Dict[str, Any],
    limit: int = MAX_DIFF_ENTRIES
) -> Dict[str, Any]:
    """
    Compute a diff between main extraction result and shadow result.
    
    Returns a summary suitable for inclusion in extraction_info.
    
    Args:
        main_result: The primary extraction result
        shadow_result: The shadow module extraction result
        limit: Maximum number of entries per diff category
        
    Returns:
        Dict with added_keys, removed_keys, changed_keys counts and samples
    """
    # Flatten both results for comparison
    # Exclude extraction_info and performance to avoid noise
    def filter_for_diff(d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in d.items() 
                if k not in ("extraction_info", "performance", "_locked")}
    
    fa = flatten_dict(filter_for_diff(main_result or {}))
    fb = flatten_dict(filter_for_diff(shadow_result or {}))
    
    ka = set(fa.keys())
    kb = set(fb.keys())
    
    added = sorted(list(kb - ka))[:limit]
    removed = sorted(list(ka - kb))[:limit]
    
    changed: List[str] = []
    for k in sorted(list(ka & kb)):
        if fa[k] != fb[k]:
            changed.append(k)
            if len(changed) >= limit:
                break
    
    return {
        "added_keys": added,
        "added_keys_count": len(kb - ka),
        "removed_keys": removed,
        "removed_keys_count": len(ka - kb),
        "changed_keys": changed,
        "changed_keys_count": len(changed),
        "main_total_keys": len(ka),
        "shadow_total_keys": len(kb),
    }


def should_run_shadow() -> bool:
    """
    Determine if shadow mode should run for this request.
    
    Respects sampling percentage to control overhead.
    Uses per-request randomness (not seeded once at import).
    """
    if not SHADOW_IMAGE_MASTER_ENABLED:
        return False
    
    if SHADOW_SAMPLE_PCT >= 100:
        return True
    
    if SHADOW_SAMPLE_PCT <= 0:
        return False
    
    # Use SystemRandom for per-request randomness (not affected by global seed)
    return random.SystemRandom().randint(1, 100) <= SHADOW_SAMPLE_PCT


def run_shadow_extraction_safe(
    filepath: str,
    timeout: float = SHADOW_TIMEOUT_SECONDS
) -> Dict[str, Any]:
    """
    Run image_master extraction in shadow mode with timeout and error isolation.
    
    This function NEVER raises exceptions - all errors are captured in the result.
    
    Args:
        filepath: Path to the file to extract
        timeout: Maximum time to allow for shadow extraction
        
    Returns:
        Dict with shadow extraction results or error info
    """
    import concurrent.futures
    
    shadow_info: Dict[str, Any] = {
        "enabled": True,
        "duration_seconds": 0.0,
        "error": None,
        "diff": None,
    }
    
    start_time = time.time()
    
    try:
        # Import image_master dynamically to avoid import errors at module load
        from .modules.image_master import extract_image_master
        
        # Run with timeout using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(extract_image_master, filepath)
            try:
                result = future.result(timeout=timeout)
                shadow_info["duration_seconds"] = time.time() - start_time
                shadow_info["result"] = result
            except concurrent.futures.TimeoutError:
                shadow_info["duration_seconds"] = timeout
                shadow_info["error"] = f"Shadow extraction timed out after {timeout}s"
                logger.warning(f"Shadow image_master timed out for {filepath}")
                
    except ImportError as e:
        shadow_info["duration_seconds"] = time.time() - start_time
        shadow_info["error"] = f"image_master not available: {e}"
        logger.debug(f"image_master import failed: {e}")
        
    except Exception as e:
        shadow_info["duration_seconds"] = time.time() - start_time
        shadow_info["error"] = f"Shadow extraction failed: {type(e).__name__}: {e}"
        logger.warning(f"Shadow image_master failed for {filepath}: {e}")
    
    return shadow_info


def build_shadow_summary(
    shadow_info: Dict[str, Any],
    main_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build a summary of shadow mode results for extraction_info.
    
    The full shadow result is NOT included - only diff summary and metadata.
    
    Args:
        shadow_info: Result from run_shadow_extraction_safe
        main_result: The main extraction result for diff comparison
        
    Returns:
        Dict suitable for extraction_info.shadow.image_master
    """
    summary: Dict[str, Any] = {
        "enabled": shadow_info.get("enabled", False),
        "duration_seconds": shadow_info.get("duration_seconds", 0.0),
        "error": shadow_info.get("error"),
    }
    
    # Compute diff if we have both results
    shadow_result = shadow_info.get("result")
    if shadow_result and main_result and not shadow_info.get("error"):
        diff = diff_extraction_results(main_result, shadow_result)
        summary["diff"] = {
            "added_keys_count": diff["added_keys_count"],
            "removed_keys_count": diff["removed_keys_count"],
            "changed_keys_count": diff["changed_keys_count"],
            "main_total_keys": diff["main_total_keys"],
            "shadow_total_keys": diff["shadow_total_keys"],
            # Include sample PATHS only for debugging (never raw values - security invariant)
            "added_keys_sample": diff["added_keys"][:MAX_SAMPLE_KEYS],
            "changed_keys_sample": diff["changed_keys"][:MAX_SAMPLE_KEYS],
        }
        
        # Log diff summary to stderr if enabled
        # SECURITY: Log only paths and counts, NEVER raw values
        if os.environ.get("IMAGE_MVP_SHADOW_LOG_DIFF", "0") == "1":
            logger.info(f"Shadow diff: "
                       f"added={diff['added_keys_count']}, "
                       f"removed={diff['removed_keys_count']}, "
                       f"changed={diff['changed_keys_count']}")
    
    return summary


# ============================================================================
# Main Integration Function
# ============================================================================

def add_observability_to_result(
    result: Dict[str, Any],
    provenance: Dict[str, str],
    conflicts: List[Dict[str, str]],
    shadow_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add all observability data to the extraction result's extraction_info.
    
    This is the main integration point - call this at the end of extraction
    to add provenance, sensitive field detection, and shadow mode results.
    
    Args:
        result: The main extraction result (mutated in place)
        provenance: Module provenance dict from record_top_level_provenance calls
        conflicts: Provenance conflicts list
        shadow_info: Optional shadow mode results
        
    Returns:
        The modified result dict
    """
    if "extraction_info" not in result:
        result["extraction_info"] = {}
    
    # Add observability version for schema evolution
    result["extraction_info"]["observability_version"] = OBSERVABILITY_VERSION
    
    # Add provenance tracking
    result["extraction_info"]["provenance"] = build_provenance_summary(provenance, conflicts)
    
    # Add sensitive field detection
    result["extraction_info"]["sensitive_fields"] = build_sensitive_fields_summary(result)
    
    # Add shadow mode results if available
    if shadow_info:
        if "shadow" not in result["extraction_info"]:
            result["extraction_info"]["shadow"] = {}
        result["extraction_info"]["shadow"]["image_master"] = build_shadow_summary(
            shadow_info, result
        )
    else:
        # Record that shadow mode was not enabled
        if "shadow" not in result["extraction_info"]:
            result["extraction_info"]["shadow"] = {}
        result["extraction_info"]["shadow"]["image_master"] = {
            "enabled": False,
            "reason": "not_enabled" if not SHADOW_IMAGE_MASTER_ENABLED else "not_sampled",
        }
    
    return result
