#!/usr/bin/env python3
"""
Industrial and Manufacturing Metadata Extraction Module - Ultimate Edition

Extracts comprehensive metadata from industrial and manufacturing data including:
- CAD and Engineering Files (AutoCAD, SolidWorks, Inventor, Fusion 360)
- Manufacturing Data (CNC programs, G-code, toolpath data)
- Quality Control Data (measurement reports, inspection data, CMM data)
- Industrial IoT Sensor Data (temperature, pressure, vibration, flow)
- Process Control Data (SCADA, PLC data, HMI configurations)
- Supply Chain Data (inventory, logistics, tracking data)
- Maintenance Records (equipment logs, service data, failure analysis)
- Safety and Compliance Data (MSDS, safety reports, regulatory data)
- Production Planning Data (schedules, capacity, resource allocation)
- Energy Management Data (power consumption, efficiency metrics)
- Robotics and Automation Data (robot programs, motion data)
- Materials and Specifications (material properties, test data, certifications)

Author: MetaExtract Team
Version: 1.0.0
"""

import os
import json
import struct
import logging
import xml.etree.ElementTree as ET
import csv
import re
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime
import tempfile
import hashlib

logger = logging.getLogger(__name__)

# Library availability checks
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def extract_industrial_manufacturing_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive industrial and manufacturing metadata"""
    
    result = {
        "available": True,
        "industrial_type": "unknown",
        "cad_engineering": {},
        "manufacturing_data": {},
        "quality_control": {},
        "iot_sensor_data": {},
        "process_control": {},
        "supply_chain": {},
        "maintenance_records": {},
        "safety_compliance": {},
        "production_planning": {},
        "energy_management": {},
        "robotics_automation": {},
        "materials_specs": {},
        "industrial_standards": {},
        "performance_metrics": {}
    }
    
    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()
        
        # CAD and Engineering Files
        if file_ext in ['.dwg', '.dxf', '.step', '.stp', '.iges', '.igs', '.sldprt', '.sldasm', '.ipt', '.iam']:
            result["industrial_type"] = "cad_engineering"
            cad_result = _analyze_cad_engineering(filepath, file_ext)
            if cad_result:
                result["cad_engineering"].update(cad_result)
        
        # Manufacturing Data
        elif file_ext in ['.nc', '.cnc', '.gcode', '.tap', '.mpf'] or any(term in filename for term in ['cnc', 'machining', 'toolpath']):
            result["industrial_type"] = "manufacturing"
            manufacturing_result = _analyze_manufacturing_data(filepath, file_ext)
            if manufacturing_result:
                result["manufacturing_data"].update(manufacturing_result)
        
        # Quality Control Data
        elif any(term in filename for term in ['quality', 'inspection', 'measurement', 'cmm', 'qc']):
            result["industrial_type"] = "quality_control"
            qc_result = _analyze_quality_control_data(filepath, file_ext)
            if qc_result:
                result["quality_control"].update(qc_result)
        
        # Industrial IoT Sensor Data
        elif any(term in filename for term in ['sensor', 'iot', 'telemetry', 'monitoring', 'scada']):
            result["industrial_type"] = "iot_sensor"
            iot_result = _analyze_iot_sensor_data(filepath, file_ext)
            if iot_result:
                result["iot_sensor_data"].update(iot_result)
        
        # Process Control Data
        elif any(term in filename for term in ['plc', 'hmi', 'process', 'control', 'automation']):
            result["industrial_type"] = "process_control"
            # For now, just basic file analysis since we haven't implemented the full function
            result["process_control"] = {
                "process_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['plc', 'hmi', 'process', 'control', 'automation'] if term in filename]
                }
            }
        
        # Supply Chain Data
        elif any(term in filename for term in ['inventory', 'logistics', 'supply', 'warehouse', 'shipping']):
            result["industrial_type"] = "supply_chain"
            # For now, just basic file analysis since we haven't implemented the full function
            result["supply_chain"] = {
                "supply_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['inventory', 'logistics', 'supply', 'warehouse', 'shipping'] if term in filename]
                }
            }
        
        # Maintenance Records
        elif any(term in filename for term in ['maintenance', 'service', 'repair', 'failure', 'downtime']):
            result["industrial_type"] = "maintenance"
            # For now, just basic file analysis since we haven't implemented the full function
            result["maintenance_records"] = {
                "maintenance_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['maintenance', 'service', 'repair', 'failure', 'downtime'] if term in filename]
                }
            }
        
        # Safety and Compliance Data
        elif any(term in filename for term in ['safety', 'msds', 'compliance', 'regulatory', 'hazard']):
            result["industrial_type"] = "safety_compliance"
            # For now, just basic file analysis since we haven't implemented the full function
            result["safety_compliance"] = {
                "safety_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['safety', 'msds', 'compliance', 'regulatory', 'hazard'] if term in filename]
                }
            }
        
        # Production Planning Data
        elif any(term in filename for term in ['production', 'planning', 'schedule', 'capacity', 'resource']):
            result["industrial_type"] = "production_planning"
            # For now, just basic file analysis since we haven't implemented the full function
            result["production_planning"] = {
                "production_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['production', 'planning', 'schedule', 'capacity', 'resource'] if term in filename]
                }
            }
        
        # Energy Management Data
        elif any(term in filename for term in ['energy', 'power', 'consumption', 'efficiency', 'utility']):
            result["industrial_type"] = "energy_management"
            # For now, just basic file analysis since we haven't implemented the full function
            result["energy_management"] = {
                "energy_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['energy', 'power', 'consumption', 'efficiency', 'utility'] if term in filename]
                }
            }
        
        # Robotics and Automation Data
        elif any(term in filename for term in ['robot', 'automation', 'motion', 'trajectory', 'program']):
            result["industrial_type"] = "robotics_automation"
            # For now, just basic file analysis since we haven't implemented the full function
            result["robotics_automation"] = {
                "robotics_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['robot', 'automation', 'motion', 'trajectory', 'program'] if term in filename]
                }
            }
        
        # Materials and Specifications
        elif any(term in filename for term in ['material', 'spec', 'properties', 'test', 'certification']):
            result["industrial_type"] = "materials_specs"
            # For now, just basic file analysis since we haven't implemented the full function
            result["materials_specs"] = {
                "materials_analysis": {
                    "file_type": file_ext,
                    "detected_keywords": [term for term in ['material', 'spec', 'properties', 'test', 'certification'] if term in filename]
                }
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in industrial manufacturing analysis: {e}")
        return {"available": False, "error": str(e)}

def _analyze_cad_engineering(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze CAD and engineering files"""
    try:
        result = {
            "cad_analysis": {
                "software": "unknown",
                "file_format": file_ext,
                "drawing_info": {},
                "geometry_data": {},
                "material_properties": {},
                "dimensions": {},
                "annotations": {},
                "version_info": {}
            }
        }
        
        # Detect CAD software from file extension
        software_map = {
            '.dwg': 'AutoCAD',
            '.dxf': 'AutoCAD/Generic CAD',
            '.step': 'STEP (ISO 10303)',
            '.stp': 'STEP (ISO 10303)',
            '.iges': 'IGES',
            '.igs': 'IGES',
            '.sldprt': 'SolidWorks Part',
            '.sldasm': 'SolidWorks Assembly',
            '.ipt': 'Autodesk Inventor Part',
            '.iam': 'Autodesk Inventor Assembly'
        }
        
        result["cad_analysis"]["software"] = software_map.get(file_ext, "unknown")
        
        # DXF file analysis (ASCII format)
        if file_ext == '.dxf':
            dxf_result = _analyze_dxf_file(filepath)
            if dxf_result:
                result["cad_analysis"].update(dxf_result)
        
        # STEP file analysis
        elif file_ext in ['.step', '.stp']:
            step_result = _analyze_step_file(filepath)
            if step_result:
                result["cad_analysis"].update(step_result)
        
        return result
        
    except Exception as e:
        logger.error(f"CAD engineering analysis error: {e}")
        return {}

def _analyze_dxf_file(filepath: str) -> Dict[str, Any]:
    """Analyze DXF (Drawing Exchange Format) files"""
    try:
        result = {
            "dxf_info": {
                "version": "unknown",
                "units": "unknown",
                "entities": {},
                "layers": [],
                "blocks": [],
                "drawing_limits": {}
            }
        }
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Parse DXF structure
        entity_counts = {}
        layers = set()
        blocks = set()
        
        i = 0
        while i < len(lines) - 1:
            code = lines[i].strip()
            value = lines[i + 1].strip()
            
            # Version information
            if code == '1' and 'AC' in value:
                result["dxf_info"]["version"] = value
            
            # Units
            elif code == '70' and i > 0 and lines[i-2].strip() == '$INSUNITS':
                units_map = {
                    '0': 'Unitless',
                    '1': 'Inches',
                    '2': 'Feet',
                    '4': 'Millimeters',
                    '5': 'Centimeters',
                    '6': 'Meters'
                }
                result["dxf_info"]["units"] = units_map.get(value, f"Unknown ({value})")
            
            # Entity types
            elif code == '0':
                entity_type = value
                if entity_type in ['LINE', 'CIRCLE', 'ARC', 'POLYLINE', 'TEXT', 'DIMENSION']:
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            # Layers
            elif code == '8':
                layers.add(value)
            
            # Blocks
            elif code == '2' and i > 0 and lines[i-2].strip() == 'BLOCK':
                blocks.add(value)
            
            i += 2
        
        result["dxf_info"]["entities"] = entity_counts
        result["dxf_info"]["layers"] = sorted(list(layers))
        result["dxf_info"]["blocks"] = sorted(list(blocks))
        
        # Calculate complexity
        total_entities = sum(entity_counts.values())
        result["dxf_info"]["complexity"] = {
            "total_entities": total_entities,
            "layer_count": len(layers),
            "block_count": len(blocks),
            "complexity_level": "high" if total_entities > 1000 else "medium" if total_entities > 100 else "low"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"DXF analysis error: {e}")
        return {}

def _analyze_step_file(filepath: str) -> Dict[str, Any]:
    """Analyze STEP (Standard for Exchange of Product Data) files"""
    try:
        result = {
            "step_info": {
                "version": "unknown",
                "schema": "unknown",
                "entities": {},
                "product_info": {},
                "geometric_data": {}
            }
        }
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)  # Read first 10KB for header analysis
        
        lines = content.split('\n')
        
        # Parse STEP header
        in_header = False
        for line in lines:
            line = line.strip()
            
            if line == 'HEADER;':
                in_header = True
                continue
            elif line == 'ENDSEC;':
                in_header = False
                continue
            
            if in_header:
                # Extract file description
                if line.startswith('FILE_DESCRIPTION'):
                    desc_match = re.search(r"'([^']*)'", line)
                    if desc_match:
                        result["step_info"]["description"] = desc_match.group(1)
                
                # Extract file name
                elif line.startswith('FILE_NAME'):
                    name_match = re.search(r"'([^']*)'", line)
                    if name_match:
                        result["step_info"]["filename"] = name_match.group(1)
                
                # Extract file schema
                elif line.startswith('FILE_SCHEMA'):
                    schema_match = re.search(r"'([^']*)'", line)
                    if schema_match:
                        result["step_info"]["schema"] = schema_match.group(1)
        
        # Count entity types in data section
        entity_counts = {}
        data_lines = [line for line in lines if line.startswith('#')]
        
        for line in data_lines[:1000]:  # Analyze first 1000 entities
            # Extract entity type
            if '=' in line:
                entity_part = line.split('=', 1)[1].strip()
                if '(' in entity_part:
                    entity_type = entity_part.split('(')[0].strip()
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        result["step_info"]["entities"] = entity_counts
        result["step_info"]["total_entities"] = sum(entity_counts.values())
        
        return result
        
    except Exception as e:
        logger.error(f"STEP analysis error: {e}")
        return {}

def _analyze_manufacturing_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze manufacturing data files (CNC, G-code, etc.)"""
    try:
        result = {
            "manufacturing_analysis": {
                "program_type": "unknown",
                "machine_info": {},
                "tooling_data": {},
                "operations": {},
                "material_info": {},
                "quality_parameters": {},
                "cycle_time": {}
            }
        }
        
        # G-code analysis
        if file_ext in ['.nc', '.cnc', '.gcode', '.tap']:
            gcode_result = _analyze_gcode_program(filepath)
            if gcode_result:
                result["manufacturing_analysis"].update(gcode_result)
                result["manufacturing_analysis"]["program_type"] = "gcode"
        
        return result
        
    except Exception as e:
        logger.error(f"Manufacturing data analysis error: {e}")
        return {}

def _analyze_gcode_program(filepath: str) -> Dict[str, Any]:
    """Analyze G-code CNC programs"""
    try:
        result = {
            "gcode_info": {
                "total_lines": 0,
                "commands": {},
                "tools_used": [],
                "coordinates": {},
                "feed_rates": [],
                "spindle_speeds": [],
                "estimated_time": None
            }
        }
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        result["gcode_info"]["total_lines"] = len(lines)
        
        command_counts = {}
        tools = set()
        feed_rates = []
        spindle_speeds = []
        x_coords = []
        y_coords = []
        z_coords = []
        
        for line in lines:
            line = line.strip().upper()
            
            # Skip comments and empty lines
            if not line or line.startswith('(') or line.startswith(';'):
                continue
            
            # Extract G-codes and M-codes
            g_codes = re.findall(r'G\d+', line)
            m_codes = re.findall(r'M\d+', line)
            
            for code in g_codes + m_codes:
                command_counts[code] = command_counts.get(code, 0) + 1
            
            # Extract tool numbers
            tool_match = re.search(r'T(\d+)', line)
            if tool_match:
                tools.add(int(tool_match.group(1)))
            
            # Extract feed rates
            feed_match = re.search(r'F([\d.]+)', line)
            if feed_match:
                feed_rates.append(float(feed_match.group(1)))
            
            # Extract spindle speeds
            spindle_match = re.search(r'S(\d+)', line)
            if spindle_match:
                spindle_speeds.append(int(spindle_match.group(1)))
            
            # Extract coordinates
            x_match = re.search(r'X([-\d.]+)', line)
            if x_match:
                x_coords.append(float(x_match.group(1)))
            
            y_match = re.search(r'Y([-\d.]+)', line)
            if y_match:
                y_coords.append(float(y_match.group(1)))
            
            z_match = re.search(r'Z([-\d.]+)', line)
            if z_match:
                z_coords.append(float(z_match.group(1)))
        
        result["gcode_info"]["commands"] = command_counts
        result["gcode_info"]["tools_used"] = sorted(list(tools))
        
        if feed_rates:
            result["gcode_info"]["feed_rates"] = {
                "min": min(feed_rates),
                "max": max(feed_rates),
                "average": sum(feed_rates) / len(feed_rates)
            }
        
        if spindle_speeds:
            result["gcode_info"]["spindle_speeds"] = {
                "min": min(spindle_speeds),
                "max": max(spindle_speeds),
                "average": sum(spindle_speeds) / len(spindle_speeds)
            }
        
        # Calculate work envelope
        if x_coords and y_coords and z_coords:
            result["gcode_info"]["coordinates"] = {
                "x_range": [min(x_coords), max(x_coords)],
                "y_range": [min(y_coords), max(y_coords)],
                "z_range": [min(z_coords), max(z_coords)],
                "work_envelope": {
                    "x_size": max(x_coords) - min(x_coords),
                    "y_size": max(y_coords) - min(y_coords),
                    "z_size": max(z_coords) - min(z_coords)
                }
            }
        
        return result
        
    except Exception as e:
        logger.error(f"G-code analysis error: {e}")
        return {}

def _analyze_quality_control_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze quality control and inspection data"""
    try:
        result = {
            "qc_analysis": {
                "inspection_type": "unknown",
                "measurement_data": {},
                "statistical_analysis": {},
                "tolerance_analysis": {},
                "pass_fail_results": {},
                "equipment_info": {}
            }
        }
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            # Analyze CSV quality control data
            df = pd.read_csv(filepath, nrows=10000)  # Limit for performance
            
            # Look for measurement columns
            measurement_columns = []
            for col in df.columns:
                if any(term in col.lower() for term in ['measurement', 'dimension', 'tolerance', 'actual', 'nominal']):
                    measurement_columns.append(col)
            
            if measurement_columns:
                result["qc_analysis"]["measurement_data"] = {
                    "measurement_columns": measurement_columns,
                    "total_measurements": len(df),
                    "measurement_count": len(measurement_columns)
                }
                
                # Statistical analysis of measurements
                numeric_cols = df[measurement_columns].select_dtypes(include=[np.number])
                if not numeric_cols.empty:
                    result["qc_analysis"]["statistical_analysis"] = {
                        "mean_values": numeric_cols.mean().to_dict(),
                        "std_values": numeric_cols.std().to_dict(),
                        "min_values": numeric_cols.min().to_dict(),
                        "max_values": numeric_cols.max().to_dict()
                    }
                    
                    # Calculate Cp/Cpk if tolerance data is available
                    for col in numeric_cols.columns:
                        col_data = numeric_cols[col].dropna()
                        if len(col_data) > 1:
                            # Basic process capability (assuming ±3σ tolerance)
                            mean_val = col_data.mean()
                            std_val = col_data.std()
                            if std_val > 0:
                                cp = (6 * std_val) / (col_data.max() - col_data.min()) if col_data.max() != col_data.min() else 0
                                result["qc_analysis"]["statistical_analysis"][f"{col}_cp"] = cp
            
            # Look for pass/fail results
            result_columns = [col for col in df.columns if any(term in col.lower() for term in ['pass', 'fail', 'result', 'status'])]
            if result_columns:
                for col in result_columns:
                    value_counts = df[col].value_counts().to_dict()
                    result["qc_analysis"]["pass_fail_results"][col] = value_counts
        
        return result
        
    except Exception as e:
        logger.error(f"Quality control analysis error: {e}")
        return {}

def _analyze_iot_sensor_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze Industrial IoT sensor data"""
    try:
        result = {
            "iot_analysis": {
                "sensor_types": [],
                "data_format": file_ext,
                "time_series_info": {},
                "sensor_readings": {},
                "anomaly_detection": {},
                "data_quality": {},
                "communication_protocol": {}
            }
        }
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Detect sensor types from column names
            sensor_indicators = {
                'temperature': ['temp', 'temperature', 'celsius', 'fahrenheit', 'kelvin'],
                'pressure': ['pressure', 'bar', 'psi', 'pascal', 'kpa', 'mpa'],
                'vibration': ['vibration', 'acceleration', 'velocity', 'displacement'],
                'flow': ['flow', 'rate', 'volume', 'gpm', 'lpm'],
                'level': ['level', 'height', 'depth'],
                'humidity': ['humidity', 'rh', 'moisture'],
                'voltage': ['voltage', 'volt', 'v'],
                'current': ['current', 'amp', 'ampere', 'a'],
                'power': ['power', 'watt', 'kw', 'mw'],
                'speed': ['speed', 'rpm', 'velocity']
            }
            
            detected_sensors = []
            for sensor_type, indicators in sensor_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_sensors.append(sensor_type)
                        break
            
            result["iot_analysis"]["sensor_types"] = list(set(detected_sensors))
            
            # Time series analysis
            time_columns = [col for col in df.columns if any(time_word in col.lower() 
                           for time_word in ['time', 'timestamp', 'date', 'datetime'])]
            
            if time_columns:
                result["iot_analysis"]["time_series_info"] = {
                    "has_timestamps": True,
                    "time_columns": time_columns,
                    "data_points": len(df),
                    "sampling_info": "regular" if len(df) > 1 else "unknown"
                }
            
            # Sensor reading statistics
            numeric_cols = df.select_dtypes(include=[np.number])
            if not numeric_cols.empty:
                result["iot_analysis"]["sensor_readings"] = {
                    "numeric_sensors": len(numeric_cols.columns),
                    "reading_ranges": {
                        col: {"min": float(numeric_cols[col].min()), "max": float(numeric_cols[col].max())}
                        for col in numeric_cols.columns
                    },
                    "missing_data": numeric_cols.isnull().sum().to_dict()
                }
                
                # Simple anomaly detection (values beyond 3 standard deviations)
                anomalies = {}
                for col in numeric_cols.columns:
                    col_data = numeric_cols[col].dropna()
                    if len(col_data) > 1:
                        mean_val = col_data.mean()
                        std_val = col_data.std()
                        if std_val > 0:
                            outliers = col_data[(col_data < mean_val - 3*std_val) | (col_data > mean_val + 3*std_val)]
                            anomalies[col] = len(outliers)
                
                result["iot_analysis"]["anomaly_detection"] = anomalies
        
        return result
        
    except Exception as e:
        logger.error(f"IoT sensor analysis error: {e}")
        return {}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_industrial_manufacturing_metadata(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python industrial_manufacturing_ultimate.py <industrial_file>")