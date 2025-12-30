"""
File Analysis Components for Context Detection

Provides specialized analyzers for different aspects of file analysis:
- FileTypeAnalyzer: Basic file type and MIME detection
- MetadataPatternAnalyzer: Pattern-based context detection from metadata
"""

import os
import re
import mimetypes
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Try to import optional dependencies
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class AnalysisResult:
    """Result from an analyzer with context scores"""
    scores: Dict[str, float]  # context_type -> confidence score (0-1)
    evidence: Dict[str, Any]  # Supporting evidence for the detection
    analyzer_name: str


class FileTypeAnalyzer:
    """
    Analyzes file type based on extension, magic bytes, and MIME type.
    This is the first layer of context detection.
    """

    # File extension to context mappings
    EXTENSION_CONTEXT_MAP: Dict[str, List[Tuple[str, float]]] = {
        # Image formats
        '.jpg': [('generic_photo', 0.5)],
        '.jpeg': [('generic_photo', 0.5)],
        '.png': [('generic_photo', 0.4), ('screenshot', 0.3)],
        '.heic': [('smartphone_photo', 0.7)],
        '.heif': [('smartphone_photo', 0.7)],
        '.webp': [('generic_photo', 0.4)],
        '.tiff': [('dslr_photo', 0.4), ('geospatial', 0.3)],
        '.tif': [('dslr_photo', 0.4), ('geospatial', 0.3)],
        '.dng': [('dslr_photo', 0.8)],
        '.raw': [('dslr_photo', 0.8)],
        '.cr2': [('dslr_photo', 0.9)],
        '.cr3': [('dslr_photo', 0.9)],
        '.nef': [('dslr_photo', 0.9)],
        '.arw': [('dslr_photo', 0.9)],
        '.orf': [('dslr_photo', 0.9)],
        '.rw2': [('dslr_photo', 0.9)],

        # Video formats
        '.mp4': [('generic_video', 0.5)],
        '.mov': [('generic_video', 0.5), ('smartphone_photo', 0.3)],
        '.avi': [('generic_video', 0.5)],
        '.mkv': [('generic_video', 0.5)],

        # Specialized formats
        '.dcm': [('dicom_medical', 0.95)],
        '.dicom': [('dicom_medical', 0.95)],
        '.fits': [('astronomy_fits', 0.95)],
        '.fit': [('astronomy_fits', 0.95)],
        '.fts': [('astronomy_fits', 0.95)],

        # Documents
        '.pdf': [('generic_document', 0.8)],
        '.doc': [('generic_document', 0.8)],
        '.docx': [('generic_document', 0.8)],
    }

    # MIME type patterns
    MIME_CONTEXT_MAP: Dict[str, List[Tuple[str, float]]] = {
        'image/jpeg': [('generic_photo', 0.5)],
        'image/png': [('generic_photo', 0.4), ('screenshot', 0.3)],
        'image/heic': [('smartphone_photo', 0.7)],
        'image/heif': [('smartphone_photo', 0.7)],
        'image/tiff': [('dslr_photo', 0.4), ('geospatial', 0.3)],
        'video/mp4': [('generic_video', 0.5)],
        'video/quicktime': [('generic_video', 0.5)],
        'application/dicom': [('dicom_medical', 0.95)],
        'application/fits': [('astronomy_fits', 0.95)],
        'application/pdf': [('generic_document', 0.8)],
    }

    def analyze(self, file_path: str, user_profile: Optional[Dict] = None) -> AnalysisResult:
        """Analyze file and return context scores based on file type"""
        scores: Dict[str, float] = {}
        evidence: Dict[str, Any] = {}

        # Get file extension
        ext = Path(file_path).suffix.lower()
        evidence['extension'] = ext

        # Check extension mapping
        if ext in self.EXTENSION_CONTEXT_MAP:
            for context, score in self.EXTENSION_CONTEXT_MAP[ext]:
                scores[context] = max(scores.get(context, 0), score)

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_file(file_path, mime=True)
            except Exception:
                pass

        if mime_type:
            evidence['mime_type'] = mime_type

            # Check MIME mapping
            if mime_type in self.MIME_CONTEXT_MAP:
                for context, score in self.MIME_CONTEXT_MAP[mime_type]:
                    scores[context] = max(scores.get(context, 0), score)

            # Additional MIME-based heuristics
            if mime_type.startswith('image/'):
                scores['generic_photo'] = max(scores.get('generic_photo', 0), 0.3)
            elif mime_type.startswith('video/'):
                scores['generic_video'] = max(scores.get('generic_video', 0), 0.3)

        # Get file size
        try:
            file_size = os.path.getsize(file_path)
            evidence['file_size'] = file_size

            # Large files might be RAW or specialized formats
            if file_size > 20_000_000:  # > 20MB
                scores['dslr_photo'] = scores.get('dslr_photo', 0) + 0.1
        except Exception:
            pass

        return AnalysisResult(
            scores=scores,
            evidence=evidence,
            analyzer_name='FileTypeAnalyzer'
        )


class MetadataPatternAnalyzer:
    """
    Analyzes metadata patterns to detect file context.
    This is the primary layer for accurate context detection.
    """

    # Smartphone maker patterns
    SMARTPHONE_MAKERS = {
        'apple': 0.9,
        'iphone': 0.95,
        'samsung': 0.85,
        'google': 0.85,
        'pixel': 0.9,
        'huawei': 0.85,
        'xiaomi': 0.85,
        'oneplus': 0.85,
        'oppo': 0.85,
        'vivo': 0.85,
    }

    # DSLR/Mirrorless maker patterns
    DSLR_MAKERS = {
        'canon eos': 0.9,
        'nikon': 0.85,
        'sony alpha': 0.9,
        'sony ilce': 0.9,
        'fujifilm': 0.85,
        'olympus': 0.85,
        'panasonic lumix': 0.85,
        'pentax': 0.85,
        'leica': 0.9,
        'hasselblad': 0.95,
        'phase one': 0.95,
    }

    # Drone maker patterns
    DRONE_MAKERS = {
        'dji': 0.95,
        'mavic': 0.95,
        'phantom': 0.95,
        'parrot': 0.9,
        'autel': 0.9,
        'skydio': 0.9,
    }

    # Action camera patterns
    ACTION_CAM_MAKERS = {
        'gopro': 0.95,
        'dji action': 0.95,
        'dji osmo': 0.9,
        'insta360': 0.9,
    }

    # AI generation software patterns
    AI_SOFTWARE_PATTERNS = [
        (r'midjourney', 'ai_generated', 0.95),
        (r'dall-?e', 'ai_generated', 0.95),
        (r'stable.?diffusion', 'ai_generated', 0.95),
        (r'automatic1111', 'ai_generated', 0.9),
        (r'comfyui', 'ai_generated', 0.9),
        (r'invoke.?ai', 'ai_generated', 0.9),
        (r'leonardo\.ai', 'ai_generated', 0.9),
        (r'firefly', 'ai_generated', 0.85),
    ]

    # Editing software patterns
    EDITING_SOFTWARE_PATTERNS = [
        (r'photoshop', 'edited_image', 0.85),
        (r'lightroom', 'edited_image', 0.85),
        (r'capture.?one', 'edited_image', 0.85),
        (r'darktable', 'edited_image', 0.8),
        (r'rawtherapee', 'edited_image', 0.8),
        (r'gimp', 'edited_image', 0.75),
        (r'affinity.?photo', 'edited_image', 0.85),
        (r'luminar', 'edited_image', 0.85),
    ]

    def analyze(
        self,
        file_path: str,
        metadata: Dict[str, Any],
        user_profile: Optional[Dict] = None
    ) -> AnalysisResult:
        """Analyze metadata and return context scores"""
        scores: Dict[str, float] = {}
        evidence: Dict[str, Any] = {}

        # Flatten metadata for easier searching
        flat_metadata = self._flatten_metadata(metadata)

        # Check for smartphone patterns
        smartphone_score, smartphone_evidence = self._check_smartphone(flat_metadata)
        if smartphone_score > 0:
            scores['smartphone_photo'] = smartphone_score
            evidence['smartphone'] = smartphone_evidence

        # Check for DSLR patterns
        dslr_score, dslr_evidence = self._check_dslr(flat_metadata)
        if dslr_score > 0:
            scores['dslr_photo'] = dslr_score
            evidence['dslr'] = dslr_evidence

        # Check for drone patterns
        drone_score, drone_evidence = self._check_drone(flat_metadata)
        if drone_score > 0:
            scores['drone_photo'] = drone_score
            evidence['drone'] = drone_evidence

        # Check for action camera patterns
        action_score, action_evidence = self._check_action_camera(flat_metadata)
        if action_score > 0:
            scores['action_camera_photo'] = action_score
            evidence['action_camera'] = action_evidence

        # Check for AI-generated content
        ai_score, ai_evidence = self._check_ai_generated(flat_metadata)
        if ai_score > 0:
            scores['ai_generated'] = ai_score
            evidence['ai_generated'] = ai_evidence

        # Check for edited images
        edited_score, edited_evidence = self._check_edited(flat_metadata)
        if edited_score > 0:
            scores['edited_image'] = edited_score
            evidence['edited'] = edited_evidence

        # Check for screenshot indicators
        screenshot_score = self._check_screenshot(flat_metadata)
        if screenshot_score > 0:
            scores['screenshot'] = screenshot_score

        # Check for specialized formats (DICOM, FITS, etc.)
        specialized_score, specialized_context = self._check_specialized(flat_metadata)
        if specialized_score > 0 and specialized_context:
            scores[specialized_context] = specialized_score

        return AnalysisResult(
            scores=scores,
            evidence=evidence,
            analyzer_name='MetadataPatternAnalyzer'
        )

    def _flatten_metadata(self, metadata: Dict[str, Any], prefix: str = '') -> Dict[str, str]:
        """Flatten nested metadata dict to string values for pattern matching"""
        result = {}

        for key, value in metadata.items():
            if key.startswith('_'):
                continue

            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                result.update(self._flatten_metadata(value, f"{full_key}."))
            elif isinstance(value, (list, tuple)):
                result[full_key] = ' '.join(str(v) for v in value)
            else:
                result[full_key] = str(value)

        return result

    def _check_smartphone(self, metadata: Dict[str, str]) -> Tuple[float, Dict]:
        """Check for smartphone camera patterns"""
        score = 0.0
        evidence = {}

        # Check Make/Model fields
        make = metadata.get('Make', '').lower()
        model = metadata.get('Model', '').lower()
        software = metadata.get('Software', '').lower()

        for pattern, pattern_score in self.SMARTPHONE_MAKERS.items():
            if pattern in make or pattern in model:
                score = max(score, pattern_score)
                evidence['maker_match'] = pattern

        # Check for computational photography indicators
        computational_indicators = [
            'hdr', 'portrait', 'night mode', 'deep fusion',
            'smart hdr', 'scene optimizer', 'ai camera'
        ]

        for indicator in computational_indicators:
            for key, value in metadata.items():
                if indicator in key.lower() or indicator in value.lower():
                    score = max(score, 0.8)
                    evidence['computational'] = indicator
                    break

        # Check for Live Photo / Motion Photo
        if any('livephoto' in k.lower() or 'motionphoto' in k.lower() for k in metadata.keys()):
            score = max(score, 0.85)
            evidence['live_photo'] = True

        # Check for depth data
        if any('depth' in k.lower() for k in metadata.keys()):
            score = max(score, 0.8)
            evidence['depth_data'] = True

        return score, evidence

    def _check_dslr(self, metadata: Dict[str, str]) -> Tuple[float, Dict]:
        """Check for DSLR/Mirrorless camera patterns"""
        score = 0.0
        evidence = {}

        make = metadata.get('Make', '').lower()
        model = metadata.get('Model', '').lower()
        combined = f"{make} {model}"

        for pattern, pattern_score in self.DSLR_MAKERS.items():
            if pattern in combined:
                score = max(score, pattern_score)
                evidence['maker_match'] = pattern

        # Shutter count is a strong indicator
        if 'ShutterCount' in metadata or 'ImageCount' in metadata:
            score = max(score, 0.85)
            evidence['shutter_count'] = True

        # Serial number presence
        if 'SerialNumber' in metadata or 'InternalSerialNumber' in metadata:
            score = max(score, 0.7)
            evidence['serial_number'] = True

        # Lens information
        if 'LensModel' in metadata or 'LensID' in metadata:
            score = max(score, 0.6)
            evidence['lens_info'] = True

        return score, evidence

    def _check_drone(self, metadata: Dict[str, str]) -> Tuple[float, Dict]:
        """Check for drone/aerial photography patterns"""
        score = 0.0
        evidence = {}

        make = metadata.get('Make', '').lower()
        model = metadata.get('Model', '').lower()
        combined = f"{make} {model}"

        for pattern, pattern_score in self.DRONE_MAKERS.items():
            if pattern in combined:
                score = max(score, pattern_score)
                evidence['maker_match'] = pattern

        # Check for flight-specific metadata
        flight_indicators = [
            'flightaltitude', 'relativealtitude', 'gimbal',
            'flightspeed', 'flightroll', 'flightpitch', 'flightyaw',
            'dronemodel', 'aircraft'
        ]

        for indicator in flight_indicators:
            if any(indicator in k.lower() for k in metadata.keys()):
                score = max(score, 0.9)
                evidence['flight_data'] = indicator
                break

        # Check for XMP drone data
        xmp_drone_namespaces = ['drone-dji', 'camera:isflightselfie']
        for ns in xmp_drone_namespaces:
            if any(ns.lower() in k.lower() for k in metadata.keys()):
                score = max(score, 0.95)
                evidence['xmp_drone'] = ns

        return score, evidence

    def _check_action_camera(self, metadata: Dict[str, str]) -> Tuple[float, Dict]:
        """Check for action camera patterns"""
        score = 0.0
        evidence = {}

        make = metadata.get('Make', '').lower()
        model = metadata.get('Model', '').lower()
        combined = f"{make} {model}"

        for pattern, pattern_score in self.ACTION_CAM_MAKERS.items():
            if pattern in combined:
                score = max(score, pattern_score)
                evidence['maker_match'] = pattern

        # Check for motion/sensor data
        sensor_indicators = ['accelerometer', 'gyroscope', 'gps speed']
        for indicator in sensor_indicators:
            if any(indicator in k.lower() for k in metadata.keys()):
                score = max(score, 0.8)
                evidence['sensor_data'] = indicator

        return score, evidence

    def _check_ai_generated(self, metadata: Dict[str, str]) -> Tuple[float, Dict]:
        """Check for AI-generated content patterns"""
        score = 0.0
        evidence = {}

        # Check all metadata values against AI patterns
        all_values = ' '.join(metadata.values()).lower()

        for pattern, context, pattern_score in self.AI_SOFTWARE_PATTERNS:
            if re.search(pattern, all_values, re.IGNORECASE):
                score = max(score, pattern_score)
                evidence['software_match'] = pattern

        # Check for AI-specific XMP fields
        ai_xmp_indicators = ['prompt', 'negative_prompt', 'cfg_scale', 'sampler', 'seed']
        for indicator in ai_xmp_indicators:
            if any(indicator in k.lower() for k in metadata.keys()):
                score = max(score, 0.9)
                evidence['ai_metadata'] = indicator

        # Check for C2PA AI content credentials
        if any('c2pa' in k.lower() and 'ai' in str(metadata.get(k, '')).lower() for k in metadata.keys()):
            score = max(score, 0.95)
            evidence['c2pa_ai'] = True

        return score, evidence

    def _check_edited(self, metadata: Dict[str, str]) -> Tuple[float, Dict]:
        """Check for edited image patterns"""
        score = 0.0
        evidence = {}

        software = metadata.get('Software', '').lower()

        for pattern, context, pattern_score in self.EDITING_SOFTWARE_PATTERNS:
            if re.search(pattern, software, re.IGNORECASE):
                score = max(score, pattern_score)
                evidence['software_match'] = pattern

        # Check for edit history
        history_indicators = ['history', 'documentid', 'derivedfrom', 'originaldocumentid']
        for indicator in history_indicators:
            if any(indicator in k.lower() for k in metadata.keys()):
                score = max(score, 0.75)
                evidence['edit_history'] = True

        # Multiple software tags indicate editing chain
        if 'CreatorTool' in metadata and 'Software' in metadata:
            if metadata.get('CreatorTool') != metadata.get('Software'):
                score = max(score, 0.7)
                evidence['software_chain'] = True

        return score, evidence

    def _check_screenshot(self, metadata: Dict[str, str]) -> float:
        """Check for screenshot indicators"""
        score = 0.0

        # Check for typical screenshot dimensions (exact screen resolutions)
        width = metadata.get('ImageWidth', metadata.get('ExifImageWidth', ''))
        height = metadata.get('ImageHeight', metadata.get('ExifImageHeight', ''))

        common_resolutions = [
            ('1920', '1080'), ('2560', '1440'), ('3840', '2160'),  # Desktop
            ('1125', '2436'), ('1170', '2532'), ('1284', '2778'),  # iPhone
            ('1080', '2400'), ('1440', '3200'),  # Android
        ]

        for w, h in common_resolutions:
            if str(width) == w and str(height) == h:
                score = max(score, 0.6)
                break

        # PNG with no camera metadata is likely screenshot
        if not metadata.get('Make') and not metadata.get('Model'):
            if not metadata.get('ExposureTime') and not metadata.get('FNumber'):
                score = max(score, 0.5)

        # Check for screenshot-related software
        screenshot_software = ['screenshot', 'snipping', 'snip', 'capture', 'grab']
        software = metadata.get('Software', '').lower()
        for sw in screenshot_software:
            if sw in software:
                score = max(score, 0.85)
                break

        return score

    def _check_specialized(self, metadata: Dict[str, str]) -> Tuple[float, Optional[str]]:
        """Check for specialized format indicators"""
        # DICOM indicators
        dicom_tags = ['PatientID', 'StudyDate', 'Modality', 'SOPClassUID']
        if any(tag in metadata for tag in dicom_tags):
            return 0.95, 'dicom_medical'

        # FITS indicators
        fits_tags = ['SIMPLE', 'BITPIX', 'NAXIS', 'TELESCOP', 'INSTRUME']
        if any(tag in metadata for tag in fits_tags):
            return 0.95, 'astronomy_fits'

        # Geospatial indicators
        geo_tags = ['GeoTransform', 'Projection', 'EPSG', 'SRS']
        if any(tag in metadata for tag in geo_tags):
            return 0.9, 'geospatial'

        return 0.0, None
