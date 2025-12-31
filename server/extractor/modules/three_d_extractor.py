#!/usr/bin/env python3
"""
3D/AR/VR Extractor for MetaExtract.
Extracts metadata from 3D formats (OBJ, STL, 3MF, USD, glTF).
"""

import os
import sys
import json
import struct
import zipfile
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re

logger = logging.getLogger(__name__)


class OBJExtractor:
    """Extract metadata from Wavefront OBJ files."""

    def detect_obj(self, filepath: str) -> bool:
        """Check if file is a valid OBJ file."""
        if not filepath.lower().endswith('.obj'):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'r') as f:
                first_lines = f.read(500)
                return any(line.startswith(('v ', 'f ', 'g ', 'o ', 'vn ', 'vt ')) 
                       for line in first_lines.split('\n') if line.strip())
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_obj_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "obj_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            metadata = {
                "format": "obj",
                "file_size": os.path.getsize(filepath),
            }

            lines = content.split('\n')

            vertices = []
            normals = []
            texcoords = []
            faces = []
            groups = []
            objects = []
            lines_geo = []

            for line in lines[:50000]:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('v '):
                    parts = line.split()[1:]
                    if len(parts) >= 3:
                        try:
                            vertices.append((float(parts[0]), float(parts[1]), float(parts[2])))
                        except:
                            pass
                elif line.startswith('vn '):
                    parts = line.split()[1:]
                    if len(parts) >= 3:
                        try:
                            normals.append((float(parts[0]), float(parts[1]), float(parts[2])))
                        except:
                            pass
                elif line.startswith('vt '):
                    parts = line.split()[1:]
                    if len(parts) >= 2:
                        try:
                            texcoords.append((float(parts[0]), float(parts[1])))
                        except:
                            pass
                elif line.startswith('f '):
                    parts = line.split()[1:]
                    faces.append(len(parts))
                elif line.startswith('g '):
                    groups.append(line.split(' ', 1)[1] if len(line.split()) > 1 else 'default')
                elif line.startswith('o '):
                    objects.append(line.split(' ', 1)[1] if len(line.split()) > 1 else 'default')
                elif line.startswith('l '):
                    lines_geo.append(line)

            metadata["vertex_count"] = len(vertices)
            metadata["normal_count"] = len(normals)
            metadata["texcoord_count"] = len(texcoords)
            metadata["face_count"] = len(faces)
            metadata["group_count"] = len(groups)
            metadata["object_count"] = len(objects)

            if vertices:
                lons = [v[0] for v in vertices]
                lats = [v[1] for v in vertices]
                alts = [v[2] for v in vertices]
                metadata["bounds"] = [min(lons), min(lats), min(alts), max(lons), max(lats), max(alts)]
                metadata["center"] = [(min(lons) + max(lons)) / 2, (min(lats) + max(lats)) / 2, (min(alts) + max(alts)) / 2]

            if faces:
                avg_face_vertices = sum(faces) / len(faces) if faces else 0
                metadata["avg_face_vertices"] = avg_face_vertices

            mtllib_match = re.search(r'mtllib\s+(\S+)', content)
            if mtllib_match:
                metadata["mtl_file"] = mtllib_match.group(1)

            usemtl_match = re.search(r'usemtl\s+(\S+)', content)
            if usemtl_match:
                metadata["material"] = usemtl_match.group(1)

            comment_match = re.search(r'#\s*(.+)', content)
            if comment_match:
                metadata["comment"] = comment_match.group(1)[:200]

            result["format_detected"] = "obj"
            result["obj_metadata"] = metadata
            result["extraction_success"] = True

        except Exception as e:
            result["obj_metadata"] = {"error": str(e)}

        return result


class STLExtractor:
    """Extract metadata from STL files."""

    def detect_stl(self, filepath: str) -> bool:
        """Check if file is a valid STL file."""
        if not filepath.lower().endswith('.stl'):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(80)
                if header[:5] == b'solid':
                    return True
                f.seek(80)
                triangle_count = struct.unpack('<I', f.read(4))[0]
                return 0 < triangle_count < 10000000
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_stl_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "stl_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                header = f.read(80)
                is_ascii = header[:5] == b'solid'

                if is_ascii:
                    content = header + f.read()
                    text = content.decode('ascii', errors='replace')
                    triangles = text.count('facet normal')
                    metadata = {
                        "format": "stl",
                        "type": "ascii",
                        "file_size": os.path.getsize(filepath),
                        "triangle_count": triangles,
                    }
                else:
                    f.seek(80)
                    triangle_count = struct.unpack('<I', f.read(4))[0]
                    
                    triangles_data = []
                    for _ in range(min(triangle_count, 10000)):
                        data = f.read(50)
                        if len(data) < 50:
                            break
                        normal = struct.unpack('<3f', data[:12])
                        v1 = struct.unpack('<3f', data[12:24])
                        v2 = struct.unpack('<3f', data[24:36])
                        v3 = struct.unpack('<3f', data[36:48])
                        triangles_data.append({'normal': normal, 'vertices': [v1, v2, v3]})

                    vertices = []
                    for tri in triangles_data:
                        vertices.extend(tri['vertices'])
                    
                    metadata = {
                        "format": "stl",
                        "type": "binary",
                        "file_size": os.path.getsize(filepath),
                        "triangle_count": triangle_count,
                        "sample_triangles": len(triangles_data),
                    }

                    if vertices:
                        xs = [v[0] for v in vertices]
                        ys = [v[1] for v in vertices]
                        zs = [v[2] for v in vertices]
                        metadata["bounds"] = [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)]

            name_match = re.search(rb'solid\s+(\S+)', header)
            if name_match:
                try:
                    metadata["name"] = name_match.group(1).decode('ascii').strip()
                except:
                    pass

            result["format_detected"] = "stl"
            result["stl_metadata"] = metadata
            result["extraction_success"] = True

        except Exception as e:
            result["stl_metadata"] = {"error": str(e)}

        return result


class GLTFExtractor:
    """Extract metadata from glTF/glb files."""

    def detect_gltf(self, filepath: str) -> bool:
        """Check if file is a valid glTF file."""
        if not filepath.lower().endswith(('.gltf', '.glb')):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            if filepath.endswith('.glb'):
                with open(filepath, 'rb') as f:
                    header = f.read(12)
                    return header[:4] == b'glTF'
            else:
                with open(filepath, 'r') as f:
                    content = f.read(100)
                    return '"asset"' in content and '"version"' in content
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_gltf_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "gltf_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            is_binary = filepath.endswith('.glb')
            
            if is_binary:
                with open(filepath, 'rb') as f:
                    header = f.read(12)
                    version = struct.unpack('<I', header[4:8])[0]
                    length = struct.unpack('<I', header[8:12])[0]
                    
                    chunk_length = struct.unpack('<I', f.read(4))[0]
                    chunk_type = f.read(4)
                    json_data = f.read(chunk_length).decode('utf-8', errors='replace')
                    json_start = json_data.find('{')
                    json_end = json_data.rfind('}') + 1
                    gltf_json = json.loads(json_data[json_start:json_end])
            else:
                with open(filepath, 'r') as f:
                    gltf_json = json.load(f)

            metadata = {
                "format": "glb" if is_binary else "gltf",
                "file_size": os.path.getsize(filepath),
            }

            if 'asset' in gltf_json:
                asset = gltf_json['asset']
                metadata["version"] = asset.get('version')
                metadata["min_version"] = asset.get('minVersion')
                metadata["generator"] = asset.get('generator')

            metadata["scene"] = gltf_json.get('scene')
            metadata["scenes_count"] = len(gltf_json.get('scenes', []))
            metadata["nodes_count"] = len(gltf_json.get('nodes', []))
            metadata["meshes_count"] = len(gltf_json.get('meshes', []))
            metadata["accessors_count"] = len(gltf_json.get('accessors', []))
            metadata["buffers_count"] = len(gltf_json.get('buffers', []))
            metadata["buffer_views_count"] = len(gltf_json.get('bufferViews', []))
            metadata["textures_count"] = len(gltf_json.get('textures', []))
            metadata["images_count"] = len(gltf_json.get('images', []))
            metadata["materials_count"] = len(gltf_json.get('materials', []))
            metadata["animations_count"] = len(gltf_json.get('animations', []))

            if 'extensions' in gltf_json:
                metadata["extensions"] = list(gltf_json['extensions'].keys())

            if 'extras' in gltf_json:
                metadata["extras"] = gltf_json['extras']

            total_vertices = 0
            total_indices = 0
            if 'meshes' in gltf_json:
                for mesh in gltf_json['meshes']:
                    for prim in mesh.get('primitives', []):
                        if 'attributes' in prim:
                            total_vertices += len(prim.get('indices', [])) if 'indices' in prim else 0
            
            metadata["total_vertices_estimate"] = total_vertices

            result["format_detected"] = "glb" if is_binary else "gltf"
            result["gltf_metadata"] = metadata
            result["extraction_success"] = True

        except json.JSONDecodeError as e:
            result["gltf_metadata"] = {"error": f"Invalid JSON: {e}"}
        except Exception as e:
            result["gltf_metadata"] = {"error": str(e)}

        return result


class USDExtractor:
    """Extract metadata from USD files."""

    def detect_usd(self, filepath: str) -> bool:
        """Check if file is a valid USD file."""
        if not filepath.lower().endswith(('.usd', '.usda', '.usdc', '.usdz')):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb' if filepath.endswith('.usdz') else 'r') as f:
                content = f.read(500)
                if filepath.endswith('.usdz'):
                    return b'glTF' in content or b'USDA' in content or b'USD' in content
                return '<?xml' in content or content.startswith('#usda') or ('(' in content and ')' in content)
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_usd_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "usd_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            is_zipped = filepath.endswith('.usdz')
            is_ascii = filepath.endswith('.usda')

            if is_zipped:
                with zipfile.ZipFile(filepath, 'r') as z:
                    names = z.namelist()
                    usd_files = [n for n in names if n.lower().endswith(('.usd', '.usda', '.usdc'))]
                    metadata = {
                        "format": "usdz",
                        "file_size": os.path.getsize(filepath),
                        "contents": names[:20],
                        "usd_files": usd_files,
                    }
                    if usd_files:
                        content = z.read(usd_files[0]).decode('utf-8', errors='replace')[:10000]
                        metadata["sample_content"] = content[:500]
            else:
                with open(filepath, 'r') as f:
                    content = f.read(100000)
                    metadata = {
                        "format": "usda" if is_ascii else "usd",
                        "file_size": os.path.getsize(filepath),
                    }

            if is_ascii or not is_zipped:
                header_match = re.search(r'#usda\s+v?([\d.]+)', content)
                if header_match:
                    metadata["version"] = header_match.group(1)

                up_axis_match = re.search(r'upAxis\s+(\w+)', content)
                if up_axis_match:
                    metadata["up_axis"] = up_axis_match.group(1)

                meters_per_unit_match = re.search(r'metersPerUnit\s+([\d.e-]+)', content)
                if meters_per_unit_match:
                    metadata["meters_per_unit"] = float(meters_per_unit_match.group(1))

                frames_match = re.search(r'timeSamples\s+\{\s*[\d.]+\s*:\s*\{[^}]+\}', content)
                metadata["has_animations"] = frames_match is not None

                xform_ops = len(re.findall(r'xformOp:', content))
                metadata["xform_op_count"] = xform_ops

                prim_count = content.count('def ')
                metadata["prim_count"] = prim_count

                materials = content.count('Material')
                metadata["material_count"] = materials

                meshes = content.count('Mesh')
                metadata["mesh_count"] = meshes

                points = content.count('points')
                metadata["point_attribute_count"] = points

            result["format_detected"] = "usdz" if is_zipped else ("usda" if is_ascii else "usd")
            result["usd_metadata"] = metadata
            result["extraction_success"] = True

        except Exception as e:
            result["usd_metadata"] = {"error": str(e)}

        return result


class Extractor3D:
    """Main 3D extractor that dispatches to specific format extractors."""

    def __init__(self):
        self.obj = OBJExtractor()
        self.stl = STLExtractor()
        self.gltf = GLTFExtractor()
        self.usd = USDExtractor()

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract 3D metadata from file."""
        ext = Path(filepath).suffix.lower()

        if ext == '.obj':
            return self.obj.extract(filepath)
        elif ext == '.stl':
            return self.stl.extract(filepath)
        elif ext in ['.gltf', '.glb']:
            return self.gltf.extract(filepath)
        elif ext in ['.usd', '.usda', '.usdc', '.usdz']:
            return self.usd.extract(filepath)

        for extractor, name in [(self.obj, 'obj'), (self.stl, 'stl'), 
                                (self.gltf, 'gltf'), (self.usd, 'usd')]:
            detect_method = getattr(extractor, 'detect_' + name)
            if detect_method(filepath):
                return extractor.extract(filepath)

        return {
            "source": "metaextract_3d_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "error": "Unknown 3D format",
        }


def extract_3d_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract 3D metadata."""
    extractor = Extractor3D()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 3d_extractor.py <file.obj|stl|gltf|usd>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_3d_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
