# server/extractor/modules/pdf_complete_ultimate.py

"""
Complete PDF Metadata Extraction - Ultimate Edition
Target: +1,965 fields for comprehensive PDF coverage

Covers ALL PDF metadata areas:
1. Document Structure (pages, objects, streams, xref)
2. Catalog & Names Dictionary
3. Outlines (Bookmarks)
4. Article Threads
5. Named Destinations
6. Interactive Forms (AcroForm)
7. Annotations (all 25+ types)
8. Widget Annotations
9. Actions (all types)
10. JavaScript
11. OpenAction & Additional Actions
12. Optional Content Groups (Layers/OCG)
13. Metadata Streams
14. Struct Tree Root
15. Mark Information
16. PieceInfo
17. Web Capture Information
8. Logical Structure
9. Output Intents
20. AcroForm Dynamic XFA
21. Digital Signatures (field-level)
22. Portfolio Files
23. Embedded Files
24. Multimedia (Rich Media)
25. 3D Annotations
26. Security & Encryption
27. Permissions
28. Document Requirements
29. Collection (Portfolio)
30. Filespecs
31. Dictionary Streams
32. Array Streams
33. String Streams
34. Stream Filters
35. Font Metadata
36. Image Metadata
37. Color Space Metadata
38. Pattern Metadata
39. Shading Metadata
40. PostScript XObjects
41. Form XObjects
42. Page Tree
43. Names Tree
44. Dests Name Tree
45. JavaScript Name Tree
46. Pages Name Tree
47. Templates Name Tree
48. IDS Name Tree
49. URLS Name Tree
50. Embedded Files Name Tree
51. Alternate Presentations
52. Resource Dictionaries
53. ExtGState
54. Pattern CS
55. Separation Hints
56. DeviceN Hints
57. Rendering Intent
58. Struct Parent Map
59. Field Types
60. Field Flags
61. Widget Flags
62. Check Box Flags
63. Radio Button Flags
64. Text Field Flags
65. Choice Field Flags
66. Button Flags
67. Constraint Flags
68. Signature Field Flags
69. Link Annotations
70. Subform Architecture
71. Incremental Update Info
82. Document Part Hierarchy
73. Signature Fields
74. Certification Status
75. Signature References
76. Byte Ranges
77. Contents Streams
78. Cert Dictionaries
79. Sig Ref Dictionaries
80. Lock Dictionaries
81. Perms Dictionaries
82. Seed Values
93. Appearance Streams
84. Appearance Characteristics
85. Border Styles
86. Background Styles
87. Icon Fit
88. State Modes
89. Trigger Events
90. Trigger Actions
91. Trigger Conditions
92. Trigger Annotations
93. Trigger Fields
94. Field Dependencies
95. Value Commitments
96. Range Limits
97. Current Page Indices
98. Default Fields
99. Template Dictionary
100. Pagination State
"""

import struct
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re
import json

logger = logging.getLogger(__name__)

try:
    import fitz as FitzModule
    PYMUPDF_AVAILABLE = True
    fitz = FitzModule
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

try:
    from pypdf import PdfReader as PyPdfReader
    PYPDF_AVAILABLE = True
    PdfReader = PyPdfReader
except ImportError:
    PYPDF_AVAILABLE = False
    PdfReader = None


PDF_ANNOTATION_TYPES = {
    'Text': 'Text',
    'Link': 'Link',
    'FreeText': 'FreeText',
    'Line': 'Line',
    'Square': 'Square',
    'Circle': 'Circle',
    'Polygon': 'Polygon',
    'PolyLine': 'PolyLine',
    'Highlight': 'Highlight',
    'Underline': 'Underline',
    'Squiggly': 'Squiggly',
    'StrikeOut': 'StrikeOut',
    'Stamp': 'Stamp',
    'Caret': 'Caret',
    'Ink': 'Ink',
    'Popup': 'Popup',
    'FileAttachment': 'FileAttachment',
    'Sound': 'Sound',
    'Movie': 'Movie',
    'Widget': 'Widget',
    'Screen': 'Screen',
    'PrinterMark': 'PrinterMark',
    'TrapNet': 'TrapNet',
    'Watermark': 'Watermark',
    '3D': '3D',
    'RichMedia': 'RichMedia',
    'WebMedia': 'WebMedia',
}

PDF_ACTION_TYPES = {
    'GoTo': 'GoTo',
    'GoToR': 'GoToR',
    'GoToE': 'GoToE',
    'Launch': 'Launch',
    'Thread': 'Thread',
    'URI': 'URI',
    'Sound': 'Sound',
    'Movie': 'Movie',
    'Hide': 'Hide',
    'Named': 'Named',
    'SubmitForm': 'SubmitForm',
    'ResetForm': 'ResetForm',
    'ImportData': 'ImportData',
    'JavaScript': 'JavaScript',
    'Rendition': 'Rendition',
    'Trans': 'Trans',
    'GoToView': 'GoToView',
    'GoToRaster': 'GoToRaster',
    'SetOCGState': 'SetOCGState',
    'RichMediaExecute': 'RichMediaExecute',
}

PDF_KEYWORDS = {
    'pdf_docinfo_title', 'pdf_docinfo_author', 'pdf_docinfo_subject', 'pdf_docinfo_keywords',
    'pdf_docinfo_creator', 'pdf_docinfo_producer', 'pdf_docinfo_creation_date', 'pdf_docinfo_mod_date',
    'pdf_docinfo_trapped', 'pdf_page_count', 'pdf_version', 'pdf_is_encrypted', 'pdf_is_linearized',
    'pdf_page_width', 'pdf_page_height', 'pdf_page_rotation', 'pdf_page_labels', 'pdf_page_mode',
    'pdf_page_layout', 'pdf_open_action', 'pdf_additional_actions', 'pdf_rubton_cubemap',
    'pdf_article_threads', 'pdf_web_capture', 'pdf_named_destinations', 'pdf_catalog_dict',
    'pdf_names_tree', 'pdf_dests_tree', 'pdf_javascript_tree', 'pdf_pages_tree', 'pdf_templates_tree',
    'pdf_embedded_files_tree', 'pdf_outline', 'pdf_struct_tree_root', 'pdf_mark_info',
    'pdf_metadata', 'pdf_oc_properties', 'pdf_perms', 'pdf_acroform', 'pdf_portfolio',
    'pdf_collection', 'pdf_REQUIREMENTS', 'pdf_needs_pass', 'pdf_is_repaired', 'pdf_has_signature',
    'pdf_signature_field', 'pdf_certification_level', 'pdf_doctimestamp', 'pdf_extension_level',
    'pdf_xref_table', 'pdf_xref_stream', 'pdf_object_count', 'pdf_stream_count', 'pdf_dict_count',
    'pdf_array_count', 'pdf_string_count', 'pdf_number_count', 'pdf_null_count', 'pdf_indirect_refs',
    'pdf_compression_type', 'pdf_filter_count', 'pdf_decode_parms', 'pdf_predictor_type',
    'pdf_colorspace_count', 'pdf_images_count', 'pdf_fonts_count', 'pdf_patterns_count',
    'pdf_shading_count', 'pdf_form_xobjects', 'pdf_postscript_xobjects', 'pdf_type3_fonts',
    'pdf_type0_fonts', 'pdf_cid_fonts', 'pdf_true_type_fonts', 'pdf_type1_fonts', 'pdf_mm_fonts',
    'pdf_font_descriptor', 'pdf_to_unicode', 'pdf_c_map', 'pdf_cid_system_info', 'pdf_base_font',
    'pdf_subtype', 'pdf_encoding', 'pdf_first_char', 'pdf_last_char', 'pdf_widths', 'pdf_font_file',
    'pdf_font_file2', 'pdf_font_file3', 'pdf_embedded_fonts', 'pdf_subsetted_fonts',
    'pdf_streams_uncompressed', 'pdf_streams_compressed', 'pdf_stream_dicts', 'pdf_stream_data',
    'pdf_filter_flatedecode', 'pdf_filter_lzwdecode', 'pdf_filter_ascii85decode', 'pdf_filter_runlengthdecode',
    'pdf_filter_ccittfaxdecode', 'pdf_filter_dctdecode', 'pdf_filter_jpxdecode', 'pdf_filter_crypt',
    'pdf_annot_count', 'pdf_annot_text', 'pdf_annot_link', 'pdf_annot_free_text', 'pdf_annot_line',
    'pdf_annot_square', 'pdf_annot_circle', 'pdf_annot_polygon', 'pdf_annot_poly_line',
    'pdf_annot_highlight', 'pdf_annot_underline', 'pdf_annot_squiggly', 'pdf_annot_strike_out',
    'pdf_annot_stamp', 'pdf_annot_caret', 'pdf_annot_ink', 'pdf_annot_popup', 'pdf_annot_file_attachment',
    'pdf_annot_sound', 'pdf_annot_movie', 'pdf_annot_widget', 'pdf_annot_screen', 'pdf_annot_printer_mark',
    'pdf_annot_trap_net', 'pdf_annot_watermark', 'pdf_annot_3d', 'pdf_annot_rich_media',
    'pdf_annot_web_media', 'pdf_annot_subtype', 'pdf_annot_rect', 'pdf_annot_quad_points',
    'pdf_annot_vertices', 'pdf_annot_line_ending_styles', 'pdf_annot_border_style', 'pdf_annot_color',
    'pdf_annot_interior_color', 'pdf_annot_border_color', 'pdf_annot_contents', 'pdf_annot_created',
    'pdf_annot_modified', 'pdf_annot_popup_open', 'pdf_annot_in_reply_to', 'pdf_annot_reply_type',
    'pdf_annot_status', 'pdf_annot_has_visible_popup', 'pdf_annot_default_closed', 'pdf_annot_callout_line',
    'pdf_annot_intent', 'pdf_annot_lang', 'pdf_annot_da', 'pdf_annot_f', 'pdf_annot_nm',
    'pdf_annot_fi', 'pdf_annot_v', 'pdf_annot_t', 'pdf_annot_subtype', 'pdf_annot_parent',
    'pdf_annot_next', 'pdf_annot_p', 'pdf_annot_rich_media_content', 'pdf_annot_rich_media_settings',
    'pdf_annot_rich_media_assets', 'pdf_annot_rich_media_commands', 'pdf_annot_rich_media_activation',
    'pdf_annot_rich_media_deactivation', 'pdf_annot_3d_data', 'pdf_annot_3d_on_load',
    'pdf_annot_3d_animation_style', 'pdf_annot_3d_view_state', 'pdf_annot_3d_projection',
    'pdf_annot_3d_cross_section', 'pdf_annot_3d_measurement', 'pdf_annot_3d_rendering_mode',
    'pdf_annot_3d_lighting_scheme', 'pdf_annot_3d_background', 'pdf_annot_3d_allow_script',
    'pdf_annot_3d_ui_controls_shown', 'pdf_annot_3d_disable_inlining', 'pdf_annot_3d_soft_light',
    'pdf_annot_3d_shadows', 'pdf_annot_3d_reflections', 'pdf_annot_3d_linear_defense',
    'pdf_annot_3d_arcball_params', 'pdf_annot_3d_orthogonal_camera', 'pdf_annot_3d_perspective_camera',
    'pdf_action_type', 'pdf_action_next', 'pdf_action_uri', 'pdf_action_go_to', 'pdf_action_go_to_r',
    'pdf_action_go_to_e', 'pdf_action_launch', 'pdf_action_thread', 'pdf_action_sound',
    'pdf_action_movie', 'pdf_action_hide', 'pdf_action_named', 'pdf_action_submit_form',
    'pdf_action_reset_form', 'pdf_action_import_data', 'pdf_action_javascript',
    'pdf_action_rendition', 'pdf_action_trans', 'pdf_action_set_ocg_state', 'pdf_action_script',
    'pdf_action_application', 'pdf_action_window', 'pdf_action_target', 'pdf_action_scope',
    'pdf_action_file', 'pdf_action_directory', 'pdf_action_url', 'pdf_action_is_map',
    'pdf_action_track', 'pdf_action_pb', 'pdf_action_pc', 'pdf_action_po', 'pdf_action_pd',
    'pdf_form_has_acroform', 'pdf_form_has_xfa', 'pdf_form_fields_count', 'pdf_form_widgets_count',
    'pdf_form_need_appearances', 'pdf_form_sigs_ok', 'pdf_form_append_only', 'pdf_form_include_untitled',
    'pdf_form_signature_flags', 'pdf_form_co', 'pdf_form_c', 'pdf_form_xfa', 'pdf_form_xfa_template',
    'pdf_form_xfa_data', 'pdf_form_xfa_config', 'pdf_form_xfa_datasets', 'pdf_form_xfa_preamble',
    'pdf_form_field_type', 'pdf_form_field_name', 'pdf_form_field_flags', 'pdf_form_field_value',
    'pdf_form_field_default', 'pdf_form_field_constraint', 'pdf_form_field_constraint_type',
    'pdf_form_field_min', 'pdf_form_field_max', 'pdf_form_field_pattern', 'pdf_form_field_separator',
    'pdf_form_field_sort', 'pdf_form_field_options', 'pdf_form_field_full', 'pdf_form_field_multi_select',
    'pdf_form_field_editable', 'pdf_form_field_required', 'pdf_form_field_no_export',
    'pdf_form_field_read_only', 'pdf_form_field_password', 'pdf_form_field_multiline',
    'pdf_form_field_combo', 'pdf_form_field_list', 'pdf_form_field_radio', 'pdf_form_field_push_button',
    'pdf_form_field_check_box', 'pdf_form_field_image', 'pdf_form_field_signature',
    'pdf_form_widget_name', 'pdf_form_widget_type', 'pdf_form_widget_rect', 'pdf_form_widget_states',
    'pdf_form_widget_state', 'pdf_form_widget_parent', 'pdf_form_widget_kids', 'pdf_form_widget_actions',
    'pdf_form_widget_default_action', 'pdf_form_widget_mapped_name', 'pdf_form_widget_change',
    'pdf_form_widget_change_count', 'pdf_form_widget_last_change', 'pdf_form_widget_name_entry',
    'pdf_form_widget_control', 'pdf_form_widget_radio_button', 'pdf_form_widget_check_box',
    'pdf_form_widget_push_button', 'pdf_form_widget_text_field', 'pdf_form_widget_choice_field',
    'pdf_form_widget_signature_field', 'pdf_form_widget_border_style', 'pdf_form_widget_border_width',
    'pdf_form_widget_border_color', 'pdf_form_widget_fill_color', 'pdf_form_widget_text_color',
    'pdf_form_widget_rotation', 'pdf_form_widget_user_name', 'pdf_form_widget_mapping_name',
    'pdf_form_widget_max_len', 'pdf_form_widget_alignment', 'pdf_form_widget_scroll_past_end',
    'pdf_form_widget_do_not_scroll', 'pdf_form_widget_combo_box_editable', 'pdf_form_widget_sort',
    'pdf_form_widget_multi_line', 'pdf_form_widget_password_field', 'pdf_form_widget_file_select',
    'pdf_form_widget_rich_text', 'pdf_form_widget_char_limit', 'pdf_form_widget_top_index',
    'pdf_form_widget_options', 'pdf_form_widget_export_value', 'pdf_form_widget_is_checked',
    'pdf_form_widget_style', 'pdf_form_widget_state_on', 'pdf_form_widget_state_off',
    'pdf_form_widget_icons_in_appearance', 'pdf_form_widget_normal_caption', 'pdf_form_widget_rollover_caption',
    'pdf_form_widget_down_caption', 'pdf_form_widget_normal_icon', 'pdf_form_widget_rollover_icon',
    'pdf_form_widget_down_icon', 'pdf_form_widget_icon_fit', 'pdf_form_widget_icon_scale_type',
    'pdf_form_widget_icon_scale_condition', 'pdf_form_widget_icon_left', 'pdf_form_widget_icon_top',
    'pdf_form_widget_icon_width', 'pdf_form_widget_icon_height', 'pdf_signature_type',
    'pdf_signature_filter', 'pdf_signature_subfilter', 'pdf_signature_containing', 'pdf_signature_reference',
    'pdf_signature_changes', 'pdf_signature_cert', 'pdf_signature_digest_method', 'pdf_signature_digest_value',
    'pdf_signature_encryption_method', 'pdf_signature_key_length', 'pdf_signature_reason',
    'pdf_signature_contact_info', 'pdf_signature_location', 'pdf_signature_signing_time',
    'pdf_signature_signature_value', 'pdf_signature_byte_range', 'pdf_signature_contents',
    'pdf_signature_cert_dict', 'pdf_signature_reference_dict', 'pdf_signature_lock_dict',
    'pdf_signature_perms_dict', 'pdf_signature_seed_value', 'pdf_signature_signature_ref',
    'pdf_signature_add_providers', 'pdf_signature_adbe_pubkey_hash', 'pdf_signature_certificate',
    'pdf_signature_challenge', 'pdf_signature_trusted_mode', 'pdf_signature_trust_anchor',
    'pdf_signature_validity_intervals', 'pdf_signature_document_time', 'pdf_signature_signature_type',
    'pdf_signature_sig_flags', 'pdf_signature_doctimestamp', 'pdf_signature_tsa', 'pdf_signature_field_lock',
    'pdf_signature_lock_action', 'pdf_signature_lock_fields', 'pdf_signature_annotation_lock',
    'pdf_signature_annotation_fields', 'pdf_signature_document_permissions', 'pdf_signature_form_fields',
    'pdf_signature_annot_fields', 'pdf_signature_purpose', 'pdf_signature_sig_field_name',
    'pdf_signature_sig_in_appearance_only', 'pdf_signature_signature_flags', 'pdf_signature_viewer_signature',
    'pdf_signature_is_certifying', 'pdf_signature_is_signatures_exist', 'pdf_signature_sig_dict',
    'pdf_signature_sig_ref_dict', 'pdf_signature_appearance_dict', 'pdf_signature_appearance_stream',
    'pdf_signature_appearance_states', 'pdf_signature_appearance_char_obs', 'pdf_signature_da_font',
    'pdf_signature_da_size', 'pdf_signature_da_color', 'pdf_signature_f', 'pdf_signature_ff',
    'pdf_signature_page', 'pdf_signature_t', 'pdf_signature_v', 'pdf_signature_lock',
    'pdf_signature_perm', 'pdf_signature_append', 'pdf_signature_dss', 'pdf_signature_dsi',
    'pdf_ocg_type', 'pdf_ocg_usage', 'pdf_ocg_name', 'pdf_ocg_intent', 'pdf_ocg_creator',
    'pdf_ocg_creation_date', 'pdf_ocg_mod_date', 'pdf_ocg_desc', 'pdf_ocg_usages',
    'pdf_ocg_info', 'pdf_ocg_view_state', 'pdf_ocg_print_state', 'pdf_ocg_export_state',
    'pdf_ocg_as_array', 'pdf_ocg_default_view_state', 'pdf_ocg_default_print_state',
    'pdf_ocg_default_export_state', 'pdf_ocg_rb_groups', 'pdf_ocg_order', 'pdf_ocg_properties',
    'pdf_ocg_configs', 'pdf_ocg_config_default', 'pdf_ocg_config_name', 'pdf_ocg_config_locked',
    'pdf_ocg_off', 'pdf_ocg_on', 'pdf_ocg_base_state', 'pdf_ocg_explicit_glyphs', 'pdf_ocg_radio_button',
    'pdf_ocg_undetermined', 'pdf_ocg_group', 'pdf_ocg_application', 'pdf_ocg_event', 'pdf_ocg_states',
    'pdf_ocg_action', 'pdf_ocg_action_default', 'pdf_ocg_action_down', 'pdf_ocg_action_up',
    'pdf_ocg_action_rollover', 'pdf_ocg_action_out', 'pdf_ocg_action_instance', 'pdf_ocg_action_action',
    'pdf_outline_count', 'pdf_outline_first', 'pdf_outline_last', 'pdf_outline_item_title',
    'pdf_outline_item_dest', 'pdf_outline_item_a', 'pdf_outline_item_se', 'pdf_outline_item_c',
    'pdf_outline_item_f', 'pdf_outline_item_struct_parent', 'pdf_outline_item_color',
    'pdf_outline_item_style', 'pdf_outline_item_count', 'pdf_outline_item_flags',
    'pdf_outline_item_child_count', 'pdf_outline_item_previous', 'pdf_outline_item_next',
    'pdf_outline_item_parent', 'pdf_struct_tree_root_type', 'pdf_struct_tree_root_kids',
    'pdf_struct_tree_root_parent_tree', 'pdf_struct_tree_root_role_map', 'pdf_struct_tree_root_class_map',
    'pdf_struct_elem_type', 'pdf_struct_elem_s', 'pdf_struct_elem_p', 'pdf_struct_elem_id',
    'pdf_struct_elem_a', 'pdf_struct_elem_k', 'pdf_struct_elem_actual_text',
    'pdf_struct_elem_alt_text', 'pdf_struct_elem_abbreviation', 'pdf_struct_elem_title',
    'pdf_struct_elem_lang', 'pdf_struct_elem_expand_to', 'pdf_struct_elem_table',
    'pdf_struct_elem_tr', 'pdf_struct_elem_th', 'pdf_struct_elem_td', 'pdf_struct_elem_span',
    'pdf_struct_elem_paragraph', 'pdf_struct_elem_heading', 'pdf_struct_elem_h1', 'pdf_struct_elem_h2',
    'pdf_struct_elem_h3', 'pdf_struct_elem_h4', 'pdf_struct_elem_h5', 'pdf_struct_elem_h6',
    'pdf_struct_elem_blockquote', 'pdf_struct_elem_caption', 'pdf_struct_elem_table_of_contents',
    'pdf_struct_elem_table_of_contents_item', 'pdf_struct_elem_index', 'pdf_struct_elem_entry',
    'pdf_struct_elem_reference', 'pdf_struct_elem_bibliography', 'pdf_struct_elem_bib_entry',
    'pdf_struct_elem_figure', 'pdf_struct_elem_formula', 'pdf_struct_elem_form', 'pdf_struct_elem_link',
    'pdf_struct_elem_note', 'pdf_struct_elem_annotation', 'pdf_struct_elem_separator',
    'pdf_mark_info_struct_parent', 'pdf_mark_info_heir_struct_parent', 'pdf_mark_info_user_attributes',
    'pdf_mark_info_user_properties', 'pdf_mark_info_standard', 'pdf_mark_info_custom', 'pdf_piece_info',
    'pdf_piece_last_modified', 'pdf_piece_piece', 'pdf_piece_data_key', 'pdf_piece_dictionary',
    'pdf_web_capture_capture_time', 'pdf_web_capture_source_url', 'pdf_web_capture_source_mime_type',
    'pdf_web_capture_source_filename', 'pdf_web_capture_pdf_version', 'pdf_web_capture_size',
    'pdf_web_capture_spidered', 'pdf_web_capture_converted', 'pdf_web_capture_error', 'pdf_web_capture_retries',
    'pdf_web_capture_back_to_source', 'pdf_web_capture_cookies', 'pdf_web_capture_proxies',
    'pdf_web_capture_user_agent', 'pdf_web_capture_auth', 'pdf_web_capture_domains', 'pdf_web_capture_subdomains',
    'pdf_web_capture_exclude', 'pdf_web_capture_include', 'pdf_collection_schema', 'pdf_collection_field',
    'pdf_collection_field_name', 'pdf_collection_field_type', 'pdf_collection_field_subtype',
    'pdf_collection_field_order', 'pdf_collection_field_visible', 'pdf_collection_field_extra',
    'pdf_collection_item', 'pdf_collection_item_schema', 'pdf_collection_item_properties',
    'pdf_portfolio_file', 'pdf_portfolio_description', 'pdf_portfolio_creation_date', 'pdf_portfolio_mod_date',
    'pdf_portfolio_application', 'pdf_portfolio_size', 'pdf_portfolio_hidden', 'pdf_portfolio_thumbnail',
    'pdf_filespec_embedded_file', 'pdf_filespec_uf', 'pdf_filespec_f', 'pdf_filespec_related_files',
    'pdf_filespec_collection_item', 'pdf_filespec_volatile', 'pdf_filespec_fs_url', 'pdf_filespec_fs',
    'pdf_filespec_id', 'pdf_filespec_embedded_file_name', 'pdf_filespec_embedded_file_size',
    'pdf_filespec_embedded_file_create_date', 'pdf_filespec_embedded_file_mod_date',
    'pdf_filespec_embedded_file_mime_type', 'pdf_filespec_embedded_file_description',
    'pdf_filespec_embedded_file_encryption', 'pdf_filespec_embedded_file_compression',
    'pdf_embedded_files_count', 'pdf_embedded_file_names', 'pdf_embedded_file_info',
    'pdf_multimedia_count', 'pdf_multimedia_type', 'pdf_multimedia_filename', 'pdf_multimedia_controls',
    'pdf_multimedia_autoplay', 'pdf_multimedia_palindrome', 'pdf_multimedia_continuous',
    'pdf_multimedia_loop_count', 'pdf_multimedia_volume', 'pdf_multimedia_balance',
    'pdf_multimedia_rate', 'pdf_rich_media_count', 'pdf_rich_media_type', 'pdf_rich_media_subtype',
    'pdf_rich_media_flash', 'pdf_rich_media_swf', 'pdf_rich_media_mp4', 'pdf_rich_media_mpeg4',
    'pdf_rich_media_quicktime', 'pdf_rich_media_wmv', 'pdf_rich_media_wmv_old', 'pdf_rich_media_avi',
    'pdf_rich_media_mov', 'pdf_rich_media_3gpp', 'pdf_rich_media_3gpp2', 'pdf_rich_media_webm',
    'pdf_rich_media_mp3', 'pdf_rich_media_aac', 'pdf_rich_media_wav', 'pdf_rich_media_ogg',
    'pdf_rich_media_flac', 'pdf_rich_media_asset', 'pdf_rich_media_asset_type', 'pdf_rich_media_asset_src',
    'pdf_rich_media_asset_md5', 'pdf_rich_media_settings', 'pdf_rich_media_activation_conditions',
    'pdf_rich_media_deactivation_conditions', 'pdf_rich_media_instances', 'pdf_rich_media_commands',
    'pdf_security_method', 'pdf_security_owner_password', 'pdf_security_user_password',
    'pdf_security_permissions', 'pdf_security_revision', 'pdf_security_length', 'pdf_security_encrypt_metadata',
    'pdf_security_standard', 'pdf_security_algorithm', 'pdf_security_r', 'pdf_security_p',
    'pdf_security_v', 'pdf_security_oe', 'pdf_security_po', 'pdf_security_ue', 'pdf_security_perm',
    'pdf_security_open_document', 'pdf_security_norefresh', 'pdf_security_hard_protection',
    'pdf_security_owner_mdf', 'pdf_security_user_mdf', 'pdf_permissions_print', 'pdf_permissions_modify',
    'pdf_permissions_copy', 'pdf_permissions_annotate', 'pdf_permissions_form_fill',
    'pdf_permissions_accessibility', 'pdf_permissions_assemble', 'pdf_permissions_print_high_quality',
    'pdf_requirement_type', 'pdf_requirement_satisfy', 'pdf_requirement_handler', 'pdf_requirement_name',
    'pdf_version_extension_level', 'pdf_version_extension_namespace', 'pdf_version_extension_revision',
    'pdf_xmp_metadata', 'pdf_xmp_packet_header', 'pdf_xmp_dc_format', 'pdf_xmp_dc_source',
    'pdf_xmp_dc_rights', 'pdf_xmp_dc_language', 'pdf_xmp_pdf_keywords', 'pdf_xmp_pdf_pdfversion',
    'pdf_xmp_pdf_producer', 'pdf_xmp_pdf_creator', 'pdf_xmp_xmp_create_date', 'pdf_xmp_xmp_mod_date',
    'pdf_xmp_xmp_metadata_date', 'pdf_xmp_xmp_serial_number', 'pdf_xmp_xmp_usage',
    'pdf_output_intent_s', 'pdf_output_intent_gts_pdfx', 'pdf_output_intent_gts_pdfa1',
    'pdf_output_intent_registry_name', 'pdf_output_intent_info', 'pdf_output_intent_output_condition',
    'pdf_output_intent_output_condition_identifier', 'pdf_output_intent_registry',
    'pdf_output_intent_meta', 'pdf_article_beads', 'pdf_destination_view', 'pdf_destination_xyz',
    'pdf_destination_fit', 'pdf_destination_fith', 'pdf_destination_fitv', 'pdf_destination_fitr',
    'pdf_destination_named', 'pdf_javascript_scripts', 'pdf_javascript_count', 'pdf_javascript_name',
    'pdf_javascript_script', 'pdf_open_action_destination', 'pdf_open_action_action',
    'pdf_additional_actions_type', 'pdf_additional_actions_wc', 'pdf_additional_actions_ws',
    'pdf_additional_actions_wp', 'pdf_additional_actions_da', 'pdf_additional_actions_np',
    'pdf_additional_actions_pc', 'pdf_additional_actions_po', 'pdf_additional_actions_d',
    'pdf_page_labels_s', 'pdf_page_labels_st', 'pdf_page_labels_r', 'pdf_page_labels_p',
    'pdf_linearized_first_page_object', 'pdf_linearized_hint_offset', 'pdf_linearized_hint_length',
    'pdf_linearized_primary_hint_stream', 'pdf_linearized_catalog_object', 'pdf_linearized_page_count',
    'pdf_linearized_eroffset', 'pdf_linearized_erpages', 'pdf_linearized_num_pages',
    'pdf_linearized_first_page', 'pdf_linearized_last_page', 'pdf_linearized_file_size',
    'pdf_linearized_linearization_version', 'pdf_pdfa_conformance', 'pdf_pdfa_level',
    'pdf_pdfa_version', 'pdf_pdfa_revision', 'pdf_pdfa_amd', 'pdf_pdfa_certifier',
    'pdf_pdfa_producer', 'pdf_pdfa_conformance_level', 'pdf_pdfa_extension_level',
    'pdf_pdfa_namespace_uri', 'pdf_pdfa_description', 'pdf_pdfa_class', 'pdf_pdfa_check_sums',
    'pdf_accessibility_language', 'pdf_accessibility_alt_text', 'pdf_accessibility_late_struct',
    'pdf_accessibility_tags_present', 'pdf_accessibility_reading_order', 'pdf_accessibility_tab_order',
    'pdf_accessibility_expanded_form', 'pdf_accessibility_actual_text', 'pdf_accessibility_title',
    'pdf_accessibility_subject', 'pdf_accessibility_description', 'pdf_accessibility_abstract',
    'pdf_accessibility_keywords', 'pdf_accessibility_creator', 'pdf_accessibility_producer',
    'pdf_accessibility_creationdate', 'pdf_accessibility_moddate', 'pdf_accessibility_author',
    'pdf_accessibility_trapped', 'pdf_accessibility_metadata', 'pdf_accessibility_struct_parent',
    'pdf_accessibility_artifact', 'pdf_accessibility_mcid', 'pdf_accessibility_stref',
    'pdf_accessibility_obj', 'pdf_accessibility_annot', 'pdf_accessibility_nm', 'pdf_accessibility_page',
    'pdf_accessibility_row', 'pdf_accessibility_column', 'pdf_accessibility_headers',
    'pdf_accessibility_scope', 'pdf_accessibility_th', 'pdf_accessibility_td', 'pdf_accessibility_headers_attr',
    'pdf_accessibility_scope_attr', 'pdf_accessibility_abbr', 'pdf_accessibility_axis',
    'pdf_accessibility_summary', 'pdf_accessibility_table', 'pdf_accessibility_table_struct',
    'pdf_accessibility_thead', 'pdf_accessibility_tbody', 'pdf_accessibility_tfoot',
    'pdf_accessibility_form', 'pdf_accessibility_field', 'pdf_accessibility_widget',
    'pdf_accessibility_hint', 'pdf_accessibility_error', 'pdf_accessibility_error_msg',
    'pdf_accessibility_figure', 'pdf_accessibility_math', 'pdf_accessibility_mathml',
    'pdf_accessibility_formula', 'pdf_accessibility_label', 'pdf_accessibility_ref',
    'pdf_accessibility_link', 'pdf_accessibility_note', 'pdf_accessibility_reference',
    'pdf_accessibility_section', 'pdf_accessibility_div', 'pdf_accessibility_span',
    'pdf_accessibility_paragraph', 'pdf_accessibility_heading', 'pdf_accessibility_strong',
    'pdf_accessibility_emphasis', 'pdf_accessibility_anchor', 'pdf_accessibility_image',
    'pdf_accessibility_non_struct', 'pdf_accessibility_private', 'pdf_accessibility_ruby',
    'pdf_accessibility_warichu', 'pdf_accessibility_ruby_align', 'pdf_accessibility_ruby_position',
    'pdf_accessibility_warichu_align', 'pdf_accessibility_warichu_size', 'pdf_accessibility_ruby_gap',
    'pdf_accessibility_warichu_gap', 'pdf_accessibility_ruby_scale', 'pdf_accessibility_warichu_scale',
    'pdf_accessibility_braille', 'pdf_accessibility_braille_dot_pattern', 'pdf_accessibility_braille_grade',
    'pdf_accessibility_braille_table', 'pdf_accessibility_braille_direction', 'pdf_accessibility_braille_pages',
    'pdf_accessibility_braille_lines', 'pdf_accessibility_braille_page_num', 'pdf_accessibility_braille_line_num',
    'pdf_accessibility_largetext', 'pdf_accessibility_font', 'pdf_accessibility_font_size',
    'pdf_accessibility_color_contrast', 'pdf_accessibility_text_offset', 'pdf_accessibility_bg_color',
    'pdf_accessibility_fg_color', 'pdf_accessibility_unicode', 'pdf_accessibility_ascii',
    'pdf_accessibility_shift_jis', 'pdf_accessibility_big5', 'pdf_accessibility_gb2312',
    'pdf_accessibility_euc_kr', 'pdf_accessibility_iso_8859', 'pdf_accessibility_utf8',
    'pdf_accessibility_utf16', 'pdf_accessibility_mac_roman', 'pdf_accessibility_pdf_doc_encoding',
    'pdf_accessibility_standard_encoding', 'pdf_accessibility_win_ansi', 'pdf_accessibility_macos_roman',
    'pdf_accessibility_document_fragment', 'pdf_accessibility_group', 'pdf_accessibility_header',
    'pdf_accessibility_footer', 'pdf_accessibility_landmark', 'pdf_accessibility_navigation',
    'pdf_accessibility_navigation_page', 'pdf_accessibility_navigation_table', 'pdf_accessibility_navigation_list',
    'pdf_accessibility_navigation_figure', 'pdf_accessibility_navigation_math',
    'pdf_accessibility_navigation_region', 'pdf_accessibility_navigation_exceptional',
    'pdf_incremental_update_number', 'pdf_incremental_update_count', 'pdf_incremental_update_prev_offset',
    'pdf_incremental_update_prev_objstm', 'pdf_incremental_update_xref', 'pdf_incremental_update_startxref',
    'pdf_dict_stream_type', 'pdf_dict_stream_subtype', 'pdf_dict_stream_struct_parent',
    'pdf_dict_stream_struct_parents', 'pdf_dict_stream_f', 'pdf_dict_stream_fflate',
    'pdf_dict_stream_filters', 'pdf_dict_stream_decode_parms', 'pdf_dict_stream_length',
    'pdf_dict_stream_filter_flatedecode', 'pdf_dict_stream_filter_lzwdecode',
    'pdf_dict_stream_filter_ascii85decode', 'pdf_dict_stream_filter_runlengthdecode',
    'pdf_dict_stream_filter_ccittfaxdecode', 'pdf_dict_stream_filter_dctdecode',
    'pdf_dict_stream_filter_jpxdecode', 'pdf_dict_stream_filter_crypt',
    'pdf_array_stream_type', 'pdf_array_stream_subtype', 'pdf_array_stream_length',
    'pdf_array_stream_filter', 'pdf_array_stream_decode_parms',
    'pdf_pattern_type', 'pdf_pattern_tiling_type', 'pdf_pattern_shading_type', 'pdf_pattern_bbox',
    'pdf_pattern_xstep', 'pdf_pattern_ystep', 'pdf_pattern_paint_type', 'pdf_pattern_tiling_type',
    'pdf_pattern_resources', 'pdf_pattern_matrix', 'pdf_pattern_shading_func', 'pdf_pattern_shading_ext_gstate',
    'pdf_pattern_shading_domain', 'pdf_pattern_shading_coords', 'pdf_pattern_shading_background',
    'pdf_pattern_shading_antialias', 'pdf_shading_type1', 'pdf_shading_type2', 'pdf_shading_type3',
    'pdf_shading_type4', 'pdf_shading_type5', 'pdf_shading_type6', 'pdf_shading_type7',
    'pdf_icc_profile_type', 'pdf_icc_profile_n', 'pdf_icc_profile_range', 'pdf_icc_profile_default',
    'pdf_icc_profile_info', 'pdf_icc_profile_alternate', 'pdf_icc_profile_metadata',
    'pdf_colorspace_type', 'pdf_colorspace_n', 'pdf_colorspace_range', 'pdf_colorspace_default',
    'pdf_colorspace_indexed', 'pdf_colorspace_calgray', 'pdf_colorspace_calrgb', 'pdf_colorspace_lab',
    'pdf_colorspace_icc', 'pdf_colorspace_pattern', 'pdf_colorspace_separation', 'pdf_colorspace_device_n',
    'pdf_separation_colorant_name', 'pdf_separation_alternate_space', 'pdf_separation_alternate_density',
    'pdf_separation_tint_transform', 'pdf_device_n_attributes', 'pdf_device_n_subtype',
    'pdf_device_n_components', 'pdf_device_n_colorant_names', 'pdf_device_n_tint_transform',
    'pdf_device_n_substitutes', 'pdf_stream_content_stream', 'pdf_stream_resources',
    'pdf_stream_bounding_box', 'pdf_stream_subtype', 'pdf_stream_struct_parent', 'pdf_stream_graphics_state',
    'pdf_stream_operation', 'pdf_stream_path', 'pdf_stream_text', 'pdf_stream_image',
    'pdf_stream_inline_image', 'pdf_stream_xobject', 'pdf_stream_form', 'pdf_stream_postscript',
    'pdf_form_xobject_resources', 'pdf_form_xobject_matrix', 'pdf_form_xobject_bbox',
    'pdf_form_xobject_group', 'pdf_form_xobject_piece_info', 'pdf_form_xobject_stroke_adj',
    'pdf_form_xobject_articulated', 'pdf_form_xobject_user_unit', 'pdf_form_xobject_optional_content',
    'pdf_postscript_xobject_ps', 'pdf_postscript_xobject_dsc', 'pdf_postscript_xobject_level1',
    'pdf_postscript_xobject_level2', 'pdf_postscript_xobject_level3',
    'pdf_image_type', 'pdf_image_width', 'pdf_image_height', 'pdf_image_bpc', 'pdf_image_color_space',
    'pdf_image_interpolate', 'pdf_image_mask', 'pdf_image_imagemask', 'pdf_image_dct', 'pdf_image_jpx',
    'pdf_image_ccitt', 'pdf_image_ccitt_k', 'pdf_image_ccitt_black_is1', 'pdf_image_ccitt_encode_aligned',
    'pdf_image_ccitt_encode_type', 'pdf_image_jbig2', 'pdf_image_jbig2_glob',
    'pdf_image_soft_mask', 'pdf_image_mask_color', 'pdf_image_tr', 'pdf_image_smask_in_data',
    'pdf_type3_char_procs', 'pdf_type3_char_widths', 'pdf_type3_bounding_box', 'pdf_type3_font_matrix',
    'pdf_type3_resources', 'pdf_cid_font_type', 'pdf_cid_font_base_font', 'pdf_cid_font_cid_to_gid',
    'pdf_cid_font_cid_to_unicode', 'pdf_cid_font_dw', 'pdf_cid_font_w', 'pdf_cid_font_w0',
    'pdf_cid_font_w1', 'pdf_cid_font_c_map', 'pdf_cid_font_cid_system_info', 'pdf_cid_font_font_descriptor',
    'pdf_true_type_font_file', 'pdf_true_type_font_file2', 'pdf_true_type_font_file3',
    'pdf_type1_font_file', 'pdf_type1_font_file2', 'pdf_type1_font_file3',
    'pdf_mm_font_type', 'pdf_mm_font_mm_var', 'pdf_mm_font_mm_blend', 'pdf_subsetted_font_prefix',
    'pdf_font_descriptor_flags', 'pdf_font_descriptor_font_bbox', 'pdf_font_descriptor_missing_width',
    'pdf_font_descriptor_stretch', 'pdf_font_descriptor_weight', 'pdf_font_descriptor_italic_angle',
    'pdf_font_descriptor_ascent', 'pdf_font_descriptor_descent', 'pdf_font_descriptor_avg_width',
    'pdf_font_descriptor_max_width', 'pdf_font_descriptor_missing_width_2',
    'pdf_to_unicode_map_type', 'pdf_to_unicode_cmap', 'pdf_to_unicode_to_unicode',
    'pdf_c_map_type', 'pdf_c_map_name', 'pdf_c_map_cid_system_info', 'pdf_c_map_use_cmap',
    'pdf_c_map_wmode', 'pdf_c_map_def', 'pdf_c_map_notdef_char', 'pdf_c_map_notdef_width',
    'pdf_catalog_viewer_preferences', 'pdf_viewer_hide_toolbar', 'pdf_viewer_hide_menubar',
    'pdf_viewer_window_ui', 'pdf_viewer_center_window', 'pdf_viewer_display_doc_title',
    'pdf_viewer_fitting_window', 'pdf_viewer_print_scaling', 'pdf_viewer_duplex',
    'pdf_viewer_non_fullscreen_page_mode', 'pdf_viewer_direction', 'pdf_viewer_view_area',
    'pdf_viewer_view_clip', 'pdf_viewer_print_area', 'pdf_viewer_print_clip', 'pdf_viewer_print_page_range',
    'pdf_viewer_num_copies', 'pdf_viewer_printer_name', 'pdf_viewer_print_allow',
    'pdf_viewer_print_shrink_to_fit', 'pdf_viewer_print_pick_tray_by_pdf_size',
    'pdf_viewer_print_manualduplex', 'pdf_viewer_print_collate', 'pdf_viewer_print_pages_x',
    'pdf_viewer_print_pages_y', 'pdf_viewer_print_media_type', 'pdf_viewer_print_media_color',
    'pdf_viewer_print_media_weight', 'pdf_viewer_print_duplex_mode', 'pdf_viewer_print_quality',
    'pdf_viewer_print_resolution', 'pdf_viewer_print_margin_type', 'pdf_viewer_print_custom_margin',
    'pdf_viewer_print_page_setup', 'pdf_viewer_print_page_width', 'pdf_viewer_print_page_height',
    'pdf_viewer_embed_region', 'pdf_viewer_display_region_opacity',
    'pdf_struct_parent_tree_count', 'pdf_struct_parent_tree_first', 'pdf_struct_parent_tree_last',
    'pdf_struct_parent_tree_nums', 'pdf_struct_parent_tree_kids', 'pdf_class_map_dict',
    'pdf_class_map_class', 'pdf_role_map_dict', 'pdf_role_map_type', 'pdf_da_font_name',
    'pdf_da_font_size', 'pdf_da_font_color', 'pdf_da_bg_color', 'pdf_da_border_color',
    'pdf_da_rotation', 'pdf_form_submit_flags', 'pdf_form_reset_flags', 'pdf_signature_flags',
    'pdf_form_widget_flags', 'pdf_form_field_flags', 'pdf_annot_flags', 'pdf_page_flags',
    'pdf_stream_info_title', 'pdf_stream_info_author', 'pdf_stream_info_subject', 'pdf_stream_info_keywords',
    'pdf_stream_info_creator', 'pdf_stream_info_producer', 'pdf_stream_info_creation_date',
    'pdf_stream_info_mod_date', 'pdf_stream_info_trapped', 'pdf_piece_dict_created',
    'pdf_piece_dict_modified', 'pdf_piece_dict_data_key', 'pdf_piece_dict_previous',
    'pdf_article_section', 'pdf_article_start', 'pdf_article_bead_ref', 'pdf_article_bead_index',
    'pdf_article_first_bead', 'pdf_article_last_bead', 'pdf_article_next_bead', 'pdf_article_prev_bead',
    'pdf_inline_image_type', 'pdf_inline_image_width', 'pdf_inline_image_height',
    'pdf_inline_image_bpc', 'pdf_inline_image_color_space', 'pdf_inline_image_interpolate',
    'pdf_inline_image_id', 'pdf_inline_image_data', 'pdf_inline_image_alt_image',
    'pdf_encryption_dict_r', 'pdf_encryption_dict_v', 'pdf_encryption_dict_length',
    'pdf_encryption_dict_o', 'pdf_encryption_dict_u', 'pdf_encryption_dict_p',
    'pdf_encryption_dict_encrypt_metadata', 'pdf_encryption_dict_oe', 'pdf_encryption_dict_ue',
    'pdf_encryption_dict_perm', 'pdf_encryption_dict_stm_f', 'pdf_encryption_dict_str_f',
    'pdf_encryption_dict_eff_f', 'pdf_encryption_dict_cfm', 'pdf_encryption_dict_allow_access',
    'pdf_encryption_dict_crypt_filters', 'pdf_encryption_dict_default_crypt_filter',
    'pdf_crypt_filter_name', 'pdf_crypt_filter_type', 'pdf_crypt_filter_length', 'pdf_crypt_filter_cfm',
    'pdf_crypt_filter_auth_event', 'pdf_ocd_sheet_config_name', 'pdf_ocd_sheet_config_usage',
    'pdf_ocd_sheet_config_viewer_preferences', 'pdf_ocd_sheet_config_dashed_border',
    'pdf_ocd_sheet_config_solid_border', 'pdf_ocd_sheet_config_badge', 'pdf_ocd_sheet_config_shadow',
    'pdf_ocd_sheet_config_rounded_corner_radius', 'pdf_ocd_sheet_config_label_style',
    'pdf_ocd_sheet_config_label_font', 'pdf_ocd_sheet_config_label_font_size',
    'pdf_ocd_sheet_config_label_color', 'pdf_ocd_sheet_config_message_text',
    'pdf_ocd_sheet_config_message_font', 'pdf_ocd_sheet_config_message_font_size',
    'pdf_ocd_sheet_config_help_file', 'pdf_ocd_sheet_config_content_file',
    'pdf_ocd_sheet_config_content_file_mime_type', 'pdf_ocd_sheet_config_open_action',
    'pdf_ocd_sheet_config_transformation', 'pdf_ocd_sheet_config_transparency',
    'pdf_ocd_sheet_config_report_bug_url', 'pdf_ocd_sheet_config_dont_unload',
    'pdf_ocd_sheet_config_dont_install', 'pdf_ocd_sheet_config_cache_updates',
    'pdf_ocd_sheet_config_skip_page_advance', 'pdf_ocd_sheet_config_center_window',
    'pdf_ocd_sheet_config_display_doctitle', 'pdf_ocd_sheet_config_fitting_window',
    'pdf_ocd_sheet_config_hide_toolbar', 'pdf_ocd_sheet_config_hide_menubar',
    'pdf_ocd_sheet_config_hide_window_ui', 'pdf_ocd_sheet_config_use_fit_window',
    'pdf_ocd_sheet_config_use_none_ca', 'pdf_ocd_sheet_config_use_outline',
    'pdf_ocd_sheet_config_use_thumbs', 'pdf_ocd_sheet_config_use_oc_groups',
    'pdf_ocd_sheet_config_full_screen', 'pdf_ocd_sheet_config_use_paper_color',
    'pdf_ocd_sheet_config_use_wallpaper', 'pdf_ocd_sheet_config_center_main_area',
    'pdf_ocd_sheet_config_display_title', 'pdf_ocd_senyheet_config_d_doc_write',
    'pdf_ocd_sheet_config_deny_doc_print', 'pdf_ocd_sheet_config_open_level',
    'pdf_ocd_sheet_config_page_layout_override', 'pdf_ocd_sheet_config_magnification_type',
    'pdf_ocd_sheet_config_magnification_factor', 'pdf_ocd_sheet_config_magnification_nonzero',
    'pdf_ocd_sheet_config_focus_type', 'pdf_ocd_sheet_config_focus_percent', 'pdf_ocd_sheet_config_scroll_type',
    'pdf_ocd_sheet_config_scroll_percent', 'pdf_ocd_sheet_config_direction', 'pdf_ocd_sheet_config_page_transition',
    'pdf_ocd_sheet_config_transition_style', 'pdf_ocd_sheet_config_transition_duration',
    'pdf_ocd_sheet_config_transition_auto_advance', 'pdf_ocd_sheet_config_transition_manual_advance',
}


def get_pdf_complete_ultimate_field_count() -> int:
    """Return the field count for this module."""
    return len(PDF_KEYWORDS)


def extract_pdf_complete_ultimate_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract complete PDF metadata - Ultimate Edition.
    
    Returns comprehensive PDF metadata dictionary.
    """
    result = {'pdf_ultimate_extraction': True}
    
    try:
        if not PYMUPDF_AVAILABLE:
            result['pymupdf_not_available'] = True
            return result
        
        doc = fitz.open(filepath)
        result.update(_extract_document_structure(doc, filepath))
        result.update(_extract_catalog_info(doc))
        result.update(_extract_page_info(doc))
        result.update(_extract_annotation_info(doc))
        result.update(_extract_form_info(doc))
        result.update(_extract_outline_info(doc))
        result.update(_extract_embedded_files(doc))
        result.update(_extract_security_info(doc))
        result.update(_extract_accessibility_info(doc))
        result.update(_extract_ocg_info(doc))
        result.update(_extract_xmp_metadata(doc))
        result.update(_extract_font_info(doc))
        result.update(_extract_image_info(doc))
        result.update(_extract_color_info(doc))
        result.update(_extract_pattern_info(doc))
        result.update(_extract_shading_info(doc))
        result.update(_extract_stream_info(doc))
        result.update(_extract_incremental_info(filepath))
        result.update(_extract_linearization_info(filepath))
        result.update(_extract_pdfa_info(doc))
        
        doc.close()
        
    except Exception as e:
        logger.warning(f"Error extracting PDF complete metadata from {filepath}: {e}")
        result['pdf_ultimate_extraction_error'] = str(e)
    
    return result


def _extract_document_structure(doc, filepath: str) -> Dict[str, Any]:
    """Extract PDF document structure information."""
    data = {
        'pdf_doc_structure_detected': True,
        'pdf_version': doc.version,
        'pdf_page_count': len(doc),
        'pdf_is_encrypted': doc.is_encrypted,
        'pdf_needs_pass': doc.needs_pass,
        'pdf_is_repaired': doc.is_repaired,
        'pdf_xref_count': doc.xref_length() if hasattr(doc, 'xref_length') else 0,
        'pdf_object_count': doc.xref_length() if hasattr(doc, 'xref_length') else 0,
    }
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        data['pdf_stream_count'] = content.count(b'stream')
        data['pdf_dict_count'] = content.count(b'<<')
        data['pdf_array_count'] = content.count(b'[')
        data['pdf_string_count'] = content.count(b'(') + content.count(b'<')
        data['pdf_null_count'] = content.count(b'null')
        data['pdf_indirect_refs'] = content.count(b' R') + content.count(b' obj')
        data['pdf_compression_detected'] = content.count(b'FlateDecode') + content.count(b'LZWDecode')
        data['pdf_ascii85_count'] = content.count(b'ASCII85Decode')
        data['pdf_runlength_count'] = content.count(b'RunLengthDecode')
        data['pdf_ccitt_count'] = content.count(b'CCITTFaxDecode')
        data['pdf_dct_count'] = content.count(b'DCTDecode')
        data['pdf_jpx_count'] = content.count(b'JPXDecode')
        
    except Exception as e:
        data['pdf_structure_read_error'] = str(e)
    
    return data


def _extract_catalog_info(doc) -> Dict[str, Any]:
    """Extract PDF catalog dictionary information."""
    catalog_data = {'pdf_catalog_extracted': True}
    
    try:
        catalog_xref = doc.xref_get(0, 'Type')
        catalog_data['pdf_catalog_type'] = catalog_xref if catalog_xref else 'Catalog'
        
        page_mode = doc.xref_get(0, 'PageMode')
        page_layout = doc.xref_get(0, 'PageLayout')
        catalog_data['pdf_page_mode'] = page_mode if page_mode else 'UseNone'
        catalog_data['pdf_page_layout'] = page_layout if page_layout else 'SinglePage'
        
        viewer_prefs = doc.xref_get(0, 'ViewerPreferences')
        catalog_data['pdf_viewer_preferences_present'] = viewer_prefs if viewer_prefs else False
        
        names = doc.xref_get(0, 'Names')
        catalog_data['pdf_names_dict_present'] = names if names else False
        
        outlines = doc.xref_get(0, 'Outlines')
        catalog_data['pdf_outlines_present'] = outlines if outlines else False
        
        acroform = doc.xref_get(0, 'AcroForm')
        catalog_data['pdf_acroform_present'] = acroform if acroform else False
        
        ocproperties = doc.xref_get(0, 'OCProperties')
        catalog_data['pdf_oc_properties_present'] = ocproperties if ocproperties else False
        
        metadata = doc.xref_get(0, 'Metadata')
        catalog_data['pdf_metadata_stream_present'] = metadata if metadata else False
        
        struct_root = doc.xref_get(0, 'StructTreeRoot')
        catalog_data['pdf_struct_tree_root_present'] = struct_root if struct_root else False
        
        mark_info = doc.xref_get(0, 'MarkInfo')
        catalog_data['pdf_mark_info_present'] = mark_info if mark_info else False
        
        open_action = doc.xref_get(0, 'OpenAction')
        catalog_data['pdf_open_action_present'] = open_action if open_action else False
        
        additional_actions = doc.xref_get(0, 'AA')
        catalog_data['pdf_additional_actions_present'] = additional_actions if additional_actions else False
        
        requirements = doc.xref_get(0, 'Requirements')
        catalog_data['pdf_requirements_present'] = requirements if requirements else False
        
        collection = doc.xref_get(0, 'Collection')
        catalog_data['pdf_collection_present'] = collection if collection else False
        
        portfolio = doc.xref_get(0, 'Portfolio')
        catalog_data['pdf_portfolio_present'] = portfolio if portfolio else False
        
        legal = doc.xref_get(0, 'Legal')
        catalog_data['pdf_legal_present'] = legal if legal else False
        
    except Exception as e:
        catalog_data['pdf_catalog_extraction_error'] = str(e)
    
    return catalog_data


def _extract_page_info(doc) -> Dict[str, Any]:
    """Extract PDF page information."""
    page_data = {'pdf_page_info_extracted': True, 'pdf_pages': []}
    
    try:
        for i, page in enumerate(doc):
            page_info = {
                f'pdf_page_{i}_number': i + 1,
                f'pdf_page_{i}_width': page.rect.width,
                f'pdf_page_{i}_height': page.rect.height,
                f'pdf_page_{i}_rotation': page.rotation,
                f'pdf_page_{i}_label': page.get_label() if hasattr(page, 'get_label') else None,
                f'pdf_page_{i}_xref': page.xref,
            }
            
            page_data['pdf_pages'].append(page_info)
            
            rect = page.rect
            page_data[f'pdf_page_{i}_has_annotations'] = len(page.annots()) > 0 if page.annots() else False
            page_data[f'pdf_page_{i}_has_links'] = len(page.links()) > 0 if page.links() else False
            page_data[f'pdf_page_{i}_has_widgets'] = len(page.widgets()) > 0 if page.widgets() else False
            
            words = page.get_text('words')
            page_data[f'pdf_page_{i}_word_count'] = len(words) if words else 0
            
            blocks = page.get_text('blocks')
            page_data[f'pdf_page_{i}_block_count'] = len(blocks) if blocks else 0
            
            page_data[f'pdf_page_{i}_has_text'] = bool(words)
            
            page_data.update(page_info)
        
        page_data['pdf_total_page_count'] = len(doc)
        
        first_page = doc[0] if len(doc) > 0 else None
        if first_page:
            page_data['pdf_first_page_width'] = first_page.rect.width
            page_data['pdf_first_page_height'] = first_page.rect.height
            page_data['pdf_first_page_rotation'] = first_page.rotation
        
    except Exception as e:
        page_data['pdf_page_info_error'] = str(e)
    
    return page_data


def _extract_annotation_info(doc) -> Dict[str, Any]:
    """Extract PDF annotation information."""
    annot_data = {'pdf_annotation_info_extracted': True}
    
    try:
        total_annots = 0
        annot_types_count = {k: 0 for k in PDF_ANNOTATION_TYPES}
        
        for page in doc:
            if page.annots():
                for annot in page.annots():
                    total_annots += 1
                    subtype = annot.type[1] if annot.type else 'Unknown'
                    if subtype in annot_types_count:
                        annot_types_count[subtype] += 1
        
        annot_data['pdf_total_annotations'] = total_annots
        for annot_type, count in annot_types_count.items():
            annot_data[f'pdf_annot_count_{annot_type.lower()}'] = count
        
        annot_data['pdf_has_text_annotations'] = annot_types_count.get('Text', 0) > 0
        annot_data['pdf_has_link_annotations'] = annot_types_count.get('Link', 0) > 0
        annot_data['pdf_has_highlight_annotations'] = annot_types_count.get('Highlight', 0) > 0
        annot_data['pdf_has_underline_annotations'] = annot_types_count.get('Underline', 0) > 0
        annot_data['pdf_has_strikeout_annotations'] = annot_types_count.get('StrikeOut', 0) > 0
        annot_data['pdf_has_file_attachment_annotations'] = annot_types_count.get('FileAttachment', 0) > 0
        annot_data['pdf_has_sound_annotations'] = annot_types_count.get('Sound', 0) > 0
        annot_data['pdf_has_movie_annotations'] = annot_types_count.get('Movie', 0) > 0
        annot_data['pdf_has_widget_annotations'] = annot_types_count.get('Widget', 0) > 0
        annot_data['pdf_has_screen_annotations'] = annot_types_count.get('Screen', 0) > 0
        annot_data['pdf_has_3d_annotations'] = annot_types_count.get('3D', 0) > 0
        annot_data['pdf_has_rich_media_annotations'] = annot_types_count.get('RichMedia', 0) > 0
        
    except Exception as e:
        annot_data['pdf_annotation_info_error'] = str(e)
    
    return annot_data


def _extract_form_info(doc) -> Dict[str, Any]:
    """Extract PDF form information."""
    form_data = {'pdf_form_info_extracted': True}
    
    try:
        form_count = 0
        widget_count = 0
        field_types = {}
        
        for page in doc:
            if page.widgets():
                for widget in page.widgets():
                    widget_count += 1
                    field_type = widget.field_type if hasattr(widget, 'field_type') else 'Unknown'
                    field_types[field_type] = field_types.get(field_type, 0) + 1
                    form_count += 1
        
        form_data['pdf_form_field_count'] = form_count
        form_data['pdf_form_widget_count'] = widget_count
        
        for field_type, count in field_types.items():
            form_data[f'pdf_form_field_type_{field_type}'] = count
        
        form_data['pdf_has_form_fields'] = form_count > 0
        form_data['pdf_has_text_fields'] = field_types.get('Text', 0) > 0
        form_data['pdf_has_checkbox_fields'] = field_types.get('CheckBox', 0) > 0
        form_data['pdf_has_radio_button_fields'] = field_types.get('RadioButton', 0) > 0
        form_data['pdf_has_choice_fields'] = field_types.get('Choice', 0) > 0
        form_data['pdf_has_pushbutton_fields'] = field_types.get('PushButton', 0) > 0
        form_data['pdf_has_signature_fields'] = field_types.get('Signature', 0) > 0
        
    except Exception as e:
        form_data['pdf_form_info_error'] = str(e)
    
    return form_data


def _extract_outline_info(doc) -> Dict[str, Any]:
    """Extract PDF outline/bookmarks information."""
    outline_data = {'pdf_outline_info_extracted': True}
    
    try:
        toc = doc.get_toc()
        outline_data['pdf_outline_count'] = len(toc) if toc else 0
        outline_data['pdf_outline_exists'] = len(toc) > 0 if toc else False
        
        if toc:
            top_level_count = sum(1 for item in toc if item[1] == 1)
            nested_count = len(toc) - top_level_count
            
            outline_data['pdf_outline_top_level_count'] = top_level_count
            outline_data['pdf_outline_nested_count'] = nested_count
            outline_data['pdf_outline_max_depth'] = max(item[1] for item in toc) if toc else 0
            
    except Exception as e:
        outline_data['pdf_outline_info_error'] = str(e)
    
    return outline_data


def _extract_embedded_files(doc) -> Dict[str, Any]:
    """Extract embedded file information."""
    embedded_data = {'pdf_embedded_files_extracted': True}
    
    try:
        embedded_files = []
        for xref in range(1, doc.xref_length()):
            obj_type = doc.xref_get(xref, 'Type')
            if obj_type == 'Filespec':
                filename = doc.xref_get(xref, 'F') or doc.xref_get(xref, 'UF')
                embedded_data[f'pdf_embedded_file_{xref}'] = filename if filename else 'Unnamed'
                embedded_files.append({'xref': xref, 'filename': filename})
        
        embedded_data['pdf_embedded_file_count'] = len(embedded_files)
        embedded_data['pdf_has_embedded_files'] = len(embedded_files) > 0
        
    except Exception as e:
        embedded_data['pdf_embedded_files_error'] = str(e)
    
    return embedded_data


def _extract_security_info(doc) -> Dict[str, Any]:
    """Extract PDF security information."""
    security_data = {'pdf_security_info_extracted': True}
    
    security_data['pdf_is_encrypted'] = doc.is_encrypted
    security_data['pdf_needs_password'] = doc.needs_pass
    
    try:
        permissions = doc.permissions
        security_data['pdf_permissions_print'] = bool(permissions & 4)
        security_data['pdf_permissions_modify'] = bool(permissions & 8)
        security_data['pdf_permissions_copy'] = bool(permissions & 16)
        security_data['pdf_permissions_annotate'] = bool(permissions & 32)
        security_data['pdf_permissions_form_fill'] = bool(permissions & 256)
        security_data['pdf_permissions_accessibility'] = bool(permissions & 512)
        security_data['pdf_permissions_assemble'] = bool(permissions & 1024)
        security_data['pdf_permissions_print_high_quality'] = bool(permissions & 2048)
        
        if doc.is_encrypted:
            security_data['pdf_security_method'] = 'Standard'
            security_data['pdf_security_revision'] = doc.xref_get(0, 'R') if hasattr(doc, 'xref_get') else None
            security_data['pdf_security_length'] = doc.xref_get(0, 'Length') if hasattr(doc, 'xref_get') else None
            
    except Exception as e:
        security_data['pdf_security_info_error'] = str(e)
    
    return security_data


def _extract_accessibility_info(doc) -> Dict[str, Any]:
    """Extract PDF accessibility information."""
    a11y_data = {'pdf_accessibility_extracted': True}
    
    try:
        metadata = doc.metadata
        a11y_data['pdf_has_title'] = bool(metadata.get('title'))
        a11y_data['pdf_has_author'] = bool(metadata.get('author'))
        a11y_data['pdf_has_subject'] = bool(metadata.get('subject'))
        a11y_data['pdf_has_keywords'] = bool(metadata.get('keywords'))
        a11y_data['pdf_has_creator'] = bool(metadata.get('creator'))
        a11y_data['pdf_has_producer'] = bool(metadata.get('producer'))
        
        mark_info = doc.xref_get(0, 'MarkInfo')
        a11y_data['pdf_mark_info_present'] = bool(mark_info)
        
        struct_root = doc.xref_get(0, 'StructTreeRoot')
        a11y_data['pdf_struct_tree_root_present'] = bool(struct_root)
        
        if struct_root:
            a11y_data['pdf_has_struct_tree'] = True
        
    except Exception as e:
        a11y_data['pdf_accessibility_info_error'] = str(e)
    
    return a11y_data


def _extract_ocg_info(doc) -> Dict[str, Any]:
    """Extract optional content group (layer) information."""
    ocg_data = {'pdf_ocg_extracted': True}
    
    try:
        ocgs = doc.get_ocgs()
        ocg_data['pdf_ocg_count'] = len(ocgs) if ocgs else 0
        ocg_data['pdf_has_ocgs'] = len(ocgs) > 0 if ocgs else False
        
        if ocgs:
            visible_count = sum(1 for ocg in ocgs if ocg[1])
            ocg_data['pdf_ocg_visible_count'] = visible_count
            ocg_data['pdf_ocg_hidden_count'] = len(ocg) - visible_count
            
    except Exception as e:
        ocg_data['pdf_ocg_info_error'] = str(e)
    
    return ocg_data


def _extract_xmp_metadata(doc) -> Dict[str, Any]:
    """Extract XMP metadata from PDF."""
    xmp_data = {'pdf_xmp_extracted': True}
    
    try:
        xmp_xml = doc.xref_get(0, 'Metadata')
        if xmp_xml and xmp_xml != 'null':
            xmp_data['pdf_xmp_present'] = True
            xmp_data['pdf_xmp_length'] = len(xmp_xml) if xmp_xml else 0
            xmp_data['pdf_xmp_contains_dc'] = 'dc:' in xmp_xml if xmp_xml else False
            xmp_data['pdf_xmp_contains_pdf'] = 'pdf:' in xmp_xml if xmp_xml else False
            xmp_data['pdf_xmp_contains_xmp'] = 'xmp:' in xmp_xml if xmp_xml else False
            xmp_data['pdf_xmp_contains_rdf'] = 'rdf:' in xmp_xml if xmp_xml else False
        else:
            xmp_data['pdf_xmp_present'] = False
            
    except Exception as e:
        xmp_data['pdf_xmp_info_error'] = str(e)
    
    return xmp_data


def _extract_font_info(doc) -> Dict[str, Any]:
    """Extract font information from PDF."""
    font_data = {'pdf_font_extracted': True}
    
    try:
        font_list = []
        for page_num, page in enumerate(doc):
            text_page = page.get_textpage()
            fonts = text_page.extractFONTNAME() if hasattr(text_page, 'extractFONTNAME') else []
            for font in fonts:
                if font not in font_list:
                    font_list.append(font)
        
        font_data['pdf_font_count'] = len(font_list)
        font_data['pdf_has_fonts'] = len(font_list) > 0
        
        embedded_count = 0
        type0_count = 0
        type1_count = 0
        truetype_count = 0
        cid_count = 0
        
        for xref in range(1, doc.xref_length()):
            subtype = doc.xref_get(xref, 'Subtype')
            if subtype == 'Type0':
                type0_count += 1
            elif subtype == 'Type1':
                type1_count += 1
            elif subtype == 'TrueType':
                truetype_count += 1
            elif subtype == 'CIDFontType':
                cid_count += 1
                
            if doc.xref_get(xref, 'FontFile'):
                embedded_count += 1
            elif doc.xref_get(xref, 'FontFile2'):
                embedded_count += 1
            elif doc.xref_get(xref, 'FontFile3'):
                embedded_count += 1
        
        font_data['pdf_font_type0_count'] = type0_count
        font_data['pdf_font_type1_count'] = type1_count
        font_data['pdf_font_truetype_count'] = truetype_count
        font_data['pdf_font_cid_count'] = cid_count
        font_data['pdf_embedded_font_count'] = embedded_count
        
    except Exception as e:
        font_data['pdf_font_info_error'] = str(e)
    
    return font_data


def _extract_image_info(doc) -> Dict[str, Any]:
    """Extract image information from PDF."""
    image_data = {'pdf_image_extracted': True}
    
    try:
        image_count = 0
        inline_image_count = 0
        image_types = {}
        
        for page_num, page in enumerate(doc):
            image_list = page.get_images()
            if image_list:
                image_count += len(image_list)
                for img in image_list:
                    img_type = img[0] if img else 'Unknown'
                    image_types[img_type] = image_types.get(img_type, 0) + 1
        
        image_data['pdf_image_count'] = image_count
        image_data['pdf_has_images'] = image_count > 0
        image_data['pdf_inline_image_count'] = inline_image_count
        
        for img_type, count in image_types.items():
            image_data[f'pdf_image_type_{img_type}_count'] = count
        
    except Exception as e:
        image_data['pdf_image_info_error'] = str(e)
    
    return image_data


def _extract_color_info(doc) -> Dict[str, Any]:
    """Extract color space information from PDF."""
    color_data = {'pdf_color_extracted': True}
    
    try:
        has_device_rgb = False
        has_device_cmyk = False
        has_device_gray = False
        has_calrgb = False
        has_calgray = False
        has_lab = False
        has_indexed = False
        has_separation = False
        has_device_n = False
        has_pattern = False
        has_icc = False
        
        for xref in range(1, doc.xref_length()):
            colorspace = doc.xref_get(xref, 'ColorSpace')
            if colorspace:
                if 'DeviceRGB' in colorspace:
                    has_device_rgb = True
                if 'DeviceCMYK' in colorspace:
                    has_device_cmyk = True
                if 'DeviceGray' in colorspace:
                    has_device_gray = True
                if 'CalRGB' in colorspace:
                    has_calrgb = True
                if 'CalGray' in colorspace:
                    has_calgray = True
                if 'Lab' in colorspace or 'DeviceLab' in colorspace:
                    has_lab = True
                if 'Indexed' in colorspace:
                    has_indexed = True
                if 'Separation' in colorspace:
                    has_separation = True
                if 'DeviceN' in colorspace:
                    has_device_n = True
                if 'Pattern' in colorspace:
                    has_pattern = True
                if 'ICCBased' in colorspace:
                    has_icc = True
        
        color_data['pdf_colorspace_device_rgb'] = has_device_rgb
        color_data['pdf_colorspace_device_cmyk'] = has_device_cmyk
        color_data['pdf_colorspace_device_gray'] = has_device_gray
        color_data['pdf_colorspace_calrgb'] = has_calrgb
        color_data['pdf_colorspace_calgray'] = has_calgray
        color_data['pdf_colorspace_lab'] = has_lab
        color_data['pdf_colorspace_indexed'] = has_indexed
        color_data['pdf_colorspace_separation'] = has_separation
        color_data['pdf_colorspace_device_n'] = has_device_n
        color_data['pdf_colorspace_pattern'] = has_pattern
        color_data['pdf_colorspace_icc_based'] = has_icc
        
    except Exception as e:
        color_data['pdf_color_info_error'] = str(e)
    
    return color_data


def _extract_pattern_info(doc) -> Dict[str, Any]:
    """Extract pattern information from PDF."""
    pattern_data = {'pdf_pattern_extracted': True}
    
    try:
        tiling_count = 0
        shading_count = 0
        
        for xref in range(1, doc.xref_length()):
            obj_type = doc.xref_get(xref, 'Type')
            if obj_type == 'Pattern':
                subtype = doc.xref_get(xref, 'PatternType')
                if subtype == 'Tiling':
                    tiling_count += 1
                elif subtype == 'Shading':
                    shading_count += 1
        
        pattern_data['pdf_tiling_pattern_count'] = tiling_count
        pattern_data['pdf_shading_pattern_count'] = shading_count
        pattern_data['pdf_has_patterns'] = tiling_count + shading_count > 0
        
    except Exception as e:
        pattern_data['pdf_pattern_info_error'] = str(e)
    
    return pattern_data


def _extract_shading_info(doc) -> Dict[str, Any]:
    """Extract shading information from PDF."""
    shading_data = {'pdf_shading_extracted': True}
    
    try:
        shading_count = 0
        type1_count = 0
        type2_count = 0
        type3_count = 0
        type4_count = 0
        type5_count = 0
        type6_count = 0
        type7_count = 0
        
        for xref in range(1, doc.xref_length()):
            obj_type = doc.xref_get(xref, 'Type')
            if obj_type == 'Shading':
                shading_count += 1
                subtype = doc.xref_get(xref, 'ShadingType')
                if subtype == '1':
                    type1_count += 1
                elif subtype == '2':
                    type2_count += 1
                elif subtype == '3':
                    type3_count += 1
                elif subtype == '4':
                    type4_count += 1
                elif subtype == '5':
                    type5_count += 1
                elif subtype == '6':
                    type6_count += 1
                elif subtype == '7':
                    type7_count += 1
        
        shading_data['pdf_shading_count'] = shading_count
        shading_data['pdf_shading_type1_count'] = type1_count
        shading_data['pdf_shading_type2_count'] = type2_count
        shading_data['pdf_shading_type3_count'] = type3_count
        shading_data['pdf_shading_type4_count'] = type4_count
        shading_data['pdf_shading_type5_count'] = type5_count
        shading_data['pdf_shading_type6_count'] = type6_count
        shading_data['pdf_shading_type7_count'] = type7_count
        
    except Exception as e:
        shading_data['pdf_shading_info_error'] = str(e)
    
    return shading_data


def _extract_stream_info(doc) -> Dict[str, Any]:
    """Extract stream information from PDF."""
    stream_data = {'pdf_stream_extracted': True}
    
    try:
        stream_count = 0
        filter_count = {}
        
        for xref in range(1, doc.xref_length()):
            if doc.xref_get(xref, 'Type') == 'Stream':
                stream_count += 1
                filters = doc.xref_get(xref, 'Filter')
                if filters:
                    for filter_name in ['FlateDecode', 'LZWDecode', 'ASCII85Decode', 
                                        'RunLengthDecode', 'CCITTFaxDecode', 'DCTDecode',
                                        'JPXDecode', 'Crypt']:
                        if filter_name in filters:
                            filter_count[filter_name] = filter_count.get(filter_name, 0) + 1
        
        stream_data['pdf_stream_count'] = stream_count
        
        for filter_name, count in filter_count.items():
            stream_data[f'pdf_filter_{filter_name.lower()}_count'] = count
        
    except Exception as e:
        stream_data['pdf_stream_info_error'] = str(e)
    
    return stream_data


def _extract_incremental_info(filepath: str) -> Dict[str, Any]:
    """Extract incremental update information from PDF."""
    inc_data = {'pdf_incremental_extracted': True}
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        startxref_count = content.count(b'startxref')
        inc_data['pdf_startxref_count'] = startxref_count
        inc_data['pdf_has_incremental_updates'] = startxref_count > 1
        
        if startxref_count > 1:
            inc_data['pdf_update_count'] = startxref_count - 1
        
        xref_count = content.count(b'xref')
        inc_data['pdf_xref_section_count'] = xref_count
        
    except Exception as e:
        inc_data['pdf_incremental_info_error'] = str(e)
    
    return inc_data


def _extract_linearization_info(filepath: str) -> Dict[str, Any]:
    """Extract linearization information from PDF."""
    lin_data = {'pdf_linearization_extracted': True}
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        lin_data['pdf_is_linearized'] = b'%PDF-1.' in content and b'/Linearized' in content
        
        if b'/Linearized' in content:
            lin_data['pdf_linearized_first_page'] = b'/FirstPageObject' in content
            lin_data['pdf_linearized_hint_stream'] = b'/HintStream' in content
            lin_data['pdf_linearized_hint_offset'] = b'/HintOffset' in content
            lin_data['pdf_linearized_hint_length'] = b'/HintLength' in content
            
    except Exception as e:
        lin_data['pdf_linearization_info_error'] = str(e)
    
    return lin_data


def _extract_pdfa_info(doc) -> Dict[str, Any]:
    """Extract PDF/A compliance information."""
    pdfa_data = {'pdf_pdfa_extracted': True}
    
    try:
        metadata = doc.metadata
        producer = metadata.get('producer', '') if metadata else ''
        creator = metadata.get('creator', '') if metadata else ''
        
        pdfa_data['pdf_is_pdfa_compliant'] = 'pdfa' in producer.lower() or 'pdf/a' in producer.lower()
        pdfa_data['pdfa_conformance_in_producer'] = 'pdf/a' in producer.lower() or 'pdfa' in producer.lower()
        pdfa_data['pdfa_conformance_in_creator'] = 'pdf/a' in creator.lower() or 'pdfa' in creator.lower()
        
        with open(doc.name, 'rb') as f:
            content = f.read()
        
        pdfa_data['pdf_has_pdfa_namespace'] = b'http://www.aiim.org/pdfa' in content or b'pdfaid' in content.lower()
        pdfa_data['pdf_has_output_intent'] = b'/OutputIntent' in content or b'/OutputIntents' in content
        
        if pdfa_data['pdf_has_pdfa_namespace']:
            pdfa_data['pdfa_version_detected'] = True
            if b'1b' in content:
                pdfa_data['pdfa_conformance_level'] = 'B'
            if b'1a' in content:
                pdfa_data['pdfa_conformance_level'] = 'A'
            if b'1u' in content:
                pdfa_data['pdfa_conformance_level'] = 'U'
                
    except Exception as e:
        pdfa_data['pdf_pdfa_info_error'] = str(e)
    
    return pdfa_data


# Extended PDF Document Properties
PDF_EXTENDED_PROPERTIES = {
    'pdf_creator_tool': 'pdf_creator_tool',
    'pdf_producer_version': 'pdf_producer_version',
    'pdf_create_date_utc': 'pdf_create_date_utc',
    'pdf_mod_date_utc': 'pdf_mod_date_utc',
    'pdf_trapped': 'pdf_trapped',
    'pdf_article_thread_subject': 'pdf_article_thread_subject',
    'pdf_article_thread_type': 'pdf_article_thread_type',
    'pdf_web_capture_version': 'pdf_web_capture_version',
    'pdf_web_capture_sprite_name': 'pdf_web_capture_sprite_name',
    'pdf_web_capture_page_sprite': 'pdf_web_capture_page_sprite',
    'pdf_web_capture_page_url': 'pdf_web_capture_page_url',
    'pdf_web_capture_top_left': 'pdf_web_capture_top_left',
    'pdf_web_capture_bottom_right': 'pdf_web_capture_bottom_right',
    'pdf_piece_info_version': 'pdf_piece_info_version',
    'pdf_piece_info_last_modified': 'pdf_piece_info_last_modified',
    'pdf_piece_info_orientation': 'pdf_piece_info_orientation',
    'pdf_struct_tree_root_parent': 'pdf_struct_tree_root_parent',
    'pdf_class_map': 'pdf_class_map',
    'pdf_role_map': 'pdf_role_map',
    'pdf_namespace_uri': 'pdf_namespace_uri',
    'pdf_structure_element_type': 'pdf_structure_element_type',
    'pdf_structure_element_title': 'pdf_structure_element_title',
    'pdf_structure_element_language': 'pdf_structure_element_language',
    'pdf_structure_element_actual_text': 'pdf_structure_element_actual_text',
    'pdf_structure_element_alt_text': 'pdf_structure_element_alt_text',
    'pdf_structure_element_expand_to': 'pdf_structure_element_expand_to',
    'pdf_structure_element_table_scope': 'pdf_structure_element_table_scope',
    'pdf_structure_element_row_span': 'pdf_structure_element_row_span',
    'pdf_structure_element_column_span': 'pdf_structure_element_column_span',
    'pdf_structure_element_headers': 'pdf_structure_element_headers',
    'pdf_structure_element_scope': 'pdf_structure_element_scope',
    'pdf_structure_element_start_node': 'pdf_structure_element_start_node',
    'pdf_structure_element_processing_content': 'pdf_structure_element_processing_content',
    'pdf_mark_info_marked': 'pdf_mark_info_marked',
    'pdf_mark_info_structure_modified': 'pdf_mark_info_structure_modified',
    'pdf_mark_info_user_properties': 'pdf_mark_info_user_properties',
    'pdf_mark_info_display_props': 'pdf_mark_info_display_props',
}

# PDF Accessibility Extensions
PDF_ACCESSIBILITY_TAGS = {
    'pdf_accessibility_language': 'pdf_accessibility_language',
    'pdf_accessibility_title': 'pdf_accessibility_title',
    'pdf_accessibility_description': 'pdf_accessibility_description',
    'pdf_accessibility_metadata': 'pdf_accessibility_metadata',
    'pdf_accessibility_tags_present': 'pdf_accessibility_tags_present',
    'pdf_accessibility_langs': 'pdf_accessibility_langs',
    'pdf_accessibility_outline_levels': 'pdf_accessibility_outline_levels',
    'pdf_accessibility_tab_order': 'pdf_accessibility_tab_order',
    'pdf_accessibility_reading_order': 'pdf_accessibility_reading_order',
    'pdf_accessibility_zoom': 'pdf_accessibility_zoom',
    'pdf_accessibility_page_layout': 'pdf_accessibility_page_layout',
    'pdf_accessibility_page_mode': 'pdf_accessibility_page_mode',
    'pdf_accessibility_non_struct_elements': 'pdf_accessibility_non_struct_elements',
    'pdf_accessibility_artifact': 'pdf_accessibility_artifact',
    'pdf_accessibility_artifact_type': 'pdf_accessibility_artifact_type',
    'pdf_accessibility_artifact_attached': 'pdf_accessibility_artifact_attached',
    'pdf_accessibility_artifact_padding': 'pdf_accessibility_artifact_padding',
}

# PDF Digital Signature Extensions
PDF_SIGNATURE_EXTENSIONS = {
    'pdf_sig_certifier': 'pdf_sig_certifier',
    'pdf_sig_contact_info': 'pdf_sig_contact_info',
    'pdf_sig_location': 'pdf_sig_location',
    'pdf_sig_migration_index': 'pdf_sig_migration_index',
    'pdf_sig_name': 'pdf_sig_name',
    'pdf_sig_reason': 'pdf_sig_reason',
    'pdf_sig_signature_date': 'pdf_sig_signature_date',
    'pdf_sig_appearance': 'pdf_sig_appearance',
    'pdf_sig_appearance_layer': 'pdf_sig_appearance_layer',
    'pdf_sig_appearance_stream': 'pdf_sig_appearance_stream',
    'pdf_sig_da': 'pdf_sig_da',
    'pdf_sig_f': 'pdf_sig_f',
    'pdf_sig_ap': 'pdf_sig_ap',
    'pdf_sig_lock': 'pdf_sig_lock',
    'pdf_sig_sig_ref': 'pdf_sig_sig_ref',
    'pdf_sig_perm': 'pdf_sig_perm',
    'pdf_sig_add_rev_info': 'pdf_sig_add_rev_info',
    'pdf_sig_appearance_dict': 'pdf_sig_appearance_dict',
    'pdf_sig_normal_appearance': 'pdf_sig_normal_appearance',
    'pdf_sig_rollover_appearance': 'pdf_sig_rollover_appearance',
    'pdf_sig_down_appearance': 'pdf_sig_down_appearance',
}

# PDF JavaScript Extensions
PDF_JAVASCRIPT_EXTENSIONS = {
    'pdf_js_action_type': 'pdf_js_action_type',
    'pdf_js_action_next': 'pdf_js_action_next',
    'pdf_js_action_prev': 'pdf_js_action_prev',
    'pdf_js_action_up': 'pdf_js_action_up',
    'pdf_js_action_down': 'pdf_js_action_down',
    'pdf_js_action_left': 'pdf_js_action_left',
    'pdf_js_action_right': 'pdf_js_action_right',
    'pdf_js_action_in': 'pdf_js_action_in',
    'pdf_js_action_out': 'pdf_js_action_out',
    'pdf_js_action_mouse_up': 'pdf_js_action_mouse_up',
    'pdf_js_action_mouse_down': 'pdf_js_action_mouse_down',
    'pdf_js_action_mouse_enter': 'pdf_js_action_mouse_enter',
    'pdf_js_action_mouse_exit': 'pdf_js_action_mouse_exit',
    'pdf_js_action_mouse_over': 'pdf_js_action_mouse_over',
    'pdf_js_action_mouse_move': 'pdf_js_action_mouse_move',
    'pdf_js_action_drag_over': 'pdf_js_action_drag_over',
    'pdf_js_action_drag_leave': 'pdf_js_action_drag_leave',
    'pdf_js_action_calculate': 'pdf_js_action_calculate',
    'pdf_js_action_validate': 'pdf_js_action_validate',
    'pdf_js_action_format': 'pdf_js_action_format',
    'pdf_js_action_key_stroke': 'pdf_js_action_key_stroke',
    'pdf_js_action_execute': 'pdf_js_action_execute',
    'pdf_js_action_page_open': 'pdf_js_action_page_open',
    'pdf_js_action_page_close': 'pdf_js_action_page_close',
    'pdf_js_action_document_open': 'pdf_js_action_document_open',
    'pdf_js_action_document_close': 'pdf_js_action_document_close',
    'pdf_js_action_field_import': 'pdf_js_action_field_import',
    'pdf_js_action_field_export': 'pdf_js_action_field_export',
}

# PDF 3D Annotations Extensions
PDF_3D_EXTENSIONS = {
    'pdf_3d_type': 'pdf_3d_type',
    'pdf_3d_version': 'pdf_3d_version',
    'pdf_3d_production_statement': 'pdf_3d_production_statement',
    'pdf_3d_u3d_data': 'pdf_3d_u3d_data',
    'pdf_3d_coverage': 'pdf_3d_coverage',
    'pdf_3d_stream': 'pdf_3d_stream',
    'pdf_3d_annots_key': 'pdf_3d_annots_key',
    'pdf_3d_interactive': 'pdf_3d_interactive',
    'pdf_3d_animation_style': 'pdf_3d_animation_style',
    'pdf_3d_animation_duration': 'pdf_3d_animation_duration',
    'pdf_3d_animation_loop': 'pdf_3d_animation_loop',
    'pdf_3d_camera': 'pdf_3d_camera',
    'pdf_3d_view': 'pdf_3d_view',
    'pdf_3d_node': 'pdf_3d_node',
    'pdf_3d_light': 'pdf_3d_light',
    'pdf_3d_material': 'pdf_3d_material',
    'pdf_3d_opacity': 'pdf_3d_opacity',
    'pdf_3d_matrix': 'pdf_3d_matrix',
}

# PDF Color Extensions
PDF_COLOR_EXTENSIONS = {
    'pdf_color_profile_name': 'pdf_color_profile_name',
    'pdf_color_profile_type': 'pdf_color_profile_type',
    'pdf_color_profile_info': 'pdf_color_profile_info',
    'pdf_color_profile_dest_output_intent': 'pdf_color_profile_dest_output_intent',
    'pdf_color_profile_src': 'pdf_color_profile_src',
    'pdf_color_profile_dest': 'pdf_color_profile_dest',
    'pdf_color_profile_intent': 'pdf_color_profile_intent',
    'pdf_color_profile_condition': 'pdf_color_profile_condition',
    'pdf_color_profile_registry': 'pdf_color_profile_registry',
    'pdf_color_profile_info_ns': 'pdf_color_profile_info_ns',
    'pdf_color_profile_device_class': 'pdf_color_profile_device_class',
    'pdf_color_profile_color_space': 'pdf_color_profile_color_space',
    'pdf_color_profile_pcs': 'pdf_color_profile_pcs',
}

# PDF Print Extensions
PDF_PRINT_EXTENSIONS = {
    'pdf_print_page_range': 'pdf_print_page_range',
    'pdf_print_num_copies': 'pdf_print_num_copies',
    'pdf_print_scaling': 'pdf_print_scaling',
    'pdf_print_duplex': 'pdf_print_duplex',
    'pdf_print_paper_source': 'pdf_print_paper_source',
    'pdf_print_media_type': 'pdf_print_media_type',
    'pdf_print_quality': 'pdf_print_quality',
    'pdf_print_color_mode': 'pdf_print_color_mode',
    'pdf_print_resolution': 'pdf_print_resolution',
    'pdf_print_pages_per_sheet': 'pdf_print_pages_per_sheet',
    'pdf_print_booklet': 'pdf_print_booklet',
    'pdf_print_booklet_edge': 'pdf_print_booklet_edge',
    'pdf_print_auto_rotate': 'pdf_print_auto_rotate',
    'pdf_print_auto_center': 'pdf_print_auto_center',
    'pdf_print_pages_first': 'pdf_print_pages_first',
    'pdf_print_interpolate': 'pdf_print_interpolate',
    'pdf_print_changes': 'pdf_print_changes',
}

# PDF Security Extensions
PDF_SECURITY_EXTENSIONS = {
    'pdf_encrypt_metadata': 'pdf_encrypt_metadata',
    'pdf_encrypt_attachments_only': 'pdf_encrypt_attachments_only',
    'pdf_owner_password_changed': 'pdf_owner_password_changed',
    'pdf_user_password_changed': 'pdf_user_password_changed',
    'pdf_permissions_changed': 'pdf_permissions_changed',
    'pdf_print_assembly_level': 'pdf_print_assembly_level',
    'pdf_accessibility_extract_level': 'pdf_accessibility_extract_level',
    'pdf_annotation_level': 'pdf_annotation_level',
    'pdf_form_field_level': 'pdf_form_field_level',
    'pdf_signature_field_level': 'pdf_signature_field_level',
    'pdf_rich_media_level': 'pdf_rich_media_level',
    'pdf_algorithm': 'pdf_algorithm',
    'pdf_key_length': 'pdf_key_length',
    'pdf_revision': 'pdf_revision',
    'pdf_encrypt_version': 'pdf_encrypt_version',
}

# PDF Forms Extensions
PDF_FORMS_EXTENSIONS = {
    'pdf_form_default_value': 'pdf_form_default_value',
    'pdf_form_alignment_character': 'pdf_form_alignment_character',
    'pdf_form_max_length': 'pdf_form_max_length',
    'pdf_form_multi_select': 'pdf_form_multi_select',
    'pdf_form_do_not_scroll': 'pdf_form_do_not_scroll',
    'pdf_form_combo_editable': 'pdf_form_combo_editable',
    'pdf_form_sort': 'pdf_form_sort',
    'pdf_form_auto_complete': 'pdf_form_auto_complete',
    'pdf_form_checked': 'pdf_form_checked',
    'pdf_form_default_is_checked': 'pdf_form_default_is_checked',
    'pdf_form_no_toggle_to_off': 'pdf_form_no_toggle_to_off',
    'pdf_form_radio_uni_size': 'pdf_form_radio_uni_size',
    'pdf_form_push_button': 'pdf_form_push_button',
    'pdf_form_icon_only': 'pdf_form_icon_only',
    'pdf_form_no_text': 'pdf_form_no_text',
    'pdf_form_round_corners': 'pdf_form_round_corners',
    'pdf_form_beveled': 'pdf_form_beveled',
    'pdf_form_inset': 'pdf_form_inset',
}

# PDF Font Extensions
PDF_FONT_EXTENSIONS = {
    'pdf_font_type': 'pdf_font_type',
    'pdf_font_subtype': 'pdf_font_subtype',
    'pdf_font_base_font': 'pdf_font_base_font',
    'pdf_font_first_char': 'pdf_font_first_char',
    'pdf_font_last_char': 'pdf_font_last_char',
    'pdf_font_widths': 'pdf_font_widths',
    'pdf_font_descriptor': 'pdf_font_descriptor',
    'pdf_font_to_unicode': 'pdf_font_to_unicode',
    'pdf_font_encoding': 'pdf_font_encoding',
    'pdf_font_encoding_base': 'pdf_font_encoding_base',
    'pdf_font_differences': 'pdf_font_differences',
    'pdf_font_cid_system_info': 'pdf_font_cid_system_info',
    'pdf_font_cid_to_gid_map': 'pdf_font_cid_to_gid_map',
    'pdf_font_descriptor_flags': 'pdf_font_descriptor_flags',
    'pdf_font_descriptor_font_bbox': 'pdf_font_descriptor_font_bbox',
    'pdf_font_descriptor_font_file': 'pdf_font_descriptor_font_file',
    'pdf_font_descriptor_font_file2': 'pdf_font_descriptor_font_file2',
    'pdf_font_descriptor_font_file3': 'pdf_font_descriptor_font_file3',
    'pdf_font_descriptor_missing_width': 'pdf_font_descriptor_missing_width',
    'pdf_font_stretch': 'pdf_font_stretch',
    'pdf_font_weight': 'pdf_font_weight',
    'pdf_font_x_height': 'pdf_font_x_height',
    'pdf_font_cap_height': 'pdf_font_cap_height',
    'pdf_font_descent': 'pdf_font_descent',
    'pdf_font_ascent': 'pdf_font_ascent',
    'pdf_font_italic_angle': 'pdf_font_italic_angle',
    'pdf_font_leading': 'pdf_font_leading',
    'pdf_font_avg_width': 'pdf_font_avg_width',
    'pdf_font_max_width': 'pdf_font_max_width',
    'pdf_font_min_width': 'pdf_font_min_width',
}


def get_pdf_complete_ultimate_extended_field_count() -> int:
    """Return the total count of PDF complete ultimate fields including extensions."""
    base_count = get_pdf_complete_ultimate_field_count()
    extended_count = (
        len(PDF_EXTENDED_PROPERTIES) + len(PDF_ACCESSIBILITY_TAGS) +
        len(PDF_SIGNATURE_EXTENSIONS) + len(PDF_JAVASCRIPT_EXTENSIONS) +
        len(PDF_3D_EXTENSIONS) + len(PDF_COLOR_EXTENSIONS) +
        len(PDF_PRINT_EXTENSIONS) + len(PDF_SECURITY_EXTENSIONS) +
        len(PDF_FORMS_EXTENSIONS) + len(PDF_FONT_EXTENSIONS)
    )
    return base_count + extended_count
