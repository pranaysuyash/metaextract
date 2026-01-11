#!/usr/bin/env python3
"""
Comprehensive Image Format Registry
Maps all known image formats, extensions, MIME types, and standards.
"""

from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


class ImageCategory(Enum):
    RASTER = "raster"
    RAW_CAMERA = "raw_camera"
    VECTOR = "vector"
    COMPOSITE = "composite"
    SCIENTIFIC = "scientific"
    CINEMA = "cinema"
    THREE_D = "3d"
    ANIMATED = "animated"
    DOCUMENT = "document"
    MEDICAL = "medical"
    REMOTE_SENSING = "remote_sensing"
    SPECIALIZED = "specialized"


IMAGE_FORMAT_REGISTRY: Dict[str, Dict] = {
    # RASTER FORMATS
    "JPEG": {
        "extensions": [".jpg", ".jpeg", ".jfif", ".jpe"],
        "mime_types": ["image/jpeg"],
        "category": ImageCategory.RASTER,
        "standard": "ISO 10918-1",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["lossy"],
        "metadata_standards": ["EXIF", "IPTC", "XMP", "ICC"],
    },
    "JPEG2000": {
        "extensions": [".jp2", ".jpx", ".jpm", ".mj2"],
        "mime_types": ["image/jp2", "image/jpx", "image/jpm"],
        "category": ImageCategory.RASTER,
        "standard": "ISO 15444",
        "max_components": 256,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossy", "lossless"],
        "metadata_standards": ["EXIF", "IPTC", "XMP", "ICC"],
    },
    "PNG": {
        "extensions": [".png"],
        "mime_types": ["image/png"],
        "category": ImageCategory.RASTER,
        "standard": "ISO 15948",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossless"],
        "metadata_standards": ["tEXt", "zTXt", "iTXt", "eXIf", "XMP", "ICC"],
    },
    "GIF": {
        "extensions": [".gif"],
        "mime_types": ["image/gif"],
        "category": ImageCategory.ANIMATED,
        "standard": "GIF89a",
        "max_components": 3,
        "max_bit_depth": 8,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossless"],
        "metadata_standards": ["XMP", "ICC"],
    },
    "APNG": {
        "extensions": [".png", ".apng"],
        "mime_types": ["image/apng"],
        "category": ImageCategory.ANIMATED,
        "standard": "PNG + animation",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossless"],
        "metadata_standards": ["acTL", "fcTL", "XMP", "ICC"],
    },
    "WebP": {
        "extensions": [".webp"],
        "mime_types": ["image/webp"],
        "category": ImageCategory.RASTER,
        "standard": "WebP",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossy", "lossless"],
        "metadata_standards": ["EXIF", "XMP", "ICC", "ANIM"],
    },
    "BMP": {
        "extensions": [".bmp", ".dib"],
        "mime_types": ["image/bmp", "image/x-bmp"],
        "category": ImageCategory.RASTER,
        "standard": "BMP",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "RLE"],
        "metadata_standards": ["XMP", "ICC"],
    },
    "TIFF": {
        "extensions": [".tif", ".tiff"],
        "mime_types": ["image/tiff", "image/x-tiff"],
        "category": ImageCategory.RASTER,
        "standard": "TIFF 6.0",
        "max_components": "unlimited",
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["none", "LZW", "ZIP", "JPEG", "PackBits"],
        "metadata_standards": ["EXIF", "IPTC", "XMP", "ICC", "GPS", "MakerNotes"],
    },
    "AVIF": {
        "extensions": [".avif", ".heic"],
        "mime_types": ["image/avif", "image/heic"],
        "category": ImageCategory.RASTER,
        "standard": "AV1 Image File Format",
        "max_components": 4,
        "max_bit_depth": 12,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossy", "lossless"],
        "metadata_standards": ["EXIF", "XMP", "ICC", "IPTC"],
    },
    "HEIF": {
        "extensions": [".heif", ".heic"],
        "mime_types": ["image/heif", "image/heic"],
        "category": ImageCategory.RASTER,
        "standard": "ISO 23008-12",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossy", "lossless"],
        "metadata_standards": ["EXIF", "XMP", "ICC", "IPTC"],
    },
    "JPEG_XL": {
        "extensions": [".jxl"],
        "mime_types": ["image/jxl"],
        "category": ImageCategory.RASTER,
        "standard": "ISO 18181",
        "max_components": "unlimited",
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossy", "lossless", "near-lossless"],
        "metadata_standards": ["EXIF", "XMP", "ICC"],
    },
    
    # CAMERA RAW FORMATS
    "DNG": {
        "extensions": [".dng"],
        "mime_types": ["image/x-adobe-dng"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP + DNG",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "JPEG", "Lossless"],
        "metadata_standards": ["EXIF", "XMP", "ICC", "MakerNotes", "DNGPrivateData"],
    },
    "CR2": {
        "extensions": [".cr2"],
        "mime_types": ["image/x-canon-cr2"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "JPEG"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "CR3": {
        "extensions": [".cr3"],
        "mime_types": ["image/x-canon-cr3"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "ISO BMFF",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": True,
        "compression": ["none", "JPEG", "Lossless"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "NEF": {
        "extensions": [".nef"],
        "mime_types": ["image/x-nikon-nef"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "JPEG", "Lossless"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "ARW": {
        "extensions": [".arw"],
        "mime_types": ["image/x-sony-arw"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "JPEG"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "ORF": {
        "extensions": [".orf"],
        "mime_types": ["image/x-olympus-orf"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "JPEG"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "RAF": {
        "extensions": [".raf"],
        "mime_types": ["image/x-fuji-raf"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "JPEG"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "RW2": {
        "extensions": [".rw2"],
        "mime_types": ["image/x-panasonic-rw2"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "JPEG"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "PEF": {
        "extensions": [".pef"],
        "mime_types": ["image/x-pentax-pef"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 14,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "Lossless"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "X3F": {
        "extensions": [".x3f"],
        "mime_types": ["image/x-sigma-x3f"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "Foveon X3",
        "max_components": 3,
        "max_bit_depth": 14,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "JPEG"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "SRW": {
        "extensions": [".srw"],
        "mime_types": ["image/x-samsung-srw"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "TIFF/EP",
        "max_components": 3,
        "max_bit_depth": 14,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "Lossless"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    "RAW_GENERIC": {
        "extensions": [".raw"],
        "mime_types": ["image/x-raw"],
        "category": ImageCategory.RAW_CAMERA,
        "standard": "Various",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none"],
        "metadata_standards": ["EXIF", "XMP", "MakerNotes"],
    },
    
    # CINEMA/POST FORMATS
    "OpenEXR": {
        "extensions": [".exr"],
        "mime_types": ["image/x-exr"],
        "category": ImageCategory.CINEMA,
        "standard": "OpenEXR",
        "max_components": "unlimited",
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["none", "RLE", "ZIP", "B44", "B44A"],
        "metadata_standards": ["EXR", "XMP", "ICC"],
    },
    "DPX": {
        "extensions": [".dpx"],
        "mime_types": ["image/x-dpx"],
        "category": ImageCategory.CINEMA,
        "standard": "SMPTE 268M",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "RLE"],
        "metadata_standards": ["SMPTE", "XMP"],
    },
    "CIN": {
        "extensions": [".cin"],
        "mime_types": ["image/x-cin"],
        "category": ImageCategory.CINEMA,
        "standard": "Kodak Cineon",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none"],
        "metadata_standards": ["Cineon", "XMP"],
    },
    "PSD": {
        "extensions": [".psd", ".psb"],
        "mime_types": ["image/vnd.adobe.photoshop", "image/x-photoshop"],
        "category": ImageCategory.COMPOSITE,
        "standard": "Photoshop Document",
        "max_components": 56,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["none", "RLE", "ZIP"],
        "metadata_standards": ["XMP", "IPTC", "ICC", "8BIM"],
    },
    "CinemaDNG": {
        "extensions": [".dng", ".cin"],
        "mime_types": ["image/x-adobe-dng"],
        "category": ImageCategory.CINEMA,
        "standard": "SMPTE ST 268/268M",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "JPEG", "Lossless"],
        "metadata_standards": ["EXIF", "XMP", "ICC", "DNG"],
    },
    
    # VECTOR FORMATS
    "SVG": {
        "extensions": [".svg", ".svgz"],
        "mime_types": ["image/svg+xml"],
        "category": ImageCategory.VECTOR,
        "standard": "SVG 1.1/2.0",
        "components": "unlimited",
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["none", "gzip"],
        "metadata_standards": ["RDF", "Dublin Core", "XMP", "ARIA"],
    },
    
    # PROFESSIONAL RAW
    "ARRI_RAW": {
        "extensions": [".ari", ".mov"],
        "mime_types": ["video/x-arri-raw"],
        "category": ImageCategory.CINEMA,
        "standard": "ARRI ALEXA",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": True,
        "compression": ["lossless"],
        "metadata_standards": ["ARRI", "EXIF", "XMP"],
    },
    "RED_RAW": {
        "extensions": [".r3d"],
        "mime_types": ["video/x-red-r3d"],
        "category": ImageCategory.CINEMA,
        "standard": "REDcode RAW",
        "max_components": 3,
        "max_bit_depth": 16,
        "supports_alpha": False,
        "supports_animation": True,
        "compression": ["REDcode"],
        "metadata_standards": ["RED", "EXIF", "XMP"],
    },
    
    # SPECIALIZED
    "ICO": {
        "extensions": [".ico"],
        "mime_types": ["image/x-icon", "image/vnd.microsoft.icon"],
        "category": ImageCategory.SPECIALIZED,
        "standard": "ICO",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none"],
        "metadata_standards": ["PNG"],
    },
    "CUR": {
        "extensions": [".cur"],
        "mime_types": ["image/x-win-bitmap"],
        "category": ImageCategory.SPECIALIZED,
        "standard": "CUR",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none"],
        "metadata_standards": [],
    },
    "TGA": {
        "extensions": [".tga", ".tpic"],
        "mime_types": ["image/x-targa"],
        "category": ImageCategory.RASTER,
        "standard": "TGA Truevision",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "RLE"],
        "metadata_standards": [],
    },
    "PCX": {
        "extensions": [".pcx"],
        "mime_types": ["image/x-pcx"],
        "category": ImageCategory.RASTER,
        "standard": "PC Paintbrush",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["RLE"],
        "metadata_standards": [],
    },
    "PNM": {
        "extensions": [".pnm", ".ppm", ".pgm", ".pbm", ".pam"],
        "mime_types": ["image/x-portable-anymap"],
        "category": ImageCategory.RASTER,
        "standard": "Netpbm",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none"],
        "metadata_standards": [],
    },
    "QOI": {
        "extensions": [".qoi"],
        "mime_types": ["image/qoi"],
        "category": ImageCategory.RASTER,
        "standard": "QOI Image Format",
        "max_components": 4,
        "max_bit_depth": 8,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["lossless"],
        "metadata_standards": ["XMP"],
    },
    "FLIF": {
        "extensions": [".flif"],
        "mime_types": ["image/flif"],
        "category": ImageCategory.RASTER,
        "standard": "FLIF",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossless", "near-lossless"],
        "metadata_standards": [],
    },
    "WebP_Animation": {
        "extensions": [".webp"],
        "mime_types": ["image/webp"],
        "category": ImageCategory.ANIMATED,
        "standard": "WebP Animated",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["lossy", "lossless"],
        "metadata_standards": ["EXIF", "XMP", "ICC", "ANIM"],
    },
    
    # HDR FORMATS
    "Radiance_HDR": {
        "extensions": [".hdr", ".rgbe"],
        "mime_types": ["image/vnd.radiance"],
        "category": ImageCategory.SCIENTIFIC,
        "standard": "Radiance RGBE",
        "max_components": 3,
        "max_bit_depth": 32,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["runlength"],
        "metadata_standards": [],
    },
    "OpenHDR": {
        "extensions": [".hdr", ".exr"],
        "mime_types": ["image/x-openexr"],
        "category": ImageCategory.SCIENTIFIC,
        "standard": "OpenEXR HDR",
        "max_components": "unlimited",
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["none", "RLE", "ZIP"],
        "metadata_standards": ["EXR", "XMP", "ICC"],
    },
    
    # MEDICAL IMAGING
    "DICOM_Image": {
        "extensions": [".dcm", ".dicom"],
        "mime_types": ["application/dicom"],
        "category": ImageCategory.MEDICAL,
        "standard": "DICOM PS3.1",
        "max_components": 16,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["none", "JPEG", "JPEG2000", "RLE"],
        "metadata_standards": ["DICOM", "XMP"],
    },
    "NIfTI": {
        "extensions": [".nii", ".nii.gz", ".img", ".hdr"],
        "mime_types": ["application/x-nifti"],
        "category": ImageCategory.MEDICAL,
        "standard": "NIfTI-1",
        "max_components": 16,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "gzip"],
        "metadata_standards": ["NIfTI", "DICOM"],
    },
    
    # SCIENTIFIC IMAGING
    "FITS": {
        "extensions": [".fits", ".fit", ".fts"],
        "mime_types": ["image/fits"],
        "category": ImageCategory.SCIENTIFIC,
        "standard": "FITS 4.0",
        "max_components": 999,
        "max_bit_depth": 64,
        "supports_alpha": False,
        "supports_animation": False,
        "compression": ["none", "RICE", "GZIP", "HCompress"],
        "metadata_standards": ["FITS", "WCS"],
    },
    
    # 3D/POINT CLOUD
    "PLY": {
        "extensions": [".ply"],
        "mime_types": ["model/ply"],
        "category": ImageCategory.THREE_D,
        "standard": "PLY",
        "max_components": "unlimited",
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "ascii"],
        "metadata_standards": ["XMP"],
    },
    "glTF": {
        "extensions": [".gltf", ".glb"],
        "mime_types": ["model/gltf+json", "model/gltf-binary"],
        "category": ImageCategory.THREE_D,
        "standard": "glTF 2.0",
        "max_components": "unlimited",
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": True,
        "compression": ["none", "gzip"],
        "metadata_standards": ["XMP"],
    },
    
    # REMOTE SENSING
    "GeoTIFF": {
        "extensions": [".tif", ".tiff", ".gtif", ".geotif"],
        "mime_types": ["image/tiff", "image/x-geotiff"],
        "category": ImageCategory.REMOTE_SENSING,
        "standard": "GeoTIFF 1.0",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "LZW", "ZIP", "PackBits"],
        "metadata_standards": ["GeoTIFF", "EXIF", "XMP", "ICC"],
    },
    "Cloud_Optimized_GeoTIFF": {
        "extensions": [".tif", ".tiff", ".cog"],
        "mime_types": ["image/tiff"],
        "category": ImageCategory.REMOTE_SENSING,
        "standard": "COG",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["none", "LZW", "DEFLATE"],
        "metadata_standards": ["GeoTIFF", "EXIF", "XMP"],
    },
    
    # VR/360
    "Equirectangular_Panorama": {
        "extensions": [".jpg", ".png", ".tif", ".exr"],
        "mime_types": ["image/jpeg", "image/png"],
        "category": ImageCategory.SPECIALIZED,
        "standard": "Photo Sphere",
        "max_components": 4,
        "max_bit_depth": 16,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["lossy", "lossless"],
        "metadata_standards": ["GPano", "EXIF", "XMP"],
    },
    "CubeMap": {
        "extensions": [".jpg", ".png", ".hdr", ".exr"],
        "mime_types": ["image/jpeg", "image/png"],
        "category": ImageCategory.SPECIALIZED,
        "standard": "CubeMap",
        "max_components": 4,
        "max_bit_depth": 32,
        "supports_alpha": True,
        "supports_animation": False,
        "compression": ["lossy", "lossless"],
        "metadata_standards": ["XMP"],
    },
}


METADATA_STANDARDS: Dict[str, Dict] = {
    "EXIF": {
        "full_name": "Exchangeable Image File Format",
        "version": "2.32",
        "standard": "CIPA DC-008",
        "tags": 300,
        "extensions": ["exif", "Exif", "EXIF"],
    },
    "IPTC": {
        "full_name": "International Press Telecommunications Council",
        "version": "IIM 4.2",
        "standard": "IPTC Photo Metadata",
        "tags": 80,
        "extensions": ["8BIM", "iptc", "IPTC"],
    },
    "XMP": {
        "full_name": "Extensible Metadata Platform",
        "version": "2008",
        "standard": "W3C XMP",
        "tags": "infinite",
        "extensions": ["xmp", "XMP", "xml"],
    },
    "ICC": {
        "full_name": "International Color Consortium",
        "version": "4.3",
        "standard": "ICC Profile",
        "tags": 200,
        "extensions": ["icc", "ICM", "prof"],
    },
    "GPS": {
        "full_name": "GPS Exchange Format",
        "version": "2.1",
        "standard": "EXIF GPS",
        "tags": 30,
        "extensions": ["GPS"],
    },
    "MakerNotes": {
        "full_name": "Camera Maker Notes",
        "version": "proprietary",
        "standard": "Various",
        "tags": "proprietary",
        "extensions": ["MakerNote"],
    },
    "Dublin_Core": {
        "full_name": "Dublin Core Metadata Initiative",
        "version": "1.1",
        "standard": "ISO 15836",
        "tags": 15,
        "extensions": ["dc", "dublin core"],
    },
    "GPano": {
        "full_name": "Google Photo Sphere",
        "version": "1.0",
        "standard": "XMP Panorama",
        "tags": 20,
        "extensions": ["GPano", "gphoto"],
    },
    "C2PA": {
        "full_name": "Coalition for Content Authenticity",
        "version": "1.0",
        "standard": "C2PA Spec",
        "tags": "dynamic",
        "extensions": ["c2pa", "manifest"],
    },
    "DNG": {
        "full_name": "Digital Negative",
        "version": "1.6",
        "standard": "TIFF/EP + DNG",
        "tags": 100,
        "extensions": ["dng", "DNGPrivateData"],
    },
    "OpenEXR": {
        "full_name": "OpenEXR",
        "version": "3.0",
        "standard": "OpenEXR",
        "tags": 50,
        "extensions": ["exr", "EXR"],
    },
    "XMP_Rights": {
        "full_name": "XMP Rights Management",
        "version": "2005",
        "standard": "XMP",
        "tags": 10,
        "extensions": ["xmpRights"],
    },
}


def get_all_extensions() -> Set[str]:
    """Get all file extensions"""
    extensions = set()
    for format_info in IMAGE_FORMAT_REGISTRY.values():
        extensions.update(format_info.get("extensions", []))
    return extensions


def get_format_by_extension(ext: str) -> Optional[Dict]:
    """Get format info by extension"""
    ext = ext.lower() if ext.startswith(".") else f".{ext}"
    for format_name, format_info in IMAGE_FORMAT_REGISTRY.items():
        if ext in format_info.get("extensions", []):
            return format_info
    return None


def get_all_mime_types() -> Set[str]:
    """Get all MIME types"""
    mime_types = set()
    for format_info in IMAGE_FORMAT_REGISTRY.values():
        mime_types.update(format_info.get("mime_types", []))
    return mime_types


def get_formats_by_category(category: ImageCategory) -> List[str]:
    """Get all formats in a category"""
    return [name for name, info in IMAGE_FORMAT_REGISTRY.items() 
            if info.get("category") == category]


def get_formats_by_metadata_standard(standard: str) -> List[str]:
    """Get formats supporting a metadata standard"""
    results = []
    for format_name, format_info in IMAGE_FORMAT_REGISTRY.items():
        if standard in format_info.get("metadata_standards", []):
            results.append(format_name)
    return results


def get_animated_formats() -> List[str]:
    """Get formats supporting animation"""
    return [name for name, info in IMAGE_FORMAT_REGISTRY.items() 
            if info.get("supports_animation", False)]


def get_lossless_formats() -> List[str]:
    """Get formats supporting lossless compression"""
    results = []
    for format_name, format_info in IMAGE_FORMAT_REGISTRY.items():
        compression = info.get("compression", [])
        if "lossless" in compression or "none" in compression:
            results.append(format_name)
    return results


def get_high_bit_depth_formats() -> List[str]:
    """Get formats supporting >8 bit depth"""
    return [name for name, info in IMAGE_FORMAT_REGISTRY.items() 
            if info.get("max_bit_depth", 8) > 8]


def get_transparency_formats() -> List[str]:
    """Get formats supporting alpha channel"""
    return [name for name, info in IMAGE_FORMAT_REGISTRY.items() 
            if info.get("supports_alpha", False)]


if __name__ == "__main__":
    print(f"Total formats registered: {len(IMAGE_FORMAT_REGISTRY)}")
    print(f"Total extensions: {len(get_all_extensions())}")
    print(f"Total MIME types: {len(get_all_mime_types())}")
    print(f"Animated formats: {len(get_animated_formats())}")
    print(f"Lossless formats: {len(get_lossless_formats())}")
    print(f"High bit depth formats: {len(get_high_bit_depth_formats())}")
    print(f"Transparency formats: {len(get_transparency_formats())}")
