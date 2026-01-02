import unittest
import numpy as np
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.extractor.modules.advanced_analysis import EnhancedManipulationDetector

class TestEnhancedManipulationDetector(unittest.TestCase):
    def setUp(self):
        # We might need to patch libraries if they are not available in the test environment
        # But let's assume valid environment or handle gracefully
        self.detector = EnhancedManipulationDetector()

    def create_solid_image(self, width=100, height=100, color=(100, 100, 100)):
        return np.full((height, width, 3), color, dtype=np.uint8)

    @patch('cv2.imread')
    def test_detect_image_manipulation_clean(self, mock_imread):
        """Test manipulation detection on a 'clean' image."""
        if not self.detector.initialized:
            self.skipTest("Missing dependencies (OpenCV/Scikit-Learn)")
            
        mock_imread.return_value = self.create_solid_image()
        
        # Mock other internal methods to avoid complex image processing in unit test
        # OR trust the "solid image" to produce low scores.
        # Solid image should have 0 ELA error, 0 noise variance, consistent lighting.
        
        result = self.detector.detect_image_manipulation("dummy_path.jpg")
        
        self.assertIn("manipulation_probability", result)
        # Should be low for a perfect image
        self.assertLess(result["manipulation_probability"], 0.3)

    @patch('cv2.imread')
    def test_check_metadata_consistency(self, mock_imread):

        """Test metadata consistency checks."""
        # Create image 100x100
        img = self.create_solid_image(100, 100)
        mock_imread.return_value = img
        
        # Metadata says 200x200
        metadata = {
            "exif": {
                "ExifImageWidth": 200,
                "ExifImageHeight": 200,
                "Software": "Adobe Photoshop CS6"
            }
        }
        
        inconsistencies = self.detector._check_metadata_consistency(metadata, img)
        
        # Should detect dimension mismatch and photoshop
        self.assertTrue(any("width" in m for m in inconsistencies))
        self.assertTrue(any("height" in m for m in inconsistencies))
        self.assertTrue(any("photoshop" in m.lower() for m in inconsistencies))

    def test_calculate_skewness(self):
        """Test helper method."""
        data = np.array([1, 2, 3, 4, 5])
        skew = self.detector._calculate_skewness(data)
        self.assertAlmostEqual(skew, 0.0) # Symmetric

if __name__ == '__main__':
    unittest.main()
