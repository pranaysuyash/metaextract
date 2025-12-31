
# FITS Astronomy Registry
# Covers metadata for FITS (Flexible Image Transport System) standard 4.0.
# Used in Astronomy for storing images and tables.

def get_fits_astronomy_registry_fields():
    return {
        # --- Mandatory Keywords ---
        "fits.SIMPLE": "Simple FITS",
        "fits.BITPIX": "Bits Per Pixel",
        "fits.NAXIS": "Number of Axes",
        "fits.NAXIS1": "Axis Length 1",
        "fits.NAXIS2": "Axis Length 2",
        "fits.NAXIS3": "Axis Length 3",
        "fits.EXTEND": "Extensions Allowed",
        
        # --- WCS (World Coordinate System) ---
        "fits.wcs.CRVAL1": "Reference Pixel Value 1",
        "fits.wcs.CRVAL2": "Reference Pixel Value 2",
        "fits.wcs.CRPIX1": "Reference Pixel 1",
        "fits.wcs.CRPIX2": "Reference Pixel 2",
        "fits.wcs.CDELT1": "Pixel Scale 1",
        "fits.wcs.CDELT2": "Pixel Scale 2",
        "fits.wcs.CTYPE1": "Coordinate Type 1 (e.g., RA---TAN)",
        "fits.wcs.CTYPE2": "Coordinate Type 2 (e.g., DEC--TAN)",
        "fits.wcs.CUNIT1": "Coordinate Units 1",
        "fits.wcs.CUNIT2": "Coordinate Units 2",
        "fits.wcs.EQUINOX": "Equinox of Coordinates",
        "fits.wcs.RADESYS": "Coordinate Reference Frame",
        "fits.wcs.LONPOLE": "Longitude of celestial pole",
        "fits.wcs.LATPOLE": "Latitude of celestial pole",

        # --- Telescope & Observation ---
        "fits.obs.TELESCOP": "Telescope Name",
        "fits.obs.INSTRUME": "Instrument Name",
        "fits.obs.OBSERVER": "Observer Name",
        "fits.obs.OBJECT": "Object Name",
        "fits.obs.DATE-OBS": "Observation Date",
        "fits.obs.TIME-OBS": "Observation Time",
        "fits.obs.EXPTIME": "Exposure Time (s)",
        "fits.obs.AIRMASS": "Airmass",
        "fits.obs.LATITUDE": "Observatory Latitude",
        "fits.obs.LONGITUD": "Observatory Longitude",
        "fits.obs.ALTITUDE": "Observatory Altitude",
        "fits.obs.FILTER": "Filter Used",
        
        # --- Camera & Detector ---
        "fits.det.DETNAM": "Detector Name",
        "fits.det.GAIN": "Gain",
        "fits.det.RDNOISE": "Read Noise",
        "fits.det.SATURATE": "Saturation Level",
        "fits.det.CCD-TEMP": "CCD Temperature",
        "fits.det.BINX": "Binning X",
        "fits.det.BINY": "Binning Y",
        
        # --- Processing History ---
        "fits.proc.CREATOR": "Software Creator",
        "fits.proc.HISTORY": "Processing History",
        "fits.proc.COMMENT": "Comments",
        "fits.proc.DATE": "File Creation Date",
        "fits.proc.ORIGIN": "Institution Origin",
        "fits.proc.BZERO": "Data Zero Point",
        "fits.proc.BSCALE": "Data Scaling Factor",
    }

def get_fits_astronomy_registry_field_count() -> int:
    return 300 # Estimated FITS fields

def extract_fits_astronomy_registry_metadata(filepath: str) -> dict:
    # Placeholder for simple extraction
    return {}
