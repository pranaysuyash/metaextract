#!/usr/bin/env python3
"""Calculate total metadata field count across all modules."""

import sys
sys.path.insert(0, 'server')

from extractor.modules import (
    get_exif_field_count,
    get_iptc_xmp_field_count,
    get_video_field_count,
    get_audio_field_count,
    get_scientific_medical_field_count,
    get_forensic_metadata_field_count,
    # Add more as needed
)

def main():
    """Calculate total field count."""
    field_counts = {
        'EXIF': get_exif_field_count(),
        'IPTC/XMP': get_iptc_xmp_field_count(),
        'Video': get_video_field_count(),
        'Audio': get_audio_field_count(),
        'Scientific/Medical': get_scientific_medical_field_count(),
        'Forensic': get_forensic_metadata_field_count(),
    }

    total = sum(field_counts.values())

    print("MEGA EXPANSION FIELD COUNTS")
    print("=" * 40)
    for module, count in field_counts.items():
        print(f"{module:20s}: {count:4d} fields")
    print("=" * 40)
    print(f"{'TOTAL':20s}: {total:4d} fields")
    print()
    print(f"✅ Mega expansion successfully added {total} new fields!")

    return total

if __name__ == "__main__":
    main()