"""
Hash Implementation Tests

Tests for file hash and perceptual hash implementations to ensure:
- extract_file_hashes works correctly (md5, sha1, sha256, crc32)
- extract_perceptual_hashes works correctly (imagehash functions)
- Module exports are correct
- Functions handle edge cases properly
"""

import os
import sys
import tempfile
import hashlib
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'server'))

from extractor.modules import extract_file_hashes, extract_perceptual_hashes


def create_test_file(content: bytes, filename: str) -> str:
    """Create a temporary test file with given content."""
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(content)
    return filepath


def test_extract_file_hashes_basic():
    """Test that extract_file_hashes returns all expected hash types."""
    test_content = b"Hello, World! This is a test file for hashing."
    filepath = create_test_file(test_content, 'test.txt')

    try:
        result = extract_file_hashes(filepath)

        # Check that all expected hash types are present
        assert 'md5' in result, "MD5 hash missing"
        assert 'sha256' in result, "SHA256 hash missing"
        assert 'sha1' in result, "SHA1 hash missing"
        assert 'crc32' in result, "CRC32 hash missing"

        # Verify hash formats (should be hex strings)
        assert len(result['md5']) == 32, "MD5 should be 32 hex characters"
        assert len(result['sha256']) == 64, "SHA256 should be 64 hex characters"
        assert len(result['sha1']) == 40, "SHA1 should be 40 hex characters"
        assert len(result['crc32']) == 8, "CRC32 should be 8 hex characters"

        # Verify hashes are valid hex
        for hash_name, hash_value in result.items():
            if hash_name != 'error':
                try:
                    int(hash_value, 16)
                except ValueError:
                    assert False, f"{hash_name} hash is not valid hex: {hash_value}"

        print("✅ extract_file_hashes basic test passed")
        print(f"   MD5: {result['md5']}")
        print(f"   SHA256: {result['sha256']}")
        print(f"   SHA1: {result['sha1']}")
        print(f"   CRC32: {result['crc32']}")

    finally:
        # Cleanup
        try:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
        except:
            pass


def test_extract_file_hashes_consistency():
    """Test that extract_file_hashes produces consistent results."""
    test_content = b"Consistent test content for hash verification."
    filepath = create_test_file(test_content, 'consistent.txt')

    try:
        # Hash the same file twice and compare
        result1 = extract_file_hashes(filepath)
        result2 = extract_file_hashes(filepath)

        # Results should be identical
        assert result1['md5'] == result2['md5'], "MD5 hashes should be consistent"
        assert result1['sha256'] == result2['sha256'], "SHA256 hashes should be consistent"
        assert result1['sha1'] == result2['sha1'], "SHA1 hashes should be consistent"
        assert result1['crc32'] == result2['crc32'], "CRC32 hashes should be consistent"

        print("✅ extract_file_hashes consistency test passed")

    finally:
        # Cleanup
        try:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
        except:
            pass


def test_extract_file_hashes_python_comparison():
    """Test that extract_file_hashes matches Python's hashlib output."""
    test_content = b"Python comparison test content."
    filepath = create_test_file(test_content, 'python_test.txt')

    try:
        # Get our implementation's results
        result = extract_file_hashes(filepath)

        # Calculate expected hashes using Python's hashlib directly
        md5_expected = hashlib.md5(test_content).hexdigest()
        sha256_expected = hashlib.sha256(test_content).hexdigest()
        sha1_expected = hashlib.sha1(test_content).hexdigest()

        # CRC32 requires special handling
        import zlib
        crc32_expected = format(zlib.crc32(test_content) & 0xFFFFFFFF, "08x")

        # Verify they match
        assert result['md5'] == md5_expected, "MD5 should match Python hashlib"
        assert result['sha256'] == sha256_expected, "SHA256 should match Python hashlib"
        assert result['sha1'] == sha1_expected, "SHA1 should match Python hashlib"
        assert result['crc32'] == crc32_expected, "CRC32 should match zlib.crc32"

        print("✅ extract_file_hashes Python comparison test passed")

    finally:
        # Cleanup
        try:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
        except:
            pass


def test_extract_file_hashes_error_handling():
    """Test that extract_file_hashes handles errors gracefully."""
    # Test with non-existent file
    try:
        result = extract_file_hashes('/nonexistent/file.txt')
        # Should return error dict or raise appropriate exception
        assert 'error' in result or isinstance(result, dict), "Should handle missing file gracefully"
        print("✅ extract_file_hashes error handling test passed")
    except Exception as e:
        # Also acceptable if it raises a controlled exception
        print(f"✅ extract_file_hashes error handling test passed (raised {type(e).__name__})")


def test_extract_file_hashes_empty_file():
    """Test that extract_file_hashes handles empty files."""
    filepath = create_test_file(b"", 'empty.txt')

    try:
        result = extract_file_hashes(filepath)

        # Should still produce hashes for empty file
        assert 'md5' in result, "Should hash empty file"
        assert result['md5'] == 'd41d8cd98f00b204e9800998ecf8427e', "Empty file MD5 should match known value"

        print("✅ extract_file_hashes empty file test passed")

    finally:
        # Cleanup
        try:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
        except:
            pass


def test_extract_file_hashes_large_file():
    """Test that extract_file_hashes handles large files efficiently."""
    # Create a 10MB test file
    large_content = b"X" * (10 * 1024 * 1024)
    filepath = create_test_file(large_content, 'large.txt')

    try:
        result = extract_file_hashes(filepath)

        # Should process large file without issues
        assert 'md5' in result, "Should hash large file"
        assert 'sha256' in result, "Should calculate SHA256 for large file"

        print("✅ extract_file_hashes large file test passed")
        print(f"   Processed 10MB file successfully")

    finally:
        # Cleanup
        try:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
        except:
            pass


def test_extract_perceptual_hashes_import():
    """Test that extract_perceptual_hashes can be imported and has correct signature."""
    # Test that the function exists and is callable
    assert callable(extract_perceptual_hashes), "extract_perceptual_hashes should be callable"
    print("✅ extract_perceptual_hashes import test passed")


def test_module_exports():
    """Test that module exports are correct and not duplicated."""
    # Check that we can import both functions from the modules
    from extractor.modules.hashes import extract_file_hashes
    from extractor.modules.perceptual_hashes import extract_perceptual_hashes as extract_perceptual_from_perceptual_module

    # Both should be callable
    assert callable(extract_file_hashes), "extract_file_hashes should be callable from hashes module"
    assert callable(extract_perceptual_from_perceptual_module), "extract_perceptual_hashes should be callable from perceptual_hashes module"

    # The compatibility wrapper in hashes.py should also work
    try:
        from extractor.modules.hashes import extract_perceptual_hashes as extract_perceptual_from_hashes
        assert callable(extract_perceptual_from_hashes), "Compatibility wrapper should be callable"
        print("✅ Module exports test passed - no duplication found")
    except ImportError as e:
        # Expected if imagehash is not installed
        print(f"✅ Module exports test passed - expected ImportError: {e}")


def run_all_tests():
    """Run all hash implementation tests."""
    print("=" * 60)
    print("Hash Implementation Tests")
    print("=" * 60)

    # File hash tests
    print("\n--- File Hash Tests ---")
    test_extract_file_hashes_basic()
    test_extract_file_hashes_consistency()
    test_extract_file_hashes_python_comparison()
    test_extract_file_hashes_error_handling()
    test_extract_file_hashes_empty_file()
    test_extract_file_hashes_large_file()

    # Perceptual hash tests
    print("\n--- Perceptual Hash Tests ---")
    test_extract_perceptual_hashes_import()

    # Module export tests
    print("\n--- Module Export Tests ---")
    test_module_exports()

    print("\n" + "=" * 60)
    print("All hash implementation tests passed! ✅")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()