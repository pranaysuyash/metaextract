#!/usr/bin/env python3
"""
Steganography Detection Module for MetaExtract

Detects hidden data in images using various analysis techniques:
- LSB (Least Significant Bit) analysis
- Frequency domain analysis
- Entropy calculation
- Statistical analysis
- Visual attack detection
"""

import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import hashlib

# Import PIL Image at module level
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None  # type: ignore[assignment]
    PIL_AVAILABLE = False

try:
    import scipy.fft
    import scipy.stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class SteganographyDetector:
    """Advanced steganography detection using multiple analysis methods."""
    
    def __init__(self):
        self.detection_methods = [
            self._lsb_analysis,
            self._entropy_analysis,
            self._frequency_analysis,
            self._statistical_analysis,
            self._visual_attack_detection
        ]
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Comprehensive steganography analysis of an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing analysis results and suspicion scores
        """
        if not PIL_AVAILABLE:
            return {"error": "PIL not available for steganography detection"}
        
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to numpy array for analysis
                img_array = np.array(img)
                
                results = {
                    "image_info": {
                        "width": img.width,
                        "height": img.height,
                        "mode": img.mode,
                        "format": img.format,
                        "total_pixels": img.width * img.height
                    },
                    "analysis_methods": {},
                    "overall_suspicion": 0.0,
                    "recommendations": []
                }
                
                # Run all detection methods
                suspicion_scores = []
                
                for method in self.detection_methods:
                    try:
                        method_name = method.__name__.replace('_', ' ').title()
                        method_result = method(img_array, img)
                        results["analysis_methods"][method_name] = method_result
                        
                        if "suspicion_score" in method_result:
                            suspicion_scores.append(method_result["suspicion_score"])
                            
                    except Exception as e:
                        logger.warning(f"Steganography method {method.__name__} failed: {e}")
                        results["analysis_methods"][method.__name__] = {"error": str(e)}
                
                # Calculate overall suspicion score
                if suspicion_scores:
                    results["overall_suspicion"] = np.mean(suspicion_scores)
                    results["max_suspicion"] = max(suspicion_scores)
                    results["methods_triggered"] = sum(1 for score in suspicion_scores if score > 0.5)
                
                # Generate recommendations
                results["recommendations"] = self._generate_recommendations(results)
                
                return results
                
        except Exception as e:
            logger.error(f"Steganography analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _lsb_analysis(self, img_array: np.ndarray, img: 'Image.Image') -> Dict[str, Any]:
        """
        Analyze Least Significant Bit patterns for hidden data.
        
        LSB steganography hides data in the least significant bits of pixel values.
        We look for statistical anomalies in these bits.
        """
        result = {
            "method": "LSB Analysis",
            "description": "Detects hidden data in least significant bits",
            "suspicion_score": 0.0,
            "details": {}
        }
        
        try:
            # Extract LSBs from each color channel
            lsb_data = {}
            
            for channel_idx, channel_name in enumerate(['red', 'green', 'blue']):
                if img_array.shape[2] > channel_idx:
                    channel_data = img_array[:, :, channel_idx]
                    lsbs = channel_data & 1  # Extract LSBs
                    
                    # Calculate statistics
                    total_bits = lsbs.size
                    ones_count = np.sum(lsbs)
                    zeros_count = total_bits - ones_count
                    
                    # Expected ratio should be close to 50/50 for natural images
                    ones_ratio = ones_count / total_bits
                    deviation_from_expected = abs(ones_ratio - 0.5)
                    
                    # Calculate entropy of LSB sequence
                    lsb_flat = lsbs.flatten()
                    entropy = self._calculate_entropy(lsb_flat)
                    
                    # Check for patterns (runs of same bits)
                    max_run_length = self._find_max_run_length(lsb_flat)
                    
                    lsb_data[channel_name] = {
                        "ones_ratio": round(ones_ratio, 4),
                        "deviation_from_50_50": round(deviation_from_expected, 4),
                        "entropy": round(entropy, 4),
                        "max_run_length": max_run_length,
                        "total_bits": total_bits
                    }
            
            result["details"] = lsb_data
            
            # Calculate suspicion score based on multiple factors
            suspicion_factors = []
            
            for channel_data in lsb_data.values():
                # High deviation from 50/50 ratio is suspicious
                if channel_data["deviation_from_50_50"] > 0.1:
                    suspicion_factors.append(channel_data["deviation_from_50_50"] * 2)
                
                # Very high or very low entropy is suspicious
                entropy = channel_data["entropy"]
                if entropy < 0.8 or entropy > 0.99:
                    suspicion_factors.append(abs(entropy - 0.9) * 2)
                
                # Unusually long runs of same bits
                if channel_data["max_run_length"] > 50:
                    suspicion_factors.append(min(channel_data["max_run_length"] / 100, 1.0))
            
            if suspicion_factors:
                result["suspicion_score"] = min(np.mean(suspicion_factors), 1.0)
            
            # Add interpretation
            if result["suspicion_score"] > 0.7:
                result["interpretation"] = "High probability of LSB steganography"
            elif result["suspicion_score"] > 0.4:
                result["interpretation"] = "Moderate suspicion of hidden data"
            else:
                result["interpretation"] = "LSB patterns appear normal"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _entropy_analysis(self, img_array: np.ndarray, img: 'Image.Image') -> Dict[str, Any]:
        """
        Analyze entropy patterns to detect hidden data.
        
        Hidden data often changes the entropy characteristics of image regions.
        """
        result = {
            "method": "Entropy Analysis",
            "description": "Analyzes randomness patterns in image data",
            "suspicion_score": 0.0,
            "details": {}
        }
        
        try:
            # Calculate entropy for different block sizes
            block_sizes = [8, 16, 32, 64]
            entropy_data = {}
            
            for block_size in block_sizes:
                entropies = []
                
                # Divide image into blocks and calculate entropy for each
                height, width = img_array.shape[:2]
                
                for y in range(0, height - block_size, block_size):
                    for x in range(0, width - block_size, block_size):
                        block = img_array[y:y+block_size, x:x+block_size]
                        block_entropy = self._calculate_entropy(block.flatten())
                        entropies.append(block_entropy)
                
                if entropies:
                    entropy_data[f"block_{block_size}"] = {
                        "mean_entropy": round(np.mean(entropies), 4),
                        "std_entropy": round(np.std(entropies), 4),
                        "min_entropy": round(np.min(entropies), 4),
                        "max_entropy": round(np.max(entropies), 4),
                        "entropy_variance": round(np.var(entropies), 4)
                    }
            
            result["details"] = entropy_data
            
            # Calculate suspicion based on entropy patterns
            suspicion_factors = []
            
            for block_data in entropy_data.values():
                # Very high variance in entropy across blocks is suspicious
                if block_data["entropy_variance"] > 0.1:
                    suspicion_factors.append(block_data["entropy_variance"] * 5)
                
                # Unusually high mean entropy
                if block_data["mean_entropy"] > 0.95:
                    suspicion_factors.append((block_data["mean_entropy"] - 0.9) * 10)
            
            if suspicion_factors:
                result["suspicion_score"] = min(np.mean(suspicion_factors), 1.0)
            
            # Add interpretation
            if result["suspicion_score"] > 0.6:
                result["interpretation"] = "Unusual entropy patterns detected"
            elif result["suspicion_score"] > 0.3:
                result["interpretation"] = "Some entropy irregularities found"
            else:
                result["interpretation"] = "Entropy patterns appear normal"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _frequency_analysis(self, img_array: np.ndarray, img: 'Image.Image') -> Dict[str, Any]:
        """
        Analyze frequency domain characteristics for steganography detection.
        
        Hidden data can create artifacts in the frequency domain.
        """
        result = {
            "method": "Frequency Analysis",
            "description": "Analyzes frequency domain for hidden data artifacts",
            "suspicion_score": 0.0,
            "details": {}
        }
        
        if not SCIPY_AVAILABLE:
            result["error"] = "SciPy not available for frequency analysis"
            return result
        
        try:
            # Convert to grayscale for frequency analysis
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            # Perform 2D FFT
            fft_result = scipy.fft.fft2(gray)
            fft_magnitude = np.abs(fft_result)
            fft_phase = np.angle(fft_result)
            
            # Calculate frequency domain statistics
            freq_stats = {
                "dc_component": float(fft_magnitude[0, 0]),
                "mean_magnitude": float(np.mean(fft_magnitude)),
                "std_magnitude": float(np.std(fft_magnitude)),
                "max_magnitude": float(np.max(fft_magnitude)),
                "high_freq_energy": float(np.sum(fft_magnitude[fft_magnitude.shape[0]//2:, fft_magnitude.shape[1]//2:]))
            }
            
            # Analyze phase characteristics
            phase_stats = {
                "mean_phase": float(np.mean(fft_phase)),
                "std_phase": float(np.std(fft_phase)),
                "phase_entropy": self._calculate_entropy(fft_phase.flatten())
            }
            
            result["details"] = {
                "frequency_domain": freq_stats,
                "phase_analysis": phase_stats
            }
            
            # Calculate suspicion based on frequency anomalies
            suspicion_factors = []
            
            # Unusual high frequency energy can indicate hidden data
            total_energy = np.sum(fft_magnitude)
            high_freq_ratio = freq_stats["high_freq_energy"] / total_energy
            
            if high_freq_ratio > 0.3:  # Threshold for suspicious high freq energy
                suspicion_factors.append(high_freq_ratio)
            
            # Unusual phase characteristics
            if phase_stats["phase_entropy"] > 0.95:
                suspicion_factors.append((phase_stats["phase_entropy"] - 0.9) * 10)
            
            if suspicion_factors:
                result["suspicion_score"] = min(np.mean(suspicion_factors), 1.0)
            
            # Add interpretation
            if result["suspicion_score"] > 0.5:
                result["interpretation"] = "Frequency domain anomalies detected"
            else:
                result["interpretation"] = "Frequency characteristics appear normal"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _statistical_analysis(self, img_array: np.ndarray, img: 'Image.Image') -> Dict[str, Any]:
        """
        Perform statistical tests for steganography detection.
        
        Uses chi-square and other statistical tests to detect hidden data.
        """
        result = {
            "method": "Statistical Analysis",
            "description": "Statistical tests for hidden data detection",
            "suspicion_score": 0.0,
            "details": {}
        }
        
        try:
            # Flatten image for statistical analysis
            flat_data = img_array.flatten()
            
            # Calculate basic statistics
            stats = {
                "mean": float(np.mean(flat_data)),
                "std": float(np.std(flat_data)),
                "skewness": float(scipy.stats.skew(flat_data)) if SCIPY_AVAILABLE else None,
                "kurtosis": float(scipy.stats.kurtosis(flat_data)) if SCIPY_AVAILABLE else None,
                "min_value": int(np.min(flat_data)),
                "max_value": int(np.max(flat_data))
            }
            
            # Histogram analysis
            hist, bins = np.histogram(flat_data, bins=256, range=(0, 255))
            
            # Chi-square test for uniformity
            expected_freq = len(flat_data) / 256
            chi_square = np.sum((hist - expected_freq) ** 2 / expected_freq)
            
            # Calculate histogram entropy
            hist_normalized = hist / np.sum(hist)
            hist_entropy = -np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))
            
            result["details"] = {
                "basic_stats": stats,
                "chi_square": float(chi_square),
                "histogram_entropy": float(hist_entropy),
                "histogram_peaks": int(np.sum(hist > expected_freq * 2))  # Count significant peaks
            }
            
            # Calculate suspicion based on statistical anomalies
            suspicion_factors = []
            
            # Very high chi-square indicates non-uniform distribution
            if chi_square > 1000:  # Threshold for suspicious chi-square
                suspicion_factors.append(min(chi_square / 5000, 1.0))
            
            # Unusual skewness or kurtosis
            if stats["skewness"] is not None:
                if abs(stats["skewness"]) > 2:
                    suspicion_factors.append(min(abs(stats["skewness"]) / 5, 1.0))
            
            if stats["kurtosis"] is not None:
                if abs(stats["kurtosis"]) > 5:
                    suspicion_factors.append(min(abs(stats["kurtosis"]) / 10, 1.0))
            
            if suspicion_factors:
                result["suspicion_score"] = min(np.mean(suspicion_factors), 1.0)
            
            # Add interpretation
            if result["suspicion_score"] > 0.6:
                result["interpretation"] = "Statistical anomalies suggest hidden data"
            elif result["suspicion_score"] > 0.3:
                result["interpretation"] = "Some statistical irregularities detected"
            else:
                result["interpretation"] = "Statistical properties appear normal"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _visual_attack_detection(self, img_array: np.ndarray, img: 'Image.Image') -> Dict[str, Any]:
        """
        Visual attack detection - looks for patterns visible to human eye.
        
        Some steganography methods create visible artifacts.
        """
        result = {
            "method": "Visual Attack Detection",
            "description": "Detects visually apparent steganography artifacts",
            "suspicion_score": 0.0,
            "details": {}
        }
        
        try:
            # Analyze each color channel separately
            channel_analysis = {}
            
            for channel_idx, channel_name in enumerate(['red', 'green', 'blue']):
                if img_array.shape[2] > channel_idx:
                    channel = img_array[:, :, channel_idx]
                    
                    # Look for unusual patterns in LSBs
                    lsb_plane = channel & 1
                    
                    # Calculate local variance in LSB plane
                    lsb_variance = np.var(lsb_plane)
                    
                    # Look for checkerboard patterns (common artifact)
                    checkerboard_score = self._detect_checkerboard_pattern(lsb_plane)
                    
                    # Detect unusual edge patterns
                    edge_score = self._detect_unusual_edges(channel)
                    
                    channel_analysis[channel_name] = {
                        "lsb_variance": float(lsb_variance),
                        "checkerboard_score": float(checkerboard_score),
                        "edge_anomaly_score": float(edge_score)
                    }
            
            result["details"] = channel_analysis
            
            # Calculate overall suspicion
            suspicion_factors = []
            
            for channel_data in channel_analysis.values():
                # High LSB variance can indicate hidden data
                if channel_data["lsb_variance"] > 0.3:
                    suspicion_factors.append(channel_data["lsb_variance"])
                
                # Checkerboard patterns are suspicious
                if channel_data["checkerboard_score"] > 0.5:
                    suspicion_factors.append(channel_data["checkerboard_score"])
                
                # Unusual edge patterns
                if channel_data["edge_anomaly_score"] > 0.4:
                    suspicion_factors.append(channel_data["edge_anomaly_score"])
            
            if suspicion_factors:
                result["suspicion_score"] = min(np.mean(suspicion_factors), 1.0)
            
            # Add interpretation
            if result["suspicion_score"] > 0.7:
                result["interpretation"] = "Visual artifacts strongly suggest steganography"
            elif result["suspicion_score"] > 0.4:
                result["interpretation"] = "Some visual anomalies detected"
            else:
                result["interpretation"] = "No obvious visual artifacts found"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy of data."""
        try:
            # Get unique values and their counts
            unique, counts = np.unique(data, return_counts=True)
            
            # Calculate probabilities
            probabilities = counts / len(data)
            
            # Calculate entropy
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            
            # Normalize by maximum possible entropy
            max_entropy = np.log2(len(unique))
            
            return entropy / max_entropy if max_entropy > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    def _find_max_run_length(self, data: np.ndarray) -> int:
        """Find the maximum run length of consecutive identical values."""
        if len(data) == 0:
            return 0
        
        max_run = 1
        current_run = 1
        
        for i in range(1, len(data)):
            if data[i] == data[i-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        
        return max_run
    
    def _detect_checkerboard_pattern(self, lsb_plane: np.ndarray) -> float:
        """Detect checkerboard patterns in LSB plane."""
        try:
            height, width = lsb_plane.shape
            
            # Create expected checkerboard patterns
            checkerboard1 = np.zeros((height, width))
            checkerboard2 = np.zeros((height, width))
            
            for i in range(height):
                for j in range(width):
                    checkerboard1[i, j] = (i + j) % 2
                    checkerboard2[i, j] = (i + j + 1) % 2
            
            # Calculate correlation with both patterns
            corr1 = np.corrcoef(lsb_plane.flatten(), checkerboard1.flatten())[0, 1]
            corr2 = np.corrcoef(lsb_plane.flatten(), checkerboard2.flatten())[0, 1]
            
            # Return maximum absolute correlation
            return max(abs(corr1), abs(corr2))
            
        except Exception as e:
            return 0.0
    
    def _detect_unusual_edges(self, channel: np.ndarray) -> float:
        """Detect unusual edge patterns that might indicate steganography."""
        try:
            # Simple edge detection using gradients
            grad_x = np.gradient(channel, axis=1)
            grad_y = np.gradient(channel, axis=0)
            
            # Calculate edge magnitude
            edge_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Look for unusually sharp or artificial edges
            edge_threshold = np.percentile(edge_magnitude, 95)
            strong_edges = edge_magnitude > edge_threshold
            
            # Calculate edge density
            edge_density = np.sum(strong_edges) / strong_edges.size
            
            # High edge density in LSB modifications can be suspicious
            return min(edge_density * 10, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        overall_suspicion = results.get("overall_suspicion", 0.0)
        
        if overall_suspicion > 0.7:
            recommendations.append("HIGH ALERT: Multiple indicators suggest hidden data presence")
            recommendations.append("Recommend forensic analysis with specialized tools")
            recommendations.append("Consider examining file with hex editor for embedded data")
        elif overall_suspicion > 0.4:
            recommendations.append("MODERATE SUSPICION: Some anomalies detected")
            recommendations.append("Further analysis recommended")
            recommendations.append("Check file history and source")
        else:
            recommendations.append("LOW SUSPICION: Image appears normal")
            recommendations.append("No immediate steganography indicators found")
        
        # Method-specific recommendations
        methods = results.get("analysis_methods", {})
        
        if "Lsb Analysis" in methods:
            lsb_score = methods["Lsb Analysis"].get("suspicion_score", 0)
            if lsb_score > 0.6:
                recommendations.append("LSB steganography highly suspected - check least significant bits")
        
        if "Frequency Analysis" in methods:
            freq_score = methods["Frequency Analysis"].get("suspicion_score", 0)
            if freq_score > 0.5:
                recommendations.append("Frequency domain anomalies detected - possible DCT-based hiding")
        
        if "Visual Attack Detection" in methods:
            visual_score = methods["Visual Attack Detection"].get("suspicion_score", 0)
            if visual_score > 0.6:
                recommendations.append("Visual artifacts detected - examine image closely for patterns")
        
        return recommendations

# Global detector instance
_detector = None

def get_steganography_detector() -> SteganographyDetector:
    """Get or create the global steganography detector instance."""
    global _detector
    if _detector is None:
        _detector = SteganographyDetector()
    return _detector

def analyze_steganography(image_path: str) -> Dict[str, Any]:
    """
    Analyze an image for steganography indicators.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dictionary containing analysis results
    """
    detector = get_steganography_detector()
    return detector.analyze_image(image_path)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python steganography.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"Error: File {image_path} not found")
        sys.exit(1)
    
    print(f"Analyzing {image_path} for steganography...")
    result = analyze_steganography(image_path)
    
    print(json.dumps(result, indent=2, default=str))