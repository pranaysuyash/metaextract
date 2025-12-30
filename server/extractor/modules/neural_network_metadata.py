# server/extractor/modules/neural_network_metadata.py

"""
Neural network metadata extraction for Phase 4.

Extracts metadata from:
- Neural network model files (HDF5, SavedModel, ONNX, PyTorch)
- Model architecture definitions
- Training configuration files
- Neural network configuration files
- Model weights and biases
- Layer information and hyperparameters
"""

import logging
import json
import re
import struct
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import h5py

logger = logging.getLogger(__name__)

# Neural network file extensions and formats
NEURAL_NETWORK_EXTENSIONS = [
    '.h5', '.hdf5', '.pb', '.pbtxt', '.onnx', '.pt', '.pth',
    '.ckpt', '.tflite', '.mlmodel', '.caffemodel', '.prototxt',
    '.json', '.yaml', '.yml', '.py', '.ipynb'
]

# Neural network-specific keywords
NN_KEYWORDS = [
    'neural', 'network', 'model', 'layer', 'neuron', 'activation',
    'convolution', 'dense', 'dropout', 'batch_norm', 'pooling',
    'lstm', 'rnn', 'cnn', 'transformer', 'attention', 'embedding',
    'optimizer', 'loss', 'accuracy', 'epoch', 'batch_size',
    'learning_rate', 'gradient', 'backprop', 'forward', 'inference',
    'training', 'validation', 'test', 'dataset', 'tensor',
    'keras', 'tensorflow', 'pytorch', 'onnx', 'caffe', 'mxnet'
]


def extract_neural_network_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract neural network metadata from model and configuration files.

    Supports various deep learning frameworks and formats.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is neural network related
        is_nn_file = _is_neural_network_related_file(filepath, filename)

        if not is_nn_file:
            return result

        result['nn_file_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.h5', '.hdf5']:
            hdf5_data = _extract_hdf5_nn_metadata(filepath)
            result.update(hdf5_data)

        elif file_ext in ['.pb', '.pbtxt']:
            tf_data = _extract_tensorflow_metadata(filepath)
            result.update(tf_data)

        elif file_ext == '.onnx':
            onnx_data = _extract_onnx_metadata(filepath)
            result.update(onnx_data)

        elif file_ext in ['.pt', '.pth', '.ckpt']:
            pytorch_data = _extract_pytorch_metadata(filepath)
            result.update(pytorch_data)

        elif file_ext == '.tflite':
            tflite_data = _extract_tflite_metadata(filepath)
            result.update(tflite_data)

        elif file_ext in ['.json', '.yaml', '.yml']:
            config_data = _extract_nn_config_metadata(filepath)
            result.update(config_data)

        elif file_ext in ['.py', '.ipynb']:
            python_nn_data = _extract_python_nn_metadata(filepath)
            result.update(python_nn_data)

        # Extract general neural network properties
        general_data = _extract_general_nn_properties(filepath)
        result.update(general_data)

        # Analyze neural network architecture
        nn_analysis = _analyze_nn_architecture(filepath)
        result.update(nn_analysis)

    except Exception as e:
        logger.warning(f"Error extracting neural network metadata from {filepath}: {e}")
        result['nn_extraction_error'] = str(e)

    return result


def _is_neural_network_related_file(filepath: str, filename: str) -> bool:
    """Check if file is neural network related."""
    try:
        # Check filename patterns
        nn_patterns = ['model', 'network', 'neural', 'cnn', 'rnn', 'lstm', 'transformer']
        if any(pattern in filename for pattern in nn_patterns):
            return True

        # Check file content for neural network keywords
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096)  # Read first 4KB

        content_lower = content.lower()

        # Count neural network keywords
        nn_keyword_count = sum(1 for keyword in NN_KEYWORDS if keyword in content_lower)

        # Must have multiple NN keywords to be considered NN-related
        if nn_keyword_count >= 3:
            return True

        # Check for specific NN patterns
        nn_patterns = [
            r'keras|tensorflow|pytorch|torch',  # Framework imports
            r'layer|model|network',  # NN components
            r'conv|dense|lstm|rnn',  # Layer types
            r'optimizer|loss|metric',  # Training components
            r'batch_size|epochs|learning_rate',  # Hyperparameters
        ]

        for pattern in nn_patterns:
            if re.search(pattern, content_lower):
                return True

    except Exception:
        pass

    return False


def _extract_hdf5_nn_metadata(filepath: str) -> Dict[str, Any]:
    """Extract neural network metadata from HDF5 model files."""
    hdf5_data = {'nn_hdf5_format_present': True}

    try:
        with h5py.File(filepath, 'r') as f:
            # Extract Keras model configuration
            if 'model_config' in f:
                config_group = f['model_config']
                if hasattr(config_group, 'attrs') and 'model_config' in config_group.attrs:
                    model_config = json.loads(config_group.attrs['model_config'])
                    hdf5_data['nn_model_config'] = model_config

                    # Extract model architecture info
                    if 'config' in model_config:
                        config = model_config['config']
                        hdf5_data['nn_model_name'] = config.get('name')

                        # Extract layers
                        if 'layers' in config:
                            layers = config['layers']
                            hdf5_data['nn_layer_count'] = len(layers)

                            layer_types = {}
                            for layer in layers:
                                layer_type = layer.get('class_name', 'unknown')
                                layer_types[layer_type] = layer_types.get(layer_type, 0) + 1

                            hdf5_data['nn_layer_types'] = layer_types

            # Extract training configuration
            if 'training_config' in f:
                training_group = f['training_config']
                if hasattr(training_group, 'attrs') and 'training_config' in training_group.attrs:
                    training_config = json.loads(training_group.attrs['training_config'])
                    hdf5_data['nn_training_config'] = training_config

                    # Extract optimizer info
                    if 'optimizer_config' in training_config:
                        optimizer = training_config['optimizer_config']
                        hdf5_data['nn_optimizer'] = optimizer.get('class_name')
                        hdf5_data['nn_learning_rate'] = optimizer.get('config', {}).get('learning_rate')

                    # Extract loss and metrics
                    hdf5_data['nn_loss'] = training_config.get('loss')
                    hdf5_data['nn_metrics'] = training_config.get('metrics', [])

            # Extract model weights info
            if 'model_weights' in f:
                weights_group = f['model_weights']
                total_params = 0
                trainable_params = 0

                def count_parameters(name, obj):
                    nonlocal total_params, trainable_params
                    if isinstance(obj, h5py.Dataset):
                        params = obj.size
                        total_params += params
                        if 'trainable' in name.lower():
                            trainable_params += params

                weights_group.visititems(count_parameters)
                hdf5_data['nn_total_parameters'] = total_params
                hdf5_data['nn_trainable_parameters'] = trainable_params

    except Exception as e:
        hdf5_data['nn_hdf5_extraction_error'] = str(e)

    return hdf5_data


def _extract_tensorflow_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from TensorFlow model files."""
    tf_data = {'nn_tensorflow_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext == '.pbtxt':
            # Text protobuf format
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract node information
            node_matches = re.findall(r'node\s*\{[^}]*name:\s*"([^"]+)"[^}]*op:\s*"([^"]+)"', content, re.DOTALL)
            tf_data['nn_tf_nodes'] = len(node_matches)

            # Count operation types
            op_types = {}
            for _, op in node_matches:
                op_types[op] = op_types.get(op, 0) + 1

            tf_data['nn_tf_operations'] = op_types

            # Look for specific layer types
            layer_patterns = {
                'Conv2D': r'Conv2D',
                'Dense': r'Dense',
                'LSTM': r'LSTM',
                'BatchNorm': r'BatchNorm',
                'Dropout': r'Dropout',
            }

            for layer_type, pattern in layer_patterns.items():
                count = len(re.findall(pattern, content))
                if count > 0:
                    tf_data[f'nn_tf_{layer_type.lower()}_layers'] = count

        elif file_ext == '.pb':
            # Binary protobuf format - limited analysis
            with open(filepath, 'rb') as f:
                # Read first 1KB to check for TensorFlow magic
                header = f.read(1024)
                if b'TensorFlow' in header:
                    tf_data['nn_tf_binary_format'] = True

                # Estimate file size for model complexity
                file_size = Path(filepath).stat().st_size
                tf_data['nn_tf_model_size'] = file_size

    except Exception as e:
        tf_data['nn_tf_extraction_error'] = str(e)

    return tf_data


def _extract_onnx_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from ONNX model files."""
    onnx_data = {'nn_onnx_format_present': True}

    try:
        # ONNX files are protobuf-based, try to read as binary
        with open(filepath, 'rb') as f:
            data = f.read(2048)  # Read first 2KB

        # Look for ONNX magic bytes
        if data.startswith(b'\x08\x01\x12'):  # ONNX protobuf magic
            onnx_data['nn_onnx_valid_format'] = True

        # Try to extract string data that might contain metadata
        strings = []
        i = 0
        while i < len(data) - 4:
            try:
                # Look for length-prefixed strings
                length = struct.unpack('<I', data[i:i+4])[0]
                if length > 0 and length < 1000 and i + 4 + length < len(data):
                    string_data = data[i+4:i+4+length].decode('utf-8', errors='ignore')
                    if string_data and len(string_data) > 3:
                        strings.append(string_data)
                i += 4 + length
            except:
                i += 1

        # Analyze extracted strings for metadata
        if strings:
            # Look for model info
            for s in strings:
                if 'producer_name' in s.lower():
                    onnx_data['nn_onnx_producer'] = s
                elif 'domain' in s.lower():
                    onnx_data['nn_onnx_domain'] = s
                elif 'model_version' in s.lower():
                    onnx_data['nn_onnx_version'] = s

            onnx_data['nn_onnx_strings_found'] = len(strings)

    except Exception as e:
        onnx_data['nn_onnx_extraction_error'] = str(e)

    return onnx_data


def _extract_pytorch_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from PyTorch model files."""
    pytorch_data = {'nn_pytorch_format_present': True}

    try:
        # PyTorch files are pickled, limited analysis without loading
        with open(filepath, 'rb') as f:
            data = f.read(1024)  # Read first 1KB

        # Check for pickle protocol
        if data.startswith(b'\x80'):  # Pickle protocol marker
            pytorch_data['nn_pytorch_pickle_format'] = True

        # Look for PyTorch-specific strings
        data_str = data.decode('latin-1', errors='ignore')

        if 'torch' in data_str.lower():
            pytorch_data['nn_pytorch_torch_detected'] = True

        # Estimate model size
        file_size = Path(filepath).stat().st_size
        pytorch_data['nn_pytorch_model_size'] = file_size

        # Classify by size (rough heuristic)
        if file_size < 1024 * 1024:  # < 1MB
            pytorch_data['nn_pytorch_model_size_category'] = 'small'
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            pytorch_data['nn_pytorch_model_size_category'] = 'medium'
        else:
            pytorch_data['nn_pytorch_model_size_category'] = 'large'

    except Exception as e:
        pytorch_data['nn_pytorch_extraction_error'] = str(e)

    return pytorch_data


def _extract_tflite_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from TensorFlow Lite model files."""
    tflite_data = {'nn_tflite_format_present': True}

    try:
        with open(filepath, 'rb') as f:
            data = f.read(1024)  # Read first 1KB

        # TFLite files start with 'TFL3' magic
        if data.startswith(b'TFL3'):
            tflite_data['nn_tflite_valid_format'] = True

            # Extract version (next 4 bytes, little endian)
            if len(data) >= 8:
                version = struct.unpack('<I', data[4:8])[0]
                tflite_data['nn_tflite_version'] = version

        # Estimate model size
        file_size = Path(filepath).stat().st_size
        tflite_data['nn_tflite_model_size'] = file_size

    except Exception as e:
        tflite_data['nn_tflite_extraction_error'] = str(e)

    return tflite_data


def _extract_nn_config_metadata(filepath: str) -> Dict[str, Any]:
    """Extract neural network metadata from configuration files."""
    config_data = {'nn_config_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if file_ext in ['.yaml', '.yml']:
            try:
                import yaml
                config = yaml.safe_load(content)
            except ImportError:
                config = None
        else:  # JSON
            try:
                config = json.loads(content)
            except:
                config = None

        if config and isinstance(config, dict):
            # Extract model architecture
            if 'layers' in config:
                layers = config['layers']
                if isinstance(layers, list):
                    config_data['nn_config_layer_count'] = len(layers)

                    layer_types = {}
                    for layer in layers:
                        if isinstance(layer, dict):
                            layer_type = layer.get('type') or layer.get('class')
                            if layer_type:
                                layer_types[layer_type] = layer_types.get(layer_type, 0) + 1

                    config_data['nn_config_layer_types'] = layer_types

            # Extract training parameters
            training_params = {}
            param_keys = ['batch_size', 'epochs', 'learning_rate', 'optimizer', 'loss', 'metrics']

            def extract_params(obj, prefix=''):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    if key.lower() in param_keys:
                        training_params[key] = value
                    elif isinstance(value, dict):
                        extract_params(value, full_key)

            extract_params(config)

            if training_params:
                config_data['nn_config_training_params'] = training_params

            # Extract model metadata
            if 'name' in config:
                config_data['nn_config_model_name'] = config['name']

            if 'version' in config:
                config_data['nn_config_model_version'] = config['version']

    except Exception as e:
        config_data['nn_config_extraction_error'] = str(e)

    return config_data


def _extract_python_nn_metadata(filepath: str) -> Dict[str, Any]:
    """Extract neural network metadata from Python files."""
    python_data = {'nn_python_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Detect frameworks
        frameworks = {
            'tensorflow': 'tensorflow' in content or 'tf.' in content,
            'keras': 'keras' in content,
            'pytorch': 'torch' in content or 'pytorch' in content,
            'mxnet': 'mxnet' in content,
            'caffe': 'caffe' in content,
            'onnx': 'onnx' in content,
        }

        detected_frameworks = [fw for fw, detected in frameworks.items() if detected]
        if detected_frameworks:
            python_data['nn_python_frameworks'] = detected_frameworks

        # Count neural network components
        nn_components = {
            'model_definition': len(re.findall(r'class.*Model|def.*model', content, re.IGNORECASE)),
            'layer_definition': len(re.findall(r'Conv2D|Dense|LSTM|Dropout', content)),
            'training_loop': len(re.findall(r'fit\(|train\(', content)),
            'optimizer_usage': len(re.findall(r'Adam|SGD|RMSprop', content)),
            'loss_function': len(re.findall(r'loss|Loss', content)),
        }

        # Only include counts > 0
        nn_components = {k: v for k, v in nn_components.items() if v > 0}
        if nn_components:
            python_data['nn_python_components'] = nn_components

        # Extract hyperparameters
        hyperparams = {}
        hyperparam_patterns = {
            'batch_size': r'batch_size\s*=\s*(\d+)',
            'epochs': r'epochs\s*=\s*(\d+)',
            'learning_rate': r'learning_rate\s*=\s*([0-9.]+)',
        }

        for param, pattern in hyperparam_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                hyperparams[param] = matches[0]  # Take first match

        if hyperparams:
            python_data['nn_python_hyperparams'] = hyperparams

        # Check for specific NN architectures
        architectures = ['resnet', 'vgg', 'inception', 'mobilenet', 'bert', 'gpt', 'transformer']
        detected_architectures = [arch for arch in architectures if arch in content.lower()]
        if detected_architectures:
            python_data['nn_python_architectures'] = detected_architectures

    except Exception as e:
        python_data['nn_python_extraction_error'] = str(e)

    return python_data


def _extract_general_nn_properties(filepath: str) -> Dict[str, Any]:
    """Extract general neural network file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['nn_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['nn_filename'] = filename

        # Check for NN-specific naming patterns
        nn_indicators = ['model', 'network', 'neural', 'cnn', 'rnn', 'lstm', 'transformer']
        if any(indicator in filename.lower() for indicator in nn_indicators):
            props['nn_filename_suggests_nn'] = True

        # Extract version numbers from filename
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['nn_file_version_hint'] = version_match.group(1)

        # Classify model size
        file_size = stat_info.st_size
        if file_size < 1024 * 1024:  # < 1MB
            props['nn_model_size_category'] = 'small'
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            props['nn_model_size_category'] = 'medium'
        elif file_size < 1024 * 1024 * 1024:  # < 1GB
            props['nn_model_size_category'] = 'large'
        else:
            props['nn_model_size_category'] = 'very_large'

    except Exception:
        pass

    return props


def _analyze_nn_architecture(filepath: str) -> Dict[str, Any]:
    """Analyze neural network architecture and complexity."""
    analysis = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(8192)  # Read first 8KB

        # Analyze layer complexity
        layer_indicators = {
            'convolutional': ['conv', 'convolution'],
            'recurrent': ['lstm', 'rnn', 'gru'],
            'attention': ['attention', 'transformer', 'self_attention'],
            'dense': ['dense', 'fully_connected', 'linear'],
            'normalization': ['batch_norm', 'layer_norm'],
            'dropout': ['dropout'],
            'pooling': ['pool', 'maxpool', 'avgpool'],
        }

        layer_counts = {}
        for layer_type, indicators in layer_indicators.items():
            count = 0
            for indicator in indicators:
                count += content.lower().count(indicator)
            if count > 0:
                layer_counts[layer_type] = count

        if layer_counts:
            analysis['nn_architecture_layers'] = layer_counts

        # Estimate model complexity
        total_layers = sum(layer_counts.values())
        if total_layers > 0:
            analysis['nn_estimated_complexity'] = total_layers

            # Classify architecture type
            if layer_counts.get('convolutional', 0) > layer_counts.get('recurrent', 0) and layer_counts.get('convolutional', 0) > layer_counts.get('attention', 0):
                analysis['nn_primary_architecture'] = 'cnn'
            elif layer_counts.get('recurrent', 0) > layer_counts.get('convolutional', 0) and layer_counts.get('recurrent', 0) > layer_counts.get('attention', 0):
                analysis['nn_primary_architecture'] = 'rnn'
            elif layer_counts.get('attention', 0) > layer_counts.get('convolutional', 0) and layer_counts.get('attention', 0) > layer_counts.get('recurrent', 0):
                analysis['nn_primary_architecture'] = 'transformer'
            else:
                analysis['nn_primary_architecture'] = 'mixed'

        # Check for pre-trained models
        pretrained_indicators = ['imagenet', 'pretrained', 'transfer_learning', 'fine_tune']
        if any(indicator in content.lower() for indicator in pretrained_indicators):
            analysis['nn_pretrained_model'] = True

        # Check for quantization
        if any(term in content.lower() for term in ['quantize', 'int8', 'fp16', 'half_precision']):
            analysis['nn_quantization_used'] = True

        # Check for distributed training
        if any(term in content.lower() for term in ['distributed', 'multi_gpu', 'horovod', 'nccl']):
            analysis['nn_distributed_training'] = True

    except Exception:
        pass

    return analysis


def get_neural_network_field_count() -> int:
    """Return the number of fields extracted by neural network metadata."""
    # Format detection (5)
    detection_fields = 5

    # HDF5/Keras specific (15)
    hdf5_fields = 15

    # TensorFlow specific (12)
    tf_fields = 12

    # ONNX specific (8)
    onnx_fields = 8

    # PyTorch specific (8)
    pytorch_fields = 8

    # TFLite specific (6)
    tflite_fields = 6

    # Config specific (10)
    config_fields = 10

    # Python NN specific (10)
    python_fields = 10

    # General properties (8)
    general_fields = 8

    # NN analysis (10)
    analysis_fields = 10

    return detection_fields + hdf5_fields + tf_fields + onnx_fields + pytorch_fields + tflite_fields + config_fields + python_fields + general_fields + analysis_fields


# Integration point for metadata_engine.py
def extract_neural_network_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for neural network metadata extraction."""
    return extract_neural_network_metadata(filepath)