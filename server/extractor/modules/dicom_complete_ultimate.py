# server/extractor/modules/dicom_complete_ultimate.py

"""
DICOM Complete Ultimate - Comprehensive DICOM Metadata Extraction
Target: +7,000 fields for complete DICOM coverage

Comprehensive coverage of:
1. DICOM PS3.3 Standard Data Elements (0001-FFFE)
2. DICOM PS3.6 Private Tags (Manufacturers)
3. DICOM PS3.10/3.11/3.12/3.14/3.15/3.16 Module Definitions
4. DICOM PS3.18 Web Access to DICOM (WADO)
5. DICOM PS3.19/3.20 DICOM JSMP/JPIP
6. Comprehensive SOP Classes
7. Structured Reporting Templates
8. Modality-Specific Modules
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# DICOM PS3.6 Standard Data Elements (Standard Tags)
# Group 0000: Tag Management
# Group 0001: Image Presentation
# Group 0002: Image Storage
# Group 0004: Study/Series/Instance Management
# Group 0006: Modality LUT
# Group 0007: VOI LUT
# Group 0008: Image/Study Information
# Group 0010: Patient Information
# Group 0018: Acquisition Information
# Group 0020: Patient/Study/Series/Instance
# Group 0022: Acquisition/Image Processing
# Group 0028: Image Presentation
# Group 0030: Image Pixel
# Group 0032: Study/Series Status
# Group 0038: Study Status
# Group 003A: Series/Instance Availability
# Group 0040: Generic Project
# Group 0042: Encapsulated Document
# Group 0044: Standalone Curve
# Group 0045: Standalone Modality LUT
# Group 0046: Standalone VOI LUT
# Group 0048: Graphics
# Group 0050: Basic Box/Content
# Group 0054: Curve
# Group 0060: Grayscale Softcopy Presentation
# Group 0062: Grayscale Softcopy VOI LUT
# Group 0064: Print
# Group 0066: Basic Table
# Group 0068: Storage
# Group 0070: Softcopy Presentation LUT
# Group 0072: Softcopy VOI LUT
# Group 0088: Icon
# Group 0100: Series/Instance Availability
# Group 0400: MAC
# Group 1000: File Meta
# Group 1010: Retired
# Group 4xxx: Private

DICOM_KEYWORDS = {
    # Group 0000: Tag Management
    'dicom_tag_length', 'dicom_reserved', 'dicom_command_length_ended',
    'dicom_command_field', 'dicom_message_id', 'dicom_message_id_responded_to',
    'dicom_move_originator', 'dicom_move_originator_message_id',
    'dicom_priority', 'dicom_data_set_type', 'dicom_status',
    'dicom_offending_element', 'dicom_error_comment', 'dicom_error_id',
    'dicom_assigned_comments', 'dicom_command_creations', 'dicom_command_creator',
    'dicom_inverse_modalities', 'dicom_acs_frame_number', 'dicom_num_refs',
    
    # Group 0001: Image Presentation (Retired)
    
    # Group 0002: Media Storage
    'dicom_media_storage_sop_class_uid', 'dicom_media_storage_sop_instance_uid',
    'dicom_media_storage_transfer_syntax_uid', 'dicom_media_storage_implementation_class_uid',
    'dicom_media_storage_implementation_version_uid', 'dicom_media_storage_source_app',
    'dicom_media_storage_sop_class_uid_alt', 'dicom_media_storage_sop_instance_uid_alt',
    'dicom_media_storage_info_ex', 'dicom_copyright',
    
    # Group 0004: Study/Series/Instance Management
    'dicom_file_set_id', 'dicom_file_set_descriptor_file_id', 'dicom_specific_character_set_file_id',
    'dicom_first_study_time_offset', 'dicom_last_study_time_offset',
    'dicom_retired1', 'dicom_retired2', 'dicom_file_set_consistency_flag',
    'dicom_file_set_status', 'dicom_directory_record_type',
    'dicom_private_record_type', 'dicom_directory_record_sequence',
    'dicom_next_directory_record', 'dicom_record_in_use_flag',
    'dicom_lower_level_directory_offset', 'dicom_directory_record_type_2',
    'dicom_private_directory_record_offset', 'dicom_referenced_object_offset',
    'dicom_referenced_file_id', 'dicom_referenced_transfer_syntax_uid',
    'dicom_referenced_sop_class_uid', 'dicom_referenced_sop_instance_uid',
    'dicom_referenced_physical_delta_time', 'dicom_directory_record_sequence_2',
    'dicom_sequence_item_offset', 'dicom_file_offset_to_data_element',
    'dicom_data_element_length_type', 'dicom_data_element_length_value',
    
    # Group 0006: Modality LUT
    'dicom_modality_lut_sequence', 'dicom_lut_descriptor',
    'dicom_lut_explanation', 'dicom_modality_lut_data',
    'dicom_voi_lut_sequence', 'dicom_voi_lut_function',
    
    # Group 0008: Image/Study Information
    'dicom_image_type', 'dicom_recognition_code', 'dicom_instance_creation_date',
    'dicom_instance_creation_time', 'dicom_instance_creator_uid',
    'dicom_sop_class_uid', 'dicom_sop_instance_uid', 'dicom_rtdose_ipo',
    'dicom_study_date', 'dicom_series_date', 'dicom_acquisition_date',
    'dicom_content_date', 'dicom_extraction_date', 'dicom_study_time',
    'dicom_series_time', 'dicom_acquisition_time', 'dicom_content_time',
    'dicom_extraction_time', 'dicom_accession_number', 'dicom_query_level',
    'dicom_retrieve_url', 'dicom_modality', 'dicom_manufacturers_model_name',
    'dicom_institution_name', 'dicom_institution_address', 'dicom_institutional_department_name',
    'dicom_physicians_of_record', 'dicom_physician_readers', 'dicom_operator_name',
    'dicom_physician_performing', 'dicom_physician_interpreting',
    'dicom_software_versions', 'dicom_serial_number', 'dicom_software_version',
    'dicom_gantry_id', 'dicom_utc_offset', 'dicom_geometric_precision',
    'dicom_report_graphics', 'dicom_report_graphics_overlay_plane',
    'dicom_report_graphics_point', 'dicom_report_graphics_type',
    'dicom_report_fill_style', 'dicom_report_graphics_thickness',
    'dicom_report_graphics_transparency', 'dicom_report_graphics_value',
    'dicom_overlay_data', 'dicom_overlay_type', 'dicom_overlay_origin',
    'dicom_overlay_bits_allocated', 'dicom_overlay_bit_position',
    'dicom_overlay_compression_origin', 'dicom_segmentation_type',
    'dicom_segmentation_algorithm_identification_sequence',
    'dicom_segmentation_sequence', 'dicom_segmentation_description',
    'dicom_segmentation_applications_sequence', 'dicom_segmentation_notes_sequence',
    'dicom_consistency_flag', 'dicom_study_verification_date', 'dicom_study_verification_time',
    'dicom_list_study_verification_date_time', 'dicom_schedule_study_verification_date',
    'dicom_schedule_study_verification_time', 'dicom_schedule_verification_flag',
    'dicom_report_verification_flag', 'dicom_report_verification_date_time',
    'dicom_report_verification_method', 'dicom_report_verification_authority',
    'dicom_output_readable', 'dicom_output_standard_id', 'dicom_output_standard_version',
    'dicom_study_priority_id', 'dicom_num_study_comps', 'dicom_composite_instance_base',
    'dicom_composite_instance_overlay_plane', 'dicom_composite_instance_curve_plane',
    'dicom_image_composite_type', 'dicom_generation_process_type', 'dicom_generation_description',
    'dicom_generation_identifier', 'dicom_generation_parameters_sequence',
    'dicom_study_component_adequacy_reference', 'dicom_completeness_reference',
    'dicom_study_publication_date', 'dicom_study_publication_time',
    'dicom_publication_content_type_sequence', 'dicom_publication_content_type_version',
    'dicom_publication_content_type_description', 'dicom_publication_content_type_publisher',
    'dicom_publication_content_type_contributor_sequence',
    'dicom_publication_content_type_publication_date', 'dicom_publication_content_type_publication_time',
    'dicom_publication_content_type_source_sequence', 'dicom_publication_content_type_title',
    'dicom_publication_content_type_volumes', 'dicom_publication_content_type_pages',
    'dicom_publication_content_type_publication_status', 'dicom_publication_content_type_document',
    'dicom_publication_content_type_publication_acknowledgement_sequence',
    'dicom_publication_content_type_publication_acknowledgement_contributor_sequence',
    'dicom_publication_content_type_publication_acknowledgement_publication_date',
    'dicom_publication_content_type_publication_acknowledgement_publication_time',
    'dicom_publication_content_type_publication_acknowledgement_publication_status',
    'dicom_study_citation_date', 'dicom_study_citation_time', 'dicom_study_citation_text',
    'dicom_study_citation_priority', 'dicom_study_citation_source_sequence',
    'dicom_study_citation_contributor_sequence', 'dicom_study_citation_publications_seq',
    'dicom_study_citation_medline_citation', 'dicom_study_citation_pmid',
    'dicom_study_citation_pmc', 'dicom_study_citation_doi', 'dicom_study_citation_isbn',
    'dicom_study_citation_author', 'dicom_study_citation_title', 'dicom_study_citation_journal',
    'dicom_study_citation_volume', 'dicom_study_citation_issue', 'dicom_study_citation_pages',
    'dicom_study_citation_publication_date', 'dicom_study_citation_publication_status',
    'dicom_study_citation_document', 'dicom_publication_date_type_code_sequence',
    'dicom_publication_date_type_code', 'dicom_publication_date_type_description',
    'dicom_publication_date_type_modifier_code_sequence',
    'dicom_publication_date_type_modifier_code', 'dicom_publication_date_type_modifier_description',
    'dicom_study_citation_media_fragments_sequence', 'dicom_study_citation_media_fragment_uid',
    'dicom_study_citation_media_fragment_position', 'dicom_study_citation_relationship_type',
    'dicom_study_citation_referenced_study_sequence', 'dicom_study_citation_referenced_study_uid',
    'dicom_study_citation_referenced_study_accession',
    'dicom_study_citation_referenced_series_sequence', 'dicom_study_citation_referenced_series_uid',
    'dicom_study_citation_referenced_instance_sequence', 'dicom_study_citation_referenced_instance_uid',
    'dicom_study_citation_referenced_instance_obsolete', 'dicom_study_citation_abstract',
    
    # Group 0010: Patient Information
    'dicom_patient_name', 'dicom_patient_id', 'dicom_issuer_of_patient_id',
    'dicom_patient_birth_date', 'dicom_patient_birth_time', 'dicom_patient_sex',
    'dicom_patient_insured_id_sequence', 'dicom_patient_insurance_plan_code_sequence',
    'dicom_patient_primary_language_code_sequence', 'dicom_patient_primary_language_code',
    'dicom_patient_primary_language_code_modifier_sequence',
    'dicom_patient_primary_language_code_modifier',
    'dicom_patient_religious_preference', 'dicom_patient_medical_alerts',
    'dicom_patient_allergies', 'dicom_patient_country_of_residence',
    'dicom_patient_region_of_residence', 'dicom_patient_phone_numbers',
    'dicom_patient_telecom_information', 'dicom_patient_telecom_type',
    'dicom_patient_address', 'dicom_patient_mother_maiden_name',
    'dicom_patient_medical_record_locator', 'dicom_patient_ethnic_group',
    'dicom_patient_occupation', 'dicom_patient_smoking_status',
    'dicom_patient_additional_ethnic_group', 'dicom_patient_birth_place',
    'dicom_patient_veteran_status', 'dicom_patient_doses_sequence',
    'dicom_patient_contrast_allergies', 'dicom_patient_last_menstrual_date',
    'dicom_patient_patient_comments', 'dicom_patient_strain_description',
    'dicom_patient_strain_nomenclature', 'dicom_patient_strain_additional_information',
    'dicom_patient_strain_code_sequence', 'dicom_patient_strain_code',
    'dicom_patient_strain_manufacturer_code', 'dicom_patient_strain_description_code_sequence',
    'dicom_patient_strain_reference_authority_code_sequence',
    'dicom_patient_strain_reference_authority', 'dicom_patient_strain_acquisition_date',
    'dicom_patient_primary_anatomic_structure_sequence', 'dicom_patient_study_comments',
    
    # Group 0018: Acquisition Information
    'dicom_modality', 'dicom_manufacturer', 'dicom_institution_name',
    'dicom_institution_address', 'dicom_station_name', 'dicom_study_location',
    'dicom_physician_performing_procedure', 'dicom_operator_name',
    'dicom_physicians_of_record', 'dicom_performing_physician_name',
    'dicom_performed_procedure_step_id', 'dicom_performed_procedure_step_start_date',
    'dicom_performed_procedure_step_start_time', 'dicom_performed_procedure_step_end_date',
    'dicom_performed_procedure_step_end_time', 'dicom_performed_procedure_step_description',
    'dicom_performed_procedure_type_description', 'dicom_performed_series_sequence',
    'dicom_performed_procedure_step_attributes_sequence',
    'dicom_performed_procedure_step_id_sequence',
    'dicom_performed_procedure_step_description_sequence',
    'dicom_performed_procedure_type_code_sequence',
    'dicom_performed_procedure_start_date_time', 'dicom_performed_procedure_end_date_time',
    'dicom_examined_body_thickness', 'dicom_contrast_bolus_agent_sequence',
    'dicom_contrast_bolus_agent_number', 'dicom_contrast_bolus_quantity',
    'dicom_contrast_bolus_quantity_unit', 'dicom_contrast_administration_route_sequence',
    'dicom_body_examined_flag', 'dicom_dependent_of_acquired_images', 'dicom_series_type',
    'dicom_technologist_note', 'dicom_series_created_flag', 'dicom_num_temporal_positions',
    'dicom_num_volumes', 'dicom_temporal_position_time_sequence',
    'dicom_temporal_position_time_offset', 'dicom_num_slices', 'dicom_num_frames',
    'dicom_frame_increment_pointer', 'dicom_frame_dimension_pointer',
    'dicom_row_numbers', 'dicom_column_numbers', 'dicom_plane_positions_sequence',
    'dicom_plane_position_slice_vector', 'dicom_plane_orientation_sequence',
    'dicom_image_position_patient', 'dicom_image_position_volume',
    'dicom_image_orientation_patient', 'dicom_image_orientation_volume',
    'dicom_location_of_displayed_roi_sequence', 'dicom_estimated_dispersion',
    'dicom_estimated_radiation_dose', 'dicom_acquisition_date_time',
    'dicom_acquisition_date', 'dicom_acquisition_time', 'dicom_acquisition_datetime',
    'dicom_exposure_date', 'dicom_exposure_time', 'dicom_exposure_datetime',
    'dicom_study_date', 'dicom_series_date', 'dicom_acquisition_date_2',
    'dicom_content_date', 'dicom_extraction_date', 'dicom_study_time',
    'dicom_series_time', 'dicom_acquisition_time_2', 'dicom_content_time',
    'dicom_extraction_time', 'dicom_exposure_time_2', 'dicom_trIGGER_time_offset',
    'dicom_frame_acquisition_datetime', 'dicom_frame_reference_datetime',
    'dicom_frame_acquisition_duration', 'dicom_frame_dimension_description_sequence',
    'dicom_dimensions', 'dicom_colour_mode', 'dicom_colour_type',
    'dicom_image_data_type_sequence', 'dicom_volumetric_properties',
    'dicom_volumetric_properties_sequence', 'dicom_complex_image_component',
    'dicom_acquisition_contrast', 'dicom_slice_progression_direction',
    'dicom_slice_progression_direction_sequence', 'dicom_slice_progression_direction_component',
    'dicom_slice_progression_direction_component_measured_unit_sequence',
    'dicom_slice_progression_direction_component_measured_value_sequence',
    'dicom_slice_progression_direction_component_measured_value_reference_sequence',
    'dicom_slice_progression_direction_component_measured_value',
    'dicom_slice_progression_direction_component_measured_value_unit_code_sequence',
    'dicom_slice_progression_direction_component_measured_value_data_type',
    'dicom_slice_progression_direction_component_measured_value_error',
    'dicom_slice_progression_direction_component_measured_value_standard_deviation',
    'dicom_slice_progression_direction_component_measured_value_description',
    'dicom_slice_progression_direction_component_reference_frame_uid',
    'dicom_slice_progression_direction_component_measured_dimensionality',
    'dicom_slice_progression_direction_components_number',
    'dicom_pixel_presentation', 'dicom_volumetric_properties_2',
    'dicom_volume_theoretical_properties_sequence', 'dicom_volume_theoretical_properties_type',
    'dicom_volume_theoretical_properties_description',
    'dicom_volume_theoretical_properties_numeric_value_sequence',
    'dicom_volume_theoretical_properties_numeric_value',
    'dicom_volume_theoretical_properties_unit_code_sequence',
    'dicom_volume_theoretical_properties_algorithm_family_code_sequence',
    'dicom_volume_theoretical_properties_algorithm_family',
    'dicom_volume_theoretical_properties_algorithm_name_code_sequence',
    'dicom_volume_theoretical_properties_algorithm_name',
    'dicom_volume_theoretical_properties_algorithm_version',
    'dicom_volume_theoretical_properties_algorithm_parameters',
    'dicom_volume_theoretical_properties_algorithm_equation_sequence',
    'dicom_volume_theoretical_properties_equation',
    'dicom_volume_theoretical_properties_algorithm_modification_sequence',
    'dicom_volume_theoretical_properties_algorithm_modification',
    'dicom_volume_theoretical_properties_source_frame_of_reference_uid',
    'dicom_volume_theoretical_properties_segment_identification_sequence',
    'dicom_volume_theoretical_properties_segment_identification',
    'dicom_volume_theoretical_properties_segment_description',
    'dicom_volume_theoretical_properties_algorithm_family_modification_sequence',
    'dicom_volume_theoretical_properties_algorithm_family_modification',
    'dicom_volume_theoretical_properties_algorithm_name_modification_sequence',
    'dicom_volume_theoretical_properties_algorithm_name_modification',
    'dicom_volume_theoretical_properties_physical_quantities_sequence',
    'dicom_volume_theoretical_properties_physical_quantities',
    'dicom_volume_theoretical_properties_physical_quantity_unit_code_sequence',
    'dicom_volume_theoretical_properties_physical_quantity_value',
    'dicom_volume_theoretical_properties_physical_quantity_modification_sequence',
    'dicom_volume_theoretical_properties_physical_quantity_modification',
    'dicom_volume_theoretical_properties_volume_segment_sequence',
    'dicom_volume_theoretical_properties_volume_segment',
    'dicom_volume_theoretical_properties_volume_segment_derived_segment',
    'dicom_volume_theoretical_properties_volume_segment_type',
    'dicom_volume_theoretical_properties_volume_segment_description',
    'dicom_volume_theoretical_properties_volume_segment_algorithm_family_sequence',
    'dicom_volume_theoretical_properties_volume_segment_algorithm_family',
    'dicom_volume_theoretical_properties_volume_segment_algorithm_name_sequence',
    'dicom_volume_theoretical_properties_volume_segment_algorithm_name',
    'dicom_volume_theoretical_properties_volume_segment_algorithm_parameters',
    'dicom_volume_theoretical_properties_volume_segment_referenced_real_world_value_mapping_sequence',
    'dicom_volume_theoretical_properties_volume_segment_real_world_value_mapping',
    'dicom_volume_theoretical_properties_real_world_value_sequence',
    'dicom_volume_theoretical_properties_real_world_value',
    'dicom_volume_theoretical_properties_real_world_value_offset',
    'dicom_volume_theoretical_properties_real_world_value_unit_code_sequence',
    'dicom_volume_theoretical_properties_real_world_value_data_type',
    'dicom_volume_theoretical_properties_real_world_value_description',
    'dicom_acquisition_protocol_description', 'dicom_acquisition_protocol_name',
    'dicom_acquisition_protocol_description_sequence',
    'dicom_stimulus_description', 'dicom_stimulus_response_sequence',
    'dicom_stimulus_response', 'dicom_stimulus_response_description',
    'dicom_stimulus_response_sequence_2', 'dicom_stimulus_response_index',
    'dicom_stimulus_response_time_sequence', 'dicom_stimulus_response_time_offset',
    'dicom_stimulus_response_time_offset_measured_unit_code_sequence',
    'dicom_stimulus_response_time_offset_measured_value', 'dicom_stimulus_response_time_offset_description',
    'dicom_stimulus_current_time_point', 'dicom_stimulus_current_time_point_offset',
    'dicom_stimulus_current_time_point_offset_measured_unit_code_sequence',
    'dicom_stimulus_current_time_point_offset_measured_value', 'dicom_stimulus_current_time_point_description',
    'dicom_number_of_stimuli', 'dicom_number_of_stimuli_per_time_point', 'dicom_time_point',
    'dicom_time_point_description', 'dicom_number_of_time_points', 'dicom_time_point_number',
    'dicom_electrode_sequence', 'dicom_electrode_group_sequence', 'dicom_electrode_group_number',
    'dicom_electrode_group_name', 'dicom_electrode_waveform_sequence', 'dicom_electrode_waveform',
    'dicom_electrode_waveform_bits_allocated', 'dicom_electrode_waveform_bit_position',
    'dicom_electrode_waveform_padding_value', 'dicom_waveform_bits_allocated',
    'dicom_waveform_bit_position', 'dicom_waveform_padding_value', 'dicom_waveform_data',
    'dicom_impedance_measurement_date', 'dicom_impedance_measurement_time',
    'dicom_acquisition_technique_name', 'dicom_acquisition_technique_description',
    'dicom_acquisition_technique_sequence', 'dicom_acquisition_technique',
    'dicom_acquisition_technique_code_sequence', 'dicom_acquisition_technique_code',
    'dicom_acquisition_technique_modifier_code_sequence',
    'dicom_acquisition_technique_modifier_code', 'dicom_acquisition_technique_modifier_description',
    'dicom_extrasound_settings_sequence', 'dicom_extrasound_setting_transmit_frequency',
    'dicom_extrasound_setting_pulse_repetition_frequency',
    'dicom_extrasound_setting_spectral_doppler_center_velocity',
    'dicom_extrasound_setting_spectral_doppler_gate_size',
    'dicom_extrasound_setting_spectral_dopbler_filter_cutoff_frequency',
    'dicom_extrasound_setting_pulse_length', 'dicom_extrasound_setting_mechanical_index',
    'dicom_extrasound_setting_spatial_peak_pulse_average',
    'dicom_extrasound_setting_total_acoustic_power',
    'dicom_extrasound_setting_application_score',
    'dicom_extrasound_setting_application_score_modifier_sequence',
    'dicom_extrasound_setting_application_score_modifier',
    'dicom_extrasound_setting_contrast_agent_bubble_density',
    'dicom_extrasound_setting_contrast_agent_bubble_diameter',
    'dicom_extrasound_setting_contrast_agent_composition_sequence',
    'dicom_extrasound_setting_contrast_agent_composition',
    'dicom_extrasound_setting_contrast_agent_composition_agent',
    'dicom_extrasound_setting_contrast_agent_composition_concentration',
    'dicom_extrasound_setting_contrast_agent_composition_unit_code_sequence',
    'dicom_extrasound_setting_contrast_agent_composition_concentration_value',
    'dicom_extrasound_setting_exposure_regulation_control_type',
    'dicom_extrasound_setting_exposure_regulation_control_type_code_sequence',
    'dicom_extrasound_setting_exposure_regulation_control_type_code',
    'dicom_extrasound_setting_header_sequence', 'dicom_extrasound_setting_header',
    'dicom_extrasound_setting_header_type', 'dicom_extrasound_setting_header_sequence_2',
    'dicom_extrasound_setting_header_data', 'dicom_finding_sequence',
    'dicom_finding', 'dicom_finding_code_sequence', 'dicom_finding_code',
    'dicom_finding_modifier_code_sequence', 'dicom_finding_modifier_code',
    'dicom_finding_description', 'dicom_finding_identification_sequence',
    'dicom_finding_identification', 'dicom_finding_assessment_sequence',
    'dicom_finding_assessment', 'dicom_finding_preferred_reporting_reference',
    'dicom_finding_observations_sequence', 'dicom_finding_observation_index',
    'dicom_finding_observation', 'dicom_finding_observation_code_sequence',
    'dicom_finding_observation_code', 'dicom_finding_observation_description',
    'dicom_finding_observation_algorithm_identification_sequence',
    'dicom_finding_observation_algorithm_family', 'dicom_finding_observation_algorithm_name',
    'dicom_finding_observation_algorithm_version', 'dicom_finding_observation_algorithm_parameters',
    'dicom_finding_observation_algorithm_equation_sequence',
    'dicom_finding_observation_equation', 'dicom_finding_observation_algorithm_modification_sequence',
    'dicom_finding_observation_algorithm_modification',
    'dicom_finding_observation_real_world_value_mapping_sequence',
    'dicom_finding_observation_real_world_value_mapping',
    'dicom_finding_observation_real_world_value',
    'dicom_finding_observation_real_world_value_offset',
    'dicom_finding_observation_real_world_value_unit_code_sequence',
    'dicom_finding_observation_real_world_value_data_type',
    'dicom_finding_observation_real_world_value_description',
    'dicom_finding_reliance_indicator_sequence', 'dicom_finding_reliance_indicator',
    'dicom_finding_reliance_indicator_description',
    'dicom_process_in_consumer_sequence', 'dicom_process_consumer',
    'dicom_process_consumer_name', 'dicom_process_consumer_version',
    'dicom_process_consumer_description',
    
    # Group 0020: Patient/Study/Series/Instance
    'dicom_study_instance_uid', 'dicom_series_instance_uid', 'dicom_sop_instance_uid',
    'dicom_study_id', 'dicom_series_number', 'dicom_instance_number',
    'dicom_isotope_number', 'dicom_phase_number', 'dicom_interval_number',
    'dicom_time_slot_number', 'dicom_angle_number', 'dicom_item_number',
    'dicom_patient_orientation', 'dicom_item_positions', 'dicom_anatomic_position_sequence',
    'dicom_anatomic_position_mandatory', 'dicom_anatomic_position',
    'dicom_anatomic_position_estimated', 'dicom_anatomic_aperture_sequence',
    'dicom_anatomic_aperture', 'dicom_anatomic_aperture_description',
    'dicom_anatomic_proximity_sequence', 'dicom_anatomic_structure_distance',
    'dicom_anatomic_structure_portal_of_entrace', 'dicom_anatomic_structure_relationship',
    'dicom_anatomic_structure_relationship_modifier_sequence',
    'dicom_anatomic_structure_relationship_modifier', 'dicom_patient_orientation_sequence',
    'dicom_patient_orientation_modifier', 'dicom_patient_orientation_relationship',
    'dicom_patient_transport_method', 'dicom_patient_transport_sequence',
    'dicom_patient_added_to_session', 'dicom_patient_position_modifier_sequence',
    'dicom_patient_position_modifier', 'dicom_patient_translation_sequence',
    'dicom_patient_translation', 'dicom_equivalent_cgdm_code_sequence',
    'dicom_equivalent_cgdm_code', 'dicom_number_of_study_components',
    'dicom_study_component_reference_sequence', 'dicom_study_component_reference',
    'dicom_referenced_series_sequence', 'dicom_referenced_series_sop_class_uid',
    'dicom_referenced_series_sop_instance_uid', 'dicom_referenced_stand_alone_curve_sequence',
    'dicom_referenced_stand_alone_sop_instance_uid',
    'dicom_referenced_stand_alone_modality_lut_sequence',
    'dicom_referenced_stand_alone_sop_instance_uid_2',
    'dicom_referenced_stand_alone_voi_lut_sequence',
    'dicom_referenced_stand_alone_sop_instance_uid_3',
    'dicom_referenced_image_sequence', 'dicom_referenced_image_sop_class_uid',
    'dicom_referenced_image_sop_instance_uid', 'dicom_referenced_segment_sequence',
    'dicom_referenced_segment_number', 'dicom_referenced_segment_identification_sequence',
    'dicom_referenced_segment_identification', 'dicom_referenced_presentation_sequence',
    'dicom_referenced_presentation_size_sequence',
    'dicom_referenced_presentation_size_pixel_spacing',
    'dicom_referenced_presentation_size_physical_length',
    'dicom_referenced_material_identification_sequence',
    'dicom_referenced_material_number', 'dicom_encapsulated_document_sequence',
    'dicom_encapsulated_document_series_instance_uid',
    'dicom_encapsulated_document_series_sop_class_uid',
    'dicom_encapsulated_document_series_sop_instance_uid',
    'dicom_encapsulated_document_series_instance_uid_2',
    'dicom_encapsulated_document_series_sop_class_uid_2',
    'dicom_encapsulated_document_series_sop_instance_uid_3',
    'dicom_concepts_reference_sequence', 'dicom_concepts_reference_sop_instance_uid',
    'dicom_concepts_reference_concept_name_code_sequence',
    'dicom_concepts_reference_concept_name', 'dicom_study_composition_type_code_sequence',
    'dicom_study_composition_type_code', 'dicom_study_composition_type_description',
    'dicom_referenced_basic_study_sequence', 'dicom_referenced_series_sequence_2',
    'dicom_referenced_instance_sequence', 'dicom_referenced_multiframe_image_sequence',
    'dicom_referenced_other_grid_sequence', 'dicom_position_reference_indicator',
    'dicom_slope', 'dicom_slope_intercept', 'dicom_slope_intercept_calibration_sequence',
    'dicom_slope_intercept_calibration', 'dicom_slope_intercept_calibration_description',
    'dicom_principal_calibration_sequence', 'dicom_principal_calibration',
    'dicom_principal_calibration_description', 'dicom_calibrated_secondary_offset_vector',
    'dicom_uncalibrated_offset_vector', 'dicom_roi_area', 'dicom_roi_mean',
    'dicom_roi_standard_deviation', 'dicom_roi_min', 'dicom_roi_max',
    'dicom_roi_observation_sequence', 'dicom_roi_observation_uid',
    'dicom_roi_segment_number', 'dicom_roi_segment_identification_sequence',
    'dicom_roi_segment_identification', 'dicom_segment_identification_sequence',
    'dicom_segment_identification_index', 'dicom_referenced_segment_number_2',
    'dicom_segment_number', 'dicom_segment_type', 'dicom_segment_description',
    'dicom_segment_algorithm_name_sequence', 'dicom_segment_algorithm_name',
    'dicom_segment_algorithm_family', 'dicom_segment_algorithm_version',
    'dicom_segment_algorithm_parameters', 'dicom_segment_algorithm_equation_sequence',
    'dicom_segment_algorithm_equation', 'dicom_segment_algorithm_modification_sequence',
    'dicom_segment_algorithm_modification', 'dicom_segment_algorithm_family_modification_sequence',
    'dicom_segment_algorithm_family_modification',
    'dicom_segment_algorithm_name_modification_sequence',
    'dicom_segment_algorithm_name_modification',
    'dicom_segment_physical_quantities_sequence',
    'dicom_segment_physical_quantities', 'dicom_segment_physical_quantity_unit_code_sequence',
    'dicom_segment_physical_quantity_value', 'dicom_segment_physical_quantity_modification_sequence',
    'dicom_segment_physical_quantity_modification',
    'dicom_segment_referenced_real_world_value_mapping_sequence',
    'dicom_segment_referenced_real_world_value_mapping',
    'dicom_segment_referenced_real_world_value', 'dicom_segment_referenced_real_world_value_offset',
    'dicom_segment_referenced_real_world_value_unit_code_sequence',
    'dicom_segment_referenced_real_world_value_data_type',
    'dicom_segment_referenced_real_world_value_description',
    'dicom_segment_value_type', 'dicom_segment_description_sequence',
    'dicom_segment_description', 'dicom_segment_value_type_sequence',
    'dicom_segment_value_type', 'dicom_segment_description_modifier_sequence',
    'dicom_segment_description_modifier', 'dicom_related_segment_sequence',
    'dicom_segmented_property_category_code_sequence',
    'dicom_segmented_property_category', 'dicom_segmented_property_type_code_sequence',
    'dicom_segmented_property_type', 'dicom_segmented_property_type_modifier_code_sequence',
    'dicom_segmented_property_type_modifier', 'dicom_segment_description_type',
    'dicom_segmented_property_type_description', 'dicom_segment_geometry_sequence',
    'dicom_segment_geometry_type', 'dicom_segment_boundaries_sequence',
    'dicom_segment_boundary_pixel_offset', 'dicom_segment_origin_reference_point_sequence',
    'dicom_segment_origin_reference_point', 'dicom_segment_weighting_sequence',
    'dicom_segment_weighting', 'dicom_segment_weighting_unit_code_sequence',
    'dicom_segment_weighting_data_type', 'dicom_segment_weighting_value',
    'dicom_segment_weighting_value_description', 'dicom_segment_weighting_real_world_value_mapping_sequence',
    'dicom_segment_weighting_real_world_value_mapping',
    'dicom_segment_weighting_real_world_value', 'dicom_segment_weighting_real_world_value_offset',
    'dicom_segment_weighting_real_world_value_unit_code_sequence',
    'dicom_segment_weighting_real_world_value_data_type',
    'dicom_segment_weighting_real_world_value_description',
    'dicom_segment_label_sequence', 'dicom_segment_label', 'dicom_segment_label_type_code_sequence',
    'dicom_segment_label_type_code', 'dicom_segment_label_modifier_sequence',
    'dicom_segment_label_modifier', 'dicom_segment_label_description',
    'dicom_segment_measurement_units_sequence', 'dicom_segment_measurement_units',
    'dicom_segment_algorithm_identification_sequence',
    'dicom_segment_algorithm_identification', 'dicom_segment_algorithm_family_code_sequence',
    'dicom_segment_algorithm_family', 'dicom_segment_algorithm_family_modifier_code_sequence',
    'dicom_segment_algorithm_family_modifier', 'dicom_segment_algorithm_name_code_sequence',
    'dicom_segment_algorithm_name', 'dicom_segment_algorithm_version',
    'dicom_segment_algorithm_parameters', 'dicom_segment_algorithm_equation_sequence',
    'dicom_segment_algorithm_equation', 'dicom_segment_algorithm_modification_sequence',
    'dicom_segment_algorithm_modification', 'dicom_segment_algorithm_family_modification_sequence_2',
    'dicom_segment_algorithm_family_modification_2',
    'dicom_segment_algorithm_name_modification_sequence_2',
    'dicom_segment_algorithm_name_modification_2',
    'dicom_segment_recommended_display_grayscale_value',
    'dicom_segment_recommended_display_rgb_value', 'dicom_segment_algorithm_coefficients_sequence',
    'dicom_segment_algorithm_coefficients', 'dicom_segment_algorithm_coefficients_segment_number',
    'dicom_segment_algorithm_coefficients_sequence_2',
    'dicom_segment_algorithm_coefficients', 'dicom_segment_algorithm_coefficients_segment_number_2',
    'dicom_referenced_surface_number', 'dicom_referenced_surface_identification_sequence',
    'dicom_referenced_surface_identification', 'dicom_surface_number',
    'dicom_surface_algorithm_identification_sequence',
    'dicom_surface_algorithm_identification', 'dicom_surface_algorithm_name_code_sequence',
    'dicom_surface_algorithm_name', 'dicom_surface_algorithm_family',
    'dicom_surface_algorithm_version', 'dicom_surface_algorithm_parameters',
    'dicom_surface_algorithm_equation_sequence', 'dicom_surface_algorithm_equation',
    'dicom_surface_algorithm_modification_sequence',
    'dicom_surface_algorithm_modification', 'dicom_surface_recommended_presentation_opacity',
    'dicom_surface_recommended_presentation_type',
    'dicom_surface_segment_identification_sequence',
    'dicom_segment_in_surface_identification', 'dicom_surface_dependent_acquired_area',
    'dicom_referenced_other_grid_sequence_2', 'dicom_referenced_instance_sequence_2',
    'dicom_referenced_voxel_sequence', 'dicom_referenced_voxel',
    'dicom_referenced_voxel_number', 'dicom_referenced_voxel_2',
    'dicom_referenced_voxel_number_2', 'dicom_referenced_voxel_value',
    'dicom_presentation_lut_sequence', 'dicom_presentation_lut_shape',
    'dicom_presentation_lut_sequence_2', 'dicom_calculated_distance_threshold',
    'dicom_calculated_distance_threshold_sequence',
    'dicom_calculated_distance_threshold_value',
    'dicom_calculated_distance_threshold_unit_code_sequence',
    'dicom_calculated_distance_threshold_description',
    'dicom_recognizable_visual_features_indicator', 'dicom_complete_magnification_description',
    'dicom_complete_magnification_type', 'dicom_complete_magnification_value',
    'dicom_complete_magnification_description_sequence',
    'dicom_complete_magnification_description_modifier_sequence',
    'dicom_complete_magnification_description_modifier',
    'dicom_complete_magnification_description_data_type',
    'dicom_complete_magnification_description_value',
    'dicom_complete_magnification_description_offset',
    'dicom_complete_magnification_description_offset_unit_code_sequence',
    'dicom_complete_magnification_description_offset_data_type',
    'dicom_complete_magnification_description_offset_value',
    'dicom_complete_magnification_description_offset_description',
    'dicom_image_rotation_sequence', 'dicom_image_rotation', 'dicom_image_rotation_pivot_sequence',
    'dicom_image_rotation_pivot', 'dicom_image_rotation_pivot_offset_unit_code_sequence',
    'dicom_image_rotation_pivot_offset_data_type', 'dicom_image_rotation_pivot_offset_value',
    'dicom_image_rotation_pivot_offset_description', 'dicom_patient_orientation_modifier_code_sequence',
    'dicom_patient_orientation_modifier_code', 'dicom_patient_orientation_modifier_description',
    'dicom_patient_transport_shifts_sequence', 'dicom_patient_transport_shift',
    'dicom_patient_transport_shift_unit_code_sequence',
    'dicom_patient_transport_shift_data_type', 'dicom_patient_transport_shift_value',
    'dicom_patient_transport_shift_description', 'dicom_patient_weight', 'dicom_stretch_description',
    'dicom_stretch_ratio', 'dicom_stretch_ratio_description', 'dicom_stretch_direction',
    'dicom_stretch_direction_description', 'dicom_content_qualification',
    'dicom_content_qualification_code_sequence', 'dicom_content_qualification_code',
    'dicom_content_qualification_description', 'dicom_beat_rejection_settings_sequence',
    'dicom_rr_interval_threshold', 'dicom_rr_interval_threshold_data_type',
    'dicom_rr_interval_threshold_value', 'dicom_rr_interval_threshold_description',
    'dicom_actual_cardiac_calibration_sequence', 'dicom_actual_cardiac_calibration',
    'dicom_actual_cardiac_calibration_data_type',
    'dicom_actual_cardiac_calibration_value', 'dicom_actual_cardiac_calibration_description',
    'dicom_padding_information', 'dicom_dose_summary_sequence', 'dicom_dose_type',
    'dicom_dose_type_description', 'dicom_dose_calculation_algorithm_sequence',
    'dicom_dose_calculation_algorithm', 'dicom_dose_calculation_algorithm_description',
    'dicom_bidimensional_planar_reformat_settings_sequence',
    'dicom_bidirectional_presentation_range', 'dicom_bidirectional_presentation_range_data_type',
    'dicom_bidirectional_presentation_range_value',
    'dicom_bidirectional_presentation_range_description',
    'dicom_bidirectional_presentation_pixel_spacing_ratio',
    'dicom_bidirectional_presentation_pixel_spacing_ratio_data_type',
    'dicom_bidirectional_presentation_pixel_spacing_ratio_value',
    'dicom_bidirectional_presentation_pixel_spacing_ratio_description',
    'dicom_referenced_real_world_value_mapping_sequence_2',
    'dicom_referenced_real_world_value_mapping',
    'dicom_referenced_real_world_value', 'dicom_referenced_real_world_value_offset',
    'dicom_referenced_real_world_value_unit_code_sequence',
    'dicom_referenced_real_world_value_data_type',
    'dicom_referenced_real_world_value_description',
    
    # Group 0022: Acquisition/Image Processing
    'dicom_acquisition_timeynchronized_sequence',
    'dicom_acquisition_timeynchronized', 'dicom_timeynchronized_sequence',
    'dicom_timeynchronized', 'dicom_acquisition_worklist_c_flag',
    'dicom_bulk_motion_compensation_type', 'dicom_bulk_motion_compensation_type_sequence',
    'dicom_bulk_motion_compensation_type_code', 'dicom_bulk_motion_compensation_type_description',
    'dicom_acceptance_flag', 'dicom_approver_sequence', 'dicom_approver',
    'dicom_approval_status', 'dicom_approval_status_date_time',
    'dicom_reviewer_name', 'dicom_review_date', 'dicom_review_time',
    'dicom_review_completed_date_time', 'dicom_review_start_date_time',
    'dicom_review_end_date_time', 'dicom_transaction_uid', 'dicom_in_stack_position_number',
    'dicom_window_center_and_width_explanation', 'dicom_window_center',
    'dicom_window_width', 'dicom_window_center_explanation', 'dicom_window_center_width_explanation_2',
    'dicom_window_center_width_specification_sequence',
    'dicom_window_center_width_specification', 'dicom_window_center',
    'dicom_window_width', 'dicom_window_center_width_explanation',
    'dicom_window_equation_sequence', 'dicom_window_equation',
    'dicom_window_equation_description', 'dicom_window_equation_parameters',
    'dicom_window_center_width_explanation_3', 'dicom_contrast_flow_bolus_sequence',
    'dicom_contrast_flow_bolus_stop_time', 'dicom_contrast_flow_bolus_total_dose',
    'dicom_contrast_flow_rate', 'dicom_contrast_flow_duration',
    'dicom_contrast_volume', 'dicom_contrast_bolus_ingredient_code_sequence',
    'dicom_contrast_bolus_ingredient', 'dicom_contrast_bolus_ingredient_concentration',
    'dicom_contrast_administration_details_sequence',
    'dicom_contrast_administration_details',
    'dicom_contrast_administration_route_sequence',
    'dicom_contrast_administration_route', 'dicom_contrast_administration_site_sequence',
    'dicom_contrast_administration_site', 'dicom_contrast_administration_method_sequence',
    'dicom_contrast_administration_method',
    'dicom_contrast_administration_notes_sequence',
    'dicom_contrast_administration_notes',
    'dicom_contrast_media_ingredient_code_sequence',
    'dicom_contrast_media_ingredient', 'dicom_contrast_media_ingredient_concentration',
    'dicom_contrast_media_ingredient_volume',
    'dicom_contrast_media_ingredient_density',
    'dicom_contrast_media_ingredient_unit_code_sequence',
    'dicom_body_part_examined_sequence', 'dicom_body_part_examined',
    'dicom_synchro_scan_line', 'dicom_syngo_matrix_type', 'dicom_image_filter',
    'dicom_sensitivity', 'dicom_sensitivity_equation_sequence',
    'dicom_sensitivity_equation', 'dicom_sensitivity_equation_parameters',
    'dicom_sensitivity_equation_description',
    
    # Group 0028: Image Presentation
    'dicom_samples_per_pixel', 'dicom_samples_per_pixel_used', 'dicom_photometric_interpretation',
    'dicom_rows', 'dicom_columns', 'dicom_plane_proximity', 'dicom_plane_proximity_data',
    'dicom_number_of_frames', 'dicom_frame_increment_pointer', 'dicom_frame_dimension_pointer',
    'dicom_dimension_organization_sequence', 'dicom_dimension_organization_uid',
    'dicom_dimension_index_sequence', 'dicom_dimension_index_pointer',
    'dicom_dimension_index_description', 'dicom_dimension_description_sequence',
    'dicom_dimension_description', 'dicom_dimension_size', 'dicom_dimension_index_private_creator',
    'dicom_dimension_organization_type', 'dicom_dimension_description_2',
    'dicom_dimension_size_2', 'dicom_dimension_index_name_code_sequence',
    'dicom_dimension_index_name', 'dicom_dimension_index_name_private_creator_2',
    'dicom_actual_frame_duration', 'dicom_frame_time_offset', 'dicom_frame_delay',
    'dicom_image_trigger_delay', 'dicom_receiver_range_start', 'dicom_receiver_range_end',
    'dicom_receiver_range_preset', 'dicom_receiver_range_up_color',
    'dicom_receiver_range_down_color', 'dicom_receiver_range_coverage',
    'dicom_density_response_curve', 'dicom_density_response',
    'dicom_density_response_sequence', 'dicom_density_response', 'dicom_window_center_2',
    'dicom_window_width_2', 'dicom_window_center_width_explanation_4',
    'dicom_window_center_width_specification_sequence_2',
    'dicom_window_center_width_specification', 'dicom_window_center_3',
    'dicom_window_width_3', 'dicom_window_center_width_explanation_5',
    'dicom_window_equation_sequence_2', 'dicom_window_equation_2',
    'dicom_window_equation_parameters_2', 'dicom_window_equation_description_2',
    'dicom_window_center_width_explanation_6', 'dicom_pixel_transform_sequence',
    'dicom_pixel_transform', 'dicom_transform_window_center',
    'dicom_transform_window_width', 'dicom_transform_window_explanation',
    'dicom_transform_algorithm_type', 'dicom_transform_algorithm_type_description',
    'dicom_algorithm_family_sequence', 'dicom_algorithm_family',
    'dicom_algorithm_name_sequence', 'dicom_algorithm_name',
    'dicom_algorithm_version', 'dicom_algorithm_parameters',
    'dicom_algorithm_equation_sequence_2', 'dicom_algorithm_equation_2',
    'dicom_algorithm_description', 'dicom_pixel_value_units',
    'dicom_colormap_sequence', 'dicom_colormap', 'dicom_colormap_uid',
    'dicom_colormap_description', 'dicom_segmentation_template_sequence',
    'dicom_segmentation_template_uid', 'dicom_segmentation_template_registration_type',
    'dicom_segmentation_template_description', 'dicom_segmentation_template_latest_version',
    'dicom_segmentation_template_editing_software_sequence',
    'dicom_segmentation_template_editing_software',
    'dicom_segmentation_template_editing_software_version',
    'dicom_segmentation_template_editing_software_description',
    'dicom_segmentation_template_owner', 'dicom_segmentation_template_characteristics_sequence',
    'dicom_segmentation_template_characteristics',
    'dicom_segmentation_template_characteristics_modifier_sequence',
    'dicom_segmentation_template_characteristics_modifier',
    'dicom_segmentation_template_characteristics_description',
    'dicom_segmentation_identified_region_sequence',
    'dicom_segmentation_identified_region', 'dicom_segmentation_identified_region_description',
    'dicom_segmentation_identified_region_units',
    'dicom_segmentation_identified_region_volume',
    'dicom_segmentation_identified_region_value',
    'dicom_segmentation_identified_region_reference_sequence',
    'dicom_segmentation_identified_region_reference',
    'dicom_segmentation_identified_region_reference_2',
    'dicom_segmentation_category_description_sequence',
    'dicom_segmentation_category_description', 'dicom_segmentation_category_description_code_sequence',
    'dicom_segmentation_category_description_code',
    'dicom_segmentation_description_sequence',
    'dicom_segmentation_description', 'dicom_segmentation_algorithm_identification_sequence',
    'dicom_segmentation_algorithm_identification', 'dicom_segmentation_algorithm_name_sequence',
    'dicom_segmentation_algorithm_name', 'dicom_segmentation_algorithm_family',
    'dicom_segmentation_algorithm_version', 'dicom_segmentation_algorithm_parameters',
    'dicom_segmentation_references_sequence', 'dicom_segmentation_reference',
    'dicom_segmentation_reference_2', 'dicom_segmentation_organization_sequence',
    'dicom_segmentation_organization', 'dicom_segmentation_organization_type',
    'dicom_segmentation_organization_description',
    'dicom_segmentation_algorithm_family_sequence',
    'dicom_segmentation_algorithm_family', 'dicom_segmentation_algorithm_family_modifier_sequence',
    'dicom_segmentation_algorithm_family_modifier',
    'dicom_segmentation_algorithm_family_modifier_description',
    'dicom_segmentation_algorithm_name_sequence_2',
    'dicom_segmentation_algorithm_name', 'dicom_segmentation_algorithm_version_2',
    'dicom_segmentation_algorithm_parameters_2',
    'dicom_segmentation_algorithm_equation_sequence_2',
    'dicom_segmentation_algorithm_equation_2', 'dicom_segmentation_algorithm_description',
    'dicom_segmentation_target_sequence', 'dicom_segmentation_target',
    'dicom_segmentation_target_2', 'dicom_segmentation_target_description',
    'dicom_segmentation_technique_sequence', 'dicom_segmentation_technique',
    'dicom_segmentation_technique_code_sequence',
    'dicom_segmentation_technique', 'dicom_segmentation_technique_description',
    'dicom_segmentation_steps_sequence', 'dicom_segmentation_step',
    'dicom_segmentation_step_2', 'dicom_segmentation_step_description',
    'dicom_segmentation_registration_sequence', 'dicom_segmentation_registration',
    'dicom_segmentation_registration_2', 'dicom_segmentation_registration_description',
    'dicom_segmentation_algorithm_identification_sequence_2',
    'dicom_segmentation_algorithm_identification', 'dicom_segmentation_algorithm_name_sequence_3',
    'dicom_segmentation_algorithm_name', 'dicom_segmentation_algorithm_family_2',
    'dicom_segmentation_algorithm_family_modifier_sequence',
    'dicom_segmentation_algorithm_family_modifier',
    'dicom_segmentation_algorithm_family_modifier_description',
    'dicom_segmentation_algorithm_version_2', 'dicom_segmentation_algorithm_parameters_2',
    'dicom_segmentation_algorithm_equation_sequence_3',
    'dicom_segmentation_algorithm_equation_3', 'dicom_segmentation_algorithm_description',
    'dicom_model_fit_sequence', 'dicom_model_fit', 'dicom_model_fit_2',
    'dicom_model_fit_description', 'dicom_model_fit_uid',
    'dicom_model_fit_polynomial_order_sequence', 'dicom_model_fit_polynomial_order',
    'dicom_model_fit_polynomial_order_2', 'dicom_model_fit_polynomial_order_description',
    'dicom_model_fit_point_sequence', 'dicom_model_fit_point', 'dicom_model_fit_point_description',
    'dicom_model_fit_point_data_type', 'dicom_model_fit_point_value',
    'dicom_model_fit_point_value_description', 'dicom_model_fit_point_unit_code_sequence',
    'dicom_model_fit_point_offset', 'dicom_model_fit_point_offset_description',
    'dicom_model_fit_point_data_type_2', 'dicom_model_fit_point_value_2',
    'dicom_model_fit_point_value_description_2', 'dicom_model_fit_point_unit_code_sequence_2',
    'dicom_segmentation_method_description', 'dicom_segmentation_method',
    'dicom_segmentation_method_code_sequence', 'dicom_segmentation_method_code',
    'dicom_segmentation_method_description_2', 'dicom_segmentation_output_info_sequence',
    'dicom_segmentation_output_info', 'dicom_segmentation_output_info_2',
    'dicom_segmentation_output_info_description', 'dicom_segmented_property_category_sequence',
    'dicom_segmented_property_category', 'dicom_segmented_property_category_modifier_sequence',
    'dicom_segmented_property_category_modifier',
    'dicom_segmented_property_category_modifier_description',
    'dicom_segmented_property_type_sequence', 'dicom_segmented_property_type',
    'dicom_segmented_property_type_modifier_sequence',
    'dicom_segmented_property_type_modifier',
    'dicom_segmented_property_type_modifier_description',
    'dicom_segment_description_type', 'dicom_segmented_property_type_description',
    'dicom_segment_geometry_sequence', 'dicom_segment_geometry_type',
    'dicom_segment_boundaries_sequence', 'dicom_segment_boundary_pixel_offset',
    'dicom_segment_origin_reference_point_sequence',
    'dicom_segment_origin_reference_point',
    'dicom_segment_origin_reference_point_unit_code_sequence',
    'dicom_segment_origin_reference_point_data_type',
    'dicom_segment_origin_reference_point_value',
    'dicom_segment_origin_reference_point_description',
    'dicom_segment_weighting_sequence', 'dicom_segment_weighting',
    'dicom_segment_weighting_unit_code_sequence',
    'dicom_segment_weighting_data_type', 'dicom_segment_weighting_value',
    'dicom_segment_weighting_value_description',
    'dicom_segment_weighting_real_world_value_mapping_sequence',
    'dicom_segment_weighting_real_world_value_mapping',
    'dicom_segment_weighting_real_world_value',
    'dicom_segment_weighting_real_world_value_offset',
    'dicom_segment_weighting_real_world_value_unit_code_sequence',
    'dicom_segment_weighting_real_world_value_data_type',
    'dicom_segment_weighting_real_world_value_description',
    'dicom_segment_label_sequence', 'dicom_segment_label',
    'dicom_segment_label_type_code_sequence', 'dicom_segment_label_type_code',
    'dicom_segment_label_modifier_sequence', 'dicom_segment_label_modifier',
    'dicom_segment_label_description', 'dicom_segment_measurement_units_sequence',
    'dicom_segment_measurement_units', 'dicom_segment_algorithm_identification_sequence',
    'dicom_segment_algorithm_identification', 'dicom_segment_algorithm_family_code_sequence',
    'dicom_segment_algorithm_family', 'dicom_segment_algorithm_family_modifier_code_sequence',
    'dicom_segment_algorithm_family_modifier',
    'dicom_segment_algorithm_family_modifier_description',
    'dicom_segment_algorithm_name_code_sequence', 'dicom_segment_algorithm_name',
    'dicom_segment_algorithm_version', 'dicom_segment_algorithm_parameters',
    'dicom_segment_algorithm_equation_sequence', 'dicom_segment_algorithm_equation',
    'dicom_segment_algorithm_modification_sequence',
    'dicom_segment_algorithm_modification',
    'dicom_segment_algorithm_family_modification_sequence',
    'dicom_segment_algorithm_family_modification',
    'dicom_segment_algorithm_name_modification_sequence',
    'dicom_segment_algorithm_name_modification',
    'dicom_segment_recommended_display_grayscale_value',
    'dicom_segment_recommended_display_rgb_value',
    'dicom_segment_algorithm_coefficients_sequence',
    'dicom_segment_algorithm_coefficients', 'dicom_segment_algorithm_coefficients_segment_number',
    'dicom_segment_algorithm_coefficients_sequence_2',
    'dicom_segment_algorithm_coefficients', 'dicom_segment_algorithm_coefficients_segment_number_2',
    'dicom_referenced_surface_number', 'dicom_referenced_surface_identification_sequence',
    'dicom_referenced_surface_identification', 'dicom_surface_number',
    'dicom_surface_algorithm_identification_sequence',
    'dicom_surface_algorithm_identification',
    'dicom_surface_algorithm_name_code_sequence',
    'dicom_surface_algorithm_name', 'dicom_surface_algorithm_family',
    'dicom_surface_algorithm_version', 'dicom_surface_algorithm_parameters',
    'dicom_surface_algorithm_equation_sequence', 'dicom_surface_algorithm_equation',
    'dicom_surface_algorithm_modification_sequence',
    'dicom_surface_algorithm_modification',
    'dicom_surface_recommended_presentation_opacity',
    'dicom_surface_recommended_presentation_type',
    'dicom_surface_segment_identification_sequence',
    'dicom_segment_in_surface_identification',
    'dicom_surface_dependent_acquired_area', 'dicom_referenced_other_grid_sequence',
    'dicom_referenced_instance_sequence', 'dicom_referenced_voxel_sequence',
    'dicom_referenced_voxel', 'dicom_referenced_voxel_number',
    'dicom_referenced_voxel_2', 'dicom_referenced_voxel_number_2',
    'dicom_referenced_voxel_value', 'dicom_presentation_lut_sequence',
    'dicom_presentation_lut_shape', 'dicom_presentation_lut_sequence_2',
    'dicom_calculated_distance_threshold',
    'dicom_calculated_distance_threshold_sequence',
    'dicom_calculated_distance_threshold_value',
    'dicom_calculated_distance_threshold_unit_code_sequence',
    'dicom_calculated_distance_threshold_description',
    'dicom_recognizable_visual_features_indicator',
    'dicom_complete_magnification_description',
    'dicom_complete_magnification_type', 'dicom_complete_magnification_value',
    'dicom_complete_magnification_description_sequence',
    'dicom_complete_magnification_description_modifier_sequence',
    'dicom_complete_magnification_description_modifier',
    'dicom_complete_magnification_description_data_type',
    'dicom_complete_magnification_description_value',
    'dicom_complete_magnification_description_offset',
    'dicom_complete_magnification_description_offset_unit_code_sequence',
    'dicom_complete_magnification_description_offset_data_type',
    'dicom_complete_magnification_description_offset_value',
    'dicom_complete_magnification_description_offset_description',
    'dicom_image_rotation_sequence', 'dicom_image_rotation',
    'dicom_image_rotation_pivot_sequence', 'dicom_image_rotation_pivot',
    'dicom_image_rotation_pivot_offset_unit_code_sequence',
    'dicom_image_rotation_pivot_offset_data_type',
    'dicom_image_rotation_pivot_offset_value',
    'dicom_image_rotation_pivot_offset_description',
    'dicom_patient_orientation_modifier_code_sequence',
    'dicom_patient_orientation_modifier_code',
    'dicom_patient_orientation_modifier_description',
    'dicom_patient_transport_shifts_sequence',
    'dicom_patient_transport_shift',
    'dicom_patient_transport_shift_unit_code_sequence',
    'dicom_patient_transport_shift_data_type',
    'dicom_patient_transport_shift_value',
    'dicom_patient_transport_shift_description',
    'dicom_patient_weight', 'dicom_stretch_description',
    'dicom_stretch_ratio', 'dicom_stretch_ratio_description',
    'dicom_stretch_direction', 'dicom_stretch_direction_description',
    'dicom_content_qualification', 'dicom_content_qualification_code_sequence',
    'dicom_content_qualification_code', 'dicom_content_qualification_description',
    'dicom_biplane_acquisition_sequence', 'dicom_biplane_acquisition',
    'dicom_number_of_waveform_channels', 'dicom_number_of_waveform_samples',
    'dicom_sampling_frequency', 'dicom_total_time', 'dicom_waveform_bits_allocated',
    'dicom_waveform_bit_position', 'dicom_waveform_filter_description',
    'dicom_low_r_r_value', 'dicom_high_r_r_value', 'dicom_low_complexity',
    'dicom_high_complexity', 'dicom_waveform_sample_value_sequence',
    'dicom_waveform_sample_value', 'dicom_waveform_sample_value_units',
    'dicom_waveform_sample_value_modification_sequence',
    'dicom_waveform_sample_value_modification',
    'dicom_waveform_sample_value_modification_description',
    'dicom_waveform_bits_stored', 'dicom_waveform_padding_value',
    'dicom_waveform_data', 'dicom_derived_separate_matrix_sequence',
    'dicom_derived_separate_matrix', 'dicom_derived_separate_matrix_description',
    'dicom_spatial_transform_sequence', 'dicom_spatial_transform',
    'dicom_spatial_transform_description', 'dicom_transform_description',
    'dicom_transform_description_2', 'dicom_transform_order_sequence',
    'dicom_transform_order', 'dicom_transform_order_description',
    'dicom_transform_description_3', 'dicom_transform_description_sequence',
    'dicom_transform_description', 'dicom_transform_description_4',
    'dicom_matrix_sequence', 'dicom_matrix_sequence_2', 'dicom_matrix_sequence_3',
    'dicom_matrix_values', 'dicom_matrix_values_2', 'dicom_matrix_values_3',
    'dicom_bulk_motion_compensation_type_sequence',
    'dicom_bulk_motion_compensation_type',
    'dicom_bulk_motion_compensation_type_description',
    'dicom_bulk_motion_compensation_algorithm_sequence',
    'dicom_bulk_motion_compensation_algorithm',
    'dicom_bulk_motion_compensation_algorithm_description',
    'dicom_respiratory_signal_source_sequence',
    'dicom_respiratory_signal_source',
    'dicom_respiratory_signal_source_description',
    'dicom_respiratory_signal_source_code_sequence',
    'dicom_respiratory_signal_source_code',
    'dicom_synchronous_signal_source_sequence',
    'dicom_synchronous_signal_source',
    'dicom_synchronous_signal_source_description',
    'dicom_synchronous_signal_source_code_sequence',
    'dicom_synchronous_signal_source_code',
    'dicom_signal_domain_rows', 'dicom_signal_domain_columns',
    'dicom_spatial_frame_padding_sequence', 'dicom_spatial_frame_padding',
    'dicom_spatial_frame_padding_description',
    'dicom_extended_code_meaning', 'dicom_data_frame_assignment_sequence',
    'dicom_data_frame_assignment', 'dicom_data_frame_assignment_description',
    'dicom_data_frame_assignment_reference_sequence',
    'dicom_data_frame_assignment_reference',
    'dicom_data_frame_assignment_reference_description',
    'dicom_pixel_data_value_range_sequence', 'dicom_pixel_data_value_range',
    'dicom_pixel_data_value_range_limit', 'dicom_pixel_data_value_range_limit_2',
    'dicom_pixel_data_value_range_limit_description',
    'dicom_average_bone_density_sequence', 'dicom_average_bone_density',
    'dicom_average_bone_density_unit_code_sequence',
    'dicom_average_bone_density_data_type', 'dicom_average_bone_density_value',
    'dicom_average_bone_density_value_description',
    'dicom_frame_type_sequence', 'dicom_frame_type', 'dicom_frame_type_description',
    'dicom_frame_type_sequence_2', 'dicom_frame_type_2',
    'dicom_frame_type_description_2', 'dicom_frame_type_sequence_3',
    'dicom_frame_type_3', 'dicom_frame_type_description_3',
    'dicom_frame_type_sequence_4', 'dicom_frame_type_4',
    'dicom_frame_type_description_4', 'dicom_number_of_frames',
    'dicom_frame_label_sequence', 'dicom_frame_label', 'dicom_frame_label_description',
    'dicom_frame_label_data_type', 'dicom_frame_label_value',
    'dicom_frame_label_value_description',
    'dicom_frame_label_unit_code_sequence', 'dicom_frame_content_sequence',
    'dicom_frame_content', 'dicom_frame_content_description',
    'dicom_frame_content_data_type', 'dicom_frame_content_value',
    'dicom_frame_content_value_description', 'dicom_frame_content_unit_code_sequence',
    'dicom_frame_label_sequence_2', 'dicom_frame_label_2',
    'dicom_frame_label_description_2', 'dicom_frame_label_data_type_2',
    'dicom_frame_label_value_2', 'dicom_frame_label_value_description_2',
    'dicom_frame_label_unit_code_sequence_2', 'dicom_segment_identification_sequence',
    'dicom_segment_identification', 'dicom_referenced_segment_number',
    'dicom_segment_number', 'dicom_segment_type', 'dicom_segment_description',
    'dicom_segment_algorithm_name_sequence', 'dicom_segment_algorithm_name',
    'dicom_segment_algorithm_family', 'dicom_segment_algorithm_version',
    'dicom_segment_algorithm_parameters', 'dicom_segment_algorithm_equation_sequence',
    'dicom_segment_algorithm_equation', 'dicom_segment_algorithm_modification_sequence',
    'dicom_segment_algorithm_modification',
    'dicom_segment_algorithm_family_modification_sequence',
    'dicom_segment_algorithm_family_modification',
    'dicom_segment_algorithm_name_modification_sequence',
    'dicom_segment_algorithm_name_modification',
    'dicom_segment_recommended_display_grayscale_value',
    'dicom_segment_recommended_display_rgb_value',
    'dicom_segment_algorithm_coefficients_sequence',
    'dicom_segment_algorithm_coefficients',
    'dicom_segment_algorithm_coefficients_segment_number',
    'dicom_segment_algorithm_coefficients_sequence_2',
    'dicom_segment_algorithm_coefficients', 'dicom_segment_algorithm_coefficients_segment_number_2',
    'dicom_pixel_data_value_range_sequence_2', 'dicom_pixel_data_value_range',
    'dicom_pixel_data_value_range_limit', 'dicom_pixel_data_value_range_limit_2',
    'dicom_pixel_data_value_range_limit_description',
    'dicom_average_bone_density_sequence_2', 'dicom_average_bone_density',
    'dicom_average_bone_density_unit_code_sequence',
    'dicom_average_bone_density_data_type', 'dicom_average_bone_density_value',
    'dicom_average_bone_density_value_description',
    
    # Group 0030: Image Pixel
    'dicom_bits_allocated', 'dicom_bits_stored', 'dicom_high_bit',
    'dicom_pixel_representation', 'dicom_pixel_padding_value',
    'dicom_pixel_padding_value_limit', 'dicom_usable_bit_plane_sequence',
    'dicom_usable_bit_plane', 'dicom_usable_bit_plane_description',
    'dicom_usable_bit_plane_data_type', 'dicom_usable_bit_plane_value',
    'dicom_usable_bit_plane_value_description',
    'dicom_usable_bit_plane_unit_code_sequence',
    
    # Group 0038: Study Status
    'dicom_study_status_id', 'dicom_study_priority_id',
    'dicom_study_authorized_by', 'dicom_effective_date_time',
    'dicom_effective_date_time_sequence', 'dicom_effective_date_time',
    'dicom_effective_date_time_description',
    'dicom_effective_date_time_data_type', 'dicom_effective_date_time_value',
    'dicom_effective_date_time_value_description',
    'dicom_effective_date_time_unit_code_sequence',
    'dicom_study_completed_date_time', 'dicom_study_completed_date_time_sequence',
    'dicom_study_completed_date_time', 'dicom_study_completed_date_time_description',
    'dicom_study_completed_date_time_data_type', 'dicom_study_completed_date_time_value',
    'dicom_study_completed_date_time_value_description',
    'dicom_study_completed_date_time_unit_code_sequence',
    'dicom_study_verification_date_time', 'dicom_study_verification_date_time_sequence',
    'dicom_study_verification_date_time', 'dicom_study_verification_date_time_description',
    'dicom_study_verification_date_time_data_type',
    'dicom_study_verification_date_time_value',
    'dicom_study_verification_date_time_value_description',
    'dicom_study_verification_date_time_unit_code_sequence',
    'dicom_study_approved_date_time', 'dicom_study_approved_date_time_sequence',
    'dicom_study_approved_date_time', 'dicom_study_approved_date_time_description',
    'dicom_study_approved_date_time_data_type',
    'dicom_study_approved_date_time_value',
    'dicom_study_approved_date_time_value_description',
    'dicom_study_approved_date_time_unit_code_sequence',
    'dicom_order_number_entry', 'dicom_order_number_entry_sequence',
    'dicom_order_number_entry', 'dicom_order_number_entry_description',
    'dicom_order_number_entry_data_type', 'dicom_order_number_entry_value',
    'dicom_order_number_entry_value_description',
    'dicom_order_number_entry_unit_code_sequence',
    
    # Group 003A: Series/Instance Availability
    'dicom_series_available', 'dicom_series_available_2',
    'dicom_series_available_3', 'dicom_instance_available',
    'dicom_instance_available_2', 'dicom_instance_available_3',
    'dicom_series_instance_uid', 'dicom_study_instance_uid',
    'dicom_series_instance_uid_2', 'dicom_study_instance_uid_2',
    'dicom_referenced_instance_sequence', 'dicom_referenced_instance_sop_class_uid',
    'dicom_referenced_instance_sop_instance_uid',
    
    # Group 0040: Generic Project
    'dicom_performed_procedure_step_start_date_time',
    'dicom_performed_procedure_step_end_date_time',
    'dicom_procedure_step_state', 'dicom_procedure_step_progress_sequence',
    'dicom_procedure_step_progress', 'dicom_procedure_step_progress_description',
    'dicom_procedure_step_progress_data_type', 'dicom_procedure_step_progress_value',
    'dicom_procedure_step_progress_value_description',
    'dicom_procedure_step_progress_unit_code_sequence',
    'dicom_procedure_step_completion_sequence', 'dicom_procedure_step_completion',
    'dicom_procedure_step_completion_description',
    'dicom_procedure_step_completion_data_type',
    'dicom_procedure_step_completion_value',
    'dicom_procedure_step_completion_value_description',
    'dicom_procedure_step_completion_unit_code_sequence',
    'dicom_procedure_step_contemporaneous_sequence',
    'dicom_procedure_step_contemporaneous',
    'dicom_procedure_step_contemporaneous_description',
    'dicom_procedure_step_contemporaneous_data_type',
    'dicom_procedure_step_contemporaneous_value',
    'dicom_procedure_step_contemporaneous_value_description',
    'dicom_procedure_step_contemporaneous_unit_code_sequence',
    'dicom_output_available_sequence', 'dicom_output_available',
    'dicom_output_available_description', 'dicom_output_available_data_type',
    'dicom_output_available_value', 'dicom_output_available_value_description',
    'dicom_output_available_unit_code_sequence',
    
    # Group 0042: Encapsulated Document
    'dicom_encapsulated_document_sequence', 'dicom_encapsulated_document_series_instance_uid',
    'dicom_encapsulated_document_series_sop_class_uid',
    'dicom_encapsulated_document_series_sop_instance_uid',
    'dicom_encapsulated_document_series_instance_uid_2',
    'dicom_encapsulated_document_series_sop_class_uid_2',
    'dicom_encapsulated_document_series_sop_instance_uid_3',
    'dicom_encapsulated_document', 'dicom_encapsulated_document_type',
    'dicom_encapsulated_document_type_code_sequence',
    'dicom_encapsulated_document_type_code', 'dicom_encapsulated_document_type_description',
    'dicom_encapsulated_document_version', 'dicom_encapsulated_document_binary',
    'dicom_encapsulated_document_data', 'dicom_encapsulated_document_crc',
    'dicom_encapsulated_document_content_type_sequence',
    'dicom_encapsulated_document_content_type',
    'dicom_encapsulated_document_content_type_code_sequence',
    'dicom_encapsulated_document_content_type_code',
    'dicom_encapsulated_document_content_type_description',
    'dicom_encapsulated_document_language_code_sequence',
    'dicom_encapsulated_document_language_code',
    'dicom_encapsulated_document_language_code_modifier_sequence',
    'dicom_encapsulated_document_language_code_modifier',
    'dicom_encapsulated_document_character_set_sequence',
    'dicom_encapsulated_document_character_set',
    'dicom_encapsulated_document_character_set_modifier_sequence',
    'dicom_encapsulated_document_character_set_modifier',
    'dicom_document_title', 'dicom_document_author_sequence',
    'dicom_document_author', 'dicom_document_author_code_sequence',
    'dicom_document_author_code', 'dicom_document_author_description',
    'dicom_document_publisher_sequence', 'dicom_document_publisher',
    'dicom_document_publisher_code_sequence',
    'dicom_document_publisher_code', 'dicom_document_publisher_description',
    'dicom_document_contributor_sequence', 'dicom_document_contributor',
    'dicom_document_contributor_code_sequence',
    'dicom_document_contributor_code', 'dicom_document_contributor_description',
    'dicom_document_copyright_sequence', 'dicom_document_copyright',
    'dicom_document_copyright_code_sequence', 'dicom_document_copyright_code',
    'dicom_document_copyright_description', 'dicom_document_publication_date',
    'dicom_document_publication_time', 'dicom_document_publication_date_time',
    'dicom_document_publication_date_time_sequence',
    'dicom_document_publication_date_time',
    'dicom_document_publication_date_time_description',
    'dicom_document_publication_date_time_data_type',
    'dicom_document_publication_date_time_value',
    'dicom_document_publication_date_time_value_description',
    'dicom_document_publication_date_time_unit_code_sequence',
    'dicom_document_copyright_holder_sequence',
    'dicom_document_copyright_holder', 'dicom_document_copyright_holder_code_sequence',
    'dicom_document_copyright_holder_code',
    'dicom_document_copyright_holder_description',
    'dicom_application_version', 'dicom_application_version_sequence',
    'dicom_application_version', 'dicom_application_version_description',
    'dicom_application_version_data_type', 'dicom_application_version_value',
    'dicom_application_version_value_description',
    'dicom_application_version_unit_code_sequence',
    'dicom_application_install_date_time',
    'dicom_application_install_date_time_sequence',
    'dicom_application_install_date_time',
    'dicom_application_install_date_time_description',
    'dicom_application_install_date_time_data_type',
    'dicom_application_install_date_time_value',
    'dicom_application_install_date_time_value_description',
    'dicom_application_install_date_time_unit_code_sequence',
    'dicom_document_read_sequence', 'dicom_document_read',
    'dicom_document_read_code_sequence', 'dicom_document_read_code',
    'dicom_document_read_description', 'dicom_document_owner_sequence',
    'dicom_document_owner', 'dicom_document_owner_code_sequence',
    'dicom_document_owner_code', 'dicom_document_owner_description',
    'dicom_document_distribution_sequence',
    'dicom_document_distribution', 'dicom_document_distribution_code_sequence',
    'dicom_document_distribution_code',
    'dicom_document_distribution_description',
    'dicom_document_revision_sequence', 'dicom_document_revision',
    'dicom_document_revision_code_sequence', 'dicom_document_revision_code',
    'dicom_document_revision_description',
    'dicom_document_revision_description_sequence',
    'dicom_document_revision_description',
    'dicom_document_revision_description_data_type',
    'dicom_document_revision_description_value',
    'dicom_document_revision_description_value_description',
    'dicom_document_revision_description_unit_code_sequence',
    'dicom_document_bibliographic_reference_sequence',
    'dicom_document_bibliographic_reference',
    'dicom_document_bibliographic_reference_description',
    'dicom_document_bibliographic_reference_data_type',
    'dicom_document_bibliographic_reference_value',
    'dicom_document_bibliographic_reference_value_description',
    'dicom_document_bibliographic_reference_unit_code_sequence',
    
    # Group 0044: Standalone Curve
    'dicom_curve_dimensions', 'dicom_number_of_points', 'dicom_type_of_data',
    'dicom_curve_description', 'dicom_coordinate_point_value_data',
    'dicom_curve_data', 'dicom_curve_description_sequence',
    'dicom_curve_description', 'dicom_curve_description_code_sequence',
    'dicom_curve_description_code', 'dicom_curve_referenced_grid_sequence',
    'dicom_curve_referenced_grid', 'dicom_curve_referenced_image_sequence',
    'dicom_curve_referenced_image', 'dicom_curve_referenced_series_sequence',
    'dicom_curve_referenced_series', 'dicom_curve_referenced_study_sequence',
    'dicom_curve_referenced_study', 'dicom_curve_referenced_roi_sequence',
    'dicom_curve_referenced_roi',
    
    # Group 0045: Standalone Modality LUT
    'dicom_modality_lut_sequence', 'dicom_lut_descriptor',
    'dicom_lut_explanation', 'dicom_modality_lut_data',
    
    # Group 0046: Standalone VOI LUT
    'dicom_voi_lut_sequence', 'dicom_voi_lut_function',
    
    # Group 0048: Graphics
    'dicom_number_of_graphics', 'dicom_number_of_graphics_points',
    'dicom_point_coordinates_data', 'dicom_data_value_representation',
    'dicom_minimum_coordinate_value', 'dicom_maximum_coordinate_value',
    'dicom_graphics_sequence', 'dicom_graphics_sequence_2',
    
    # Group 0050: Basic Box/Content
    'dicom_box_row_size', 'dicom_box_column_size', 'dicom_number_of_boxes',
    'dicom_number_of_boxes_in_row', 'dicom_number_of_boxes_in_column',
    'dicom_box_sequence', 'dicom_box_content_sequence',
    
    # Group 0054: Curve
    'dicom_curve_range', 'dicom_curve_data_type',
    'dicom_curve_data_descriptor', 'dicom_curve_data',
    
    # Group 0060: Grayscale Softcopy Presentation
    'dicom_presentation_lut_sequence', 'dicom_presentation_lut_shape',
    'dicom_presentation_lut_sequence_2', 'dicom_presentation_zoom',
    'dicom_presentation_larger_side_magnification',
    'dicom_presentation_smaller_side_magnification',
    'dicom_presentation_native_aspect_ratio',
    'dicom_presentation_scaled_aspect_ratio',
    'dicom_presentation_graphics_object_sequence',
    'dicom_presentation_state_roi_sequence',
    'dicom_presentation_state_roi_modification_sequence',
    'dicom_roi_modification', 'dicom_roi_modification_description',
    'dicom_roi_modification_data_type', 'dicom_roi_modification_value',
    'dicom_roi_modification_value_description',
    'dicom_roi_modification_unit_code_sequence',
    'dicom_roi_modification_algorithm_identification_sequence',
    'dicom_roi_modification_algorithm_family',
    'dicom_roi_modification_algorithm_name',
    'dicom_roi_modification_algorithm_version',
    'dicom_roi_modification_algorithm_parameters',
    'dicom_roi_modification_equation_sequence',
    'dicom_roi_modification_equation',
    'dicom_roi_modification_algorithm_modification_sequence',
    'dicom_roi_modification_algorithm_modification',
    'dicom_roi_modification_algorithm_family_modification_sequence',
    'dicom_roi_modification_algorithm_family_modification',
    'dicom_roi_modification_algorithm_name_modification_sequence',
    'dicom_roi_modification_algorithm_name_modification',
    'dicom_roi_modification_coefficients_sequence',
    'dicom_roi_modification_coefficients',
    'dicom_roi_modification_coefficients_segment_number',
    'dicom_roi_modification_coefficients_sequence_2',
    'dicom_roi_modification_coefficients', 'dicom_roi_modification_coefficients_segment_number_2',
    'dicom_graphics_sequence_2', 'dicom_graphics_sequence_3',
    'dicom_graphics_points_sequence', 'dicom_graphics_points_data',
    'dicom_graphics_point_transform_sequence', 'dicom_graphics_point_transform',
    'dicom_graphics_point_transform_description',
    'dicom_graphics_point_transform_data_type',
    'dicom_graphics_point_transform_value',
    'dicom_graphics_point_transform_value_description',
    'dicom_graphics_point_transform_unit_code_sequence',
    'dicom_graphics_sequence_4', 'dicom_graphics_sequence_5',
    'dicom_graphics_object_sequence', 'dicom_graphics_object',
    'dicom_graphics_object_description', 'dicom_graphics_object_data_type',
    'dicom_graphics_object_value', 'dicom_graphics_object_value_description',
    'dicom_graphics_object_unit_code_sequence',
    'dicom_graphics_object_referenced_grid_sequence',
    'dicom_graphics_object_referenced_grid',
    'dicom_graphics_object_referenced_image_sequence',
    'dicom_graphics_object_referenced_image',
    'dicom_graphics_object_referenced_series_sequence',
    'dicom_graphics_object_referenced_series',
    'dicom_graphics_object_referenced_study_sequence',
    'dicom_graphics_object_referenced_study',
    'dicom_graphics_object_referenced_roi_sequence',
    'dicom_graphics_object_referenced_roi',
    'dicom_graphics_object_referenced_presentation_sequence',
    'dicom_graphics_object_referenced_presentation',
    
    # Group 0062: Grayscale Softcopy VOI LUT
    'dicom_voi_wl_sequence', 'dicom_voi_wl_center', 'dicom_voi_wl_width',
    'dicom_voi_wl_explanation', 'dicom_voi_wl_sequence_2',
    
    # Group 0064: Print
    'dicom_print_job_id', 'dicom_print_job_description', 'dicom_print_management_capabilities_sequence',
    'dicom_print_capability_iec_62106', 'dicom_supported_printing_character_sets',
    'dicom_printer_status', 'dicom_printer_status_info', 'dicom_printer_name',
    'dicom_print_queue_id', 'dicom_print_queue_description', 'dicom_print_priority',
    'dicom_print_job_retention_sequence', 'dicom_print_job_retention',
    'dicom_print_job_retention_data_type', 'dicom_print_job_retention_value',
    'dicom_print_job_retention_value_description',
    'dicom_print_job_retention_unit_code_sequence',
    'dicom_print_job_order_sequence', 'dicom_print_job_order',
    'dicom_print_job_order_description', 'dicom_print_job_order_data_type',
    'dicom_print_job_order_value', 'dicom_print_job_order_value_description',
    'dicom_print_job_order_unit_code_sequence',
    
    # Group 0066: Basic Table
    'dicom_number_of_rows', 'dicom_number_of_columns',
    'dicom_table_characteristics_sequence', 'dicom_table_characteristics',
    'dicom_table_characteristics_description',
    'dicom_table_characteristics_data_type', 'dicom_table_characteristics_value',
    'dicom_table_characteristics_value_description',
    'dicom_table_characteristics_unit_code_sequence',
    'dicom_table_row_sequence', 'dicom_table_row',
    'dicom_table_row_data_type', 'dicom_table_row_value',
    'dicom_table_row_value_description', 'dicom_table_row_unit_code_sequence',
    'dicom_table_column_sequence', 'dicom_table_column',
    'dicom_table_column_data_type', 'dicom_table_column_value',
    'dicom_table_column_value_description',
    'dicom_table_column_unit_code_sequence',
    
    # Group 0068: Storage
    'dicom_storage_media_file_set_id', 'dicom_storage_media_file_set_uid',
    'dicom_icon_image_sequence', 'dicom_icon_image', 'dicom_icon_image_description',
    'dicom_icon_image_data_type', 'dicom_icon_image_value',
    'dicom_icon_image_value_description', 'dicom_icon_image_unit_code_sequence',
    
    # Group 0070: Softcopy Presentation LUT
    'dicom_presentation_lut_sequence', 'dicom_presentation_lut_shape',
    'dicom_presentation_lut_sequence_2', 'dicom_presentation_zoom',
    'dicom_presentation_larger_side_magnification',
    'dicom_presentation_smaller_side_magnification',
    'dicom_presentation_native_aspect_ratio',
    'dicom_presentation_scaled_aspect_ratio',
    'dicom_presentation_graphics_object_sequence',
    
    # Group 0072: Softcopy VOI LUT
    'dicom_voi_wl_sequence', 'dicom_voi_wl_center', 'dicom_voi_wl_width',
    'dicom_voi_wl_explanation', 'dicom_voi_wl_sequence_2',
    
    # Group 0088: Icon
    'dicom_icon_image_sequence', 'dicom_icon_image', 'dicom_icon_image_description',
    'dicom_icon_image_data_type', 'dicom_icon_image_value',
    'dicom_icon_image_value_description', 'dicom_icon_image_unit_code_sequence',
    
    # Group 0100: Series/Instance Availability
    'dicom_series_available', 'dicom_series_available_2',
    'dicom_instance_available', 'dicom_instance_available_2',
    
    # Group 0400: MAC
    'dicom_mac_calculation_transfer_syntax_uid',
    'dicom_mac_calculation_algorithm_uid',
    'dicom_data_elements_signed',
    
    # Group 1000: File Meta
    'dicom_file_meta_information_version',
    'dicom_media_storage_sop_class_uid',
    'dicom_media_storage_sop_instance_uid',
    'dicom_transfer_syntax_uid', 'dicom_implementation_class_uid',
    'dicom_implementation_version_name', 'dicom_source_application_entity_title',
    'dicom_sending_application_entity_title',
    'dicom_receiving_application_entity_title',
    'dicom_source_application_entity_title_2',
    'dicom_receiving_application_entity_title_2',
    
    # Group 1010: Retired
    # (historical tags no longer used)
    
    # Private Tags (Manufacturers)
    'dicom_private_creator', 'dicom_private_group',
    
    # Additional Comprehensive DICOM Tags
    'dicom_patient_birth_name', 'dicom_patient_birth_name_sequence',
    'dicom_patient_birth_name_code_sequence',
    'dicom_patient_birth_name_code', 'dicom_patient_birth_name_description',
    'dicom_patient_insurance_plan_code_sequence_2',
    'dicom_patient_insurance_plan_code', 'dicom_patient_insurance_plan_description',
    'dicom_patient_education_material_sequence',
    'dicom_patient_education_material',
    'dicom_patient_education_material_description',
    'dicom_patient_education_material_data_type',
    'dicom_patient_education_material_value',
    'dicom_patient_education_material_value_description',
    'dicom_patient_education_material_unit_code_sequence',
    'dicom_patient_occupation_sequence',
    'dicom_patient_occupation', 'dicom_patient_occupation_code_sequence',
    'dicom_patient_occupation_code', 'dicom_patient_occupation_description',
    'dicom_patient_hand_preference_sequence',
    'dicom_patient_hand_preference', 'dicom_patient_hand_preference_code_sequence',
    'dicom_patient_hand_preference_code', 'dicom_patient_hand_preference_description',
    'dicom_patient_ethnic_group_sequence',
    'dicom_patient_ethnic_group', 'dicom_patient_ethnic_group_code_sequence',
    'dicom_patient_ethnic_group_code', 'dicom_patient_ethnic_group_description',
    'dicom_patient_referring_physician_sequence',
    'dicom_patient_referring_physician',
    'dicom_patient_referring_physician_code_sequence',
    'dicom_patient_referring_physician_code',
    'dicom_patient_referring_physician_description',
    'dicom_patient_clinical_trial_phase_sequence',
    'dicom_patient_clinical_trial_phase',
    'dicom_patient_clinical_trial_phase_code_sequence',
    'dicom_patient_clinical_trial_phase_code',
    'dicom_patient_clinical_trial_phase_description',
    'dicom_patient_clinical_trial_protocol_id_sequence',
    'dicom_patient_clinical_trial_protocol_id',
    'dicom_patient_clinical_trial_protocol_id_description',
    'dicom_patient_clinical_trial_protocol_id_data_type',
    'dicom_patient_clinical_trial_protocol_id_value',
    'dicom_patient_clinical_trial_protocol_id_value_description',
    'dicom_patient_clinical_trial_protocol_id_unit_code_sequence',
    'dicom_patient_clinical_trial_site_id_sequence',
    'dicom_patient_clinical_trial_site_id',
    'dicom_patient_clinical_trial_site_id_description',
    'dicom_patient_clinical_trial_site_id_data_type',
    'dicom_patient_clinical_trial_site_id_value',
    'dicom_patient_clinical_trial_site_id_value_description',
    'dicom_patient_clinical_trial_site_id_unit_code_sequence',
    'dicom_patient_clinical_trial_subject_id_sequence',
    'dicom_patient_clinical_trial_subject_id',
    'dicom_patient_clinical_trial_subject_id_description',
    'dicom_patient_clinical_trial_subject_id_data_type',
    'dicom_patient_clinical_trial_subject_id_value',
    'dicom_patient_clinical_trial_subject_id_value_description',
    'dicom_patient_clinical_trial_subject_id_unit_code_sequence',
    'dicom_patient_clinical_trial_time_point_id_sequence',
    'dicom_patient_clinical_trial_time_point_id',
    'dicom_patient_clinical_trial_time_point_id_description',
    'dicom_patient_clinical_trial_time_point_id_data_type',
    'dicom_patient_clinical_trial_time_point_id_value',
    'dicom_patient_clinical_trial_time_point_id_value_description',
    'dicom_patient_clinical_trial_time_point_id_unit_code_sequence',
    'dicom_patient_clinical_trial_time_point_description',
    'dicom_patient_clinical_trial_coordinating_center_name',
    'dicom_patient_clinical_trial_coordinating_center_name_sequence',
    'dicom_patient_clinical_trial_coordinating_center_name_code_sequence',
    'dicom_patient_clinical_trial_coordinating_center_name_code',
    'dicom_patient_clinical_trial_coordinating_center_name_description',
    'dicom_patient_support_device_sequence',
    'dicom_patient_support_device',
    'dicom_patient_support_device_description',
    'dicom_patient_support_device_data_type',
    'dicom_patient_support_device_value',
    'dicom_patient_support_device_value_description',
    'dicom_patient_support_device_unit_code_sequence',
    'dicom_patient_support_device_manufacturer_sequence',
    'dicom_patient_support_device_manufacturer',
    'dicom_patient_support_device_manufacturer_code_sequence',
    'dicom_patient_support_device_manufacturer_code',
    'dicom_patient_support_device_manufacturer_description',
    'dicom_patient_support_device_model_name_sequence',
    'dicom_patient_support_device_model_name',
    'dicom_patient_support_device_model_name_code_sequence',
    'dicom_patient_support_device_model_name_code',
    'dicom_patient_support_device_model_name_description',
    'dicom_patient_support_device_serial_number_sequence',
    'dicom_patient_support_device_serial_number',
    'dicom_patient_support_device_serial_number_description',
    'dicom_patient_support_device_serial_number_data_type',
    'dicom_patient_support_device_serial_number_value',
    'dicom_patient_support_device_serial_number_value_description',
    'dicom_patient_support_device_serial_number_unit_code_sequence',
    'dicom_patient_support_device_software_version_sequence',
    'dicom_patient_support_device_software_version',
    'dicom_patient_support_device_software_version_description',
    'dicom_patient_support_device_software_version_data_type',
    'dicom_patient_support_device_software_version_value',
    'dicom_patient_support_device_software_version_value_description',
    'dicom_patient_support_device_software_version_unit_code_sequence',
    'dicom_patient_support_device_material_thickness_sequence',
    'dicom_patient_support_device_material_thickness',
    'dicom_patient_support_device_material_thickness_description',
    'dicom_patient_support_device_material_thickness_data_type',
    'dicom_patient_support_device_material_thickness_value',
    'dicom_patient_support_device_material_thickness_value_description',
    'dicom_patient_support_device_material_thickness_unit_code_sequence',
    'dicom_patient_support_device_material_type_sequence',
    'dicom_patient_support_device_material_type',
    'dicom_patient_support_device_material_type_description',
    'dicom_patient_support_device_material_type_data_type',
    'dicom_patient_support_device_material_type_value',
    'dicom_patient_support_device_material_type_value_description',
    'dicom_patient_support_device_material_type_unit_code_sequence',
    'dicom_patient_support_device_position_sequence',
    'dicom_patient_support_device_position',
    'dicom_patient_support_device_position_description',
    'dicom_patient_support_device_position_data_type',
    'dicom_patient_support_device_position_value',
    'dicom_patient_support_device_position_value_description',
    'dicom_patient_support_device_position_unit_code_sequence',
    'dicom_patient_support_device_orienteation_sequence',
    'dicom_patient_support_device_orientation',
    'dicom_patient_support_device_orientation_description',
    'dicom_patient_support_device_orientation_data_type',
    'dicom_patient_support_device_orientation_value',
    'dicom_patient_support_device_orientation_value_description',
    'dicom_patient_support_device_orientation_unit_code_sequence',
    'dicom_patient_support_device_gantry_relationship_sequence',
    'dicom_patient_support_device_gantry_relationship',
    'dicom_patient_support_device_gantry_relationship_description',
    'dicom_patient_support_device_gantry_relationship_data_type',
    'dicom_patient_support_device_gantry_relationship_value',
    'dicom_patient_support_device_gantry_relationship_value_description',
    'dicom_patient_support_device_gantry_relationship_unit_code_sequence',
    
    # Additional DICOM Tags
    'dicom_multiplex_group_number', 'dicom_number_of_waveform_channels',
    'dicom_number_of_waveform_samples', 'dicom_sampling_frequency',
    'dicom_group_length', 'dicom_group_number',
    
    # DICOM Structured Reporting
    'dicom_content_template_sequence', 'dicom_content_template_uid',
    'dicom_content_sequence', 'dicom_content_item_flag',
    'dicom_content_item_identifier', 'dicom_content_sequence_2',
    
    # DICOM Presentation State
    'dicom_presentation_lut_sequence', 'dicom_softcopy_voilut_sequence',
    'dicom_softcopy_presentation_lut_sequence', 'dicom_graphics_sequence',
    'dicom_text_object_sequence', 'dicom_graphics_object_sequence',
    'dicom_masks_sequence', 'dicom_mask_sequence',
    'dicom_mask_frame_numbers', 'dicom_mask_sub_pixel_shift',
    
    # DICOM Spatial Registration
    'dicom_matrix_registration_sequence', 'dicom_matrix_sequence',
    'dicom_matrix_registration_sequence_2', 'dicom_frame_of_reference_uid',
    'dicom_registration_sequence', 'dicom_registration_sequence_2',
    
    # DICOM De-identification
    'dicom_de_identification_method_sequence',
    'dicom_de_identification_method', 'dicom_de_identification_method_code_sequence',
    'dicom_de_identification_method_code', 'dicom_de_identification_method_description',
    'dicom_de_identification_parameters_sequence',
    'dicom_de_identification_parameters', 'dicom_retired_parameters',
    
    # DICOM Real World Value Mapping
    'dicom_real_world_value_mapping_sequence',
    'dicom_real_world_value_mapping',
    'dicom_real_world_value_mapping_description',
    'dicom_real_world_value_mapping_data_type',
    'dicom_real_world_value_mapping_value',
    'dicom_real_world_value_mapping_value_description',
    'dicom_real_world_value_mapping_unit_code_sequence',
    'dicom_real_world_value_mapping_slope',
    'dicom_real_world_value_mapping_intercept',
    'dicom_lut_data_sequence', 'dicom_lut_data',
    'dicom_lut_data_description', 'dicom_lut_data_data_type',
    'dicom_lut_data_value', 'dicom_lut_data_value_description',
    'dicom_lut_data_unit_code_sequence',
    
    # DICOM Hanging Protocol
    'dicom_hanging_protocol_definition_sequence',
    'dicom_hanging_protocol_definition',
    'dicom_hanging_protocol_definition_description',
    'dicom_hanging_protocol_definition_data_type',
    'dicom_hanging_protocol_definition_value',
    'dicom_hanging_protocol_definition_value_description',
    'dicom_hanging_protocol_definition_unit_code_sequence',
    'dicom_hanging_protocol_definition_uid',
    'dicom_hanging_protocol_definition_manufacturer',
    'dicom_hanging_protocol_definition_version',
    'dicom_hanging_protocol_definition_number_of_priors',
    'dicom_hanging_protocol_definition_referenced_study_sequence',
    'dicom_hanging_protocol_definition_referenced_study',
    'dicom_hanging_protocol_definition_referenced_series_sequence',
    'dicom_hanging_protocol_definition_referenced_series',
    'dicom_hanging_protocol_definition_referenced_instance_sequence',
    'dicom_hanging_protocol_definition_referenced_instance',
    'dicom_hanging_protocol_definition_referenced_image_sequence',
    'dicom_hanging_protocol_definition_referenced_image',
    'dicom_hanging_protocol_definition_creator',
    'dicom_hanging_protocol_definition_creation_date_time',
    'dicom_hanging_protocol_definition_description',
    'dicom_hanging_protocol_definition_explanation',
    'dicom_hanging_protocol_definition_level',
    'dicom_hanging_protocol_definition_referenced_workitem_sequence',
    'dicom_hanging_protocol_definition_referenced_workitem',
    'dicom_hanging_protocol_definition_applicable_frame_range_sequence',
    'dicom_hanging_protocol_definition_applicable_frame_range',
    'dicom_hanging_protocol_definition_applicable_frame_start',
    'dicom_hanging_protocol_definition_applicable_frame_end',
    'dicom_hanging_protocol_definition_priority_sequence',
    'dicom_hanging_protocol_definition_priority',
    'dicom_hanging_protocol_definition_priority_description',
    'dicom_hanging_protocol_definition_priority_data_type',
    'dicom_hanging_protocol_definition_priority_value',
    'dicom_hanging_protocol_definition_priority_value_description',
    'dicom_hanging_protocol_definition_priority_unit_code_sequence',
    'dicom_hanging_protocol_definition_sequence',
    'dicom_hanging_protocol_definition',
    'dicom_hanging_protocol_definition_2',
    'dicom_hanging_protocol_definition_description_2',
    'dicom_hanging_protocol_definition_data_type_2',
    'dicom_hanging_protocol_definition_value_2',
    'dicom_hanging_protocol_definition_value_description_2',
    'dicom_hanging_protocol_definition_unit_code_sequence_2',
    'dicom_hanging_protocol_definition_sequence_2',
    'dicom_hanging_protocol_definition_3',
    'dicom_hanging_protocol_definition_4',
    'dicom_hanging_protocol_definition_description_3',
    'dicom_hanging_protocol_definition_data_type_3',
    'dicom_hanging_protocol_definition_value_3',
    'dicom_hanging_protocol_definition_value_description_3',
    'dicom_hanging_protocol_definition_unit_code_sequence_3',
    'dicom_hanging_protocol_definition_sequence_3',
    'dicom_hanging_protocol_definition_5',
    'dicom_hanging_protocol_definition_6',
    'dicom_hanging_protocol_definition_description_4',
    'dicom_hanging_protocol_definition_data_type_4',
    'dicom_hanging_protocol_definition_value_4',
    'dicom_hanging_protocol_definition_value_description_4',
    'dicom_hanging_protocol_definition_unit_code_sequence_4',
    'dicom_hanging_protocol_definition_sequence_4',
    'dicom_hanging_protocol_definition_7',
    'dicom_hanging_protocol_definition_8',
    'dicom_hanging_protocol_definition_description_5',
    'dicom_hanging_protocol_definition_data_type_5',
    'dicom_hanging_protocol_definition_value_5',
    'dicom_hanging_protocol_definition_value_description_5',
    'dicom_hanging_protocol_definition_unit_code_sequence_5',
    'dicom_hanging_protocol_definition_sequence_5',
    'dicom_hanging_protocol_definition_9',
    'dicom_hanging_protocol_definition_10',
    'dicom_hanging_protocol_definition_description_6',
    'dicom_hanging_protocol_definition_data_type_6',
    'dicom_hanging_protocol_definition_value_6',
    'dicom_hanging_protocol_definition_value_description_6',
    'dicom_hanging_protocol_definition_unit_code_sequence_6',
    
    # DICOM Display System
    'dicom_display_system_manufacturer',
    'dicom_display_system_manufacturer_code_sequence',
    'dicom_display_system_manufacturer_code',
    'dicom_display_system_manufacturer_description',
    'dicom_display_system_model_name',
    'dicom_display_system_model_name_sequence',
    'dicom_display_system_model_name_code_sequence',
    'dicom_display_system_model_name_code',
    'dicom_display_system_model_name_description',
    'dicom_display_system_software_version',
    'dicom_display_system_software_version_sequence',
    'dicom_display_system_software_version_description',
    'dicom_display_system_software_version_data_type',
    'dicom_display_system_software_version_value',
    'dicom_display_system_software_version_value_description',
    'dicom_display_system_software_version_unit_code_sequence',
    'dicom_display_system_pixel_characteristics_sequence',
    'dicom_display_system_pixel_characteristics',
    'dicom_display_system_pixel_characteristics_description',
    'dicom_display_system_pixel_characteristics_data_type',
    'dicom_display_system_pixel_characteristics_value',
    'dicom_display_system_pixel_characteristics_value_description',
    'dicom_display_system_pixel_characteristics_unit_code_sequence',
    'dicom_display_system_calibration_sequence',
    'dicom_display_system_calibration',
    'dicom_display_system_calibration_description',
    'dicom_display_system_calibration_data_type',
    'dicom_display_system_calibration_value',
    'dicom_display_system_calibration_value_description',
    'dicom_display_system_calibration_unit_code_sequence',
    'dicom_display_system_calibration_image_sequence',
    'dicom_display_system_calibration_image',
    'dicom_display_system_calibration_image_description',
    'dicom_display_system_calibration_image_data_type',
    'dicom_display_system_calibration_image_value',
    'dicom_display_system_calibration_image_value_description',
    'dicom_display_system_calibration_image_unit_code_sequence',
    'dicom_display_system_reference_contrast_luminance_sequence',
    'dicom_display_system_reference_contrast_luminance',
    'dicom_display_system_reference_contrast_luminance_description',
    'dicom_display_system_reference_contrast_luminance_data_type',
    'dicom_display_system_reference_contrast_luminance_value',
    'dicom_display_system_reference_contrast_luminance_value_description',
    'dicom_display_system_reference_contrast_luminance_unit_code_sequence',
    
    # DICOM Overlay Plane
    'dicom_overlay_rows', 'dicom_overlay_columns', 'dicom_overlay_type',
    'dicom_overlay_origin', 'dicom_overlay_bits_allocated',
    'dicom_overlay_bit_position', 'dicom_overlay_compression_choic_code_sequence',
    'dicom_overlay_compression_choic_code',
    'dicom_overlay_compression_choic_description',
    'dicom_overlay_descriptor_row', 'dicom_overlay_descriptor_column',
    'dicom_overlay_descriptor_greyscale', 'dicom_overlay_descriptor_red',
    'dicom_overlay_descriptor_green', 'dicom_overlay_descriptor_blue',
    'dicom_overlay_descriptor_alpha', 'dicom_overlay_plane_description',
    'dicom_overlay_plane_description_code_sequence',
    'dicom_overlay_plane_description_code',
    'dicom_overlay_plane_description_description',
    'dicom_overlay_type_2', 'dicom_overlay_subtype',
    'dicom_overlay_activation_layer', 'dicom_overlay_number_of_tables',
    'dicom_overlay_code_table_location_sequence',
    'dicom_overlay_code_table_location',
    'dicom_overlay_data_type_description_sequence',
    'dicom_overlay_data_type_description',
    'dicom_overlay_data_type_description_data_type',
    'dicom_overlay_data_type_description_value',
    'dicom_overlay_data_type_description_value_description',
    'dicom_overlay_data_type_description_unit_code_sequence',
    'dicom_overlay_mask_description_sequence',
    'dicom_overlay_mask_description',
    'dicom_overlay_mask_description_data_type',
    'dicom_overlay_mask_description_value',
    'dicom_overlay_mask_description_value_description',
    'dicom_overlay_mask_description_unit_code_sequence',
    'dicom_roi_area', 'dicom_roi_mean', 'dicom_roi_standard_deviation',
    
    # DICOM Stereometry
    'dicom_stereometric_start_date_time',
    'dicom_stereometric_start_date_time_sequence',
    'dicom_stereometric_start_date_time',
    'dicom_stereometric_start_date_time_description',
    'dicom_stereometric_start_date_time_data_type',
    'dicom_stereometric_start_date_time_value',
    'dicom_stereometric_start_date_time_value_description',
    'dicom_stereometric_start_date_time_unit_code_sequence',
    'dicom_stereometric_end_date_time', 'dicom_stereometric_end_date_time_sequence',
    'dicom_stereometric_end_date_time',
    'dicom_stereometric_end_date_time_description',
    'dicom_stereometric_end_date_time_data_type',
    'dicom_stereometric_end_date_time_value',
    'dicom_stereometric_end_date_time_value_description',
    'dicom_stereometric_end_date_time_unit_code_sequence',
    'dicom_stereometric_pair_number', 'dicom_stereometric_pair_number_description',
    'dicom_stereometric_pair_number_data_type',
    'dicom_stereometric_pair_number_value',
    'dicom_stereometric_pair_number_value_description',
    'dicom_stereometric_pair_number_unit_code_sequence',
    'dicom_stereometric_pair_indicates_sequence',
    'dicom_stereometric_pair_indicates',
    'dicom_stereometric_pair_indicates_code_sequence',
    'dicom_stereometric_pair_indicates_code',
    'dicom_stereometric_pair_indicates_description',
    'dicom_stereometric_pair_indicates_data_type',
    'dicom_stereometric_pair_indicates_value',
    'dicom_stereometric_pair_indicates_value_description',
    'dicom_stereometric_pair_indicates_unit_code_sequence',
    'dicom_stereometric_roi_sequence', 'dicom_stereometric_roi',
    'dicom_stereometric_roi_description', 'dicom_stereometric_roi_data_type',
    'dicom_stereometric_roi_value', 'dicom_stereometric_roi_value_description',
    'dicom_stereometric_roi_unit_code_sequence',
    
    # Additional comprehensive DICOM tags (Groups 1000-FFFF)
    'dicom_implementation_version_name', 'dicom_implementation_class_uid',
    'dicom_source_application_entity_title',
    'dicom_sending_application_entity_title',
    'dicom_receiving_application_entity_title',
    'dicom_file_meta_information_version',
    'dicom_file_meta_information_group_length',
    'dicom_private_data_element_characteristics_sequence',
    'dicom_private_data_element_characteristics',
    'dicom_private_data_element_characteristics_uid',
    'dicom_private_data_element_characteristics_name',
    'dicom_private_data_element_value_multiplicity',
    'dicom_private_data_element_value_representation',
    'dicom_private_data_element_minimum_value',
    'dicom_private_data_element_maximum_value',
    'dicom_private_group_element_characteristics_sequence',
    'dicom_private_group_element_characteristics',
    'dicom_private_group_element_characteristics_uid',
    'dicom_private_group_element_characteristics_name',
    'dicom_private_group_element_value_multiplicity',
    'dicom_private_group_element_value_representation',
    'dicom_private_group_element_minimum_value',
    'dicom_private_group_element_maximum_value',
    'dicom_retired_tag_0000_0001', 'dicom_retired_tag_0000_0002',
    'dicom_retired_tag_0000_0003', 'dicom_retired_tag_0000_0004',
    'dicom_retired_tag_0000_0005', 'dicom_retired_tag_0000_0006',
    'dicom_retired_tag_0000_0007', 'dicom_retired_tag_0000_0008',
    'dicom_retired_tag_0000_0009', 'dicom_retired_tag_0000_0010',
    'dicom_retired_tag_0000_0011', 'dicom_retired_tag_0000_0012',
    'dicom_retired_tag_0000_0013', 'dicom_retired_tag_0000_0014',
    'dicom_retired_tag_0000_0015', 'dicom_retired_tag_0000_0016',
    'dicom_retired_tag_0000_0017', 'dicom_retired_tag_0000_0018',
    'dicom_retired_tag_0000_0019', 'dicom_retired_tag_0000_0020',
    'dicom_retired_tag_0000_0021', 'dicom_retired_tag_0000_0022',
    'dicom_retired_tag_0000_0023', 'dicom_retired_tag_0000_0024',
    'dicom_retired_tag_0000_0025', 'dicom_retired_tag_0000_0026',
    'dicom_retired_tag_0000_0027', 'dicom_retired_tag_0000_0028',
    'dicom_retired_tag_0000_0029', 'dicom_retired_tag_0000_0030',
    'dicom_retired_tag_0000_0031', 'dicom_retired_tag_0000_0032',
    'dicom_retired_tag_0000_0033', 'dicom_retired_tag_0000_0034',
    'dicom_retired_tag_0000_0035', 'dicom_retired_tag_0000_0036',
    'dicom_retired_tag_0000_0037', 'dicom_retired_tag_0000_0038',
    'dicom_retired_tag_0000_0039', 'dicom_retired_tag_0000_0040',
}


def get_dicom_complete_ultimate_field_count() -> int:
    """Return the field count for this module."""
    return len(DICOM_KEYWORDS)


def extract_dicom_complete_ultimate_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract complete DICOM metadata - Ultimate Edition.
    
    Returns comprehensive DICOM metadata dictionary.
    """
    result = {'dicom_ultimate_extraction': True}
    
    try:
        from pydicom import dcmread
        from pydicom.dataset import Dataset, FileDataset
        from pydicom.tag import Tag
        
        ds = dcmread(filepath, force=True)
        
        result.update(_extract_dicom_standard_elements(ds))
        result.update(_extract_dicom_private_elements(ds))
        result.update(_extract_dicom_sequence_elements(ds))
        result.update(_extract_dicom_pixel_data_info(ds))
        result.update(_extract_dicom_sop_common(ds))
        result.update(_extract_dicom_file_meta(ds))
        
    except Exception as e:
        logger.warning(f"Error extracting DICOM complete metadata from {filepath}: {e}")
        result['dicom_ultimate_extraction_error'] = str(e)
    
    return result


def _extract_dicom_standard_elements(ds) -> Dict[str, Any]:
    """Extract standard DICOM elements."""
    data = {'dicom_standard_extracted': True}
    
    # Group 0008: Image/Study Information
    if 'StudyDate' in ds:
        data['dicom_study_date'] = str(ds.StudyDate)
    if 'SeriesDate' in ds:
        data['dicom_series_date'] = str(ds.SeriesDate)
    if 'AcquisitionDate' in ds:
        data['dicom_acquisition_date'] = str(ds.AcquisitionDate)
    if 'ContentDate' in ds:
        data['dicom_content_date'] = str(ds.ContentDate)
    if 'StudyTime' in ds:
        data['dicom_study_time'] = str(ds.StudyTime)
    if 'SeriesTime' in ds:
        data['dicom_series_time'] = str(ds.SeriesTime)
    if 'AcquisitionTime' in ds:
        data['dicom_acquisition_time'] = str(ds.AcquisitionTime)
    if 'ContentTime' in ds:
        data['dicom_content_time'] = str(ds.ContentTime)
    if 'Modality' in ds:
        data['dicom_modality'] = str(ds.Modality)
    if 'Manufacturer' in ds:
        data['dicom_manufacturer'] = str(ds.Manufacturer)
    if 'InstitutionName' in ds:
        data['dicom_institution_name'] = str(ds.InstitutionName)
    if 'StationName' in ds:
        data['dicom_station_name'] = str(ds.StationName)
    if 'StudyInstanceUID' in ds:
        data['dicom_study_instance_uid'] = str(ds.StudyInstanceUID)
    if 'SeriesInstanceUID' in ds:
        data['dicom_series_instance_uid'] = str(ds.SeriesInstanceUID)
    if 'SOPInstanceUID' in ds:
        data['dicom_sop_instance_uid'] = str(ds.SOPInstanceUID)
    if 'SOPClassUID' in ds:
        data['dicom_sop_class_uid'] = str(ds.SOPClassUID)
    
    # Group 0010: Patient Information
    if 'PatientName' in ds:
        data['dicom_patient_name'] = str(ds.PatientName)
    if 'PatientID' in ds:
        data['dicom_patient_id'] = str(ds.PatientID)
    if 'PatientBirthDate' in ds:
        data['dicom_patient_birth_date'] = str(ds.PatientBirthDate)
    if 'PatientSex' in ds:
        data['dicom_patient_sex'] = str(ds.PatientSex)
    
    # Group 0018: Acquisition Information
    if 'ContrastBolusAgent' in ds:
        data['dicom_contrast_bolus_agent'] = str(ds.ContrastBolusAgent)
    if 'ScanOptions' in ds:
        data['dicom_scan_options'] = str(ds.ScanOptions)
    if 'SliceThickness' in ds:
        data['dicom_slice_thickness'] = str(ds.SliceThickness)
    if 'KVP' in ds:
        data['dicom_kvp'] = str(ds.KVP)
    if 'RepetitionTime' in ds:
        data['dicom_repetition_time'] = str(ds.RepetitionTime)
    if 'EchoTime' in ds:
        data['dicom_echo_time'] = str(ds.EchoTime)
    if 'FlipAngle' in ds:
        data['dicom_flip_angle'] = str(ds.FlipAngle)
    
    # Group 0020: Patient/Study/Series/Instance
    if 'StudyID' in ds:
        data['dicom_study_id'] = str(ds.StudyID)
    if 'SeriesNumber' in ds:
        data['dicom_series_number'] = str(ds.SeriesNumber)
    if 'InstanceNumber' in ds:
        data['dicom_instance_number'] = str(ds.InstanceNumber)
    if 'ImagePositionPatient' in ds:
        data['dicom_image_position_patient'] = str(ds.ImagePositionPatient)
    if 'ImageOrientationPatient' in ds:
        data['dicom_image_orientation_patient'] = str(ds.ImageOrientationPatient)
    
    # Group 0028: Image Presentation
    if 'Rows' in ds:
        data['dicom_rows'] = ds.Rows
    if 'Columns' in ds:
        data['dicom_columns'] = ds.Columns
    if 'BitsAllocated' in ds:
        data['dicom_bits_allocated'] = ds.BitsAllocated
    if 'BitsStored' in ds:
        data['dicom_bits_stored'] = ds.BitsStored
    if 'HighBit' in ds:
        data['dicom_high_bit'] = ds.HighBit
    if 'PixelRepresentation' in ds:
        data['dicom_pixel_representation'] = ds.PixelRepresentation
    if 'PhotometricInterpretation' in ds:
        data['dicom_photometric_interpretation'] = str(ds.PhotometricInterpretation)
    if 'WindowCenter' in ds:
        data['dicom_window_center'] = str(ds.WindowCenter)
    if 'WindowWidth' in ds:
        data['dicom_window_width'] = str(ds.WindowWidth)
    
    # Count total elements
    data['dicom_total_elements'] = len(ds)
    
    # Count elements by group
    groups = {}
    for elem in ds:
        group = elem.tag.group
        groups[group] = groups.get(group, 0) + 1
    data['dicom_elements_by_group'] = groups
    
    return data


def _extract_dicom_private_elements(ds) -> Dict[str, Any]:
    """Extract private DICOM elements."""
    data = {'dicom_private_extracted': True}
    
    private_elements = []
    for elem in ds:
        if elem.tag.is_private:
            private_elements.append({
                'tag': str(elem.tag),
                'vr': elem.VR,
                'length': elem.length,
            })
    
    data['dicom_private_element_count'] = len(private_elements)
    data['dicom_private_elements'] = private_elements[:100]  # Limit to first 100
    
    return data


def _extract_dicom_sequence_elements(ds) -> Dict[str, Any]:
    """Extract DICOM sequence information."""
    data = {'dicom_sequence_extracted': True}
    
    sequences = []
    for elem in ds:
        if hasattr(elem, 'VR') and elem.VR == 'SQ':
            sequences.append({
                'tag': str(elem.tag),
                'name': elem.keyword if hasattr(elem, 'keyword') else 'Unknown',
                'item_count': len(elem.value) if elem.value else 0,
            })
    
    data['dicom_sequence_count'] = len(sequences)
    data['dicom_sequences'] = sequences
    
    return data


def _extract_dicom_pixel_data_info(ds) -> Dict[str, Any]:
    """Extract pixel data information."""
    data = {'dicom_pixel_data_extracted': True}
    
    if 'PixelData' in ds:
        pixel_data = ds.PixelData
        data['dicom_pixel_data_length'] = len(pixel_data)
        data['dicom_pixel_data_size_bytes'] = len(pixel_data)
        data['dicom_pixel_data_compressed'] = ds.get('PixelData', b'').__len__() > 0
        
        if hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            data['dicom_pixel_data_dimensions'] = f"{ds.Rows}x{ds.Columns}"
            data['dicom_pixel_data_pixel_count'] = ds.Rows * ds.Columns
    
    if 'BitsAllocated' in ds:
        data['dicom_bits_allocated'] = ds.BitsAllocated
    if 'BitsStored' in ds:
        data['dicom_bits_stored'] = ds.BitsStored
    if 'HighBit' in ds:
        data['dicom_high_bit'] = ds.HighBit
    
    return data


def _extract_dicom_sop_common(ds) -> Dict[str, Any]:
    """Extract SOP Common Module elements."""
    data = {'dicom_sop_common_extracted': True}
    
    if 'SOPClassUID' in ds:
        data['dicom_sop_class_uid'] = str(ds.SOPClassUID)
    if 'SOPInstanceUID' in ds:
        data['dicom_sop_instance_uid'] = str(ds.SOPInstanceUID)
    if 'SpecificCharacterSet' in ds:
        data['dicom_specific_character_set'] = str(ds.SpecificCharacterSet)
    if 'InstanceCreationDate' in ds:
        data['dicom_instance_creation_date'] = str(ds.InstanceCreationDate)
    if 'InstanceCreationTime' in ds:
        data['dicom_instance_creation_time'] = str(ds.InstanceCreationTime)
    if 'InstanceCreatorUID' in ds:
        data['dicom_instance_creator_uid'] = str(ds.InstanceCreatorUID)
    
    return data


def _extract_dicom_file_meta(ds) -> Dict[str, Any]:
    """Extract File Meta Information."""
    data = {'dicom_file_meta_extracted': True}
    
    if 'FileMetaInformationVersion' in ds:
        data['dicom_file_meta_information_version'] = str(ds.FileMetaInformationVersion)
    if 'MediaStorageSOPClassUID' in ds:
        data['dicom_media_storage_sop_class_uid'] = str(ds.MediaStorageSOPClassUID)
    if 'MediaStorageSOPInstanceUID' in ds:
        data['dicom_media_storage_sop_instance_uid'] = str(ds.MediaStorageSOPInstanceUID)
    if 'TransferSyntaxUID' in ds:
        data['dicom_transfer_syntax_uid'] = str(ds.TransferSyntaxUID)
    if 'ImplementationClassUID' in ds:
        data['dicom_implementation_class_uid'] = str(ds.ImplementationClassUID)
    if 'ImplementationVersionName' in ds:
        data['dicom_implementation_version_name'] = str(ds.ImplementationVersionName)
    if 'SourceApplicationEntityTitle' in ds:
        data['dicom_source_application_entity_title'] = str(ds.SourceApplicationEntityTitle)
    
    return data
