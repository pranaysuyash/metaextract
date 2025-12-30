"""
Utility conversion functions for metadata
"""
from math import gcd
from typing import Sequence, Optional, Union

def dms_to_decimal(dms: Sequence[Union[float, int]], ref: str) -> Optional[Union[float, None]]:
    """
    Convert GPS coordinates from DMS (degrees, minutes, seconds) to decimal.
    
    Args:
        dms: Sequence of (degrees, minutes, seconds)
        ref: Reference (N/S for latitude, E/W for longitude)
    
    Returns:
        Decimal coordinate if conversion succeeds, otherwise None
    """
    try:
        if len(dms) < 3:
            return None
        
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        
        result = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        if ref in ['S', 'W']:
            result = -result
        
        return result
    except Exception as e:
        return None

def aspect_ratio_string(width: int, height: int) -> str:
    """
    Calculate aspect ratio string from dimensions.
    
    Args:
        width: Image width
        height: Image height
    
    Returns:
        Aspect ratio string (e.g., "16:9")
    """
    if height == 0:
        return "0:0"
    
    try:
        divisor = gcd(int(width), int(height)) or 1
        return f"{int(width) // divisor}:{int(height) // divisor}"
    except Exception as e:
        return f"{width}:{height}"

def human_readable_size(bytes_value: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        bytes_value: Size in bytes
    
    Returns:
        Human-readable string (e.g., "3.2 MB")
    """
    value = float(bytes_value)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(value) < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"
