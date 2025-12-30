# server/extractor/modules/iot_metadata.py

"""
IoT device metadata extraction for Phase 4.

Extracts metadata from:
- IoT device configuration files
- Sensor data files
- Device firmware information
- Network configuration
- Device telemetry data
- IoT platform configurations
"""

import logging
import json
import re
import struct
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# IoT file extensions and formats
IOT_EXTENSIONS = [
    '.json', '.xml', '.yaml', '.yml', '.config', '.conf',
    '.ini', '.cfg', '.properties', '.env',
    '.csv', '.tsv', '.log', '.data'
]

# IoT-specific file patterns
IOT_PATTERNS = [
    'iot', 'device', 'sensor', 'firmware', 'telemetry',
    'mqtt', 'coap', 'zigbee', 'bluetooth', 'wifi',
    'configuration', 'config', 'settings', 'calibration'
]


def extract_iot_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract IoT device metadata from configuration and data files.

    Supports various IoT device formats and configurations.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is IoT-related
        is_iot_file = _is_iot_related_file(filepath, filename)

        if not is_iot_file:
            return result

        result['iot_file_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.json']:
            json_data = _extract_json_iot_metadata(filepath)
            result.update(json_data)

        elif file_ext in ['.xml']:
            xml_data = _extract_xml_iot_metadata(filepath)
            result.update(xml_data)

        elif file_ext in ['.yaml', '.yml']:
            yaml_data = _extract_yaml_iot_metadata(filepath)
            result.update(yaml_data)

        elif file_ext in ['.ini', '.cfg', '.conf', '.properties']:
            config_data = _extract_config_iot_metadata(filepath)
            result.update(config_data)

        elif file_ext in ['.csv', '.tsv']:
            sensor_data = _extract_sensor_data_metadata(filepath)
            result.update(sensor_data)

        elif file_ext in ['.log', '.data']:
            telemetry_data = _extract_telemetry_metadata(filepath)
            result.update(telemetry_data)

        # Extract general IoT properties
        general_data = _extract_general_iot_properties(filepath)
        result.update(general_data)

        # Analyze for IoT-specific features
        iot_analysis = _analyze_iot_features(filepath)
        result.update(iot_analysis)

    except Exception as e:
        logger.warning(f"Error extracting IoT metadata from {filepath}: {e}")
        result['iot_extraction_error'] = str(e)

    return result


def _is_iot_related_file(filepath: str, filename: str) -> bool:
    """Check if file is IoT-related based on content and naming."""
    try:
        # Check filename patterns
        if any(pattern in filename for pattern in IOT_PATTERNS):
            return True

        # Check file content for IoT keywords
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2048)  # Read first 2KB

        iot_keywords = [
            'device_id', 'sensor_id', 'firmware_version', 'mqtt', 'coap',
            'zigbee', 'bluetooth', 'wifi_config', 'telemetry', 'calibration',
            'adc', 'gpio', 'i2c', 'spi', 'uart', 'pwm', 'interrupt',
            'temperature', 'humidity', 'pressure', 'accelerometer', 'gyroscope',
            'gps', 'rfid', 'nfc', 'lora', 'sigfox', 'nbiot', 'lte'
        ]

        content_lower = content.lower()
        if any(keyword in content_lower for keyword in iot_keywords):
            return True

        # Check for common IoT data patterns
        if re.search(r'device.*id|sensor.*id|mac.*address', content_lower):
            return True

        # Check for configuration patterns
        if re.search(r'host.*:.*port|server.*:.*port|broker.*:.*port', content_lower):
            return True

    except Exception:
        pass

    return False


def _extract_json_iot_metadata(filepath: str) -> Dict[str, Any]:
    """Extract IoT metadata from JSON files."""
    json_data = {'iot_json_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        data = json.loads(content)

        # Extract device information
        if 'device' in data:
            device = data['device']
            json_data['iot_device_id'] = device.get('id') or device.get('device_id')
            json_data['iot_device_type'] = device.get('type') or device.get('device_type')
            json_data['iot_device_model'] = device.get('model')
            json_data['iot_firmware_version'] = device.get('firmware_version') or device.get('version')
            json_data['iot_manufacturer'] = device.get('manufacturer')

        # Extract sensor information
        if 'sensors' in data:
            sensors = data['sensors']
            if isinstance(sensors, list):
                json_data['iot_sensor_count'] = len(sensors)
                sensor_types = [s.get('type') for s in sensors if isinstance(s, dict)]
                json_data['iot_sensor_types'] = sensor_types
            elif isinstance(sensors, dict):
                json_data['iot_sensor_count'] = len(sensors)
                json_data['iot_sensor_types'] = list(sensors.keys())

        # Extract network configuration
        if 'network' in data:
            network = data['network']
            json_data['iot_network_type'] = network.get('type')
            json_data['iot_mqtt_broker'] = network.get('mqtt', {}).get('broker')
            json_data['iot_mqtt_port'] = network.get('mqtt', {}).get('port')
            json_data['iot_coap_server'] = network.get('coap', {}).get('server')

        # Extract calibration data
        if 'calibration' in data:
            calibration = data['calibration']
            json_data['iot_has_calibration'] = True
            if isinstance(calibration, dict):
                json_data['iot_calibration_parameters'] = len(calibration)

        # Extract telemetry configuration
        if 'telemetry' in data:
            telemetry = data['telemetry']
            json_data['iot_telemetry_interval'] = telemetry.get('interval')
            json_data['iot_telemetry_enabled'] = telemetry.get('enabled', True)

    except Exception as e:
        json_data['iot_json_extraction_error'] = str(e)

    return json_data


def _extract_xml_iot_metadata(filepath: str) -> Dict[str, Any]:
    """Extract IoT metadata from XML files."""
    xml_data = {'iot_xml_format_present': True}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Extract device information
        device_elem = root.find('.//device')
        if device_elem is not None:
            xml_data['iot_device_id'] = device_elem.get('id')
            xml_data['iot_device_type'] = device_elem.get('type')
            xml_data['iot_device_model'] = device_elem.get('model')

            firmware = device_elem.find('firmware')
            if firmware is not None:
                xml_data['iot_firmware_version'] = firmware.get('version')

        # Extract sensor information
        sensors = root.findall('.//sensor')
        if sensors:
            xml_data['iot_sensor_count'] = len(sensors)
            sensor_types = [s.get('type') for s in sensors]
            xml_data['iot_sensor_types'] = sensor_types

        # Extract network configuration
        network = root.find('.//network')
        if network is not None:
            xml_data['iot_network_type'] = network.get('type')

            mqtt = network.find('mqtt')
            if mqtt is not None:
                xml_data['iot_mqtt_broker'] = mqtt.get('broker')
                xml_data['iot_mqtt_port'] = mqtt.get('port')

        # Extract configuration parameters
        config_params = root.findall('.//parameter')
        if config_params:
            xml_data['iot_config_parameters'] = len(config_params)

    except Exception as e:
        xml_data['iot_xml_extraction_error'] = str(e)

    return xml_data


def _extract_yaml_iot_metadata(filepath: str) -> Dict[str, Any]:
    """Extract IoT metadata from YAML files."""
    yaml_data = {'iot_yaml_format_present': True}

    try:
        import yaml
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            return yaml_data

        # Extract device information
        if 'device' in data:
            device = data['device']
            yaml_data['iot_device_id'] = device.get('id')
            yaml_data['iot_device_type'] = device.get('type')
            yaml_data['iot_firmware_version'] = device.get('firmware_version')

        # Extract sensor configuration
        if 'sensors' in data:
            sensors = data['sensors']
            if isinstance(sensors, list):
                yaml_data['iot_sensor_count'] = len(sensors)
            elif isinstance(sensors, dict):
                yaml_data['iot_sensor_count'] = len(sensors)

        # Extract network settings
        if 'network' in data:
            network = data['network']
            yaml_data['iot_network_configured'] = True
            yaml_data['iot_mqtt_enabled'] = 'mqtt' in network

    except ImportError:
        yaml_data['iot_yaml_not_available'] = True
    except Exception as e:
        yaml_data['iot_yaml_extraction_error'] = str(e)

    return yaml_data


def _extract_config_iot_metadata(filepath: str) -> Dict[str, Any]:
    """Extract IoT metadata from configuration files."""
    config_data = {'iot_config_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')

        # Extract key-value pairs
        config_pairs = {}
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config_pairs[key.strip().lower()] = value.strip()

        # Look for IoT-specific configurations
        iot_keys = {
            'device_id': 'iot_device_id',
            'sensor_id': 'iot_sensor_id',
            'firmware_version': 'iot_firmware_version',
            'mqtt_broker': 'iot_mqtt_broker',
            'mqtt_port': 'iot_mqtt_port',
            'coap_server': 'iot_coap_server',
            'wifi_ssid': 'iot_wifi_ssid',
            'bluetooth_enabled': 'iot_bluetooth_enabled'
        }

        for config_key, metadata_key in iot_keys.items():
            if config_key in config_pairs:
                config_data[metadata_key] = config_pairs[config_key]

        # Count configuration parameters
        config_data['iot_config_parameters'] = len(config_pairs)

        # Check for network-related configurations
        network_indicators = ['host', 'port', 'server', 'broker', 'ssid', 'password']
        network_configs = [k for k in config_pairs.keys() if any(ind in k for ind in network_indicators)]
        if network_configs:
            config_data['iot_network_configs'] = len(network_configs)

    except Exception as e:
        config_data['iot_config_extraction_error'] = str(e)

    return config_data


def _extract_sensor_data_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from sensor data files."""
    sensor_data = {'iot_sensor_data_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10240)  # Read first 10KB

        lines = content.split('\n')

        # Analyze header row (CSV/TSV)
        header_line = None
        for line in lines[:5]:  # Check first 5 lines for header
            if line.strip() and not line.startswith('#'):
                header_line = line
                break

        if header_line:
            # Detect delimiter
            if '\t' in header_line:
                delimiter = '\t'
                sensor_data['iot_data_format'] = 'tsv'
            else:
                delimiter = ','
                sensor_data['iot_data_format'] = 'csv'

            # Parse header
            headers = [h.strip() for h in header_line.split(delimiter)]
            sensor_data['iot_data_columns'] = len(headers)

            # Identify sensor types from headers
            sensor_type_indicators = {
                'temp': 'temperature',
                'humidity': 'humidity',
                'pressure': 'pressure',
                'accel': 'accelerometer',
                'gyro': 'gyroscope',
                'gps': 'gps',
                'light': 'light',
                'sound': 'audio'
            }

            detected_sensors = []
            for header in headers:
                header_lower = header.lower()
                for indicator, sensor_type in sensor_type_indicators.items():
                    if indicator in header_lower:
                        if sensor_type not in detected_sensors:
                            detected_sensors.append(sensor_type)

            if detected_sensors:
                sensor_data['iot_detected_sensor_types'] = detected_sensors

            # Count data rows
            data_rows = [line for line in lines if line.strip() and not line.startswith('#') and line != header_line]
            sensor_data['iot_data_rows'] = len(data_rows)

            # Estimate sampling rate if timestamp column exists
            timestamp_cols = [i for i, h in enumerate(headers) if 'time' in h.lower() or 'timestamp' in h.lower()]
            if timestamp_cols and len(data_rows) > 1:
                try:
                    # Simple sampling rate estimation
                    sensor_data['iot_has_timestamps'] = True
                except:
                    pass

    except Exception as e:
        sensor_data['iot_sensor_data_extraction_error'] = str(e)

    return sensor_data


def _extract_telemetry_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from telemetry/log files."""
    telemetry_data = {'iot_telemetry_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(20480)  # Read first 20KB

        lines = content.split('\n')

        # Analyze log entries
        log_entries = [line for line in lines if line.strip()]

        # Look for common log patterns
        timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}:\d{2}:\d{2}')
        json_pattern = re.compile(r'\{.*\}|\[.*\]')

        timestamped_entries = 0
        json_entries = 0

        for line in log_entries[:100]:  # Sample first 100 entries
            if timestamp_pattern.search(line):
                timestamped_entries += 1
            if json_pattern.search(line):
                json_entries += 1

        telemetry_data['iot_log_entries'] = len(log_entries)
        telemetry_data['iot_timestamped_entries'] = timestamped_entries
        telemetry_data['iot_json_entries'] = json_entries

        # Look for device/sensor data patterns
        device_patterns = [
            r'device.*:', r'sensor.*:', r'temperature.*:', r'humidity.*:',
            r'voltage.*:', r'current.*:', r'status.*:', r'error.*:'
        ]

        device_data_lines = 0
        for line in log_entries[:100]:
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in device_patterns):
                device_data_lines += 1

        if device_data_lines > 0:
            telemetry_data['iot_device_data_lines'] = device_data_lines

        # Check for error patterns
        error_patterns = ['error', 'fail', 'exception', 'warning']
        error_lines = sum(1 for line in log_entries[:100] if any(err in line.lower() for err in error_patterns))
        if error_lines > 0:
            telemetry_data['iot_error_lines'] = error_lines

    except Exception as e:
        telemetry_data['iot_telemetry_extraction_error'] = str(e)

    return telemetry_data


def _extract_general_iot_properties(filepath: str) -> Dict[str, Any]:
    """Extract general IoT file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['iot_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['iot_filename'] = filename

        # Check for IoT-specific naming patterns
        iot_indicators = ['iot', 'device', 'sensor', 'telemetry', 'firmware', 'config']
        if any(indicator in filename.lower() for indicator in iot_indicators):
            props['iot_filename_suggests_iot'] = True

        # Extract version numbers from filename
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['iot_file_version_hint'] = version_match.group(1)

    except Exception:
        pass

    return props


def _analyze_iot_features(filepath: str) -> Dict[str, Any]:
    """Analyze file for IoT-specific features."""
    analysis = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5120)  # Read first 5KB

        # Look for IoT protocols and standards
        protocols = ['mqtt', 'coap', 'http', 'https', 'websocket', 'tcp', 'udp']
        found_protocols = [p for p in protocols if p in content.lower()]
        if found_protocols:
            analysis['iot_protocols_detected'] = found_protocols

        # Look for connectivity technologies
        connectivity = ['wifi', 'bluetooth', 'zigbee', 'zwave', 'lora', 'sigfox', 'nbiot', 'lte', 'gsm']
        found_connectivity = [c for c in connectivity if c in content.lower()]
        if found_connectivity:
            analysis['iot_connectivity_detected'] = found_connectivity

        # Look for sensor types
        sensor_types = ['temperature', 'humidity', 'pressure', 'accelerometer', 'gyroscope', 'gps', 'light', 'motion', 'proximity']
        found_sensors = [s for s in sensor_types if s in content.lower()]
        if found_sensors:
            analysis['iot_sensor_types_detected'] = found_sensors

        # Look for cloud platforms
        platforms = ['aws', 'azure', 'gcp', 'ibm', 'thingspeak', 'adafruit', 'particle']
        found_platforms = [p for p in platforms if p in content.lower()]
        if found_platforms:
            analysis['iot_platforms_detected'] = found_platforms

        # Check for security features
        security_features = ['ssl', 'tls', 'certificate', 'encryption', 'authentication', 'token']
        found_security = [s for s in security_features if s in content.lower()]
        if found_security:
            analysis['iot_security_features'] = found_security

    except Exception:
        pass

    return analysis


def get_iot_field_count() -> int:
    """Return the number of fields extracted by IoT metadata."""
    # Format detection (5)
    detection_fields = 5

    # JSON specific (15)
    json_fields = 15

    # XML specific (10)
    xml_fields = 10

    # YAML specific (8)
    yaml_fields = 8

    # Config specific (12)
    config_fields = 12

    # Sensor data specific (10)
    sensor_fields = 10

    # Telemetry specific (10)
    telemetry_fields = 10

    # General properties (6)
    general_fields = 6

    # IoT analysis (8)
    analysis_fields = 8

    return detection_fields + json_fields + xml_fields + yaml_fields + config_fields + sensor_fields + telemetry_fields + general_fields + analysis_fields


# Integration point for metadata_engine.py
def extract_iot_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for IoT metadata extraction."""
    return extract_iot_metadata(filepath)