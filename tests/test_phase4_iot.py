# tests/test_phase4_iot.py

import pytest
import json
import tempfile
import os
from pathlib import Path

from server.extractor.modules import iot_metadata as iot


def test_iot_module_import():
    """Test that the iot_metadata module can be imported and has expected functions."""
    assert hasattr(iot, 'extract_iot_metadata')
    assert hasattr(iot, 'get_iot_field_count')
    assert callable(iot.extract_iot_metadata)
    assert callable(iot.get_iot_field_count)


def test_get_iot_field_count():
    """Test that get_iot_field_count returns a reasonable number."""
    count = iot.get_iot_field_count()
    assert isinstance(count, int)
    assert count > 50  # Should have substantial field coverage


def test_extract_iot_metadata_non_iot_file():
    """Test handling of non-IoT files."""
    # Create a regular text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is just regular text content.")
        temp_path = f.name

    try:
        result = iot.extract_iot_metadata(temp_path)
        assert isinstance(result, dict)
        assert len(result) == 0  # Should return empty dict for non-IoT files
    finally:
        os.unlink(temp_path)


def test_extract_iot_metadata_json_device_config():
    """Test JSON IoT device configuration extraction."""
    device_config = {
        "device": {
            "id": "sensor_001",
            "type": "temperature_sensor",
            "model": "TS-100",
            "firmware_version": "1.2.3",
            "manufacturer": "IoT Corp"
        },
        "sensors": [
            {"type": "temperature", "unit": "celsius"},
            {"type": "humidity", "unit": "percent"}
        ],
        "network": {
            "type": "wifi",
            "mqtt": {
                "broker": "mqtt.example.com",
                "port": 1883
            }
        },
        "telemetry": {
            "interval": 60,
            "enabled": True
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(device_config, f)
        temp_path = f.name

    try:
        result = iot.extract_iot_metadata(temp_path)

        assert isinstance(result, dict)
        assert result.get('iot_file_detected') is True
        assert result.get('iot_json_format_present') is True
        assert result.get('iot_device_id') == 'sensor_001'
        assert result.get('iot_device_type') == 'temperature_sensor'
        assert result.get('iot_firmware_version') == '1.2.3'
        assert result.get('iot_sensor_count') == 2
        assert result.get('iot_mqtt_broker') == 'mqtt.example.com'
        assert result.get('iot_mqtt_port') == 1883
        assert result.get('iot_telemetry_enabled') is True

    finally:
        os.unlink(temp_path)


def test_extract_iot_metadata_xml_config():
    """Test XML IoT configuration extraction."""
    xml_config = """<?xml version="1.0" encoding="UTF-8"?>
<iot_config>
  <device id="device_123" type="multi_sensor" model="MS-200">
    <firmware version="2.1.0"/>
  </device>
  <sensors>
    <sensor type="temperature"/>
    <sensor type="pressure"/>
  </sensors>
  <network type="bluetooth">
    <mqtt broker="broker.iot.com" port="8883"/>
  </network>
  <parameters>
    <parameter name="interval">30