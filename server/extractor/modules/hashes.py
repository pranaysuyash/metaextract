"""
File Hashes helpers.
"""
from typing import Dict, Any
import hashlib
import zlib

try:
    from .perceptual_hashes import extract_perceptual_hashes as _extract_perceptual_hashes
except Exception:
    _extract_perceptual_hashes = None


def extract_file_hashes(filepath: str) -> Dict[str, Any]:
    """Extract MD5, SHA256, SHA1, and CRC32 hashes."""
    try:
        hashers = {
            "md5": hashlib.md5(),
            "sha256": hashlib.sha256(),
            "sha1": hashlib.sha1(),
        }
        crc = 0
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                for hasher in hashers.values():
                    hasher.update(chunk)
                crc = zlib.crc32(chunk, crc)
        result = {name: hasher.hexdigest() for name, hasher in hashers.items()}
        result["crc32"] = format(crc & 0xFFFFFFFF, "08x")
        return result
    except Exception as e:
        return {"error": str(e)}


def extract_perceptual_hashes(filepath: str) -> Dict[str, Any]:
    """Compatibility wrapper for perceptual hashes."""
    if _extract_perceptual_hashes is None:
        raise ImportError("perceptual_hashes module not available")
    return _extract_perceptual_hashes(filepath)
