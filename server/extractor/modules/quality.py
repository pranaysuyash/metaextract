"""
Image Quality Metrics
Sharpness, blur detection, noise level, brightness, contrast analysis
"""

from typing import Dict, Any, Optional
from pathlib import Path


try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def extract_quality_metrics(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract image quality metrics using OpenCV.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Dictionary with quality metrics
    """
    if not CV2_AVAILABLE:
        return {"error": "OpenCV not installed"}
    
    try:
        img = cv2.imread(image_path)
        
        if img is None:
            return {"error": f"Could not read image: {image_path}"}
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = laplacian_var < 100
        
        # Blur type classification
        if is_blurry:
            if laplacian_var < 50:
                blur_type = "motion_blur"
            elif laplacian_var < 100:
                blur_type = "out_of_focus"
            else:
                blur_type = "slight_blur"
        else:
            blur_type = "sharp"
        
        # Noise estimation
        mean, std_dev = cv2.meanStdDev(gray)
        noise_level = float(std_dev[0][0])
        
        # Brightness
        mean_brightness = float(mean[0])
        
        # Contrast
        contrast = float(std_dev[0][0])
        
        # Assessments
        if mean_brightness < 60:
            brightness_assessment = "dark"
        elif mean_brightness > 200:
            brightness_assessment = "bright"
        else:
            brightness_assessment = "normal"
        
        if contrast < 40:
            contrast_assessment = "low"
        elif contrast < 80:
            contrast_assessment = "normal"
        else:
            contrast_assessment = "high"
        
        if noise_level < 15:
            noise_assessment = "low"
        elif noise_level < 30:
            noise_assessment = "medium"
        else:
            noise_assessment = "high"
        
        # Dynamic range
        dynamic_range = contrast / mean_brightness * 100 if mean_brightness > 0 else 0
        
        # Histogram analysis for exposure
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()
        total_pixels = gray.shape[0] * gray.shape[1]
        
        shadows_pct = float(hist[:64].sum() / total_pixels * 100)
        highlights_pct = float(hist[192:].sum() / total_pixels * 100)
        
        if highlights_pct > 5 and shadows_pct > 5:
            exposure = "high_contrast"
        elif highlights_pct > 5:
            exposure = "overexposed"
        elif shadows_pct > 5:
            exposure = "underexposed"
        else:
            exposure = "well_exposed"
        
        return {
            "sharpness_score": round(laplacian_var, 2),
            "is_blurry": is_blurry,
            "blur_type": blur_type,
            "noise_level": round(noise_level, 2),
            "noise_assessment": noise_assessment,
            "mean_brightness": round(mean_brightness, 2),
            "brightness_assessment": brightness_assessment,
            "contrast": round(contrast, 2),
            "contrast_assessment": contrast_assessment,
            "dynamic_range": round(dynamic_range, 2),
            "exposure": exposure,
            "histogram_analysis": {
                "shadows_pct": round(shadows_pct, 2),
                "highlights_pct": round(highlights_pct, 2)
            },
            "image_dimensions": {"width": img.shape[1], "height": img.shape[0]}
        }
        
    except Exception as e:
        return {"error": f"Failed to extract quality metrics: {str(e)}"}


def estimate_image_sharpness(image_path: str) -> float:
    """Quick sharpness estimate using variance of Laplacian."""
    if not CV2_AVAILABLE:
        return 0.0
    
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    except Exception as e:
        return 0.0


def detect_blur(image_path: str, threshold: float = 100.0) -> Dict[str, Any]:
    """Detect if image is blurry using Laplacian variance."""
    sharpness = estimate_image_sharpness(image_path)
    
    return {
        "is_blurry": sharpness < threshold,
        "sharpness_score": round(sharpness, 2),
        "threshold": threshold,
        "blur_type": "blur_detected" if sharpness < threshold else "sharp"
    }


def get_quality_field_count() -> int:
    """Return approximate number of quality metric fields."""
    return 15
