#!/usr/bin/env python3
"""Quick test script for metadata_engine.py"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extractor.metadata_engine import extract_metadata

def test_extraction(filepath: str):
    """Test metadata extraction on a file."""
    print(f"\n{'='*60}")
    print(f"Testing: {filepath}")
    print('='*60)
    
    for tier in ["free", "starter", "premium", "super"]:
        print(f"\n--- Tier: {tier.upper()} ---")
        result = extract_metadata(filepath, tier=tier)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
        
        info = result.get("extraction_info", {})
        print(f"Fields extracted: {info.get('fields_extracted', 0)}")
        print(f"Locked categories: {info.get('locked_categories', 0)}")
        print(f"Locked fields: {result.get('locked_fields', [])}")
        
        # Print summary
        summary = result.get("summary", {})
        for key, val in list(summary.items())[:5]:
            print(f"  {key}: {val}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_extractor.py <file_path>")
        print("\nExample: python test_extractor.py ~/Pictures/test.jpg")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    test_extraction(filepath)
