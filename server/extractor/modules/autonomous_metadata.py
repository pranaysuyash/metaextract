# server/extractor/modules/autonomous_metadata.py

"""
Autonomous Systems metadata extraction for Phase 4.

Extracts metadata from:
- Autonomous vehicle configurations
- Self-driving car systems
- Drone/UAV control systems
- Autonomous robot navigation
- Sensor fusion configurations
- Path planning algorithms
- Decision-making systems
"""

import logging
import json
import re
import struct
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

# Autonomous systems file extensions and formats
AUTONOMOUS_EXTENSIONS = [
    '.json', '.yaml', '.yml', '.xml', '.config', '.conf',
    '.py', '.cpp', '.launch', '.world', '.bag', '.db3',
    '.pcd', '.ply', '.las', '.csv', '.log'
]

# Autonomous systems-specific keywords
AUTONOMOUS_KEYWORDS = [
    'autonomous', 'self-driving', 'autopilot', 'navigation',
    'path_planning', 'trajectory', 'localization', 'slam',
    'sensor_fusion', 'perception', 'decision_making',
    'control_system', 'vehicle', 'drone', 'uav', 'ugv',
    'lidar', 'radar', 'camera', 'imu', 'gps', 'odometry',
    'ros2', 'autoware', 'apollo', 'carla', 'gazebo',
    'rviz', 'foxglove', 'cyber', 'dreamview', 'modules',
    'planning', 'prediction', 'routing', 'hdmap', 'opendrive'
]


def extract_autonomous_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract autonomous systems metadata from configuration and data files.

    Supports various autonomous driving and robotics frameworks.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is autonomous-related
        is_autonomous_file = _is_autonomous_related_file(filepath, filename)

        if not is_autonomous_file:
            return result

        result['autonomous_file_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.yaml', '.yml']:
            yaml_autonomous_data = _extract_yaml_autonomous_metadata(filepath)
            result.update(yaml_autonomous_data)

        elif file_ext == '.json':
            json_autonomous_data = _extract_json_autonomous_metadata(filepath)
            result.update(json_autonomous_data)

        elif file_ext == '.xml':
            xml_autonomous_data = _extract_xml_autonomous_metadata(filepath)
            result.update(xml_autonomous_data)

        elif file_ext in ['.py', '.cpp']:
            code_data = _extract_autonomous_code_metadata(filepath)
            result.update(code_data)

        elif file_ext == '.launch':
            launch_data = _extract_autonomous_launch_metadata(filepath)
            result.update(launch_data)

        elif file_ext == '.world':
            world_data = _extract_autonomous_world_metadata(filepath)
            result.update(world_data)

        elif file_ext in ['.bag', '.db3']:
            rosbag_data = _extract_rosbag_metadata(filepath)
            result.update(rosbag_data)

        # Extract general autonomous properties
        general_data = _extract_general_autonomous_properties(filepath)
        result.update(general_data)

        # Analyze autonomous components
        autonomous_analysis = _analyze_autonomous_components(filepath)
        result.update(autonomous_analysis)

    except Exception as e:
        logger.warning(f"Error extracting autonomous metadata from {filepath}: {e}")
        result['autonomous_extraction_error'] = str(e)

    return result


def _is_autonomous_related_file(filepath: str, filename: str) -> bool:
    """Check if file is autonomous systems-related."""
    try:
        # Check filename patterns
        autonomous_patterns = [
            'autonomous', 'selfdriving', 'autopilot', 'navigation',
            'planning', 'perception', 'control', 'vehicle',
            'drone', 'uav', 'ugv', 'sensor', 'fusion'
        ]
        if any(pattern in filename for pattern in autonomous_patterns):
            return True

        # Check file content for autonomous keywords
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096)  # Read first 4KB

        content_lower = content.lower()

        # Count autonomous keywords
        autonomous_keyword_count = sum(1 for keyword in AUTONOMOUS_KEYWORDS if keyword in content_lower)

        # Must have multiple autonomous keywords to be considered autonomous-related
        if autonomous_keyword_count >= 3:
            return True

        # Check for specific autonomous patterns
        autonomous_patterns = [
            r'vehicle_id|vehicle_config',  # Vehicle configurations
            r'sensor_fusion|fusion_config',  # Sensor fusion
            r'path_planning|planning_config',  # Path planning
            r'localization|slam_config',  # Localization/SLAM
            r'perception|perception_config',  # Perception systems
            r'control|control_config',  # Control systems
            r'hdmap|opendrive',  # HD maps
            r'autoware|apollo|carla',  # Autonomous frameworks
        ]

        for pattern in autonomous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

    except Exception:
        pass

    return False


def _extract_yaml_autonomous_metadata(filepath: str) -> Dict[str, Any]:
    """Extract autonomous metadata from YAML configuration files."""
    yaml_data = {'autonomous_yaml_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            return yaml_data

        # Extract autonomous vehicle configuration
        if any(key in data for key in ['vehicle', 'vehicle_config', 'vehicle_info']):
            yaml_data['autonomous_vehicle_config_present'] = True

            vehicle_config = data.get('vehicle', data.get('vehicle_config', data.get('vehicle_info', {})))
            if isinstance(vehicle_config, dict):
                if 'id' in vehicle_config:
                    yaml_data['autonomous_vehicle_id'] = vehicle_config['id']
                if 'type' in vehicle_config:
                    yaml_data['autonomous_vehicle_type'] = vehicle_config['type']
                if 'dimensions' in vehicle_config:
                    dims = vehicle_config['dimensions']
                    if isinstance(dims, dict):
                        yaml_data['autonomous_vehicle_length'] = dims.get('length')
                        yaml_data['autonomous_vehicle_width'] = dims.get('width')
                        yaml_data['autonomous_vehicle_height'] = dims.get('height')

        # Extract sensor configuration
        if 'sensors' in data:
            sensors = data['sensors']
            if isinstance(sensors, list):
                yaml_data['autonomous_sensor_count'] = len(sensors)

                sensor_types = {}
                for sensor in sensors:
                    if isinstance(sensor, dict):
                        sensor_type = sensor.get('type', sensor.get('sensor_type'))
                        if sensor_type:
                            sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1

                if sensor_types:
                    yaml_data['autonomous_sensor_types'] = sensor_types

        # Extract planning configuration
        if any(key in data for key in ['planning', 'planning_config', 'path_planning']):
            yaml_data['autonomous_planning_config_present'] = True

            planning_config = data.get('planning', data.get('planning_config', data.get('path_planning', {})))
            if isinstance(planning_config, dict):
                if 'algorithm' in planning_config:
                    yaml_data['autonomous_planning_algorithm'] = planning_config['algorithm']
                if 'max_velocity' in planning_config:
                    yaml_data['autonomous_max_velocity'] = planning_config['max_velocity']

        # Extract localization configuration
        if any(key in data for key in ['localization', 'localization_config', 'slam']):
            yaml_data['autonomous_localization_config_present'] = True

            loc_config = data.get('localization', data.get('localization_config', data.get('slam', {})))
            if isinstance(loc_config, dict):
                if 'method' in loc_config:
                    yaml_data['autonomous_localization_method'] = loc_config['method']

        # Extract control configuration
        if any(key in data for key in ['control', 'control_config', 'controller']):
            yaml_data['autonomous_control_config_present'] = True

            ctrl_config = data.get('control', data.get('control_config', data.get('controller', {})))
            if isinstance(ctrl_config, dict):
                if 'type' in ctrl_config:
                    yaml_data['autonomous_control_type'] = ctrl_config['type']

        # Check for ROS2 configuration
        if any(key in data for key in ['ros', 'ros2', 'cyber', 'dds']):
            yaml_data['autonomous_ros2_config_present'] = True

        # Check for HD map configuration
        if any(key in data for key in ['hdmap', 'map', 'opendrive']):
            yaml_data['autonomous_hdmap_config_present'] = True

    except Exception as e:
        yaml_data['autonomous_yaml_extraction_error'] = str(e)

    return yaml_data


def _extract_json_autonomous_metadata(filepath: str) -> Dict[str, Any]:
    """Extract autonomous metadata from JSON configuration files."""
    json_data = {'autonomous_json_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return json_data

        # Extract Apollo Cyber RT configuration
        if 'modules' in data:
            modules = data['modules']
            if isinstance(modules, list):
                json_data['autonomous_cyber_modules_count'] = len(modules)

                module_types = {}
                for module in modules:
                    if isinstance(module, dict):
                        module_type = module.get('type', module.get('class_name', module.get('name', '')))
                        if module_type:
                            # Extract base type
                            base_type = module_type.split('.')[-1].lower()
                            module_types[base_type] = module_types.get(base_type, 0) + 1

                if module_types:
                    json_data['autonomous_cyber_module_types'] = module_types

        # Extract routing configuration
        if 'routing' in data or 'route' in data:
            json_data['autonomous_routing_config_present'] = True

            routing_config = data.get('routing', data.get('route', {}))
            if isinstance(routing_config, dict):
                if 'waypoints' in routing_config:
                    waypoints = routing_config['waypoints']
                    if isinstance(waypoints, list):
                        json_data['autonomous_routing_waypoints'] = len(waypoints)

        # Extract prediction configuration
        if 'prediction' in data:
            prediction_config = data['prediction']
            if isinstance(prediction_config, dict):
                json_data['autonomous_prediction_config_present'] = True

                if 'obstacle_types' in prediction_config:
                    obs_types = prediction_config['obstacle_types']
                    if isinstance(obs_types, list):
                        json_data['autonomous_prediction_obstacle_types'] = obs_types

        # Extract scenario configuration
        if 'scenario' in data or 'scenarios' in data:
            json_data['autonomous_scenario_config_present'] = True

            scenarios = data.get('scenarios', [data.get('scenario', {})])
            if isinstance(scenarios, list):
                json_data['autonomous_scenario_count'] = len(scenarios)

        # Extract calibration data
        if 'calibration' in data or 'calib' in data:
            json_data['autonomous_calibration_data_present'] = True

            calib_data = data.get('calibration', data.get('calib', {}))
            if isinstance(calib_data, dict):
                if 'intrinsics' in calib_data:
                    json_data['autonomous_camera_intrinsics_present'] = True
                if 'extrinsics' in calib_data:
                    json_data['autonomous_camera_extrinsics_present'] = True

    except Exception as e:
        json_data['autonomous_json_extraction_error'] = str(e)

    return json_data


def _extract_xml_autonomous_metadata(filepath: str) -> Dict[str, Any]:
    """Extract autonomous metadata from XML configuration files."""
    xml_data = {'autonomous_xml_format_present': True}

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Extract OpenDRIVE road network data
        if root.tag == 'OpenDRIVE':
            xml_data['autonomous_opendrive_format'] = True

            roads = root.findall('.//road')
            xml_data['autonomous_road_count'] = len(roads)

            junctions = root.findall('.//junction')
            xml_data['autonomous_junction_count'] = len(junctions)

            # Extract road types
            road_types = {}
            for road in roads:
                road_type = road.get('type') or road.get('name')
                if road_type:
                    road_types[road_type] = road_types.get(road_type, 0) + 1

            if road_types:
                xml_data['autonomous_road_types'] = road_types

        # Extract vehicle configuration
        vehicle_elem = root.find('.//vehicle')
        if vehicle_elem is not None:
            xml_data['autonomous_vehicle_config_present'] = True

            bbox = vehicle_elem.find('boundingBox')
            if bbox is not None:
                xml_data['autonomous_vehicle_bbox_length'] = bbox.get('length')
                xml_data['autonomous_vehicle_bbox_width'] = bbox.get('width')
                xml_data['autonomous_vehicle_bbox_height'] = bbox.get('height')

        # Extract sensor configuration
        sensors = root.findall('.//sensor')
        xml_data['autonomous_sensor_count'] = len(sensors)

        sensor_types = {}
        for sensor in sensors:
            sensor_type = sensor.get('type') or sensor.tag
            if sensor_type:
                sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1

        if sensor_types:
            xml_data['autonomous_sensor_types'] = sensor_types

        # Extract controller configuration
        controllers = root.findall('.//controller')
        xml_data['autonomous_controller_count'] = len(controllers)

    except Exception as e:
        xml_data['autonomous_xml_extraction_error'] = str(e)

    return xml_data


def _extract_autonomous_code_metadata(filepath: str) -> Dict[str, Any]:
    """Extract autonomous metadata from code files."""
    code_data = {'autonomous_code_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        file_ext = Path(filepath).suffix.lower()

        # Detect programming language
        if file_ext == '.py':
            code_data['autonomous_code_language'] = 'python'
        elif file_ext == '.cpp':
            code_data['autonomous_code_language'] = 'cpp'

        # Count autonomous-specific code elements
        autonomous_elements = {
            'ros2_import': len(re.findall(r'import\s+rclpy|from\s+rclpy', content)),
            'cyber_import': len(re.findall(r'#include\s+.*cyber|cyber::', content)),
            'autoware_import': len(re.findall(r'autoware|autoware_auto', content, re.IGNORECASE)),
            'apollo_import': len(re.findall(r'apollo|modules/', content, re.IGNORECASE)),
            'planning_call': len(re.findall(r'plan\(|planning\.|path_planning', content)),
            'localization_call': len(re.findall(r'localize\(|localization\.|slam', content)),
            'perception_call': len(re.findall(r'perceive\(|perception\.|detect', content)),
            'control_call': len(re.findall(r'control\(|controller\.|pid', content)),
        }

        # Only include counts > 0
        autonomous_elements = {k: v for k, v in autonomous_elements.items() if v > 0}
        if autonomous_elements:
            code_data['autonomous_code_elements'] = autonomous_elements

        # Detect autonomous frameworks
        frameworks = {
            'ros2': 'rclpy' in content or 'ros2' in content.lower(),
            'cyber_rt': 'cyber' in content.lower() and 'rt' in content.lower(),
            'autoware': 'autoware' in content.lower(),
            'apollo': 'apollo' in content.lower() or 'modules/' in content,
            'carla': 'carla' in content.lower(),
            'gazebo': 'gazebo' in content.lower(),
        }

        detected_frameworks = [fw for fw, detected in frameworks.items() if detected]
        if detected_frameworks:
            code_data['autonomous_frameworks_detected'] = detected_frameworks

        # Count autonomous-specific functions/classes
        autonomous_functions = {
            'planning': len(re.findall(r'def\s+plan|class.*Planning', content, re.IGNORECASE)),
            'localization': len(re.findall(r'def\s+localize|class.*Localization', content, re.IGNORECASE)),
            'perception': len(re.findall(r'def\s+perceive|class.*Perception', content, re.IGNORECASE)),
            'control': len(re.findall(r'def\s+control|class.*Controller', content, re.IGNORECASE)),
            'sensor_fusion': len(re.findall(r'fusion|sensor.*fusion', content, re.IGNORECASE)),
            'trajectory': len(re.findall(r'trajectory|path.*planning', content, re.IGNORECASE)),
        }

        autonomous_functions = {k: v for k, v in autonomous_functions.items() if v > 0}
        if autonomous_functions:
            code_data['autonomous_code_functions'] = autonomous_functions

        # Check for autonomous hardware interfaces
        hardware_interfaces = [
            'lidar', 'radar', 'camera', 'imu', 'gps', 'can', 'ethernet',
            'serial', 'pwm', 'adc', 'gpio', 'i2c', 'spi'
        ]
        detected_hardware = [hw for hw in hardware_interfaces if hw in content.lower()]
        if detected_hardware:
            code_data['autonomous_hardware_interfaces'] = detected_hardware

    except Exception as e:
        code_data['autonomous_code_extraction_error'] = str(e)

    return code_data


def _extract_autonomous_launch_metadata(filepath: str) -> Dict[str, Any]:
    """Extract autonomous metadata from ROS2 launch files."""
    launch_data = {'autonomous_launch_format_present': True}

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Count launch elements
        nodes = root.findall('.//node')
        launch_data['autonomous_launch_node_count'] = len(nodes)

        includes = root.findall('.//include')
        launch_data['autonomous_launch_include_count'] = len(includes)

        # Extract node packages and executables
        node_packages = {}
        node_executables = {}

        for node in nodes:
            pkg = node.get('pkg')
            executable = node.get('exec')

            if pkg:
                node_packages[pkg] = node_packages.get(pkg, 0) + 1
            if executable:
                node_executables[executable] = node_executables.get(executable, 0) + 1

        if node_packages:
            launch_data['autonomous_launch_node_packages'] = node_packages
        if node_executables:
            launch_data['autonomous_launch_node_executables'] = node_executables

        # Check for autonomous-specific packages
        autonomous_packages = [
            'nav2', 'navigation', 'planning', 'localization', 'slam',
            'perception', 'control', 'vehicle', 'sensor', 'fusion'
        ]
        detected_packages = [pkg for pkg in node_packages.keys() if any(ap in pkg.lower() for ap in autonomous_packages)]
        if detected_packages:
            launch_data['autonomous_launch_autonomous_packages'] = detected_packages

        # Extract parameters
        params = root.findall('.//param')
        launch_data['autonomous_launch_param_count'] = len(params)

        # Check for autonomous configuration parameters
        autonomous_params = {}
        for param in params:
            param_name = param.get('name', '')
            if any(keyword in param_name.lower() for keyword in AUTONOMOUS_KEYWORDS):
                autonomous_params[param_name] = param.get('value', 'configured')

        if autonomous_params:
            launch_data['autonomous_launch_config_params'] = autonomous_params

    except Exception as e:
        launch_data['autonomous_launch_extraction_error'] = str(e)

    return launch_data


def _extract_autonomous_world_metadata(filepath: str) -> Dict[str, Any]:
    """Extract autonomous metadata from Gazebo world files."""
    world_data = {'autonomous_world_format_present': True}

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Extract world properties
        if root.tag == 'world':
            world_name = root.get('name')
            if world_name:
                world_data['autonomous_world_name'] = world_name

        # Count world elements
        roads = root.findall('.//road')
        world_data['autonomous_world_road_count'] = len(roads)

        traffic_lights = root.findall('.//traffic_light')
        world_data['autonomous_world_traffic_light_count'] = len(traffic_lights)

        stop_signs = root.findall('.//stop_sign')
        world_data['autonomous_world_stop_sign_count'] = len(stop_signs)

        # Extract vehicle spawn points
        spawn_points = root.findall('.//spawn')
        world_data['autonomous_world_spawn_point_count'] = len(spawn_points)

        # Extract pedestrian areas
        pedestrians = root.findall('.//pedestrian')
        world_data['autonomous_world_pedestrian_count'] = len(pedestrians)

        # Extract weather conditions
        weather = root.find('.//weather')
        if weather is not None:
            world_data['autonomous_world_weather_configured'] = True

            # Extract weather properties
            if weather.get('sunrise'):
                world_data['autonomous_world_sunrise'] = weather.get('sunrise')
            if weather.get('sunset'):
                world_data['autonomous_world_sunset'] = weather.get('sunset')

        # Extract time of day
        time_of_day = root.find('.//time')
        if time_of_day is not None:
            world_data['autonomous_world_time_configured'] = True

            if time_of_day.get('hour'):
                world_data['autonomous_world_hour'] = time_of_day.get('hour')

    except Exception as e:
        world_data['autonomous_world_extraction_error'] = str(e)

    return world_data


def _extract_rosbag_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from ROS bag files."""
    rosbag_data = {'autonomous_rosbag_format_present': True}

    try:
        # Basic file information
        stat_info = Path(filepath).stat()
        rosbag_data['autonomous_rosbag_file_size'] = stat_info.st_size

        file_ext = Path(filepath).suffix.lower()
        if file_ext == '.bag':
            rosbag_data['autonomous_rosbag_version'] = 'ros1'
        elif file_ext == '.db3':
            rosbag_data['autonomous_rosbag_version'] = 'ros2'

        # Try to read basic bag info using rosbag API if available
        try:
            if file_ext == '.bag':
                import rosbag
                bag = rosbag.Bag(filepath, 'r')
                info = bag.get_type_and_topic_info()

                rosbag_data['autonomous_rosbag_topic_count'] = len(info.topics)
                rosbag_data['autonomous_rosbag_message_count'] = info.msg_count

                # Extract topic information
                topics = {}
                for topic_name, topic_info in info.topics.items():
                    topics[topic_name] = {
                        'type': topic_info.msg_type,
                        'count': topic_info.message_count
                    }

                if topics:
                    rosbag_data['autonomous_rosbag_topics'] = topics

                # Extract message types
                msg_types = {}
                for topic_info in info.topics.values():
                    msg_type = topic_info.msg_type
                    msg_types[msg_type] = msg_types.get(msg_type, 0) + topic_info.message_count

                if msg_types:
                    rosbag_data['autonomous_rosbag_message_types'] = msg_types

                bag.close()

            elif file_ext == '.db3':
                # For ROS2 bag files, we can try to get basic info
                rosbag_data['autonomous_rosbag_format'] = 'ros2'

        except ImportError:
            rosbag_data['autonomous_rosbag_api_unavailable'] = True
        except Exception as e:
            rosbag_data['autonomous_rosbag_read_error'] = str(e)

    except Exception as e:
        rosbag_data['autonomous_rosbag_extraction_error'] = str(e)

    return rosbag_data


def _extract_general_autonomous_properties(filepath: str) -> Dict[str, Any]:
    """Extract general autonomous file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['autonomous_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['autonomous_filename'] = filename

        # Check for autonomous-specific naming patterns
        autonomous_indicators = [
            'autonomous', 'vehicle', 'drone', 'planning', 'navigation',
            'perception', 'control', 'sensor', 'fusion', 'localization'
        ]
        if any(indicator in filename.lower() for indicator in autonomous_indicators):
            props['autonomous_filename_suggests_autonomous'] = True

        # Extract version numbers from filename
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['autonomous_file_version_hint'] = version_match.group(1)

    except Exception:
        pass

    return props


def _analyze_autonomous_components(filepath: str) -> Dict[str, Any]:
    """Analyze autonomous system components and capabilities."""
    analysis = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(8192)  # Read first 8KB

        # Analyze autonomous system type
        system_type_indicators = {
            'autonomous_vehicle': ['vehicle', 'car', 'truck', 'bus', 'autonomous', 'selfdriving'],
            'drone_uav': ['drone', 'uav', 'quadcopter', 'multirotor', 'flight'],
            'ugv': ['ugv', 'ground_vehicle', 'mobile_robot', 'wheeled'],
            'autonomous_robot': ['robot', 'manipulator', 'arm', 'mobile'],
        }

        detected_system_types = {}
        for system_type, indicators in system_type_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_system_types[system_type] = count

        if detected_system_types:
            # Find primary system type
            primary_type = max(detected_system_types.items(), key=lambda x: x[1])[0]
            analysis['autonomous_primary_system_type'] = primary_type

        # Analyze sensor suite
        sensor_indicators = {
            'lidar': ['lidar', 'velodyne', 'sick', 'pointcloud', 'pcl'],
            'radar': ['radar', 'delphi', 'conti', 'bosch'],
            'camera': ['camera', 'vision', 'opencv', 'cv'],
            'imu': ['imu', 'gyroscope', 'accelerometer', 'xsens'],
            'gps': ['gps', 'gnss', 'rtk', 'ublox'],
            'ultrasonic': ['ultrasonic', 'sonar', 'proximity'],
        }

        detected_sensors = {}
        for sensor_type, indicators in sensor_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_sensors[sensor_type] = count

        if detected_sensors:
            analysis['autonomous_detected_sensors'] = detected_sensors

        # Analyze autonomous capabilities
        capability_indicators = {
            'path_planning': ['path_planning', 'planning', 'a_star', 'rrt'],
            'localization': ['localization', 'slam', 'ekf', 'ukf', 'particle_filter'],
            'perception': ['perception', 'detection', 'tracking', 'segmentation'],
            'control': ['control', 'pid', 'mpc', 'lqr', 'control_system'],
            'sensor_fusion': ['sensor_fusion', 'kalman', 'fusion', 'data_fusion'],
            'decision_making': ['decision', 'behavior', 'fsm', 'planning'],
        }

        detected_capabilities = {}
        for capability, indicators in capability_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_capabilities[capability] = count

        if detected_capabilities:
            analysis['autonomous_system_capabilities'] = detected_capabilities

        # Check for simulation environment
        if any(term in content.lower() for term in ['gazebo', 'carla', 'airsim', 'simulation', 'virtual']):
            analysis['autonomous_simulation_environment'] = True

        # Check for real hardware deployment
        if any(term in content.lower() for term in ['hardware', 'real', 'physical', 'deployment', 'production']):
            analysis['autonomous_real_hardware'] = True

        # Check for safety systems
        if any(term in content.lower() for term in ['safety', 'failsafe', 'emergency', 'backup', 'redundant']):
            analysis['autonomous_safety_systems'] = True

        # Estimate autonomy level (SAE levels)
        autonomy_indicators = {
            'level_0': ['manual', 'no_automation'],
            'level_1': ['driver_assistance', 'cruise_control'],
            'level_2': ['partial_automation', 'autopilot'],
            'level_3': ['conditional_automation', 'hands_off'],
            'level_4': ['high_automation', 'geo_fenced'],
            'level_5': ['full_automation', 'unrestricted'],
        }

        detected_levels = {}
        for level, indicators in autonomy_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_levels[level] = count

        if detected_levels:
            # Find highest autonomy level mentioned
            level_order = ['level_0', 'level_1', 'level_2', 'level_3', 'level_4', 'level_5']
            for level in reversed(level_order):
                if level in detected_levels:
                    analysis['autonomous_estimated_level'] = level
                    break

    except Exception:
        pass

    return analysis


def get_autonomous_field_count() -> int:
    """Return the number of fields extracted by autonomous metadata."""
    # Format detection (5)
    detection_fields = 5

    # YAML specific (15)
    yaml_fields = 15

    # JSON specific (12)
    json_fields = 12

    # XML specific (12)
    xml_fields = 12

    # Code specific (12)
    code_fields = 12

    # Launch specific (10)
    launch_fields = 10

    # World specific (12)
    world_fields = 12

    # ROS bag specific (10)
    rosbag_fields = 10

    # General properties (6)
    general_fields = 6

    # Autonomous analysis (12)
    analysis_fields = 12

    return detection_fields + yaml_fields + json_fields + xml_fields + code_fields + launch_fields + world_fields + rosbag_fields + general_fields + analysis_fields


# Integration point for metadata_engine.py
def extract_autonomous_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for autonomous metadata extraction."""
    return extract_autonomous_metadata(filepath)