# MetaExtract Naming Conventions

**Date**: 2024-01-12
**Version**: 1.0
**Status**: Phase 6 - Enforcement

---

## 1. Overview

This document establishes naming conventions for all files in the MetaExtract codebase. These conventions ensure consistency, readability, and maintainability across the project.

---

## 2. Module File Naming

### 2.1 Pattern

All module files should follow the pattern:

```
{descriptive_domain}_{functionality}.py
```

### 2.2 Examples

**Good Examples** ✅

```python
# Medical Imaging
cardiac_imaging.py          # Domain: cardiac, Function: imaging
neuroimaging.py             # Domain: neuroimaging (compound)
mammography_imaging.py      # Domain: mammography, Function: imaging
orthopedic_imaging.py       # Domain: orthopedic, Function: imaging

# Scientific Research
ecological_imaging.py       # Domain: ecological, Function: imaging
genetics_imaging.py         # Domain: genetics, Function: imaging
proteomics.py               # Domain: proteomics (single domain)

# Camera/Photo
camera_makernotes_advanced.py   # Domain: camera_makernotes, Descriptor: advanced
camera_makernotes_pro.py        # Domain: camera_makernotes, Descriptor: pro

# Audio/Video
audio_advanced_id3.py       # Domain: audio, Function: id3, Descriptor: advanced
video_professional.py       # Domain: video, Descriptor: professional
video_streaming.py          # Domain: video, Function: streaming

# Forensic/Security
forensic_security_advanced.py   # Domain: forensic_security, Descriptor: advanced
forensic_basic.py           # Domain: forensic, Descriptor: basic
security_monitoring.py      # Domain: security, Function: monitoring
```

**Bad Examples** ❌

```python
# Forbidden: Roman numerals
scientific_dicom_fits_ultimate_advanced_extension_ii.py
makernotes_ultimate_advanced_extension_xvi.py

# Forbidden: Superlatives
ultimate_complete_mega_advanced_extension.py
complete_imaging_module.py
mega_extraction_tool.py

# Forbidden: Excessive length
very_very_long_descriptive_name_that_is_hard_to_read.py

# Forbidden: CamelCase
CardiacImaging.py           # Should be lowercase with underscores
```

---

## 3. Forbidden Patterns

The following patterns are **strictly forbidden**:

| Pattern                      | Forbidden | Use Instead                          |
| ---------------------------- | --------- | ------------------------------------ |
| `ultimate`                   | ❌        | Descriptive domain name              |
| `complete`                   | ❌        | Version numbers (v1, v2)             |
| `mega`                       | ❌        | Descriptive adjectives               |
| `ultra`                      | ❌        | Specific descriptors (pro, advanced) |
| `massive`                    | ❌        | Size indicators if needed            |
| Roman numerals (II, III, IV) | ❌        | Descriptive domain names             |
| `advanced_extension_`        | ❌        | Actual extension description         |
| CamelCase                    | ❌        | lowercase_with_underscores           |

### Examples of Corrections

| Before (Forbidden)               | After (Correct)          |
| -------------------------------- | ------------------------ |
| `ultimate_advanced_extension.py` | `cardiac_imaging.py`     |
| `mega_module.py`                 | `large_file_handler.py`  |
| `extension_iv.py`                | `mammography_imaging.py` |
| `complete_solution.py`           | `extraction_core.py`     |

---

## 4. Naming Guidelines

### 4.1 Length Limits

- **Maximum file name length**: 30 characters
- **Recommended length**: 15-25 characters
- **Exception**: Compound domain names may exceed 30 characters

### 4.2 Case and Separators

- Use **lowercase** only
- Use **underscores** (`_`) to separate words
- No spaces or hyphens

### 4.3 Pluralization

- Use **singular nouns** for modules
- `cardiac_imaging.py` NOT `cardiacs_imaging.py`

### 4.4 Compound Domains

When domain names are naturally compound (like `camera_makernotes`), use the full compound name:

```python
camera_makernotes_advanced.py  # ✅ Correct
camera_makernotes_pro.py       # ✅ Correct
camera_mak_nt_adv.py           # ❌ Wrong - don't abbreviate
```

---

## 5. Function Naming

### 5.1 Extract Functions

```python
def extract_{module_name}(file_path: str) -> Dict[str, Any]:
    """Extract metadata from file."""
```

**Examples**:

```python
def extract_cardiac_imaging(file_path: str) -> Dict[str, Any]:
    """Extract cardiac imaging metadata."""

def extract_mammography_imaging(file_path: str) -> Dict[str, Any]:
    """Extract mammography imaging metadata."""
```

### 5.2 Helper Functions

```python
def get_{module_name}_field_count() -> int:
    """Return number of fields extracted."""

def get_{module_name}_version() -> str:
    """Return module version."""

def get_{module_name}_description() -> str:
    """Return module description."""

def get_{module_name}_supported_formats() -> List[str]:
    """Return list of supported file formats."""

def get_{module_name}_modalities() -> List[str]:
    """Return list of supported DICOM modalities."""
```

---

## 6. Class Naming

### 6.1 Pattern

Use PascalCase for classes:

```python
class CardiacImagingExtractor:
    """Extract cardiac imaging metadata."""

class SecurityEventLogger:
    """Log security events."""
```

### 6.2 Examples

| Purpose   | Class Name              |
| --------- | ----------------------- |
| Extractor | `MammographyExtractor`  |
| Logger    | `SecurityEventLogger`   |
| Manager   | `FileExtractionManager` |
| Validator | `MetadataValidator`     |

---

## 7. Variable Naming

### 7.1 Constants

Use UPPERCASE with underscores:

```python
MAX_FILE_SIZE = 1024 * 1024 * 100  # 100MB
SUPPORTED_FORMATS = ['.dcm', '.dicom']
```

### 7.2 Variables and Parameters

Use lowercase with underscores:

```python
file_path = "/path/to/file.dcm"
extracted_fields = {}
modality = "CT"
```

### 7.3 Private Variables

Use leading underscore:

```python
class Extractor:
    def __init__(self):
        self._internal_cache = {}
        self._config = {}
```

---

## 8. Directory Naming

### 8.1 Pattern

Use lowercase with hyphens for directories:

```
server/extractor/modules/          # ✅ Correct
Server/Extractor/Modules/          # ❌ Wrong
```

### 8.2 Examples

| Purpose           | Directory Name                |
| ----------------- | ----------------------------- |
| Extractor modules | `server/extractor/modules/`   |
| Tests             | `tests/` or `__tests__/`      |
| Documentation     | `docs/` or `documentation/`   |
| Configuration     | `config/` or `configuration/` |

---

## 9. Configuration Files

### 9.1 Pattern

Use lowercase with potential hyphens:

```
pyproject.toml              # ✅ Standard Python
package.json                # ✅ Standard npm
.prettierrc                 # ✅ Standard config
```

### 9.2 Examples

| Purpose           | File Name                     |
| ----------------- | ----------------------------- |
| Python config     | `pyproject.toml`, `setup.cfg` |
| TypeScript config | `tsconfig.json`               |
| ESLint config     | `.eslintrc.js`                |
| Prettier config   | `.prettierrc`                 |
| Git ignore        | `.gitignore`                  |

---

## 10. Test File Naming

### 10.1 Pattern

Use `test_{module_name}.py` or `{module_name}.test.py`:

```python
test_cardiac_imaging.py     # ✅ Correct
cardiac_imaging_test.py     # ✅ Correct
cardiac_imaging.spec.ts     # ✅ Correct (TypeScript)
testCardiacImaging.js       # ❌ Wrong - inconsistent
```

### 10.2 Examples

| Module                 | Test File                   |
| ---------------------- | --------------------------- |
| `cardiac_imaging.py`   | `test_cardiac_imaging.py`   |
| `forensic_security.py` | `test_forensic_security.py` |
| `audio_extractor.py`   | `test_audio_extractor.py`   |

---

## 11. Validation Tools

### 11.1 Pre-commit Hook

A pre-commit hook is provided to validate naming conventions:

```bash
# Run validation
python scripts/validate_naming.py
```

### 11.2 Git Hook Installation

```bash
# Install pre-commit hook
pre-commit install --hook-type pre-commit
```

### 11.3 CI/CD Integration

The naming validation is automatically run in CI/CD pipelines.

---

## 12. Enforcement

### 12.1 Pre-commit Checks

All new files must pass naming validation before commit:

```bash
# Check a single file
python scripts/validate_naming.py --file server/extractor/modules/new_module.py

# Check entire codebase
python scripts/validate_naming.py --all
```

### 12.2 CI/CD Pipeline

Naming validation is part of the CI pipeline:

```yaml
# In .github/workflows/ci.yml
- name: Validate naming conventions
  run: python scripts/validate_naming.py --all
```

### 12.3 Breaking Changes

If a rename is required:

1. Create the new file with correct naming
2. Update all imports referencing the old file
3. Run full test suite
4. Remove the old file
5. Commit all changes together

---

## 13. Migration Guide

### 13.1 Converting Legacy Files

For files with forbidden patterns, follow this migration path:

**Step 1**: Identify the domain and functionality

```
scientific_dicom_fits_ultimate_advanced_extension_iv.py
                    ↓
        Domain: mammography
        Function: imaging
```

**Step 2**: Create new filename

```
mammography_imaging.py
```

**Step 3**: Add aliases for backward compatibility

```python
# In mammography_imaging.py

# New function
def extract_mammography_imaging(file_path: str) -> Dict[str, Any]:
    """Extract mammography imaging metadata."""
    ...

# Alias for backward compatibility
def extract_scientific_dicom_fits_ultimate_advanced_extension_iv(file_path: str) -> Dict[str, Any]:
    """Alias for extract_mammography_imaging."""
    return extract_mammography_imaging(file_path)
```

**Step 4**: Update imports gradually

```python
# Old import (still works)
from server.extractor.modules import extract_scientific_dicom_fits_ultimate_advanced_extension_iv

# New import (preferred)
from server.extractor.modules import extract_mammography_imaging
```

---

## 14. Exceptions

### 14.1 When to Request Exception

Exceptions may be granted for:

- External API compatibility (e.g., maintaining API endpoint names)
- Legacy system integration
- Standard format compliance (e.g., DICOM, EXIF standards)

### 14.2 Exception Process

1. Create an issue explaining the exception request
2. Document why the convention cannot be followed
3. Get approval from project maintainer
4. Document the exception in this file

---

## 15. Related Documents

- `IMPLEMENTATION_PLAN.md` - Overall implementation plan
- `IMPLEMENTATION_PROGRESS.md` - Current progress tracking
- `scripts/validate_naming.py` - Validation tool
- `.prettierrc` - Code formatting rules
- `.eslintrc.js` - JavaScript/TypeScript linting rules

---

**Document Version**: 1.0
**Last Updated**: 2024-01-12
**Next Review**: 2024-02-12
