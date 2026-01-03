#!/usr/bin/env python3
"""
Manipulation Detection Module for MetaExtract

This module provides forensic manipulation detection capabilities.
"""

import os
import sys
import json
import logging
import numpy as np
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger("metaextract.manipulation")

# Library availability checks
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class ForensicManipulation:
    """Forensic manipulation detection class"""
    
    def __init__(self):
        self.initialized = OPENCV_AVAILABLE and SKLEARN_AVAILABLE
        
    def detect_manipulation(self, filepath: str, metadata: Dict = None) -> Dict[str, Any]:
        """Detect manipulation in images"""
        result = {
            "available": self.initialized,
            "manipulation_probability": 0.0,
            "detection_methods": {},
            "suspicious_regions": [],
            "metadata_inconsistencies": []
        }
        
        if not self.initialized:
            result["error"] = "Required libraries not available"
            return result
        
        try:
            # Load image
            img = cv2.imread(filepath)
            if img is None:
                result["error"] = "Could not load image"
                return result
            
            # Perform manipulation detection
            result["detection_methods"]["error_level_analysis"] = self._error_level_analysis(filepath)
            result["detection_methods"]["copy_move_detection"] = self._copy_move_detection(img)
            result["detection_methods"]["noise_analysis"] = self._noise_analysis(img)
            
            # Check metadata consistency
            if metadata:
                result["metadata_inconsistencies"] = self._check_metadata_consistency(metadata, img)
            
            # Calculate overall manipulation probability
            manipulation_indicators = 0
            total_methods = 0
            
            for method, analysis in result["detection_methods"].items():
                if isinstance(analysis, dict) and "manipulation_likelihood" in analysis:
                    manipulation_indicators += analysis["manipulation_likelihood"]
                    total_methods += 1
            
            if total_methods > 0:
                result["manipulation_probability"] = manipulation_indicators / total_methods
            
            return result
            
        except Exception as e:
            logger.error(f"Error in manipulation detection: {e}")
            result["error"] = str(e)
            return result
    
    def _error_level_analysis(self, filepath: str) -> Dict[str, Any]:
        """Error Level Analysis for detecting manipulated regions"""
        try:
            # Load original image
            original = cv2.imread(filepath)
            
            # Save as JPEG with quality 90 and reload
            temp_path = filepath + "_temp_ela.jpg"
            cv2.imwrite(temp_path, original, [cv2.IMWRITE_JPEG_QUALITY, 90])
            recompressed = cv2.imread(temp_path)
            os.remove(temp_path)
            
            # Calculate difference
            diff = cv2.absdiff(original, recompressed)
            
            # Enhance the difference
            enhanced = cv2.convertScaleAbs(diff, alpha=15, beta=0)
            
            # Analyze the error level distribution
            gray_diff = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
            
            # Calculate statistics
            mean_error = np.mean(gray_diff)
            std_error = np.std(gray_diff)
            max_error = np.max(gray_diff)
            
            # Find regions with high error levels
            threshold = mean_error + 2 * std_error
            high_error_mask = gray_diff > threshold
            high_error_percentage = np.sum(high_error_mask) / gray_diff.size
            
            manipulation_likelihood = 0.0
            if high_error_percentage > 0.05:  # More than 5% high error
                manipulation_likelihood += 0.4
            if std_error > 20:  # High variation in error levels
                manipulation_likelihood += 0.3
            
            return {
                "mean_error": float(mean_error),
                "std_error": float(std_error),
                "max_error": float(max_error),
                "high_error_percentage": float(high_error_percentage),
                "manipulation_likelihood": min(manipulation_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "manipulation_likelihood": 0.0}
    
    def _copy_move_detection(self, img: np.ndarray) -> Dict[str, Any]:
        """Detect copy-move forgeries using block matching"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Use SIFT features for block matching
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            if descriptors is None or len(descriptors) < 10:
                return {"manipulation_likelihood": 0.0, "matches": 0}
            
            # Match features with themselves to find duplicates
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(descriptors, descriptors, k=3)
            
            # Filter matches (exclude self-matches and very close matches)
            good_matches = []
            for match_group in matches:
                if len(match_group) >= 2:
                    m1, m2 = match_group[0], match_group[1]
                    # Exclude self-matches and very similar matches
                    if m1.distance < 0.7 * m2.distance and m1.trainIdx != m1.queryIdx:
                        # Check if keypoints are far enough apart
                        pt1 = keypoints[m1.queryIdx].pt
                        pt2 = keypoints[m1.trainIdx].pt
                        distance = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
                        if distance > 50:  # Minimum distance threshold
                            good_matches.append(m1)
            
            # Analyze match clusters
            match_count = len(good_matches)
            manipulation_likelihood = 0.0
            
            if match_count > 20:  # Many duplicate features suggest copy-move
                manipulation_likelihood += 0.5
            if match_count > 50:
                manipulation_likelihood += 0.3
            
            return {
                "total_keypoints": len(keypoints),
                "duplicate_matches": match_count,
                "manipulation_likelihood": min(manipulation_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "manipulation_likelihood": 0.0}
    
    def _noise_analysis(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze noise patterns for manipulation detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
            
            # Extract noise using wavelet-like approach
            # Apply Gaussian blur and subtract
            blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
            noise = gray - blurred
            
            # Divide image into blocks and analyze noise consistency
            h, w = noise.shape
            block_size = 64
            noise_stats = []
            
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = noise[y:y+block_size, x:x+block_size]
                    noise_stats.append({
                        'mean': np.mean(block),
                        'std': np.std(block),
                        'skewness': self._calculate_skewness(block.flatten())
                    })
            
            if not noise_stats:
                return {"manipulation_likelihood": 0.0}
            
            # Analyze consistency across blocks
            std_values = [stat['std'] for stat in noise_stats]
            skew_values = [stat['skewness'] for stat in noise_stats]
            
            std_variance = np.var(std_values)
            skew_variance = np.var(skew_values)
            
            manipulation_likelihood = 0.0
            if std_variance > 5.0:  # High variance in noise levels
                manipulation_likelihood += 0.3
            if skew_variance > 0.5:  # Inconsistent noise distribution
                manipulation_likelihood += 0.2
            
            return {
                "noise_std_variance": float(std_variance),
                "noise_skew_variance": float(skew_variance),
                "manipulation_likelihood": min(manipulation_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "manipulation_likelihood": 0.0}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data distribution"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)
    
    def _check_metadata_consistency(self, metadata: Dict, img: np.ndarray) -> List[str]:
        """Check for inconsistencies between metadata and image content"""
        inconsistencies = []
        
        try:
            # Check image dimensions
            exif_data = metadata.get("exif", {})
            image_data = metadata.get("image", {})
            
            # Compare EXIF dimensions with actual image dimensions
            exif_width = exif_data.get("ExifImageWidth") or exif_data.get("ImageWidth")
            exif_height = exif_data.get("ExifImageHeight") or exif_data.get("ImageLength")
            actual_height, actual_width = img.shape[:2]
            
            if exif_width and int(exif_width) != actual_width:
                inconsistencies.append(f"EXIF width ({exif_width}) doesn't match actual width ({actual_width})")
            
            if exif_height and int(exif_height) != actual_height:
                inconsistencies.append(f"EXIF height ({exif_height}) doesn't match actual height ({actual_height})")
            
            # Check for suspicious software/processing history
            software = exif_data.get("Software", "").lower()
            processing_software = exif_data.get("ProcessingSoftware", "").lower()
            
            manipulation_software = ["photoshop", "gimp", "paint.net", "canva", "pixlr"]
            for soft in manipulation_software:
                if soft in software or soft in processing_software:
                    inconsistencies.append(f"Image processing software detected: {soft}")
            
            # Check for multiple creation dates
            dates = []
            for date_field in ["DateTime", "DateTimeOriginal", "DateTimeDigitized", "CreateDate", "ModifyDate"]:
                date_value = exif_data.get(date_field)
                if date_value:
                    dates.append((date_field, date_value))
            
            if len(set(date[1] for date in dates)) > 2:  # More than 2 different dates
                inconsistencies.append("Multiple different creation/modification dates found")
            
            # Check for missing expected metadata
            camera_make = exif_data.get("Make")
            camera_model = exif_data.get("Model")
            
            if not camera_make and not camera_model:
                inconsistencies.append("Missing camera make/model information")
            
        except Exception as e:
            inconsistencies.append(f"Error checking metadata consistency: {e}")
        
        return inconsistencies

def analyze_manipulation(filepath: str, metadata: Dict = None) -> Dict[str, Any]:
    """Main interface function for manipulation detection"""
    detector = ForensicManipulation()
    return detector.detect_manipulation(filepath, metadata)