#!/usr/bin/env python3
"""
Machine Learning/AI Model Extractor for MetaExtract.
Extracts metadata from ONNX, TensorFlow, PyTorch, and other ML model formats.
"""

import os
import sys
import json
import struct
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

TORCH_AVAILABLE = True
try:
    import torch
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - model extraction limited")

ONNX_AVAILABLE = True
try:
    import onnx
except ImportError:
    ONNX_AVAILABLE = False
    logger.debug("ONNX not available")

TENSORFLOW_AVAILABLE = True
try:
    import tensorflow as tf
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.debug("TensorFlow not available")


class MLModelFormat(Enum):
    PYTORCH = "pytorch"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"
    TFLITE = "tflite"
    TORCHSCRIPT = "torchscript"
    SAFETENSORS = "safetensors"
    UNKNOWN = "unknown"


@dataclass
class ONNXMetadata:
    ir_version: Optional[int] = None
    opset_import: Dict[str, int] = field(default_factory=dict)
    producer_name: Optional[str] = None
    producer_version: Optional[str] = None
    domain: Optional[str] = None
    model_version: Optional[int] = None
    doc_string: Optional[str] = None
    graph_name: Optional[str] = None
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    node_count: int = 0
    initializer_count: int = 0


@dataclass
class PyTorchMetadata:
    version: Optional[str] = None
    model_name: Optional[str] = None
    model_type: Optional[str] = None
    training: bool = False
    parameters_count: int = 0
    buffers_count: int = 0
    layers: List[Dict[str, Any]] = field(default_factory=list)
    modules: List[Dict[str, Any]] = field(default_factory=list)


class MLExtractor:
    """Extract ML/AI model metadata from various formats."""

    def __init__(self):
        pass

    def detect_format(self, filepath: str) -> MLModelFormat:
        """Detect ML model format from file header and extension."""
        ext = Path(filepath).suffix.lower()

        if ext in ['.pt', '.pth']:
            if self._is_torchscript(filepath):
                return MLModelFormat.TORCHSCRIPT
            return MLModelFormat.PYTORCH
        elif ext in ['.onnx']:
            return MLModelFormat.ONNX
        elif ext in ['.pb', '.ckpt']:
            return MLModelFormat.TENSORFLOW
        elif ext in ['.tflite']:
            return MLModelFormat.TFLITE
        elif ext in ['.safetensors']:
            return MLModelFormat.SAFETENSORS

        with open(filepath, 'rb') as f:
            header = f.read(8)
            if header[:2] == b'\x00\x08':
                return MLModelFormat.PYTORCH
            elif header[:4] == b'ONNX':
                return MLModelFormat.ONNX

        return MLModelFormat.UNKNOWN

    def _is_torchscript(self, filepath: str) -> bool:
        """Check if file is a TorchScript model."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(2)
                return header == b'\x00\x08'
        except:
            return False

    def extract_onnx_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract ONNX model metadata."""
        if not ONNX_AVAILABLE:
            return {"error": "ONNX library not available"}

        try:
            model = onnx.load(filepath)

            metadata = ONNXMetadata(
                ir_version=model.ir_version,
                producer_name=model.producer_name,
                producer_version=model.producer_version,
                domain=model.domain,
                model_version=model.model_version,
                doc_string=model.doc_string,
            )

            for imp in model.opset_import:
                metadata.opset_import[imp.domain] = imp.version

            graph = model.graph
            metadata.graph_name = graph.name

            for inp in graph.input:
                if inp.name in [init.name for init in graph.initializer]:
                    continue
                dims = []
                if hasattr(inp.type, 'tensor_type'):
                    shape = inp.type.tensor_type.shape
                    for d in shape.dim:
                        if d.dim_value:
                            dims.append(d.dim_value)
                        elif d.dim_param:
                            dims.append(d.dim_param)
                metadata.inputs.append({
                    "name": inp.name,
                    "dtype": str(inp.type.tensor_type.elem_type) if hasattr(inp.type, 'tensor_type') else None,
                    "shape": dims,
                })

            for out in graph.output:
                dims = []
                if hasattr(out.type, 'tensor_type'):
                    shape = out.type.tensor_type.shape
                    for d in shape.dim:
                        if d.dim_value:
                            dims.append(d.dim_value)
                        elif d.dim_param:
                            dims.append(d.dim_param)
                metadata.outputs.append({
                    "name": out.name,
                    "dtype": str(out.type.tensor_type.elem_type) if hasattr(out.type, 'tensor_type') else None,
                    "shape": dims,
                })

            metadata.node_count = len(graph.node)
            metadata.initializer_count = len(graph.initializer)

            result = {
                "format": "onnx",
                "ir_version": metadata.ir_version,
                "producer_name": metadata.producer_name,
                "producer_version": metadata.producer_version,
                "domain": metadata.domain,
                "model_version": metadata.model_version,
                "opset_import": metadata.opset_import,
                "graph_name": metadata.graph_name,
                "input_count": len(metadata.inputs),
                "output_count": len(metadata.outputs),
                "node_count": metadata.node_count,
                "initializer_count": metadata.initializer_count,
                "inputs": metadata.inputs,
                "outputs": metadata.outputs,
            }

            return result

        except Exception as e:
            logger.error(f"Error extracting ONNX metadata: {e}")
            return {"error": str(e)}

    def extract_pytorch_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract PyTorch model metadata."""
        if not TORCH_AVAILABLE:
            return {"error": "PyTorch not available"}

        try:
            checkpoint = torch.load(filepath, map_location='cpu')

            metadata = PyTorchMetadata(
                version=str(torch.__version__),
            )

            if isinstance(checkpoint, dict):
                if 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                    if hasattr(state_dict, 'keys'):
                        metadata.parameters_count = len(list(state_dict.keys()))
                elif 'model' in checkpoint:
                    model = checkpoint['model']
                    if hasattr(model, 'state_dict'):
                        metadata.parameters_count = len(list(model.state_dict().keys()))

                if 'epoch' in checkpoint:
                    metadata.model_name = f"epoch_{checkpoint['epoch']}"
                if 'arch' in checkpoint:
                    metadata.model_type = checkpoint['arch']
                if 'training' in checkpoint:
                    metadata.training = checkpoint['training']

            if isinstance(checkpoint, torch.nn.Module):
                metadata.training = checkpoint.training
                metadata.parameters_count = sum(p.numel() for p in checkpoint.parameters())
                metadata.layers = []
                for name, module in checkpoint.named_modules():
                    if len(list(module.parameters())) > 0:
                        layer_info = {
                            "name": name,
                            "type": type(module).__name__,
                        }
                        if hasattr(module, 'in_features'):
                            layer_info["in_features"] = module.in_features
                        if hasattr(module, 'out_features'):
                            layer_info["out_features"] = module.out_features
                        if hasattr(module, 'kernel_size'):
                            layer_info["kernel_size"] = module.kernel_size
                        metadata.layers.append(layer_info)

            result = {
                "format": "pytorch",
                "torch_version": metadata.version,
                "model_name": metadata.model_name,
                "model_type": metadata.model_type,
                "training_mode": metadata.training,
                "parameters_count": metadata.parameters_count,
                "layers_count": len(metadata.layers),
                "layers": metadata.layers,
            }

            if isinstance(checkpoint, dict):
                result["checkpoint_keys"] = list(checkpoint.keys())[:20]

            return result

        except Exception as e:
            logger.error(f"Error extracting PyTorch metadata: {e}")
            return {"error": str(e)}

    def extract_torchscript_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract TorchScript model metadata."""
        if not TORCH_AVAILABLE:
            return {"error": "PyTorch not available"}

        try:
            model = torch.jit.load(filepath)
            metadata = PyTorchMetadata(
                version=str(torch.__version__),
                training=model.training,
            )

            if hasattr(model, 'graph'):
                metadata.parameters_count = len(list(model.parameters()))

            layers = []
            for name, module in model.named_modules():
                if len(list(module.parameters())) > 0:
                    layers.append({
                        "name": name,
                        "type": type(module).__name__,
                    })

            result = {
                "format": "torchscript",
                "torch_version": metadata.version,
                "training_mode": metadata.training,
                "parameters_count": metadata.parameters_count,
                "layers": layers,
            }

            return result

        except Exception as e:
            logger.error(f"Error extracting TorchScript metadata: {e}")
            return {"error": str(e)}

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract ML model metadata from a file."""
        result = {
            "source": "metaextract_ml_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "ml_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        format_type = self.detect_format(filepath)
        result["format_detected"] = format_type.value

        if format_type == MLModelFormat.ONNX:
            result["ml_metadata"] = self.extract_onnx_metadata(filepath)
            result["extraction_success"] = "error" not in result["ml_metadata"]

        elif format_type == MLModelFormat.PYTORCH:
            result["ml_metadata"] = self.extract_pytorch_metadata(filepath)
            result["extraction_success"] = "error" not in result["ml_metadata"]

        elif format_type == MLModelFormat.TORCHSCRIPT:
            result["ml_metadata"] = self.extract_torchscript_metadata(filepath)
            result["extraction_success"] = "error" not in result["ml_metadata"]

        else:
            result["ml_metadata"] = {"message": "Unsupported ML model format"}
            result["extraction_success"] = False

        return result


def extract_ml_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract ML model metadata."""
    extractor = MLExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ml_extractor.py <model.onnx>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_ml_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
