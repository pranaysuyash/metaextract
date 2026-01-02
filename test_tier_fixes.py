#!/usr/bin/env python3
"""
Simple test to verify tier defaults are working correctly.
"""

import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def test_tier_defaults():
    """Test that tier defaults are set to 'free' instead of premium tiers."""

    # Test 1: Check Python engine function signatures
    try:
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata, extract_comprehensive_metadata_async

        # Check function signatures
        import inspect
        sig1 = inspect.signature(extract_comprehensive_metadata)
        sig2 = inspect.signature(extract_comprehensive_metadata_async)

        tier_param1 = sig1.parameters['tier']
        tier_param2 = sig2.parameters['tier']

        assert tier_param1.default == "free", f"Expected 'free', got {tier_param1.default}"
        assert tier_param2.default == "free", f"Expected 'free', got {tier_param2.default}"

        print("✅ Python engine tier defaults: PASS")

    except Exception as e:
        print(f"❌ Python engine test failed: {e}")
        return False

    # Test 2: Check CLI argument default by reading the source
    try:
        with open('server/extractor/comprehensive_metadata_engine.py', 'r') as f:
            content = f.read()
            if 'default="free"' in content and '--tier' in content:
                print("✅ CLI tier default: PASS (verified in source code)")
            else:
                raise AssertionError("CLI default not found or incorrect")

    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Testing tier enforcement fixes...")
    print("=" * 50)

    success = test_tier_defaults()

    print("=" * 50)
    if success:
        print("🎉 ALL TIER DEFAULT FIXES VERIFIED!")
        print("Users will now default to 'free' tier instead of premium access.")
    else:
        print("❌ Some tests failed. Please check the implementation.")

    sys.exit(0 if success else 1)