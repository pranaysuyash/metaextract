"""
AI-Assisted Photo Culling Service
==================================

Automatically selects best shots based on:
- AF/focus scores and sharpness analysis
- Exposure evaluation and histogram analysis  
- Composition and aesthetic scoring
- Face detection and expression analysis
- Technical quality assessment
- User preferences and learning

Author: MetaExtract Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CullingScore:
    """Individual culling score component."""
    focus_score: float
    exposure_score: float
    composition_score: float
    technical_score: float
    aesthetic_score: float
    overall_score: float
    confidence: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization."""
        return {
            'focus_score': self.focus_score,
            'exposure_score': self.exposure_score,
            'composition_score': self.composition_score,
            'technical_score': self.technical_score,
            'aesthetic_score': self.aesthetic_score,
            'overall_score': self.overall_score,
            'confidence': self.confidence
        }

@dataclass
class PhotoGroup:
    """Group of similar photos for culling."""
    group_id: str
    photos: List[Dict[str, Any]]
    similarity_reason: str  # 'time_sequence', 'similar_composition', 'same_subject'
    best_shot_index: Optional[int] = None
    culling_scores: Optional[List[CullingScore]] = None

class AICullingEngine:
    """AI-powered photo culling engine."""
    
    def __init__(self, user_preferences: Optional[Dict[str, Any]] = None):
        self.user_preferences = user_preferences or {}
        self.focus_weight = self.user_preferences.get('focus_weight', 0.3)
        self.exposure_weight = self.user_preferences.get('exposure_weight', 0.25)
        self.composition_weight = self.user_preferences.get('composition_weight', 0.2)
        self.technical_weight = self.user_preferences.get('technical_weight', 0.15)
        self.aesthetic_weight = self.user_preferences.get('aesthetic_weight', 0.1)
        
    def analyze_batch(self, photos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a batch of photos and return culling recommendations.
        
        Args:
            photos: List of photo metadata dictionaries
            
        Returns:
            Dict containing groups, scores, and recommendations
        """
        if not photos:
            return {
                'groups': [],
                'total_photos': 0,
                'recommendations': [],
                'processing_time': 0,
                'success': False,
                'error': 'No photos provided'
            }
        
        start_time = datetime.now()
        
        try:
            # Step 1: Group similar photos
            groups = self._group_similar_photos(photos)
            
            # Step 2: Score each photo
            scored_groups = []
            for group in groups:
                scores = []
                for photo in group.photos:
                    score = self._score_photo(photo)
                    scores.append(score)
                
                group.culling_scores = scores
                group.best_shot_index = self._select_best_shot(scores)
                scored_groups.append(group)
            
            # Step 3: Generate recommendations
            recommendations = self._generate_recommendations(scored_groups)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'groups': [self._group_to_dict(g) for g in scored_groups],
                'total_photos': len(photos),
                'recommendations': recommendations,
                'processing_time': processing_time,
                'success': True,
                'scoring_weights': {
                    'focus': self.focus_weight,
                    'exposure': self.exposure_weight,
                    'composition': self.composition_weight,
                    'technical': self.technical_weight,
                    'aesthetic': self.aesthetic_weight
                }
            }
            
        except Exception as e:
            logger.error(f"Error during batch culling analysis: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'groups': [],
                'total_photos': len(photos),
                'recommendations': [],
                'processing_time': processing_time,
                'success': False,
                'error': str(e)
            }
    
    def _group_similar_photos(self, photos: List[Dict[str, Any]]) -> List[PhotoGroup]:
        """Group photos based on similarity."""
        groups = []
        ungrouped = photos.copy()
        
        # Sort by timestamp for time-based grouping
        photos_by_time = sorted(ungrouped, key=lambda p: p.get('exif', {}).get('datetimeoriginal', ''))
        
        current_group = []
        last_timestamp = None
        
        for photo in photos_by_time:
            exif = photo.get('exif', {})
            timestamp = exif.get('datetimeoriginal')
            
            if timestamp:
                try:
                    # Parse timestamp
                    if isinstance(timestamp, str):
                        photo_time = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
                    else:
                        photo_time = timestamp
                    
                    # Group if within 3 seconds
                    if last_timestamp and abs((photo_time - last_timestamp).total_seconds()) <= 3:
                        current_group.append(photo)
                    else:
                        if current_group:
                            groups.append(PhotoGroup(
                                group_id=f"time_sequence_{len(groups)}",
                                photos=current_group,
                                similarity_reason="time_sequence"
                            ))
                        current_group = [photo]
                    
                    last_timestamp = photo_time
                    
                except (ValueError, TypeError):
                    # If timestamp parsing fails, start new group
                    if current_group:
                        groups.append(PhotoGroup(
                            group_id=f"time_sequence_{len(groups)}",
                            photos=current_group,
                            similarity_reason="time_sequence"
                        ))
                    current_group = [photo]
                    last_timestamp = None
            else:
                # No timestamp, individual photo
                if current_group:
                    groups.append(PhotoGroup(
                        group_id=f"time_sequence_{len(groups)}",
                        photos=current_group,
                        similarity_reason="time_sequence"
                    ))
                    current_group = []
                
                groups.append(PhotoGroup(
                    group_id=f"individual_{len(groups)}",
                    photos=[photo],
                    similarity_reason="unique_photo"
                ))
        
        # Add final group
        if current_group:
            groups.append(PhotoGroup(
                group_id=f"time_sequence_{len(groups)}",
                photos=current_group,
                similarity_reason="time_sequence"
            ))
        
        return groups
    
    def _score_photo(self, photo: Dict[str, Any]) -> CullingScore:
        """Score an individual photo across multiple dimensions."""
        
        # Focus score analysis
        focus_score = self._analyze_focus(photo)
        
        # Exposure score analysis
        exposure_score = self._analyze_exposure(photo)
        
        # Composition score analysis
        composition_score = self._analyze_composition(photo)
        
        # Technical quality analysis
        technical_score = self._analyze_technical_quality(photo)
        
        # Aesthetic score analysis
        aesthetic_score = self._analyze_aesthetics(photo)
        
        # Calculate weighted overall score
        overall_score = (
            focus_score * self.focus_weight +
            exposure_score * self.exposure_weight +
            composition_score * self.composition_weight +
            technical_score * self.technical_weight +
            aesthetic_score * self.aesthetic_weight
        )
        
        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(photo, {
            'focus': focus_score,
            'exposure': exposure_score,
            'composition': composition_score,
            'technical': technical_score,
            'aesthetic': aesthetic_score
        })
        
        return CullingScore(
            focus_score=focus_score,
            exposure_score=exposure_score,
            composition_score=composition_score,
            technical_score=technical_score,
            aesthetic_score=aesthetic_score,
            overall_score=overall_score,
            confidence=confidence
        )
    
    def _analyze_focus(self, photo: Dict[str, Any]) -> float:
        """Analyze focus quality from EXIF metadata."""
        exif = photo.get('exif', {})
        focus_score = 50.0  # Default neutral score
        
        # Check focus mode
        focus_mode = exif.get('focusmode') or exif.get('afmode')
        if focus_mode:
            focus_modes_good = ['AF-S', 'Single', 'One Shot', 'AF-C', 'Continuous']
            if any(good_mode in str(focus_mode) for good_mode in focus_modes_good):
                focus_score += 15
        
        # Check AF points
        af_points = exif.get('pointsinfocus') or exif.get('afpoints')
        if af_points:
            if isinstance(af_points, (list, str)):
                if isinstance(af_points, str):
                    try:
                        af_count = int(af_points)
                    except ValueError:
                        af_count = 1
                else:
                    af_count = len(af_points)
                
                if af_count >= 1:
                    focus_score += 10
                if af_count > 1:
                    focus_score += 5
        
        # Check face detection
        face_detected = exif.get('facedetected')
        if face_detected:
            focus_score += 15
        
        # Check focus distance (if available)
        focus_distance = exif.get('focusdistance')
        if focus_distance:
            try:
                distance = float(focus_distance)
                # Reasonable focus distances get higher scores
                if 0.5 <= distance <= 10.0:
                    focus_score += 10
            except (ValueError, TypeError):
                pass
        
        # Lens information
        lens_model = exif.get('lensmodel')
        if lens_model:
            # Professional lenses tend to have better AF
            pro_indicators = ['GM', 'L', 'Art', 'Pro', 'EX', 'DG']
            if any(indicator in str(lens_model) for indicator in pro_indicators):
                focus_score += 10
        
        return min(100.0, focus_score)
    
    def _analyze_exposure(self, photo: Dict[str, Any]) -> float:
        """Analyze exposure quality from EXIF metadata."""
        exif = photo.get('exif', {})
        exposure_score = 50.0  # Default neutral score
        
        # ISO analysis
        iso = exif.get('isospeedratings') or exif.get('iso')
        if iso:
            try:
                iso_val = float(iso)
                if iso_val <= 100:
                    exposure_score += 20  # Base ISO is best
                elif iso_val <= 400:
                    exposure_score += 15
                elif iso_val <= 800:
                    exposure_score += 10
                elif iso_val <= 1600:
                    exposure_score += 5
                else:
                    exposure_score -= 10  # High ISO penalty
            except (ValueError, TypeError):
                pass
        
        # Aperture analysis
        fnumber = exif.get('fnumber')
        if fnumber:
            try:
                aperture = float(fnumber)
                # Sweet spot for most lenses
                if 2.8 <= aperture <= 8.0:
                    exposure_score += 15
                elif 1.4 <= aperture <= 11.0:
                    exposure_score += 10
                else:
                    exposure_score += 5
            except (ValueError, TypeError):
                pass
        
        # Shutter speed analysis
        exposure_time = exif.get('exposuretime')
        if exposure_time:
            try:
                shutter = float(exposure_time)
                # Reasonable shutter speeds
                if 0.001 <= shutter <= 0.5:
                    exposure_score += 15
                elif 0.0001 <= shutter < 0.001:
                    exposure_score += 10  # Fast but acceptable
                elif 0.5 < shutter <= 2.0:
                    exposure_score += 10  # Slow but acceptable
                else:
                    exposure_score += 5
            except (ValueError, TypeError):
                pass
        
        # Exposure compensation
        exposure_bias = exif.get('exposurebiasvalue')
        if exposure_bias:
            try:
                bias = float(exposure_bias)
                # Minimal compensation is good
                if abs(bias) <= 0.3:
                    exposure_score += 10
                elif abs(bias) <= 1.0:
                    exposure_score += 5
                else:
                    exposure_score -= 5  # Heavy compensation
            except (ValueError, TypeError):
                pass
        
        return min(100.0, max(0.0, exposure_score))
    
    def _analyze_composition(self, photo: Dict[str, Any]) -> float:
        """Analyze composition based on available metadata."""
        exif = photo.get('exif', {})
        composition_score = 50.0  # Default neutral score
        
        # Aspect ratio analysis
        width = photo.get('width')
        height = photo.get('height')
        if width and height:
            try:
                aspect_ratio = float(width) / float(height)
                
                # Common artistic aspect ratios
                if abs(aspect_ratio - 1.618) < 0.1:  # Golden ratio
                    composition_score += 20
                elif abs(aspect_ratio - 1.5) < 0.1:  # 3:2
                    composition_score += 15
                elif abs(aspect_ratio - 1.333) < 0.1:  # 4:3
                    composition_score += 10
                elif abs(aspect_ratio - 1.0) < 0.1:  # Square
                    composition_score += 10
                elif abs(aspect_ratio - 2.333) < 0.1:  # 21:9 cinema
                    composition_score += 15
                else:
                    composition_score += 5
            except (ValueError, TypeError):
                pass
        
        # Face detection in composition
        face_detected = exif.get('facedetected')
        face_count = exif.get('facecount')
        if face_detected:
            composition_score += 10
            if face_count:
                try:
                    count = int(face_count)
                    if 1 <= count <= 3:  # Good number of subjects
                        composition_score += 15
                    elif 4 <= count <= 6:
                        composition_score += 10
                    else:
                        composition_score += 5
                except (ValueError, TypeError):
                    pass
        
        # Scene detection
        scene_type = exif.get('scenecapturetype')
        if scene_type:
            # Certain scene types indicate better composition
            good_scenes = ['Portrait', 'Landscape', 'Night Scene']
            if any(scene in str(scene_type) for scene in good_scenes):
                composition_score += 10
        
        return min(100.0, composition_score)
    
    def _analyze_technical_quality(self, photo: Dict[str, Any]) -> float:
        """Analyze technical quality of the photo."""
        exif = photo.get('exif', {})
        technical_score = 50.0  # Default neutral score
        
        # Resolution analysis
        width = photo.get('width')
        height = photo.get('height')
        if width and height:
            try:
                megapixels = float(width) * float(height) / 1_000_000
                
                if megapixels >= 20:
                    technical_score += 25
                elif megapixels >= 12:
                    technical_score += 20
                elif megapixels >= 8:
                    technical_score += 15
                elif megapixels >= 4:
                    technical_score += 10
                else:
                    technical_score += 5
            except (ValueError, TypeError):
                pass
        
        # Color depth
        bits_per_sample = exif.get('bitspersample')
        if bits_per_sample:
            try:
                bits = float(bits_per_sample)
                if bits >= 14:
                    technical_score += 15
                elif bits >= 12:
                    technical_score += 10
                elif bits >= 10:
                    technical_score += 5
            except (ValueError, TypeError):
                pass
        
        # Camera make/model (professional cameras tend to produce better quality)
        make = exif.get('make')
        model = exif.get('model')
        if make and model:
            make_str = str(make).upper()
            model_str = str(model).upper()
            
            # Professional camera indicators
            pro_indicators = ['EOS R', 'EOS-1D', 'D5', 'D850', 'A7R', 'A9', ' GFX', 'Hasselblad', 'Leica']
            if any(indicator in model_str for indicator in pro_indicators):
                technical_score += 15
            elif any(indicator in make_str for indicator in ['CANON', 'NIKON', 'SONY', 'FUJIFILM']):
                technical_score += 10
            else:
                technical_score += 5
        
        # Lens quality
        lens_model = exif.get('lensmodel')
        if lens_model:
            lens_str = str(lens_model).upper()
            pro_lens_indicators = ['GM', 'L', 'ART', 'PRO', 'OTUS', 'MASTER', 'DG']
            if any(indicator in lens_str for indicator in pro_lens_indicators):
                technical_score += 10
        
        return min(100.0, technical_score)
    
    def _analyze_aesthetics(self, photo: Dict[str, Any]) -> float:
        """Analyze aesthetic qualities (limited by metadata)."""
        exif = photo.get('exif', {})
        aesthetic_score = 50.0  # Default neutral score
        
        # Subject distance estimation
        subject_distance = exif.get('subjectdistance')
        if subject_distance:
            try:
                distance = float(subject_distance)
                # Portrait-friendly distances
                if 0.5 <= distance <= 3.0:
                    aesthetic_score += 15
                elif 3.0 < distance <= 10.0:
                    aesthetic_score += 10
            except (ValueError, TypeError):
                pass
        
        # Focal length (affects perspective and aesthetics)
        focal_length = exif.get('focallength')
        if focal_length:
            try:
                fl = float(focal_length)
                # Classic portrait and landscape focal lengths
                if 35 <= fl <= 85:  # Classic range
                    aesthetic_score += 15
                elif 24 <= fl < 35:  # Wide angle
                    aesthetic_score += 10
                elif 85 < fl <= 135:  # Short telephoto
                    aesthetic_score += 10
                else:
                    aesthetic_score += 5
            except (ValueError, TypeError):
                pass
        
        # Flash usage (aesthetic consideration)
        flash = exif.get('flash')
        if flash:
            flash_str = str(flash)
            if 'Off' in flash_str or 'Did not fire' in flash_str:
                aesthetic_score += 10  # Natural light often better
            else:
                aesthetic_score += 5  # Fill flash can be good too
        
        return min(100.0, aesthetic_score)
    
    def _calculate_confidence(self, photo: Dict[str, Any], scores: Dict[str, float]) -> float:
        """Calculate confidence in the scoring based on data completeness."""
        exif = photo.get('exif', {})
        
        # Check availability of key metadata
        available_fields = 0
        total_fields = 0
        
        # Focus-related fields
        focus_fields = ['focusmode', 'afmode', 'pointsinfocus', 'afpoints', 'facedetected']
        total_fields += len(focus_fields)
        for field in focus_fields:
            if exif.get(field):
                available_fields += 1
        
        # Exposure-related fields
        exposure_fields = ['isospeedratings', 'iso', 'fnumber', 'exposuretime', 'exposurebiasvalue']
        total_fields += len(exposure_fields)
        for field in exposure_fields:
            if exif.get(field):
                available_fields += 1
        
        # Composition-related fields
        comp_fields = ['scenecapturetype', 'facecount']
        total_fields += len(comp_fields)
        for field in comp_fields:
            if exif.get(field):
                available_fields += 1
        
        # Basic image properties
        if photo.get('width') and photo.get('height'):
            available_fields += 1
        total_fields += 1
        
        # Calculate base confidence from metadata completeness
        base_confidence = available_fields / total_fields if total_fields > 0 else 0.5
        
        # Adjust based on score consistency
        score_values = list(scores.values())
        if score_values:
            score_std = np.std(score_values)
            # Lower standard deviation = more consistent scoring = higher confidence
            consistency_factor = max(0.5, 1.0 - (score_std / 50.0))
        else:
            consistency_factor = 0.5
        
        # Combine factors
        confidence = (base_confidence * 0.7 + consistency_factor * 0.3)
        
        return min(1.0, max(0.1, confidence))
    
    def _select_best_shot(self, scores: List[CullingScore]) -> int:
        """Select the best shot from a group based on scores."""
        if not scores:
            return 0
        
        # Find the index of the photo with highest overall score
        best_index = 0
        best_score = scores[0].overall_score
        
        for i, score in enumerate(scores):
            # Consider both overall score and confidence
            adjusted_score = score.overall_score * score.confidence
            
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_index = i
        
        return best_index
    
    def _generate_recommendations(self, groups: List[PhotoGroup]) -> List[Dict[str, Any]]:
        """Generate culling recommendations."""
        recommendations = []
        
        for group in groups:
            if len(group.photos) == 1:
                # Single photo recommendations
                score = group.culling_scores[0] if group.culling_scores else None
                if score:
                    rec = {
                        'type': 'single_photo',
                        'group_id': group.group_id,
                        'photo_index': 0,
                        'action': 'keep' if score.overall_score >= 60 else 'review',
                        'reason': self._get_single_photo_reason(score),
                        'score': score.to_dict()
                    }
                    recommendations.append(rec)
            else:
                # Multi-photo group recommendations
                if group.culling_scores and group.best_shot_index is not None:
                    # Keep the best shot
                    best_score = group.culling_scores[group.best_shot_index]
                    rec_keep = {
                        'type': 'group_best',
                        'group_id': group.group_id,
                        'photo_index': group.best_shot_index,
                        'action': 'keep',
                        'reason': f'Best shot in {group.similarity_reason} group',
                        'score': best_score.to_dict()
                    }
                    recommendations.append(rec_keep)
                    
                    # Recommendations for other shots
                    for i, score in enumerate(group.culling_scores):
                        if i != group.best_shot_index:
                            action = self._get_action_for_alternative(score, best_score)
                            rec_alt = {
                                'type': 'group_alternative',
                                'group_id': group.group_id,
                                'photo_index': i,
                                'action': action,
                                'reason': self._get_alternative_reason(score, best_score, group.similarity_reason),
                                'score': score.to_dict()
                            }
                            recommendations.append(rec_alt)
        
        return recommendations
    
    def _get_single_photo_reason(self, score: CullingScore) -> str:
        """Get recommendation reason for single photo."""
        if score.overall_score >= 80:
            return "Excellent quality - highly recommended"
        elif score.overall_score >= 70:
            return "Good quality - recommended"
        elif score.overall_score >= 60:
            return "Acceptable quality - consider keeping"
        elif score.overall_score >= 50:
            return "Below average - review carefully"
        else:
            return "Poor quality - consider culling"
    
    def _get_action_for_alternative(self, alt_score: CullingScore, best_score: CullingScore) -> str:
        """Determine action for alternative photo in group."""
        score_diff = best_score.overall_score - alt_score.overall_score
        
        if score_diff > 20:
            return "cull"
        elif score_diff > 10:
            return "review"
        elif alt_score.overall_score >= 70:
            return "consider"
        else:
            return "review"
    
    def _get_alternative_reason(self, alt_score: CullingScore, best_score: CullingScore, similarity_reason: str) -> str:
        """Get reason for alternative photo recommendation."""
        score_diff = best_score.overall_score - alt_score.overall_score
        
        if score_diff > 15:
            return f"Significantly lower quality than best shot in {similarity_reason}"
        elif score_diff > 8:
            return f"Lower quality than best shot in {similarity_reason}"
        else:
            return f"Similar to best shot in {similarity_reason}"
    
    def _group_to_dict(self, group: PhotoGroup) -> Dict[str, Any]:
        """Convert PhotoGroup to dictionary for JSON serialization."""
        return {
            'group_id': group.group_id,
            'photos': group.photos,
            'similarity_reason': group.similarity_reason,
            'best_shot_index': group.best_shot_index,
            'culling_scores': [s.to_dict() for s in group.culling_scores] if group.culling_scores else None
        }

# Convenience functions
def analyze_photos_for_culling(photos: List[Dict[str, Any]], 
                               user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze photos for AI-assisted culling.
    
    Args:
        photos: List of photo metadata dictionaries
        user_preferences: Optional user preference dictionary
        
    Returns:
        Analysis results with groups, scores, and recommendations
    """
    engine = AICullingEngine(user_preferences)
    return engine.analyze_batch(photos)

def get_culling_recommendations(photos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get simple culling recommendations for a list of photos.
    
    Args:
        photos: List of photo metadata dictionaries
        
    Returns:
        List of recommendation dictionaries
    """
    result = analyze_photos_for_culling(photos)
    return result.get('recommendations', [])

def score_single_photo(photo: Dict[str, Any], 
                      user_preferences: Optional[Dict[str, Any]] = None) -> CullingScore:
    """
    Score a single photo for culling purposes.
    
    Args:
        photo: Photo metadata dictionary
        user_preferences: Optional user preference dictionary
        
    Returns:
        CullingScore object with detailed scoring
    """
    engine = AICullingEngine(user_preferences)
    return engine._score_photo(photo)