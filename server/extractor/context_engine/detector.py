"""
Context Detector - Main Entry Point

Coordinates multiple analyzers to detect the most appropriate context
for a given file, enabling dynamic UI adaptation.
"""

import os
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

from .analyzer import FileTypeAnalyzer, MetadataPatternAnalyzer, AnalysisResult
from .profiles import CONTEXT_PROFILES, get_profile_for_context, ContextProfile


@dataclass
class ContextDetectionResult:
    """Result of context detection with confidence and evidence"""
    context_type: str
    confidence: float
    confidence_level: str  # 'high', 'medium', 'low'
    profile: ContextProfile
    evidence: Dict[str, Any]
    alternative_contexts: List[Tuple[str, float]]
    detection_time_ms: float
    is_fallback: bool = False


class ContextDetector:
    """
    Main context detection engine that coordinates multiple analyzers
    to determine the most appropriate context for a file.

    Usage:
        detector = ContextDetector()
        result = detector.detect(file_path, metadata)
        print(f"Context: {result.context_type} ({result.confidence:.0%})")
    """

    # Weights for different analyzers
    ANALYZER_WEIGHTS = {
        'MetadataPatternAnalyzer': 0.5,  # Metadata patterns are most reliable
        'FileTypeAnalyzer': 0.3,         # File type is a good baseline
        'ContentAnalyzer': 0.2,          # Content analysis (if available)
    }

    # Confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        'high': 0.75,
        'medium': 0.50,
        'low': 0.30,
    }

    # Conflict resolution rules: (context1, context2) -> winner
    # More specific contexts win over generic ones
    CONFLICT_RULES = {
        ('smartphone_photo', 'generic_photo'): 'smartphone_photo',
        ('dslr_photo', 'generic_photo'): 'dslr_photo',
        ('drone_photo', 'generic_photo'): 'drone_photo',
        ('drone_photo', 'smartphone_photo'): 'drone_photo',
        ('action_camera_photo', 'generic_photo'): 'action_camera_photo',
        ('dicom_medical', 'generic_photo'): 'dicom_medical',
        ('astronomy_fits', 'generic_photo'): 'astronomy_fits',
        ('geospatial', 'generic_photo'): 'geospatial',
        ('ai_generated', 'edited_image'): 'ai_generated',
        ('ai_generated', 'generic_photo'): 'ai_generated',
        ('edited_image', 'generic_photo'): 'edited_image',
        ('screenshot', 'generic_photo'): 'screenshot',
    }

    def __init__(self):
        self.file_type_analyzer = FileTypeAnalyzer()
        self.metadata_analyzer = MetadataPatternAnalyzer()
        self._cache: Dict[str, ContextDetectionResult] = {}
        self._cache_ttl = 300  # 5 minutes

    def detect(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict] = None
    ) -> ContextDetectionResult:
        """
        Detect the context for a file.

        Args:
            file_path: Path to the file
            metadata: Pre-extracted metadata (optional, will extract if not provided)
            user_profile: User preferences for personalization (optional)

        Returns:
            ContextDetectionResult with context type, confidence, and evidence
        """
        start_time = time.time()

        # Check cache
        cache_key = self._get_cache_key(file_path, metadata)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # Return cached result if still valid
            if time.time() - cached.detection_time_ms < self._cache_ttl * 1000:
                return cached

        # Run analyzers
        results: List[AnalysisResult] = []

        # File type analysis (always runs)
        file_result = self.file_type_analyzer.analyze(file_path, user_profile)
        results.append(file_result)

        # Metadata pattern analysis (if metadata provided)
        if metadata:
            metadata_result = self.metadata_analyzer.analyze(file_path, metadata, user_profile)
            results.append(metadata_result)

        # Combine results
        combined_scores = self._combine_scores(results)

        # Resolve conflicts
        final_context, final_score = self._resolve_context(combined_scores)

        # Get confidence level
        confidence_level = self._get_confidence_level(final_score)

        # Get alternative contexts
        alternatives = [
            (ctx, score) for ctx, score in sorted(
                combined_scores.items(), key=lambda x: x[1], reverse=True
            )
            if ctx != final_context
        ][:3]

        # Build evidence
        evidence = {}
        for result in results:
            evidence[result.analyzer_name] = result.evidence

        # Get profile
        profile = get_profile_for_context(final_context)

        detection_time = (time.time() - start_time) * 1000

        result = ContextDetectionResult(
            context_type=final_context,
            confidence=final_score,
            confidence_level=confidence_level,
            profile=profile,
            evidence=evidence,
            alternative_contexts=alternatives,
            detection_time_ms=detection_time,
            is_fallback=final_score < self.CONFIDENCE_THRESHOLDS['low']
        )

        # Cache result
        self._cache[cache_key] = result

        return result

    def _combine_scores(self, results: List[AnalysisResult]) -> Dict[str, float]:
        """Combine scores from multiple analyzers using weighted average"""
        combined: Dict[str, float] = {}

        for result in results:
            weight = self.ANALYZER_WEIGHTS.get(result.analyzer_name, 0.1)
            for context, score in result.scores.items():
                combined[context] = combined.get(context, 0) + score * weight

        # Normalize scores to 0-1 range
        if combined:
            max_score = max(combined.values())
            if max_score > 1:
                combined = {k: v / max_score for k, v in combined.items()}

        return combined

    def _resolve_context(self, scores: Dict[str, float]) -> Tuple[str, float]:
        """Resolve conflicts and determine final context"""
        if not scores:
            return 'generic_file', 0.0

        # Sort by score
        sorted_contexts = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_contexts) == 1:
            return sorted_contexts[0]

        top_context, top_score = sorted_contexts[0]
        second_context, second_score = sorted_contexts[1]

        # Check for conflicts
        conflict_key = tuple(sorted([top_context, second_context]))

        if conflict_key in self.CONFLICT_RULES:
            winner = self.CONFLICT_RULES[conflict_key]
            return winner, scores[winner]

        # If scores are close, prefer more specific context
        if top_score - second_score < 0.1:
            # Check if either is a generic context
            generic_contexts = {'generic_photo', 'generic_video', 'generic_document', 'generic_file'}
            if top_context in generic_contexts and second_context not in generic_contexts:
                return second_context, second_score

        return top_context, top_score

    def _get_confidence_level(self, score: float) -> str:
        """Convert numeric score to confidence level"""
        if score >= self.CONFIDENCE_THRESHOLDS['high']:
            return 'high'
        elif score >= self.CONFIDENCE_THRESHOLDS['medium']:
            return 'medium'
        elif score >= self.CONFIDENCE_THRESHOLDS['low']:
            return 'low'
        else:
            return 'uncertain'

    def _get_cache_key(self, file_path: str, metadata: Optional[Dict]) -> str:
        """Generate cache key for a file"""
        try:
            stat = os.stat(file_path)
            file_key = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
        except OSError:
            file_key = file_path

        if metadata:
            # Include hash of key metadata fields
            key_fields = ['Make', 'Model', 'Software', 'FileType']
            meta_str = '|'.join(str(metadata.get(f, '')) for f in key_fields)
            file_key += f":{hashlib.md5(meta_str.encode()).hexdigest()[:8]}"

        return file_key

    def detect_batch(
        self,
        files: List[Tuple[str, Optional[Dict[str, Any]]]],
        max_workers: int = 4
    ) -> List[ContextDetectionResult]:
        """
        Detect context for multiple files in parallel.

        Args:
            files: List of (file_path, metadata) tuples
            max_workers: Maximum parallel workers

        Returns:
            List of ContextDetectionResult for each file
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(
                lambda x: self.detect(x[0], x[1]),
                files
            ))
        return results

    def clear_cache(self):
        """Clear the detection cache"""
        self._cache.clear()


# Convenience function for simple usage
def detect_file_context(
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> ContextDetectionResult:
    """
    Detect context for a single file.

    This is a convenience function that creates a detector and runs detection.
    For multiple files, use ContextDetector directly for better performance.

    Args:
        file_path: Path to the file
        metadata: Pre-extracted metadata (optional)

    Returns:
        ContextDetectionResult
    """
    detector = ContextDetector()
    return detector.detect(file_path, metadata)


# Export for API integration
def get_context_for_api(
    file_path: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get context detection result formatted for API response.

    Args:
        file_path: Path to the file
        metadata: Extracted metadata

    Returns:
        Dictionary with context info for frontend
    """
    result = detect_file_context(file_path, metadata)

    return {
        'context_type': result.context_type,
        'confidence': result.confidence,
        'confidence_level': result.confidence_level,
        'is_fallback': result.is_fallback,
        'detection_time_ms': result.detection_time_ms,
        'profile': {
            'display_name': result.profile.display_name,
            'description': result.profile.description,
            'ui_template': result.profile.ui_template,
            'icon': result.profile.icon,
            'color': result.profile.color,
            'priority_fields': result.profile.priority_fields,
            'special_components': result.profile.special_components,
            'field_groups': result.profile.field_groups,
        },
        'alternative_contexts': [
            {'context_type': ctx, 'confidence': conf}
            for ctx, conf in result.alternative_contexts
        ],
        'evidence': result.evidence,
    }
