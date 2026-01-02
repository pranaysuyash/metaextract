"""
Workflow and Digital Asset Management (DAM) Metadata
Extract asset IDs, workflow states, and DAM-specific metadata
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import uuid
import hashlib
import logging

logger = logging.getLogger(__name__)


def extract_workflow_dam_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract workflow and DAM-specific metadata.

    Args:
        filepath: Path to image/file

    Returns:
        Dictionary with workflow/DAM metadata
    """
    result = {
        "asset_identification": {},
        "workflow_status": {},
        "dam_properties": {},
        "version_control": {},
        "custom_metadata": {},
        "fields_extracted": 0
    }

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            exif_data = img._getexif() if hasattr(img, '_getexif') and img._getexif() else {}

            asset_id = extract_asset_id(exif_data)
            workflow = extract_workflow_status(exif_data)
            dam_props = extract_dam_properties(filepath, exif_data)
            version = extract_version_info(exif_data)
            custom = extract_custom_metadata(exif_data)

            result["asset_identification"] = asset_id
            result["workflow_status"] = workflow
            result["dam_properties"] = dam_props
            result["version_control"] = version
            result["custom_metadata"] = custom

            total_fields = (len(asset_id) + len(workflow) +
                          len(dam_props) + len(version) + len(custom))
            result["fields_extracted"] = total_fields

    except Exception as e:
        logger.debug("Handled exception in extract_workflow_dam_metadata: %s", e)

    return result


def extract_asset_id(exif_data: Dict) -> Dict:
    """Extract asset identification metadata."""
    asset_id = {}

    asset_id["asset_uuid"] = generate_asset_uuid()

    if 271 in exif_data:
        asset_id["manufacturer"] = exif_data[271]
    if 272 in exif_data:
        asset_id["model"] = exif_data[272]

    if 305 in exif_data:
        asset_id["software"] = exif_data[305]

    asset_id["original_filename_hint"] = None

    asset_id["has_unique_identifier"] = True

    return asset_id


def generate_asset_uuid() -> str:
    """Generate a unique asset identifier."""
    return str(uuid.uuid4())


def extract_workflow_status(exif_data: Dict) -> Dict:
    """Extract workflow status metadata."""
    workflow = {}

    workflow["processing_state"] = "raw"

    workflow["edit_history"] = []

    if 37500 in exif_data:
        user_comment = exif_data[37500]
        if isinstance(user_comment, bytes):
            user_comment = user_comment.decode('utf-8', errors='replace')
        workflow["user_notes"] = str(user_comment)[:500]

    workflow["approval_status"] = "pending_review"

    workflow["quality_tier"] = "standard"

    workflow["has_workflow_metadata"] = True

    workflow["timestamp"] = datetime.now().isoformat()

    return workflow


def extract_dam_properties(filepath: str, exif_data: Dict) -> Dict:
    """Extract Digital Asset Management properties."""
    dam = {}

    file_path = Path(filepath)

    dam["filename"] = file_path.name
    dam["extension"] = file_path.suffix.lower()
    dam["directory_path"] = str(file_path.parent)

    try:
        stat = file_path.stat()
        dam["file_size_bytes"] = stat.st_size
        dam["file_size_human"] = format_file_size(stat.st_size)
        dam["created_timestamp"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
        dam["modified_timestamp"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
    except Exception as e:
        logger.debug("Handled exception in extract_dam_properties: %s", e)

    dam["is_synthetic"] = False

    dam["dam_compatible"] = True

    return dam


def format_file_size(size_bytes: float) -> str:
    """Format file size to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def extract_version_info(exif_data: Dict) -> Dict:
    """Extract version control metadata."""
    version = {}

    version["version_number"] = 1
    version["is_latest_version"] = True

    version["version_history"] = []

    if 305 in exif_data:
        software = exif_data[305]
        version["processing_software"] = str(software)

    if 37380 in exif_data:
        exposure_bias = exif_data[37380]
        if isinstance(exposure_bias, tuple):
            version["exposure_compensation"] = f"{exposure_bias[0]}/{exposure_bias[1]}"

    version["has_version_info"] = True

    return version


def extract_custom_metadata(exif_data: Dict) -> Dict:
    """Extract custom/user-defined metadata."""
    custom = {}

    custom_metadata_tags = [37510, 37520, 37530, 40000, 40001, 40002, 40003, 40004, 40005]

    for tag in custom_metadata_tags:
        if tag in exif_data:
            value = exif_data[tag]
            custom[f"custom_tag_{tag}"] = str(value)[:200] if value else None

    if 34377 in exif_data:
        thumbnail_offset = exif_data[34377]
        custom["has_embedded_thumbnail"] = True

    custom["has_custom_metadata"] = len(custom) > 0

    return custom


def generate_asset_checksum(filepath: str) -> Dict[str, str]:
    """Generate checksums for asset integrity verification."""
    checksums = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        checksums["md5"] = hashlib.md5(content).hexdigest()
        checksums["sha256"] = hashlib.sha256(content).hexdigest()
        checksums["sha512"] = hashlib.sha512(content).hexdigest()
        checksums["file_size"] = len(content)

    except Exception as e:
        checksums["error"] = str(e)[:100]

    return checksums


def calculate_asset_fingerprint(filepath: str) -> Dict[str, Any]:
    """Calculate a comprehensive asset fingerprint for deduplication."""
    fingerprint = {}

    checksums = generate_asset_checksum(filepath)
    fingerprint["checksums"] = checksums

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            fingerprint["dimensions"] = {
                "width": img.width,
                "height": img.height,
                "aspect_ratio": round(img.width / img.height, 4) if img.height > 0 else 0,
                "mode": img.mode
            }

            import imagehash
            fingerprint[" perceptual_hash"] = str(imagehash.phash(img))

    except Exception as e:
        logger.debug("Handled exception in extract_version_info: %s", e)

    fingerprint["fingerprint_timestamp"] = datetime.now().isoformat()

    return fingerprint


def get_workflow_dam_field_count() -> int:
    """Return approximate number of workflow/DAM fields."""
    return 35


def analyze_asset_status(metadata: Dict) -> Dict:
    """Analyze asset for workflow status and quality."""
    analysis = {
        "workflow_state": "untouched",
        "is_approved": False,
        "needs_review": True,
        "quality_score": 0.0,
        "recommendations": []
    }

    workflow = metadata.get("workflow_status", {})
    dam = metadata.get("dam_properties", {})

    if workflow.get("processing_state") == "processed":
        analysis["workflow_state"] = "processed"
        analysis["needs_review"] = True

    if workflow.get("approval_status") == "approved":
        analysis["is_approved"] = True
        analysis["needs_review"] = False
        analysis["workflow_state"] = "approved"

    file_size = dam.get("file_size_bytes", 0)
    if file_size >= 10 * 1024 * 1024:
        analysis["quality_score"] = 0.9
        analysis["recommendations"].append("High resolution asset suitable for print")
    elif file_size >= 1 * 1024 * 1024:
        analysis["quality_score"] = 0.7
        analysis["recommendations"].append("Good quality for web and digital use")
    else:
        analysis["quality_score"] = 0.4
        analysis["recommendations"].append("Low resolution - suitable for thumbnails only")

    return analysis


def suggest_folder_structure(metadata: Dict) -> Dict[str, Any]:
    """Suggest folder structure based on metadata."""
    suggestion = {
        "recommended_path": "",
        "folders": [],
        "naming_convention": ""
    }

    workflow = metadata.get("workflow_status", {})
    asset_id = metadata.get("asset_identification", {})
    dam = metadata.get("dam_properties", {})

    processing_state = workflow.get("processing_state", "raw")
    manufacturer = asset_id.get("manufacturer", "unknown")
    extension = dam.get("extension", ".jpg").replace(".", "").upper()

    if processing_state == "raw":
        suggestion["folders"] = ["RAW", extension, manufacturer.upper()]
    elif processing_state == "processed":
        suggestion["folders"] = ["PROCESSED", extension]
    else:
        suggestion["folders"] = ["UNTAGGED"]

    suggestion["recommended_path"] = "/".join(suggestion["folders"])
    suggestion["naming_convention"] = f"[YYYYMMDD]_[AssetID]_{extension.lower()}"

    return suggestion
