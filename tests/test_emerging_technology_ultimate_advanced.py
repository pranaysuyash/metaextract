import json
import struct
import zipfile

from server.extractor.modules.emerging_technology_ultimate_advanced import (
    extract_emerging_technology_metadata,
)


def _write(path, data: bytes) -> None:
    with open(path, "wb") as f:
        f.write(data)


def test_glb_parsing(tmp_path):
    glb_path = tmp_path / "scene.glb"
    gltf_json = {
        "asset": {"version": "2.0", "generator": "unit"},
        "scenes": [{}],
        "nodes": [{}],
        "meshes": [{}],
        "materials": [{}],
        "animations": [],
    }
    json_bytes = json.dumps(gltf_json).encode("utf-8")
    padding = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b" " * padding
    chunk_len = len(json_bytes)
    header = b"glTF" + struct.pack("<II", 2, 12 + 8 + chunk_len)
    chunk_header = struct.pack("<I4s", chunk_len, b"JSON")
    _write(glb_path, header + chunk_header + json_bytes)

    result = extract_emerging_technology_metadata(str(glb_path))
    assert result.get("arvr_ultimate_asset_format") == "glb"
    assert result.get("arvr_ultimate_glb_version") == 2
    assert result.get("arvr_ultimate_scene_count") == 1
    assert result.get("arvr_ultimate_mesh_count") == 1


def test_gltf_parsing(tmp_path):
    gltf_path = tmp_path / "scene.gltf"
    data = {
        "asset": {"version": "2.0"},
        "scenes": [{}, {}],
        "nodes": [{}, {}, {}],
        "meshes": [{}],
        "materials": [{}, {}],
    }
    _write(gltf_path, json.dumps(data).encode("utf-8"))
    result = extract_emerging_technology_metadata(str(gltf_path))
    assert result.get("arvr_ultimate_asset_format") == "gltf"
    assert result.get("arvr_ultimate_scene_count") == 2
    assert result.get("arvr_ultimate_node_count") == 3
    assert result.get("arvr_ultimate_material_count") == 2


def test_usdz_parsing(tmp_path):
    usdz_path = tmp_path / "asset.usdz"
    with zipfile.ZipFile(usdz_path, "w") as zf:
        zf.writestr(
            "model.usda",
            "#usda 1.0\n"
            "defaultPrim = \"Root\"\n"
            "upAxis = \"Y\"\n"
            "metersPerUnit = 0.01\n"
            "def Xform \"Root\" {}\n",
        )
        zf.writestr("model.usdc", b"PXR-USDC\x00\x00")
        zf.writestr("Textures/tex.png", b"\x89PNG\r\n\x1a\n")
    result = extract_emerging_technology_metadata(str(usdz_path))
    assert result.get("arvr_ultimate_asset_format") == "usdz"
    assert result.get("arvr_ultimate_usdz_is_zip") is True
    assert result.get("arvr_ultimate_usdz_has_usd") is True
    assert result.get("arvr_ultimate_usdz_texture_count") == 1
    assert result.get("arvr_ultimate_usdz_usda_default_prim") == "Root"
    assert result.get("arvr_ultimate_usdz_usda_up_axis") == "Y"
    assert result.get("arvr_ultimate_usdz_usda_meters_per_unit") == 0.01
    assert result.get("arvr_ultimate_usdz_usdc_count") == 1
    assert result.get("arvr_ultimate_usdz_usdc_has_magic") is True


def test_qasm_parsing(tmp_path):
    qasm_path = tmp_path / "circuit.qasm"
    qasm = "\n".join([
        "OPENQASM 2.0;",
        "qreg q[2];",
        "creg c[2];",
        "h q[0];",
        "cx q[0],q[1];",
        "measure q[0] -> c[0];",
    ])
    _write(qasm_path, qasm.encode("utf-8"))
    result = extract_emerging_technology_metadata(str(qasm_path))
    assert result.get("quantum_ultimate_qasm_version") == "2.0"
    assert result.get("quantum_ultimate_gate_count") == 3
    gate_set = result.get("quantum_ultimate_gate_set") or []
    assert "h" in gate_set and "cx" in gate_set


def test_robotics_urdf_parsing(tmp_path):
    urdf_path = tmp_path / "robot.urdf"
    xml = (
        "<robot name=\"test\">"
        "<link name=\"base\" />"
        "<link name=\"arm\" />"
        "<joint name=\"joint1\" />"
        "<transmission name=\"t1\"></transmission>"
        "<gazebo></gazebo>"
        "</robot>"
    )
    _write(urdf_path, xml.encode("utf-8"))
    result = extract_emerging_technology_metadata(str(urdf_path))
    assert result.get("robotics_ultimate_robot_name") == "test"
    assert result.get("robotics_ultimate_link_count") == 2
    assert result.get("robotics_ultimate_joint_count") == 1
    assert result.get("robotics_ultimate_transmission_count") == 1
    assert result.get("robotics_ultimate_gazebo_tag_count") == 1


def test_biotech_fasta_parsing(tmp_path):
    fasta_path = tmp_path / "sample.dna"
    fasta = ">seq1\nACGTACGT\n"
    _write(fasta_path, fasta.encode("utf-8"))
    result = extract_emerging_technology_metadata(str(fasta_path))
    assert result.get("biotech_ultimate_sequence_length") == 8
    assert result.get("biotech_ultimate_gc_content") == 0.5
    assert result.get("biotech_ultimate_record_count") == 1


def test_blockchain_json_parsing(tmp_path):
    path = tmp_path / "asset.nft"
    payload = {
        "chainId": 1,
        "contractAddress": "0xabc",
        "name": "Token",
        "symbol": "TKN",
        "totalSupply": 1000,
        "standard": "ERC-20",
        "transactions": [{}, {}],
    }
    _write(path, json.dumps(payload).encode("utf-8"))
    result = extract_emerging_technology_metadata(str(path))
    assert result.get("blockchain_ultimate_chain_id") == 1
    assert result.get("blockchain_ultimate_token_symbol") == "TKN"
    assert result.get("blockchain_ultimate_transaction_count") == 2


def test_tflite_header_parsing(tmp_path):
    tflite_path = tmp_path / "model.tflite"
    header = struct.pack("<I4s", 16, b"TFL3")
    payload = header + b"CONV_2D" + b"\x00" * 24
    _write(tflite_path, payload)
    result = extract_emerging_technology_metadata(str(tflite_path))
    assert result.get("ai_ultimate_model_has_tflite_signature") is True
    assert result.get("ai_ultimate_model_tflite_identifier") == "TFL3"
    assert result.get("ai_ultimate_model_tflite_root_offset") == 16
    tflite_strings = result.get("ai_ultimate_model_tflite_strings") or []
    assert "CONV_2D" in tflite_strings
    assert result.get("ai_ultimate_model_tflite_op_type_count") >= 1


def test_onnx_header_parsing(tmp_path):
    onnx_path = tmp_path / "model.onnx"
    payload = b"ONNX\x00producer_name\x00unit\x00Conv\x00Relu"
    _write(onnx_path, payload + b"\\x00" * 16)
    result = extract_emerging_technology_metadata(str(onnx_path))
    assert result.get("ai_ultimate_model_has_onnx_signature") is True
    markers = result.get("ai_ultimate_model_onnx_markers") or []
    assert any("onnx" in marker.lower() for marker in markers)
    op_types = result.get("ai_ultimate_model_onnx_op_type_guess") or []
    assert "Conv" in op_types
    assert result.get("ai_ultimate_model_onnx_op_type_count") >= 1


def test_iot_json_parsing(tmp_path):
    path = tmp_path / "device.iot"
    payload = {
        "deviceId": "dev1",
        "deviceType": "sensor",
        "protocol": "mqtt",
        "firmwareVersion": "1.0",
        "sensors": [{"type": "temp"}, {"type": "humid"}],
        "location": {"lat": 1.0},
    }
    _write(path, json.dumps(payload).encode("utf-8"))
    result = extract_emerging_technology_metadata(str(path))
    assert result.get("iot_ultimate_device_id") == "dev1"
    assert result.get("iot_ultimate_sensor_count") == 2
    sensor_types = result.get("iot_ultimate_sensor_types") or []
    assert "temp" in sensor_types


def test_tle_parsing(tmp_path):
    tle_path = tmp_path / "orbit.tle"
    tle = "\n".join([
        "ISS (ZARYA)",
        "1 25544U 98067A   21275.51001157  .00001264  00000-0  29660-4 0  9991",
        "2 25544  51.6442 348.9791 0004096  95.7605  32.2947 15.48815319303657",
    ])
    _write(tle_path, tle.encode("utf-8"))
    result = extract_emerging_technology_metadata(str(tle_path))
    assert result.get("space_ultimate_tle_norad_id") == "25544"
    assert result.get("space_ultimate_tle_inclination") == 51.6442


def test_digital_twin_json_parsing(tmp_path):
    path = tmp_path / "model.twin"
    payload = {
        "twinId": "t1",
        "simulationEngine": "engine",
        "modelFormat": "gltf",
        "assets": [{}, {}],
    }
    _write(path, json.dumps(payload).encode("utf-8"))
    result = extract_emerging_technology_metadata(str(path))
    assert result.get("digital_twin_ultimate_twin_id") == "t1"
    assert result.get("digital_twin_ultimate_asset_count") == 2
