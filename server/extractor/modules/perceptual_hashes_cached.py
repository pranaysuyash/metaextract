"""
Cached Perceptual Hashing Module for MetaExtract

Enhanced perceptual hashing with comprehensive caching support.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import base64
import io

# Import the original module for fallback
from . import perceptual_hashes

# Import cache manager
try:
    from ...cache.cache_manager import get_cache_manager
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    get_cache_manager = None

logger = logging.getLogger("metaextract.modules.perceptual_hashes_cached")

# Import imagehash and PIL
try:
    from PIL import Image
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    Image = None
    imagehash = None
    IMAGEHASH_AVAILABLE = False


def extract_perceptual_hashes_cached(filepath: str, enable_cache: bool = True) -> Optional[Dict[str, Any]]:
    """
    Extract perceptual hashes with caching support.
    
    Args:
        filepath: Path to image file
        enable_cache: Whether to use caching
        
    Returns:
        Dictionary with perceptual hashes and cache information
    """
    if not IMAGEHASH_AVAILABLE or Image is None:
        logger.warning("imagehash and Pillow not available, falling back to original module")
        return perceptual_hashes.extract_perceptual_hashes(filepath)
    
    # Initialize cache manager if caching is enabled
    cache_manager = None
    if enable_cache and CACHING_AVAILABLE:
        cache_manager = get_cache_manager()
    
    start_time = time.time()
    
    try:
        # Check cache first
        if cache_manager:
            cached_hash = cache_manager.get_perceptual_hash(filepath, algorithm="phash")
            if cached_hash:
                # We have a cached pHash, let's build the full result
                logger.debug(f"Cache hit for perceptual hash: {filepath}")
                
                # Get other hash types from cache or calculate them
                result = {
                    "perceptual_hashes": {},
                    "hash_comparison": {},
                    "fields_extracted": 0,
                    "cache_info": {"hit": True, "source": "perceptual_cache"}
                }
                
                # Get cached hashes for all algorithms
                algorithms = ["phash", "dhash", "ahash", "whash"]
                for algorithm in algorithms:
                    cached_result = cache_manager.get_perceptual_hash(
                        filepath, algorithm=algorithm
                    )
                    if cached_result:
                        result["perceptual_hashes"][algorithm] = cached_result
                        result["perceptual_hashes"][f"{algorithm}_hex"] = cached_result
                        result["fields_extracted"] += 1
                
                # Calculate bit counts
                for hash_name in algorithms:
                    hash_val = result["perceptual_hashes"].get(hash_name)
                    if hash_val:
                        result["perceptual_hashes"][f"{hash_name}_bits"] = len(hash_val) * 4
                
                return result
        
        # Cache miss or caching disabled, calculate hashes
        logger.debug(f"Calculating perceptual hashes for: {filepath}")
        
        with Image.open(filepath) as img:
            img = img.convert('RGB')
            
            result = {
                "perceptual_hashes": {},
                "hash_comparison": {},
                "fields_extracted": 0,
                "cache_info": {"hit": False}
            }
            
            # Calculate all hash types
            hash_results = {}
            
            # pHash (Perceptual Hash) - most effective for similarity
            try:
                phash_val = imagehash.phash(img)
                hash_results["phash"] = {
                    "value": str(phash_val),
                    "hex": phash_val.tohex(),
                    "b64": base64.b64encode(phash_val.tobytes()).decode('ascii')
                }
                result["perceptual_hashes"]["phash"] = str(phash_val)
                result["perceptual_hashes"]["phash_hex"] = phash_val.tohex()
                result["perceptual_hashes"]["phash_b64"] = base64.b64encode(phash_val.tobytes()).decode('ascii')
                
                # Cache the pHash
                if cache_manager:
                    cache_manager.cache_perceptual_hash(
                        phash_val.tohex(), filepath, algorithm="phash",
                        execution_time_ms=100  # Estimated time
                    )
                
            except Exception as e:
                logger.warning(f"Failed to calculate pHash: {e}")
                result["perceptual_hashes"]["phash"] = None
            
            # dHash (Difference Hash)
            try:
                dhash_val = imagehash.dhash(img)
                hash_results["dhash"] = {
                    "value": str(dhash_val),
                    "hex": dhash_val.tohex()
                }
                result["perceptual_hashes"]["dhash"] = str(dhash_val)
                result["perceptual_hashes"]["dhash_hex"] = dhash_val.tohex()
                
                # Cache the dHash
                if cache_manager:
                    cache_manager.cache_perceptual_hash(
                        dhash_val.tohex(), filepath, algorithm="dhash",
                        execution_time_ms=80  # Estimated time
                    )
                
            except Exception as e:
                logger.warning(f"Failed to calculate dHash: {e}")
                result["perceptual_hashes"]["dhash"] = None
            
            # aHash (Average Hash)
            try:
                ahash_val = imagehash.average_hash(img)
                hash_results["ahash"] = {
                    "value": str(ahash_val),
                    "hex": ahash_val.tohex()
                }
                result["perceptual_hashes"]["ahash"] = str(ahash_val)
                result["perceptual_hashes"]["ahash_hex"] = ahash_val.tohex()
                
                # Cache the aHash
                if cache_manager:
                    cache_manager.cache_perceptual_hash(
                        ahash_val.tohex(), filepath, algorithm="ahash",
                        execution_time_ms=60  # Estimated time
                    )
                
            except Exception as e:
                logger.warning(f"Failed to calculate aHash: {e}")
                result["perceptual_hashes"]["ahash"] = None
            
            # wHash (Wavelet Hash)
            try:
                whash_val = imagehash.whash(img)
                hash_results["whash"] = {
                    "value": str(whash_val),
                    "hex": whash_val.tohex()
                }
                result["perceptual_hashes"]["whash"] = str(whash_val)
                result["perceptual_hashes"]["whash_hex"] = whash_val.tohex()
                
                # Cache the wHash
                if cache_manager:
                    cache_manager.cache_perceptual_hash(
                        whash_val.tohex(), filepath, algorithm="whash",
                        execution_time_ms=90  # Estimated time
                    )
                
            except Exception as e:
                logger.warning(f"Failed to calculate wHash: {e}")
                result["perceptual_hashes"]["whash"] = None
            
            # Calculate hash bit counts
            for hash_name in ["phash", "dhash", "ahash", "whash"]:
                hash_val = result["perceptual_hashes"].get(hash_name)
                if hash_val:
                    result["perceptual_hashes"][f"{hash_name}_bits"] = len(hash_val) * 4
            
            result["fields_extracted"] = len([h for h in result["perceptual_hashes"] 
                                            if h and not h.endswith("_bits") and not h.endswith("_hex") and not h.endswith("_b64")])
            
            processing_time = (time.time() - start_time) * 1000
            result["processing_time_ms"] = processing_time
            
            return result
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        logger.error(f"Failed to extract perceptual hashes: {e}")
        raise RuntimeError(f"Failed to extract perceptual hashes: {str(e)}")


def calculate_similarity_cached(hash1: str, hash2: str, algorithm: str = "phash") -> float:
    """
    Calculate similarity between two perceptual hashes with caching.
    
    Args:
        hash1: First hash (hex string)
        hash2: Second hash (hex string)
        algorithm: Hash algorithm used
        
    Returns:
        Similarity score (0.0 to 1.0, where 1.0 = identical)
    """
    if not IMAGEHASH_AVAILABLE:
        logger.warning("imagehash not available, falling back to original module")
        return perceptual_hashes.calculate_similarity(hash1, hash2, algorithm)
    
    # Initialize cache manager
    cache_manager = None
    if CACHING_AVAILABLE:
        cache_manager = get_cache_manager()
    
    # Check cache for comparison result
    if cache_manager:
        cached_similarity = cache_manager.perceptual_cache.get_cached_comparison(
            hash1, hash2, algorithm
        )
        if cached_similarity is not None:
            logger.debug(f"Cache hit for hash comparison: {algorithm}")
            return cached_similarity
    
    # Calculate similarity
    try:
        from . import perceptual_hashes
        similarity = perceptual_hashes.calculate_similarity(hash1, hash2, algorithm)
        
        # Cache the comparison result
        if cache_manager:
            cache_manager.perceptual_cache.cache_comparison_result(
                similarity, hash1, hash2, algorithm
            )
        
        return similarity
        
    except Exception as e:
        logger.error(f"Failed to calculate hash similarity: {e}")
        return 0.0


# Maintain compatibility with original function names
extract_perceptual_hashes = extract_perceptual_hashes_cached
calculate_similarity = calculate_similarity_cached


# Enhanced batch processing functions
def batch_extract_perceptual_hashes(file_paths: List[str], enable_cache: bool = True) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Extract perceptual hashes for multiple files with batch caching.
    
    Args:
        file_paths: List of file paths
        enable_cache: Whether to use caching
        
    Returns:
        Dictionary mapping file paths to hash results
    """
    results = {}
    
    # Initialize cache manager
    cache_manager = None
    if enable_cache and CACHING_AVAILABLE:
        cache_manager = get_cache_manager()
    
    # Check cache for all files first
    if cache_manager:
        cached_results = cache_manager.perceptual_cache.batch_get_hashes(file_paths)
        for file_path, cached_result in cached_results.items():
            if cached_result:
                results[file_path] = cached_result
    
    # Process uncached files
    uncached_files = [fp for fp in file_paths if fp not in results]
    if uncached_files:
        # Calculate hashes for uncached files
        new_results = {}
        for file_path in uncached_files:
            try:
                result = extract_perceptual_hashes_cached(file_path, enable_cache=False)
                new_results[file_path] = result
            except Exception as e:
                logger.error(f"Failed to extract hashes for {file_path}: {e}")
                new_results[file_path] = None
        
        # Cache the new results in batch
        if cache_manager:
            hash_data = {}
            for file_path, result in new_results.items():
                if result and 'perceptual_hashes' in result:
                    # Extract hash values for caching
                    hash_values = {}
                    for algo in ['phash', 'dhash', 'ahash', 'whash']:
                        hash_val = result['perceptual_hashes'].get(f'{algo}_hex')
                        if hash_val:
                            hash_values[file_path] = {
                                'hash_value': hash_val,
                                'execution_time_ms': result.get('processing_time_ms', 100)
                            }
                    
                    if hash_values:
                        cache_manager.perceptual_cache.batch_cache_hashes(hash_values)
        
        # Merge results
        results.update(new_results)
    
    return results


def batch_calculate_similarity(hash_pairs: List[Tuple[str, str]], 
                              algorithm: str = "phash",
                              enable_cache: bool = True) -> List[float]:
    """
    Calculate similarity for multiple hash pairs with caching.
    
    Args:
        hash_pairs: List of (hash1, hash2) tuples
        algorithm: Hash algorithm to use
        enable_cache: Whether to use caching
        
    Returns:
        List of similarity scores
    """
    similarities = []
    
    # Initialize cache manager
    cache_manager = None
    if enable_cache and CACHING_AVAILABLE:
        cache_manager = get_cache_manager()
    
    for hash1, hash2 in hash_pairs:
        try:
            similarity = calculate_similarity_cached(hash1, hash2, algorithm)
            similarities.append(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate similarity for hash pair: {e}")
            similarities.append(0.0)
    
    return similarities