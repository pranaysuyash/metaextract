"""
Scientific and Medical Metadata
Extract metadata from DICOM, FITS, OME-TIFF, and other scientific image formats
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import struct
import json
import logging

from .shared_utils import count_fields as _count_fields

logger = logging.getLogger(__name__)


GEOTIFF_KEY_NAMES = {
    1024: "GTModelTypeGeoKey",
    1025: "GTRasterTypeGeoKey",
    2048: "GeographicTypeGeoKey",
    2050: "GeogCitationGeoKey",
    2052: "GeogGeodeticDatumGeoKey",
    2054: "GeogPrimeMeridianGeoKey",
    2056: "GeogLinearUnitsGeoKey",
    2057: "GeogLinearUnitSizeGeoKey",
    2058: "GeogAngularUnitsGeoKey",
    2059: "GeogAngularUnitSizeGeoKey",
    2061: "GeogEllipsoidGeoKey",
    2062: "GeogSemiMajorAxisGeoKey",
    2063: "GeogSemiMinorAxisGeoKey",
    2064: "GeogInvFlatteningGeoKey",
    3072: "ProjectedCSTypeGeoKey",
    3075: "ProjCoordTransGeoKey",
    3076: "ProjLinearUnitsGeoKey",
    3077: "ProjLinearUnitSizeGeoKey",
    3080: "ProjStdParallel1GeoKey",
    3081: "ProjStdParallel2GeoKey",
    3082: "ProjNatOriginLongGeoKey",
    3083: "ProjNatOriginLatGeoKey",
    3084: "ProjFalseEastingGeoKey",
    3085: "ProjFalseNorthingGeoKey",
    4096: "VerticalCSTypeGeoKey",
    4099: "VerticalUnitsGeoKey",
}



# ULTRA EXPANSION FIELDS
# Additional 36 fields
ULTRA_SCIENTIFIC_MEDICAL_FIELDS = {
    "experiment_id": "unique_experiment_identifier",
    "research_group": "laboratory_institution",
    "principal_investigator": "lead_researcher_name",
    "funding_source": "grant_funding_agency",
    "project_code": "research_project_number",
    "ethics_approval": "irb_ethics_committee_id",
    "protocol_number": "experimental_protocol",
    "data_collection_date": "acquisition_datetime",
    "instrument_manufacturer": "equipment_vendor",
    "instrument_model": "device_model_number",
    "instrument_serial": "serial_identifier",
    "firmware_version": "device_firmware",
    "calibration_date": "last_calibration_timestamp",
    "maintenance_log": "service_history_records",
    "operating_parameters": "instrument_settings",
    "measurement_type": "observation_category",
    "measurement_unit": "si_unit_of_measure",
    "measurement_precision": "uncertainty_error_range",
    "sampling_rate": "data_acquisition_frequency",
    "integration_time": "signal_accumulation_duration",
    "detection_limit": "minimum_detectable_amount",
    "quantitation_limit": "quantification_threshold",
    "sample_id": "specimen_identifier",
    "sample_type": "biological_material_category",
    "sample_source": "origin_tissue_organism",
    "collection_date": "sample_acquisition_date",
    "storage_conditions": "temperature_humidity_storage",
    "preparation_method": "sample_processing_protocol",
    "quality_metrics": "sample_quality_assessment",
    "processing_software": "analysis_application",
    "processing_version": "software_version",
    "processing_parameters": "algorithm_settings",
    "corrections_applied": "data_corrections",
    "normalization_method": "data_standardization",
    "quality_control": "qc_measures_applied",
    "validation_status": "data_validation_result",
}


# MEGA EXPANSION FIELDS
# Additional 52 fields
MEGA_SCIENTIFIC_MEDICAL_FIELDS = {
    "modality": "ct_mri_ultrasound_pet_spect",
    "scan_protocol": "imaging_sequence",
    "contrast_agent": "gadolinium_iodine_barium",
    "contrast_dosage": "agent_volume_ml",
    "scan_parameters": "tr_te_flip_angle",
    "repetition_time": "tr_milliseconds",
    "echo_time": "te_milliseconds",
    "inversion_time": "ti_milliseconds",
    "flip_angle": "rf_excitation_degrees",
    "field_strength": "magnet_tesla_1_5_3_7",
    "pixel_spacing": "mm_per_pixel",
    "slice_thickness": "image_slice_mm",
    "slice_gap": "inter_slice_gap",
    "image_orientation": "axial_sagittal_coronal",
    "acquisition_matrix": "scan_dimensions",
    "fov": "field_of_view_cm",
    "reconstruction_algorithm": "filtered_back_projection",
    "kernel_type": "soft_sharp_lung_bone",
    "window_center": "display_center_hu",
    "window_width": "display_range_hu",
    "treatment_machine": "linear_accelerator",
    "beam_energy": "photon_mv_electron_mev",
    "beam_modality": "photons_electrons_protons",
    "gantry_angle": "treatment_head_angle",
    "collimator_opening": "beam_field_size",
    "mu_gating": "motion_management",
    "fraction_dose": "daily_dose_gy",
    "total_dose": "cumulative_dose_gy",
    "treatment_fractions": "number_of_sessions",
    "target_volume": "treatment_area_cc",
    "organ_at_risk": "critical_structure_dose",
    "sequencing_platform": "illumina_ion_torrent_pacbio",
    "sequencing_chemistry": "library_prep_kit",
    "read_length": "base_pair_read_length",
    "read_quality": "phred_quality_score",
    "coverage_depth": "sequencing_depth_x",
    "variant_type": "snp_indel_structural_variant",
    "genomic_coordinates": "chromosome_position",
    "reference_genome": "grch38_hg19",
    "variant_annotation": "clinical_significance",
    "allele_frequency": "population_frequency",
    "pathogenicity": "disease_causing_variant",
    "test_method": "assay_technique",
    "test_unit": "measurement_units",
    "reference_range": "normal_values",
    "sensitivity": "test_true_positive_rate",
    "specificity": "test_true_negative_rate",
    "positive_predictive": "ppv_probability",
    "negative_predictive": "npv_probability",
}

def _parse_geokey_directory(key_dir, double_params=None, ascii_params=None) -> Dict[str, Any]:
    if not key_dir:
        return {}
    if isinstance(key_dir, bytes):
        if len(key_dir) % 2 == 1:
            return {}
        key_dir = list(struct.unpack("<" + "H" * (len(key_dir) // 2), key_dir))
    else:
        key_dir = list(key_dir)

    if len(key_dir) < 4:
        return {}
    version, rev, minor, key_count = key_dir[0:4]
    result = {
        "version": version,
        "revision": rev,
        "minor_revision": minor,
        "key_count": key_count,
        "keys": [],
    }
    if isinstance(double_params, bytes):
        double_params = list(struct.unpack("<" + "d" * (len(double_params) // 8), double_params))
    if isinstance(ascii_params, bytes):
        try:
            ascii_params = ascii_params.decode("latin1", errors="ignore")
        except Exception:
            ascii_params = None

    for i in range(key_count):
        start = 4 + i * 4
        if start + 4 > len(key_dir):
            break
        key_id, tiff_tag_location, count, value_offset = key_dir[start:start + 4]
        key_name = GEOTIFF_KEY_NAMES.get(key_id, str(key_id))
        value = None
        if tiff_tag_location == 0:
            value = value_offset
        elif tiff_tag_location == 34736 and double_params:
            value = double_params[value_offset:value_offset + count]
        elif tiff_tag_location == 34737 and ascii_params:
            value = ascii_params[value_offset:value_offset + count]
            if isinstance(value, str):
                value = value.rstrip("|")
        result["keys"].append({
            "key_id": key_id,
            "key_name": key_name,
            "tiff_tag_location": tiff_tag_location,
            "count": count,
            "value_offset": value_offset,
            "value": value,
        })
    return result


def _parse_geotiff_tags(tiff_tags: Dict[int, Any]) -> Dict[str, Any]:
    geo = {}
    model_pixel_scale = tiff_tags.get(33550)
    if model_pixel_scale:
        geo["model_pixel_scale"] = list(model_pixel_scale)
    model_tiepoint = tiff_tags.get(33922)
    if model_tiepoint:
        geo["model_tiepoint"] = list(model_tiepoint)
    model_transform = tiff_tags.get(34264)
    if model_transform:
        geo["model_transformation"] = list(model_transform)
    geo_keys = tiff_tags.get(34735)
    geo_double = tiff_tags.get(34736)
    geo_ascii = tiff_tags.get(34737)
    if geo_keys:
        geo["geokey_directory"] = _parse_geokey_directory(geo_keys, geo_double, geo_ascii)
    if geo_ascii:
        if isinstance(geo_ascii, bytes):
            geo["geo_ascii_params"] = geo_ascii.decode("latin1", errors="ignore").rstrip("|")
        else:
            geo["geo_ascii_params"] = str(geo_ascii)
    if geo_double:
        if isinstance(geo_double, bytes):
            geo["geo_double_params"] = list(struct.unpack("<" + "d" * (len(geo_double) // 8), geo_double))
        else:
            geo["geo_double_params"] = list(geo_double)
    return geo


def _detect_tiff_subtype(filepath: str) -> Optional[str]:
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            tags = getattr(img, "tag_v2", {})
            description = tags.get(270, "")
            if isinstance(description, bytes):
                description = description.decode("utf-8", errors="ignore")
            if any(tag in tags for tag in [33550, 33922, 34264, 34735, 34736, 34737]):
                return "GEOTIFF"
            if "OME" in description or "ome" in description:
                return "OME-TIFF"
    except Exception:
        return None
    return None


def _parse_las_header(filepath: str) -> Dict[str, Any]:
    las = {}
    try:
        with open(filepath, "rb") as f:
            sig = f.read(4)
            if sig != b"LASF":
                return las
            las["signature"] = "LASF"
            las["file_source_id"] = struct.unpack("<H", f.read(2))[0]
            las["global_encoding"] = struct.unpack("<H", f.read(2))[0]
            guid = f.read(16)
            if len(guid) == 16:
                las["project_id_guid"] = guid.hex()
            las["version_major"] = struct.unpack("<B", f.read(1))[0]
            las["version_minor"] = struct.unpack("<B", f.read(1))[0]
            las["system_identifier"] = f.read(32).rstrip(b"\x00").decode("latin1", errors="ignore")
            las["generating_software"] = f.read(32).rstrip(b"\x00").decode("latin1", errors="ignore")
            las["file_creation_day"] = struct.unpack("<H", f.read(2))[0]
            las["file_creation_year"] = struct.unpack("<H", f.read(2))[0]
            header_size = struct.unpack("<H", f.read(2))[0]
            las["header_size"] = header_size
            las["offset_to_point_data"] = struct.unpack("<I", f.read(4))[0]
            las["num_vlrs"] = struct.unpack("<I", f.read(4))[0]
            las["point_data_format"] = struct.unpack("<B", f.read(1))[0]
            las["point_data_record_length"] = struct.unpack("<H", f.read(2))[0]
            las["num_point_records"] = struct.unpack("<I", f.read(4))[0]
            las["num_points_by_return"] = list(struct.unpack("<5I", f.read(20)))
            las["scale_factors"] = list(struct.unpack("<3d", f.read(24)))
            las["offsets"] = list(struct.unpack("<3d", f.read(24)))
            las["max_x"], las["min_x"] = struct.unpack("<2d", f.read(16))
            las["max_y"], las["min_y"] = struct.unpack("<2d", f.read(16))
            las["max_z"], las["min_z"] = struct.unpack("<2d", f.read(16))

            if header_size >= 375:
                f.seek(247, 0)
                las["start_of_waveform_data"] = struct.unpack("<Q", f.read(8))[0]
                las["start_of_first_evlr"] = struct.unpack("<Q", f.read(8))[0]
                las["number_of_evlrs"] = struct.unpack("<I", f.read(4))[0]
                las["num_point_records_14"] = struct.unpack("<Q", f.read(8))[0]
                las["num_points_by_return_14"] = list(struct.unpack("<15Q", f.read(120)))
    except Exception:
        return las
    return las


def _parse_las_vlrs(filepath: str, offset: int, count: int) -> Dict[str, Any]:
    vlr_info = {
        "vlr_count": 0,
        "vlrs": [],
        "projection": {},
    }
    try:
        with open(filepath, "rb") as f:
            f.seek(offset, 0)
            for _ in range(count):
                header = f.read(54)
                if len(header) < 54:
                    break
                user_id = header[2:18].rstrip(b"\x00").decode("latin1", errors="ignore")
                record_id = struct.unpack("<H", header[18:20])[0]
                record_length = struct.unpack("<H", header[20:22])[0]
                description = header[22:54].rstrip(b"\x00").decode("latin1", errors="ignore")
                data = f.read(record_length)
                vlr_info["vlrs"].append({
                    "user_id": user_id,
                    "record_id": record_id,
                    "record_length": record_length,
                    "description": description,
                })
                vlr_info["vlr_count"] += 1
                if user_id == "LASF_Projection" and record_id in [34735, 34736, 34737]:
                    if record_id == 34735:
                        geokeys = _parse_geokey_directory(data)
                        if geokeys:
                            vlr_info["projection"]["geokey_directory"] = geokeys
                    elif record_id == 34736:
                        try:
                            doubles = struct.unpack("<" + "d" * (len(data) // 8), data)
                            vlr_info["projection"]["geo_double_params"] = list(doubles)
                        except Exception:
                            pass
                    elif record_id == 34737:
                        vlr_info["projection"]["geo_ascii_params"] = data.decode("latin1", errors="ignore").rstrip("|")
                if user_id == "LASF_Projection" and record_id in [2112, 2111]:
                    try:
                        vlr_info["projection"]["wkt"] = data.decode("utf-8", errors="ignore").strip()
                    except Exception:
                        pass
    except Exception:
        return vlr_info
    return vlr_info

def extract_scientific_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract scientific/medical metadata from supported file formats.

    Args:
        filepath: Path to image/file

    Returns:
        Dictionary with scientific metadata
    """
    result = {
        "format_type": None,
        "scientific": {},
        "fields_extracted": 0
    }

    ext = Path(filepath).suffix.lower()

    if ext in ['.dcm', '.dcim', '.dicom']:
        result = extract_dicom_metadata(filepath, result)
    elif ext in ['.fits', '.fit', '.fts']:
        result = extract_fits_metadata(filepath, result)
    elif ext in ['.tif', '.tiff']:
        subtype = _detect_tiff_subtype(filepath)
        if subtype == "GEOTIFF":
            result = extract_geotiff_metadata(filepath, result)
        elif subtype == "OME-TIFF":
            result = extract_ome_tiff_metadata(filepath, result)
        else:
            result = extract_generic_tiff_metadata(filepath, result)
    elif ext in ['.czi', '.lif', '.nd2']:
        result = extract_microscopy_metadata(filepath, result, ext)
    elif ext in ['.ome.xml']:
        result = extract_ome_xml_metadata(filepath, result)
    elif ext in ['.las', '.laz']:
        result = extract_las_metadata(filepath, result)

    return result


def extract_dicom_metadata(filepath: str, result: Dict) -> Dict:
    """Extract DICOM medical imaging metadata."""
    result["format_type"] = "DICOM"

    dicom_data = {}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(132)

            if header[128:132] == b'DICM':
                dicom_data["valid_dicom"] = True

                f.seek(132)
                preamble = f.read(4)

                import pydicom
                ds = pydicom.dcmread(filepath)

                DICOM_PATIENT_TAGS = [
                    (0x0010, 0x0010, "patient_name"),
                    (0x0010, 0x0020, "patient_id"),
                    (0x0010, 0x0030, "patient_birth_date"),
                    (0x0010, 0x0040, "patient_sex"),
                    (0x0010, 0x1010, "patient_age"),
                    (0x0010, 0x1020, "patient_size"),
                    (0x0010, 0x1030, "patient_weight"),
                    (0x0010, 0x1040, "patient_address"),
                    (0x0010, 0x1080, "military_rank"),
                    (0x0010, 0x1090, "medical_record_locator"),
                    (0x0010, 0x2000, "medical_alerts"),
                    (0x0010, 0x2110, "allergies"),
                    (0x0010, 0x2150, "patient_comments"),
                    (0x0010, 0x2152, "patient_ethnic_group"),
                    (0x0010, 0x2160, "patient_religion"),
                    (0x0010, 0x2180, "patient_pregnancy_status"),
                    (0x0010, 0x21B0, "additional_patient_history"),
                    (0x0010, 0x21C0, "patient_state"),
                    (0x0010, 0x21D0, "last_menstrual_date"),
                    (0x0010, 0x21F0, "patient_telephone_numbers"),
                    (0x0010, 0x2200, "responsible_person"),
                    (0x0010, 0x2292, "responsible_organization"),
                    (0x0010, 0x4000, "patient_instructions"),
                ]

                for tag_group, tag_elem, name in DICOM_PATIENT_TAGS:
                    try:
                        value = ds.get((tag_group, tag_elem), None)
                        if value:
                            dicom_data[name] = str(value)
                    except Exception as e:
                        logger.debug(f"Failed to extract DICOM patient tag {name}: {e}")

                DICOM_STUDY_TAGS = [
                    (0x0020, 0x000D, "study_instance_uid"),
                    (0x0008, 0x1030, "study_description"),
                    (0x0008, 0x0020, "study_date"),
                    (0x0008, 0x0030, "study_time"),
                    (0x0008, 0x0050, "accession_number"),
                    (0x0008, 0x0090, "referring_physician_name"),
                    (0x0008, 0x0094, "referring_physician_telephone"),
                    (0x0008, 0x0096, "referring_physician_address"),
                    (0x0008, 0x0098, "study_id"),
                    (0x0008, 0x0201, "timezone_offset"),
                    (0x0020, 0x0010, "study_number"),
                    (0x0032, 0x000A, "study_status_id"),
                    (0x0032, 0x000C, "study_priority_id"),
                    (0x0032, 0x1030, "study_verified_date"),
                    (0x0032, 0x1031, "study_verified_time"),
                    (0x0032, 0x1050, "study_read_date"),
                    (0x0032, 0x1051, "study_read_time"),
                    (0x0040, 0xA300, "study_completed_date"),
                    (0x0040, 0xA301, "study_completed_time"),
                    (0x0040, 0xA307, "study_verified_physician"),
                ]

                for tag_group, tag_elem, name in DICOM_STUDY_TAGS:
                    try:
                        value = ds.get((tag_group, tag_elem), None)
                        if value:
                            dicom_data[name] = str(value)
                    except Exception as e:
                        logger.debug(f"Failed to extract DICOM study tag {name}: {e}")

                DICOM_SERIES_TAGS = [
                    (0x0020, 0x000E, "series_instance_uid"),
                    (0x0008, 0x0060, "modality"),
                    (0x0020, 0x0011, "series_number"),
                    (0x0008, 0x103E, "series_description"),
                    (0x0020, 0x0006, "referenced_frame_number"),
                    (0x0008, 0x0021, "series_date"),
                    (0x0008, 0x0031, "series_time"),
                    (0x0018, 0x0015, "body_part_examined"),
                    (0x0018, 0x0020, "patient_position"),
                    (0x0018, 0x0021, "sequence_name"),
                    (0x0018, 0x0024, "sequence_variant"),
                    (0x0018, 0x0025, "scan_options"),
                    (0x0018, 0x0050, "slice_thickness"),
                    (0x0018, 0x0080, "repetition_time"),
                    (0x0018, 0x0081, "echo_time"),
                    (0x0018, 0x0082, "inversion_time"),
                    (0x0018, 0x0083, "number_of_averages"),
                    (0x0018, 0x0084, "imaging_frequency"),
                    (0x0018, 0x0085, "echo_number"),
                    (0x0018, 0x0086, "magnetic_field_strength"),
                    (0x0018, 0x0087, "spacing_between_slices"),
                    (0x0018, 0x0088, "number_of_phase_encoding_steps"),
                    (0x0018, 0x0089, "data_acquisition_dead_time"),
                    (0x0018, 0x0090, "pixel_bandwidth"),
                    (0x0018, 0x1020, "software_versions"),
                    (0x0018, 0x1030, "protocol_name"),
                    (0x0018, 0x1040, "transmitter_coil"),
                    (0x0018, 0x1050, "receive_coil"),
                    (0x0018, 0x1060, "flip_angle"),
                    (0x0018, 0x1080, "sar"),
                    (0x0018, 0x1094, "dwi_b_value"),
                    (0x0018, 0x1095, "dwi_gradient_direction"),
                    (0x0018, 0x1100, "probe_drive_application"),
                    (0x0018, 0x1240, "receive_gain"),
                    (0x0018, 0x1250, "transmit_gain"),
                    (0x0018, 0x1251, "pre_amp_duty_cycle"),
                    (0x0018, 0x9004, "contrast_bolus_agent"),
                    (0x0018, 0x9010, "contrast_bolus_start_time"),
                    (0x0018, 0x9012, "contrast_bolus_duration"),
                    (0x0018, 0x9014, "contrast_bolus_stopped"),
                    (0x0018, 0x9016, "contrast_bolus_administered"),
                    (0x0018, 0x9018, "contrast_bolus_volume"),
                    (0x0018, 0x9020, "mr_gradient_moment"),
                    (0x0020, 0x0037, "image_orientation"),
                    (0x0020, 0x0050, "slice_location"),
                    (0x0020, 0x0100, "temporal_position_identifier"),
                    (0x0020, 0x0105, "number_of_temporal_positions"),
                    (0x0020, 0x0128, "number_of_frames"),
                    (0x0020, 0x0013, "instance_number"),
                ]

                for tag_group, tag_elem, name in DICOM_SERIES_TAGS:
                    try:
                        value = ds.get((tag_group, tag_elem), None)
                        if value:
                            dicom_data[name] = str(value)
                    except Exception as e:
                        logger.debug(f"Failed to extract DICOM series tag {name}: {e}")

                DICOM_IMAGE_TAGS = [
                    (0x0008, 0x0008, "image_type"),
                    (0x0008, 0x0018, "sop_instance_uid"),
                    (0x0008, 0x0023, "content_date"),
                    (0x0008, 0x0033, "content_time"),
                    (0x0020, 0x0013, "instance_number"),
                    (0x0028, 0x0002, "samples_per_pixel"),
                    (0x0028, 0x0004, "photometric_interpretation"),
                    (0x0028, 0x0006, "planar_configuration"),
                    (0x0028, 0x0008, "number_of_frames"),
                    (0x0028, 0x0010, "rows"),
                    (0x0028, 0x0011, "columns"),
                    (0x0028, 0x0034, "pixel_aspect_ratio"),
                    (0x0028, 0x0100, "bits_allocated"),
                    (0x0028, 0x0101, "bits_stored"),
                    (0x0028, 0x0102, "high_bit"),
                    (0x0028, 0x0103, "pixel_representation"),
                    (0x0028, 0x0106, "smallest_image_pixel_value"),
                    (0x0028, 0x0107, "largest_image_pixel_value"),
                    (0x0028, 0x0120, "pixel_padding_value"),
                    (0x0028, 0x1050, "window_center"),
                    (0x0028, 0x1051, "window_width"),
                    (0x0028, 0x1052, "window_center_width_explanation"),
                    (0x0028, 0x1053, "rescale_intercept"),
                    (0x0028, 0x1054, "rescale_slope"),
                    (0x0028, 0x1055, "rescale_type"),
                    (0x0028, 0x1080, "modalities_in_phantom"),
                    (0x0028, 0x1090, "pixel_intensity_relationship"),
                    (0x0028, 0x1091, "pixel_intensity_relationship_sign"),
                    (0x0028, 0x1100, "calibration_object"),
                    (0x0028, 0x1101, "calibration_date"),
                    (0x0028, 0x1102, "calibration_time"),
                    (0x0028, 0x1200, "foreground_pixel_value"),
                    (0x0028, 0x1201, "background_pixel_value"),
                    (0x0028, 0x2000, "icc_profile"),
                    (0x0028, 0x2110, "lossy_image_compression"),
                    (0x0028, 0x2112, "lossy_image_compression_ratio"),
                    (0x0028, 0x2114, "lossy_image_compression_method"),
                    (0x0040, 0x0244, "study_segmentation_start"),
                    (0x0040, 0x0245, "study_segmentation_end"),
                    (0x0040, 0x0250, "segmentation_algorithm"),
                    (0x0040, 0x0251, "segmentation_algorithm_description"),
                    (0x0050, 0x0010, "calibration_phantom"),
                    (0x7FE0, 0x0010, "pixel_data_offset"),
                    (0x7FE0, 0x0020, "pixel_data_length"),
                ]

                for tag_group, tag_elem, name in DICOM_IMAGE_TAGS:
                    try:
                        value = ds.get((tag_group, tag_elem), None)
                        if value:
                            dicom_data[name] = str(value)
                    except Exception as e:
                        logger.debug(f"Failed to extract DICOM image tag {name}: {e}")

                DICOM_EQUIPMENT_TAGS = [
                    (0x0008, 0x0070, "manufacturer"),
                    (0x0008, 0x0080, "institution_name"),
                    (0x0008, 0x0081, "institution_address"),
                    (0x0008, 0x0090, "referring_physician_name"),
                    (0x0008, 0x1010, "station_name"),
                    (0x0008, 0x1011, "procedure_log_location"),
                    (0x0008, 0x1012, "station_name_code"),
                    (0x0008, 0x1020, "software_versions"),
                    (0x0008, 0x1030, "study_description"),
                    (0x0008, 0x1040, "institutional_department_name"),
                    (0x0008, 0x1048, "physicians_of_record"),
                    (0x0008, 0x1050, "institution_code"),
                    (0x0008, 0x1090, "manufacturer_model_name"),
                    (0x0008, 0x1091, "device_serial_number"),
                    (0x0008, 0x1100, "secondary_capture_device_id"),
                    (0x0008, 0x1111, "referenced_performed_procedure_step"),
                    (0x0018, 0x1000, "device_serial_number"),
                    (0x0018, 0x1002, "device_uid"),
                    (0x0018, 0x1004, "plate_id"),
                    (0x0018, 0x1005, "generative_model"),
                    (0x0018, 0x1010, "secondary_capture_device_manufacturer"),
                    (0x0018, 0x1011, "secondary_capture_device_model"),
                    (0x0018, 0x1012, "secondary_capture_device_software"),
                    (0x0018, 0x1018, "secondary_capture_device_version"),
                    (0x0018, 0x1020, "software_versions"),
                    (0x0018, 0x1200, "date_of_secondary_capture"),
                    (0x0018, 0x1201, "time_of_secondary_capture"),
                    (0x0018, 0x1202, "secondary_capture_device_processing_description"),
                    (0x0018, 0x1203, "secondary_capture_device_processing_parameters"),
                    (0x0018, 0x1204, "external_video_input_signal"),
                ]

                for tag_group, tag_elem, name in DICOM_EQUIPMENT_TAGS:
                    try:
                        value = ds.get((tag_group, tag_elem), None)
                        if value:
                            dicom_data[name] = str(value)
                    except Exception as e:
                        logger.debug(f"Failed to extract DICOM equipment tag {name}: {e}")

                DICOM_VOI_LUT_TAGS = [
                    (0x0028, 0x1056, "voilut_function"),
                    (0x0028, 0x1057, "lut_data"),
                    (0x0028, 0x3010, "lut_descriptor"),
                    (0x0028, 0x3011, "lut_data"),
                    (0x0028, 0x3012, "lut_type"),
                    (0x0028, 0x3015, "lut_explanation"),
                ]

                for tag_group, tag_elem, name in DICOM_VOI_LUT_TAGS:
                    try:
                        value = ds.get((tag_group, tag_elem), None)
                        if value:
                            dicom_data[name] = str(value)
                    except Exception as e:
                        logger.debug(f"Failed to extract DICOM VOI LUT tag {name}: {e}")

                DICOM_SOP_TAGS = [
                    (0x0008, 0x0016, "sop_class_uid"),
                    (0x0008, 0x0018, "sop_instance_uid"),
                    (0x0008, 0x0019, "sop_instance_creation_time"),
                    (0x0008, 0x0020, "study_date"),
                    (0x0008, 0x0021, "series_date"),
                    (0x0008, 0x0022, "acquisition_date"),
                    (0x0008, 0x0023, "content_date"),
                    (0x0008, 0x0030, "study_time"),
                    (0x0008, 0x0031, "series_time"),
                    (0x0008, 0x0032, "acquisition_time"),
                    (0x0008, 0x0033, "content_time"),
                    (0x0008, 0x0060, "modality"),
                    (0x0008, 0x0064, "conversion_type"),
                    (0x0008, 0x0068, "presentation_intent_type"),
                    (0x0008, 0x0100, "copyright"),
                    (0x0008, 0x0201, "timezone_offset"),
                ]

                for tag_group, tag_elem, name in DICOM_SOP_TAGS:
                    try:
                        value = ds.get((tag_group, tag_elem), None)
                        if value:
                            dicom_data[name] = str(value)
                    except Exception as e:
                        logger.debug(f"Failed to extract DICOM SOP tag {name}: {e}")

                if hasattr(ds, 'pixel_array'):
                    dicom_data["has_pixel_data"] = True
                    dicom_data["pixel_array_shape"] = str(ds.pixel_array.shape)
                    dicom_data["pixel_array_dtype"] = str(ds.pixel_array.dtype)

    except ImportError:
        dicom_data["pydicom_not_available"] = True
        dicom_data["note"] = "Install pydicom for full DICOM support"
    except Exception as e:
        dicom_data["extraction_error"] = str(e)[:100]

    result["scientific"] = dicom_data
    result["fields_extracted"] = len(dicom_data)
    return result


def extract_fits_metadata(filepath: str, result: Dict) -> Dict:
    """Extract FITS astronomy image metadata."""
    result["format_type"] = "FITS"

    fits_data = {}

    try:
        with open(filepath, 'rb') as f:
            header_lines = []
            line = f.read(80)

            while line and line != b'END' + b' ' * 77:
                header_lines.append(line)
                if len(header_lines) > 1000:
                    break
                line = f.read(80)

            for line in header_lines:
                line_str = line.decode('ascii', errors='replace')
                if '=' in line_str and '/' in line_str:
                    key = line_str.split('=')[0].strip()
                    value_part = line_str.split('=')[1].split('/')[0].strip()
                    if key and len(key) <= 8 and value_part:
                        fits_data[key.strip()] = value_part.strip()
                elif '=' in line_str:
                    parts = line_str.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and len(key) <= 8:
                            fits_data[key] = value

        if 'TELESCOP' in fits_data:
            fits_data["telescope"] = fits_data['TELESCOP']
        if 'INSTRUME' in fits_data:
            fits_data["instrument"] = fits_data['INSTRUME']
        if 'OBSERVER' in fits_data:
            fits_data["observer"] = fits_data['OBSERVER']
        if 'DATE-OBS' in fits_data:
            fits_data["observation_date"] = fits_data['DATE-OBS']
        if 'EXPTIME' in fits_data:
            fits_data["exposure_time"] = fits_data['EXPTIME']
        if 'FILTER' in fits_data:
            fits_data["filter_used"] = fits_data['FILTER']
        if 'OBJECT' in fits_data:
            fits_data["target_object"] = fits_data['OBJECT']
        if 'BITPIX' in fits_data:
            fits_data["bits_per_pixel"] = fits_data['BITPIX']
        if 'NAXIS' in fits_data:
            fits_data["number_of_axes"] = fits_data['NAXIS']

    except Exception as e:
        fits_data["extraction_error"] = str(e)[:100]

    result["scientific"] = fits_data
    result["fields_extracted"] = len(fits_data)
    return result


def extract_geotiff_metadata(filepath: str, result: Dict) -> Dict:
    """Extract GeoTIFF metadata."""
    result["format_type"] = "GEOTIFF"
    geo_data: Dict[str, Any] = {}

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            tags = getattr(img, "tag_v2", {})
            geo_data["tiff_tag_count"] = len(tags)
            geo_data.update(_parse_geotiff_tags(tags))
            description = tags.get(270, "")
            if isinstance(description, bytes):
                description = description.decode("utf-8", errors="ignore")
            if description:
                geo_data["image_description"] = description[:200]
    except Exception as e:
        geo_data["extraction_error"] = str(e)[:100]

    result["scientific"] = geo_data
    result["fields_extracted"] = _count_fields(geo_data)
    return result


def extract_generic_tiff_metadata(filepath: str, result: Dict) -> Dict:
    """Extract generic TIFF tags when no specific subtype detected."""
    result["format_type"] = "TIFF"
    tiff_data: Dict[str, Any] = {}

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            tags = getattr(img, "tag_v2", {})
            tiff_data["tiff_tag_count"] = len(tags)
            for tag, value in tags.items():
                tiff_data[f"tiff_tag_{tag}"] = str(value)[:200]
            if hasattr(img, "n_frames"):
                tiff_data["number_of_frames"] = img.n_frames
            if hasattr(img, "is_animated"):
                tiff_data["is_animated"] = img.is_animated
    except Exception as e:
        tiff_data["extraction_error"] = str(e)[:100]

    result["scientific"] = tiff_data
    result["fields_extracted"] = _count_fields(tiff_data)
    return result


def extract_las_metadata(filepath: str, result: Dict) -> Dict:
    """Extract LAS/LAZ point cloud metadata."""
    result["format_type"] = "LAS"
    las_data: Dict[str, Any] = {}

    header = _parse_las_header(filepath)
    if header:
        las_data.update(header)
        vlr_info = _parse_las_vlrs(filepath, header.get("header_size", 0), header.get("num_vlrs", 0))
        las_data["vlr_info"] = vlr_info
    else:
        las_data["extraction_error"] = "Invalid LAS header"

    result["scientific"] = las_data
    result["fields_extracted"] = _count_fields(las_data)
    return result


def extract_ome_tiff_metadata(filepath: str, result: Dict) -> Dict:
    """Extract OME-TIFF microscopy metadata."""
    result["format_type"] = "OME-TIFF"

    ome_data = {}

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            if hasattr(img, 'tag_v2'):
                for tag, value in img.tag_v2.items():
                    tag_name = str(tag)
                    ome_data[f"tiff_tag_{tag_name}"] = str(value)[:200]

            description = img.tag_v2.get(270, "")
            if isinstance(description, bytes):
                description = description.decode('utf-8', errors='replace')

            if 'OME' in description or 'xml' in description.lower():
                ome_data["ome_xml_present"] = True
                ome_data["description_length"] = len(description)

                if '<?xml' in description:
                    ome_data["has_xml_header"] = True

            if hasattr(img, 'n_frames'):
                ome_data["number_of_frames"] = img.n_frames
            if hasattr(img, 'is_animated'):
                ome_data["is_animated"] = img.is_animated

    except Exception as e:
        ome_data["extraction_error"] = str(e)[:100]

    result["scientific"] = ome_data
    result["fields_extracted"] = len(ome_data)
    return result


def extract_microscopy_metadata(filepath: str, result: Dict, ext: str) -> Dict:
    """Extract metadata from microscopy file formats (CZI, LIF, ND2)."""
    result["format_type"] = "MICROSCOPY"

    micro_data = {}

    if ext == '.czi':
        micro_data["format"] = "Carl Zeiss Image (CZI)"
        micro_data["zeiss_czi"] = True
    elif ext == '.lif':
        micro_data["format"] = "Leica Image File (LIF)"
        micro_data["leica_lif"] = True
    elif ext == '.nd2':
        micro_data["format"] = "Nikon ND2"
        micro_data["nikon_nd2"] = True

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            if hasattr(img, 'tag_v2'):
                for tag, value in img.tag_v2.items():
                    micro_data[f"tiff_tag_{tag}"] = str(value)[:100]

            if hasattr(img, 'n_frames'):
                micro_data["number_of_frames"] = img.n_frames
            if hasattr(img, 'n_frames') and img.n_frames > 1:
                micro_data["is_multi_channel"] = True

    except Exception as e:
        logger.debug(f"Failed to extract TIFF/Image tags from microscopy file: {e}")

    micro_data["microscopy_detected"] = True
    result["scientific"] = micro_data
    result["fields_extracted"] = len(micro_data)
    return result


def extract_ome_xml_metadata(filepath: str, result: Dict) -> Dict:
    """Extract OME-XML metadata."""
    result["format_type"] = "OME-XML"

    ome_xml_data = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        if '<?xml' in content:
            ome_xml_data["valid_xml"] = True

        if '<OME' in content:
            ome_xml_data["ome_root_element"] = True

        if '<Image' in content:
            image_count = content.count('<Image ')
            ome_xml_data["image_count"] = image_count

        if '<Channel' in content:
            channel_count = content.count('<Channel')
            ome_xml_data["channel_count"] = channel_count

        if '<Pixels' in content:
            pixels_count = content.count('<Pixels')
            ome_xml_data["pixels_elements"] = pixels_count

        if '<Plane' in content:
            plane_count = content.count('<Plane')
            ome_xml_data["plane_count"] = plane_count

        if '<PhysicalSize' in content:
            ome_xml_data["has_physical_size"] = True

        if '<ObjectiveSettings' in content:
            ome_xml_data["has_objective_settings"] = True

    except Exception as e:
        ome_xml_data["extraction_error"] = str(e)[:100]

    result["scientific"] = ome_xml_data
    result["fields_extracted"] = len(ome_xml_data)
    return result


def get_scientific_medical_field_count() -> int:
    """Return total number of scientific_medical metadata fields."""
    total = 0
    total += len(GEOTIFF_KEY_NAMES)
    total += len(ULTRA_SCIENTIFIC_MEDICAL_FIELDS)
    total += len(MEGA_SCIENTIFIC_MEDICAL_FIELDS)
    total += len(MICROSCOPY_EXTENDED)
    total += len(OME_TIFF_EXTENDED)
    total += len(BIO_FORMATS_EXTENDED)
    total += len(LIDAR_EXTENSIONS)
    total += len(REMOTE_SENSING_EXTENSIONS)
    total += len(MICROSCOPY_ANALYSIS_EXTENSIONS)
    return total


def get_scientific_field_count() -> int:
    """Backward-compatible alias for get_scientific_medical_field_count."""
    return get_scientific_medical_field_count()


def analyze_scientific_metadata(metadata: Dict) -> Dict:
    """Analyze scientific metadata for completeness and quality."""
    analysis = {
        "completeness_score": 0.0,
        "data_quality": "unknown",
        "issues": [],
        "recommendations": []
    }

    if not metadata or "scientific" not in metadata:
        analysis["issues"].append("No scientific metadata found")
        analysis["recommendations"].append("Check if file format is supported")
        return analysis

    scientific = metadata.get("scientific", {})
    field_count = len(scientific)

    if field_count >= 50:
        analysis["completeness_score"] = 1.0
        analysis["data_quality"] = "excellent"
    elif field_count >= 20:
        analysis["completeness_score"] = 0.7
        analysis["data_quality"] = "good"
    elif field_count >= 10:
        analysis["completeness_score"] = 0.4
        analysis["data_quality"] = "fair"
    else:
        analysis["completeness_score"] = 0.2
        analysis["data_quality"] = "limited"
        analysis["issues"].append("Limited metadata available")

    format_type = metadata.get("format_type")
    if format_type == "DICOM":
        if "patient_name" not in scientific and "patient_id" not in scientific:
            analysis["issues"].append("Missing patient identification")
        if "modality" not in scientific:
            analysis["issues"].append("Missing imaging modality")
        if "has_pixel_data" not in scientific:
            analysis["recommendations"].append("Verify pixel data availability")

    elif format_type == "FITS":
        if "TELESCOP" not in scientific:
            analysis["issues"].append("Missing telescope information")
        if "OBJECT" not in scientific:
            analysis["issues"].append("Missing target object information")
        if "EXPTIME" not in scientific:
            analysis["issues"].append("Missing exposure time")
    elif format_type == "GEOTIFF":
        if "geokey_directory" not in scientific:
            analysis["issues"].append("Missing GeoKeyDirectoryTag")
        if "model_pixel_scale" not in scientific and "model_tiepoint" not in scientific:
            analysis["issues"].append("Missing georeferencing tags")
    elif format_type == "LAS":
        if "point_data_format" not in scientific:
            analysis["issues"].append("Missing point data format")
        if "num_point_records" not in scientific:
            analysis["issues"].append("Missing point record count")

    return analysis


def detect_scientific_format(filepath: str) -> Dict[str, Any]:
    """Detect the scientific file format type."""
    result = {
        "is_scientific": False,
        "format": None,
        "confidence": 0.0
    }

    ext = Path(filepath).suffix.lower()

    scientific_extensions = {
        '.dcm': ('DICOM', 0.9),
        '.dcim': ('DICOM', 0.9),
        '.fits': ('FITS', 0.9),
        '.fit': ('FITS', 0.9),
        '.fts': ('FITS', 0.9),
        '.czi': ('CZI', 0.8),
        '.lif': ('LIF', 0.8),
        '.nd2': ('ND2', 0.8),
        '.ome.xml': ('OME-XML', 0.9),
        '.las': ('LAS', 0.9),
        '.laz': ('LAS', 0.9),
        '.tif': ('TIFF', 0.4),
        '.tiff': ('TIFF', 0.4),
    }

    if ext in scientific_extensions:
        result["is_scientific"] = True
        result["format"], result["confidence"] = scientific_extensions[ext]
        if ext in [".tif", ".tiff"]:
            subtype = _detect_tiff_subtype(filepath)
            if subtype:
                result["format"] = subtype
                result["confidence"] = 0.7
    else:
        try:
            with open(filepath, 'rb') as f:
                header = f.read(132)
                if header[128:132] == b'DICM':
                    result["is_scientific"] = True
                    result["format"] = "DICOM"
                    result["confidence"] = 1.0
                elif header[:6] == b'SIMPLE':
                    result["is_scientific"] = True
                    result["format"] = "FITS"
                    result["confidence"] = 1.0
        except Exception as e:
            logger.debug(f"Failed to detect scientific file format from header: {e}")

    return result


# Extended Scientific Microscopy Formats
MICROSCOPY_EXTENDED = {
    'czi_channel_names': 'czi_channel_names',
    'czi_channel_colors': 'czi_channel_colors',
    'czi_channel_excitation': 'czi_channel_excitation',
    'czi_channel_emission': 'czi_channel_emission',
    'czi_tile_position': 'czi_tile_position',
    'czi_pyramid_level': 'czi_pyramid_level',
    'czi_zoom': 'czi_zoom',
    'czi_readout_time': 'czi_readout_time',
    'czi_binning': 'czi_binning',
    'czi_pixel_type': 'czi_pixel_type',
    'czi_compression': 'czi_compression',
    'czi_objective_name': 'czi_objective_name',
    'czi_objective_magnification': 'czi_objective_magnification',
    'czi_objective_na': 'czi_objective_na',
    'czi_objective_immersion': 'czi_objective_immersion',
    'czi_tube_lens_focal_length': 'czi_tube_lens_focal_length',
    'czi_camera_setting': 'czi_camera_setting',
    'czi_detector_setting': 'czi_detector_setting',
    'czi_laser_lines': 'czi_laser_lines',
    'czi_laser_power': 'czi_laser_power',
    'czi_acquisition_time': 'czi_acquisition_time',
    'czi_experiment': 'czi_experiment',
    'czi_well_position': 'czi_well_position',
    'czi_well_row': 'czi_well_row',
    'czi_well_column': 'czi_well_column',
    'lif_reference_image': 'lif_reference_image',
    'lif_laser_lines': 'lif_laser_lines',
    'lif_detectors': 'lif_detectors',
    'lif_pmt_voltages': 'lif_pmt_voltages',
    'lif_gain_settings': 'lif_gain_settings',
    'lif_scan_speed': 'lif_scan_speed',
    'lif_averaging': 'lif_averaging',
    'lif_pinhole': 'lif_pinhole',
    'lif_z_stack': 'lif_z_stack',
    'lif_time_series': 'lif_time_series',
    'lif_tile_scan': 'lif_tile_scan',
    'lif_region': 'lif_region',
    'lif_roi': 'lif_roi',
    'nd2_file_version': 'nd2_file_version',
    'nd2_acquisition_time': 'nd2_acquisition_time',
    'nd2_experiment': 'nd2_experiment',
    'nd2_loop_parameters': 'nd2_loop_parameters',
    'nd2_stage_positions': 'nd2_stage_positions',
    'nd2_z_stacks': 'nd2_z_stacks',
    'nd2_time_series': 'nd2_time_series',
    'nd2_channels': 'nd2_channels',
    'nd2_channel_names': 'nd2_channel_names',
    'nd2_channel_wavelengths': 'nd2_channel_wavelengths',
    'nd2_laser_lines': 'nd2_laser_lines',
    'nd2_laser_powers': 'nd2_laser_powers',
    'nd2_filter_sets': 'nd2_filter_sets',
    'nd2_objectives': 'nd2_objectives',
    'nd2_camera_settings': 'nd2_camera_settings',
}

# Extended OME-TIFF Metadata
OME_TIFF_EXTENDED = {
    'ome_instrument_id': 'ome_instrument_id',
    'ome_objective_id': 'ome_objective_id',
    'ome_detector_id': 'ome_detector_id',
    'ome_light_source_id': 'ome_light_source_id',
    'ome_filter_id': 'ome_filter_id',
    'ome_dichroic_id': 'ome_dichroic_id',
    'ome_channel_samples_per_pixel': 'ome_channel_samples_per_pixel',
    'ome_channel_illumination_type': 'ome_channel_illumination_type',
    'ome_channel_contrast_method': 'ome_channel_contrast_method',
    'ome_channel_acquisition_mode': 'ome_channel_acquisition_mode',
    'ome_channel_pinhole_size': 'ome_channel_pinhole_size',
    'ome_channel_pinhole_size_unit': 'ome_channel_pinhole_size_unit',
    'ome_channel_excitation_wavelength': 'ome_channel_excitation_wavelength',
    'ome_channel_emission_wavelength': 'ome_channel_emission_wavelength',
    'ome_channel_fluorochrome': 'ome_channel_fluorochrome',
    'ome_channel_naming_convention': 'ome_channel_naming_convention',
    'ome_channel_color': 'ome_channel_color',
    'ome_plane_the_z': 'ome_plane_the_z',
    'ome_plane_the_t': 'ome_plane_the_t',
    'ome_plane_position_x': 'ome_plane_position_x',
    'ome_plane_position_y': 'ome_plane_position_y',
    'ome_plane_position_z': 'ome_plane_position_z',
    'ome_plane_exposure_time': 'ome_plane_exposure_time',
    'ome_plane_delta_t': 'ome_plane_delta_t',
    'ome_plane_timestamp': 'ome_plane_timestamp',
    'ome_roi_id': 'ome_roi_id',
    'ome_roi_x': 'ome_roi_x',
    'ome_roi_y': 'ome_roi_y',
    'ome_roi_width': 'ome_roi_width',
    'ome_roi_height': 'ome_roi_height',
    'ome_roi_geometry_type': 'ome_roi_geometry_type',
    'ome_well_samples_ref': 'ome_well_samples_ref',
    'ome_well_row': 'ome_well_row',
    'ome_well_column': 'ome_well_column',
    'ome_well_origin_x': 'ome_well_origin_x',
    'ome_well_origin_y': 'ome_well_origin_y',
    'ome_plate_id': 'ome_plate_id',
    'ome_plate_rows': 'ome_plate_rows',
    'ome_plate_columns': 'ome_plate_columns',
    'ome_plate_well_origin_x': 'ome_plate_well_origin_x',
    'ome_plate_well_origin_y': 'ome_plate_well_origin_y',
    'ome_plate_well_spacing': 'ome_plate_well_spacing',
    'ome_plate_external_identifier': 'ome_plate_external_identifier',
}

# Extended Bio-Formats Metadata
BIO_FORMATS_EXTENDED = {
    'bf_screen_id': 'bf_screen_id',
    'bf_screen_name': 'bf_screen_name',
    'bf_screen_type': 'bf_screen_type',
    'bf_screen_status': 'bf_screen_status',
    'bf_plate_id': 'bf_plate_id',
    'bf_plate_name': 'bf_plate_name',
    'bf_plate_wells': 'bf_plate_wells',
    'bf_plate_column_count': 'bf_plate_column_count',
    'bf_plate_row_count': 'bf_plate_row_count',
    'bf_well_origin_x': 'bf_well_origin_x',
    'bf_well_origin_y': 'bf_well_origin_y',
    'bf_well_sample_count': 'bf_well_sample_count',
    'bf_well_sample_ref': 'bf_well_sample_ref',
    'bf_experimenter_id': 'bf_experimenter_id',
    'bf_experimenter_first_name': 'bf_experimenter_first_name',
    'bf_experimenter_last_name': 'bf_experimenter_last_name',
    'bf_experimenter_email': 'bf_experimenter_email',
    'bf_experimenter_institution': 'bf_experimenter_institution',
    'bf_experimenter_department': 'bf_experimenter_department',
    'bf_project_id': 'bf_project_id',
    'bf_project_name': 'bf_project_name',
    'bf_project_description': 'bf_project_description',
    'bf_dataset_id': 'bf_dataset_id',
    'bf_dataset_name': 'bf_dataset_name',
    'bf_dataset_description': 'bf_dataset_description',
    'bf_algorithm_id': 'bf_algorithm_id',
    'bf_algorithm_name': 'bf_algorithm_name',
    'bf_algorithm_version': 'bf_algorithm_version',
    'bf_parameters': 'bf_parameters',
    'bf_settings': 'bf_settings',
    'bf_roi_id': 'bf_roi_id',
    'bf_roi_description': 'bf_roi_description',
    'bf_annotation_id': 'bf_annotation_id',
    'bf_annotation_value': 'bf_annotation_value',
    'bf_annotation_namespace': 'bf_annotation_namespace',
}

# LiDAR Point Cloud Extensions
LIDAR_EXTENSIONS = {
    'lidar_point_format': 'lidar_point_format',
    'lidar_point_count': 'lidar_point_count',
    'lidar_returns_count': 'lidar_returns_count',
    'lidar_return_number': 'lidar_return_number',
    'lidar_number_of_returns': 'lidar_number_of_returns',
    'lidar_scan_direction_flag': 'lidar_scan_direction_flag',
    'lidar_edge_of_flight_line': 'lidar_edge_of_flight_line',
    'lidar_classification': 'lidar_classification',
    'lidar_classification_synthetic': 'lidar_classification_synthetic',
    'lidar_classification_keypoint': 'lidar_classification_keypoint',
    'lidar_classification_water': 'lidar_classification_water',
    'lidar_classification_rail': 'lidar_classification_rail',
    'lidar_classification_road_surface': 'lidar_classification_road_surface',
    'lidar_classification_overlap': 'lidar_classification_overlap',
    'lidar_intensity': 'lidar_intensity',
    'lidar_scan_angle': 'lidar_scan_angle',
    'lidar_scan_angle_rank': 'lidar_scan_angle_rank',
    'lidar_minimum': 'lidar_minimum',
    'lidar_maximum': 'lidar_maximum',
    'lidar_point_source_id': 'lidar_point_source_id',
    'lidar_gps_time': 'lidar_gps_time',
    'lidar_red': 'lidar_red',
    'lidar_green': 'lidar_green',
    'lidar_blue': 'lidar_blue',
    'lidar_nir': 'lidar_nir',
    'lidar_wave_packet_descriptor_index': 'lidar_wave_packet_descriptor_index',
    'lidar_byte_offset_to_waveform_data': 'lidar_byte_offset_to_waveform_data',
    'lidar_waveform_packet_size': 'lidar_waveform_packet_size',
    'lidar_return_point_waveform_location': 'lidar_return_point_waveform_location',
    'lidar_x': 'lidar_x',
    'lidar_y': 'lidar_y',
    'lidar_z': 'lidar_z',
    'lidar_x_scaled': 'lidar_x_scaled',
    'lidar_y_scaled': 'lidar_y_scaled',
    'lidar_z_scaled': 'lidar_z_scaled',
    'lidar_scan_channel': 'lidar_scan_channel',
    'lidar_user_data': 'lidar_user_data',
    'lidar_point_skip': 'lidar_point_skip',
}

# Remote Sensing Extensions
REMOTE_SENSING_EXTENSIONS = {
    'rs_satellite_name': 'rs_satellite_name',
    'rs_sensor_name': 'rs_sensor_name',
    'rs_sensor_type': 'rs_sensor_type',
    'rs_sensor_resolution': 'rs_sensor_resolution',
    'rs_sensor_band_count': 'rs_sensor_band_count',
    'rs_wrs_path': 'rs_wrs_path',
    'rs_wrs_row': 'rs_wrs_row',
    'rs_day_night_indicator': 'rs_day_night_indicator',
    'rs_scene_center_time': 'rs_scene_center_time',
    'rs_cloud_coverage': 'rs_cloud_coverage',
    'rs_image_quality': 'rs_image_quality',
    'rs_azimuth_angle': 'rs_azimuth_angle',
    'rs_elevation_angle': 'rs_elevation_angle',
    'rs_sun_azimuth': 'rs_sun_azimuth',
    'rs_sun_elevation': 'rs_sun_elevation',
    'rs_ground_sample_distance': 'rs_ground_sample_distance',
    'rs_ullatitude': 'rs_ullatitude',
    'rs_ullongitude': 'rs_ullongitude',
    'rs_urlatitude': 'rs_urlatitude',
    'rs_urlongitude': 'rs_urlongitude',
    'rs_llllatitude': 'rs_llllatitude',
    'rs_llllongitude': 'rs_llllongitude',
    'rs_lrlatitude': 'rs_lrlatitude',
    'rs_lrlongitude': 'rs_lrlongitude',
    'rs_corner_lat_lon': 'rs_corner_lat_lon',
    'rs_nadir_along_track': 'rs_nadir_along_track',
    'rs_nadir_across_track': 'rs_nadir_across_track',
    'rs_acquisition_date': 'rs_acquisition_date',
    'rs_production_date': 'rs_production_date',
    'rs_quality_assessment': 'rs_quality_assessment',
    'rs_geometric_accuracy': 'rs_geometric_accuracy',
    'rs_radiometric_resolution': 'rs_radiometric_resolution',
    'rs_temporal_resolution': 'rs_temporal_resolution',
    'rs_orbital_period': 'rs_orbital_period',
    'rs_orbit_type': 'rs_orbit_type',
    'rs_antenna_look_direction': 'rs_antenna_look_direction',
}

# Microscopy Image Analysis Extensions
MICROSCOPY_ANALYSIS_EXTENSIONS = {
    'mia_cell_count': 'mia_cell_count',
    'mia_nucleus_count': 'mia_nucleus_count',
    'mia_region_count': 'mia_region_count',
    'mia_object_count': 'mia_object_count',
    'mia_average_intensity': 'mia_average_intensity',
    'mia_total_intensity': 'mia_total_intensity',
    'mia_standard_deviation': 'mia_standard_deviation',
    'mia_min_intensity': 'mia_min_intensity',
    'mia_max_intensity': 'mia_max_intensity',
    'mia_area': 'mia_area',
    'mia_perimeter': 'mia_perimeter',
    'mia_circularity': 'mia_circularity',
    'mia_solidity': 'mia_solidity',
    'mia_eccentricity': 'mia_eccentricity',
    'mia_major_axis': 'mia_major_axis',
    'mia_minor_axis': 'mia_minor_axis',
    'mia_aspect_ratio': 'mia_aspect_ratio',
    'mia_roundness': 'mia_roundness',
    'mia_compactness': 'mia_compactness',
    'mia_convexity': 'mia_convexity',
    'mia_extent': 'mia_extent',
    'mia_centroid_x': 'mia_centroid_x',
    'mia_centroid_y': 'mia_centroid_y',
    'mia_centroid_z': 'mia_centroid_z',
    'mia_boundary_points': 'mia_boundary_points',
    'mia_holes_count': 'mia_holes_count',
    'mia_euler_number': 'mia_euler_number',
    'mia_texture_contrast': 'mia_texture_contrast',
    'mia_texture_homogeneity': 'mia_texture_homogeneity',
    'mia_texture_entropy': 'mia_texture_entropy',
    'mia_texture_energy': 'mia_texture_energy',
    'mia_texture_correlation': 'mia_texture_correlation',
    'mia_features_calculated': 'mia_features_calculated',
    'mia_classification_result': 'mia_classification_result',
    'mia_classification_confidence': 'mia_classification_confidence',
    'mia_segmentation_method': 'mia_segmentation_method',
    'mia_segmentation_parameters': 'mia_segmentation_parameters',
}


def get_scientific_medical_field_count() -> int:
    """Return total number of scientific_medical metadata fields."""
    total = 0
    total += len(GEOTIFF_KEY_NAMES)
    total += len(ULTRA_SCIENTIFIC_MEDICAL_FIELDS)
    total += len(MEGA_SCIENTIFIC_MEDICAL_FIELDS)
    total += len(MICROSCOPY_EXTENDED)
    total += len(OME_TIFF_EXTENDED)
    total += len(BIO_FORMATS_EXTENDED)
    total += len(LIDAR_EXTENSIONS)
    total += len(REMOTE_SENSING_EXTENSIONS)
    total += len(MICROSCOPY_ANALYSIS_EXTENSIONS)
    return total
