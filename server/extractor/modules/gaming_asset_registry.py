
"""
Gaming Asset Registry
Comprehensive registry of Game Development and 3D Asset metadata.
Includes Unity meta files, Unreal Engine assets (.uasset), glTF/GLB, FBX, and texture metadata.
Target: ~3,000 fields
"""

from __future__ import annotations

import json
import os
import struct
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Dict, List

FALLBACK_GAMING_FIELDS: List[str] = [
    "gltf.asset.version",
    "gltf.asset.generator",
    "gltf.asset.copyright",
    "gltf.scene.count",
    "gltf.node.count",
    "gltf.mesh.count",
    "gltf.primitive.count",
    "gltf.material.count",
    "gltf.texture.count",
    "gltf.image.count",
    "gltf.sampler.count",
    "gltf.buffer.count",
    "gltf.bufferview.count",
    "gltf.accessor.count",
    "gltf.animation.count",
    "gltf.skin.count",
    "gltf.camera.count",
    "gltf.extensions_used",
    "gltf.extensions_required",
    "unity.meta.file_format_version",
    "unity.meta.guid",
    "unity.meta.time_created",
    "unity.meta.license_type",
]


@lru_cache(maxsize=1)
def _load_gaming_inventory_fields() -> List[str]:
    root = Path(__file__).resolve().parents[3]
    inventory_path = root / "scripts" / "inventory_gaming.py"
    if inventory_path.exists():
        try:
            spec = spec_from_file_location("inventory_gaming", inventory_path)
            if spec and spec.loader:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "generate_gaming_inventory"):
                    inventory = module.generate_gaming_inventory()
                else:
                    inventory = getattr(module, "INVENTORY", None)
                if isinstance(inventory, dict):
                    fields: List[str] = []
                    for category in inventory.get("categories", {}).values():
                        for field in category.get("fields", []) or []:
                            fields.append(str(field))
                    if fields:
                        return sorted(set(fields))
        except Exception:
            pass
    return list(FALLBACK_GAMING_FIELDS)


def get_gaming_asset_registry_fields() -> List[str]:
    return _load_gaming_inventory_fields()


def get_gaming_asset_registry_field_count() -> int:
    fields = get_gaming_asset_registry_fields()
    return len(fields) if fields else 3000


def extract_gaming_asset_registry_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract gaming_asset_registry metadata from files'''
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
        "is_valid_gaming_asset_registry": False,
        "extraction_method": "format_scan",
        "registry": registry,
    }

    try:
        if not filepath or not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        def _add_value(key: str, value: Any) -> None:
            if value is None:
                return
            metadata[key] = value
            registry["tags"][key] = {"name": key, "value": value}

        ext = Path(filepath).suffix.lower()

        try:
            if ext == ".gltf":
                with open(filepath, "r", encoding="utf-8", errors="ignore") as handle:
                    gltf_data = json.load(handle)
                _extract_gltf_json(gltf_data, _add_value)
                _add_value("gaming_asset_type", "gltf")
                registry["available"] = True

            elif ext == ".glb":
                gltf_data = _read_glb_json(filepath)
                if gltf_data:
                    _extract_gltf_json(gltf_data, _add_value)
                    _add_value("gaming_asset_type", "glb")
                    registry["available"] = True

            elif ext == ".meta":
                unity_metadata = _parse_unity_meta(filepath)
                for key, value in unity_metadata.items():
                    _add_value(f"unity.meta.{key}", value)
                _add_value("gaming_asset_type", "unity_meta")
                registry["available"] = True

            elif ext == ".fbx":
                fbx_metadata = _parse_fbx_header(filepath)
                for key, value in fbx_metadata.items():
                    _add_value(f"fbx.{key}", value)
                _add_value("gaming_asset_type", "fbx")
                registry["available"] = True

            elif ext == ".uasset":
                _add_value("gaming_asset_type", "unreal_uasset")
                registry["available"] = True

            if registry["available"]:
                result["is_valid_gaming_asset_registry"] = True
                registry["fields_extracted"] = len(registry["tags"])
                result["fields_extracted"] = len(metadata)
        except Exception as e:
            result["error"] = f"gaming_asset_registry extraction failed: {str(e)[:200]}"

    except Exception as e:
        result["error"] = f"gaming_asset_registry metadata extraction failed: {str(e)[:200]}"

    return result


def _extract_gltf_json(gltf_data: Dict[str, Any], add_value) -> None:
    asset = gltf_data.get("asset", {}) if isinstance(gltf_data, dict) else {}
    add_value("gltf.asset.version", asset.get("version"))
    add_value("gltf.asset.generator", asset.get("generator"))
    add_value("gltf.asset.copyright", asset.get("copyright"))

    def _count_list(key: str) -> int:
        value = gltf_data.get(key, [])
        return len(value) if isinstance(value, list) else 0

    add_value("gltf.scene.count", _count_list("scenes"))
    add_value("gltf.node.count", _count_list("nodes"))
    add_value("gltf.mesh.count", _count_list("meshes"))
    add_value("gltf.material.count", _count_list("materials"))
    add_value("gltf.texture.count", _count_list("textures"))
    add_value("gltf.image.count", _count_list("images"))
    add_value("gltf.sampler.count", _count_list("samplers"))
    add_value("gltf.buffer.count", _count_list("buffers"))
    add_value("gltf.bufferview.count", _count_list("bufferViews"))
    add_value("gltf.accessor.count", _count_list("accessors"))
    add_value("gltf.animation.count", _count_list("animations"))
    add_value("gltf.skin.count", _count_list("skins"))
    add_value("gltf.camera.count", _count_list("cameras"))

    primitive_count = 0
    attribute_keys: List[str] = []
    for mesh in gltf_data.get("meshes", []) if isinstance(gltf_data, dict) else []:
        for primitive in mesh.get("primitives", []) if isinstance(mesh, dict) else []:
            primitive_count += 1
            attrs = primitive.get("attributes", {}) if isinstance(primitive, dict) else {}
            if isinstance(attrs, dict):
                attribute_keys.extend(list(attrs.keys()))
    if attribute_keys:
        add_value("gltf.attribute.keys", sorted(set(attribute_keys))[:200])
    add_value("gltf.primitive.count", primitive_count)

    extensions_used = gltf_data.get("extensionsUsed")
    if isinstance(extensions_used, list):
        add_value("gltf.extensions_used", extensions_used)
    extensions_required = gltf_data.get("extensionsRequired")
    if isinstance(extensions_required, list):
        add_value("gltf.extensions_required", extensions_required)


def _read_glb_json(filepath: str) -> Dict[str, Any] | None:
    try:
        with open(filepath, "rb") as handle:
            header = handle.read(12)
            if len(header) < 12 or header[0:4] != b"glTF":
                return None
            chunk_header = handle.read(8)
            if len(chunk_header) < 8:
                return None
            chunk_length, chunk_type = struct.unpack("<I4s", chunk_header)
            if chunk_type != b"JSON":
                return None
            json_bytes = handle.read(chunk_length)
        return json.loads(json_bytes.decode("utf-8", errors="ignore"))
    except Exception:
        return None


def _parse_unity_meta(filepath: str) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as handle:
            lines = handle.readlines()
    except Exception:
        return metadata

    stack: List[tuple[int, str]] = []
    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path_parts = [entry[1] for entry in stack] + [key]
        full_key = ".".join(path_parts)
        if value:
            metadata[full_key] = value
        stack.append((indent, key))
    return metadata


def _parse_fbx_header(filepath: str) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    try:
        with open(filepath, "rb") as handle:
            header = handle.read(27)
        if header.startswith(b"Kaydara FBX Binary"):
            if len(header) >= 27:
                version = struct.unpack("<I", header[23:27])[0]
                metadata["format"] = "binary"
                metadata["version"] = version
        else:
            metadata["format"] = "ascii"
    except Exception:
        return metadata
    return metadata
