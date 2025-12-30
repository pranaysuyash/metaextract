"""
Image Quality Assessment Metrics
BRISQUE, NIQE, PIQE, and aesthetic scoring
"""

from typing import Dict, Any, Optional
import numpy as np


try:
    import cv2
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def extract_quality_metrics(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract comprehensive image quality metrics.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with quality assessment metrics
    """
    if not CV2_AVAILABLE:
        return {"error": "opencv-python and Pillow are required for quality metrics"}
    
    result = {
        "brisque_score": None,
        "niqe_score": None,
        "piqe_score": None,
        "sharpness": None,
        "noise_metrics": {},
        "artifact_metrics": {},
        "composition_metrics": {},
        "overall_quality_score": None,
        "quality_grade": None,
        "fields_extracted": 0
    }
    
    try:
        img = cv2.imread(filepath)
        if img is None:
            return {"error": "Failed to load image for quality analysis"}
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = img_gray.shape
        
        result["sharpness"] = calculate_sharpness(img_gray)
        
        result["noise_metrics"] = calculate_noise_metrics(img_gray)
        
        result["artifact_metrics"] = calculate_artifact_metrics(img)
        
        result["composition_metrics"] = calculate_composition_metrics(img)
        
        result["brisque_score"] = estimate_brisque_score(img_gray)
        
        result["niqe_score"] = estimate_niqe_score(img_gray)
        
        result["piqe_score"] = estimate_piqe_score(img_gray)
        
        if result["brisque_score"] is not None:
            result["overall_quality_score"] = round(
                max(0, min(100, 100 - result["brisque_score"])), 2
            )
            
            if result["overall_quality_score"] >= 80:
                result["quality_grade"] = "Excellent"
            elif result["overall_quality_score"] >= 60:
                result["quality_grade"] = "Good"
            elif result["overall_quality_score"] >= 40:
                result["quality_grade"] = "Fair"
            elif result["overall_quality_score"] >= 20:
                result["quality_grade"] = "Poor"
            else:
                result["quality_grade"] = "Very Poor"
        
        total_fields = 1 + 1 + 1 + 1 + len(result["noise_metrics"]) + len(result["artifact_metrics"]) + len(result["composition_metrics"]) + 2
        result["fields_extracted"] = total_fields
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract quality metrics: {str(e)}"}


def calculate_sharpness(img_gray: np.ndarray) -> Optional[float]:
    """Calculate sharpness using Laplacian variance."""
    try:
        laplacian = cv2.Laplacian(img_gray, cv2.CV_64F)
        sharpness = laplacian.var()
        return round(sharpness, 4)
    except Exception as e:
        return None


def calculate_noise_metrics(img_gray: np.ndarray) -> Dict[str, float]:
    """Calculate noise-related metrics."""
    try:
        noise_metrics = {}
        
        noise_metrics["noise_variance"] = float(np.var(img_gray))
        
        denoised = cv2.GaussianBlur(img_gray, (5, 5), 0)
        noise_diff = img_gray.astype(float) - denoised.astype(float)
        noise_metrics["estimated_noise_std"] = float(np.std(noise_diff))
        
        noise_metrics["snr_estimate"] = float(np.mean(img_gray) / (np.std(noise_diff) + 1e-10))
        
        noise_metrics["brightness"] = float(np.mean(img_gray))
        noise_metrics["contrast"] = float(np.std(img_gray))
        
        return {k: round(v, 4) for k, v in noise_metrics.items()}
    except Exception as e:
        return {}


def calculate_artifact_metrics(img: np.ndarray) -> Dict[str, float]:
    """Calculate compression and processing artifact metrics."""
    try:
        artifact_metrics = {}
        
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        y_channel = yuv[:, :, 0]
        
        diff_y = np.diff(y_channel.astype(float), axis=1)
        artifact_metrics["horizontal_edge_variance"] = float(np.var(diff_y))
        
        diff_y = np.diff(y_channel.astype(float), axis=0)
        artifact_metrics["vertical_edge_variance"] = float(np.var(diff_y))
        
        block_size = 8
        blocks = []
        for i in range(0, y_channel.shape[0], block_size):
            for j in range(0, y_channel.shape[1], block_size):
                block = y_channel[i:i+block_size, j:j+block_size]
                if block.shape[0] == block_size and block.shape[1] == block_size:
                    dct = cv2.dct(block.astype(float))
                    blocks.append(np.mean(np.abs(dct[1:, 1:])))
        
        if blocks:
            artifact_metrics["blocking_score"] = float(np.mean(blocks))
        else:
            artifact_metrics["blocking_score"] = 0.0
        
        return {k: round(v, 4) for k, v in artifact_metrics.items()}
    except Exception as e:
        return {}


def calculate_composition_metrics(img: np.ndarray) -> Dict[str, float]:
    """Calculate basic composition metrics."""
    try:
        composition_metrics = {}
        
        height, width = img.shape[:2]
        aspect_ratio = width / height if height > 0 else 1.0
        composition_metrics["aspect_ratio"] = round(aspect_ratio, 4)
        
        if aspect_ratio >= 1.7:
            composition_metrics["aspect_category"] = "ultra_wide"
        elif aspect_ratio >= 1.3:
            composition_metrics["aspect_category"] = "wide"
        elif aspect_ratio >= 0.9:
            composition_metrics["aspect_category"] = "standard"
        else:
            composition_metrics["aspect_category"] = "portrait"
        
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        y_channel = yuv[:, :, 0]
        composition_metrics["brightness_variance"] = round(float(np.var(y_channel)), 4)
        
        center_region = y_channel[height//4:3*height//4, width//4:3*width//4]
        edge_region_top = y_channel[:height//4, :]
        edge_region_bottom = y_channel[3*height//4:, :]
        edge_region_left = y_channel[height//4:3*height//4, :width//4]
        edge_region_right = y_channel[height//4:3*height//4, 3*width//4:]
        
        center_brightness = np.mean(center_region)
        edge_brightness = (np.mean(edge_region_top) + np.mean(edge_region_bottom) + 
                          np.mean(edge_region_left) + np.mean(edge_region_right)) / 4
        
        composition_metrics["center_edge_contrast"] = round(
            abs(center_brightness - edge_brightness) / 255.0, 4
        )
        
        composition_metrics["rule_of_thirds_score"] = round(
            calculate_rule_of_thirds_score(img), 4
        )
        
        return composition_metrics
    except Exception as e:
        return {}


def calculate_rule_of_thirds_score(img: np.ndarray) -> float:
    """Calculate a simple rule of thirds score based on saliency."""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        saliency = cv2.saliency.StaticSaliencySpectralRes_create()
        success, saliency_map = saliency.computeSaliency(gray)
        
        if not success or saliency_map is None:
            return 0.5
        
        saliency_map = saliency_map.astype(float)
        
        height, width = saliency_map.shape
        third_h, third_w = height // 3, width // 3
        
        power_points = [
            (third_h, third_w),
            (third_h, 2 * third_w),
            (2 * third_h, third_w),
            (2 * third_h, 2 * third_w),
        ]
        
        total_saliency = np.sum(saliency_map)
        if total_saliency == 0:
            return 0.5
        
        point_saliency = sum(saliency_map[hp, wp] for hp, wp in power_points)
        score = point_saliency / total_saliency
        
        return min(1.0, score * 2)
    except Exception as e:
        return 0.5


def estimate_brisque_score(img_gray: np.ndarray) -> Optional[float]:
    """
    Estimate BRISQUE (Blind/Referenceless Image Spatial Quality Evaluator) score.
    Lower is better. Range: 0-100.
    """
    try:
        img_float = img_gray.astype(float) / 255.0
        img_float = cv2.resize(img_float, (256, 256))
        
        mu = cv2.GaussianBlur(img_float, (7, 7), 1.5)
        mu_sq = mu * mu
        sigma = np.sqrt(np.abs(cv2.GaussianBlur(img_float * img_float, (7, 7), 1.5) - mu_sq))
        
        sigma = np.maximum(sigma, 1.0 / 255.0)
        
        struct = (img_float - mu) / sigma
        
        alpha = 2.0
        gamma = np.power(np.abs(struct) + 1e-10, alpha)
        gamma = np.mean(gamma)
        
        brisque = gamma * 50 + 20
        brisque = max(0, min(100, brisque))
        
        return round(brisque, 2)
    except Exception as e:
        return None


def estimate_niqe_score(img_gray: np.ndarray) -> Optional[float]:
    """
    Estimate NIQE (Naturalness Image Quality Evaluator) score.
    Lower is better.
    """
    try:
        img_float = img_gray.astype(float) / 255.0
        img_float = cv2.resize(img_float, (256, 256))
        
        patch_size = 32
        patches = []
        for i in range(0, 256 - patch_size, patch_size):
            for j in range(0, 256 - patch_size, patch_size):
                patch = img_float[i:i+patch_size, j:j+patch_size]
                if patch.shape[0] == patch_size and patch.shape[1] == patch_size:
                    patches.append(patch)
        
        if not patches:
            return 3.0
        
        patch_var = np.var(np.array(patches), axis=(1, 2))
        mean_var = np.mean(patch_var)
        
        niqe = np.log10(mean_var + 1e-10) * 10 + 3
        niqe = max(0, min(10, niqe))
        
        return round(niqe, 2)
    except Exception as e:
        return None


def estimate_piqe_score(img_gray: np.ndarray) -> Optional[float]:
    """
    Estimate PIQE (Perception-based Image Quality Evaluator) score.
    Lower is better.
    """
    try:
        img_float = img_gray.astype(float) / 255.0
        img_float = cv2.resize(img_float, (256, 256))
        
        noise_map = np.zeros_like(img_float)
        for i in range(1, img_float.shape[0] - 1):
            for j in range(1, img_float.shape[1] - 1):
                local_std = np.std(img_float[i-1:i+2, j-1:j+2])
                noise_map[i, j] = local_std
        
        noise_score = np.mean(noise_map) * 100
        
        piqe = noise_score + 10
        piqe = max(0, min(100, piqe))
        
        return round(piqe, 2)
    except Exception as e:
        return None


def get_quality_field_count() -> int:
    """Return approximate number of quality metric fields."""
    return 16


def extract_aesthetic_metrics(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract aesthetic scoring metrics.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with aesthetic metrics
    """
    if not CV2_AVAILABLE:
        return {"error": "opencv-python is required for aesthetic metrics"}
    
    result = {
        "composition_score": None,
        "color_harmony_score": None,
        "subject_clarity_score": None,
        "technical_quality_score": None,
        "overall_aesthetic_score": None,
        "aesthetic_grade": None
    }
    
    try:
        img = cv2.imread(filepath)
        if img is None:
            return {"error": "Failed to load image for aesthetic analysis"}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        sharpness = calculate_sharpness(gray)
        noise_metrics = calculate_noise_metrics(gray)
        
        noise_score = noise_metrics.get("noise_variance", 50)
        technical_score = 100 - min(100, (noise_score / 50) * 50 + (100 - sharpness) / 2)
        technical_score = max(0, min(100, technical_score))
        result["technical_quality_score"] = round(technical_score, 2)
        
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        u_channel = yuv[:, :, 1]
        v_channel = yuv[:, :, 2]
        color_std = (np.std(u_channel) + np.std(v_channel)) / 2
        color_harmony = min(100, color_std * 2 + 50)
        result["color_harmony_score"] = round(color_harmony, 2)
        
        saliency = cv2.saliency.StaticSaliencySpectralRes_create()
        success, saliency_map = saliency.computeSaliency(gray)
        if success and saliency_map is not None:
            saliency_map = saliency_map.astype(float)
            center_region = saliency_map[saliency_map.shape[0]//4:3*saliency_map.shape[0]//4,
                                          saliency_map.shape[1]//4:3*saliency_map.shape[1]//4]
            subject_clarity = np.mean(center_region) * 100
            result["subject_clarity_score"] = round(min(100, subject_clarity * 2), 2)
        else:
            result["subject_clarity_score"] = 50.0
        
        aspect = img.shape[1] / img.shape[0]
        if 0.8 <= aspect <= 1.2:
            comp_score = 80
        elif 0.5 <= aspect <= 2.0:
            comp_score = 70
        else:
            comp_score = 60
        result["composition_score"] = comp_score
        
        if all(v is not None for v in [
            result["composition_score"],
            result["color_harmony_score"],
            result["subject_clarity_score"],
            result["technical_quality_score"]
        ]):
            overall = (
                result["composition_score"] * 0.2 +
                result["color_harmony_score"] * 0.2 +
                result["subject_clarity_score"] * 0.3 +
                result["technical_quality_score"] * 0.3
            )
            result["overall_aesthetic_score"] = round(overall, 2)
            
            if result["overall_aesthetic_score"] >= 80:
                result["aesthetic_grade"] = "Excellent"
            elif result["overall_aesthetic_score"] >= 60:
                result["aesthetic_grade"] = "Good"
            elif result["overall_aesthetic_score"] >= 40:
                result["aesthetic_grade"] = "Fair"
            else:
                result["aesthetic_grade"] = "Needs Improvement"
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract aesthetic metrics: {str(e)}"}
