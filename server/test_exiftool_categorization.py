#!/usr/bin/env python3
"""Sanity checks for ExifTool categorization."""

from extractor.metadata_engine import categorize_exiftool_output


def run() -> None:
    sample = {
        "System:FileName": "image.jpg",
        "File:FileType": "JPEG",
        "JFIF:JFIFVersion": 1.02,
        "IFD0:Make": "Apple",
        "ExifIFD:ExposureTime": "1/50",
        "GPS:GPSLatitude": [12.923974, 0, 0],
        "InteropIFD:InteroperabilityIndex": "R98",
        "IFD1:ThumbnailImage": "(Binary data 1234 bytes, use -b option to extract)",
        "ICC_Profile:ProfileDescription": "sRGB IEC61966-2.1",
        "XMP-dc:Title": "Sample",
        "XMP-GCamera:MotionPhoto": "1",
        "Canon:AFPoint": "Center",
        "Composite:ImageSize": "100x100",
    }

    categorized = categorize_exiftool_output(sample)

    assert categorized["file"]["FileName"] == "image.jpg"
    assert categorized["image_container"]["JFIFVersion"] == 1.02
    assert categorized["exif"]["Make"] == "Apple"
    assert categorized["exif_ifd"]["ifd0"]["Make"] == "Apple"
    assert categorized["gps"]["GPSLatitude"] == [12.923974, 0, 0]
    assert categorized["interoperability"]["InteroperabilityIndex"] == "R98"
    assert "ThumbnailImage" in categorized["thumbnail_metadata"]
    assert categorized["icc_profile"]["ProfileDescription"] == "sRGB IEC61966-2.1"
    assert categorized["xmp_namespaces"]["dc"]["Title"] == "Sample"
    assert categorized["xmp_namespaces"]["gCamera"]["MotionPhoto"] == "1"
    assert categorized["makernote"]["canon"]["AFPoint"] == "Center"
    assert categorized["composite"]["ImageSize"] == "100x100"

    print("✅ ExifTool categorization checks passed.")


if __name__ == "__main__":
    run()
