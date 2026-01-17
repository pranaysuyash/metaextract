"""
FITS Parser
===========

Extracts metadata from FITS (Flexible Image Transport System) files.
FITS is the standard data format for astronomy and scientific imaging.

FITS Structure:
- Primary HDU (Header Data Unit)
- Image array (optional)
- Binary tables (optional)
- ASCII tables (optional)
- Multiple extensions (HDUs)

Reference: FITS 4.0 (IAU 2015)
"""

from . import ScientificParser, logger
from typing import Dict, Any, Optional
from pathlib import Path
import struct


class FitsParser(ScientificParser):
    """FITS-specific metadata parser."""
    
    FORMAT_NAME = "FITS"
    SUPPORTED_EXTENSIONS = ['.fits', '.fit', '.fts']
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract FITS metadata."""
        result = {}
        
        try:
            from astropy.io import fits
            
            with fits.open(filepath) as hdul:
                result = self._extract_fits_metadata(hdul)
                
        except ImportError:
            result = self._parse_basic_fits(filepath)
        except Exception as e:
            logger.warning(f"FITS parsing failed: {e}")
            result = {"error": str(e)[:200]}
        
        return result
    
    def _extract_fits_metadata(self, hdul) -> Dict[str, Any]:
        """Extract comprehensive FITS metadata using astropy."""
        metadata = {}
        
        primary = hdul[0]
        header = primary.header
        
        metadata['file_type'] = 'FITS'
        metadata['fits_version'] = str(header.get('VERSION', ''))
        metadata['num_hdus'] = len(hdul)
        
        metadata['observation'] = self._extract_observation_data(header)
        metadata['instrument'] = self._extract_instrument_data(header)
        metadata['coordinates'] = self._extract_coordinate_data(header)
        metadata['exposure'] = self._extract_exposure_data(header)
        metadata['image'] = self._extract_image_data(header, primary)
        metadata['data_quality'] = self._extract_quality_data(header)
        
        if len(hdul) > 1:
            metadata['extensions'] = self._extract_extension_info(hdul)
        
        return metadata
    
    def _extract_observation_data(self, header) -> Dict[str, Any]:
        """Extract observation metadata."""
        return {
            'telescope': str(header.get('TELESCOP', '')),
            'instrument': str(header.get('INSTRUME', '')),
            'observer': str(header.get('OBSERVER', '')),
            'object': str(header.get('OBJECT', '')),
            'object_type': str(header.get('OBJTYPE', '')),
            'title': str(header.get('TITLE', '')),
            'science_observation': bool(header.get('SCI_OBJ', False)),
            'calibration_observation': bool(header.get('CAL_OBJ', False)),
        }
    
    def _extract_instrument_data(self, header) -> Dict[str, Any]:
        """Extract instrument/detector parameters."""
        return {
            'detector': str(header.get('DETECTOR', '')),
            'filter': str(header.get('FILTER', '')),
            'filter_lambda': float(header.get('FILTLAM', 0)) or None,
            'filter_bandwidth': float(header.get('FILTBW', 0)) or None,
            'ccd_temp': float(header.get('CCD-TEMP', 0)) or None,
            'readout_mode': str(header.get('READMODE', '')),
            'gain': float(header.get('GAIN', 0)) or None,
            'read_noise': float(header.get('RDNOISE', 0)) or None,
            'binning': str(header.get('BINNING', '')),
            'setup': str(header.get('SETUP', '')),
        }
    
    def _extract_coordinate_data(self, header) -> Dict[str, Any]:
        """Extract celestial coordinate information."""
        return {
            'ra': str(header.get('RA', '')),
            'dec': str(header.get('DEC', '')),
            'ra_deg': self._parse_sexagesimal(header.get('RA', '')),
            'dec_deg': self._parse_sexagesimal_dec(header.get('DEC', '')),
            'ra_observer': str(header.get('RA_OBS', '')),
            'dec_observer': str(header.get('DEC_OBS', '')),
            'ha': str(header.get('HA', '')),
            'airmass': float(header.get('AIRMASS', 0)) or None,
            'hour_angle': float(header.get('HOURANG', 0)) or None,
            'zenith_distance': float(header.get('ZEN_DIST', 0)) or None,
            'galactic_lat': float(header.get('GALACTIC_LAT', 0)) or None,
            'galactic_lon': float(header.get('GALACTIC_LON', 0)) or None,
            'ecliptic_lat': float(header.get('ECLIPTIC_LAT', 0)) or None,
            'ecliptic_lon': float(header.get('ECLIPTIC_LON', 0)) or None,
            'coordinate_system': str(header.get('COORDSYS', 'ICRS')),
            'equinox': str(header.get('EQUINOX', '')),
            'epoch': str(header.get('EPOCH', '')),
        }
    
    def _parse_sexagesimal(self, value: str) -> Optional[float]:
        """Parse RA in HH:MM:SS.ss format to decimal degrees."""
        try:
            if not value or ':' not in value:
                return None
            parts = value.split(':')
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2]) if len(parts) > 2 else 0
            return (hours + minutes/60 + seconds/3600) * 15
        except:
            return None
    
    def _parse_sexagesimal_dec(self, value: str) -> Optional[float]:
        """Parse DEC in +/-DD:MM:SS.s format to decimal degrees."""
        try:
            if not value or ':' not in value:
                return None
            sign = -1 if value.startswith('-') else 1
            if value.startswith('+') or value.startswith('-'):
                value = value[1:]
            parts = value.split(':')
            degrees = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0
            seconds = float(parts[2]) if len(parts) > 2 else 0
            return sign * (degrees + minutes/60 + seconds/3600)
        except:
            return None
    
    def _extract_exposure_data(self, header) -> Dict[str, Any]:
        """Extract exposure/timing information."""
        return {
            'exposure_time': float(header.get('EXPTIME', 0)) or None,
            'exposure_start': str(header.get('DATE-OBS', '')),
            'exposure_end': str(header.get('DATE-END', '')),
            'mid_exposure': str(header.get('MJD-OBS', '')),
            'mid_exposure_mjd': float(header.get('MJD-OBS', 0)) or None,
            'exposure_mjd': float(header.get('EXPJUL', 0)) or None,
            'local_time': str(header.get('LOCALTIM', '')),
            'ut_time': str(header.get('UT', '')),
            'lst': str(header.get('LST', '')),
            'elapsed_time': float(header.get('TELAPS', 0)) or None,
            'shutter_open_time': str(header.get('SHUTOPEN', '')),
            'shutter_close_time': str(header.get('SHUTCLOS', '')),
        }
    
    def _extract_image_data(self, header, primary) -> Dict[str, Any]:
        """Extract image dimensions and data characteristics."""
        bitpix = int(header.get('BITPIX', 0))
        naxis = int(header.get('NAXIS', 0))
        
        dimensions = []
        for i in range(1, naxis + 1):
            naxis_key = f'NAXIS{i}'
            dimensions.append(int(header.get(naxis_key, 0)))
        
        bzero = float(header.get('BZERO', 0)) or None
        bscale = float(header.get('BSCALE', 1)) or 1.0
        
        data_type = self._get_fits_data_type(bitpix)
        
        return {
            'bitpix': bitpix,
            'bits_per_pixel': bitpix,
            'data_type': data_type,
            'naxis': naxis,
            'dimensions': dimensions if dimensions else None,
            'width': dimensions[0] if len(dimensions) > 0 else None,
            'height': dimensions[1] if len(dimensions) > 1 else None,
            'depth': dimensions[2] if len(dimensions) > 2 else None,
            'bzero': bzero,
            'bscale': bscale,
            'blank_value': int(header.get('BLANK', 0)) or None,
            'datamin': float(header.get('DATAMIN', 0)) or None,
            'datamax': float(header.get('DATAMAX', 0)) or None,
            'extendable': bool(header.get('EXTEND', False)),
            'simple': bool(header.get('SIMPLE', False)),
        }
    
    def _get_fits_data_type(self, bitpix: int) -> str:
        """Map BITPIX to data type name."""
        types = {
            8: 'unsigned byte',
            16: 'signed short',
            32: 'signed int',
            64: 'signed long',
            -32: 'single float',
            -64: 'double float',
        }
        return types.get(bitpix, 'unknown')
    
    def _extract_quality_data(self, header) -> Dict[str, Any]:
        """Extract data quality/calibration information."""
        return {
            'origin': str(header.get('OBSERVAT', '')),
            'telescope_site': str(header.get('SITE', '')),
            'site_latitude': float(header.get('SITELAT', 0)) or None,
            'site_longitude': float(header.get('SITELONG', 0)) or None,
            'site_elevation': float(header.get('ELEVATIO', 0)) or None,
            'humidity': float(header.get('HUMIDITY', 0)) or None,
            'ambient_temp': float(header.get('TAMBIENT', 0)) or None,
            'pressure': float(header.get('PRESSURE', 0)) or None,
            'wind_speed': float(header.get('WINDSPD', 0)) or None,
            'wind_direction': float(header.get('WINDDIR', 0)) or None,
            'seeing': float(header.get('SEEING', 0)) or None,
            'transparency': float(header.get('TRANSPAR', 0)) or None,
            'calibration_level': str(header.get('CALIBLVL', '')),
            'data_reduced': bool(header.get('REDUCED', False)),
        }
    
    def _extract_extension_info(self, hdul) -> Dict[str, Any]:
        """Extract information about HDU extensions."""
        extensions = []
        for i, hdu in enumerate(hdul):
            if i == 0:
                continue
            ext_info = {
                'name': hdu.name,
                'type': hdu.__class__.__name__,
            }
            if hasattr(hdu, 'columns'):
                ext_info['num_columns'] = len(hdu.columns)
            if hasattr(hdu, 'data'):
                if hdu.data is not None:
                    ext_info['data_shape'] = list(hdu.data.shape) if hasattr(hdu.data, 'shape') else None
            extensions.append(ext_info)
        return extensions
    
    def _parse_basic_fits(self, filepath: str) -> Dict[str, Any]:
        """Parse FITS without astropy - basic header analysis."""
        try:
            with open(filepath, 'rb') as f:
                f.seek(0)
                simpi = f.read(80).decode('ascii', errors='replace').strip()
                if simpi != 'SIMPLE':
                    return {"error": "Not a valid FITS file (missing SIMPLE)"}
                
                f.seek(80)
                line = f.read(80).decode('ascii', errors='replace')
                bitpix = None
                naxis = None
                
                while b'END' not in line.encode():
                    if 'BITPIX' in line:
                        bitpix = int(line.split('=')[1].split('/')[0].strip())
                    elif 'NAXIS' in line:
                        naxis = int(line.split('=')[1].split('/')[0].strip())
                    line = f.read(80).decode('ascii', errors='replace')
                
                return {
                    "file_type": "FITS",
                    "parsing_mode": "basic",
                    "simple_header": True,
                    "bitpix": bitpix,
                    "naxis": naxis,
                }
        except Exception as e:
            return {"error": str(e)[:200], "parsing_mode": "failed"}
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real FITS metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is FITS."""
        ext = Path(filepath).suffix.lower()
        if ext not in ['.fits', '.fit', '.fts']:
            return False
        
        try:
            with open(filepath, 'rb') as f:
                f.seek(0)
                simpi = f.read(80).decode('ascii', errors='replace').strip()
                return simpi == 'SIMPLE'
        except:
            return False


def parse_fits(filepath: str) -> Dict[str, Any]:
    """Parse FITS file and return metadata."""
    parser = FitsParser()
    return parser.parse(filepath)
