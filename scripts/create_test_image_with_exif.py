#!/usr/bin/env python3
"""
Create a test image with comprehensive EXIF metadata for testing persona interpretation.
"""

from PIL import Image, ImageDraw, ImageFont
import datetime
import os

def create_test_image_with_exif():
    """Create a test JPEG image with comprehensive EXIF data using piexif."""

    try:
        import piexif
    except ImportError:
        print("piexif not available, installing...")
        import subprocess
        subprocess.check_call(["python3", "-m", "pip", "install", "piexif"])
        import piexif

    # Create a simple test image
    img = Image.new('RGB', (800, 600), color=(135, 206, 235))  # Sky blue
    draw = ImageDraw.Draw(img)

    # Add some visual content
    draw.rectangle([100, 100, 700, 500], fill=(34, 139, 34))  # Forest green
    draw.ellipse([300, 150, 500, 350], fill=(255, 255, 0))  # Yellow sun
    draw.text((350, 220), "TEST PHOTO", fill=(0, 0, 0))

    # Save without EXIF first
    output_path = "/tmp/test_photo_with_exif.jpg"
    img.save(output_path, format="JPEG")

    # Create EXIF data using piexif
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: "Apple",
            piexif.ImageIFD.Model: "iPhone 14 Pro",
            piexif.ImageIFD.Software: "Photographer Peter",
            piexif.ImageIFD.DateTime: datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ImageIFD.Orientation: 1,
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: "2024:12:25 14:30:45",
            piexif.ExifIFD.DateTimeDigitized: "2024:12:25 14:30:45",
            piexif.ExifIFD.LensModel: "iPhone 14 Pro back triple camera",
            piexif.ExifIFD.FNumber: (2, 1),  # f/2.0
            piexif.ExifIFD.ExposureTime: (1, 125),  # 1/125s
            piexif.ExifIFD.ISOSpeedRatings: 64,
            piexif.ExifIFD.FocalLength: (42, 10),  # 4.2mm
            piexif.ExifIFD.FocalLengthIn35mmFormat: 26,
            piexif.ExifIFD.MeteringMode: 5,
            piexif.ExifIFD.Flash: 0,
            piexif.ExifIFD.WhiteBalance: 0,
            piexif.ExifIFD.PixelXDimension: 800,
            piexif.ExifIFD.PixelYDimension: 600,
        },
        "GPS": {
            # San Francisco coordinates
            piexif.GPSIFD.GPSLatitude: ((37, 1), (47, 1), (24, 1)),  # 37°47'24" N
            piexif.GPSIFD.GPSLatitudeRef: b'N',
            piexif.GPSIFD.GPSLongitude: ((122, 1), (24, 1), (12, 1)),  # 122°24'12" W
            piexif.GPSIFD.GPSLongitudeRef: b'W',
            piexif.GPSIFD.GPSAltitude: (52, 1),  # 52m
            piexif.GPSIFD.GPSAltitudeRef: 0,  # Above sea level
            piexif.GPSIFD.GPSTimeStamp: ((14, 1), (30, 1), (45, 1)),  # 14:30:45
            piexif.GPSIFD.GPSDateStamp: "2024:12:25",
        }
    }

    # Convert to EXIF bytes
    exif_bytes = piexif.dump(exif_dict)

    # Insert EXIF into the image
    piexif.insert(exif_bytes, output_path)

    print(f"✅ Created test image with EXIF data: {output_path}")

    # Verify the EXIF data
    verify_exif = piexif.load(output_path)

    if verify_exif:
        print("✅ EXIF data successfully written:")
        try:
            if "0th" in verify_exif:
                zero_ifd = piexif.ImageIFD(verify_exif["0th"])
                if piexif.ImageIFD.Make in zero_ifd:
                    print(f"  Make: {zero_ifd[piexif.ImageIFD.Make]}")
                if piexif.ImageIFD.Model in zero_ifd:
                    print(f"  Model: {zero_ifd[piexif.ImageIFD.Model]}")
                if piexif.ImageIFD.DateTime in zero_ifd:
                    print(f"  DateTime: {zero_ifd[piexif.ImageIFD.DateTime]}")

            if "Exif" in verify_exif:
                exif_ifd = piexif.ExifIFD(verify_exif["Exif"])
                if piexif.ExifIFD.DateTimeOriginal in exif_ifd:
                    print(f"  DateTimeOriginal: {exif_ifd[piexif.ExifIFD.DateTimeOriginal]}")
                if piexif.ExifIFD.CreateDate in exif_ifd:
                    print(f"  CreateDate: {exif_ifd[piexif.ExifIFD.CreateDate]}")

            if "GPS" in verify_exif:
                gps_ifd = verify_exif["GPS"]
                print(f"  GPS data present: {len(gps_ifd)} fields")
        except Exception as e:
            print(f"  Error reading specific EXIF fields: {e}")
            print(f"  Raw EXIF structure: {list(verify_exif.keys())}")
    else:
        print("❌ No EXIF data found in created image")

    return output_path

if __name__ == "__main__":
    create_test_image_with_exif()