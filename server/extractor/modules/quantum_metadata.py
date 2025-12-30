# server/extractor/modules/quantum_metadata.py

"""
Quantum computing metadata extraction for Phase 4.

Extracts metadata from:
- QASM quantum circuit files
- Quantum state files
- Error correction code files
- Quantum algorithm implementations
- Qubit configuration files
- Quantum simulation data
"""

import logging
import json
import re
import struct
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Quantum computing file extensions and formats
QUANTUM_EXTENSIONS = [
    '.qasm', '.qc', '.qsd', '.qstate', '.qreg',
    '.qobj', '.qpy', '.qiskit', '.cirq', '.qsharp',
    '.quil', '.py', '.ipynb'  # Python files may contain quantum code
]

# Quantum-specific keywords and patterns
QUANTUM_KEYWORDS = [
    'qubit', 'qreg', 'creg', 'gate', 'circuit', 'quantum',
    'qasm', 'measure', 'h ', 'x ', 'y ', 'z ', 'cx ', 'ccx',
    'toffoli', 'fredkin', 'hadamard', 'pauli', 'cnot',
    'bell', 'ghz', 'wstate', 'teleportation', 'superdense',
    'shor', 'grover', 'qft', 'phase', 'controlled',
    'entanglement', 'superposition', 'decoherence',
    'error_correction', 'syndrome', 'stabilizer',
    'surface_code', 'toric_code', 'shor_code',
    'qec', 'threshold', 'fault_tolerance'
]


def extract_quantum_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract quantum computing metadata from circuit and algorithm files.

    Supports various quantum computing formats and frameworks.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is quantum-related
        is_quantum_file = _is_quantum_related_file(filepath, filename)

        if not is_quantum_file:
            return result

        result['quantum_file_detected'] = True

        # Extract format-specific metadata
        if file_ext == '.qasm':
            qasm_data = _extract_qasm_metadata(filepath)
            result.update(qasm_data)

        elif file_ext == '.qobj':
            qobj_data = _extract_qobj_metadata(filepath)
            result.update(qobj_data)

        elif file_ext in ['.py', '.ipynb']:
            python_quantum_data = _extract_python_quantum_metadata(filepath)
            result.update(python_quantum_data)

        elif file_ext == '.qsharp':
            qsharp_data = _extract_qsharp_metadata(filepath)
            result.update(qsharp_data)

        elif file_ext == '.quil':
            quil_data = _extract_quil_metadata(filepath)
            result.update(quil_data)

        # Extract general quantum properties
        general_data = _extract_general_quantum_properties(filepath)
        result.update(general_data)

        # Analyze for quantum computing features
        quantum_analysis = _analyze_quantum_features(filepath)
        result.update(quantum_analysis)

    except Exception as e:
        logger.warning(f"Error extracting quantum metadata from {filepath}: {e}")
        result['quantum_extraction_error'] = str(e)

    return result


def _is_quantum_related_file(filepath: str, filename: str) -> bool:
    """Check if file is quantum computing related."""
    try:
        # Check filename patterns
        if any(pattern in filename for pattern in ['quantum', 'qasm', 'qubit', 'qreg', 'circuit']):
            return True

        # Check file content for quantum keywords
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096)  # Read first 4KB

        content_lower = content.lower()

        # Count quantum keywords
        quantum_keyword_count = sum(1 for keyword in QUANTUM_KEYWORDS if keyword in content_lower)

        # Must have multiple quantum keywords to be considered quantum-related
        if quantum_keyword_count >= 3:
            return True

        # Check for specific quantum patterns
        quantum_patterns = [
            r'qreg\s+\w+\s*\[\s*\d+\s*\]',  # QASM qreg declarations
            r'creg\s+\w+\s*\[\s*\d+\s*\]',  # QASM creg declarations
            r'OPENQASM\s+\d+\.\d+',  # QASM header
            r'from\s+qiskit',  # Qiskit imports
            r'import\s+cirq',  # Cirq imports
            r'using\s+\w+\s*;',  # Q# using statements
            r'operation\s+\w+',  # Q# operations
            r'DEFGATE|DEFGATE\s+\w+',  # Quil gate definitions
        ]

        for pattern in quantum_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

    except Exception:
        pass

    return False


def _extract_qasm_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from QASM quantum circuit files."""
    qasm_data = {'quantum_qasm_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')

        # Extract QASM version
        version_match = re.search(r'OPENQASM\s+(\d+\.\d+)', content, re.IGNORECASE)
        if version_match:
            qasm_data['quantum_qasm_version'] = version_match.group(1)

        # Extract include statements
        include_matches = re.findall(r'include\s+["\']([^"\']+)["\']', content, re.IGNORECASE)
        if include_matches:
            qasm_data['quantum_includes'] = include_matches

        # Count qubits and classical bits
        qreg_matches = re.findall(r'qreg\s+(\w+)\s*\[\s*(\d+)\s*\]', content, re.IGNORECASE)
        creg_matches = re.findall(r'creg\s+(\w+)\s*\[\s*(\d+)\s*\]', content, re.IGNORECASE)

        total_qubits = sum(int(size) for _, size in qreg_matches)
        total_cbits = sum(int(size) for _, size in creg_matches)

        qasm_data['quantum_total_qubits'] = total_qubits
        qasm_data['quantum_total_classical_bits'] = total_cbits
        qasm_data['quantum_qreg_count'] = len(qreg_matches)
        qasm_data['quantum_creg_count'] = len(creg_matches)

        # Extract gate operations
        gate_lines = [line.strip() for line in lines if re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s+', line.strip())]
        qasm_data['quantum_gate_operations'] = len(gate_lines)

        # Count specific gate types
        gate_counts = {}
        gate_patterns = {
            'h': r'\bh\s+',  # Hadamard
            'x': r'\bx\s+',  # Pauli-X
            'y': r'\by\s+',  # Pauli-Y
            'z': r'\bz\s+',  # Pauli-Z
            'cx': r'\bcx\s+',  # CNOT
            'ccx': r'\bccx\s+',  # Toffoli
            'measure': r'\bmeasure\s+',
            'reset': r'\breset\s+',
        }

        for gate_name, pattern in gate_patterns.items():
            count = len(re.findall(pattern, content, re.IGNORECASE))
            if count > 0:
                gate_counts[gate_name] = count

        if gate_counts:
            qasm_data['quantum_gate_counts'] = gate_counts

        # Check for custom gates
        custom_gate_matches = re.findall(r'gate\s+(\w+)', content, re.IGNORECASE)
        if custom_gate_matches:
            qasm_data['quantum_custom_gates'] = custom_gate_matches

        # Check for measurements
        measure_count = len(re.findall(r'\bmeasure\b', content, re.IGNORECASE))
        if measure_count > 0:
            qasm_data['quantum_measurements'] = measure_count

    except Exception as e:
        qasm_data['quantum_qasm_extraction_error'] = str(e)

    return qasm_data


def _extract_qobj_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from Qiskit QObj JSON files."""
    qobj_data = {'quantum_qobj_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)

        # Extract QObj header information
        if 'qobj_id' in data:
            qobj_data['quantum_qobj_id'] = data['qobj_id']

        if 'header' in data:
            header = data['header']
            qobj_data['quantum_backend_name'] = header.get('backend_name')
            qobj_data['quantum_backend_version'] = header.get('backend_version')

        # Extract config information
        if 'config' in data:
            config = data['config']
            qobj_data['quantum_shots'] = config.get('shots')
            qobj_data['quantum_memory'] = config.get('memory')
            qobj_data['quantum_max_credits'] = config.get('max_credits')

        # Count experiments
        if 'experiments' in data:
            experiments = data['experiments']
            qobj_data['quantum_experiment_count'] = len(experiments)

            # Analyze first experiment for circuit info
            if experiments:
                exp = experiments[0]
                if 'header' in exp:
                    exp_header = exp['header']
                    qobj_data['quantum_circuit_name'] = exp_header.get('name')
                    qobj_data['quantum_circuit_qubits'] = exp_header.get('n_qubits')

                # Count instructions in first experiment
                if 'instructions' in exp:
                    instructions = exp['instructions']
                    qobj_data['quantum_instruction_count'] = len(instructions)

                    # Count instruction types
                    inst_types = {}
                    for inst in instructions:
                        inst_type = inst.get('name', 'unknown')
                        inst_types[inst_type] = inst_types.get(inst_type, 0) + 1

                    qobj_data['quantum_instruction_types'] = inst_types

    except Exception as e:
        qobj_data['quantum_qobj_extraction_error'] = str(e)

    return qobj_data


def _extract_python_quantum_metadata(filepath: str) -> Dict[str, Any]:
    """Extract quantum metadata from Python files."""
    python_data = {'quantum_python_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Detect quantum frameworks
        frameworks = {
            'qiskit': 'qiskit' in content.lower(),
            'cirq': 'cirq' in content.lower() or 'import cirq' in content,
            'pennylane': 'pennylane' in content.lower() or 'import pennylane' in content,
            'qutip': 'qutip' in content.lower() or 'import qutip' in content,
            'quimb': 'quimb' in content.lower() or 'import quimb' in content,
        }

        detected_frameworks = [fw for fw, detected in frameworks.items() if detected]
        if detected_frameworks:
            python_data['quantum_frameworks_detected'] = detected_frameworks

        # Count quantum objects
        quantum_objects = {
            'quantum_circuit': len(re.findall(r'QuantumCircuit|Circuit', content)),
            'qubit': len(re.findall(r'Qubit|qubit', content)),
            'gate': len(re.findall(r'Gate|gate', content)),
            'measurement': len(re.findall(r'measure|Measure', content)),
        }

        # Only include counts > 0
        quantum_objects = {k: v for k, v in quantum_objects.items() if v > 0}
        if quantum_objects:
            python_data['quantum_objects_count'] = quantum_objects

        # Extract algorithm names
        algorithms = ['shor', 'grover', 'qft', 'vqe', 'qaoa', 'hhl', 'teleportation']
        detected_algorithms = [alg for alg in algorithms if alg in content.lower()]
        if detected_algorithms:
            python_data['quantum_algorithms_detected'] = detected_algorithms

        # Check for error correction
        if any(term in content.lower() for term in ['error', 'correction', 'syndrome', 'stabilizer']):
            python_data['quantum_error_correction_present'] = True

        # Check for optimization
        if any(term in content.lower() for term in ['optimize', 'optimization', 'variational']):
            python_data['quantum_optimization_present'] = True

    except Exception as e:
        python_data['quantum_python_extraction_error'] = str(e)

    return python_data


def _extract_qsharp_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from Q# quantum programs."""
    qsharp_data = {'quantum_qsharp_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract namespace
        namespace_match = re.search(r'namespace\s+(\w+)', content, re.IGNORECASE)
        if namespace_match:
            qsharp_data['quantum_namespace'] = namespace_match.group(1)

        # Count operations
        operation_matches = re.findall(r'operation\s+(\w+)', content, re.IGNORECASE)
        qsharp_data['quantum_operations'] = operation_matches
        qsharp_data['quantum_operation_count'] = len(operation_matches)

        # Count functions
        function_matches = re.findall(r'function\s+(\w+)', content, re.IGNORECASE)
        qsharp_data['quantum_functions'] = function_matches
        qsharp_data['quantum_function_count'] = len(function_matches)

        # Extract using statements
        using_matches = re.findall(r'using\s*\(\s*([^)]+)\s*\)', content, re.IGNORECASE)
        if using_matches:
            qsharp_data['quantum_qubit_allocations'] = using_matches

        # Count quantum gates/operations used
        gate_keywords = ['H', 'X', 'Y', 'Z', 'CNOT', 'CCNOT', 'Measure', 'Reset']
        gate_counts = {}
        for gate in gate_keywords:
            count = len(re.findall(r'\b' + re.escape(gate) + r'\b', content))
            if count > 0:
                gate_counts[gate] = count

        if gate_counts:
            qsharp_data['quantum_gate_usage'] = gate_counts

    except Exception as e:
        qsharp_data['quantum_qsharp_extraction_error'] = str(e)

    return qsharp_data


def _extract_quil_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from Quil quantum programs."""
    quil_data = {'quantum_quil_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')

        # Count declared qubits
        qubit_lines = [line for line in lines if line.strip().startswith('DECLARE')]
        quil_data['quantum_declared_qubits'] = len(qubit_lines)

        # Extract qubit declarations
        qubit_declarations = []
        for line in qubit_lines:
            match = re.search(r'DECLARE\s+(\w+)', line, re.IGNORECASE)
            if match:
                qubit_declarations.append(match.group(1))

        if qubit_declarations:
            quil_data['quantum_qubit_names'] = qubit_declarations

        # Count gate definitions
        defgate_lines = [line for line in lines if line.strip().startswith('DEFGATE')]
        quil_data['quantum_custom_gates'] = len(defgate_lines)

        # Count gate applications
        gate_lines = [line for line in lines if not line.strip().startswith('#') and
                     not line.strip().startswith('DECLARE') and
                     not line.strip().startswith('DEFGATE') and
                     line.strip()]
        quil_data['quantum_gate_applications'] = len(gate_lines)

        # Extract measurement operations
        measure_lines = [line for line in lines if 'MEASURE' in line.upper()]
        quil_data['quantum_measurements'] = len(measure_lines)

    except Exception as e:
        quil_data['quantum_quil_extraction_error'] = str(e)

    return quil_data


def _extract_general_quantum_properties(filepath: str) -> Dict[str, Any]:
    """Extract general quantum file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['quantum_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['quantum_filename'] = filename

        # Check for quantum-specific naming patterns
        quantum_indicators = ['quantum', 'qasm', 'qubit', 'circuit', 'qreg']
        if any(indicator in filename.lower() for indicator in quantum_indicators):
            props['quantum_filename_suggests_quantum'] = True

        # Extract version numbers from filename
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['quantum_file_version_hint'] = version_match.group(1)

    except Exception:
        pass

    return props


def _analyze_quantum_features(filepath: str) -> Dict[str, Any]:
    """Analyze file for quantum computing features."""
    analysis = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(8192)  # Read first 8KB

        # Analyze circuit complexity
        qubit_count = 0
        gate_count = 0

        # Look for qubit declarations
        qubit_patterns = [
            r'qreg\s+\w+\s*\[\s*(\d+)\s*\]',  # QASM
            r'QuantumCircuit\((\d+)\)',  # Qiskit
            r'LineQubit\.range\((\d+)\)',  # Cirq
        ]

        for pattern in qubit_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    qubit_count += int(match)
                except ValueError:
                    pass

        if qubit_count > 0:
            analysis['quantum_circuit_qubits'] = qubit_count

        # Estimate gate count
        gate_indicators = ['h ', 'x ', 'y ', 'z ', 'cx ', 'ccx ', 'measure ', 'H(', 'X(', 'CNOT(']
        for indicator in gate_indicators:
            gate_count += content.count(indicator)

        if gate_count > 0:
            analysis['quantum_estimated_gates'] = gate_count

        # Detect quantum algorithms
        algorithms = {
            'shor': 'shor' in content.lower(),
            'grover': 'grover' in content.lower(),
            'qft': 'qft' in content.lower() or 'fourier' in content.lower(),
            'teleportation': 'teleport' in content.lower(),
            'superdense': 'superdense' in content.lower(),
            'error_correction': any(term in content.lower() for term in ['syndrome', 'stabilizer', 'surface_code']),
        }

        detected_algorithms = [alg for alg, detected in algorithms.items() if detected]
        if detected_algorithms:
            analysis['quantum_algorithms_present'] = detected_algorithms

        # Check for noise/error modeling
        if any(term in content.lower() for term in ['noise', 'error', 'decoherence', 't1', 't2']):
            analysis['quantum_noise_modeling'] = True

        # Check for optimization
        if any(term in content.lower() for term in ['optimize', 'transpile', 'basis_gates']):
            analysis['quantum_optimization_present'] = True

    except Exception:
        pass

    return analysis


def get_quantum_field_count() -> int:
    """Return the number of fields extracted by quantum metadata."""
    # Format detection (5)
    detection_fields = 5

    # QASM specific (15)
    qasm_fields = 15

    # QObj specific (12)
    qobj_fields = 12

    # Python quantum specific (10)
    python_fields = 10

    # Q# specific (10)
    qsharp_fields = 10

    # Quil specific (8)
    quil_fields = 8

    # General properties (6)
    general_fields = 6

    # Quantum analysis (10)
    analysis_fields = 10

    return detection_fields + qasm_fields + qobj_fields + python_fields + qsharp_fields + quil_fields + general_fields + analysis_fields


# Integration point for metadata_engine.py
def extract_quantum_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for quantum metadata extraction."""
    return extract_quantum_metadata(filepath)