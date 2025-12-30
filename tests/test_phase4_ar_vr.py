# tests/test_phase4_ar_vr.py

import pytest
import json
import tempfile
import os
from pathlib import Path

from server.extractor.modules import ar_vr_metadata as arvr


def test_ar_vr_module_import():
    """Test that the ar_vr_metadata module can be imported and has expected functions."""
    assert hasattr(arvr, 'extract_ar_vr_metadata')
    assert hasattr(arvr, 'get_ar_vr_field_count')
    assert callable(arvr.extract_ar_vr_metadata)
    assert callable(arvr.get_ar_vr_field_count)


def test_get_ar_vr_field_count():
    """Test that get_ar_vr_field_count returns a reasonable number."""
    count = arvr.get_ar_vr_field_count()
    assert isinstance(count, int)
    assert count > 50  # Should have substantial field coverage


def test_extract_ar_vr_metadata_nonexistent_file():
    """Test handling of nonexistent files."""
    result = arvr.extract_ar_vr_metadata("/nonexistent/file.obj")
    assert isinstance(result, dict)
    assert "ar_vr_extraction_error" in result


def test_extract_ar_vr_metadata_obj_file():
    """Test OBJ file metadata extraction."""
    # Create a simple OBJ file
    obj_content = """# Simple OBJ file
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.0 1.0 0.0
vn 0.0 0.0 1.0
vt 0.0 0.0
f 1/1/1 2/2/1 3/3/1
mtllib material.mtl
usemtl Material
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.obj', delete=False) as f:
        f.write(obj_content)
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_metadata(temp_path)

        assert isinstance(result, dict)
        assert result.get('ar_vr_format') == 'obj'
        assert result.get('obj_format_present') is True
        assert result.get('obj_vertices') == 3
        assert result.get('obj_faces') == 1
        assert result.get('obj_normals') == 1
        assert result.get('obj_texcoords') == 1
        assert result.get('obj_materials_used') == 1
        assert 'material.mtl' in result.get('obj_material_libraries', [])

    finally:
        os.unlink(temp_path)


def test_extract_ar_vr_metadata_gltf_file():
    """Test GLTF file metadata extraction."""
    # Create a simple GLTF JSON file
    gltf_content = {
        "asset": {
            "version": "2.0",
            "generator": "Test Generator"
        },
        "scenes": [{"name": "Scene"}],
        "nodes": [{"name": "Node1"}, {"name": "Node2"}],
        "meshes": [{"name": "Mesh1"}],
        "materials": [{"name": "Material1", "pbrMetallicRoughness": {}}],
        "animations": [{"name": "Animation1"}]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.gltf', delete=False) as f:
        json.dump(gltf_content, f)
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_metadata(temp_path)

        assert isinstance(result, dict)
        assert result.get('ar_vr_format') == 'gltf'
        assert result.get('gltf_format_present') is True
        assert result.get('gltf_asset_version') == '2.0'
        assert result.get('gltf_asset_generator') == 'Test Generator'
        assert result.get('gltf_scene_count') == 1
        assert result.get('gltf_node_count') == 2
        assert result.get('gltf_mesh_count') == 1
        assert result.get('gltf_material_count') == 1
        assert result.get('gltf_animation_count') == 1
        assert result.get('gltf_pbr_materials') == 1

    finally:
        os.unlink(temp_path)


def test_extract_ar_vr_metadata_fbx_file():
    """Test FBX file metadata extraction (limited due to binary format)."""
    # Create a mock FBX file with some readable content
    fbx_content = b"Kaydara FBX Binary  \x00\x00\x00\x00Geometry\x00Material\x00Texture\x00"

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.fbx', delete=False) as f:
        f.write(fbx_content)
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_metadata(temp_path)

        assert isinstance(result, dict)
        assert result.get('ar_vr_format') == 'fbx'
        assert result.get('fbx_format_present') is True
        # FBX extraction is limited due to binary format, but should not error

    finally:
        os.unlink(temp_path)


def test_extract_ar_vr_metadata_dae_file():
    """Test COLLADA DAE file metadata extraction."""
    dae_content = """<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset>
    <created>2023-01-01T00:00:00Z</created>
    <modified>2023-01-01T00:00:00Z</modified>
  </asset>
  <library_geometries>
    <geometry id="Cube-mesh"/>
    <geometry id="Sphere-mesh"/>
  </library_geometries>
  <library_materials>
    <material id="Material"/>
  </library_materials>
  <library_animations>
    <animation id="Animation"/>
  </library_animations>
</COLLADA>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.dae', delete=False) as f:
        f.write(dae_content)
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_metadata(temp_path)

        assert isinstance(result, dict)
        assert result.get('ar_vr_format') == 'dae'
        assert result.get('dae_format_present') is True
        assert result.get('dae_geometry_count') == 2
        assert result.get('dae_material_count') == 1
        assert result.get('dae_animation_count') == 1

    finally:
        os.unlink(temp_path)


def test_extract_ar_vr_metadata_usd_file():
    """Test USD file metadata extraction."""
    usd_content = """#usda 1.0
(
    upAxis = "Y"
    metersPerUnit = 1.0
)

def "Scene" {
    def Cube "Cube1" {}
    def Sphere "Sphere1" {}
}

def Material "Mat1" {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.usd', delete=False) as f:
        f.write(usd_content)
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_metadata(temp_path)

        assert isinstance(result, dict)
        assert result.get('ar_vr_format') == 'usd'
        assert result.get('usd_format_present') is True
        assert result.get('usd_up_axis') == 'Y'
        assert result.get('usd_meters_per_unit') == 1.0
        assert result.get('usd_prim_count') == 3  # Scene, Cube1, Sphere1

    finally:
        os.unlink(temp_path)


def test_extract_ar_vr_metadata_unknown_format():
    """Test handling of unknown file formats."""
    # Create a text file with .xyz extension (not AR/VR)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        f.write("Some random content")
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_metadata(temp_path)

        assert isinstance(result, dict)
        # Should still extract general properties
        assert 'ar_vr_file_size' in result
        assert 'ar_vr_filename' in result

    finally:
        os.unlink(temp_path)


def test_extract_ar_vr_metadata_ar_vr_keywords():
    """Test detection of AR/VR specific keywords."""
    # Create a file with AR/VR keywords
    content = """
# AR/VR scene file
occlusion enabled
shadow mapping on
reflection probe
transparency blend
animation controller
skeleton root
bone hierarchy
physics rigidbody
light directional
camera perspective
fog exponential
postprocessing bloom
interactive trigger
event system
mobile optimized
webvr compatible
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.scene', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_metadata(temp_path)

        assert isinstance(result, dict)
        assert 'ar_vr_keywords_found' in result
        keywords = result['ar_vr_keywords_found']
        assert isinstance(keywords, list)
        assert len(keywords) > 5  # Should find multiple keywords

    finally:
        os.unlink(temp_path)


def test_extract_ar_vr_complete_function():
    """Test the complete extraction function."""
    # Create a simple OBJ file
    obj_content = "v 0 0 0\nv 1 0 0\nf 1 2\n"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.obj', delete=False) as f:
        f.write(obj_content)
        temp_path = f.name

    try:
        result = arvr.extract_ar_vr_complete(temp_path)

        assert isinstance(result, dict)
        assert 'obj_vertices' in result
        assert result['obj_vertices'] == 2

    finally:
        os.unlink(temp_path)