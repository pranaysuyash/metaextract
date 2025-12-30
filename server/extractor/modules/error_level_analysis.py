"""
Error Level Analysis (ELA) Module
Detect image manipulation, cloning, and re-compression artifacts
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import numpy as np
import cv2


def analyze_ela(filepath: str, quality: int = 90, scale: float = 1.0) -> Dict[str, Any]:
    """
    Perform Error Level Analysis on an image to detect manipulation.
    
    Args:
        filepath: Path to the image file
        quality: JPEG quality level for re-compression (default: 90)
        scale: Scale factor for analysis (1.0 = original size)
    
    Returns:
        Dictionary containing ELA analysis results
    """
    result = {
        "ela_image": None,
        "error_map": None,
        "statistics": {},
        "manipulation_regions": [],
        "confidence": 0.0,
        "is_manipulated": False,
        "fields_extracted": 0
    }

    try:
        original = cv2.imread(filepath)
        if original is None:
            result["error"] = "Could not load image"
            return result

        original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        
        height, width = original.shape[:2]
        if scale != 1.0:
            new_h, new_w = int(height * scale), int(width * scale)
            original = cv2.resize(original, (new_w, new_h))

        temp_path = "/tmp/ela_temp.jpg"
        cv2.imwrite(temp_path, cv2.cvtColor(original, cv2.COLOR_RGB2BGR), 
                    [cv2.IMWRITE_JPEG_QUALITY, quality])

        recompressed = cv2.imread(temp_path)
        recompressed = cv2.cvtColor(recompressed, cv2.COLOR_BGR2RGB)

        if scale != 1.0:
            recompressed = cv2.resize(recompressed, (original.shape[1], original.shape[0]))

        error_map = np.abs(original.astype(np.float32) - recompressed.astype(np.float32))
        error_map = np.mean(error_map, axis=2)

        mean_error = np.mean(error_map)
        std_error = np.std(error_map)
        max_error = np.max(error_map)
        median_error = np.median(error_map)

        threshold_high = mean_error + 2 * std_error
        high_error_mask = error_map > threshold_high

        kernel = np.ones((5, 5), np.uint8)
        high_error_mask = cv2.morphologyEx(high_error_mask.astype(np.uint8), 
                                           cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(high_error_mask, cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)

        manipulation_regions = []
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                x, y, w, h = cv2.boundingRect(contour)
                region_error = error_map[y:y+h, x:x+w]
                manipulation_regions.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "mean_error": float(np.mean(region_error)),
                    "max_error": float(np.max(region_error)),
                    "area_pixels": int(w * h)
                })

        manipulation_regions.sort(key=lambda x: x["mean_error"], reverse=True)

        ela_normalized = (error_map / (max_error + 1e-10) * 255).astype(np.uint8)
        ela_colored = cv2.applyColorMap(ela_normalized, cv2.COLORMAP_JET)
        ela_colored = cv2.cvtColor(ela_colored, cv2.COLOR_BGR2RGB)

        result["ela_image"] = ela_colored.tolist()
        result["error_map"] = error_map.tolist()
        result["statistics"] = {
            "mean_error": float(mean_error),
            "std_error": float(std_error),
            "max_error": float(max_error),
            "median_error": float(median_error),
            "threshold_high": float(threshold_high),
            "total_pixels": int(height * width),
            "high_error_pixels": int(np.sum(high_error_mask)),
            "high_error_percentage": float(100 * np.sum(high_error_mask) / (height * width))
        }
        result["manipulation_regions"] = manipulation_regions
        result["fields_extracted"] = 15 + len(manipulation_regions) * 6

        if manipulation_regions:
            top_region_error = manipulation_regions[0]["mean_error"] if manipulation_regions else 0
            if top_region_error > threshold_high * 1.5:
                result["confidence"] = min(1.0, top_region_error / 50)
                result["is_manipulated"] = result["confidence"] > 0.3
            elif len(manipulation_regions) > 3:
                result["confidence"] = 0.4
                result["is_manipulated"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def detect_clone_regions(filepath: str, block_size: int = 16) -> Dict[str, Any]:
    """
    Detect cloned/duplicated regions that may indicate copy-move forgery.
    
    Args:
        filepath: Path to the image file
        block_size: Size of blocks for matching (default: 16)
    
    Returns:
        Dictionary with clone detection results
    """
    result = {
        "clone_regions": [],
        "similarity_map": None,
        "is_cloned": False,
        "confidence": 0.0,
        "fields_extracted": 0
    }

    try:
        image = cv2.imread(filepath)
        if image is None:
            result["error"] = "Could not load image"
            return result

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        blocks = []
        for y in range(0, height - block_size, block_size):
            for x in range(0, width - block_size, block_size):
                block = gray[y:y+block_size, x:x+block_size]
                blocks.append((x, y, block))

        if len(blocks) < 2:
            result["error"] = "Image too small for clone detection"
            return result

        clone_pairs = []
        similarity_threshold = 0.95

        for i in range(len(blocks)):
            x1, y1, block1 = blocks[i]
            for j in range(i + 1, len(blocks)):
                x2, y2, block2 = blocks[j]

                distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                if distance < block_size * 3:
                    continue

                similarity = 1 - np.mean(np.abs(block1.astype(np.float32) - 
                                                 block2.astype(np.float32)) / 255)

                if similarity > similarity_threshold:
                    clone_pairs.append({
                        "block1": {"x": x1, "y": y1},
                        "block2": {"x": x2, "y": y2},
                        "similarity": float(similarity),
                        "distance": float(distance)
                    })

        clone_pairs.sort(key=lambda x: x["similarity"], reverse=True)

        unique_regions = []
        used_blocks = set()
        for pair in clone_pairs:
            key1 = (pair["block1"]["x"], pair["block1"]["y"])
            key2 = (pair["block2"]["x"], pair["block2"]["y"])

            if key1 in used_blocks or key2 in used_blocks:
                continue

            if len(unique_regions) >= 10:
                break

            unique_regions.append({
                "region1": pair["block1"],
                "region2": pair["block2"],
                "similarity": pair["similarity"],
                "offset": {
                    "x": pair["block2"]["x"] - pair["block1"]["x"],
                    "y": pair["block2"]["y"] - pair["block1"]["y"]
                }
            })
            used_blocks.add(key1)
            used_blocks.add(key2)

        result["clone_regions"] = unique_regions
        result["is_cloned"] = len(unique_regions) > 0
        result["confidence"] = min(1.0, len(unique_regions) / 5)
        result["fields_extracted"] = 5 + len(unique_regions) * 4

    except Exception as e:
        result["error"] = str(e)

    return result


def detect_double_compression(filepath: str) -> Dict[str, Any]:
    """
    Detect signs of double JPEG compression.
    
    Args:
        filepath: Path to the image file
    
    Returns:
        Dictionary with double compression analysis
    """
    result = {
        "is_double_compressed": False,
        "confidence": 0.0,
        "fft_analysis": None,
        "histogram_features": {},
        "fields_extracted": 0
    }

    try:
        image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if image is None:
            result["error"] = "Could not load image"
            return result

        h, w = image.shape
        if h < 64 or w < 64:
            result["error"] = "Image too small for analysis"
            return result

        fft = np.fft.fft2(image.astype(np.float32))
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.log(np.abs(fft_shift) + 1)

        center_h, center_w = h // 2, w // 2
        roi_size = 32
        roi = magnitude[center_h-roi_size:center_h+roi_size, 
                        center_w-roi_size:center_w+roi_size]

        result["fft_analysis"] = {
            "magnitude_mean": float(np.mean(magnitude)),
            "magnitude_std": float(np.std(magnitude)),
            "roi_mean": float(np.mean(roi)),
            "center_energy": float(np.max(magnitude[center_h-4:center_h+4, center_w-4:center_w+4]))
        }

        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()

        nonzero_bins = np.sum(hist > 0.001)
        entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10))

        result["histogram_features"] = {
            "nonzero_bins": int(nonzero_bins),
            "entropy": float(entropy),
            "histogram_std": float(np.std(hist))
        }

        result["fields_extracted"] = 8

    except Exception as e:
        result["error"] = str(e)

    return result


def get_ela_field_count() -> int:
    """Return the number of fields extracted by ELA analysis."""
    return 15


def full_manipulation_analysis(filepath: str) -> Dict[str, Any]:
    """
    Comprehensive manipulation detection combining ELA, clone detection,
    and double compression analysis.
    
    Args:
        filepath: Path to the image file
    
    Returns:
        Complete manipulation analysis results
    """
    result = {
        "ela_analysis": {},
        "clone_detection": {},
        "double_compression": {},
        "overall_assessment": {},
        "fields_extracted": 0
    }

    result["ela_analysis"] = analyze_ela(filepath)
    result["clone_detection"] = detect_clone_regions(filepath)
    result["double_compression"] = detect_double_compression(filepath)

    ela_manipulated = result["ela_analysis"].get("is_manipulated", False)
    clone_detected = result["clone_detection"].get("is_cloned", False)
    double_compressed = result["double_compression"].get("is_double_compressed", False)

    confidence_scores = []
    if ela_manipulated:
        confidence_scores.append(result["ela_analysis"].get("confidence", 0.5))
    if clone_detected:
        confidence_scores.append(result["clone_detection"].get("confidence", 0.5))
    if double_compressed:
        confidence_scores.append(0.6)

    overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0

    manipulation_indicators = sum([ela_manipulated, clone_detected, double_compressed])

    if manipulation_indicators >= 2:
        assessment = "LIKELY_MANIPULATED"
        overall_confidence = min(1.0, overall_confidence + 0.2)
    elif manipulation_indicators == 1:
        assessment = "POSSIBLE_MANIPULATION"
    else:
        assessment = "NO_MANIPULATION_DETECTED"

    result["overall_assessment"] = {
        "assessment": assessment,
        "confidence": float(overall_confidence),
        "manipulation_indicators": {
            "ela_manipulation": ela_manipulated,
            "clone_detected": clone_detected,
            "double_compression": double_compressed
        },
        "recommendation": get_recommendation(assessment)
    }

    total_fields = (
        result["ela_analysis"].get("fields_extracted", 0) +
        result["clone_detection"].get("fields_extracted", 0) +
        result["double_compression"].get("fields_extracted", 0) +
        5
    )
    result["fields_extracted"] = total_fields

    return result


def get_recommendation(assessment: str) -> str:
    """Get recommendation based on manipulation assessment."""
    recommendations = {
        "LIKELY_MANIPULATED": "This image shows strong indicators of manipulation. Consider reviewing the image carefully and checking source provenance.",
        "POSSIBLE_MANIPULATION": "This image shows some indicators that may warrant further investigation.",
        "NO_MANIPULATION_DETECTED": "No clear manipulation indicators were found in this image."
    }
    return recommendations.get(assessment, "Unable to assess image integrity.")
