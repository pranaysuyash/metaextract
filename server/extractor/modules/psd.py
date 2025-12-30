"""
PSD (Photoshop) Metadata Extraction
Extract basic properties and layer information from Photoshop files
"""

from typing import Dict, Any, Optional
from pathlib import Path


try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False


try:
    from psd_tools import PSDImage
    PSD_TOOLS_AVAILABLE = True
except ImportError:
    PSDImage = None
    PSD_TOOLS_AVAILABLE = False


COLOR_MODE_MAP = {
    0: "Bitmap",
    1: "Grayscale",
    2: "Indexed",
    3: "RGB",
    4: "CMYK",
    5: "Multichannel",
    6: "Duotone",
    7: "Lab",
}


DEPTH_MAP = {
    1: "1-bit",
    8: "8-bit",
    16: "16-bit",
    32: "32-bit (float)",
}


def extract_psd_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from Photoshop PSD files.
    
    Args:
        filepath: Path to PSD file
    
    Returns:
        Dictionary with PSD metadata
    """
    if not PIL_AVAILABLE or Image is None:
        return {"error": "Pillow not installed"}
    
    result = {
        "basic": {},
        "dimensions": {},
        "color": {},
        "layer_info": {},
        "psd_specific": {},
        "fields_extracted": 0
    }
    
    try:
        with Image.open(filepath) as img:
            result["basic"] = {
                "format": getattr(img, 'format', 'PSD'),
                "mode": img.mode,
                "mode_description": COLOR_MODE_MAP.get(img.mode, img.mode),
            }
            
            result["dimensions"] = {
                "width": img.width,
                "height": img.height,
            }
            
            if img.height > 0:
                aspect = img.width / img.height
                result["dimensions"]["aspect_ratio"] = round(aspect, 4)
                result["dimensions"]["aspect_ratio_string"] = f"{img.width}:{img.height}"
            else:
                result["dimensions"]["aspect_ratio"] = 0
                result["dimensions"]["aspect_ratio_string"] = "0:0"
            
            megapixels = (img.width * img.height) / 1000000
            result["dimensions"]["megapixels"] = round(megapixels, 2)
            
            result["color"] = {
                "has_alpha": img.mode in ('RGBA', 'LA', 'PA', 'RGBa'),
                "bands": len(img.getbands()) if hasattr(img, 'getbands') else 0,
            }
            
            if hasattr(img, 'info'):
                for key, value in img.info.items():
                    if key not in ['dpi', 'icc_profile', 'exif']:
                        result["psd_specific"][f"raw_{key}"] = str(value)
                
                if 'dpi' in img.info:
                    result["dimensions"]["dpi_x"] = img.info['dpi'][0]
                    result["dimensions"]["dpi_y"] = img.info['dpi'][1]
                
                if 'icc_profile' in img.info:
                    result["color"]["has_icc_profile"] = True
                    result["color"]["icc_profile_size"] = len(img.info['icc_profile'])
        
        if PSD_TOOLS_AVAILABLE and PSDImage is not None:
            try:
                psd = PSDImage.open(filepath)
                
                layer_info = {
                    "layer_count": len(psd),
                    "layers": [],
                    "has_layer_group": False,
                    "visible_layer_count": 0,
                    "hidden_layer_count": 0,
                }
                
                layer_types = {}
                layer_blend_modes = set()
                
                def process_layer(layer, depth=0):
                    layer_data = {
                        "name": layer.name,
                        "depth": depth,
                        "is_group": hasattr(layer, 'is_group') and layer.is_group,
                        "visible": layer.visible,
                        "opacity": getattr(layer, 'opacity', None),
                        "blend_mode": getattr(layer, 'blend_mode', None),
                    }
                    
                    layer_types[type(layer).__name__] = layer_types.get(type(layer).__name__, 0) + 1
                    
                    if layer.visible:
                        layer_info["visible_layer_count"] += 1
                    else:
                        layer_info["hidden_layer_count"] += 1
                    
                    if layer_data["is_group"]:
                        layer_info["has_layer_group"] = True
                        layer_data["child_count"] = 0
                        
                        if hasattr(layer, 'layers'):
                            layer_data["child_count"] = len(layer.layers)
                            for child in layer.layers:
                                child_data = process_layer(child, depth + 1)
                                layer_info["layers"].append(child_data)
                    else:
                        layer_data["type"] = type(layer).__name__
                        
                        if hasattr(layer, 'width') and hasattr(layer, 'height'):
                            layer_data["width"] = layer.width
                            layer_data["height"] = layer.height
                            layer_data["area"] = layer.width * layer.height
                        
                        if layer.blend_mode:
                            layer_blend_modes.add(layer.blend_mode)
                    
                    return layer_data
                
                for layer in psd:
                    layer_data = process_layer(layer)
                    layer_info["layers"].append(layer_data)
                
                if layer_types:
                    layer_info["layer_types"] = layer_types
                
                if layer_blend_modes:
                    layer_info["blend_modes_used"] = list(layer_blend_modes)
                
                result["layer_info"] = layer_info
                
                if hasattr(psd, 'header'):
                    header = psd.header
                    result["basic"]["psd_version"] = header.version
                    result["basic"]["psd_version_string"] = f"PSD v{header.version}"
                    
                    if hasattr(header, 'depth'):
                        result["color"]["bit_depth"] = header.depth
                        result["color"]["bit_depth_description"] = DEPTH_MAP.get(header.depth, f"{header.depth}-bit")
                    
                    if hasattr(header, 'mode'):
                        result["color"]["color_mode"] = header.mode
                        result["color"]["color_mode_description"] = COLOR_MODE_MAP.get(header.mode, f"Mode {header.mode}")
                
                if hasattr(psd, 'image_resources'):
                    resources = {}
                    for resource in psd.image_resources:
                        resources[resource.id] = resource.name
                    result["psd_specific"]["image_resources"] = resources
                
            except Exception as e:
                result["layer_info"] = {
                    "note": "psd-tools extraction failed, falling back to PIL",
                    "error": str(e),
                    "layers_detected": False
                }
        else:
            result["layer_info"] = {
                "note": "Install psd-tools for full layer extraction: pip install psd-tools",
                "layers_detected": False,
                "layer_count_estimate": "Unknown (PIL limitation)",
                "available_with_psd_tools": True,
                "missing_features": [
                    "individual layer names",
                    "layer visibility",
                    "layer opacity",
                    "layer blend modes",
                    "layer dimensions",
                    "layer groups",
                    "layer types (text, shape, smart object, etc.)"
                ]
            }
        
        total_fields = (
            len(result["basic"]) +
            len(result["dimensions"]) +
            len(result["color"]) +
            len(result["layer_info"]) +
            len(result["psd_specific"])
        )
        result["fields_extracted"] = total_fields
        
        return result
        
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except Exception as e:
        return {"error": f"Failed to extract PSD metadata: {str(e)}"}


def get_psd_field_count() -> int:
    """Return approximate number of PSD fields."""
    return 35
