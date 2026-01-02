#!/usr/bin/env python3
"""
FITS/Astronomical Data Extractor for MetaExtract.
Extracts metadata from FITS files used in astronomy and scientific imaging.
"""

import os
import sys
import json
import struct
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib

logger = logging.getLogger(__name__)

FITS_AVAILABLE = True
try:
    from astropy.io import fits
    from astropy.wcs import WCS
except ImportError:
    FITS_AVAILABLE = False
    logger.warning("astropy not available - FITS extraction limited")


@dataclass
class FITSHeader:
    """Represents a FITS header card."""
    keyword: str = ""
    value: Any = None
    comment: str = ""


@dataclass
class FITSExtension:
    """Represents a FITS extension/HDU."""
    name: str = ""
    type: str = ""
    axis: Tuple[int, ...] = ()
    shape: Tuple[int, ...] = ()
    dtype: str = ""
    bscale: Optional[float] = None
    bzero: Optional[float] = None
    bitpix: Optional[int] = None
    extend: bool = False
    simple: bool = False


class FITSExtractor:
    """Extract metadata from FITS files."""

    def __init__(self):
        self.wcs_available = FITS_AVAILABLE

    def detect_fits(self, filepath: str) -> bool:
        """Check if file is a valid FITS file."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(80)
                return header[:8] == b'SIMPLE  '
        except:
            return False

    def parse_header_cards(self, header_str: str) -> List[FITSHeader]:
        """Parse FITS header into individual cards."""
        cards = []
        for i in range(0, len(header_str), 80):
            card_str = header_str[i:i+80]
            if len(card_str) < 80:
                continue
            
            keyword = card_str[:8].strip()
            if keyword == 'END':
                break
            
            if card_str[8:9] == b'=':
                value_str = card_str[9:30]
                comment_str = card_str[30:].strip().decode('ascii', errors='replace')
                
                try:
                    if value_str[0:1] == b"'":
                        value = value_str[1:].strip().rstrip(b"'").decode('ascii', errors='replace')
                    else:
                        value = value_str.strip().decode('ascii')
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                except:
                    value = value_str.strip().decode('ascii', errors='replace')
                
                cards.append(FITSHeader(keyword=keyword, value=value, comment=comment_str))
            else:
                cards.append(FITSHeader(keyword=keyword))
        
        return cards

    def extract_basic_header(self, filepath: str) -> Dict[str, Any]:
        """Extract basic FITS header without astropy."""
        result = {
            "format": "fits",
            "header_cards": [],
            "basic_info": {},
        }

        try:
            with open(filepath, 'rb') as f:
                header_data = b''
                while True:
                    block = f.read(2880)
                    if not block:
                        break
                    header_data += block
                    if b'END' in block:
                        break

            cards = self.parse_header_cards(header_data[:2880 * 10])
            result["header_cards"] = [
                {"keyword": c.keyword, "value": c.value, "comment": c.comment}
                for c in cards[:36]
            ]

            for card in cards:
                if card.keyword == 'SIMPLE':
                    result["basic_info"]["simple"] = card.value
                elif card.keyword == 'BITPIX':
                    result["basic_info"]["bitpix"] = card.value
                elif card.keyword == 'NAXIS':
                    result["basic_info"]["naxis"] = card.value
                elif card.keyword == 'NAXIS1':
                    result["basic_info"]["naxis1"] = card.value
                elif card.keyword == 'NAXIS2':
                    result["basic_info"]["naxis2"] = card.value
                elif card.keyword == 'OBJECT':
                    result["basic_info"]["object"] = card.value
                elif card.keyword == 'TELESCOP':
                    result["basic_info"]["telescope"] = card.value
                elif card.keyword == 'INSTRUME':
                    result["basic_info"]["instrument"] = card.value
                elif card.keyword == 'DATE-OBS':
                    result["basic_info"]["date_obs"] = card.value
                elif card.keyword == 'EXPTIME':
                    result["basic_info"]["exptime"] = card.value
                elif card.keyword == 'FILTER':
                    result["basic_info"]["filter"] = card.value
                elif card.keyword == 'OBSERVER':
                    result["basic_info"]["observer"] = card.value
                elif card.keyword == 'EQUINOX':
                    result["basic_info"]["equinox"] = card.value
                elif card.keyword == 'CTYPE1':
                    result["basic_info"]["ctype1"] = card.value
                elif card.keyword == 'CTYPE2':
                    result["basic_info"]["ctype2"] = card.value
                elif card.keyword == 'CRVAL1':
                    result["basic_info"]["crval1"] = card.value
                elif card.keyword == 'CRVAL2':
                    result["basic_info"]["crval2"] = card.value
                elif card.keyword == 'CRPIX1':
                    result["basic_info"]["crpix1"] = card.value
                elif card.keyword == 'CRPIX2':
                    result["basic_info"]["crpix2"] = card.value
                elif card.keyword == 'CDELT1':
                    result["basic_info"]["cdelt1"] = card.value
                elif card.keyword == 'CDELT2':
                    result["basic_info"]["cdelt2"] = card.value

        except Exception as e:
            logger.error(f"Error parsing FITS header: {e}")
            return {"error": str(e)}

        return result

    def extract_with_astropy(self, filepath: str) -> Dict[str, Any]:
        """Extract FITS metadata using astropy."""
        if not FITS_AVAILABLE:
            return self.extract_basic_header(filepath)

        try:
            with fits.open(filepath) as hdul:
                result = {
                    "format": "fits",
                    "astropy_available": True,
                    "filename": filepath,
                    "primary_hdu": {},
                    "extensions": [],
                    "wcs_info": {},
                    "header_summary": {},
                }

                primary = hdul[0]
                result["primary_hdu"] = {
                    "shape": list(primary.shape) if hasattr(primary, 'shape') and primary.shape else [],
                    "dtype": str(primary.dtype) if hasattr(primary, 'dtype') else None,
                    "header_length": len(primary.header) if hasattr(primary, 'header') else 0,
                }

                for i, hdu in enumerate(hdul):
                    ext = {
                        "index": i,
                        "name": hdu.name if hasattr(hdu, 'name') else str(i),
                        "type": type(hdu).__name__,
                    }
                    if hasattr(hdu, 'shape') and hdu.shape:
                        ext["shape"] = list(hdu.shape)
                    if hasattr(hdu, 'header') and hdu.header:
                        ext["header_cards"] = len(hdu.header)
                    result["extensions"].append(ext)

                if hasattr(hdul[0], 'header') and hdul[0].header:
                    hdr = hdul[0].header
                    for key in ['SIMPLE', 'BITPIX', 'NAXIS', 'OBJECT', 'TELESCOP', 
                                'INSTRUME', 'DATE-OBS', 'EXPTIME', 'FILTER', 'OBSERVER',
                                'EQUINOX', 'ORIGIN']:
                        if key in hdr:
                            result["header_summary"][key] = str(hdr[key])

                try:
                    wcs = WCS(hdul[0].header)
                    result["wcs_info"] = {
                        "ctype1": wcs.wcs.ctype[0] if hasattr(wcs.wcs, 'ctype') and len(wcs.wcs.ctype) > 0 else None,
                        "ctype2": wcs.wcs.ctype[1] if hasattr(wcs.wcs, 'ctype') and len(wcs.wcs.ctype) > 1 else None,
                        "crpix1": wcs.wcs.crpix[0] if hasattr(wcs.wcs, 'crpix') and len(wcs.wcs.crpix) > 0 else None,
                        "crpix2": wcs.wcs.crpix[1] if hasattr(wcs.wcs, 'crpix') and len(wcs.wcs.crpix) > 1 else None,
                        "crval1": wcs.wcs.crval[0] if hasattr(wcs.wcs, 'crval') and len(wcs.wcs.crval) > 0 else None,
                        "crval2": wcs.wcs.crval[1] if hasattr(wcs.wcs, 'crval') and len(wcs.wcs.crval) > 1 else None,
                        "cdelt1": wcs.wcs.cdelt[0] if hasattr(wcs.wcs, 'cdelt') and len(wcs.wcs.cdelt) > 0 else None,
                        "cdelt2": wcs.wcs.cdelt[1] if hasattr(wcs.wcs, 'cdelt') and len(wcs.wcs.cdelt) > 1 else None,
                        "cunit1": wcs.wcs.cunit[0] if hasattr(wcs.wcs, 'cunit') and len(wcs.wcs.cunit) > 0 else None,
                        "cunit2": wcs.wcs.cunit[1] if hasattr(wcs.wcs, 'cunit') and len(wcs.wcs.cunit) > 1 else None,
                    }
                except Exception as e:
                    result["wcs_error"] = str(e)

                return result

        except Exception as e:
            logger.error(f"Error extracting FITS with astropy: {e}")
            return self.extract_basic_header(filepath)

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract FITS metadata from a file."""
        result = {
            "source": "metaextract_fits_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "fits_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        if not self.detect_fits(filepath):
            result["format_detected"] = "unknown"
            result["fits_metadata"] = {"error": "Not a valid FITS file"}
            return result

        result["format_detected"] = "fits"

        if FITS_AVAILABLE:
            result["fits_metadata"] = self.extract_with_astropy(filepath)
        else:
            result["fits_metadata"] = self.extract_basic_header(filepath)

        result["extraction_success"] = "error" not in result["fits_metadata"]

        return result


def extract_fits_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract FITS metadata."""
    extractor = FITSExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fits_extractor.py <file.fits>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_fits_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))

def get_fits_extractor_field_count() -> int:
    """
    Return the number of FITS metadata fields extracted.
    
    Returns:
        Total field count (6 fields)
    """
    return 6  # source, filepath, format_detected, extraction_success, fits_metadata, error

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fits_extractor.py <file.fits>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_fits_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
