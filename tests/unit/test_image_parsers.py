"""
Unit Tests for Image Parsers
============================

Tests for the image_parsers module covering:
- Parser registry and discovery
- Format-specific parsing (JPEG, PNG, GIF, BMP, WebP, TIFF, HEIC, AVIF, PSD, SVG)
- Field counting accuracy
- Computed metadata generation
"""

import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'server'))

from extractor.modules.image_parsers import (
    parse_image_metadata,
    get_parser_registry,
    ImageParserRegistry,
    FormatParser
)


class TestImageParserRegistry(unittest.TestCase):
    """Test the parser registry and discovery."""
    
    def test_registry_singleton(self):
        """Test that registry returns consistent instance."""
        registry1 = get_parser_registry()
        registry2 = get_parser_registry()
        self.assertIs(registry1, registry2)
    
    def test_registered_parsers_count(self):
        """Test expected number of parsers are registered."""
        registry = get_parser_registry()
        parsers = registry.get_all_parsers()
        self.assertGreaterEqual(len(parsers), 9)
    
    def test_supported_extensions(self):
        """Test all expected extensions are supported."""
        registry = get_parser_registry()
        extensions = registry.get_supported_extensions()
        
        expected_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                              '.webp', '.tiff', '.tif', '.heic', '.avif',
                              '.psd', '.svg']
        
        for ext in expected_extensions:
            self.assertIn(ext, extensions, f"Extension {ext} not found in registry")
    
    def test_get_parser_by_extension(self):
        """Test getting parser for specific extension."""
        registry = get_parser_registry()
        
        jpg_parser = registry.get_parser('test.jpg')
        self.assertIsNotNone(jpg_parser)
        
        png_parser = registry.get_parser('test.png')
        self.assertIsNotNone(png_parser)
        
        unknown_parser = registry.get_parser('test.xyz')
        self.assertIsNone(unknown_parser)

    def test_registry_resolves_heic_and_avif_separately(self):
        """Regression: HEIC and AVIF must map to their dedicated parsers."""
        registry = get_parser_registry()
        heic = registry.get_parser('x.heic')
        avif = registry.get_parser('x.avif')

        self.assertIsNotNone(heic)
        self.assertIsNotNone(avif)
        self.assertEqual(heic.__class__.__name__, 'HeicParser')
        self.assertEqual(avif.__class__.__name__, 'AvifParser')


class TestFieldCounting(unittest.TestCase):
    """Test accurate field counting (not synthetic)."""
    
    def test_count_real_fields_empty(self):
        """Test counting empty/none values."""
        registry = get_parser_registry()
        parser = registry.get_parser('test.jpg')
        
        empty_data = {
            'format': None,
            'width': None,
            'empty_string': '',
            'zero': 0,
            'nested': {
                'value': None,
                'data': {}
            }
        }
        
        count = parser._count_real_fields(empty_data)
        # 0 is considered a meaningful leaf value (e.g., altitude=0).
        self.assertEqual(count, 1)
    
    def test_count_real_fields_with_data(self):
        """Test counting real data fields."""
        registry = get_parser_registry()
        parser = registry.get_parser('test.jpg')
        
        data = {
            'format': 'JPEG',
            'width': 1920,
            'height': 1080,
            'megapixels': 2.07,
            'exif': {
                'make': 'Canon',
                'model': 'EOS R5',
                'iso': 100
            }
        }
        
        count = parser._count_real_fields(data)
        self.assertGreater(count, 0)
    
    def test_count_ignores_bookkeeping(self):
        """Test that bookkeeping fields are not counted."""
        registry = get_parser_registry()
        parser = registry.get_parser('test.jpg')
        
        data = {
            'format': 'JPEG',
            'source': 'extraction_info',
            'errors': [],
            'warnings': [],
            'performance': {'duration': 0.5},
            'extraction_info': {'method': 'native'}
        }
        
        count = parser._count_real_fields(data)
        self.assertEqual(count, 1)  # Only 'format': 'JPEG' counts


class TestParseImageMetadata(unittest.TestCase):
    """Test the unified parse_image_metadata function."""
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file returns error."""
        result = parse_image_metadata('/nonexistent/path/test.jpg')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'File not found')
        self.assertEqual(result['fields_extracted'], 0)
    
    def test_parse_unsupported_format(self):
        """Test parsing unsupported format returns error."""
        unsupported_path = '/tmp/test.unsupported_format_xyz'
        Path(unsupported_path).touch()
        
        try:
            result = parse_image_metadata(unsupported_path)
            
            self.assertFalse(result['success'])
            self.assertFalse(result['supported'])
            self.assertIn('Unsupported format', result['error'])
        finally:
            Path(unsupported_path).unlink()


class TestFormatParsers(unittest.TestCase):
    """Test individual format parsers with test files."""
    
    TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'test-data'
    
    def test_jpeg_parsing(self):
        """Test JPEG parsing with sample file."""
        jpg_path = self.TEST_DATA_DIR / 'test_jpg.jpg'
        if not jpg_path.exists():
            self.skipTest("JPEG test file not found")
        
        result = parse_image_metadata(str(jpg_path))
        
        self.assertTrue(result['success'])
        self.assertIn(result['format'].upper(), ['JPEG', 'JPG'])
        self.assertGreater(result['fields_extracted'], 0)
        self.assertIn('metadata', result)
    
    def test_png_parsing(self):
        """Test PNG parsing with sample file."""
        png_path = self.TEST_DATA_DIR / 'test_png.png'
        if not png_path.exists():
            self.skipTest("PNG test file not found")
        
        result = parse_image_metadata(str(png_path))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'PNG')
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_gif_parsing(self):
        """Test GIF parsing with sample file."""
        gif_path = self.TEST_DATA_DIR / 'test_sample.gif'
        if not gif_path.exists():
            self.skipTest("GIF test file not found")
        
        result = parse_image_metadata(str(gif_path))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'GIF')
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_bmp_parsing(self):
        """Test BMP parsing with sample file."""
        bmp_path = self.TEST_DATA_DIR / 'test_bmp.bmp'
        if not bmp_path.exists():
            self.skipTest("BMP test file not found")
        
        result = parse_image_metadata(str(bmp_path))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'BMP')
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_webp_parsing(self):
        """Test WebP parsing with sample file."""
        webp_path = self.TEST_DATA_DIR / 'test_webp.webp'
        if not webp_path.exists():
            self.skipTest("WebP test file not found")
        
        result = parse_image_metadata(str(webp_path))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'WebP')
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_tiff_parsing(self):
        """Test TIFF parsing with sample file."""
        tiff_path = self.TEST_DATA_DIR / 'test_tiff.tiff'
        if not tiff_path.exists():
            self.skipTest("TIFF test file not found")
        
        result = parse_image_metadata(str(tiff_path))
        
        self.assertTrue(result['success'])
        self.assertIn(result['format'].upper(), ['TIFF', 'TIF'])
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_heic_parsing(self):
        """Test HEIC parsing with sample file."""
        heic_path = self.TEST_DATA_DIR / 'test_minimal.heic'
        if not heic_path.exists():
            self.skipTest("HEIC test file not found")
        
        result = parse_image_metadata(str(heic_path))
        
        self.assertTrue(result['success'])
        self.assertIn(result['format'].upper(), ['HEIC', 'HEIF'])
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_avif_parsing(self):
        """Test AVIF parsing with sample file."""
        avif_path = self.TEST_DATA_DIR / 'test_minimal.avif'
        if not avif_path.exists():
            self.skipTest("AVIF test file not found")
        
        result = parse_image_metadata(str(avif_path))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'AVIF')
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_psd_parsing(self):
        """Test PSD parsing with sample file."""
        psd_path = self.TEST_DATA_DIR / 'test_minimal.psd'
        if not psd_path.exists():
            self.skipTest("PSD test file not found")
        
        result = parse_image_metadata(str(psd_path))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'PSD')
        self.assertGreater(result['fields_extracted'], 0)
    
    def test_svg_parsing(self):
        """Test SVG parsing with sample file."""
        svg_path = self.TEST_DATA_DIR / 'test_svg.svg'
        if not svg_path.exists():
            self.skipTest("SVG test file not found")
        
        result = parse_image_metadata(str(svg_path))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'SVG')
        self.assertGreater(result['fields_extracted'], 0)


class TestComputedMetadata(unittest.TestCase):
    """Test computed metadata generation."""
    
    TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'test-data'
    
    def test_computed_metadata_included(self):
        """Test that computed metadata is included in results."""
        png_path = self.TEST_DATA_DIR / 'test_png.png'
        if not png_path.exists():
            self.skipTest("PNG test file not found")
        
        result = parse_image_metadata(str(png_path))
        
        if result['success']:
            metadata = result['metadata']
            
            computed_fields = [
                'image_quality_analysis',
                'ai_quality_assessment',
                'ai_color_analysis',
                'perceptual_hashes',
                'forensic',
                'technical_metadata',
                'image_analysis',
                'data_completeness'
            ]
            
            for field in computed_fields:
                self.assertIn(field, metadata, f"Computed field '{field}' not found")
    
    def test_quality_score_range(self):
        """Test that quality scores are in valid range."""
        jpg_path = self.TEST_DATA_DIR / 'test_jpg.jpg'
        if not jpg_path.exists():
            self.skipTest("JPEG test file not found")
        
        result = parse_image_metadata(str(jpg_path))
        
        if result['success']:
            quality = result['metadata'].get('image_quality_analysis', {})
            if quality:
                score = quality.get('quality_score', 0)
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)
    
    def test_ai_quality_assessment(self):
        """Test AI quality assessment is generated."""
        png_path = self.TEST_DATA_DIR / 'test_png.png'
        if not png_path.exists():
            self.skipTest("PNG test file not found")
        
        result = parse_image_metadata(str(png_path))
        
        if result['success']:
            ai_quality = result['metadata'].get('ai_quality_assessment', {})
            self.assertIsInstance(ai_quality, dict)
            if ai_quality:
                self.assertTrue(
                    'quality_score' in ai_quality or 'overall_quality_score' in ai_quality,
                    f"Expected quality_score in AI quality assessment, got: {list(ai_quality.keys())}"
                )


class TestFieldCountingHonesty(unittest.TestCase):
    """Test that field counting is honest (no synthetic placeholders)."""
    
    TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'test-data'
    
    def test_no_synthetic_drone_telemetry(self):
        """Test that drone_telemetry is not added for non-drone images."""
        png_path = self.TEST_DATA_DIR / 'test_png.png'
        if not png_path.exists():
            self.skipTest("PNG test file not found")
        
        result = parse_image_metadata(str(png_path))
        
        if result['success']:
            metadata = result['metadata']
            
            synthetic_fields = [
                'drone_telemetry',
                'blockchain_provenance',
                'healthcare_medical',
                'scientific_fits',
                'scientific_dicom'
            ]
            
            for field in synthetic_fields:
                self.assertNotIn(field, metadata, 
                    f"Synthetic field '{field}' should not be present")
    
    def test_field_count_matches_actual_data(self):
        """Test that field count matches actual data present."""
        png_path = self.TEST_DATA_DIR / 'test_png.png'
        if not png_path.exists():
            self.skipTest("PNG test file not found")
        
        result = parse_image_metadata(str(png_path))
        
        if result['success']:
            count = result['fields_extracted']
            actual_count = count_real_fields_recursive(result['metadata'])
            
            self.assertEqual(count, actual_count, 
                "Reported field count doesn't match actual count")


def count_real_fields_recursive(data, depth=0, max_depth=10):
    """Helper function to count real fields (must match production semantics)."""
    from server.extractor.utils.field_counting import (
        DEFAULT_FIELD_COUNT_IGNORED_KEYS,
        count_meaningful_fields,
    )

    ignored = set(DEFAULT_FIELD_COUNT_IGNORED_KEYS)
    ignored.discard("version")
    ignored |= {
        "analysis_type",
        "optimized_mode",
        "fallback_mode",
        "status",
        "cache_hits",
        "cache_misses",
        "cache_hit_rate",
        "performance_score",
    }

    return count_meaningful_fields(
        data,
        ignored_keys=ignored,
        max_depth=max_depth,
    )


if __name__ == '__main__':
    unittest.main()
