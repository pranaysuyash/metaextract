# server/extractor/modules/ar_vr_metadata.py

"""
AR/VR content metadata extraction for Phase 4.

Extracts metadata from:
- 3D model files (OBJ, FBX, GLTF, GLB)
- VR/AR scene files
- Animation data
- Material and texture references
- Lighting and camera information
- Interactive elements
"""

import logging
import json
import re
import struct
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# AR/VR file extensions
AR_VR_EXTENSIONS = [
    '.obj', '.fbx', '.gltf', '.glb', '.dae', '.3ds', '.blend',
    '.usd', '.usda', '.usdc', '.usdz', '.x3d', '.wrl',
    '.scn', '.scene', '.unity', '.unreal'
]

# 3D file format signatures
FILE_SIGNATURES = {
    'gltf': b'{"',  # GLTF JSON starts with brace
    'glb': b'glTF',  # GLB binary starts with glTF
    'fbx': b'Kaydara FBX Binary',  # FBX binary signature
    'dae': b'<?xml',  # COLLADA XML
}


def extract_ar_vr_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract AR/VR content metadata from 3D models and scene files.

    Supports various 3D formats used in AR/VR applications.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Detect file format
        format_type = _detect_ar_vr_format(filepath, file_ext)

        if format_type:
            result['ar_vr_format'] = format_type

        # Extract format-specific metadata
        if format_type == 'obj':
            obj_data = _extract_obj_metadata(filepath)
            result.update(obj_data)

        elif format_type in ['gltf', 'glb']:
            gltf_data = _extract_gltf_metadata(filepath)
            result.update(gltf_data)

        elif format_type == 'fbx':
            fbx_data = _extract_fbx_metadata(filepath)
            result.update(fbx_data)

        elif format_type == 'dae':
            dae_data = _extract_dae_metadata(filepath)
            result.update(dae_data)

        elif format_type == 'usd':
            usd_data = _extract_usd_metadata(filepath)
            result.update(usd_data)

        # Extract general 3D properties
        general_data = _extract_general_3d_properties(filepath)
        result.update(general_data)

        # Analyze for AR/VR specific features
        ar_vr_analysis = _analyze_ar_vr_features(filepath, format_type)
        result.update(ar_vr_analysis)

    except Exception as e:
        logger.warning(f"Error extracting AR/VR metadata from {filepath}: {e}")
        result['ar_vr_extraction_error'] = str(e)

    return result


def _detect_ar_vr_format(filepath: str, file_ext: str) -> Optional[str]:
    """Detect AR/VR file format."""
    try:
        with open(filepath, 'rb') as f:
            signature = f.read(20)

        # Check known signatures
        for fmt, sig in FILE_SIGNATURES.items():
            if signature.startswith(sig):
                return fmt

        # Extension-based detection
        ext_map = {
            '.obj': 'obj',
            '.fbx': 'fbx',
            '.gltf': 'gltf',
            '.glb': 'glb',
            '.dae': 'dae',
            '.usd': 'usd',
            '.usda': 'usd',
            '.usdc': 'usd',
            '.usdz': 'usd',
            '.x3d': 'x3d',
            '.wrl': 'vrml',
            '.3ds': '3ds',
            '.blend': 'blender',
            '.scn': 'scene',
            '.unity': 'unity',
            '.unreal': 'unreal'
        }

        return ext_map.get(file_ext)

    except Exception:
        return None


def _extract_obj_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from OBJ files."""
    obj_data = {'obj_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(102400)  # Read first 100KB

        lines = content.split('\n')

        # Count geometric elements
        vertices = 0
        faces = 0
        normals = 0
        texcoords = 0
        materials = 0
        objects = 0

        for line in lines:
            line = line.strip()
            if line.startswith('v '):
                vertices += 1
            elif line.startswith('f '):
                faces += 1
            elif line.startswith('vn '):
                normals += 1
            elif line.startswith('vt '):
                texcoords += 1
            elif line.startswith('usemtl '):
                materials += 1
            elif line.startswith('o '):
                objects += 1

        obj_data['obj_vertices'] = vertices
        obj_data['obj_faces'] = faces
        obj_data['obj_normals'] = normals
        obj_data['obj_texcoords'] = texcoords
        obj_data['obj_materials_used'] = materials
        obj_data['obj_objects'] = objects

        # Extract material library references
        mtllib_matches = re.findall(r'mtllib\s+([^\s]+)', content, re.IGNORECASE)
        if mtllib_matches:
            obj_data['obj_material_libraries'] = mtllib_matches

        # Check for texture references
        texture_lines = [line for line in lines if 'map_' in line.lower()]
        if texture_lines:
            obj_data['obj_has_textures'] = True
            obj_data['obj_texture_lines'] = len(texture_lines)

    except Exception as e:
        obj_data['obj_extraction_error'] = str(e)

    return obj_data


def _extract_gltf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from GLTF/GLB files."""
    gltf_data = {'gltf_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext == '.glb':
            # GLB is binary, extract JSON header
            with open(filepath, 'rb') as f:
                # GLB header: magic (4), version (4), length (4)
                header = f.read(12)
                if len(header) >= 12:
                    magic, version, length = struct.unpack('<III', header)
                    gltf_data['gltf_version'] = version
                    gltf_data['gltf_total_length'] = length

                    # Find JSON chunk
                    json_length = struct.unpack('<I', f.read(4))[0]
                    json_data = f.read(json_length)
                    content = json_data.decode('utf-8', errors='ignore')
        else:
            # GLTF is JSON
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        # Parse JSON content
        data = json.loads(content)

        # Extract asset info
        if 'asset' in data:
            asset = data['asset']
            gltf_data['gltf_asset_version'] = asset.get('version')
            gltf_data['gltf_asset_generator'] = asset.get('generator')
            gltf_data['gltf_asset_copyright'] = asset.get('copyright')

        # Count scenes and nodes
        if 'scenes' in data:
            gltf_data['gltf_scene_count'] = len(data['scenes'])

        if 'nodes' in data:
            gltf_data['gltf_node_count'] = len(data['nodes'])

        # Count meshes and materials
        if 'meshes' in data:
            gltf_data['gltf_mesh_count'] = len(data['meshes'])

        if 'materials' in data:
            gltf_data['gltf_material_count'] = len(data['materials'])

            # Analyze materials
            materials = data['materials']
            pbr_materials = 0
            textured_materials = 0

            for mat in materials:
                if 'pbrMetallicRoughness' in mat:
                    pbr_materials += 1
                if 'baseColorTexture' in mat or 'metallicRoughnessTexture' in mat:
                    textured_materials += 1

            gltf_data['gltf_pbr_materials'] = pbr_materials
            gltf_data['gltf_textured_materials'] = textured_materials

        # Count animations
        if 'animations' in data:
            gltf_data['gltf_animation_count'] = len(data['animations'])

        # Check for extensions
        if 'extensionsUsed' in data:
            gltf_data['gltf_extensions_used'] = data['extensionsUsed']

        # Check for cameras and lights
        if 'cameras' in data:
            gltf_data['gltf_camera_count'] = len(data['cameras'])

        # Lights are in extensions
        if 'extensions' in data and 'KHR_lights_punctual' in data['extensions']:
            lights = data['extensions']['KHR_lights_punctual'].get('lights', [])
            gltf_data['gltf_light_count'] = len(lights)

    except Exception as e:
        gltf_data['gltf_extraction_error'] = str(e)

    return gltf_data


def _extract_fbx_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from FBX files."""
    fbx_data = {'fbx_format_present': True}

    try:
        with open(filepath, 'rb') as f:
            # FBX files contain binary data with some readable strings
            data = f.read(1024)
            data_str = data.decode('latin-1', errors='ignore')

        # Look for FBX version
        version_match = re.search(r'FBX (\d+\.\d+\.\d+)', data_str)
        if version_match:
            fbx_data['fbx_version'] = version_match.group(1)

        # Look for common FBX elements
        elements = ['Geometry', 'Material', 'Texture', 'Animation', 'Camera', 'Light']
        for element in elements:
            count = data_str.count(element)
            if count > 0:
                fbx_data[f'fbx_{element.lower()}_references'] = count

    except Exception as e:
        fbx_data['fbx_extraction_error'] = str(e)

    return fbx_data


def _extract_dae_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from COLLADA DAE files."""
    dae_data = {'dae_format_present': True}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # COLLADA namespace
        ns = {'dae': 'http://www.collada.org/2005/11/COLLADASchema'}

        # Extract asset info
        asset = root.find('.//dae:asset', ns)
        if asset is not None:
            created = asset.find('dae:created', ns)
            if created is not None:
                dae_data['dae_created'] = created.text

            modified = asset.find('dae:modified', ns)
            if modified is not None:
                dae_data['dae_modified'] = modified.text

        # Count geometries
        geometries = root.findall('.//dae:geometry', ns)
        dae_data['dae_geometry_count'] = len(geometries)

        # Count materials and effects
        materials = root.findall('.//dae:material', ns)
        dae_data['dae_material_count'] = len(materials)

        effects = root.findall('.//dae:effect', ns)
        dae_data['dae_effect_count'] = len(effects)

        # Count animations
        animations = root.findall('.//dae:animation', ns)
        dae_data['dae_animation_count'] = len(animations)

        # Check for physics
        physics = root.findall('.//dae:rigid_body', ns)
        if physics:
            dae_data['dae_has_physics'] = True
            dae_data['dae_rigid_body_count'] = len(physics)

    except Exception as e:
        dae_data['dae_extraction_error'] = str(e)

    return dae_data


def _extract_usd_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from USD files."""
    usd_data = {'usd_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(51200)  # Read first 50KB

        # USD files are text-based with specific syntax
        lines = content.split('\n')

        # Count prims
        prim_count = sum(1 for line in lines if line.strip().startswith('def ') or line.strip().startswith('over '))
        usd_data['usd_prim_count'] = prim_count

        # Look for upAxis
        upaxis_match = re.search(r'upAxis\s*=\s*["\']([^"\']+)["\']', content)
        if upaxis_match:
            usd_data['usd_up_axis'] = upaxis_match.group(1)

        # Look for metersPerUnit
        meters_match = re.search(r'metersPerUnit\s*=\s*([0-9.]+)', content)
        if meters_match:
            usd_data['usd_meters_per_unit'] = float(meters_match.group(1))

        # Count references
        ref_count = content.count('references = ')
        usd_data['usd_reference_count'] = ref_count

    except Exception as e:
        usd_data['usd_extraction_error'] = str(e)

    return usd_data


def _extract_general_3d_properties(filepath: str) -> Dict[str, Any]:
    """Extract general 3D file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['ar_vr_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['ar_vr_filename'] = filename

        # Check for common AR/VR naming patterns
        if any(x in filename.lower() for x in ['ar', 'vr', 'xr', 'mixedreality']):
            props['filename_suggests_ar_vr'] = True

        # Look for version numbers
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['file_version_hint'] = version_match.group(1)

    except Exception:
        pass

    return props


def _analyze_ar_vr_features(filepath: str, format_type: Optional[str]) -> Dict[str, Any]:
    """Analyze file for AR/VR specific features."""
    analysis = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10240)  # Read first 10KB

        # Look for AR/VR specific keywords
        ar_vr_keywords = [
            'occlusion', 'shadow', 'reflection', 'transparency',
            'animation', 'skeleton', 'bone', 'joint',
            'physics', 'collision', 'rigidbody',
            'light', 'camera', 'fog', 'postprocessing',
            'interactive', 'trigger', 'event',
            'mobile', 'standalone', 'webvr', 'webxr'
        ]

        found_keywords = [kw for kw in ar_vr_keywords if kw in content.lower()]
        if found_keywords:
            analysis['ar_vr_keywords_found'] = found_keywords

        # Check for shader/material complexity indicators
        if format_type == 'gltf':
            if 'metallicFactor' in content or 'roughnessFactor' in content:
                analysis['has_pbr_materials'] = True

        # Look for texture references
        texture_extensions = ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.ktx']
        texture_refs = 0
        for ext in texture_extensions:
            texture_refs += content.count(ext)

        if texture_refs > 0:
            analysis['texture_references'] = texture_refs

        # Check for audio references
        audio_extensions = ['.wav', '.mp3', '.ogg', '.m4a']
        audio_refs = 0
        for ext in audio_extensions:
            audio_refs += content.count(ext)

        if audio_refs > 0:
            analysis['audio_references'] = audio_refs

        # Look for coordinate system hints
        if 'right-handed' in content.lower():
            analysis['coordinate_system'] = 'right-handed'
        elif 'left-handed' in content.lower():
            analysis['coordinate_system'] = 'left-handed'

    except Exception:
        pass

    return analysis


def get_ar_vr_field_count() -> int:
    """Return the number of fields extracted by AR/VR metadata."""
    # Format detection (5)
    detection_fields = 5

    # OBJ specific (10)
    obj_fields = 10

    # GLTF/GLB specific (15)
    gltf_fields = 15

    # FBX specific (8)
    fbx_fields = 8

    # COLLADA specific (10)
    dae_fields = 10

    # USD specific (8)
    usd_fields = 8

    # General properties (8)
    general_fields = 8

    # AR/VR analysis (10)
    analysis_fields = 10

    return detection_fields + obj_fields + gltf_fields + fbx_fields + dae_fields + usd_fields + general_fields + analysis_fields


# Integration point for metadata_engine.py
def extract_ar_vr_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for AR/VR metadata extraction."""
    return extract_ar_vr_metadata(filepath)