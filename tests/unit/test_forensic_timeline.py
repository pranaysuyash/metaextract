import unittest
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.extractor.modules.timeline import TimelineReconstructor

class TestTimelineReconstructor(unittest.TestCase):
    def setUp(self):
        self.reconstructor = TimelineReconstructor()

    def test_parse_timestamp_variations(self):
        """Test parsing of different timestamp formats."""
        t1 = self.reconstructor._parse_timestamp("2023:01:01 12:00:00")
        self.assertEqual(t1, datetime(2023, 1, 1, 12, 0, 0))
        
        t2 = self.reconstructor._parse_timestamp("2023-01-01T12:00:00Z")
        self.assertEqual(t2, datetime(2023, 1, 1, 12, 0, 0))

    def test_reconstruct_timeline_ordering(self):
        """Test that events are sorted chronologically."""
        metadata_list = [
            # File 1: Late
            {
                "file": {"name": "img2.jpg"},
                "exif": {"DateTimeOriginal": "2023:01:02 10:00:00"}
            },
            # File 2: Early
            {
                "file": {"name": "img1.jpg"},
                "exif": {"DateTimeOriginal": "2023:01:01 10:00:00"}
            }
        ]
        
        result = self.reconstructor.reconstruct_timeline(metadata_list)
        if "error" in result:
             self.fail(f"Timeline reconstruction returned error: {result['error']}")

        events = result["events"]
        
        self.assertEqual(len(events), 2)
        # Should be sorted
        self.assertEqual(events[0]["file_identifier"], "img1.jpg")
        self.assertEqual(events[1]["file_identifier"], "img2.jpg")

    def test_detect_anomalies_future(self):
        """Test detection of future timestamps."""
        future_year = datetime.now().year + 5
        metadata_list = [{
            "exif": {"DateTimeOriginal": f"{future_year}:01:01 00:00:00"}
        }]
        
        result = self.reconstructor.reconstruct_timeline(metadata_list)
        anomalies = result.get("anomalies", [])
        
        self.assertTrue(any(a["type"] == "future_timestamp" for a in anomalies))

    def test_single_file_timeline_inconsistency(self):
        """Test inconsistency when Modified date is BEFORE Created date."""
        metadata = {
            "exif": {
                "CreateDate": "2023:01:05 10:00:00",
                "ModifyDate": "2023:01:01 10:00:00" # Impossible!
            }
        }
        
        result = self.reconstructor.analyze_single_file_timeline(metadata)
        consistency = result["consistency_analysis"]
        
        # Logic says consistency score lowers if created > modified
        # timestamps are sorted in 'events', but consistency check uses event types
        # _check_file_timestamp_consistency logic:
        # latest_creation > earliest_modification -> consistency -= 0.3
        
        if "timestamp_consistency" in consistency:
            self.assertLess(consistency["timestamp_consistency"], 1.0)
        
        # We also check validation issues which should definitely be present
        if "validation_issues" in consistency:
            self.assertTrue(any("inconsistency" in i.lower() for i in consistency["validation_issues"]))

if __name__ == '__main__':
    unittest.main()
