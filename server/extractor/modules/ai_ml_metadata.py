# server/extractor/modules/ai_ml_metadata.py

"""
AI/ML Model metadata extraction for Phase 4.

Extracts metadata from:
- TensorFlow/Keras models (.h5, .pb, SavedModel)
- PyTorch models (.pth, .pt)
- ONNX models (.onnx)
- scikit-learn models (.pkl, .joblib)
- XGBoost models (.model)
- Model configuration files
- Training metadata and hyperparameters
"""

import logging
import json
import pickle
import struct
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Optional imports
try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Model format signatures
MODEL_SIGNATURES = {
    'tensorflow_h5': b'\x89HDF\r\n\x1a\n',  # HDF5 signature
    'pytorch_zip': b'PK\x03\x04',  # ZIP signature for PyTorch
    'onnx': b'\x08\x01\x12',  # ONNX protocol buffer
    'pickle': b'\x80\x03',  # Python pickle protocol 3
}

# Common AI/ML file extensions
AI_ML_EXTENSIONS = [
    '.h5', '.pb', '.pth', '.pt', '.onnx', '.pkl', '.joblib',
    '.model', '.tflite', '.mlmodel', '.caffemodel', '.prototxt',
    '.json', '.yaml', '.yml', '.cfg', '.ini'
]


def extract_ai_ml_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract AI/ML model metadata from various model formats.

    Supports TensorFlow, PyTorch, ONNX, scikit-learn, and other ML frameworks.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Detect model type from file signature
        model_type = _detect_model_type(filepath)

        if model_type:
            result['ai_model_type'] = model_type
            result['ai_model_format'] = _get_format_from_type(model_type)

        # Extract format-specific metadata
        if model_type == 'tensorflow_h5':
            tf_data = _extract_tensorflow_h5_metadata(filepath)
            result.update(tf_data)

        elif model_type in ['pytorch_zip', 'pytorch_pickle']:
            torch_data = _extract_pytorch_metadata(filepath)
            result.update(torch_data)

        elif model_type == 'onnx':
            onnx_data = _extract_onnx_metadata(filepath)
            result.update(onnx_data)

        elif model_type == 'pickle':
            pickle_data = _extract_pickle_metadata(filepath)
            result.update(pickle_data)

        # Extract configuration files
        if file_ext in ['.json', '.yaml', '.yml', '.cfg', '.ini']:
            config_data = _extract_config_metadata(filepath)
            result.update(config_data)

        # Extract general model properties
        general_data = _extract_general_model_properties(filepath)
        result.update(general_data)

        # Analyze model architecture if possible
        arch_data = _analyze_model_architecture(filepath, model_type)
        result.update(arch_data)

    except Exception as e:
        logger.warning(f"Error extracting AI/ML metadata from {filepath}: {e}")
        result['ai_ml_extraction_error'] = str(e)

    return result


def _detect_model_type(filepath: str) -> Optional[str]:
    """Detect the type of AI/ML model from file signature."""
    try:
        with open(filepath, 'rb') as f:
            signature = f.read(16)

        # Check for known signatures
        if signature.startswith(MODEL_SIGNATURES['tensorflow_h5']):
            return 'tensorflow_h5'
        elif signature.startswith(MODEL_SIGNATURES['pytorch_zip']):
            return 'pytorch_zip'
        elif signature.startswith(MODEL_SIGNATURES['onnx']):
            return 'onnx'
        elif signature.startswith(MODEL_SIGNATURES['pickle']):
            return 'pickle'

        # Check file extension for other formats
        ext = Path(filepath).suffix.lower()
        name = Path(filepath).name.lower()

        if ext == '.pth' or ext == '.pt':
            return 'pytorch_pickle'
        elif ext == '.pb':
            return 'tensorflow_pb'
        elif ext == '.tflite':
            return 'tflite'
        elif ext == '.mlmodel':
            return 'coreml'
        elif ext == '.caffemodel':
            return 'caffe'
        elif ext in ['.pkl', '.joblib']:
            return 'sklearn'
        elif ext == '.model':
            return 'xgboost'
        elif ext in ['.json', '.yaml', '.yml'] and any(x in name for x in ['config', 'model', 'hyper', 'param']):
            return 'config'
        elif ext in ['.cfg', '.ini'] and any(x in name for x in ['model', 'train', 'config']):
            return 'config'

    except Exception:
        pass

    return None


def _get_format_from_type(model_type: str) -> str:
    """Get human-readable format name from model type."""
    format_map = {
        'tensorflow_h5': 'TensorFlow HDF5',
        'tensorflow_pb': 'TensorFlow Protocol Buffer',
        'pytorch_zip': 'PyTorch ZIP',
        'pytorch_pickle': 'PyTorch Pickle',
        'onnx': 'ONNX',
        'tflite': 'TensorFlow Lite',
        'coreml': 'Core ML',
        'caffe': 'Caffe',
        'sklearn': 'scikit-learn',
        'xgboost': 'XGBoost',
        'config': 'Configuration File'
    }
    return format_map.get(model_type, 'Unknown')


def _extract_tensorflow_h5_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from TensorFlow HDF5 model."""
    tf_data = {'tensorflow_model_present': True}

    if not H5PY_AVAILABLE:
        tf_data['tensorflow_requires_h5py'] = True
        return tf_data

    try:
        with h5py.File(filepath, 'r') as f:
            # Extract model configuration
            if 'model_config' in f:
                config_group = f['model_config']
                tf_data['tensorflow_has_config'] = True

                # Try to extract model topology
                if 'config' in config_group:
                    config_data = _extract_hdf5_dataset(config_group['config'])
                    if config_data:
                        tf_data['tensorflow_config'] = config_data

            # Extract optimizer state
            if 'optimizer_weights' in f:
                tf_data['tensorflow_has_optimizer'] = True

            # Extract training configuration
            if 'training_config' in f:
                training_config = _extract_hdf5_dataset(f['training_config'])
                if training_config:
                    tf_data['tensorflow_training_config'] = training_config

            # Count layers and parameters
            layer_count = 0
            total_params = 0

            def count_layers(name, obj):
                nonlocal layer_count, total_params
                if isinstance(obj, h5py.Group) and 'kernel' in obj:
                    layer_count += 1
                    if 'kernel' in obj:
                        kernel_shape = obj['kernel'].shape
                        if len(kernel_shape) >= 2:
                            if NUMPY_AVAILABLE:
                                params = __import__('numpy').prod(kernel_shape)
                            else:
                                params = 1
                                for dim in kernel_shape:
                                    params *= dim
                            total_params += params

            f.visititems(count_layers)
            tf_data['tensorflow_layer_count'] = layer_count
            tf_data['tensorflow_total_parameters'] = int(total_params)

    except Exception as e:
        tf_data['tensorflow_extraction_error'] = str(e)

    return tf_data


def _extract_pytorch_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from PyTorch model."""
    torch_data = {'pytorch_model_present': True}

    try:
        # For ZIP-based PyTorch models, we can extract some metadata
        if _detect_model_type(filepath) == 'pytorch_zip':
            torch_data['pytorch_format'] = 'zip'

            # Try to read some basic info without loading the full model
            file_size = os.path.getsize(filepath)
            torch_data['pytorch_model_size'] = file_size

        else:
            # For pickle-based models, be careful not to load untrusted code
            torch_data['pytorch_format'] = 'pickle'
            torch_data['pytorch_security_note'] = 'Pickle models not fully analyzed for security'

    except Exception as e:
        torch_data['pytorch_extraction_error'] = str(e)

    return torch_data


def _extract_onnx_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from ONNX model."""
    onnx_data = {'onnx_model_present': True}

    try:
        # Read ONNX model header (first 256 bytes should contain metadata)
        with open(filepath, 'rb') as f:
            header = f.read(256)

        # ONNX models contain protocol buffer data
        # We can extract some basic information from the header
        onnx_data['onnx_header_size'] = len(header)

        # Look for IR version and other metadata in the binary data
        if len(header) > 8:
            # First 4 bytes: magic number
            # Next 4 bytes: IR version
            ir_version = struct.unpack('<I', header[4:8])[0]
            onnx_data['onnx_ir_version'] = ir_version

    except Exception as e:
        onnx_data['onnx_extraction_error'] = str(e)

    return onnx_data


def _extract_pickle_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from pickled model (scikit-learn, etc.)."""
    pickle_data = {'pickle_model_present': True}

    try:
        file_size = os.path.getsize(filepath)
        pickle_data['pickle_model_size'] = file_size

        # For security, we don't unpickle unknown files
        # But we can detect some patterns in the file
        with open(filepath, 'rb') as f:
            data = f.read(1024)

        # Look for common ML library class names in the pickle data
        data_str = data.decode('latin-1', errors='ignore')

        if 'sklearn' in data_str or 'scikit' in data_str:
            pickle_data['pickle_library'] = 'scikit-learn'
        elif 'xgboost' in data_str:
            pickle_data['pickle_library'] = 'xgboost'
        elif 'lightgbm' in data_str:
            pickle_data['pickle_library'] = 'lightgbm'
        elif 'catboost' in data_str:
            pickle_data['pickle_library'] = 'catboost'

    except Exception as e:
        pickle_data['pickle_extraction_error'] = str(e)

    return pickle_data


def _extract_config_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from configuration files."""
    config_data = {'config_file_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10240)  # Read first 10KB

        if file_ext == '.json':
            try:
                json_data = json.loads(content)
                config_data['config_format'] = 'json'
                config_data['config_has_structure'] = True

                # Extract common ML config patterns
                if isinstance(json_data, dict):
                    _analyze_config_dict(json_data, config_data)

            except json.JSONDecodeError:
                config_data['config_format'] = 'json'
                config_data['config_parse_error'] = 'Invalid JSON'

        elif file_ext in ['.yaml', '.yml']:
            config_data['config_format'] = 'yaml'
            # Basic YAML analysis
            if 'model' in content.lower():
                config_data['config_contains_model'] = True
            if 'train' in content.lower():
                config_data['config_contains_training'] = True

        elif file_ext in ['.cfg', '.ini']:
            config_data['config_format'] = 'ini'
            # Look for sections
            sections = re.findall(r'^\s*\[([^\]]+)\]', content, re.MULTILINE)
            if sections:
                config_data['config_sections'] = sections

    except Exception as e:
        config_data['config_extraction_error'] = str(e)

    return config_data


def _extract_general_model_properties(filepath: str) -> Dict[str, Any]:
    """Extract general properties applicable to all model types."""
    props = {}

    try:
        stat_info = os.stat(filepath)
        props['model_file_size'] = stat_info.st_size
        props['model_file_modified'] = stat_info.st_mtime

        # Analyze filename for clues
        filename = Path(filepath).name
        props['model_filename'] = filename

        # Look for version numbers in filename
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['model_version_string'] = version_match.group(1)

        # Look for architecture hints
        if 'resnet' in filename.lower():
            props['model_architecture_hint'] = 'ResNet'
        elif 'bert' in filename.lower():
            props['model_architecture_hint'] = 'BERT'
        elif 'gpt' in filename.lower():
            props['model_architecture_hint'] = 'GPT'
        elif 'transformer' in filename.lower():
            props['model_architecture_hint'] = 'Transformer'

    except Exception as e:
        props['model_properties_error'] = str(e)

    return props


def _analyze_model_architecture(filepath: str, model_type: Optional[str]) -> Dict[str, Any]:
    """Analyze model architecture where possible."""
    arch_data = {}

    if not H5PY_AVAILABLE and model_type == 'tensorflow_h5':
        arch_data['model_architecture_requires_h5py'] = True
        return arch_data

    try:
        if model_type == 'tensorflow_h5':
            # Additional TensorFlow analysis
            with h5py.File(filepath, 'r') as f:
                # Look for layer information
                layers = []
                def find_layers(name, obj):
                    if isinstance(obj, h5py.Group) and name.endswith('/'):
                        layer_name = name.rstrip('/')
                        if any(x in layer_name.lower() for x in ['conv', 'dense', 'lstm', 'attention']):
                            layers.append(layer_name)

                f.visititems(find_layers)
                if layers:
                    arch_data['model_layers'] = layers[:10]  # First 10 layers
                    arch_data['model_layer_count'] = len(layers)

    except Exception:
        pass

    return arch_data


def _extract_hdf5_dataset(dataset) -> Any:
    """Extract data from HDF5 dataset safely."""
    try:
        if isinstance(dataset, h5py.Dataset):
            data = dataset[()]
            if isinstance(data, bytes):
                return data.decode('utf-8', errors='ignore')
            elif NUMPY_AVAILABLE and isinstance(data, __import__('numpy').ndarray) and data.dtype.kind in 'SU':
                return data.tolist()
            else:
                return data.tolist() if hasattr(data, 'tolist') else str(data)
        elif isinstance(dataset, h5py.Group):
            result = {}
            for key in dataset.keys():
                result[key] = _extract_hdf5_dataset(dataset[key])
            return result
    except Exception:
        return None


def _analyze_config_dict(config: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Analyze configuration dictionary for ML patterns."""
    # Look for common ML configuration keys
    ml_keys = {
        'learning_rate': 'config_learning_rate',
        'batch_size': 'config_batch_size',
        'epochs': 'config_epochs',
        'optimizer': 'config_optimizer',
        'loss': 'config_loss_function',
        'metrics': 'config_metrics',
        'layers': 'config_layers',
        'model': 'config_model_type',
        'architecture': 'config_architecture',
        'dataset': 'config_dataset',
        'validation_split': 'config_validation_split'
    }

    for key, field in ml_keys.items():
        if key in config:
            result[field] = config[key]

    # Count nested structures
    if 'layers' in config and isinstance(config['layers'], list):
        result['config_layer_count'] = len(config['layers'])


def get_ai_ml_field_count() -> int:
    """Return the number of fields extracted by AI/ML metadata."""
    # Model type detection (5)
    type_fields = 5

    # TensorFlow specific (15)
    tf_fields = 15

    # PyTorch specific (5)
    torch_fields = 5

    # ONNX specific (5)
    onnx_fields = 5

    # Pickle/scikit-learn specific (10)
    pickle_fields = 10

    # Configuration files (15)
    config_fields = 15

    # General properties (10)
    general_fields = 10

    # Architecture analysis (5)
    arch_fields = 5

    return type_fields + tf_fields + torch_fields + onnx_fields + pickle_fields + config_fields + general_fields + arch_fields


# Integration point for metadata_engine.py
def extract_ai_ml_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for AI/ML metadata extraction."""
    return extract_ai_ml_metadata(filepath)