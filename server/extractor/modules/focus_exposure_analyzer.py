"""
Enhanced Focus and Exposure Analysis for AI Culling
====================================================

Advanced analysis of focus accuracy and exposure quality:
- Multi-point AF analysis
- Sharpness detection algorithms  
- Exposure histogram analysis
- Dynamic range assessment
- Face detection and eye focus
- Depth of field analysis

Author: MetaExtract Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FocusAnalysis:
    """Detailed focus analysis results."""
    overall_score: float
    af_points_used: int
    af_points_in_focus: int
    focus_mode_confidence: float
    face_detected: bool
    eyes_in_focus: bool
    sharpness_estimate: float
    depth_of_field_quality: float
    focus_recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall_score': self.overall_score,
            'af_points_used': self.af_points_used,
            'af_points_in_focus': self.af_points_in_focus,
            'focus_mode_confidence': self.focus_mode_confidence,
            'face_detected': self.face_detected,
            'eyes_in_focus': self.eyes_in_focus,
            'sharpness_estimate': self.sharpness_estimate,
            'depth_of_field_quality': self.depth_of_field_quality,
            'focus_recommendations': self.focus_recommendations
        }

@dataclass
class ExposureAnalysis:
    """Detailed exposure analysis results."""
    overall_score: float
    exposure_compensation: float
    histogram_balance: float
    dynamic_range: float
    highlight_clipping: float
    shadow_noise: float
    exposure_quality: str  # 'underexposed', 'properly_exposed', 'overexposed'
    exposure_recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall_score': self.overall_score,
            'exposure_compensation': self.exposure_compensation,
            'histogram_balance': self.histogram_balance,
            'dynamic_range': self.dynamic_range,
            'highlight_clipping': self.highlight_clipping,
            'shadow_noise': self.shadow_noise,
            'exposure_quality': self.exposure_quality,
            'exposure_recommendations': self.exposure_recommendations
        }

class FocusAnalyzer:
    """Advanced focus quality analyzer."""
    
    def __init__(self):
        # Focus mode quality weights
        self.focus_mode_scores = {
            'AF-S': 95, 'Single': 95, 'One Shot': 95, 'Single AF': 95,
            'AF-C': 90, 'Continuous': 90, 'AI Servo': 90,
            'AF-A': 85, 'Auto AF': 85,
            'Manual': 70, 'MF': 70
        }
        
        # AF area mode scores
        self.af_area_scores = {
            'Single-point AF': 100, 'Spot AF': 100,
            'Dynamic-area AF': 90, 'Zone AF': 85,
            'Wide-area AF': 80, 'Auto-area AF': 75
        }
    
    def analyze_focus(self, photo_metadata: Dict[str, Any]) -> FocusAnalysis:
        """
        Perform comprehensive focus analysis.
        
        Args:
            photo_metadata: Photo EXIF and metadata dictionary
            
        Returns:
            FocusAnalysis with detailed results
        """
        exif = photo_metadata.get('exif', {})
        focus_metadata = exif.get('exif_focus', {})
        
        # Analyze AF points
        af_analysis = self._analyze_af_points(focus_metadata)
        
        # Analyze focus mode
        focus_mode_score = self._analyze_focus_mode(exif, focus_metadata)
        
        # Face and eye detection
        face_analysis = self._analyze_face_detection(exif, focus_metadata)
        
        # Sharpness estimation (based on available data)
        sharpness_score = self._estimate_sharpness(exif, focus_metadata)
        
        # Depth of field quality
        dof_score = self._analyze_depth_of_field(exif)
        
        # Calculate overall focus score
        overall_score = self._calculate_focus_score(
            af_analysis, focus_mode_score, face_analysis, sharpness_score, dof_score
        )
        
        # Generate recommendations
        recommendations = self._generate_focus_recommendations(
            af_analysis, focus_mode_score, face_analysis, sharpness_score, overall_score
        )
        
        return FocusAnalysis(
            overall_score=overall_score,
            af_points_used=af_analysis['points_used'],
            af_points_in_focus=af_analysis['points_in_focus'],
            focus_mode_confidence=focus_mode_score,
            face_detected=face_analysis['face_detected'],
            eyes_in_focus=face_analysis['eyes_in_focus'],
            sharpness_estimate=sharpness_score,
            depth_of_field_quality=dof_score,
            focus_recommendations=recommendations
        )
    
    def _analyze_af_points(self, focus_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze AF point usage and focus."""
        points_used = 0
        points_in_focus = 0
        
        # Check various AF point fields
        af_point_fields = [
            'points_used', 'pointsinfocus', 'afpoints',
            'pointsselected', 'afarea', 'afzone'
        ]
        
        for field in af_point_fields:
            value = focus_metadata.get(field)
            if value:
                if isinstance(value, (list, tuple)):
                    points_used = len(value)
                    points_in_focus = len([p for p in value if p])
                elif isinstance(value, str):
                    try:
                        # Try to parse numeric AF point count
                        points_used = int(value.split()[0])
                        points_in_focus = points_used  # Assume all in focus
                    except (ValueError, IndexError):
                        points_used = 1
                        points_in_focus = 1
                elif isinstance(value, (int, float)):
                    points_used = int(value)
                    points_in_focus = points_used
                break
        
        return {
            'points_used': points_used,
            'points_in_focus': points_in_focus
        }
    
    def _analyze_focus_mode(self, exif: Dict[str, Any], focus_metadata: Dict[str, Any]) -> float:
        """Analyze focus mode and assign confidence score."""
        # Check various focus mode fields
        focus_mode_fields = ['focusmode', 'afmode', 'focusmode']
        
        for field in focus_mode_fields:
            value = exif.get(field) or focus_metadata.get(field)
            if value:
                focus_mode_str = str(value).upper()
                
                # Find matching focus mode score
                for mode, score in self.focus_mode_scores.items():
                    if mode.upper() in focus_mode_str:
                        return score
                
                # Partial matches
                if 'AF' in focus_mode_str and 'AUTO' in focus_mode_str:
                    return 75
                elif 'MANUAL' in focus_mode_str or 'MF' in focus_mode_str:
                    return 70
                elif 'AF' in focus_mode_str:
                    return 80
        
        return 50.0  # Unknown focus mode
    
    def _analyze_face_detection(self, exif: Dict[str, Any], focus_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze face detection and eye focus."""
        face_detected = False
        eyes_in_focus = False
        face_count = 0
        
        # Check face detection fields
        face_fields = ['facedetected', 'facedetect', 'facecount']
        for field in face_fields:
            value = exif.get(field) or focus_metadata.get(field)
            if value:
                if isinstance(value, bool):
                    face_detected = value
                elif isinstance(value, (int, float)):
                    face_count = int(value)
                    face_detected = face_count > 0
                elif isinstance(value, str):
                    if 'true' in value.lower() or 'yes' in value.lower():
                        face_detected = True
                    try:
                        face_count = int(value)
                        face_detected = face_count > 0
                    except ValueError:
                        pass
        
        # Eye focus detection (if available)
        eye_focus_fields = ['eyefocus', 'eyedetect', 'eyesinfocus']
        for field in eye_focus_fields:
            value = exif.get(field) or focus_metadata.get(field)
            if value:
                if isinstance(value, bool):
                    eyes_in_focus = value
                elif isinstance(value, str):
                    if 'true' in value.lower() or 'yes' in value.lower():
                        eyes_in_focus = True
                break
        
        # If face detected but no explicit eye focus, estimate based on focus mode
        if face_detected and not eyes_in_focus:
            # Advanced cameras with face detection usually have eye AF
            face_aware_cameras = ['R5', 'R6', 'A7R', 'A9', 'Z9', 'S1H']
            camera_model = exif.get('model', '')
            if any(cam in str(camera_model) for cam in face_aware_cameras):
                eyes_in_focus = True
        
        return {
            'face_detected': face_detected,
            'eyes_in_focus': eyes_in_focus,
            'face_count': face_count
        }
    
    def _estimate_sharpness(self, exif: Dict[str, Any], focus_metadata: Dict[str, Any]) -> float:
        """Estimate sharpness based on available metadata."""
        sharpness_score = 50.0  # Base score
        
        # ISO impact on sharpness
        iso = exif.get('isospeedratings') or exif.get('iso')
        if iso:
            try:
                iso_val = float(iso)
                if iso_val <= 100:
                    sharpness_score += 20
                elif iso_val <= 400:
                    sharpness_score += 15
                elif iso_val <= 800:
                    sharpness_score += 10
                elif iso_val <= 1600:
                    sharpness_score += 5
                else:
                    sharpness_score -= min(20, (iso_val - 1600) / 100)
            except (ValueError, TypeError):
                pass
        
        # Aperture impact on sharpness
        fnumber = exif.get('fnumber')
        if fnumber:
            try:
                aperture = float(fnumber)
                # Sweet spot for sharpness (diffraction vs aberrations)
                if 4.0 <= aperture <= 8.0:
                    sharpness_score += 20
                elif 2.8 <= aperture < 4.0 or 8.0 < aperture <= 11.0:
                    sharpness_score += 15
                elif 1.4 <= aperture < 2.8 or 11.0 < aperture <= 16.0:
                    sharpness_score += 10
                else:
                    sharpness_score += 5
            except (ValueError, TypeError):
                pass
        
        # Shutter speed impact (motion blur)
        shutter_speed = exif.get('exposuretime')
        if shutter_speed:
            try:
                shutter = float(shutter_speed)
                if shutter >= 1/125:  # Fast enough to avoid motion blur
                    sharpness_score += 15
                elif shutter >= 1/60:
                    sharpness_score += 10
                elif shutter >= 1/30:
                    sharpness_score += 5
                else:
                    sharpness_score -= 10  # Potential motion blur
            except (ValueError, TypeError):
                pass
        
        # Lens quality impact
        lens_model = exif.get('lensmodel')
        if lens_model:
            lens_str = str(lens_model).upper()
            # Professional lens indicators
            pro_indicators = ['GM', 'L', 'ART', 'PRO', 'OTUS', 'MASTER', 'DG', 'EX']
            if any(indicator in lens_str for indicator in pro_indicators):
                sharpness_score += 15
            elif any(brand in lens_str for brand in ['CANON', 'NIKON', 'SONY', 'FUJIFILM']):
                sharpness_score += 10
        
        # Image stabilization
        is_mode = exif.get('imagestabilization') or exif.get('vibrationreduction')
        if is_mode:
            is_str = str(is_mode).upper()
            if 'ON' in is_str or 'ACTIVE' in is_str:
                sharpness_score += 10
        
        return min(100.0, max(0.0, sharpness_score))
    
    def _analyze_depth_of_field(self, exif: Dict[str, Any]) -> float:
        """Analyze depth of field quality based on settings."""
        dof_score = 50.0  # Base score
        
        # Calculate depth of field based on aperture and subject distance
        fnumber = exif.get('fnumber')
        focal_length = exif.get('focallength')
        subject_distance = exif.get('subjectdistance') or exif.get('focusdistance')
        
        if fnumber and focal_length:
            try:
                aperture = float(fnumber)
                fl = float(focal_length)
                
                # Depth of field estimation (simplified)
                if subject_distance:
                    distance = float(subject_distance)
                    # Calculate approximate DoF
                    dof = (2 * aperture * (distance ** 2) * 0.03) / (fl ** 2)
                    
                    # Score based on appropriate DoF for portrait vs landscape
                    if fl >= 50:  # Telephoto (often portrait)
                        if 0.1 <= dof <= 2.0:  # Nice portrait separation
                            dof_score = 90
                        elif 2.0 < dof <= 5.0:
                            dof_score = 80
                        elif dof > 5.0:
                            dof_score = 70  # Too much DoF for telephoto
                    else:  # Wide angle (often landscape)
                        if dof >= 5.0:  # Good landscape DoF
                            dof_score = 90
                        elif 2.0 <= dof < 5.0:
                            dof_score = 80
                        else:
                            dof_score = 60  # Too shallow for wide angle
                else:
                    # Estimate based on aperture alone
                    if 2.8 <= aperture <= 5.6:
                        dof_score = 85  # Good general purpose DoF
                    elif 1.4 <= aperture < 2.8:
                        dof_score = 75  # Shallow, but artistic
                    elif 5.6 < aperture <= 11.0:
                        dof_score = 80  # Deeper focus
                    else:
                        dof_score = 70  # Extreme aperture
                        
            except (ValueError, TypeError):
                pass
        
        return min(100.0, dof_score)
    
    def _calculate_focus_score(self, af_analysis: Dict[str, Any], 
                              focus_mode_score: float, face_analysis: Dict[str, Any],
                              sharpness_score: float, dof_score: float) -> float:
        """Calculate overall focus score."""
        # Weight the different components
        af_score = min(100.0, (af_analysis['points_in_focus'] / max(1, af_analysis['points_used'])) * 100)
        
        weighted_score = (
            af_score * 0.3 +
            focus_mode_score * 0.2 +
            (90 if face_analysis['eyes_in_focus'] and face_analysis['face_detected'] else 50) * 0.25 +
            sharpness_score * 0.15 +
            dof_score * 0.1
        )
        
        return min(100.0, weighted_score)
    
    def _generate_focus_recommendations(self, af_analysis: Dict[str, Any],
                                       focus_mode_score: float, face_analysis: Dict[str, Any],
                                       sharpness_score: float, overall_score: float) -> List[str]:
        """Generate focus-related recommendations."""
        recommendations = []
        
        if af_analysis['points_in_focus'] < af_analysis['points_used']:
            recommendations.append("Some AF points not in focus - consider single-point AF")
        
        if focus_mode_score < 70:
            recommendations.append("Consider using more reliable AF mode (AF-S or AF-C)")
        
        if face_analysis['face_detected'] and not face_analysis['eyes_in_focus']:
            recommendations.append("Enable eye AF for portraits to improve focus accuracy")
        
        if sharpness_score < 60:
            recommendations.append("Consider using faster shutter speed or image stabilization")
        
        if overall_score < 70:
            recommendations.append("Focus quality below average - review focus technique")
        elif overall_score >= 90:
            recommendations.append("Excellent focus quality - suitable for large prints")
        
        return recommendations

class ExposureAnalyzer:
    """Advanced exposure quality analyzer."""
    
    def __init__(self):
        # Exposure quality thresholds
        self.good_exposure_range = (-0.5, 0.5)  # EV
        self.acceptable_exposure_range = (-1.0, 1.0)  # EV
    
    def analyze_exposure(self, photo_metadata: Dict[str, Any]) -> ExposureAnalysis:
        """
        Perform comprehensive exposure analysis.
        
        Args:
            photo_metadata: Photo EXIF and metadata dictionary
            
        Returns:
            ExposureAnalysis with detailed results
        """
        exif = photo_metadata.get('exif', {})
        
        # Analyze exposure settings
        exposure_settings = self._analyze_exposure_settings(exif)
        
        # Estimate histogram balance (based on settings)
        histogram_score = self._estimate_histogram_balance(exif, exposure_settings)
        
        # Dynamic range estimation
        dynamic_range = self._estimate_dynamic_range(exif)
        
        # Highlight and shadow analysis
        highlight_analysis = self._analyze_highlights(exif)
        shadow_analysis = self._analyze_shadows(exif)
        
        # Calculate overall exposure score
        overall_score = self._calculate_exposure_score(
            exposure_settings, histogram_score, dynamic_range, 
            highlight_analysis, shadow_analysis
        )
        
        # Determine exposure quality classification
        exposure_quality = self._classify_exposure_quality(
            exposure_settings['compensation'], overall_score
        )
        
        # Generate recommendations
        recommendations = self._generate_exposure_recommendations(
            exposure_settings, overall_score, exposure_quality
        )
        
        return ExposureAnalysis(
            overall_score=overall_score,
            exposure_compensation=exposure_settings['compensation'],
            histogram_balance=histogram_score,
            dynamic_range=dynamic_range,
            highlight_clipping=highlight_analysis,
            shadow_noise=shadow_analysis,
            exposure_quality=exposure_quality,
            exposure_recommendations=recommendations
        )
    
    def _analyze_exposure_settings(self, exif: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze exposure triangle settings."""
        iso = exif.get('isospeedratings') or exif.get('iso') or 100
        aperture = exif.get('fnumber') or 5.6
        shutter_speed = exif.get('exposuretime') or 0.125
        compensation = exif.get('exposurebiasvalue') or 0.0
        
        # Convert to numeric values
        try:
            iso_val = float(iso)
        except (ValueError, TypeError):
            iso_val = 100
        
        try:
            aperture_val = float(aperture)
        except (ValueError, TypeError):
            aperture_val = 5.6
        
        try:
            shutter_val = float(shutter_speed)
        except (ValueError, TypeError):
            shutter_val = 0.125
        
        try:
            comp_val = float(compensation)
        except (ValueError, TypeError):
            comp_val = 0.0
        
        # Calculate exposure value (EV)
        ev = np.log2((aperture_val ** 2) / shutter_val) - np.log2(iso_val / 100)
        
        return {
            'iso': iso_val,
            'aperture': aperture_val,
            'shutter_speed': shutter_val,
            'compensation': comp_val,
            'ev': ev
        }
    
    def _estimate_histogram_balance(self, exif: Dict[str, Any], 
                                  exposure_settings: Dict[str, Any]) -> float:
        """Estimate histogram balance based on exposure settings."""
        base_score = 50.0
        
        # Check exposure compensation
        comp = exposure_settings['compensation']
        if self.good_exposure_range[0] <= comp <= self.good_exposure_range[1]:
            base_score += 30
        elif self.acceptable_exposure_range[0] <= comp <= self.acceptable_exposure_range[1]:
            base_score += 15
        else:
            base_score -= 20
        
        # Consider metering mode
        metering_mode = exif.get('meteringmode')
        if metering_mode:
            metering_str = str(metering_mode).upper()
            if 'MULTI' in metering_str or 'EVALUATIVE' in metering_str:
                base_score += 10
            elif 'CENTER' in metering_str or 'SPOT' in metering_str:
                base_score += 5
        
        # Scene type considerations
        scene_type = exif.get('scenecapturetype')
        if scene_type:
            scene_str = str(scene_type).upper()
            if 'LANDSCAPE' in scene_str:
                # Landscape prefers slight underexposure for detail
                if comp < 0:
                    base_score += 5
            elif 'PORTRAIT' in scene_str:
                # Portrait prefers slight overexposure for skin tones
                if comp > 0:
                    base_score += 5
        
        return min(100.0, max(0.0, base_score))
    
    def _estimate_dynamic_range(self, exif: Dict[str, Any]) -> float:
        """Estimate dynamic range utilization."""
        dr_score = 50.0
        
        # Camera model affects dynamic range
        make = exif.get('make', '').upper()
        model = exif.get('model', '').upper()
        
        # Modern cameras have better dynamic range
        if any(brand in make for brand in ['SONY', 'CANON', 'NIKON', 'FUJIFILM']):
            if any(series in model for series in ['R5', 'R6', 'Z7', 'Z9', 'A7R', 'A9', 'S1']):
                dr_score = 90
            elif any(series in model for series in ['R', 'Z6', 'Z5', 'A7', 'XT']):
                dr_score = 80
            else:
                dr_score = 70
        
        # ISO affects dynamic range
        iso = exif.get('isospeedratings') or exif.get('iso')
        if iso:
            try:
                iso_val = float(iso)
                if iso_val <= 100:
                    dr_score += 10
                elif iso_val <= 400:
                    dr_score += 5
                elif iso_val > 1600:
                    dr_score -= min(30, (iso_val - 1600) / 100)
            except (ValueError, TypeError):
                pass
        
        # Raw files have more dynamic range than JPEG
        if 'RAW' in model or 'RAW' in str(exif.get('fileformat', '')):
            dr_score += 15
        
        return min(100.0, max(0.0, dr_score))
    
    def _analyze_highlights(self, exif: Dict[str, Any]) -> float:
        """Analyze potential highlight clipping."""
        # Based on exposure settings, estimate highlight risk
        exposure_settings = self._analyze_exposure_settings(exif)
        
        highlight_risk = 0.0
        
        # Overexposure compensation increases highlight risk
        if exposure_settings['compensation'] > 0:
            highlight_risk += exposure_settings['compensation'] * 20
        
        # Wide open aperture can increase highlight risk in bright conditions
        if exposure_settings['aperture'] < 2.8:
            highlight_risk += 10
        
        # High ISO in bright conditions can cause highlight issues
        if exposure_settings['iso'] > 1600:
            highlight_risk += 10
        
        # Scene type affects highlight risk
        scene_type = exif.get('scenecapturetype')
        if scene_type:
            scene_str = str(scene_type).upper()
            if 'BEACH' in scene_str or 'SNOW' in scene_str:
                highlight_risk += 20  # High reflectance scenes
            elif 'NIGHT' in scene_str or 'LOW LIGHT' in scene_str:
                highlight_risk -= 10  # Low light scenes
        
        # Convert risk to clipping score (lower is better)
        clipping_score = max(0, 100 - highlight_risk)
        return clipping_score
    
    def _analyze_shadows(self, exif: Dict[str, Any]) -> float:
        """Analyze shadow noise potential."""
        # Based on ISO and exposure settings
        exposure_settings = self._analyze_exposure_settings(exif)
        
        noise_risk = 0.0
        
        # High ISO increases shadow noise
        if exposure_settings['iso'] > 800:
            noise_risk += (exposure_settings['iso'] - 800) / 100
        
        # Underexposure compensation increases shadow noise
        if exposure_settings['compensation'] < -1.0:
            noise_risk += abs(exposure_settings['compensation']) * 15
        
        # Small aperture can increase diffraction affecting shadows
        if exposure_settings['aperture'] > 11.0:
            noise_risk += 10
        
        # Fast shutter in low light can cause underexposure
        if exposure_settings['shutter_speed'] > 1/1000 and exposure_settings['iso'] < 400:
            noise_risk += 15
        
        # Convert risk to noise score (higher is better)
        noise_score = max(0, 100 - noise_risk)
        return noise_score
    
    def _calculate_exposure_score(self, exposure_settings: Dict[str, Any],
                                 histogram_score: float, dynamic_range: float,
                                 highlight_score: float, shadow_score: float) -> float:
        """Calculate overall exposure score."""
        # Weight the different components
        overall_score = (
            histogram_score * 0.3 +
            dynamic_range * 0.2 +
            highlight_score * 0.25 +
            shadow_score * 0.25
        )
        
        # Bonus for good exposure triangle balance
        iso_score = max(0, 100 - abs(exposure_settings['iso'] - 200) / 10)
        aperture_score = 100 - abs(exposure_settings['aperture'] - 5.6) * 5
        shutter_score = 100 - abs(exposure_settings['shutter_speed'] - 0.125) * 50
        
        bonus_score = (iso_score + aperture_score + shutter_score) / 3 * 0.1
        
        overall_score += bonus_score
        
        return min(100.0, max(0.0, overall_score))
    
    def _classify_exposure_quality(self, compensation: float, score: float) -> str:
        """Classify overall exposure quality."""
        if score >= 80:
            return "properly_exposed"
        elif compensation > 0.5:
            return "overexposed"
        elif compensation < -0.5:
            return "underexposed"
        else:
            return "properly_exposed"  # Minor compensation is acceptable
    
    def _generate_exposure_recommendations(self, exposure_settings: Dict[str, Any],
                                         score: float, quality: str) -> List[str]:
        """Generate exposure-related recommendations."""
        recommendations = []
        
        if quality == "overexposed":
            recommendations.append("Reduce exposure compensation or use faster shutter")
        elif quality == "underexposed":
            recommendations.append("Increase exposure compensation or use slower shutter")
        
        if exposure_settings['iso'] > 1600:
            recommendations.append("High ISO - consider more light or slower shutter")
        
        if abs(exposure_settings['compensation']) > 1.0:
            recommendations.append("Large exposure compensation - adjust metering")
        
        if score >= 85:
            recommendations.append("Excellent exposure quality")
        elif score < 60:
            recommendations.append("Exposure needs improvement - review settings")
        
        return recommendations

# Convenience functions
def analyze_focus_quality(photo_metadata: Dict[str, Any]) -> FocusAnalysis:
    """Analyze focus quality for a single photo."""
    analyzer = FocusAnalyzer()
    return analyzer.analyze_focus(photo_metadata)

def analyze_exposure_quality(photo_metadata: Dict[str, Any]) -> ExposureAnalysis:
    """Analyze exposure quality for a single photo."""
    analyzer = ExposureAnalyzer()
    return analyzer.analyze_exposure(photo_metadata)

def get_focus_and_exposure_scores(photo_metadata: Dict[str, Any]) -> Tuple[float, float]:
    """Get simplified focus and exposure scores."""
    focus_analysis = analyze_focus_quality(photo_metadata)
    exposure_analysis = analyze_exposure_quality(photo_metadata)
    
    return focus_analysis.overall_score, exposure_analysis.overall_score