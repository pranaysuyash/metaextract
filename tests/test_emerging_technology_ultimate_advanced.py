import json
import struct

from server.extractor.modules.emerging_technology_ultimate_advanced import (
    extract_emerging_technology_ultimate_advanced,
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

    result = extract_emerging_technology_ultimate_advanced(str(glb_path))
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
    result = extract_emerging_technology_ultimate_advanced(str(gltf_path))
    assert result.get("arvr_ultimate_asset_format") == "gltf"
    assert result.get("arvr_ultimate_scene_count") == 2
    assert result.get("arvr_ultimate_node_count") == 3
    assert result.get("arvr_ultimate_material_count") == 2


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
    result = extract_emerging_technology_ultimate_advanced(str(qasm_path))
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
        "</robot>"
    )
    _write(urdf_path, xml.encode("utf-8"))
    result = extract_emerging_technology_ultimate_advanced(str(urdf_path))
    assert result.get("robotics_ultimate_robot_name") == "test"
    assert result.get("robotics_ultimate_link_count") == 2
    assert result.get("robotics_ultimate_joint_count") == 1


def test_biotech_fasta_parsing(tmp_path):
    fasta_path = tmp_path / "sample.dna"
    fasta = ">seq1\nACGTACGT\n"
    _write(fasta_path, fasta.encode("utf-8"))
    result = extract_emerging_technology_ultimate_advanced(str(fasta_path))
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
    result = extract_emerging_technology_ultimate_advanced(str(path))
    assert result.get("blockchain_ultimate_chain_id") == 1
    assert result.get("blockchain_ultimate_token_symbol") == "TKN"
    assert result.get("blockchain_ultimate_transaction_count") == 2


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
    result = extract_emerging_technology_ultimate_advanced(str(path))
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
    result = extract_emerging_technology_ultimate_advanced(str(tle_path))
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
    result = extract_emerging_technology_ultimate_advanced(str(path))
    assert result.get("digital_twin_ultimate_twin_id") == "t1"
    assert result.get("digital_twin_ultimate_asset_count") == 2
