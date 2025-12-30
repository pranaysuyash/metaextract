"""
Color Analysis: Palette and Histograms
Extract dominant colors, histograms, and color temperature
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def extract_color_palette(image_path: str, n_colors: int = 5) -> Optional[Dict[str, Any]]:
    """
    Extract dominant colors using k-means clustering.
    
    Args:
        image_path: Path to image file
        n_colors: Number of dominant colors to extract
    
    Returns:
        Dictionary with color palette information
    """
    if not PIL_AVAILABLE:
        return {"error": "Pillow not installed"}
    
    if not SKLEARN_AVAILABLE:
        return {"error": "scikit-learn not installed"}
    
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for performance (150x150 is enough for color analysis)
        img_small = img.resize((150, 150), Image.Resampling.LANCZOS)
        pixels = list(img_small.getdata())
        
        # Convert to numpy array
        if NUMPY_AVAILABLE:
            pixels_array = np.array(pixels, dtype=np.float32)
        else:
            pixels_array = [[p[0], p[1], p[2]] for p in pixels]
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels_array)
        
        colors = kmeans.cluster_centers_.astype(int)
        
        # Calculate percentages
        labels = kmeans.labels_
        counts = [0] * n_colors
        for label in labels:
            counts[label] += 1
        
        total_pixels = len(labels)
        percentages = [round((c / total_pixels) * 100, 2) for c in counts]
        
        # Build result
        dominant_colors = []
        for i, (color, percent) in enumerate(zip(colors, percentages)):
            r, g, b = color
            dominant_colors.append({
                "hex": f"#{r:02x}{g:02x}{b:02x}",
                "rgb": [int(r), int(g), int(b)],
                "percentage": percent
            })
        
        # Sort by percentage (most dominant first)
        dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
        
        return {
            "dominant_colors": dominant_colors,
            "color_count": n_colors,
            "extraction_method": "k-means",
            "image_size": {"width": img_small.width, "height": img_small.height}
        }
        
    except Exception as e:
        return {"error": f"Failed to extract color palette: {str(e)}"}


def extract_color_histograms(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract RGB and luminance histograms.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Dictionary with histogram data
    """
    if not PIL_AVAILABLE:
        return {"error": "Pillow not installed"}
    
    if not CV2_AVAILABLE:
        return {"error": "OpenCV not installed"}
    
    try:
        img = cv2.imread(image_path)
        
        if img is None:
            return {"error": f"Could not read image: {image_path}"}
        
        # Split channels
        b, g, r = cv2.split(img)
        
        # Calculate histograms (256 bins)
        hist_r = cv2.calcHist([r], [0], None, [256], [0, 256]).flatten()
        hist_g = cv2.calcHist([g], [0], None, [256], [0, 256]).flatten()
        hist_b = cv2.calcHist([b], [0], None, [256], [0, 256]).flatten()
        
        # Luminance histogram
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist_lum = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        
        # Clipping detection
        total_pixels = img.shape[0] * img.shape[1]
        
        # Last 10 bins (highlights)
        r_clipped = float(hist_r[-10:].sum() / total_pixels * 100)
        g_clipped = float(hist_g[-10:].sum() / total_pixels * 100)
        b_clipped = float(hist_b[-10:].sum() / total_pixels * 100)
        
        # First 10 bins (shadows)
        r_shadows = float(hist_r[:10].sum() / total_pixels * 100)
        g_shadows = float(hist_g[:10].sum() / total_pixels * 100)
        b_shadows = float(hist_b[:10].sum() / total_pixels * 100)
        
        # Tone distribution
        shadows = float(hist_lum[:64].sum() / total_pixels * 100)
        midtones = float(hist_lum[64:192].sum() / total_pixels * 100)
        highlights = float(hist_lum[192:].sum() / total_pixels * 100)
        
        return {
            "histogram_rgb": {
                "red": hist_r.tolist(),
                "green": hist_g.tolist(),
                "blue": hist_b.tolist()
            },
            "histogram_luminance": hist_lum.tolist(),
            "clipping": {
                "red_highlights_pct": r_clipped,
                "green_highlights_pct": g_clipped,
                "blue_highlights_pct": b_clipped,
                "red_shadows_pct": r_shadows,
                "green_shadows_pct": g_shadows,
                "blue_shadows_pct": b_shadows
            },
            "tone_distribution": {
                "shadows_pct": shadows,
                "midtones_pct": midtones,
                "highlights_pct": highlights
            },
            "image_dimensions": {"width": img.shape[1], "height": img.shape[0]}
        }
        
    except Exception as e:
        return {"error": f"Failed to extract histograms: {str(e)}"}


def calculate_color_temperature(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Estimate color temperature (warm/cool) from image.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Dictionary with color temperature assessment
    """
    if not PIL_AVAILABLE:
        return {"error": "Pillow not installed"}
    
    try:
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = list(img.getdata())
        
        # Calculate average color
        r_sum = sum(p[0] for p in pixels)
        g_sum = sum(p[1] for p in pixels)
        b_sum = sum(p[2] for p in pixels)
        
        total = len(pixels)
        avg_r = r_sum / total
        avg_g = g_sum / total
        avg_b = b_sum / total
        
        # Color balance (R - B)
        color_balance = avg_r - avg_b
        
        # Saturation estimate
        rgb_max = max(avg_r, avg_g, avg_b)
        rgb_min = min(avg_r, avg_g, avg_b)
        saturation = ((rgb_max - rgb_min) / 255) * 100 if rgb_max > 0 else 0
        
        # Temperature classification
        if color_balance > 20:
            temperature = "warm"
        elif color_balance < -20:
            temperature = "cool"
        else:
            temperature = "neutral"
        
        return {
            "average_rgb": [round(avg_r, 1), round(avg_g, 1), round(avg_b, 1)],
            "temperature": temperature,
            "color_balance": round(color_balance, 1),
            "saturation_pct": round(saturation, 1)
        }
        
    except Exception as e:
        return {"error": f"Failed to calculate color temperature: {str(e)}"}


def get_color_field_count() -> int:
    """Return approximate number of color analysis fields."""
    return 25
