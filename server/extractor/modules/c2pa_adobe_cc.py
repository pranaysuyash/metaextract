"""
C2PA/JUMBF and Adobe Content Credentials Parsing
Extracts content authenticity and provenance metadata from JUMBF boxes and Adobe CC structures.
"""

import json
import struct
from typing import Dict, Any, Optional, List
from pathlib import Path


# C2PA Allowlist - critical fields only (avoid PII/PHI)
C2PA_ALLOWLIST = {
    "manifest_version": "c2pa_manifest_version",
    "claim_generator": "c2pa_claim_generator",
    "claim_generator_version": "c2pa_claim_generator_version",
    "software_agent": "c2pa_software_agent",
    "signature_valid": "c2pa_signature_valid",
    "signature_algorithm": "c2pa_signature_algorithm",
    "timestamp": "c2pa_timestamp",
    "assertions_count": "c2pa_assertions_count",
    "assertion_types": "c2pa_assertion_types",
    "ingredients_count": "c2pa_ingredients_count",
    "actions_count": "c2pa_actions_count",
    "actions_types": "c2pa_actions_types",
    "has_credentials": "c2pa_has_credentials",
    "data_hash_algorithm": "c2pa_data_hash_algorithm",
    "box_hash": "c2pa_box_hash",
    "hard_binding": "c2pa_hard_binding",
    "soft_binding": "c2pa_soft_binding",
    "update_manifest": "c2pa_update_manifest",
    "redacted_fields": "c2pa_redacted_fields",
}

# Adobe Content Credentials Allowlist
ADOBE_CC_ALLOWLIST = {
    "cc_present": "adobe_cc_present",
    "cc_version": "adobe_cc_version",
    "claim_generator": "adobe_cc_claim_generator",
    "signature_valid": "adobe_cc_signature_valid",
    "actions_count": "adobe_cc_actions_count",
    "ingredients_count": "adobe_cc_ingredients_count",
    "timestamp": "adobe_cc_timestamp",
    "validation_status": "adobe_cc_validation_status",
    "content_binding": "adobe_cc_content_binding",
    "has_assertions": "adobe_cc_has_assertions",
    "assertion_types": "adobe_cc_assertion_types",
}


def parse_c2pa_manifest(jumbf_data: bytes) -> Dict[str, Any]:
    """
    Parse C2PA manifest from JUMBF box.

    Args:
        jumbf_data: Raw JUMBF box data

    Returns:
        Dictionary with C2PA metadata (allowlisted fields only)
    """
    result = {
        "c2pa_detected": False,
        "c2pa_fields": {},
        "error": None
    }

    try:
        # Try to parse as JSON (C2PA manifests are typically JSON)
        manifest_json = json.loads(jumbf_data.decode('utf-8', errors='ignore'))

        result["c2pa_detected"] = True

        # Extract allowlisted fields from manifest
        if "manifest_version" in manifest_json:
            result["c2pa_fields"]["c2pa_manifest_version"] = manifest_json["manifest_version"]

        if "claim_generator" in manifest_json:
            cg = manifest_json["claim_generator"]
            if isinstance(cg, dict):
                if "title" in cg:
                    result["c2pa_fields"]["c2pa_claim_generator"] = cg["title"]
                if "version" in cg:
                    result["c2pa_fields"]["c2pa_claim_generator_version"] = cg["version"]
            else:
                result["c2pa_fields"]["c2pa_claim_generator"] = str(cg)

        if "signature" in manifest_json:
            sig = manifest_json["signature"]
            if isinstance(sig, dict):
                if "alg" in sig:
                    result["c2pa_fields"]["c2pa_signature_algorithm"] = sig["alg"]
                result["c2pa_fields"]["c2pa_signature_valid"] = True
            else:
                result["c2pa_fields"]["c2pa_signature_valid"] = False

        if "timestamp" in manifest_json:
            result["c2pa_fields"]["c2pa_timestamp"] = manifest_json["timestamp"]

        if "assertions" in manifest_json:
            assertions = manifest_json["assertions"]
            if isinstance(assertions, list):
                result["c2pa_fields"]["c2pa_assertions_count"] = len(assertions)
                assertion_types = set()
                for assertion in assertions:
                    if isinstance(assertion, dict) and "label" in assertion:
                        assertion_types.add(assertion["label"])
                if assertion_types:
                    result["c2pa_fields"]["c2pa_assertion_types"] = list(assertion_types)

        if "ingredients" in manifest_json:
            ingredients = manifest_json["ingredients"]
            if isinstance(ingredients, list):
                result["c2pa_fields"]["c2pa_ingredients_count"] = len(ingredients)

        if "actions" in manifest_json:
            actions = manifest_json["actions"]
            if isinstance(actions, list):
                result["c2pa_fields"]["c2pa_actions_count"] = len(actions)
                action_types = set()
                for action in actions:
                    if isinstance(action, dict) and "action" in action:
                        action_types.add(action["action"])
                if action_types:
                    result["c2pa_fields"]["c2pa_actions_types"] = list(action_types)

    except json.JSONDecodeError:
        result["error"] = "Failed to parse C2PA manifest as JSON"
    except Exception as e:
        result["error"] = f"C2PA parsing error: {str(e)}"

    return result


def parse_adobe_cc_manifest(cc_data: bytes) -> Dict[str, Any]:
    """
    Parse Adobe Content Credentials manifest.

    Args:
        cc_data: Raw Adobe CC manifest data

    Returns:
        Dictionary with Adobe CC metadata (allowlisted fields only)
    """
    result = {
        "adobe_cc_detected": False,
        "adobe_cc_fields": {},
        "error": None
    }

    try:
        # Try to parse as JSON
        manifest_json = json.loads(cc_data.decode('utf-8', errors='ignore'))

        result["adobe_cc_detected"] = True

        if "version" in manifest_json:
            result["adobe_cc_fields"]["adobe_cc_version"] = manifest_json["version"]

        if "claim_generator" in manifest_json:
            cg = manifest_json["claim_generator"]
            if isinstance(cg, dict) and "title" in cg:
                result["adobe_cc_fields"]["adobe_cc_claim_generator"] = cg["title"]
            else:
                result["adobe_cc_fields"]["adobe_cc_claim_generator"] = str(cg)

        if "timestamp" in manifest_json:
            result["adobe_cc_fields"]["adobe_cc_timestamp"] = manifest_json["timestamp"]

        if "actions" in manifest_json:
            actions = manifest_json["actions"]
            if isinstance(actions, list):
                result["adobe_cc_fields"]["adobe_cc_actions_count"] = len(actions)
                action_types = set()
                for action in actions:
                    if isinstance(action, dict) and "action" in action:
                        action_types.add(action["action"])
                if action_types:
                    result["adobe_cc_fields"]["adobe_cc_assertion_types"] = list(action_types)

        if "ingredients" in manifest_json:
            ingredients = manifest_json["ingredients"]
            if isinstance(ingredients, list):
                result["adobe_cc_fields"]["adobe_cc_ingredients_count"] = len(ingredients)

        result["adobe_cc_fields"]["adobe_cc_present"] = True

    except json.JSONDecodeError:
        result["error"] = "Failed to parse Adobe CC manifest as JSON"
    except Exception as e:
        result["error"] = f"Adobe CC parsing error: {str(e)}"

    return result


def find_jumbf_boxes(filepath: str) -> Dict[str, Any]:
    """
    Search for JUMBF boxes in image/video file.
    JUMBF = JPEG Universal Media Box Format (ISO/IEC 19566-5)

    Args:
        filepath: Path to media file

    Returns:
        Dictionary with C2PA/Adobe CC metadata found
    """
    result = {
        "jumbf_found": False,
        "c2pa": {},
        "adobe_cc": {},
        "fields_extracted": 0
    }

    try:
        with open(filepath, 'rb') as f:
            data = f.read()

        # JUMBF box signature: 0x6A756D62 ("jumb")
        jumb_signature = b'jumb'
        pos = 0

        while pos < len(data):
            # Search for JUMBF box
            idx = data.find(jumb_signature, pos)
            if idx == -1:
                break

            result["jumbf_found"] = True

            # Read box size (4 bytes before signature)
            if idx >= 4:
                try:
                    box_size = struct.unpack('>I', data[idx-4:idx])[0]
                    if box_size < 8:
                        pos = idx + 4
                        continue

                    # Extract box data
                    box_end = min(idx + box_size, len(data))
                    box_data = data[idx:box_end]

                    # Look for C2PA or Adobe CC markers
                    if b'c2pa' in box_data:
                        # Extract manifest region (simplified - look for JSON structures)
                        json_start = box_data.find(b'{')
                        if json_start != -1:
                            json_end = box_data.rfind(b'}')
                            if json_end > json_start:
                                manifest_data = box_data[json_start:json_end+1]
                                c2pa_result = parse_c2pa_manifest(manifest_data)
                                result["c2pa"] = c2pa_result
                                result["fields_extracted"] += len(c2pa_result.get("c2pa_fields", {}))

                    elif b'adobe' in box_data or b'cc' in box_data:
                        json_start = box_data.find(b'{')
                        if json_start != -1:
                            json_end = box_data.rfind(b'}')
                            if json_end > json_start:
                                manifest_data = box_data[json_start:json_end+1]
                                adobe_result = parse_adobe_cc_manifest(manifest_data)
                                result["adobe_cc"] = adobe_result
                                result["fields_extracted"] += len(adobe_result.get("adobe_cc_fields", {}))

                    pos = box_end

                except struct.error:
                    pos = idx + 4
            else:
                pos = idx + 4

    except Exception as e:
        result["error"] = f"JUMBF box search error: {str(e)}"

    return result


def extract_c2pa_adobe_credentials(filepath: str) -> Dict[str, Any]:
    """
    Main function to extract C2PA and Adobe Content Credentials metadata.

    Args:
        filepath: Path to media file

    Returns:
        Dictionary with all extracted credentials metadata
    """
    result = {
        "c2pa_adobe_credentials": {
            "c2pa": {},
            "adobe_cc": {},
            "jumbf_present": False
        },
        "fields_extracted": 0,
        "error": None
    }

    try:
        jumbf_result = find_jumbf_boxes(filepath)

        result["c2pa_adobe_credentials"]["jumbf_present"] = jumbf_result.get("jumbf_found", False)

        if jumbf_result.get("c2pa"):
            result["c2pa_adobe_credentials"]["c2pa"] = jumbf_result["c2pa"]

        if jumbf_result.get("adobe_cc"):
            result["c2pa_adobe_credentials"]["adobe_cc"] = jumbf_result["adobe_cc"]

        result["fields_extracted"] = jumbf_result.get("fields_extracted", 0)

    except Exception as e:
        result["error"] = str(e)

    return result


def get_c2pa_adobe_field_count() -> int:
    """Return count of C2PA/Adobe CC fields."""
    return len(C2PA_ALLOWLIST) + len(ADOBE_CC_ALLOWLIST)
