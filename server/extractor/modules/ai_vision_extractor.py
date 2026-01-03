#!/usr/bin/env python3
"""
AI/ML Vision Metadata Extractor
Extracts metadata from AI-generated images, object detection annotations, and ML training data.
"""

import logging
import json
import struct
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ObjectDetectionExtractor:
    """
    Object detection annotation metadata extractor.
    Supports YOLO, COCO, Pascal VOC, and other formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.detection_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse object detection metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            ext = file_path.suffix.lower()
            
            if ext == '.json':
                return self._parse_coco_json()
            elif ext == '.txt':
                return self._parse_yolo_txt()
            elif ext == '.xml':
                return self._parse_pascal_voc()
            elif ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                return self._parse_embedded_annotations()
            else:
                return {"error": f"Unsupported annotation format: {ext}", "success": False}
                
        except Exception as e:
            logger.error(f"Error parsing object detection: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_coco_json(self) -> Dict[str, Any]:
        """Parse COCO format JSON"""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            
            result = {
                "format": "COCO",
                "is_valid_coco": True,
                "info": data.get("info", {}),
                "licenses": len(data.get("licenses", [])),
                "categories": [],
                "images": len(data.get("images", [])),
                "annotations": len(data.get("annotations", [])),
            }
            
            categories = data.get("categories", [])
            for cat in categories:
                result["categories"].append({
                    "id": cat.get("id"),
                    "name": cat.get("name"),
                    "supercategory": cat.get("supercategory"),
                })
            
            result["category_count"] = len(categories)
            
            if result["annotations"] > 0:
                annotations = data.get("annotations", [])
                result["total_bboxes"] = len([a for a in annotations if "bbox" in a])
                result["total_segmentations"] = len([a for a in annotations if "segmentation" in a])
                result["total_keypoints"] = len([a for a in annotations if "keypoints" in a])
            
            result["success"] = True
            return result
            
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {e}", "success": False}
    
    def _parse_yolo_txt(self) -> Dict[str, Any]:
        """Parse YOLO format text files"""
        try:
            with open(self.filepath, 'r') as f:
                lines = f.readlines()
            
            result = {
                "format": "YOLO",
                "is_valid_yolo": True,
                "total_annotations": len(lines),
                "class_counts": {},
                "bboxes": [],
            }
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    result["class_counts"][class_id] = result["class_counts"].get(class_id, 0) + 1
                    
                    bbox = {
                        "class_id": class_id,
                        "x_center": float(parts[1]),
                        "y_center": float(parts[2]),
                        "width": float(parts[3]),
                        "height": float(parts[4]),
                    }
                    result["bboxes"].append(bbox)
            
            result["unique_classes"] = len(result["class_counts"])
            result["success"] = True
            return result
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _parse_pascal_voc(self) -> Dict[str, Any]:
        """Parse Pascal VOC XML format"""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(self.filepath)
            root = tree.getroot()
            
            result = {
                "format": "Pascal VOC",
                "is_valid_voc": True,
            }
            
            size_elem = root.find('size')
            if size_elem is not None:
                result["width"] = int(size_elem.find('width').text) if size_elem.find('width') is not None else 0
                result["height"] = int(size_elem.find('height').text) if size_elem.find('height') is not None else 0
                result["depth"] = int(size_elem.find('depth').text) if size_elem.find('depth') is not None else 0
            
            objects = root.findall('object')
            result["object_count"] = len(objects)
            result["objects"] = []
            
            for obj in objects:
                obj_info = {
                    "name": obj.find('name').text if obj.find('name') is not None else "",
                    "pose": obj.find('pose').text if obj.find('pose') is not None else "",
                    "truncated": obj.find('truncated').text if obj.find('truncated') is not None else "",
                    "difficult": obj.find('difficult').text if obj.find('difficult') is not None else "",
                }
                
                bndbox = obj.find('bndbox')
                if bndbox is not None:
                    obj_info["bbox"] = {
                        "xmin": int(bndbox.find('xmin').text) if bndbox.find('xmin') is not None else 0,
                        "ymin": int(bndbox.find('ymin').text) if bndbox.find('ymin') is not None else 0,
                        "xmax": int(bndbox.find('xmax').text) if bndbox.find('xmax') is not None else 0,
                        "ymax": int(bndbox.find('ymax').text) if bndbox.find('ymax') is not None else 0,
                    }
                
                result["objects"].append(obj_info)
            
            result["success"] = True
            return result
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _parse_embedded_annotations(self) -> Dict[str, Any]:
        """Parse embedded annotations in image files"""
        try:
            from .exif import ExifParser
            exif_parser = ExifParser(self.filepath)
            exif_result = exif_parser.extract()
            
            result = {
                "has_embedded_annotations": False,
                "annotation_formats": [],
            }
            
            user_comment = exif_result.get("UserComment", "")
            if user_comment:
                result["has_embedded_annotations"] = True
                result["annotation_formats"].append("EXIF UserComment")
            
            result["success"] = True
            return result
            
        except Exception as e:
            return {"error": str(e), "success": False}


class AIGenerationExtractor:
    """
    AI-generated image detection and metadata.
    Extracts C2PA manifest data, provenance, and generation parameters.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.ai_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse AI generation metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_ai_generated": False,
                "c2pa_manifest": False,
                "generation_params": {},
                "provenance": {},
            }
            
            with open(self.filepath, 'rb') as f:
                header = f.read(4096)
            
            if b'c2pa' in header or b'C2PA' in header:
                result["c2pa_manifest"] = True
                result["has_provenance"] = True
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing AI metadata: {e}")
            return {"error": str(e), "success": False}


class SegmentationMaskExtractor:
    """
    Segmentation mask metadata extractor.
    Supports instance, semantic, and panoptic segmentation formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.mask_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse segmentation mask metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            ext = file_path.suffix.lower()
            
            if ext == '.png':
                return self._parse_png_mask()
            elif ext == '.npy':
                return self._parse_numpy_mask()
            elif ext == '.json':
                return self._parse_coco_mask()
            else:
                return {"error": f"Unsupported mask format: {ext}", "success": False}
                
        except Exception as e:
            logger.error(f"Error parsing segmentation mask: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_png_mask(self) -> Dict[str, Any]:
        """Parse PNG segmentation mask"""
        try:
            from PIL import Image
            
            with Image.open(self.filepath) as img:
                result = {
                    "format": "PNG Mask",
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "is_ grayscale": img.mode == 'I' or img.mode == 'L',
                    "is_indexed": img.mode == 'P',
                }
                
                if img.mode == 'I' or img.mode == 'L':
                    import numpy as np
                    arr = np.array(img)
                    result["unique_values"] = int(len(np.unique(arr)))
                    result["min_value"] = int(arr.min())
                    result["max_value"] = int(arr.max())
                
                result["success"] = True
                return result
                
        except ImportError:
            return {"error": "PIL required for PNG mask parsing", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _parse_numpy_mask(self) -> Dict[str, Any]:
        """Parse NumPy array mask"""
        try:
            import numpy as np
            
            arr = np.load(self.filepath)
            result = {
                "format": "NumPy",
                "shape": list(arr.shape),
                "dtype": str(arr.dtype),
                "unique_values": int(len(np.unique(arr))),
                "min_value": float(arr.min()),
                "max_value": float(arr.max()),
            }
            result["success"] = True
            return result
            
        except ImportError:
            return {"error": "NumPy required for .npy parsing", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _parse_coco_mask(self) -> Dict[str, Any]:
        """Parse COCO-style segmentation"""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            
            result = {
                "format": "COCO Segmentation",
                "is_coco_seg": True,
                "annotations": len(data),
            }
            
            if data:
                first = data[0]
                result["has_rle"] = "segmentation" in first
                result["has_poly"] = "poly" in first
            
            result["success"] = True
            return result
            
        except Exception as e:
            return {"error": str(e), "success": False}


class MLModelMetadataExtractor:
    """
    Machine learning model metadata extractor for model-in-the-loop scenarios.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse ML model metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            ext = file_path.suffix.lower()
            
            if ext == '.onnx':
                return self._parse_onnx()
            elif ext in ['.pt', '.pth', '.ckpt']:
                return self._parse_pytorch()
            elif ext == '.h5':
                return self._parse_h5()
            else:
                return {"error": f"Unsupported model format: {ext}", "success": False}
                
        except Exception as e:
            logger.error(f"Error parsing ML model: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_onnx(self) -> Dict[str, Any]:
        """Parse ONNX model metadata"""
        try:
            import onnx
            
            model = onnx.load(self.filepath)
            
            result = {
                "format": "ONNX",
                "opset_version": model.opset_import[0].version if model.opset_import else 0,
                "producer_name": model.producer_name,
                "producer_version": model.producer_version,
                "domain": model.domain,
                "metadata_props": dict(model.metadata_props),
                "input_count": len(model.graph.input),
                "output_count": len(model.graph.output),
                "node_count": len(model.graph.node),
            }
            
            result["input_names"] = [inp.name for inp in model.graph.input[:5]]
            result["output_names"] = [out.name for out in model.graph.output[:5]]
            
            result["success"] = True
            return result
            
        except ImportError:
            return {"error": "ONNX required for .onnx parsing", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _parse_pytorch(self) -> Dict[str, Any]:
        """Parse PyTorch checkpoint metadata"""
        try:
            import torch
            
            checkpoint = torch.load(self.filepath, map_location='cpu')
            
            result = {
                "format": "PyTorch",
                "is_checkpoint": True,
            }
            
            if isinstance(checkpoint, dict):
                result["keys"] = list(checkpoint.keys())[:10]
                result["key_count"] = len(checkpoint.keys())
                
                if 'state_dict' in checkpoint:
                    state = checkpoint['state_dict']
                    result["state_dict_keys"] = list(state.keys())[:5]
                    result["state_dict_count"] = len(state.keys())
                
                if 'epoch' in checkpoint:
                    result["epoch"] = int(checkpoint['epoch'])
                
                if 'learning_rate' in checkpoint:
                    result["learning_rate"] = float(checkpoint['learning_rate'])
                
                if 'optimizer' in checkpoint:
                    result["has_optimizer_state"] = True
            
            result["success"] = True
            return result
            
        except ImportError:
            return {"error": "PyTorch required for .pt parsing", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _parse_h5(self) -> Dict[str, Any]:
        """Parse HDF5/Keras model metadata"""
        try:
            import h5py
            
            with h5py.File(self.filepath, 'r') as f:
                result = {
                    "format": "HDF5/Keras",
                    "keys": list(f.keys())[:10],
                    "key_count": len(f.keys()),
                }
                
                if 'model_config' in f:
                    config = f['model_config'][()]
                    try:
                        import json
                        config_dict = json.loads(config) if isinstance(config, str) else json.loads(config.decode('utf-8'))
                        result["model_architecture"] = config_dict.get('class_name', 'Unknown')
                    except:
                        result["has_model_config"] = True
                
                result["success"] = True
                return result
            
        except ImportError:
            return {"error": "h5py required for .h5 parsing", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
