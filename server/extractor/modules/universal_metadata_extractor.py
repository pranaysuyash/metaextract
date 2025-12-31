#!/usr/bin/env python3
"""
Universal Metadata Extractor
Provides fallback extraction for any file format based on available tools
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import hashlib
import struct

class UniversalMetadataExtractor:
    """Universal metadata extractor that handles any file format"""

    def __init__(self):
        self.extractors = {
            # Image formats
            '.jpg': self._extract_image_metadata,
            '.jpeg': self._extract_image_metadata,
            '.png': self._extract_image_metadata,
            '.gif': self._extract_image_metadata,
            '.bmp': self._extract_image_metadata,
            '.tiff': self._extract_image_metadata,
            '.webp': self._extract_image_metadata,

            # Audio formats
            '.mp3': self._extract_audio_metadata,
            '.flac': self._extract_audio_metadata,
            '.wav': self._extract_audio_metadata,
            '.ogg': self._extract_audio_metadata,
            '.m4a': self._extract_audio_metadata,
            '.aac': self._extract_audio_metadata,

            # Video formats
            '.mp4': self._extract_video_metadata,
            '.avi': self._extract_video_metadata,
            '.mov': self._extract_video_metadata,
            '.mkv': self._extract_video_metadata,
            '.webm': self._extract_video_metadata,

            # Document formats
            '.pdf': self._extract_document_metadata,
            '.docx': self._extract_document_metadata,
            '.xlsx': self._extract_document_metadata,
            '.pptx': self._extract_document_metadata,

            # Archive formats
            '.zip': self._extract_archive_metadata,
            '.rar': self._extract_archive_metadata,
            '.tar': self._extract_archive_metadata,
            '.gz': self._extract_archive_metadata,
        }

    def extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract metadata from any file format

        Args:
            filepath: Path to the file

        Returns:
            Dictionary containing extracted metadata
        """
        result = {
            "file_metadata": {},
            "format_specific": {},
            "binary_analysis": {},
            "strings_extracted": [],
            "fields_extracted": 0,
            "extraction_method": "universal"
        }

        try:
            if not filepath or not os.path.exists(filepath):
                result["error"] = "File not found"
                return result

            # Basic file metadata
            result["file_metadata"] = self._extract_file_info(filepath)

            # Get file extension
            ext = Path(filepath).suffix.lower()

            # Use format-specific extractor if available
            if ext in self.extractors:
                result["format_specific"] = self.extractors[ext](filepath)
                result["extraction_method"] = f"format_specific_{ext}"
            else:
                # Fallback to binary analysis
                result["binary_analysis"] = self._extract_binary_metadata(filepath)
                result["strings_extracted"] = self._extract_strings(filepath)
                result["extraction_method"] = "binary_analysis"

            # Count total fields
            total_fields = (
                len(result["file_metadata"]) +
                len(result["format_specific"]) +
                len(result["binary_analysis"]) +
                len(result["strings_extracted"])
            )
            result["fields_extracted"] = total_fields

        except Exception as e:
            result["error"] = f"Universal extraction failed: {str(e)[:200]}"

        return result

    def _extract_file_info(self, filepath: str) -> Dict[str, Any]:
        """Extract basic file information"""
        try:
            stat = os.stat(filepath)
            file_path = Path(filepath)

            return {
                "filename": file_path.name,
                "extension": file_path.suffix,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024*1024), 2),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "is_file": os.path.isfile(filepath),
                "is_readable": os.access(filepath, os.R_OK)
            }
        except Exception as e:
            return {"error": f"File info extraction failed: {str(e)[:100]}"}

    def _extract_binary_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract metadata from binary file analysis"""
        try:
            with open(filepath, 'rb') as f:
                # Read file header (first 512 bytes)
                header = f.read(512)

                # Calculate file hash
                f.seek(0)
                file_content = f.read()
                file_hash = hashlib.md5(file_content).hexdigest()

                # Detect file signatures
                signatures = self._detect_file_signatures(header)

                # Analyze structure
                structure_info = {
                    "file_size": len(file_content),
                    "md5_hash": file_hash,
                    "sha256_hash": hashlib.sha256(file_content).hexdigest()[:32],
                    "header_hex": header[:32].hex() if len(header) >= 32 else header.hex(),
                    "file_signatures": signatures,
                    "entropy_score": self._calculate_entropy(file_content[:4096])
                }

                return structure_info

        except Exception as e:
            return {"error": f"Binary analysis failed: {str(e)[:100]}"}

    def _extract_strings(self, filepath: str, min_length: int = 4) -> List[str]:
        """Extract printable strings from binary file"""
        try:
            strings = []
            current_string = ""

            with open(filepath, 'rb') as f:
                while True:
                    byte = f.read(1)
                    if not byte:
                        break

                    # Check if printable ASCII
                    if 32 <= byte[0] <= 126:
                        current_string += chr(byte[0])
                    else:
                        if len(current_string) >= min_length:
                            strings.append(current_string)
                        current_string = ""

                    # Limit strings extracted
                    if len(strings) >= 100:
                        break

            return strings[:50]  # Return first 50 strings

        except Exception as e:
            return [f"String extraction failed: {str(e)[:100]}"]

    def _detect_file_signatures(self, header: bytes) -> List[str]:
        """Detect known file signatures in header"""
        signatures = []

        # Common file signatures
        magic_bytes = {
            b'\x50\x4B\x03\x04': 'ZIP',
            b'\x50\x4B\x05\x06': 'ZIP_empty',
            b'\x25\x50\x44\x46': 'PDF',
            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'PNG',
            b'\xFF\xD8\xFF': 'JPEG',
            b'\x47\x49\x46\x38': 'GIF',
            b'\x49\x49\x2A\x00': 'TIFF_little',
            b'\x4D\x4D\x00\x2A': 'TIFF_big',
            b'\x00\x00\x01\x00': 'ICO',
            b'\x52\x49\x46\x46': 'RIFF',
            b'\x49\x44\x33': 'MP3',
            b'\x66\x4C\x61\x43': 'FLAC',
            b'\x4D\x34\x41': 'M4A',
            b'\x00\x00\x00\x20\x66\x74\x79\x70': 'MP4',
            b'\x1A\x45\xDF\xA3': 'MKV',
            b'\x52\x61\x72\x21\x1A\x07': 'RAR',
            b'\x75\x73\x74\x61\x72': 'TAR',
            b'\x1F\x8B': 'GZIP',
        }

        for magic, format_name in magic_bytes.items():
            if header.startswith(magic):
                signatures.append(format_name)

        return signatures

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0

        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1

        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * (probability.bit_length() - 1)

        return round(entropy, 4)

    def _extract_image_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract image metadata using PIL"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS

            with Image.open(filepath) as img:
                exif_data = {}
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        for tag, value in exif.items():
                            decoded = TAGS.get(tag, tag)
                            exif_data[str(decoded)] = str(value)[:200]

                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "exif": exif_data
                }
        except Exception as e:
            return {"error": f"Image extraction failed: {str(e)[:100]}"}

    def _extract_audio_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract audio metadata using mutagen"""
        try:
            from mutagen import File

            audio_file = File(filepath)
            if audio_file is None:
                return {"error": "Could not read audio file"}

            metadata = {}
            if audio_file.tags:
                for key, value in audio_file.tags.items():
                    metadata[str(key)] = str(value)[:200]

            result = {
                "format": type(audio_file).__name__,
                "tags": metadata
            }

            if hasattr(audio_file, 'info'):
                result["duration"] = getattr(audio_file.info, 'length', 0)
                result["bitrate"] = getattr(audio_file.info, 'bitrate', 0)

            return result

        except ImportError:
            return {"error": "Mutagen not available"}
        except Exception as e:
            return {"error": f"Audio extraction failed: {str(e)[:100]}"}

    def _extract_video_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract video metadata"""
        try:
            # Basic video metadata extraction
            return {"format": "video", "detected": True}
        except Exception as e:
            return {"error": f"Video extraction failed: {str(e)[:100]}"}

    def _extract_document_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract document metadata"""
        try:
            return {"format": "document", "detected": True}
        except Exception as e:
            return {"error": f"Document extraction failed: {str(e)[:100]}"}

    def _extract_archive_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract archive metadata"""
        try:
            import zipfile
            if filepath.endswith('.zip'):
                with zipfile.ZipFile(filepath, 'r') as zf:
                    return {
                        "format": "zip",
                        "file_count": len(zf.namelist()),
                        "files": zf.namelist()[:10]  # First 10 files
                    }
        except Exception as e:
            return {"error": f"Archive extraction failed: {str(e)[:100]}"}


# Singleton instance
universal_extractor = UniversalMetadataExtractor()

def extract_universal_metadata(filepath: str) -> Dict[str, Any]:
    """Universal metadata extraction function for any file format"""
    return universal_extractor.extract_metadata(filepath)
