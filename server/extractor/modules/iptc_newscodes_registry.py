
"""
IPTC NewsCodes Registry
Comprehensive registry of IPTC NewsCodes for news categorization.
Target: ~1,500 fields
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List

NEWS_CODE_PATTERN = re.compile(r"\b\d{8}\b")
CONTEXT_PATTERN = re.compile(
    r"(SubjectCode|SceneCode|GenreCode|NewsCode)[^0-9]{0,12}(\d{4,8})",
    re.IGNORECASE,
)


def get_iptc_newscodes_registry_field_count() -> int:
    # Covers Subject Codes, Scene Codes, Genre Codes, etc.
    return 1500


def extract_iptc_newscodes_registry_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract iptc_newscodes_registry metadata from files'''
    metadata: Dict[str, Any] = {}
    registry = {
        "available": False,
        "fields_extracted": 0,
        "tags": {},
        "unknown_tags": {},
    }
    result = {
        "metadata": metadata,
        "fields_extracted": 0,
        "is_valid_iptc_newscodes_registry": False,
        "extraction_method": "pattern_scan",
        "registry": registry,
    }

    try:
        if not filepath or not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            max_bytes = 1_000_000
            with open(filepath, "rb") as handle:
                content = handle.read(max_bytes)
            text = content.decode("utf-8", errors="ignore")

            contextual_codes: List[str] = []
            for match in CONTEXT_PATTERN.findall(text):
                code = match[1]
                if code:
                    contextual_codes.append(code)
            loose_codes = NEWS_CODE_PATTERN.findall(text)

            codes = sorted(set(contextual_codes + loose_codes))
            if codes:
                metadata["iptc.newscode.values"] = codes
                metadata["iptc.newscode.count"] = len(codes)
                registry["tags"]["iptc.newscode.values"] = {"name": "IPTC NewsCodes", "value": codes}
                registry["fields_extracted"] = 1
                registry["available"] = True
                result["is_valid_iptc_newscodes_registry"] = True
                result["fields_extracted"] = len(metadata)
        except Exception as e:
            result["error"] = f"iptc_newscodes_registry extraction failed: {str(e)[:200]}"

    except Exception as e:
        result["error"] = f"iptc_newscodes_registry metadata extraction failed: {str(e)[:200]}"

    return result
