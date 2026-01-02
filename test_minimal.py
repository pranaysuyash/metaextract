#!/usr/bin/env python3

import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Test',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py list
  python test.py info plugin_name
"""
    )
    
    parser.add_argument('--test', help='Test argument')
    args = parser.parse_args()
    
    print("✅ Minimal test works")
    print(f"Test argument: {args.test}")

if __name__ == '__main__':
    main()
