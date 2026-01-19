#!/usr/bin/env python3
"""
MetaExtract Image Benchmark Runner (Updated with Real Test Files)

This script benchmarks extraction performance on ACTUAL sample files
with real metadata, and generates comprehensive benchmark reports.

Usage:
    python benchmark_extraction.py [--sample-dir PATH] [--output PATH] [--iterations N]

Output:
    - Console summary
    - JSON report (for CI/trending)
    - Markdown report (for human review)
"""

import json
import time
import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXIFTOOL_PATH = "/opt/homebrew/bin/exiftool"
EXIFTOOL_AVAILABLE = os.path.exists(EXIFTOOL_PATH) and os.access(EXIFTOOL_PATH, os.X_OK)

CREDIT_SCHEDULE = {
    'base': 1,
    'embedding': 3,
    'ocr': 5,
    'forensics': 4,
}

MP_BUCKETS = [
    {'label': 'standard', 'maxMp': 12, 'credits': 0},
    {'label': 'large', 'maxMp': 24, 'credits': 1},
    {'label': 'xl', 'maxMp': 48, 'credits': 3},
    {'label': 'xxl', 'maxMp': 96, 'credits': 7},
]

SAMPLE_FILES = {
    'standard_synthetic': [
        'test-data/test_jpg.jpg',
        'test-data/test_png.png',
        'test-data/test_webp.webp',
    ],
    'standard_real': [
        'tests/fixtures/test_image.jpg',
        'tests/fixtures/test_ultra_comprehensive.jpg',
    ],
    'professional': [
        'test-data/test_tiff.tiff',
        'test-data/test_dng.dng',
        'test-data/test_minimal.psd',
    ],
    'raw': [
        'test-data/test_cr3.cr3',
    ],
    'scientific': [
        'test-data/test_fits.fits',
        'test-data/test_minimal.exr',
    ],
    'heic': [
        'test-data/test_minimal.heic',
    ],
}

def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(filepath) if os.path.exists(filepath) else 0

def get_file_dimensions(filepath: str) -> Optional[tuple]:
    """Get image dimensions using exiftool or PIL."""
    if EXIFTOOL_AVAILABLE:
        cmd = [EXIFTOOL_PATH, '-b', '-ImageWidth', '-ImageHeight', filepath]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    width = int(lines[0].strip())
                    height = int(lines[1].strip())
                    return (width, height)
        except Exception as e:
            logger.warning(f"Could not get dimensions from exiftool: {e}")
    
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            return (img.width, img.height)
    except Exception:
        return None

def calculate_mp(width: Optional[int], height: Optional[int]) -> Optional[float]:
    """Calculate megapixels from dimensions."""
    if not width or not height or width <= 0 or height <= 0:
        return None
    return round((width * height) / 1_000_000, 2)

def get_mp_bucket(mp: Optional[float]) -> Dict[str, Any]:
    """Get megapixel bucket and credits."""
    if mp is None:
        return {'label': 'unknown', 'credits': 0}
    for bucket in MP_BUCKETS:
        if mp <= bucket['maxMp']:
            return {'label': bucket['label'], 'credits': bucket['credits']}
    return {'label': 'xxl', 'credits': 7}

def extract_with_exiftool(filepath: str) -> Dict[str, Any]:
    """Extract metadata using ExifTool."""
    if not EXIFTOOL_AVAILABLE:
        return {'error': 'ExifTool not available'}
    
    cmd = [
        EXIFTOOL_PATH,
        '-j', '-a', '-G1', '-s',
        '-overwrite_original',
        filepath
    ]
    
    start = time.perf_counter()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        elapsed = time.perf_counter() - start
        
        if result.returncode != 0:
            return {'error': result.stderr, 'elapsed_ms': round(elapsed * 1000, 2)}
        
        output = result.stdout.strip()
        if output:
            data = json.loads(output)
            raw_data = data[0] if data else {}
            
            # Categorize tags
            categories = {}
            for k in raw_data.keys():
                if ':' in k:
                    g = k.split(':')[0]
                elif not k.startswith('ExifTool') and not k.startswith('SourceFile'):
                    g = 'File'
                else:
                    g = 'System'
                categories[g] = categories.get(g, 0) + 1
            
            return {
                'data': raw_data,
                'elapsed_ms': round(elapsed * 1000, 2),
                'total_tags': len(raw_data),
                'categories': categories,
            }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {'error': str(e), 'elapsed_ms': round(elapsed * 1000, 2)}
    
    return {'error': 'No output', 'elapsed_ms': 0}

def count_registry_fields(exiftool_data: Dict) -> int:
    """Count how many registry fields would be populated from exiftool data."""
    if not exiftool_data or 'data' not in exiftool_data:
        return 0
    
    data = exiftool_data.get('data', {})
    if not data:
        return 0
    
    registry_fields = {
        'basic_properties': ['filename', 'file_size_bytes', 'modified_timestamp', 
                            'mime_type', 'width', 'height', 'color_channels', 'bit_depth'],
        'exif_standard': ['camera_make', 'camera_model', 'software', 'artist', 'copyright',
                         'date_time', 'orientation', 'x_resolution', 'y_resolution',
                         'exposure_time', 'f_number', 'iso_speed', 'exposure_program',
                         'metering_mode', 'flash', 'focal_length', 'color_space',
                         'pixel_x_dimension', 'pixel_y_dimension', 'date_time_original',
                         'date_time_digitized', 'lens_make', 'lens_model', 'body_serial_number',
                         'lens_serial_number', 'camera_owner_name', 'exposure_mode',
                         'white_balance', 'exif_version', 'gps_version_id', 'gps_latitude',
                         'gps_longitude', 'gps_altitude', 'gps_time_stamp', 'gps_date_stamp',
                         'gps_latitude_ref', 'gps_longitude_ref'],
        'iptc_standard': ['keywords', 'caption', 'headline', 'byline', 'credit', 'source',
                         'copyright_notice', 'city', 'province_state', 'country',
                         'date_created', 'object_name', 'urgency'],
        'xmp_namespaces': ['xmp_dc_title', 'xmp_dc_creator', 'xmp_dc_description',
                          'xmp_dc_subject', 'xmp_dc_rights', 'xmp_dc_format',
                          'xmp_dc_identifier', 'xmp_dc_date', 'xmp_dc_type', 'xmp_dc_language'],
        'icc_profiles': ['profile_version', 'profile_class', 'color_space', 'connection_space',
                        'profile_datetime', 'rendering_intent', 'profile_description', 'profile_copyright'],
        'file_format_chunks': ['jfif_version', 'encoding_process', 'ycbcr_subsampling'],
    }
    
    count = 0
    for category, fields in registry_fields.items():
        for field in fields:
            if field in str(data):
                count += 1
    
    return count

def calculate_credits(filepath: str, mp: Optional[float], has_ocr: bool = False, 
                      has_embedding: bool = False, has_forensics: bool = False) -> Dict[str, Any]:
    """Calculate credit consumption for a file."""
    mp_info = get_mp_bucket(mp)
    
    breakdown = {
        'base': CREDIT_SCHEDULE['base'],
        'mp': mp_info['credits'],
        'embedding': CREDIT_SCHEDULE['embedding'] if has_embedding else 0,
        'ocr': CREDIT_SCHEDULE['ocr'] if has_ocr else 0,
        'forensics': CREDIT_SCHEDULE['forensics'] if has_forensics else 0,
    }
    
    total = sum(breakdown.values())
    
    return {
        'credits_total': total,
        'breakdown': breakdown,
        'mp_bucket': mp_info['label'],
        'mp_value': mp,
    }

def benchmark_file(filepath: str, iterations: int = 3) -> Dict[str, Any]:
    """Run benchmark on a single file."""
    if not os.path.exists(filepath):
        return {'error': f'File not found: {filepath}'}
    
    file_ext = Path(filepath).suffix.lower()
    file_size = get_file_size(filepath)
    dimensions = get_file_dimensions(filepath)
    mp = calculate_mp(*dimensions) if dimensions else None
    
    times = []
    tag_counts = []
    
    for _ in range(iterations):
        result = extract_with_exiftool(filepath)
        if 'elapsed_ms' in result:
            times.append(result['elapsed_ms'])
        if 'total_tags' in result:
            tag_counts.append(result['total_tags'])
    
    avg_time = sum(times) / len(times) if times else 0
    avg_tags = sum(tag_counts) / len(tag_counts) if tag_counts else 0
    
    # Get full extraction result for categories
    full_result = extract_with_exiftool(filepath)
    
    credits_info = calculate_credits(filepath, mp)
    
    return {
        'filepath': filepath,
        'file_ext': file_ext,
        'file_size_bytes': file_size,
        'file_size_mb': round(file_size / (1024 * 1024), 3),
        'dimensions': dimensions,
        'megapixels': mp,
        'mp_bucket': credits_info['mp_bucket'],
        'iterations': iterations,
        'avg_time_ms': round(avg_time, 2),
        'min_time_ms': round(min(times), 2) if times else 0,
        'max_time_ms': round(max(times), 2) if times else 0,
        'avg_tags': round(avg_tags, 1),
        'total_tags': tag_counts[0] if tag_counts else 0,
        'categories': full_result.get('categories', {}),
        'credits_base': credits_info['breakdown']['base'],
        'credits_mp': credits_info['breakdown']['mp'],
        'credits_total': credits_info['credits_total'],
        'features': {
            'ocr': False,
            'embedding': False,
            'forensics': False,
        },
    }

def run_benchmarks(iterations: int = 3) -> Dict[str, Any]:
    """Run benchmarks on all sample files."""
    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'exiftool_available': EXIFTOOL_AVAILABLE,
        'iterations': iterations,
        'files': [],
        'by_category': {},
        'summary': {},
    }
    
    all_files = []
    for category, files in SAMPLE_FILES.items():
        for f in files:
            all_files.append((category, f))
    
    for category, filepath in all_files:
        logger.info(f"Benchmarking {filepath}...")
        result = benchmark_file(filepath, iterations)
        result['category'] = category
        results['files'].append(result)
        
        if category not in results['by_category']:
            results['by_category'][category] = []
        results['by_category'][category].append(result)
    
    if results['files']:
        times = [f['avg_time_ms'] for f in results['files'] if 'avg_time_ms' in f]
        tags = [f['avg_tags'] for f in results['files'] if 'avg_tags' in f]
        credits = [f['credits_total'] for f in results['files']]
        sizes = [f['file_size_bytes'] for f in results['files']]
        
        results['summary'] = {
            'total_files': len(results['files']),
            'avg_time_ms': round(sum(times) / len(times), 2) if times else 0,
            'min_time_ms': min(times) if times else 0,
            'max_time_ms': max(times) if times else 0,
            'avg_tags': round(sum(tags) / len(tags), 1) if tags else 0,
            'total_tags': round(sum(tags), 1),
            'total_credits': sum(credits),
            'avg_credits': round(sum(credits) / len(credits), 2),
            'total_size_bytes': sum(sizes),
            'total_size_mb': round(sum(sizes) / (1024 * 1024), 2),
        }
        
        for category, files in results['by_category'].items():
            cat_times = [f['avg_time_ms'] for f in files if 'avg_time_ms' in f]
            cat_tags = [f['avg_tags'] for f in files if 'avg_tags' in f]
            results['by_category'][category] = {
                'count': len(files),
                'avg_time_ms': round(sum(cat_times) / len(cat_times), 2) if cat_times else 0,
                'avg_tags': round(sum(cat_tags) / len(cat_tags), 1) if cat_tags else 0,
            }
    
    return results

def generate_markdown_report(results: Dict) -> str:
    """Generate markdown report from benchmark results."""
    md = []
    md.append("# MetaExtract Image Extraction Benchmarks\n")
    md.append(f"**Generated:** {results['timestamp']}\n")
    md.append(f"**ExifTool Available:** {results['exiftool_available']}\n")
    md.append(f"**Iterations per file:** {results['iterations']}\n\n")
    
    md.append("## Summary\n")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append(f"| Total Files | {results['summary'].get('total_files', 0)} |")
    md.append(f"| Avg Time | {results['summary'].get('avg_time_ms', 0)}ms |")
    md.append(f"| Min Time | {results['summary'].get('min_time_ms', 0)}ms |")
    md.append(f"| Max Time | {results['summary'].get('max_time_ms', 0)}ms |")
    md.append(f"| Avg Tags | {results['summary'].get('avg_tags', 0)} |")
    md.append(f"| Total Tags | {results['summary'].get('total_tags', 0)} |")
    md.append(f"| Total Credits | {results['summary'].get('total_credits', 0)} |")
    md.append(f"| Total Size | {results['summary'].get('total_size_mb', 0)}MB |")
    md.append("\n")
    
    md.append("## By Category\n")
    md.append("| Category | Files | Avg Time | Avg Tags |")
    md.append("|----------|-------|----------|----------|")
    for category, data in results.get('by_category', {}).items():
        md.append(f"| {category} | {data['count']} | {data['avg_time_ms']}ms | {data['avg_tags']} |")
    md.append("\n")
    
    md.append("## File Details\n")
    md.append("| File | Ext | Size | MP | Time | Tags | Credits |")
    md.append("|------|-----|------|----|------|------|---------|")
    
    for f in sorted(results['files'], key=lambda x: x.get('avg_tags', 0), reverse=True):
        if 'error' in f:
            continue
        md.append(f"| {Path(f['filepath']).name} | {f['file_ext']} | {f['file_size_mb']}MB | "
                 f"{f['megapixels'] or '?'} | {f['avg_time_ms']}ms | {f['avg_tags']} | {f['credits_total']} |")
    
    md.append("\n## Tag Categories (Best File)\n")
    best_file = max(results['files'], key=lambda x: x.get('avg_tags', 0))
    if best_file.get('categories'):
        md.append(f"**File:** {best_file['filepath']}\n")
        md.append("| Category | Tags |")
        md.append("|----------|------|")
        for cat, count in sorted(best_file['categories'].items(), key=lambda x: -x[1]):
            md.append(f"| {cat} | {count} |")
    md.append("\n")
    
    md.append("## Credit Breakdown by Feature\n")
    md.append("| Feature | Credit Cost |")
    md.append("|---------|-------------|")
    for feature, cost in CREDIT_SCHEDULE.items():
        md.append(f"| {feature} | {cost} |")
    
    md.append("\n## MP Bucket Pricing\n")
    md.append("| Bucket | Max MP | Credits |")
    md.append("|--------|--------|---------|")
    for bucket in MP_BUCKETS:
        md.append(f"| {bucket['label']} | {bucket['maxMp']} | {bucket['credits']} |")
    
    md.append("\n## Coverage Notes\n")
    md.append("- **Real test files:** `tests/fixtures/test_image.jpg` (100 tags, GPS, camera EXIF)")
    md.append("- **Synthetic files:** `test-data/*.jpg` (18-25 tags, minimal)")
    md.append("- **Production gap:** Real images may have 95-320 tags (JPEG) to 2,400+ (RAW)")
    md.append("- **Recommendation:** Add production sample files for complete validation")
    
    return '\n'.join(md)

def main():
    parser = argparse.ArgumentParser(description='MetaExtract Image Benchmark Runner')
    parser.add_argument('--output', default='benchmarks/results', help='Output directory')
    parser.add_argument('--iterations', type=int, default=5, help='Iterations per file')
    parser.add_argument('--json-only', action='store_true', help='Output JSON only')
    args = parser.parse_args()
    
    logger.info(f"Starting benchmarks (iterations={args.iterations})...")
    
    results = run_benchmarks(args.iterations)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    json_path = output_dir / f'benchmark_{timestamp}.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"JSON report: {json_path}")
    
    if not args.json_only:
        md_path = output_dir / f'benchmark_{timestamp}.md'
        with open(md_path, 'w') as f:
            f.write(generate_markdown_report(results))
        logger.info(f"Markdown report: {md_path}")
    
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"Files tested: {results['summary'].get('total_files', 0)}")
    print(f"Avg extraction time: {results['summary'].get('avg_time_ms', 0)}ms")
    print(f"Avg tags extracted: {results['summary'].get('avg_tags', 0)}")
    print(f"Total credits: {results['summary'].get('total_credits', 0)}")
    print(f"Total size: {results['summary'].get('total_size_mb', 0)}MB")
    print("="*60)
    
    return results

if __name__ == '__main__':
    main()
