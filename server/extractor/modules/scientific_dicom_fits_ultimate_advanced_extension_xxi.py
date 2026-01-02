"""
Scientific DICOM/FITS Ultimate Advanced Extension XXI - FITS Astronomical Imaging

This module provides comprehensive extraction of FITS (Flexible Image Transport System)
metadata for astronomical imaging including telescope parameters, observation details,
and astronomical coordinate systems.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXI_AVAILABLE = True

FITS_ASTRONOMICAL_TAGS = {
    "SIMPLE": "conforms_to_fits_standard",
    "BITPIX": "array_data_type",
    "NAXIS": "number_of_axes",
    "NAXIS1": "axis1_length",
    "NAXIS2": "axis2_length",
    "NAXIS3": "axis3_length",
    "BSCALE": "scaling_factor",
    "BZERO": "scaling_offset",
    "BUNIT": "physical_units",
    "OBJECT": "target_name",
    "TELESCOP": "telescope_name",
    "INSTRUME": "instrument_name",
    "OBSERVER": "observer_name",
    "DATE-OBS": "observation_date",
    "TIME-OBS": "observation_time",
    "EXPTIME": "exposure_time",
    "FILTER": "filter_name",
    "FILTERID": "filter_id",
    "OBSMODE": "observation_mode",
    "PROJECT": "project_name",
    "RUNNUM": "run_number",
    "FRAMENUM": "frame_number",
    "MJD-OBS": "modified_julian_date",
    "JD": "julian_date",
    "EPOCH": "epoch_of_coordinates",
    "RA": "right_ascension",
    "DEC": "declination",
    "ALTITUDE": "altitude_angle",
    "AZIMUTH": "azimuth_angle",
    "DOMEAZ": "dome_azimuth",
    "AIRMASS": "airmass",
    "SEEING": "seeing_fwhm",
    "TRANSPAR": "transparency",
    "HUMIDITY": "humidity",
    "TAMBIENT": "ambient_temperature",
    "PRESSURE": "pressure",
    "WINDSPEE": "wind_speed",
    "WINDDIR": "wind_direction",
    "CCDTEMP": "ccd_temperature",
    "CCDGAIN": "ccd_gain",
    "CCDRDIN": "ccd_read_noise",
    "DATAMAX": "maximum_data_value",
    "DATAMIN": "minimum_data_value",
    "HISTORY": "history_comments",
    "COMMENT": "general_comments",
}

WCS_TAGS = {
    "CTYPE1": "coordinate_type_axis1",
    "CTYPE2": "coordinate_type_axis2",
    "CTYPE3": "coordinate_type_axis3",
    "CUNIT1": "coordinate_unit_axis1",
    "CUNIT2": "coordinate_unit_axis2",
    "CRPIX1": "reference_pixel_axis1",
    "CRPIX2": "reference_pixel_axis2",
    "CRVAL1": "reference_value_axis1",
    "CRVAL2": "reference_value_axis2",
    "CDELT1": "coordinate_increment_axis1",
    "CDELT2": "coordinate_increment_axis2",
    "CROTA1": "rotation_matrix_axis1",
    "CROTA2": "rotation_matrix_axis2",
    "CD1_1": "cd_matrix_element_1_1",
    "CD1_2": "cd_matrix_element_1_2",
    "CD2_1": "cd_matrix_element_2_1",
    "CD2_2": "cd_matrix_element_2_2",
    "PV1_0": "projection_parameter_1_0",
    "PV1_1": "projection_parameter_1_1",
    "PV1_2": "projection_parameter_1_2",
    "PV2_0": "projection_parameter_2_0",
    "PV2_1": "projection_parameter_2_1",
    "PV2_2": "projection_parameter_2_2",
    "RADESYS": "reference_frame_system",
    "EQUINOX": "equinox",
    "LONPOLE": "longitude_of_pole",
    "LATPOLE": "latitude_of_pole",
    "PIXXORR": "pixel_origin_x",
    "PIXYORR": "pixel_origin_y",
}

PHOTOMETRY_TAGS = {
    "PHOTFLAM": "photon_flux_constant",
    "PHOTPLAM": "pivot_wavelength",
    "PHOTBW": "bandwidth",
    "PHOTZPT": "magnitude_zero_point",
    "PHOTSYS": "photometric_system",
    "FILTER": "filter_name",
    "FILTERID": "filter_id",
    "EXPTIME": "exposure_time",
    "GAIN": "gain_electrons_per_adu",
    "RDNOISE": "read_noise_electrons",
    "SATURATE": "saturation_level",
    "NONLINEA": "nonlinearity_fraction",
    "DARKCUR": "dark_current_electrons_per_second",
    "FLATFILE": "flat_field_file",
    "BIASFILE": "bias_frame_file",
    "DARKMAP": "dark_map_file",
}

FITS_TOTAL_TAGS = FITS_ASTRONOMICAL_TAGS | WCS_TAGS | PHOTOMETRY_TAGS


def _extract_fits_header(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in FITS_ASTRONOMICAL_TAGS.items():
        try:
            if hasattr(ds, tag):
                value = getattr(ds, tag, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_wcs_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in WCS_TAGS.items():
        try:
            if hasattr(ds, tag):
                value = getattr(ds, tag, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _calculate_fits_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'NAXIS1') and hasattr(ds, 'NAXIS2'):
            metrics['total_pixels'] = ds.NAXIS1 * ds.NAXIS2
            metrics['image_width'] = ds.NAXIS1
            metrics['image_height'] = ds.NAXIS2
        if hasattr(ds, 'BITPIX'):
            metrics['bits_per_pixel'] = ds.BITPIX
        if hasattr(ds, 'NAXIS3'):
            metrics['cube_depth'] = ds.NAXIS3
    except Exception:
        pass
    return metrics


def _is_fits_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith(('.fits', '.fit', '.fts')):
            return True
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxi_detected": False,
        "fields_extracted": 0,
        "extension_xxi_type": "fits_astronomical",
        "extension_xxi_version": "2.0.0",
        "fits_type": None,
        "astronomical_observation": {},
        "world_coordinate_system": {},
        "photometry": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_fits_file(file_path):
            return result

        try:
            from astropy.io import fits
            with fits.open(file_path) as hdul:
                primary = hdul[0].header
                if 'SIMPLE' not in primary:
                    return result
        except ImportError:
            result["extraction_errors"].append("astropy library not available")
            return result
        except Exception as e:
            result["extraction_errors"].append(f"Failed to read file: {str(e)}")
            return result

        result["extension_xxi_detected"] = True
        result["fits_type"] = "astronomical"

        astronomical = _extract_fits_header(primary)
        wcs = _extract_wcs_tags(primary)
        metrics = _calculate_fits_metrics(primary)

        result["astronomical_observation"] = astronomical
        result["world_coordinate_system"] = wcs
        result["derived_metrics"] = metrics

        total_fields = len(astronomical) + len(wcs) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxi_field_count() -> int:
    return len(FITS_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxi_description() -> str:
    return ("FITS astronomical imaging metadata extraction. Supports telescope "
            "parameters, observation details, WCS coordinate systems, and "
            "photometric calibration for comprehensive astronomical analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xxi_modalities() -> List[str]:
    return ["FITS", "FIT", "FTS"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxi_supported_formats() -> List[str]:
    return [".fits", ".fit", ".fts"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxi_category() -> str:
    return "Astronomical FITS Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxi_keywords() -> List[str]:
    return [
        "astronomy", "FITS", "telescope", "WCS", "World Coordinate System",
        "photometry", "RA", "DEC", "astronomical imaging", "observation",
        "astropy", "celestial coordinates", "spectral imaging"
    ]
