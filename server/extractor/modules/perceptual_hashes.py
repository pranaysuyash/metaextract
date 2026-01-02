"""
Perceptual Hashing Module
Visual similarity detection using multiple hash algorithms
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import base64
import io


try:
    from PIL import Image
    import imagehash
    phash = imagehash.phash
    dhash = imagehash.dhash
    ahash = imagehash.average_hash
    whash = imagehash.whash
    average_hash = imagehash.average_hash
    blockhash = imagehash.average_hash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    Image = None
    phash = None
    dhash = None
    ahash = None
    whash = None
    average_hash = None
    blockhash = None
    IMAGEHASH_AVAILABLE = True


def extract_perceptual_hashes(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract multiple perceptual hashes from an image for visual similarity detection.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with all perceptual hashes and similarity metrics
    """
    if not IMAGEHASH_AVAILABLE or Image is None:
        raise ImportError("imagehash and Pillow are required for perceptual hashing")
    
    try:
        with Image.open(filepath) as img:
            img = img.convert('RGB')
            
            result = {
                "perceptual_hashes": {},
                "hash_comparison": {},
                "fields_extracted": 0
            }
            
            # pHash (Perceptual Hash) - most effective for similarity
            try:
                phash_val = phash(img) if phash else None
                if phash_val:
                    result["perceptual_hashes"]["phash"] = str(phash_val)
                    result["perceptual_hashes"]["phash_hex"] = phash_val.tohex()
                    result["perceptual_hashes"]["phash_b64"] = base64.b64encode(phash_val.tobytes()).decode('ascii')
            except Exception as e:
                result["perceptual_hashes"]["phash"] = None
            
            # dHash (Difference Hash)
            try:
                dhash_val = dhash(img) if dhash else None
                if dhash_val:
                    result["perceptual_hashes"]["dhash"] = str(dhash_val)
                    result["perceptual_hashes"]["dhash_hex"] = dhash_val.tohex()
            except Exception as e:
                result["perceptual_hashes"]["dhash"] = None
            
            # aHash (Average Hash)
            try:
                ahash_val = ahash(img) if ahash else None
                if ahash_val:
                    result["perceptual_hashes"]["ahash"] = str(ahash_val)
                    result["perceptual_hashes"]["ahash_hex"] = ahash_val.tohex()
            except Exception as e:
                result["perceptual_hashes"]["ahash"] = None
            
            # wHash (Wavelet Hash)
            try:
                whash_val = whash(img) if whash else None
                if whash_val:
                    result["perceptual_hashes"]["whash"] = str(whash_val)
                    result["perceptual_hashes"]["whash_hex"] = whash_val.tohex()
            except Exception as e:
                result["perceptual_hashes"]["whash"] = None
            
            # Block Hash (for rotation invariance)
            try:
                blockhash_val = blockhash(img, blocks=16) if blockhash else None
                if blockhash_val:
                    result["perceptual_hashes"]["blockhash"] = str(blockhash_val)
                    result["perceptual_hashes"]["blockhash_hex"] = blockhash_val.tohex()
            except Exception as e:
                result["perceptual_hashes"]["blockhash"] = None
            
            # Calculate hash bit counts
            for hash_name in ["phash", "dhash", "ahash", "whash", "blockhash"]:
                hash_val = result["perceptual_hashes"].get(hash_name)
                if hash_val:
                    result["perceptual_hashes"][f"{hash_name}_bits"] = len(hash_val) * 4
            
            result["fields_extracted"] = len(result["perceptual_hashes"])
            
            return result
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract perceptual hashes: {str(e)}")


def calculate_similarity(hash1: str, hash2: str, algorithm: str = "phash") -> float:
    """
    Calculate similarity between two perceptual hashes.
    
    Args:
        hash1: First hash (hex string)
        hash2: Second hash (hex string)
        algorithm: Hash algorithm used
    
    Returns:
        Similarity score (0.0 to 1.0, where 1.0 = identical)
    """
    if not IMAGEHASH_AVAILABLE:
        raise ImportError("imagehash is required for similarity calculation")
    
    try:
        h1 = hex_to_hash(hash1)
        h2 = hex_to_hash(hash2)
        
        if h1 is None or h2 is None:
            return 0.0
        
        similarity = 1 - (h1 - h2) / len(h1.hash)
        return max(0.0, min(1.0, similarity))
        
    except Exception as e:
        return 0.0


def hex_to_hash(hex_str: str):
    """Convert hex string to imagehash object."""
    if not IMAGEHASH_AVAILABLE:
        return None
    
    try:
        from imagehash import ImageHash
        return ImageHash(hash=bytes.fromhex(hex_str))
    except Exception as e:
        return None


def compare_images(hash1: Dict[str, Any], hash2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two image hash dictionaries and return similarity scores.
    
    Args:
        hash1: First image's perceptual_hashes dict
        hash2: Second image's perceptual_hashes dict
    
    Returns:
        Dictionary with per-algorithm similarity scores and overall assessment
    """
    if not IMAGEHASH_AVAILABLE:
        raise ImportError("imagehash is required for image comparison")
    
    result = {
        "algorithm_comparisons": {},
        "average_similarity": 0.0,
        "is_duplicate": False,
        "is_similar": False,
        "recommendation": ""
    }
    
    algorithms = ["phash", "dhash", "ahash", "whash"]
    similarities = []
    
    for algo in algorithms:
        h1 = hash1.get(algo)
        h2 = hash2.get(algo)
        
        if h1 and h2:
            try:
                from imagehash import ImageHash
                img_hash1 = ImageHash(hash=bytes.fromhex(h1.replace("'", "")))
                img_hash2 = ImageHash(hash=bytes.fromhex(h2.replace("'", "")))
                
                similarity = 1 - (img_hash1 - img_hash2) / len(img_hash1.hash)
                result["algorithm_comparisons"][algo] = round(similarity, 4)
                similarities.append(similarity)
            except Exception as e:
                result["algorithm_comparisons"][algo] = None
    
    if similarities:
        result["average_similarity"] = round(sum(similarities) / len(similarities), 4)
        
        if result["average_similarity"] >= 0.90:
            result["is_duplicate"] = True
            result["is_similar"] = True
            result["recommendation"] = "DUPLICATE: Images are virtually identical"
        elif result["average_similarity"] >= 0.75:
            result["is_similar"] = True
            result["recommendation"] = "SIMILAR: Images are visually similar (possible resize/crop)"
        elif result["average_similarity"] >= 0.50:
            result["recommendation"] = "PARTIALLY_SIMILAR: May share some visual characteristics"
        else:
            result["recommendation"] = "DIFFERENT: Images are visually distinct"
    
    return result


def find_duplicates(hash_dicts: List[Dict[str, Any]], threshold: float = 0.90) -> List[List[int]]:
    """
    Find duplicate groups in a list of image hashes.
    
    Args:
        hash_dicts: List of perceptual_hashes dictionaries
        threshold: Similarity threshold for duplicate detection
    
    Returns:
        List of groups, where each group contains indices of duplicate images
    """
    if not IMAGEHASH_AVAILABLE:
        raise ImportError("imagehash is required for duplicate detection")
    
    n = len(hash_dicts)
    visited = [False] * n
    groups = []
    
    for i in range(n):
        if visited[i]:
            continue
        
        group = [i]
        visited[i] = True
        
        for j in range(i + 1, n):
            if visited[j]:
                continue
            
            if i < len(hash_dicts) and j < len(hash_dicts):
                comparison = compare_images(hash_dicts[i], hash_dicts[j])
                if comparison.get("average_similarity", 0) >= threshold:
                    group.append(j)
                    visited[j] = True
        
        if len(group) > 1:
            groups.append(group)
    
    return groups


def get_perceptual_hash_field_count() -> int:
    """Return approximate number of perceptual hash fields."""
    return 12


def generate_thumbnail(filepath: str, size: tuple = (128, 128)) -> Optional[bytes]:
    """
    Generate a thumbnail from an image.
    
    Args:
        filepath: Path to image file
        size: Target thumbnail size (width, height)
    
    Returns:
        Thumbnail image bytes (JPEG), or None on failure
    """
    if not IMAGEHASH_AVAILABLE or Image is None:
        raise ImportError("Pillow is required for thumbnail generation")
    
    try:
        with Image.open(filepath) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            return buffer.getvalue()
            
    except Exception as e:
        return None


def extract_image_fingerprint(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract a comprehensive image fingerprint for deduplication.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with fingerprint data including all hashes and basic info
    """
    if not IMAGEHASH_AVAILABLE or Image is None:
        raise ImportError("imagehash and Pillow are required for fingerprinting")
    
    result = extract_perceptual_hashes(filepath)
    
    try:
        with Image.open(filepath) as img:
            result["dimensions"] = {
                "width": img.width,
                "height": img.height,
                "aspect_ratio": round(img.width / img.height, 4) if img.height > 0 else 0,
                "megapixels": round(img.width * img.height / 1000000, 2)
            }
            result["mode"] = img.mode
            
            # Generate thumbnail
            thumbnail = generate_thumbnail(filepath, (256, 256))
            if thumbnail:
                result["thumbnail_b64"] = base64.b64encode(thumbnail).decode('ascii')
                result["thumbnail_size"] = len(thumbnail)
            
    except Exception as e:
        logger.debug(f"Failed to calculate image perceptual hash: {e}")
    
    return result
