"""
AI Culling System Tests and Integration Examples
==============================================

Comprehensive tests and integration examples for the AI-assisted photo culling system:
- Unit tests for scoring algorithms
- Integration tests for batch processing
- Performance benchmarks
- Real-world usage examples

Author: MetaExtract Team
Version: 1.0.0
"""

import pytest
import asyncio
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Import our modules
from ..modules.ai_culling_engine import (
    AICullingEngine, 
    analyze_photos_for_culling,
    score_single_photo,
    CullingScore
)
from ..modules.focus_exposure_analyzer import (
    FocusAnalyzer, 
    ExposureAnalyzer,
    analyze_focus_quality,
    analyze_exposure_quality
)
from ..modules.culling_performance import (
    CullingBatchProcessor,
    BatchConfig,
    CullingOptimizedEngine,
    optimize_culling_performance
)

class TestAICullingEngine:
    """Test cases for the AI Culling Engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AICullingEngine()
        self.sample_photos = self._create_sample_photos()
    
    def _create_sample_photos(self) -> List[Dict[str, Any]]:
        """Create sample photo metadata for testing."""
        return [
            {
                'filename': 'photo1.jpg',
                'filepath': '/test/photo1.jpg',
                'width': 6000,
                'height': 4000,
                'exif': {
                    'isospeedratings': 200,
                    'fnumber': 2.8,
                    'exposuretime': 0.004,
                    'exposurebiasvalue': 0.0,
                    'focusmode': 'AF-S',
                    'pointsinfocus': 1,
                    'facedetected': True,
                    'facecount': 2,
                    'scenecapturetype': 'Portrait',
                    'make': 'Canon',
                    'model': 'EOS R5',
                    'lensmodel': 'RF 50mm f/1.2L USM',
                    'focallength': 50.0,
                    'subjectdistance': 2.5
                }
            },
            {
                'filename': 'photo2.jpg',
                'filepath': '/test/photo2.jpg',
                'width': 6000,
                'height': 4000,
                'exif': {
                    'isospeedratings': 800,
                    'fnumber': 4.0,
                    'exposuretime': 0.002,
                    'exposurebiasvalue': 0.3,
                    'focusmode': 'AF-C',
                    'pointsinfocus': 3,
                    'facedetected': False,
                    'scenecapturetype': 'Landscape',
                    'make': 'Canon',
                    'model': 'EOS R5',
                    'lensmodel': 'RF 24-70mm f/2.8L IS USM',
                    'focallength': 35.0
                }
            },
            {
                'filename': 'photo3.jpg',
                'filepath': '/test/photo3.jpg',
                'width': 4000,
                'height': 3000,
                'exif': {
                    'isospeedratings': 1600,
                    'fnumber': 5.6,
                    'exposuretime': 0.001,
                    'exposurebiasvalue': -1.0,
                    'focusmode': 'Manual',
                    'facedetected': False,
                    'make': 'Nikon',
                    'model': 'D850',
                    'lensmodel': 'AF-S 85mm f/1.8G',
                    'focallength': 85.0
                }
            }
        ]
    
    def test_score_photo_basic(self):
        """Test basic photo scoring functionality."""
        photo = self.sample_photos[0]
        score = self.engine._score_photo(photo)
        
        assert isinstance(score, CullingScore)
        assert 0 <= score.focus_score <= 100
        assert 0 <= score.exposure_score <= 100
        assert 0 <= score.composition_score <= 100
        assert 0 <= score.technical_score <= 100
        assert 0 <= score.aesthetic_score <= 100
        assert 0 <= score.overall_score <= 100
        assert 0 <= score.confidence <= 1
    
    def test_focus_analysis(self):
        """Test focus analysis."""
        # High quality focus photo
        good_focus_photo = {
            'exif': {
                'focusmode': 'AF-S',
                'pointsinfocus': 1,
                'facedetected': True,
                'facecount': 2,
                'fnumber': 2.8,
                'isospeedratings': 200
            },
            'width': 6000,
            'height': 4000
        }
        
        focus_score = self.engine._analyze_focus(good_focus_photo)
        assert focus_score > 70  # Should be high quality
        
        # Poor focus photo
        poor_focus_photo = {
            'exif': {
                'focusmode': 'Manual',
                'pointsinfocus': 0,
                'facedetected': False,
                'fnumber': 16.0,
                'isospeedratings': 3200
            },
            'width': 2000,
            'height': 1500
        }
        
        focus_score_poor = self.engine._analyze_focus(poor_focus_photo)
        assert focus_score_poor < focus_score
    
    def test_exposure_analysis(self):
        """Test exposure analysis."""
        # Good exposure
        good_exposure_photo = {
            'exif': {
                'isospeedratings': 100,
                'fnumber': 5.6,
                'exposuretime': 0.125,
                'exposurebiasvalue': 0.0,
                'meteringmode': 'Multi-segment'
            }
        }
        
        exposure_score = self.engine._analyze_exposure(good_exposure_photo)
        assert exposure_score > 70
        
        # Poor exposure
        poor_exposure_photo = {
            'exif': {
                'isospeedratings': 6400,
                'fnumber': 22.0,
                'exposuretime': 30.0,
                'exposurebiasvalue': -2.0
            }
        }
        
        exposure_score_poor = self.engine._analyze_exposure(poor_exposure_photo)
        assert exposure_score_poor < exposure_score
    
    def test_group_similar_photos(self):
        """Test photo grouping functionality."""
        groups = self.engine._group_similar_photos(self.sample_photos)
        
        assert len(groups) >= 1
        for group in groups:
            assert group.group_id
            assert len(group.photos) >= 1
            assert group.similarity_reason in ['time_sequence', 'unique_photo']
    
    def test_analyze_batch(self):
        """Test batch analysis."""
        result = self.engine.analyze_batch(self.sample_photos)
        
        assert result['success']
        assert result['total_photos'] == len(self.sample_photos)
        assert 'groups' in result
        assert 'recommendations' in result
        assert 'processing_time' in result
        assert 'scoring_weights' in result
    
    def test_user_preferences(self):
        """Test user preference handling."""
        custom_prefs = {
            'focus_weight': 0.5,
            'exposure_weight': 0.3,
            'composition_weight': 0.1,
            'technical_weight': 0.05,
            'aesthetic_weight': 0.05
        }
        
        custom_engine = AICullingEngine(custom_prefs)
        result = custom_engine.analyze_batch(self.sample_photos)
        
        assert result['scoring_weights'] == custom_prefs

class TestFocusAnalyzer:
    """Test cases for Focus Analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FocusAnalyzer()
    
    def test_analyze_focus_with_af_points(self):
        """Test focus analysis with AF points."""
        photo_metadata = {
            'exif': {
                'focusmode': 'AF-S',
                'pointsinfocus': 3,
                'pointsused': 5,
                'facedetected': True,
                'facecount': 2,
                'fnumber': 2.8,
                'exposuretime': 0.125,
                'lensmodel': 'Canon RF 50mm f/1.2L',
                'focallength': 50.0
            },
            'width': 6000,
            'height': 4000
        }
        
        analysis = self.analyzer.analyze_focus(photo_metadata)
        
        assert analysis.overall_score > 70
        assert analysis.af_points_used == 5
        assert analysis.af_points_in_focus == 3
        assert analysis.face_detected
        assert analysis.sharpness_estimate > 50
    
    def test_analyze_focus_manual_mode(self):
        """Test focus analysis with manual focus."""
        photo_metadata = {
            'exif': {
                'focusmode': 'Manual',
                'facedetected': False,
                'fnumber': 8.0,
                'exposuretime': 0.5,
                'lensmodel': 'Tamron 28-75mm f/2.8',
                'focallength': 50.0
            },
            'width': 4000,
            'height': 3000
        }
        
        analysis = self.analyzer.analyze_focus(photo_metadata)
        
        assert analysis.focus_mode_confidence < 80  # Manual focus gets lower confidence
        assert not analysis.face_detected
        assert len(analysis.focus_recommendations) > 0

class TestExposureAnalyzer:
    """Test cases for Exposure Analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ExposureAnalyzer()
    
    def test_perfect_exposure(self):
        """Test analysis of perfectly exposed photo."""
        photo_metadata = {
            'exif': {
                'isospeedratings': 100,
                'fnumber': 5.6,
                'exposuretime': 0.125,
                'exposurebiasvalue': 0.0,
                'meteringmode': 'Evaluative',
                'scenecapturetype': 'Landscape',
                'make': 'Sony',
                'model': 'A7R IV'
            },
            'width': 6000,
            'height': 4000
        }
        
        analysis = self.analyzer.analyze_exposure(photo_metadata)
        
        assert analysis.overall_score > 80
        assert analysis.exposure_quality == 'properly_exposed'
        assert abs(analysis.exposure_compensation) < 0.5
    
    def test_overexposed_photo(self):
        """Test analysis of overexposed photo."""
        photo_metadata = {
            'exif': {
                'isospeedratings': 800,
                'fnumber': 1.4,
                'exposuretime': 0.002,
                'exposurebiasvalue': 1.7,
                'meteringmode': 'Center-weighted'
            },
            'width': 4000,
            'height': 3000
        }
        
        analysis = self.analyzer.analyze_exposure(photo_metadata)
        
        assert analysis.exposure_quality == 'overexposed'
        assert analysis.exposure_compensation > 1.0
        assert analysis.highlight_clipping < 70  # Potential clipping

class TestPerformanceOptimization:
    """Test cases for performance optimization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = BatchConfig(
            batch_size=10,
            max_workers=2,
            use_multiprocessing=False,  # Disable for testing
            memory_limit_mb=512,
            enable_gpu=False
        )
        self.processor = CullingBatchProcessor(self.config)
    
    def _create_large_photo_set(self, count: int = 100) -> List[Dict[str, Any]]:
        """Create a large set of sample photos."""
        photos = []
        for i in range(count):
            photos.append({
                'filename': f'photo_{i:04d}.jpg',
                'filepath': f'/test/photo_{i:04d}.jpg',
                'width': 6000,
                'height': 4000,
                'exif': {
                    'isospeedratings': 200 + (i % 10) * 100,
                    'fnumber': 2.8 + (i % 5) * 0.7,
                    'exposuretime': 0.001 * (i % 5 + 1),
                    'exposurebiasvalue': (i % 7) * 0.3 - 0.9,
                    'focusmode': ['AF-S', 'AF-C', 'Manual'][i % 3],
                    'pointsinfocus': (i % 5) + 1,
                    'facedetected': i % 3 == 0,
                    'make': ['Canon', 'Nikon', 'Sony'][i % 3],
                    'model': ['EOS R5', 'D850', 'A7R IV'][i % 3]
                }
            })
        return photos
    
    def test_batch_processing(self):
        """Test batch processing functionality."""
        photos = self._create_large_photo_set(50)
        
        async def test_batch():
            result = await self.processor.process_large_batch(photos)
            
            assert result['success']
            assert 'performance_metrics' in result
            assert result['performance_metrics']['total_photos'] == 50
            assert result['performance_metrics']['batch_size'] == 10
            
            return result
        
        result = asyncio.run(test_batch())
        assert result['success']
    
    def test_optimal_configuration(self):
        """Test optimal configuration selection."""
        engine = CullingOptimizedEngine()
        
        # Small batch
        config_small = engine.get_optimal_config(25)
        assert config_small.batch_size <= 25
        assert config_small.max_workers <= 4
        assert not config_small.use_multiprocessing
        
        # Large batch
        config_large = engine.get_optimal_config(500)
        assert config_large.batch_size <= 100
        assert config_large.use_multiprocessing
    
    def test_performance_recommendations(self):
        """Test performance recommendations."""
        from ..modules.culling_performance import ProcessingMetrics, get_performance_recommendations
        
        # Slow processing metrics
        slow_metrics = ProcessingMetrics(
            total_photos=100,
            processed_photos=100,
            processing_time=20.0,  # 20 seconds = 5 photos/sec
            memory_usage_mb=2000,
            cpu_usage_percent=95,
            throughput_photos_per_second=5.0,
            worker_count=8,
            batch_size=100
        )
        
        recommendations = get_performance_recommendations(100, 20.0, slow_metrics)
        
        assert len(recommendations) > 0
        assert any('multiprocessing' in rec.lower() for rec in recommendations)

class TestIntegrationExamples:
    """Integration examples showing real-world usage."""
    
    def test_wedding_photographer_workflow(self):
        """Example: Wedding photographer culling workflow."""
        
        # Simulate wedding photo batch
        wedding_photos = self._create_wedding_photo_set()
        
        # Photographer preferences
        wedding_prefs = {
            'focus_weight': 0.35,  # Emphasize sharp focus
            'exposure_weight': 0.25,
            'composition_weight': 0.20,
            'technical_weight': 0.15,
            'aesthetic_weight': 0.05,
            'prefer_face_detection': True,
            'prefer_eye_focus': True,
            'min_overall_score': 70.0
        }
        
        # Run culling analysis
        result = analyze_photos_for_culling(wedding_photos, wedding_prefs)
        
        assert result['success']
        
        # Check that photos with faces and good focus are preferred
        keep_recommendations = [r for r in result['recommendations'] if r['action'] == 'keep']
        assert len(keep_recommendations) > 0
        
        # Verify scoring weights match preferences
        assert result['scoring_weights']['focus'] == 0.35
    
    def test_sports_photographer_workflow(self):
        """Example: Sports photographer workflow."""
        
        # Sports photos (high ISO, fast shutter)
        sports_photos = self._create_sports_photo_set()
        
        # Sports photographer preferences
        sports_prefs = {
            'focus_weight': 0.40,  # Critical for sports
            'exposure_weight': 0.20,
            'composition_weight': 0.15,
            'technical_weight': 0.20,
            'aesthetic_weight': 0.05,
            'prefer_face_detection': False,  # Less important for sports
            'prefer_eye_focus': False,
            'min_overall_score': 65.0
        }
        
        result = analyze_photos_for_culling(sports_photos, sports_prefs)
        assert result['success']
        
        # Focus should be heavily weighted
        assert result['scoring_weights']['focus'] == 0.40
    
    def test_landscape_photographer_workflow(self):
        """Example: Landscape photographer workflow."""
        
        # Landscape photos
        landscape_photos = self._create_landscape_photo_set()
        
        # Landscape photographer preferences
        landscape_prefs = {
            'focus_weight': 0.25,
            'exposure_weight': 0.30,  # Exposure more important
            'composition_weight': 0.25,  # Composition critical for landscapes
            'technical_weight': 0.15,
            'aesthetic_weight': 0.05,
            'prefer_face_detection': False,
            'prefer_eye_focus': False,
            'min_overall_score': 75.0
        }
        
        result = analyze_photos_for_culling(landscape_photos, landscape_prefs)
        assert result['success']
        
        # Verify composition and exposure weights
        assert result['scoring_weights']['composition'] == 0.25
        assert result['scoring_weights']['exposure'] == 0.30
    
    def _create_wedding_photo_set(self) -> List[Dict[str, Any]]:
        """Create a realistic wedding photo set."""
        photos = []
        photo_types = [
            # Bride portraits (high priority)
            {'count': 8, 'has_face': True, 'iso': 400, 'f': 2.8, 'focus': 'AF-S', 'lens': '85mm f/1.4'},
            # Groom portraits (high priority)
            {'count': 6, 'has_face': True, 'iso': 400, 'f': 2.8, 'focus': 'AF-S', 'lens': '85mm f/1.4'},
            # Group photos (medium priority)
            {'count': 4, 'has_face': True, 'iso': 800, 'f': 5.6, 'focus': 'AF-C', 'lens': '24-70mm f/2.8'},
            # Detail shots (low priority)
            {'count': 5, 'has_face': False, 'iso': 200, 'f': 8.0, 'focus': 'Manual', 'lens': '100mm macro'},
            # Wide shots (medium priority)
            {'count': 3, 'has_face': False, 'iso': 1600, 'f': 4.0, 'focus': 'AF-C', 'lens': '16-35mm f/2.8'}
        ]
        
        photo_id = 0
        for photo_type in photo_types:
            for i in range(photo_type['count']):
                photo_id += 1
                photos.append({
                    'filename': f'wedding_{photo_id:03d}.jpg',
                    'filepath': f'/wedding/wedding_{photo_id:03d}.jpg',
                    'width': 6000,
                    'height': 4000,
                    'exif': {
                        'isospeedratings': photo_type['iso'],
                        'fnumber': photo_type['f'],
                        'exposuretime': 0.004 if photo_type['iso'] <= 400 else 0.002,
                        'exposurebiasvalue': 0.0,
                        'focusmode': photo_type['focus'],
                        'pointsinfocus': 3 if photo_type['has_face'] else 1,
                        'facedetected': photo_type['has_face'],
                        'facecount': 2 if photo_type['has_face'] else 0,
                        'lensmodel': photo_type['lens'],
                        'focallength': 85.0 if '85mm' in photo_type['lens'] else 35.0,
                        'make': 'Canon',
                        'model': 'EOS R5'
                    }
                })
        
        return photos
    
    def _create_sports_photo_set(self) -> List[Dict[str, Any]]:
        """Create a realistic sports photo set."""
        photos = []
        
        for i in range(30):
            photos.append({
                'filename': f'sports_{i:03d}.jpg',
                'filepath': f'/sports/sports_{i:03d}.jpg',
                'width': 4000,
                'height': 3000,
                'exif': {
                    'isospeedratings': 3200 + (i % 3) * 800,  # High ISO
                    'fnumber': 2.8,  # Wide open
                    'exposuretime': 0.001 + (i % 3) * 0.0005,  # Fast shutter
                    'exposurebiasvalue': 0.0,
                    'focusmode': 'AF-C',  # Continuous focus
                    'pointsinfocus': 5 + (i % 3),
                    'facedetected': i % 4 == 0,
                    'lensmodel': 'Canon 70-200mm f/2.8L',
                    'focallength': 200.0,
                    'make': 'Canon',
                    'model': 'EOS-1D X Mark III'
                }
            })
        
        return photos
    
    def _create_landscape_photo_set(self) -> List[Dict[str, Any]]:
        """Create a realistic landscape photo set."""
        photos = []
        
        for i in range(25):
            photos.append({
                'filename': f'landscape_{i:03d}.jpg',
                'filepath': f'/landscape/landscape_{i:03d}.jpg',
                'width': 8000,
                'height': 6000,
                'exif': {
                    'isospeedratings': 100,  # Base ISO
                    'fnumber': 8.0 + (i % 3) * 2.0,  # Deep DOF
                    'exposuretime': 0.5 + (i % 4) * 0.25,  # Various shutter speeds
                    'exposurebiasvalue': -0.3 + (i % 5) * 0.15,
                    'focusmode': 'Manual',  # Landscape often manual
                    'pointsinfocus': 1,
                    'facedetected': False,
                    'scenecapturetype': 'Landscape',
                    'lensmodel': 'Canon 16-35mm f/2.8L',
                    'focallength': 16.0 + (i % 3) * 6.0,
                    'make': 'Canon',
                    'model': 'EOS R5'
                }
            })
        
        return photos

# Performance benchmark tests
class TestPerformanceBenchmarks:
    """Performance benchmarks for the culling system."""
    
    def test_small_batch_performance(self):
        """Benchmark small batch processing."""
        photos = self._create_test_photos(20)
        
        start_time = time.time()
        result = analyze_photos_for_culling(photos)
        processing_time = time.time() - start_time
        
        assert result['success']
        assert processing_time < 5.0  # Should complete in under 5 seconds
        assert result['processing_time'] < 2.0  # Actual processing should be faster
    
    def test_medium_batch_performance(self):
        """Benchmark medium batch processing."""
        photos = self._create_test_photos(100)
        
        start_time = time.time()
        result = analyze_photos_for_culling(photos)
        processing_time = time.time() - start_time
        
        assert result['success']
        assert processing_time < 15.0  # Should complete in under 15 seconds
        assert result['processing_time'] < 10.0
    
    def test_large_batch_performance(self):
        """Benchmark large batch processing."""
        photos = self._create_test_photos(500)
        
        start_time = time.time()
        result = analyze_photos_for_culling(photos)
        processing_time = time.time() - start_time
        
        assert result['success']
        assert processing_time < 60.0  # Should complete in under 60 seconds
        assert result['processing_time'] < 45.0
    
    def _create_test_photos(self, count: int) -> List[Dict[str, Any]]:
        """Create test photos for benchmarking."""
        photos = []
        for i in range(count):
            photos.append({
                'filename': f'benchmark_{i:04d}.jpg',
                'filepath': f'/benchmark/benchmark_{i:04d}.jpg',
                'width': 6000,
                'height': 4000,
                'exif': {
                    'isospeedratings': 200 + (i % 8) * 100,
                    'fnumber': 2.8 + (i % 5) * 1.2,
                    'exposuretime': 0.001 * (i % 10 + 1),
                    'exposurebiasvalue': (i % 7) * 0.3 - 0.9,
                    'focusmode': ['AF-S', 'AF-C', 'Manual'][i % 3],
                    'pointsinfocus': (i % 5) + 1,
                    'facedetected': i % 3 == 0,
                    'make': ['Canon', 'Nikon', 'Sony'][i % 3],
                    'model': ['EOS R5', 'D850', 'A7R IV'][i % 3]
                }
            })
        return photos

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])