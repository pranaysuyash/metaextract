#!/usr/bin/env python3
"""
Fix bare except handlers in metadata_engine.py
"""
import re

file_path = '/Users/pranay/Projects/metaextract/server/extractor/metadata_engine.py'

# Read file
with open(file_path, 'r') as f:
    content = f.read()

# Define replacements (line_pattern, replacement)
replacements = [
    # Line 396: safe_str - UnicodeDecodeError
    (
        r"(\s+)except: return base64\.b64encode\(value\)\.decode\('ascii'\)\[:100\] \+ \"\.\.\.\"",
        r"\1except UnicodeDecodeError as e:\n\1    logger.debug(f\"Failed to decode bytes as UTF-8: {e}, falling back to base64\")\n\1    return base64.b64encode(value).decode('ascii')[:100] + \"...\""
    ),
    # Line 755: run_exiftool - JSONDecodeError, subprocess.TimeoutExpired, OSError
    (
        r"(\s+)except: return None\n\n def categorize_exiftool_output",
        r"\1except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError) as e:\n\1    logger.debug(f\"Failed to extract metadata with exiftool: {e}\")\n\1    return None\n\ndef categorize_exiftool_output"
    ),
    # Line 1159: extract_extended_attributes - OSError, ValueError
    (
        r"(\s+)except: return \{\"available\": False\}",
        r"\1except (OSError, ValueError) as e:\n\1    logger.debug(f\"Failed to extract extended attributes: {e}\")\n\1    return {\"available\": False}"
    ),
    # Line 1188: extract_exif_basic - OSError, KeyError, ValueError
    (
        r"(?<=return result)\n(\s+)except: return None\n\n def extract_gps_metadata",
        r"\n\1except (OSError, KeyError, ValueError) as e:\n\1    logger.debug(f\"Failed to extract EXIF metadata: {e}\")\n\1    return None\n\ndef extract_gps_metadata"
    ),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open(file_path, 'w') as f:
    f.write(content)

print("Fixed bare except handlers")
