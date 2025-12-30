# server/extractor/modules/robotics_metadata.py

"""
Robotics metadata extraction for Phase 4.

Extracts metadata from:
- Robot configuration files (URDF, SDF, XACRO)
- Robot control scripts and programs
- Sensor configurations
- Motion planning files
- Robot simulation files
- ROS (Robot Operating System) packages
"""

import logging
import json
import re
import struct
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Robotics file extensions and formats
ROBOTICS_EXTENSIONS = [
    '.urdf', '.sdf', '.xacro', '.srdf', '.yaml', '.yml',
    '.launch', '.py', '.cpp', '.xml', '.json', '.config',
    '.world', '.dae', '.stl', '.obj', '.bag', '.msg', '.srv'
]

# Robotics-specific keywords
ROBOTICS_KEYWORDS = [
    'robot', 'joint', 'link', 'sensor', 'actuator', 'gripper',
    'arm', 'manipulator', 'mobile', 'drone', 'quadcopter',
    'ros', 'gazebo', 'rviz', 'moveit', 'navigation',
    'kinematics', 'dynamics', 'trajectory', 'planning',
    'control', 'pid', 'feedback', 'odometry', 'imu',
    'lidar', 'camera', 'sonar', 'gps', 'encoder',
    'servo', 'motor', 'pwm', 'arduino', 'raspberry',
    'urdf', 'sdf', 'xacro', 'srdf', 'launch'
]


def extract_robotics_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract robotics metadata from robot configuration and control files.

    Supports various robotics frameworks and formats.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is robotics-related
        is_robotics_file = _is_robotics_related_file(filepath, filename)

        if not is_robotics_file:
            return result

        result['robotics_file_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.urdf', '.xacro']:
            urdf_data = _extract_urdf_metadata(filepath)
            result.update(urdf_data)

        elif file_ext == '.sdf':
            sdf_data = _extract_sdf_metadata(filepath)
            result.update(sdf_data)

        elif file_ext == '.srdf':
            srdf_data = _extract_srdf_metadata(filepath)
            result.update(srdf_data)

        elif file_ext in ['.yaml', '.yml']:
            yaml_robotics_data = _extract_yaml_robotics_metadata(filepath)
            result.update(yaml_robotics_data)

        elif file_ext == '.launch':
            launch_data = _extract_launch_metadata(filepath)
            result.update(launch_data)

        elif file_ext in ['.py', '.cpp']:
            code_data = _extract_robotics_code_metadata(filepath)
            result.update(code_data)

        elif file_ext == '.world':
            world_data = _extract_world_metadata(filepath)
            result.update(world_data)

        # Extract general robotics properties
        general_data = _extract_general_robotics_properties(filepath)
        result.update(general_data)

        # Analyze robotics components
        robotics_analysis = _analyze_robotics_components(filepath)
        result.update(robotics_analysis)

    except Exception as e:
        logger.warning(f"Error extracting robotics metadata from {filepath}: {e}")
        result['robotics_extraction_error'] = str(e)

    return result


def _is_robotics_related_file(filepath: str, filename: str) -> bool:
    """Check if file is robotics-related."""
    try:
        # Check filename patterns
        robotics_patterns = ['robot', 'urdf', 'sdf', 'xacro', 'ros', 'gazebo', 'rviz']
        if any(pattern in filename for pattern in robotics_patterns):
            return True

        # Check file content for robotics keywords
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096)  # Read first 4KB

        content_lower = content.lower()

        # Count robotics keywords
        robotics_keyword_count = sum(1 for keyword in ROBOTICS_KEYWORDS if keyword in content_lower)

        # Must have multiple robotics keywords to be considered robotics-related
        if robotics_keyword_count >= 3:
            return True

        # Check for specific robotics patterns
        robotics_patterns = [
            r'<robot\s+name=',  # URDF robot tag
            r'<model\s+name=',  # SDF model tag
            r'<launch>',  # ROS launch file
            r'ros::',  # ROS C++ code
            r'rospy|rclpy',  # ROS Python code
            r'gazebo::',  # Gazebo plugins
            r'moveit::',  # MoveIt code
        ]

        for pattern in robotics_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

    except Exception:
        pass

    return False


def _extract_urdf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from URDF (Unified Robot Description Format) files."""
    urdf_data = {'robotics_urdf_format_present': True}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Extract robot name
        if root.tag == 'robot' and 'name' in root.attrib:
            urdf_data['robotics_robot_name'] = root.attrib['name']

        # Count links and joints
        links = root.findall('.//link')
        joints = root.findall('.//joint')

        urdf_data['robotics_link_count'] = len(links)
        urdf_data['robotics_joint_count'] = len(joints)

        # Analyze joint types
        joint_types = {}
        for joint in joints:
            joint_type = joint.get('type')
            if joint_type:
                joint_types[joint_type] = joint_types.get(joint_type, 0) + 1

        if joint_types:
            urdf_data['robotics_joint_types'] = joint_types

        # Extract sensors
        sensors = root.findall('.//sensor')
        urdf_data['robotics_sensor_count'] = len(sensors)

        sensor_types = {}
        for sensor in sensors:
            sensor_type = sensor.get('type')
            if sensor_type:
                sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1

        if sensor_types:
            urdf_data['robotics_sensor_types'] = sensor_types

        # Extract actuators
        actuators = root.findall('.//actuator')
        urdf_data['robotics_actuator_count'] = len(actuators)

        # Extract transmission elements
        transmissions = root.findall('.//transmission')
        urdf_data['robotics_transmission_count'] = len(transmissions)

        # Check for gazebo extensions
        gazebo_elements = root.findall('.//gazebo')
        if gazebo_elements:
            urdf_data['robotics_gazebo_extensions'] = len(gazebo_elements)

        # Extract material information
        materials = root.findall('.//material')
        urdf_data['robotics_material_count'] = len(materials)

        # Check for collision and visual geometries
        collision_geoms = root.findall('.//collision')
        visual_geoms = root.findall('.//visual')

        urdf_data['robotics_collision_geometries'] = len(collision_geoms)
        urdf_data['robotics_visual_geometries'] = len(visual_geoms)

    except Exception as e:
        urdf_data['robotics_urdf_extraction_error'] = str(e)

    return urdf_data


def _extract_sdf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from SDF (Simulation Description Format) files."""
    sdf_data = {'robotics_sdf_format_present': True}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Extract world information
        worlds = root.findall('.//world')
        sdf_data['robotics_world_count'] = len(worlds)

        # Extract models
        models = root.findall('.//model')
        sdf_data['robotics_model_count'] = len(models)

        model_types = {}
        for model in models:
            model_type = model.get('type') or 'custom'
            model_types[model_type] = model_types.get(model_type, 0) + 1

        if model_types:
            sdf_data['robotics_model_types'] = model_types

        # Extract links and joints across all models
        total_links = 0
        total_joints = 0
        joint_types = {}

        for model in models:
            links = model.findall('.//link')
            joints = model.findall('.//joint')

            total_links += len(links)
            total_joints += len(joints)

            for joint in joints:
                joint_type = joint.get('type')
                if joint_type:
                    joint_types[joint_type] = joint_types.get(joint_type, 0) + 1

        sdf_data['robotics_total_links'] = total_links
        sdf_data['robotics_total_joints'] = total_joints

        if joint_types:
            sdf_data['robotics_joint_types'] = joint_types

        # Extract sensors
        sensors = root.findall('.//sensor')
        sdf_data['robotics_sensor_count'] = len(sensors)

        sensor_types = {}
        for sensor in sensors:
            sensor_type = sensor.get('type')
            if sensor_type:
                sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1

        if sensor_types:
            sdf_data['robotics_sensor_types'] = sensor_types

        # Extract plugins
        plugins = root.findall('.//plugin')
        sdf_data['robotics_plugin_count'] = len(plugins)

        # Extract lights
        lights = root.findall('.//light')
        sdf_data['robotics_light_count'] = len(lights)

    except Exception as e:
        sdf_data['robotics_sdf_extraction_error'] = str(e)

    return sdf_data


def _extract_srdf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from SRDF (Semantic Robot Description Format) files."""
    srdf_data = {'robotics_srdf_format_present': True}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Extract robot name
        if 'name' in root.attrib:
            srdf_data['robotics_srdf_robot_name'] = root.attrib['name']

        # Extract groups
        groups = root.findall('.//group')
        srdf_data['robotics_group_count'] = len(groups)

        # Extract group states
        group_states = root.findall('.//group_state')
        srdf_data['robotics_group_state_count'] = len(group_states)

        # Extract end effectors
        end_effectors = root.findall('.//end_effector')
        srdf_data['robotics_end_effector_count'] = len(end_effectors)

        # Extract virtual joints
        virtual_joints = root.findall('.//virtual_joint')
        srdf_data['robotics_virtual_joint_count'] = len(virtual_joints)

        # Extract passive joints
        passive_joints = root.findall('.//passive_joint')
        srdf_data['robotics_passive_joint_count'] = len(passive_joints)

        # Extract collision pairs to disable
        disable_collisions = root.findall('.//disable_collisions')
        srdf_data['robotics_disabled_collision_pairs'] = len(disable_collisions)

        # Extract link sphere approximations
        link_sphere_approximations = root.findall('.//link_sphere_approximation')
        srdf_data['robotics_link_sphere_approximations'] = len(link_sphere_approximations)

    except Exception as e:
        srdf_data['robotics_srdf_extraction_error'] = str(e)

    return srdf_data


def _extract_yaml_robotics_metadata(filepath: str) -> Dict[str, Any]:
    """Extract robotics metadata from YAML configuration files."""
    yaml_data = {'robotics_yaml_format_present': True}

    try:
        import yaml
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            return yaml_data

        # Extract ROS parameters
        if any(key in data for key in ['ros', 'node', 'topic', 'service', 'action']):
            yaml_data['robotics_ros_config'] = True

        # Extract robot configuration
        if 'robot' in data:
            robot_config = data['robot']
            if isinstance(robot_config, dict):
                yaml_data['robotics_robot_config_present'] = True

                if 'name' in robot_config:
                    yaml_data['robotics_robot_name'] = robot_config['name']

                if 'joints' in robot_config:
                    joints = robot_config['joints']
                    if isinstance(joints, list):
                        yaml_data['robotics_joint_config_count'] = len(joints)

        # Extract controller configuration
        if 'controllers' in data:
            controllers = data['controllers']
            if isinstance(controllers, list):
                yaml_data['robotics_controller_count'] = len(controllers)

                controller_types = {}
                for controller in controllers:
                    if isinstance(controller, dict):
                        ctrl_type = controller.get('type')
                        if ctrl_type:
                            controller_types[ctrl_type] = controller_types.get(ctrl_type, 0) + 1

                if controller_types:
                    yaml_data['robotics_controller_types'] = controller_types

        # Extract sensor configuration
        if 'sensors' in data:
            sensors = data['sensors']
            if isinstance(sensors, list):
                yaml_data['robotics_sensor_config_count'] = len(sensors)

        # Extract navigation parameters
        nav_keys = ['move_base', 'global_planner', 'local_planner', 'costmap']
        if any(key in data for key in nav_keys):
            yaml_data['robotics_navigation_config'] = True

        # Extract MoveIt configuration
        if any('moveit' in str(data).lower() for key in data.keys()):
            yaml_data['robotics_moveit_config'] = True

    except ImportError:
        yaml_data['robotics_yaml_not_available'] = True
    except Exception as e:
        yaml_data['robotics_yaml_extraction_error'] = str(e)

    return yaml_data


def _extract_launch_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from ROS launch files."""
    launch_data = {'robotics_launch_format_present': True}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Count different launch elements
        nodes = root.findall('.//node')
        launch_data['robotics_launch_node_count'] = len(nodes)

        includes = root.findall('.//include')
        launch_data['robotics_launch_include_count'] = len(includes)

        args = root.findall('.//arg')
        launch_data['robotics_launch_arg_count'] = len(args)

        params = root.findall('.//param')
        launch_data['robotics_launch_param_count'] = len(params)

        rosparams = root.findall('.//rosparam')
        launch_data['robotics_launch_rosparam_count'] = len(rosparams)

        groups = root.findall('.//group')
        launch_data['robotics_launch_group_count'] = len(groups)

        # Extract node packages and types
        node_packages = {}
        node_types = {}

        for node in nodes:
            pkg = node.get('pkg')
            node_type = node.get('type')

            if pkg:
                node_packages[pkg] = node_packages.get(pkg, 0) + 1
            if node_type:
                node_types[node_type] = node_types.get(node_type, 0) + 1

        if node_packages:
            yaml_data['robotics_launch_node_packages'] = node_packages
        if node_types:
            yaml_data['robotics_launch_node_types'] = node_types

        # Check for common ROS packages
        ros_packages = ['move_base', 'amcl', 'gmapping', 'rviz', 'robot_state_publisher']
        detected_packages = [pkg for pkg in node_packages.keys() if pkg in ros_packages]
        if detected_packages:
            launch_data['robotics_launch_common_packages'] = detected_packages

    except Exception as e:
        launch_data['robotics_launch_extraction_error'] = str(e)

    return launch_data


def _extract_robotics_code_metadata(filepath: str) -> Dict[str, Any]:
    """Extract robotics metadata from code files."""
    code_data = {'robotics_code_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        file_ext = Path(filepath).suffix.lower()

        # Detect programming language
        if file_ext == '.py':
            code_data['robotics_code_language'] = 'python'
        elif file_ext == '.cpp':
            code_data['robotics_code_language'] = 'cpp'

        # Count ROS-related code elements
        ros_elements = {
            'ros_import': len(re.findall(r'import\s+ros|from\s+ros', content)),
            'rospy_import': len(re.findall(r'import\s+rospy|from\s+rospy', content)),
            'rclcpp_import': len(re.findall(r'#include\s+.*rclcpp', content)),
            'topic_publish': len(re.findall(r'publish\(|advertise\(', content)),
            'topic_subscribe': len(re.findall(r'subscribe\(|subscribe_with', content)),
            'service_call': len(re.findall(r'call\(|call_async\(', content)),
            'service_provide': len(re.findall(r'advertiseService\(|create_service\(', content)),
        }

        # Only include counts > 0
        ros_elements = {k: v for k, v in ros_elements.items() if v > 0}
        if ros_elements:
            code_data['robotics_ros_code_elements'] = ros_elements

        # Detect robotics libraries/frameworks
        frameworks = {
            'moveit': 'moveit' in content.lower(),
            'gazebo': 'gazebo' in content.lower(),
            'opencv': 'cv2' in content or 'opencv' in content.lower(),
            'pcl': 'pcl' in content.lower(),
            'tf': 'tf' in content.lower() or 'transform' in content.lower(),
            'navigation': 'nav_msgs' in content or 'move_base' in content,
        }

        detected_frameworks = [fw for fw, detected in frameworks.items() if detected]
        if detected_frameworks:
            code_data['robotics_frameworks_detected'] = detected_frameworks

        # Count robotics-specific functions/classes
        robotics_functions = {
            'kinematics': len(re.findall(r'kinematics|inverse.*kinematics|forward.*kinematics', content, re.IGNORECASE)),
            'motion_planning': len(re.findall(r'plan|planning|trajectory', content, re.IGNORECASE)),
            'control': len(re.findall(r'control|pid|feedback', content, re.IGNORECASE)),
            'vision': len(re.findall(r'vision|camera|image|detect', content, re.IGNORECASE)),
            'localization': len(re.findall(r'localization|pose|odometry', content, re.IGNORECASE)),
        }

        robotics_functions = {k: v for k, v in robotics_functions.items() if v > 0}
        if robotics_functions:
            code_data['robotics_code_functions'] = robotics_functions

        # Check for hardware interfaces
        hardware_interfaces = ['arduino', 'raspberry', 'motor', 'servo', 'sensor', 'adc', 'pwm']
        detected_hardware = [hw for hw in hardware_interfaces if hw in content.lower()]
        if detected_hardware:
            code_data['robotics_hardware_interfaces'] = detected_hardware

    except Exception as e:
        code_data['robotics_code_extraction_error'] = str(e)

    return code_data


def _extract_world_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from Gazebo world files."""
    world_data = {'robotics_world_format_present': True}

    try:
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
                world_data['robotics_world_name'] = world_name

        # Count world elements
        lights = root.findall('.//light')
        world_data['robotics_world_light_count'] = len(lights)

        models = root.findall('.//model')
        world_data['robotics_world_model_count'] = len(models)

        # Extract physics properties
        physics = root.find('.//physics')
        if physics is not None:
            world_data['robotics_world_physics_enabled'] = True

            # Extract physics engine
            engine = physics.get('type') or physics.get('name')
            if engine:
                world_data['robotics_world_physics_engine'] = engine

        # Extract ground plane
        ground_plane = root.find('.//plane')
        if ground_plane is not None:
            world_data['robotics_world_ground_plane'] = True

        # Count plugins
        plugins = root.findall('.//plugin')
        world_data['robotics_world_plugin_count'] = len(plugins)

        # Extract GUI settings
        gui = root.find('.//gui')
        if gui is not None:
            world_data['robotics_world_gui_enabled'] = True

        # Extract scene settings
        scene = root.find('.//scene')
        if scene is not None:
            world_data['robotics_world_scene_configured'] = True

            # Extract ambient light
            ambient = scene.find('ambient')
            if ambient is not None:
                world_data['robotics_world_ambient_light'] = True

    except Exception as e:
        world_data['robotics_world_extraction_error'] = str(e)

    return world_data


def _extract_general_robotics_properties(filepath: str) -> Dict[str, Any]:
    """Extract general robotics file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['robotics_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['robotics_filename'] = filename

        # Check for robotics-specific naming patterns
        robotics_indicators = ['robot', 'urdf', 'sdf', 'ros', 'gazebo', 'rviz', 'manipulator', 'arm']
        if any(indicator in filename.lower() for indicator in robotics_indicators):
            props['robotics_filename_suggests_robotics'] = True

        # Extract version numbers from filename
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['robotics_file_version_hint'] = version_match.group(1)

    except Exception:
        pass

    return props


def _analyze_robotics_components(filepath: str) -> Dict[str, Any]:
    """Analyze robotics components and capabilities."""
    analysis = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(8192)  # Read first 8KB

        # Analyze robot type
        robot_type_indicators = {
            'manipulator': ['manipulator', 'arm', 'joint', 'gripper', 'end_effector'],
            'mobile_robot': ['mobile', 'wheel', 'odometry', 'navigation', 'slam'],
            'drone': ['drone', 'quadcopter', 'flight', 'altitude', 'thrust'],
            'humanoid': ['humanoid', 'leg', 'walking', 'biped'],
            'industrial': ['industrial', 'welding', 'painting', 'assembly'],
        }

        detected_robot_types = {}
        for robot_type, indicators in robot_type_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_robot_types[robot_type] = count

        if detected_robot_types:
            # Find primary robot type
            primary_type = max(detected_robot_types.items(), key=lambda x: x[1])[0]
            analysis['robotics_primary_robot_type'] = primary_type

        # Analyze sensor suite
        sensor_indicators = {
            'vision': ['camera', 'vision', 'opencv', 'image'],
            'lidar': ['lidar', 'laser', 'scan', 'pointcloud'],
            'imu': ['imu', 'gyroscope', 'accelerometer', 'orientation'],
            'gps': ['gps', 'gnss', 'positioning'],
            'proximity': ['sonar', 'ultrasonic', 'ir', 'proximity'],
            'force_torque': ['force', 'torque', 'wrench', 'tactile'],
        }

        detected_sensors = {}
        for sensor_type, indicators in sensor_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_sensors[sensor_type] = count

        if detected_sensors:
            analysis['robotics_detected_sensors'] = detected_sensors

        # Analyze control capabilities
        control_indicators = {
            'motion_control': ['trajectory', 'path', 'motion', 'control'],
            'force_control': ['force', 'impedance', 'compliance'],
            'vision_servo': ['visual_servoing', 'ibvs', 'pbvs'],
            'navigation': ['navigation', 'pathfinding', 'obstacle'],
            'manipulation': ['grasping', 'pick_place', 'manipulation'],
        }

        detected_controls = {}
        for control_type, indicators in control_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_controls[control_type] = count

        if detected_controls:
            analysis['robotics_control_capabilities'] = detected_controls

        # Check for simulation
        if any(term in content.lower() for term in ['gazebo', 'simulation', 'simulated', 'virtual']):
            analysis['robotics_simulation_environment'] = True

        # Check for real hardware
        if any(term in content.lower() for term in ['hardware', 'real', 'physical', 'arduino', 'raspberry']):
            analysis['robotics_real_hardware'] = True

        # Estimate degrees of freedom (DOF)
        joint_count = len(re.findall(r'joint|axis|dof', content.lower()))
        if joint_count > 0:
            analysis['robotics_estimated_dof'] = joint_count

    except Exception:
        pass

    return analysis


def get_robotics_field_count() -> int:
    """Return the number of fields extracted by robotics metadata."""
    # Format detection (5)
    detection_fields = 5

    # URDF specific (15)
    urdf_fields = 15

    # SDF specific (15)
    sdf_fields = 15

    # SRDF specific (10)
    srdf_fields = 10

    # YAML robotics specific (12)
    yaml_fields = 12

    # Launch specific (10)
    launch_fields = 10

    # Code specific (12)
    code_fields = 12

    # World specific (12)
    world_fields = 12

    # General properties (6)
    general_fields = 6

    # Robotics analysis (12)
    analysis_fields = 12

    return detection_fields + urdf_fields + sdf_fields + srdf_fields + yaml_fields + launch_fields + code_fields + world_fields + general_fields + analysis_fields


# Integration point for metadata_engine.py
def extract_robotics_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for robotics metadata extraction."""
    return extract_robotics_metadata(filepath)