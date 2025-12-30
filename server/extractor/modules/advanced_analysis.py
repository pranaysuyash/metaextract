#!/usr/bin/env python3
"""
Advanced Analysis Modules for MetaExtract v4.0

Specialized analysis modules for:
- AI Content Detection
- Manipulation Detection (Enhanced)
- Steganography Detection (Enhanced)
- Professional Video Analysis
- Social Media Context Analysis
- Mobile Sensor Analysis
"""

import os
import sys
import json
import logging
import numpy as np
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger("metaextract.advanced")

# ============================================================================
# Library Availability Checks
# ============================================================================

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# ============================================================================
# AI Content Detection Engine
# ============================================================================

class AIContentDetector:
    """Detect AI-generated content in images, audio, and text"""
    
    def __init__(self):
        self.image_detector = None
        self.text_detector = None
        self.audio_detector = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Load pre-trained models for AI detection
                self.text_detector = pipeline("text-classification", 
                                            model="roberta-base-openai-detector")
            except Exception as e:
                logger.warning(f"Could not load AI text detector: {e}")
    
    def detect_ai_image(self, filepath: str, metadata: Dict = None) -> Dict[str, Any]:
        """Detect AI-generated images using multiple techniques"""
        result = {
            "available": OPENCV_AVAILABLE,
            "ai_probability": 0.0,
            "detection_methods": {},
            "suspicious_patterns": [],
            "metadata_analysis": {}
        }
        
        if not OPENCV_AVAILABLE:
            result["error"] = "OpenCV not available"
            return result
        
        try:
            # Load image
            img = cv2.imread(filepath)
            if img is None:
                result["error"] = "Could not load image"
                return result
            
            # Method 1: Frequency domain analysis
            result["detection_methods"]["frequency_analysis"] = self._analyze_frequency_domain(img)
            
            # Method 2: Noise pattern analysis
            result["detection_methods"]["noise_analysis"] = self._analyze_noise_patterns(img)
            
            # Method 3: Compression artifact analysis
            result["detection_methods"]["compression_analysis"] = self._analyze_compression_artifacts(img)
            
            # Method 4: Metadata analysis for AI indicators
            if metadata:
                result["metadata_analysis"] = self._analyze_metadata_for_ai(metadata)
            
            # Method 5: Statistical analysis
            result["detection_methods"]["statistical_analysis"] = self._analyze_statistical_properties(img)
            
            # Combine results for overall AI probability
            ai_indicators = 0
            total_methods = 0
            
            for method, analysis in result["detection_methods"].items():
                if isinstance(analysis, dict) and "ai_likelihood" in analysis:
                    ai_indicators += analysis["ai_likelihood"]
                    total_methods += 1
            
            if total_methods > 0:
                result["ai_probability"] = ai_indicators / total_methods
            
            # Add suspicious patterns
            if result["ai_probability"] > 0.6:
                result["suspicious_patterns"].append("High frequency domain anomalies")
            if result["ai_probability"] > 0.7:
                result["suspicious_patterns"].append("Unusual noise distribution")
            if result["ai_probability"] > 0.8:
                result["suspicious_patterns"].append("Compression artifacts inconsistent with camera")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in AI image detection: {e}")
            result["error"] = str(e)
            return result
    
    def _analyze_frequency_domain(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze frequency domain for AI generation patterns"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # Analyze frequency distribution
            center = np.array(magnitude_spectrum.shape) // 2
            y, x = np.ogrid[:magnitude_spectrum.shape[0], :magnitude_spectrum.shape[1]]
            mask = (x - center[1])**2 + (y - center[0])**2 <= (min(center) * 0.1)**2
            
            center_energy = np.mean(magnitude_spectrum[mask])
            edge_energy = np.mean(magnitude_spectrum[~mask])
            
            # AI images often have unusual frequency distributions
            energy_ratio = center_energy / (edge_energy + 1e-10)
            
            # Detect periodic patterns (common in AI generation)
            autocorr = cv2.matchTemplate(magnitude_spectrum, magnitude_spectrum, cv2.TM_CCOEFF_NORMED)
            periodic_score = np.max(autocorr) - 1.0  # Subtract self-correlation
            
            ai_likelihood = 0.0
            if energy_ratio > 2.0 or energy_ratio < 0.5:
                ai_likelihood += 0.3
            if periodic_score > 0.1:
                ai_likelihood += 0.4
            
            return {
                "energy_ratio": float(energy_ratio),
                "periodic_score": float(periodic_score),
                "ai_likelihood": min(ai_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "ai_likelihood": 0.0}
    
    def _analyze_noise_patterns(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze noise patterns for AI generation indicators"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
            
            # Apply Gaussian blur and subtract to get noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
            noise = gray - blurred
            
            # Analyze noise statistics
            noise_std = np.std(noise)
            noise_mean = np.mean(np.abs(noise))
            
            # Calculate noise distribution uniformity
            hist, _ = np.histogram(noise.flatten(), bins=50, range=(-50, 50))
            hist_normalized = hist / np.sum(hist)
            entropy = -np.sum(hist_normalized * np.log(hist_normalized + 1e-10))
            
            # AI images often have too uniform or too structured noise
            ai_likelihood = 0.0
            if entropy < 3.0:  # Too uniform
                ai_likelihood += 0.4
            if noise_std < 2.0 or noise_std > 15.0:  # Unusual noise level
                ai_likelihood += 0.3
            
            return {
                "noise_std": float(noise_std),
                "noise_entropy": float(entropy),
                "ai_likelihood": min(ai_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "ai_likelihood": 0.0}
    
    def _analyze_compression_artifacts(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze compression artifacts for consistency"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Analyze edge consistency (JPEG artifacts should be consistent)
            # Apply DCT to 8x8 blocks (JPEG standard)
            h, w = gray.shape
            block_size = 8
            artifact_scores = []
            
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = gray[y:y+block_size, x:x+block_size].astype(np.float32)
                    
                    # Apply DCT
                    dct_block = cv2.dct(block)
                    
                    # Analyze high-frequency components
                    high_freq = dct_block[4:, 4:]
                    artifact_score = np.std(high_freq)
                    artifact_scores.append(artifact_score)
            
            artifact_variance = np.var(artifact_scores)
            
            # AI images may have inconsistent compression artifacts
            ai_likelihood = 0.0
            if artifact_variance > 100:  # High variance in artifacts
                ai_likelihood += 0.3
            
            return {
                "artifact_variance": float(artifact_variance),
                "ai_likelihood": min(ai_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "ai_likelihood": 0.0}
    
    def _analyze_metadata_for_ai(self, metadata: Dict) -> Dict[str, Any]:
        """Analyze metadata for AI generation indicators"""
        ai_indicators = []
        ai_likelihood = 0.0
        
        # Check software/creator fields for AI tools
        ai_software_keywords = [
            "midjourney", "dall-e", "stable diffusion", "gpt", "ai", "artificial",
            "generated", "synthetic", "deepfake", "gan", "neural", "machine learning"
        ]
        
        # Check various metadata fields
        fields_to_check = []
        
        # Collect text fields from metadata
        def collect_text_fields(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str):
                        fields_to_check.append(f"{prefix}{key}: {value}")
                    elif isinstance(value, dict):
                        collect_text_fields(value, f"{prefix}{key}.")
        
        collect_text_fields(metadata)
        
        # Check for AI keywords
        for field in fields_to_check:
            field_lower = field.lower()
            for keyword in ai_software_keywords:
                if keyword in field_lower:
                    ai_indicators.append(f"AI keyword '{keyword}' found in {field}")
                    ai_likelihood += 0.2
        
        # Check for suspicious metadata patterns
        exif_data = metadata.get("exif", {})
        
        # Missing or unusual camera data
        if not exif_data.get("Make") and not exif_data.get("Model"):
            ai_indicators.append("Missing camera make/model information")
            ai_likelihood += 0.1
        
        # Unusual creation software
        software = exif_data.get("Software", "").lower()
        if any(keyword in software for keyword in ai_software_keywords):
            ai_indicators.append(f"AI-related software detected: {software}")
            ai_likelihood += 0.3
        
        return {
            "ai_indicators": ai_indicators,
            "ai_likelihood": min(ai_likelihood, 1.0)
        }
    
    def _analyze_statistical_properties(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze statistical properties for AI detection"""
        try:
            # Convert to different color spaces
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Analyze color distribution
            color_std = np.std(img, axis=(0, 1))
            
            # Analyze texture using Local Binary Patterns approximation
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            texture_score = np.mean(gradient_magnitude)
            
            # AI images often have unusual statistical properties
            ai_likelihood = 0.0
            
            # Check for too uniform color distribution
            if np.all(color_std < 10):
                ai_likelihood += 0.2
            
            # Check for unusual texture patterns
            if texture_score < 5 or texture_score > 50:
                ai_likelihood += 0.2
            
            return {
                "color_std": color_std.tolist(),
                "texture_score": float(texture_score),
                "ai_likelihood": min(ai_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "ai_likelihood": 0.0}
    
    def detect_ai_text(self, text: str) -> Dict[str, Any]:
        """Detect AI-generated text"""
        result = {
            "available": TRANSFORMERS_AVAILABLE and self.text_detector is not None,
            "ai_probability": 0.0,
            "analysis": {}
        }
        
        if not result["available"]:
            result["error"] = "Text AI detector not available"
            return result
        
        try:
            # Use pre-trained model
            prediction = self.text_detector(text)
            
            # Extract probability (model-dependent)
            if isinstance(prediction, list) and len(prediction) > 0:
                pred = prediction[0]
                if pred.get("label") == "AI":
                    result["ai_probability"] = pred.get("score", 0.0)
                else:
                    result["ai_probability"] = 1.0 - pred.get("score", 0.0)
            
            # Additional heuristic analysis
            result["analysis"] = self._analyze_text_patterns(text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in AI text detection: {e}")
            result["error"] = str(e)
            return result
    
    def _analyze_text_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze text patterns for AI generation indicators"""
        analysis = {
            "length": len(text),
            "sentences": len(text.split('.')),
            "avg_sentence_length": 0,
            "repetition_score": 0,
            "ai_indicators": []
        }
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            analysis["avg_sentence_length"] = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Check for repetitive patterns (common in AI text)
        words = text.lower().split()
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Calculate repetition score
            total_words = len(words)
            unique_words = len(word_freq)
            analysis["repetition_score"] = 1.0 - (unique_words / total_words)
        
        # Check for AI-typical phrases
        ai_phrases = [
            "as an ai", "i'm an ai", "artificial intelligence", "machine learning",
            "i don't have personal", "i cannot", "i'm not able to"
        ]
        
        text_lower = text.lower()
        for phrase in ai_phrases:
            if phrase in text_lower:
                analysis["ai_indicators"].append(f"AI phrase detected: {phrase}")
        
        return analysis

# ============================================================================
# Enhanced Manipulation Detection
# ============================================================================

class EnhancedManipulationDetector:
    """Enhanced image and video manipulation detection"""
    
    def __init__(self):
        self.initialized = OPENCV_AVAILABLE and SKLEARN_AVAILABLE
    
    def detect_image_manipulation(self, filepath: str, metadata: Dict = None) -> Dict[str, Any]:
        """Comprehensive image manipulation detection"""
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
            
            # Method 1: Error Level Analysis (ELA)
            result["detection_methods"]["error_level_analysis"] = self._error_level_analysis(filepath)
            
            # Method 2: Copy-Move Detection
            result["detection_methods"]["copy_move_detection"] = self._copy_move_detection(img)
            
            # Method 3: JPEG Ghost Detection
            result["detection_methods"]["jpeg_ghost_detection"] = self._jpeg_ghost_detection(img)
            
            # Method 4: Noise Analysis
            result["detection_methods"]["noise_analysis"] = self._manipulation_noise_analysis(img)
            
            # Method 5: Metadata Consistency Check
            if metadata:
                result["metadata_inconsistencies"] = self._check_metadata_consistency(metadata, img)
            
            # Method 6: Lighting Consistency Analysis
            result["detection_methods"]["lighting_analysis"] = self._lighting_consistency_analysis(img)
            
            # Combine results
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
    
    def _jpeg_ghost_detection(self, img: np.ndarray) -> Dict[str, Any]:
        """Detect JPEG ghosts indicating multiple compressions"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply DCT to detect compression artifacts
            h, w = gray.shape
            block_size = 8
            ghost_scores = []
            
            for quality in [70, 80, 90, 95]:
                # Simulate JPEG compression at different quality levels
                temp_path = f"temp_ghost_{quality}.jpg"
                cv2.imwrite(temp_path, gray, [cv2.IMWRITE_JPEG_QUALITY, quality])
                compressed = cv2.imread(temp_path, cv2.IMREAD_GRAYSCALE)
                os.remove(temp_path)
                
                # Calculate difference
                diff = cv2.absdiff(gray, compressed)
                ghost_score = np.mean(diff)
                ghost_scores.append(ghost_score)
            
            # Analyze ghost pattern
            ghost_variance = np.var(ghost_scores)
            min_ghost = min(ghost_scores)
            
            manipulation_likelihood = 0.0
            if min_ghost < 2.0:  # Very low difference at some quality
                manipulation_likelihood += 0.4
            if ghost_variance > 10:  # High variance in ghost scores
                manipulation_likelihood += 0.2
            
            return {
                "ghost_scores": ghost_scores,
                "ghost_variance": float(ghost_variance),
                "min_ghost_score": float(min_ghost),
                "manipulation_likelihood": min(manipulation_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "manipulation_likelihood": 0.0}
    
    def _manipulation_noise_analysis(self, img: np.ndarray) -> Dict[str, Any]:
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
    
    def _lighting_consistency_analysis(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze lighting consistency across the image"""
        try:
            # Convert to LAB color space for better lighting analysis
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0].astype(np.float32)
            
            # Calculate gradient to find lighting direction
            grad_x = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(l_channel, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate lighting direction for different regions
            h, w = l_channel.shape
            region_size = min(h, w) // 4
            lighting_directions = []
            
            for y in range(0, h - region_size, region_size):
                for x in range(0, w - region_size, region_size):
                    region_grad_x = grad_x[y:y+region_size, x:x+region_size]
                    region_grad_y = grad_y[y:y+region_size, x:x+region_size]
                    
                    # Calculate dominant gradient direction
                    mean_grad_x = np.mean(region_grad_x)
                    mean_grad_y = np.mean(region_grad_y)
                    
                    if abs(mean_grad_x) > 1 or abs(mean_grad_y) > 1:
                        angle = np.arctan2(mean_grad_y, mean_grad_x)
                        lighting_directions.append(angle)
            
            if not lighting_directions:
                return {"manipulation_likelihood": 0.0}
            
            # Analyze consistency of lighting directions
            direction_variance = np.var(lighting_directions)
            
            manipulation_likelihood = 0.0
            if direction_variance > 2.0:  # High variance in lighting directions
                manipulation_likelihood += 0.4
            
            return {
                "lighting_direction_variance": float(direction_variance),
                "num_regions_analyzed": len(lighting_directions),
                "manipulation_likelihood": min(manipulation_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "manipulation_likelihood": 0.0}
    
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

# ============================================================================
# Enhanced Steganography Detection
# ============================================================================

class EnhancedSteganographyDetector:
    """Enhanced steganography detection using multiple techniques"""
    
    def __init__(self):
        self.initialized = OPENCV_AVAILABLE
    
    def detect_steganography(self, filepath: str) -> Dict[str, Any]:
        """Comprehensive steganography detection"""
        result = {
            "available": self.initialized,
            "steganography_probability": 0.0,
            "detection_methods": {},
            "suspicious_patterns": []
        }
        
        if not self.initialized:
            result["error"] = "OpenCV not available"
            return result
        
        try:
            # Load image
            img = cv2.imread(filepath)
            if img is None:
                result["error"] = "Could not load image"
                return result
            
            # Method 1: LSB Analysis
            result["detection_methods"]["lsb_analysis"] = self._lsb_analysis(img)
            
            # Method 2: Chi-Square Analysis
            result["detection_methods"]["chi_square_analysis"] = self._chi_square_analysis(img)
            
            # Method 3: Histogram Analysis
            result["detection_methods"]["histogram_analysis"] = self._histogram_analysis(img)
            
            # Method 4: Frequency Domain Analysis
            result["detection_methods"]["frequency_analysis"] = self._frequency_domain_stego_analysis(img)
            
            # Method 5: Pixel Pair Analysis
            result["detection_methods"]["pixel_pair_analysis"] = self._pixel_pair_analysis(img)
            
            # Combine results
            stego_indicators = 0
            total_methods = 0
            
            for method, analysis in result["detection_methods"].items():
                if isinstance(analysis, dict) and "steganography_likelihood" in analysis:
                    stego_indicators += analysis["steganography_likelihood"]
                    total_methods += 1
            
            if total_methods > 0:
                result["steganography_probability"] = stego_indicators / total_methods
            
            # Add suspicious patterns
            if result["steganography_probability"] > 0.6:
                result["suspicious_patterns"].append("Unusual LSB patterns detected")
            if result["steganography_probability"] > 0.7:
                result["suspicious_patterns"].append("Statistical anomalies in pixel distribution")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in steganography detection: {e}")
            result["error"] = str(e)
            return result
    
    def _lsb_analysis(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze Least Significant Bit patterns"""
        try:
            # Extract LSBs from each channel
            lsb_planes = []
            for channel in range(3):  # BGR channels
                channel_data = img[:, :, channel]
                lsb_plane = channel_data & 1  # Extract LSB
                lsb_planes.append(lsb_plane)
            
            # Analyze randomness of LSB planes
            randomness_scores = []
            for lsb_plane in lsb_planes:
                # Calculate entropy
                hist, _ = np.histogram(lsb_plane.flatten(), bins=2, range=(0, 1))
                hist_normalized = hist / np.sum(hist)
                entropy = -np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))
                randomness_scores.append(entropy)
            
            # Analyze adjacent pixel correlations in LSB
            correlation_scores = []
            for lsb_plane in lsb_planes:
                # Horizontal correlation
                h_corr = np.corrcoef(lsb_plane[:-1, :].flatten(), lsb_plane[1:, :].flatten())[0, 1]
                # Vertical correlation
                v_corr = np.corrcoef(lsb_plane[:, :-1].flatten(), lsb_plane[:, 1:].flatten())[0, 1]
                correlation_scores.append((abs(h_corr) + abs(v_corr)) / 2)
            
            avg_entropy = np.mean(randomness_scores)
            avg_correlation = np.mean(correlation_scores)
            
            steganography_likelihood = 0.0
            
            # High entropy in LSB suggests hidden data
            if avg_entropy > 0.9:
                steganography_likelihood += 0.4
            
            # Low correlation in LSB suggests hidden data
            if avg_correlation < 0.1:
                steganography_likelihood += 0.3
            
            return {
                "lsb_entropy": float(avg_entropy),
                "lsb_correlation": float(avg_correlation),
                "steganography_likelihood": min(steganography_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "steganography_likelihood": 0.0}
    
    def _chi_square_analysis(self, img: np.ndarray) -> Dict[str, Any]:
        """Chi-square analysis for detecting embedded data"""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Perform chi-square test on pixel pairs
            # Group pixels into pairs (even, odd)
            even_pixels = gray[::2, ::2].flatten()
            odd_pixels = gray[1::2, 1::2].flatten()
            
            min_len = min(len(even_pixels), len(odd_pixels))
            even_pixels = even_pixels[:min_len]
            odd_pixels = odd_pixels[:min_len]
            
            # Calculate expected vs observed frequencies
            pixel_pairs = list(zip(even_pixels, odd_pixels))
            
            # Count occurrences of each pair type
            pair_counts = {}
            for pair in pixel_pairs:
                pair_counts[pair] = pair_counts.get(pair, 0) + 1
            
            # Calculate chi-square statistic
            total_pairs = len(pixel_pairs)
            expected_freq = total_pairs / (256 * 256)  # Uniform distribution expectation
            
            chi_square = 0
            for count in pair_counts.values():
                chi_square += ((count - expected_freq) ** 2) / expected_freq
            
            # Normalize chi-square value
            normalized_chi_square = chi_square / total_pairs
            
            steganography_likelihood = 0.0
            if normalized_chi_square > 1.5:  # Threshold for suspicious activity
                steganography_likelihood += 0.5
            
            return {
                "chi_square_statistic": float(normalized_chi_square),
                "steganography_likelihood": min(steganography_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "steganography_likelihood": 0.0}
    
    def _histogram_analysis(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze histograms for steganography indicators"""
        try:
            # Analyze each color channel
            channel_analyses = []
            
            for channel in range(3):
                channel_data = img[:, :, channel]
                
                # Calculate histogram
                hist, _ = np.histogram(channel_data.flatten(), bins=256, range=(0, 255))
                
                # Analyze histogram properties
                # 1. Check for unusual spikes or gaps
                hist_diff = np.diff(hist)
                spike_count = np.sum(np.abs(hist_diff) > np.std(hist_diff) * 3)
                
                # 2. Check for pairs of values (common in LSB steganography)
                pair_anomalies = 0
                for i in range(0, 254, 2):
                    if abs(hist[i] - hist[i+1]) > np.mean(hist) * 0.5:
                        pair_anomalies += 1
                
                channel_analyses.append({
                    "spike_count": spike_count,
                    "pair_anomalies": pair_anomalies
                })
            
            # Combine channel analyses
            avg_spikes = np.mean([analysis["spike_count"] for analysis in channel_analyses])
            avg_pair_anomalies = np.mean([analysis["pair_anomalies"] for analysis in channel_analyses])
            
            steganography_likelihood = 0.0
            if avg_spikes > 10:
                steganography_likelihood += 0.2
            if avg_pair_anomalies > 20:
                steganography_likelihood += 0.4
            
            return {
                "average_spikes": float(avg_spikes),
                "average_pair_anomalies": float(avg_pair_anomalies),
                "steganography_likelihood": min(steganography_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "steganography_likelihood": 0.0}
    
    def _frequency_domain_stego_analysis(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze frequency domain for steganography"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply DCT
            dct = cv2.dct(gray.astype(np.float32))
            
            # Analyze high-frequency components
            h, w = dct.shape
            
            # Extract high-frequency region (bottom-right quadrant)
            high_freq = dct[h//2:, w//2:]
            
            # Calculate statistics of high-frequency components
            hf_mean = np.mean(np.abs(high_freq))
            hf_std = np.std(high_freq)
            hf_energy = np.sum(high_freq ** 2)
            
            # Compare with expected values for natural images
            steganography_likelihood = 0.0
            
            # Unusual high-frequency energy suggests hidden data
            if hf_energy > np.sum(dct ** 2) * 0.1:  # More than 10% energy in HF
                steganography_likelihood += 0.3
            
            if hf_std > hf_mean * 2:  # High variation in HF components
                steganography_likelihood += 0.2
            
            return {
                "high_freq_energy_ratio": float(hf_energy / np.sum(dct ** 2)),
                "high_freq_std_mean_ratio": float(hf_std / (hf_mean + 1e-10)),
                "steganography_likelihood": min(steganography_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "steganography_likelihood": 0.0}
    
    def _pixel_pair_analysis(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze pixel pairs for steganography detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Create pixel pairs (horizontal and vertical)
            h_pairs = []
            v_pairs = []
            
            h, w = gray.shape
            
            # Horizontal pairs
            for y in range(h):
                for x in range(w - 1):
                    h_pairs.append((gray[y, x], gray[y, x + 1]))
            
            # Vertical pairs
            for y in range(h - 1):
                for x in range(w):
                    v_pairs.append((gray[y, x], gray[y + 1, x]))
            
            # Analyze pair distributions
            def analyze_pairs(pairs):
                # Count transitions between even/odd values
                even_even = sum(1 for p1, p2 in pairs if p1 % 2 == 0 and p2 % 2 == 0)
                even_odd = sum(1 for p1, p2 in pairs if p1 % 2 == 0 and p2 % 2 == 1)
                odd_even = sum(1 for p1, p2 in pairs if p1 % 2 == 1 and p2 % 2 == 0)
                odd_odd = sum(1 for p1, p2 in pairs if p1 % 2 == 1 and p2 % 2 == 1)
                
                total = len(pairs)
                return {
                    "even_even": even_even / total,
                    "even_odd": even_odd / total,
                    "odd_even": odd_even / total,
                    "odd_odd": odd_odd / total
                }
            
            h_analysis = analyze_pairs(h_pairs)
            v_analysis = analyze_pairs(v_pairs)
            
            # Calculate deviation from expected uniform distribution (0.25 each)
            expected = 0.25
            h_deviation = sum(abs(v - expected) for v in h_analysis.values())
            v_deviation = sum(abs(v - expected) for v in v_analysis.values())
            
            avg_deviation = (h_deviation + v_deviation) / 2
            
            steganography_likelihood = 0.0
            if avg_deviation > 0.1:  # Significant deviation from uniform
                steganography_likelihood += 0.4
            
            return {
                "horizontal_deviation": float(h_deviation),
                "vertical_deviation": float(v_deviation),
                "average_deviation": float(avg_deviation),
                "steganography_likelihood": min(steganography_likelihood, 1.0)
            }
            
        except Exception as e:
            return {"error": str(e), "steganography_likelihood": 0.0}

# ============================================================================
# Main Interface Functions
# ============================================================================

def detect_ai_content(filepath: str, metadata: Dict = None) -> Dict[str, Any]:
    """Detect AI-generated content in files"""
    detector = AIContentDetector()
    
    # Determine file type
    file_ext = Path(filepath).suffix.lower()
    
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
        return detector.detect_ai_image(filepath, metadata)
    else:
        return {"available": False, "reason": "Unsupported file type for AI detection"}

def detect_enhanced_manipulation(filepath: str, metadata: Dict = None) -> Dict[str, Any]:
    """Enhanced manipulation detection"""
    detector = EnhancedManipulationDetector()
    return detector.detect_image_manipulation(filepath, metadata)

def detect_enhanced_steganography(filepath: str) -> Dict[str, Any]:
    """Enhanced steganography detection"""
    detector = EnhancedSteganographyDetector()
    return detector.detect_steganography(filepath)