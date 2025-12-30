#!/usr/bin/env python3
"""Comprehensive validation test for MetaExtract audio extractors."""

import json
import os
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


def create_test_wav(path: Path) -> bool:
    try:
        import wave
        with wave.open(str(path), 'w') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            import array
            samples = array.array('h', [0] * 44100 * 2)
            wav.writeframes(samples.tobytes())
        return True
    except Exception:
        return False


def create_test_mp3(path: Path) -> bool:
    try:
        with open(path, 'wb') as f:
            f.write(b'ID3')
            f.write(bytes([0x04, 0x00]))
            f.write(bytes([0x00] * 6))
            f.write(b'TITL')
            f.write(struct.pack('>I', 11))
            f.write(bytes([0]))
            f.write(b'Test Title\x00')
        return True
    except Exception:
        return False


def create_test_ogg(path: Path) -> bool:
    try:
        with open(path, 'wb') as f:
            f.write(b'OggS')
            f.write(bytes([0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01]))
            f.write(b'vorbis')
            f.write(bytes([0x01, 0x44, 0xAC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        return True
    except Exception:
        return False


def create_test_opus(path: Path) -> bool:
    try:
        with open(path, 'wb') as f:
            f.write(b'OggS')
            f.write(bytes([0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01]))
            f.write(b'OpusHead')
            f.write(bytes([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        return True
    except Exception:
        return False


def create_test_aiff(path: Path) -> bool:
    try:
        with open(path, 'wb') as f:
            f.write(b'FORM')
            f.write(struct.pack('>I', 38))
            f.write(b'AIFF')
            f.write(b'COMM')
            f.write(struct.pack('>I', 18))
            f.write(struct.pack('>H', 2))
            f.write(struct.pack('>I', 44100))
            f.write(struct.pack('>H', 16))
            f.write(bytes([0x40, 0x0E, 0xAC, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
            f.write(b'SSND')
            f.write(struct.pack('>I', 8))
            f.write(struct.pack('>I', 0))
            f.write(struct.pack('>I', 0))
        return True
    except Exception:
        return False


def create_test_m4a(path: Path) -> bool:
    try:
        with open(path, 'wb') as f:
            f.write(b'ftyp')
            f.write(struct.pack('>I', 24))
            f.write(b'M4A ')
            f.write(struct.pack('>I', 0))
            f.write(b'M4A ')
            f.write(b'mp42')
            f.write(b'isom')
        return True
    except Exception:
        return False


def create_test_ape(path: Path) -> bool:
    try:
        with open(path, 'wb') as f:
            f.write(b'APETAGEX')
            f.write(struct.pack('<I', 2000))
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', 0))
            f.write(b'APETAGEX200')
        return True
    except Exception:
        return False


def run_extractor_test(name: str, script_path: str, test_file: Path) -> Dict[str, Any]:
    result = {
        "extractor": name,
        "test_file": str(test_file),
        "success": False,
        "fields_found": 0,
        "error": None,
    }
    
    if not test_file.exists():
        result["error"] = "Test file not created"
        return result
    
    try:
        import subprocess
        result_proc = subprocess.run(
            [sys.executable, script_path, str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result_proc.returncode == 0:
            result["success"] = True
            for line in result_proc.stdout.split('\n'):
                if line.startswith("Fields supported:"):
                    result["fields_found"] = int(line.split(":")[1].strip())
        else:
            result["error"] = result_proc.stderr[:200] if result_proc.stderr else "Non-zero exit"
            
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    print("=" * 70)
    print("METAFIELD EXTRACTOR VALIDATION TESTS")
    print("=" * 70)
    print()
    
    base_path = Path(__file__).parent.parent
    test_dir = base_path / "dist" / "validation_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("apev2", "ape", base_path / "server" / "extractor" / "modules" / "apev2_extractor.py"),
        ("wav_riff", "wav", base_path / "server" / "extractor" / "modules" / "wav_riff_extractor.py"),
        ("mp4", "m4a", base_path / "server" / "extractor" / "modules" / "mp4_atoms_extractor.py"),
        ("aiff", "aiff", base_path / "server" / "extractor" / "modules" / "aiff_extractor.py"),
        ("opus", "opus", base_path / "server" / "extractor" / "modules" / "opus_extractor.py"),
    ]
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tests": [],
        "summary": {"total": 0, "passed": 0, "failed": 0, "fields": 0}
    }
    
    print("Testing audio metadata extractors...")
    print("-" * 70)
    
    for name, ext, script_path in tests:
        test_file = test_dir / f"test{ext}"
        
        create_func = f"create_test_{ext}"
        if create_func in globals():
            globals()[create_func](test_file)
        
        test_result = run_extractor_test(name, str(script_path), test_file)
        results["tests"].append(test_result)
        results["summary"]["total"] += 1
        
        if test_result["success"]:
            results["summary"]["passed"] += 1
            results["summary"]["fields"] += test_result["fields_found"]
            print(f"  [PASS] {name:12s} | Fields: {test_result['fields_found']:3d}")
        else:
            results["summary"]["failed"] += 1
            print(f"  [FAIL] {name:12s} | {test_result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print()
    print(f"Total Tests:  {results['summary']['total']}")
    print(f"Passed:       {results['summary']['passed']}")
    print(f"Failed:       {results['summary']['failed']}")
    print(f"Total Fields: {results['summary']['fields']}")
    print()
    
    output_dir = base_path / "dist" / "validation_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "extractor_validation.json"
    output_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results: {output_file}")
    
    if results['summary']['failed'] > 0:
        print(f"\nWARNING: {results['summary']['failed']} test(s) failed!")
    else:
        print("\nAll tests passed!")


if __name__ == "__main__":
    main()
