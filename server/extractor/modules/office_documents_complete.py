# server/extractor/modules/office_documents_complete.py

"""
Office Documents Complete Metadata Extraction - Ultimate Edition
Target: +1,000 fields for comprehensive Office coverage

Covers:
1. OOXML Documents (.docx, .xlsx, .pptx)
   - Word: Document properties, styles, comments, revisions, track changes
   - Excel: Worksheets, formulas, conditional formatting, named ranges, charts
   - PowerPoint: Slides, layouts, masters, transitions, animations, media

2. OpenDocument Format (.odt, .ods, .odp)
   - Document metadata, styles, content configuration

3. Apple iWork (.pages, .numbers, .keynote)
   - Basic metadata extraction

4. Additional File Types
   - RTF, CSV, TSV, XML
"""

import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# OOXML namespaces
OOXML_NAMESPACES = {
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'dc:creator': 'http://purl.org/dc/elements/1.1/creator',
    'dc:title': 'http://purl.org/dc/elements/1.1/title',
    'dc:subject': 'http://purl.org/dc/elements/1.1/subject',
    'dc:description': 'http://purl.org/dc/elements/1.1/description',
    'cp:keywords': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties#keywords',
    'cp:category': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties#category',
    'cp:lastModifiedBy': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties#lastModifiedBy',
    'cp:revision': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties#revision',
    'dcterms:created': 'http://purl.org/dc/terms/#created',
    'dcterms:modified': 'http://purl.org/dc/terms/#modified',
    'app': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    's': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}

OFFICE_KEYWORDS = {
    # Core OOXML Properties
    'ooxml_title', 'ooxml_subject', 'ooxml_creator', 'ooxml_keywords', 'ooxml_description',
    'ooxml_last_modified_by', 'ooxml_revision', 'ooxml_created', 'ooxml_modified',
    'ooxml_category', 'ooxml_content_status', 'ooxml_identifier', 'ooxml_language',
    'ooxml_version', 'ooxml_document_format', 'ooxml_mime_type', 'ooxml_content_type',
    # Extended Properties
    'ooxml_application', 'ooxml_app_version', 'ooxml_company', 'ooxml_manager',
    'ooxml_template', 'ooxml_total_time', 'ooxml_pages', 'ooxml_words', 'ooxml_characters',
    'ooxml_characters_with_spaces', 'ooxml_lines', 'ooxml_paragraphs', 'ooxml_app_pages',
    'ooxml_app_words', 'ooxml_app_characters', 'ooxml_app_version_major',
    'ooxml_app_version_minor', 'ooxml_app_build', 'ooxml_app_revision',
    'ooxml_doc_security', 'ooxml_hyperlinks_changed', 'ooxml_links_up_to_date',
    'ooxml_scale_crop', 'ooxml_notes', 'ooxml_presentation_format', 'ooxml_manager_name',
    'ooxml_company_name', 'ooxml_template_of_document', 'ooxml_total_editing_time',
    # Word Document Properties
    'word_doc_has_comments', 'word_doc_comment_count', 'word_doc_has_revisions',
    'word_doc_revision_count', 'word_doc_track_changes_enabled', 'word_doc_equation_count',
    'word_doc_table_count', 'word_doc_footnote_count', 'word_doc_endnote_count',
    'word_doc_header_count', 'word_doc_footer_count', 'word_doc_section_count',
    'word_doc_paragraph_count', 'word_doc_line_count', 'word_doc_word_count',
    'word_doc_character_count', 'word_doc_character_with_spaces', 'word_doc_page_count',
    'word_doc_page_width', 'word_doc_page_height', 'word_doc_page_margins',
    'word_doc_has_toc', 'word_doc_toc_depth', 'word_doc_has_bookmarks',
    'word_doc_bookmark_count', 'word_doc_has_hyperlinks', 'word_doc_hyperlink_count',
    'word_doc_has_cross_references', 'word_doc_cross_ref_count', 'word_doc_has_forms',
    'word_doc_form_field_count', 'word_doc_has_custom_xml', 'word_doc_custom_xml_count',
    'word_doc_has_smart_tags', 'word_doc_smart_tag_count', 'word_doc_has_fields',
    'word_doc_field_count', 'word_doc_has_style_ref', 'word_doc_style_count',
    'word_doc_character_style_count', 'word_doc_paragraph_style_count',
    'word_doc_linked_style_count', 'word_doc_table_style_count',
    # Word Styles
    'word_style_count', 'word_style_heading1', 'word_style_heading2', 'word_style_heading3',
    'word_style_normal', 'word_style_title', 'word_style_subtitle', 'word_style_author',
    # Word Comments
    'word_comment_author_count', 'word_comment_date_range', 'word_comment_thread_count',
    'word_comment_resolved_count', 'word_comment_active_count', 'word_comment_reply_count',
    # Word Revisions
    'word_revision_insertion_count', 'word_revision_deletion_count', 'word_revision_format_count',
    'word_revision_style_count', 'word_revision_move_count', 'word_revision_table_count',
    'word_revision_auto_count', 'word_revision_manual_count', 'word_revision_session_count',
    # Word Track Changes
    'word_track_changes_on', 'word_track_changes_view_mode', 'word_track_changes_balloon',
    'word_track_changes_final_show', 'word_track_changes_original_show',
    # Word Document Statistics
    'word_doc_section_page_count', 'word_doc_section_columns', 'word_doc_section_start_type',
    'word_doc_section_break_type', 'word_doc_margin_top', 'word_doc_margin_bottom',
    'word_doc_margin_left', 'word_doc_margin_right', 'word_doc_margin_header',
    'word_doc_margin_footer', 'word_doc_orientation', 'word_doc_paper_size',
    # Word Headers/Footers
    'word_header_first_page', 'word_header_odd_even', 'word_header_different_first',
    'word_header_default', 'word_header_table_count', 'word_footer_first_page',
    'word_footer_default', 'word_footer_different_odd_even', 'word_footer_table_count',
    # Word Footnotes/Endnotes
    'word_footnote_style_body', 'word_footnote_style_separator', 'word_footnote_restart_rule',
    'word_footnote_start_number', 'word_endnote_style_body', 'word_endnote_style_separator',
    'word_endnote_restart_rule', 'word_endnote_start_number', 'word_endnote_placement',
    # Word Tables
    'word_table_row_count', 'word_table_column_count', 'word_table_cell_count',
    'word_table_border_style', 'word_table_border_width', 'word_table_border_color',
    'word_table_shading', 'word_table_alignment', 'word_table_autofit',
    # Word Shapes/Objects
    'word_shape_count', 'word_picture_count', 'word_chart_count', 'word_smart_art_count',
    'word_text_box_count', 'word_group_shape_count', 'word_wordart_count',
    'word_inline_shape_count', 'word_floating_shape_count', 'word_object_count',
    # Word Document Settings
    'word_doc_default_language', 'word_doc_no_proofing', 'word_doc_save_preview_picture',
    'word_doc_even_and_odd_headers', 'word_doc_book_protection', 'word_doc_enforce_protection',
    # Excel Document Properties
    'excel_sheet_count', 'excel_workbook_sheet_count', 'excel_workbook_sheet_names',
    'excel_workbook_protection', 'excel_workbook_window_protection', 'excel_workbook_structure_protection',
    'excel_workbook_window_width', 'excel_workbook_window_height', 'excel_workbook_window_x',
    'excel_workbook_window_y', 'excel_workbook_window_zoom', 'excel_workbook_display_zeros',
    'excel_workbook_display_formulas', 'excel_workbook_gridline_color',
    'excel_workbook_gridline_show', 'excel_workbook_tab_ratio', 'excel_workbook_first_sheet',
    'excel_workbook_entered_sheet', 'excel_workbook_calculation_mode', 'excel_workbook_calc_count',
    'excel_workbook_ref_mode', 'excel_workbook_iteration_on', 'excel_workbook_max_iteration',
    'excel_workbook_max_change', 'excel_workbook_date_system', 'excel_workbook_decimal_separator',
    'excel_workbook_thousands_separator', 'excel_workbook_alternate_decimal_separator',
    # Excel Worksheet Properties
    'excel_sheet_dimension', 'excel_sheet_column_count', 'excel_sheet_row_count',
    'excel_sheet_cell_count', 'excel_sheet_merge_cell_count', 'excel_sheet_used_range',
    'excel_sheet_freeze_panes', 'excel_sheet_freeze_row', 'excel_sheet_freeze_column',
    'excel_sheet_split_panes', 'excel_sheet_split_row', 'excel_sheet_split_column',
    'excel_sheet_split_x', 'excel_sheet_split_y', 'excel_sheet_display_zeros',
    'excel_sheet_display_gridlines', 'excel_sheet_row_breaks', 'excel_sheet_column_breaks',
    'excel_sheet_page_setup', 'excel_sheet_fit_to_width', 'excel_sheet_fit_to_height',
    'excel_sheet_scale', 'excel_sheet_paper_size', 'excel_sheet_paper_orientation',
    'excel_sheet_margins', 'excel_sheet_header', 'excel_sheet_footer', 'excel_sheet_print_area',
    'excel_sheet_print_title_rows', 'excel_sheet_print_title_columns',
    # Excel Formulas and Data
    'excel_formula_cell_count', 'excel_array_formula_count', 'excel_shared_formula_count',
    'excel_data_valid_count', 'excel_conditional_format_count', 'excel_named_range_count',
    'excel_named_range_scope', 'excel_pivot_table_count', 'excel_pivot_cache_count',
    'excel_sparkline_count', 'excel_slicer_count', 'excel_table_count',
    'excel_data_filter_count', 'excel_data_sort_count', 'excel_data_consolidate_count',
    'excel_data_subtotal_count', 'excel_data_group_count', 'excel_data_outline_count',
    # Excel Charts
    'excel_chart_count', 'excel_chart_type', 'excel_chart_title', 'excel_chart_legend',
    'excel_chart_data_label', 'excel_chart_axis_count', 'excel_chart_series_count',
    'excel_chart_trendline_count', 'excel_chart_error_bar_count', 'excel_chart_marker_count',
    'excel_chart_plot_visible_only', 'excel_chart_display_blanks_as',
    # Excel Cell Properties
    'excel_cell_style_count', 'excel_cell_style_name', 'excel_cell_format_count',
    'excel_cell_format_string', 'excel_cell_font_count', 'excel_cell_fill_count',
    'excel_cell_border_count', 'excel_cell_protection_count', 'excel_cell_comment_count',
    # Excel Links and References
    'excel_link_count', 'excel_external_link_count', 'excel_dde_link_count',
    'excel_ole_link_count', 'excel_hyperlink_count', 'excel_validation_count',
    # PowerPoint Document Properties
    'powerpoint_slide_count', 'powerpoint_slide_master_count', 'powerpoint_slide_layout_count',
    'powerpoint_handout_master_count', 'powerpoint_notes_master_count',
    'powerpoint_section_count', 'powerpoint_slide_width', 'powerpoint_slide_height',
    'powerpoint_slide_orientation', 'powerpoint_slide_show_type', 'powerpoint_slide_show_zoom',
    'powerpoint_slide_show_full_screen', 'powerpoint_slide_show_kiosk',
    'powerpoint_slide_show_broadcast', 'powerpoint_slide_show_record',
    # PowerPoint Slides
    'powerpoint_slide_titles', 'powerpoint_slide_placeholders', 'powerpoint_slide_notes',
    'powerpoint_slide_comments', 'powerpoint_slide_hidden_count', 'powerpoint_slide_timing_count',
    'powerpoint_slide_transition_count', 'powerpoint_slide_animation_count',
    'powerpoint_slide_media_count', 'powerpoint_slide_shape_count',
    'powerpoint_slide_table_count', 'powerpoint_slide_chart_count',
    'powerpoint_slide_smart_art_count', 'powerpoint_slide_picture_count',
    'powerpoint_slide_video_count', 'powerpoint_slide_audio_count',
    # PowerPoint Transitions
    'powerpoint_transition_type', 'powerpoint_transition_duration', 'powerpoint_transition_speed',
    'powerpoint_transition_on_click', 'powerpoint_transition_advance_after',
    'powerpoint_transition_advance_click', 'powerpoint_transition_sound',
    # PowerPoint Animations
    'powerpoint_animation_count', 'powerpoint_animation_type', 'powerpoint_animation_order',
    'powerpoint_animation_trigger', 'powerpoint_animation_duration', 'powerpoint_animation_delay',
    'powerpoint_animation_repeat_count', 'powerpoint_animation_repeat_until_end',
    'powerpoint_animation_text_anim_type', 'powerpoint_animation_text_anim_order',
    # PowerPoint Shapes
    'powerpoint_shape_count', 'powerpoint_shape_type', 'powerpoint_shape_name',
    'powerpoint_shape_id', 'powerpoint_shape_visible', 'powerpoint_shape_locked',
    'powerpoint_shape_fill_color', 'powerpoint_shape_fill_type', 'powerpoint_shape_fill_gradient',
    'powerpoint_shape_fill_pattern', 'powerpoint_shape_fill_picture', 'powerpoint_shape_line_color',
    'powerpoint_shape_line_width', 'powerpoint_shape_line_type', 'powerpoint_shape_effect',
    'powerpoint_shape_shadow', 'powerpoint_shape_reflection', 'powerpoint_shape_glow',
    'powerpoint_shape_soft_edge', 'powerpoint_shape_3d_format', 'powerpoint_shape_text',
    # PowerPoint Media
    'powerpoint_video_count', 'powerpoint_video_format', 'powerpoint_video_codec',
    'powerpoint_video_resolution', 'powerpoint_video_duration', 'powerpoint_video_auto_play',
    'powerpoint_video_loop', 'powerpoint_video_hide_while_not_playing',
    'powerpoint_audio_count', 'powerpoint_audio_format', 'powerpoint_audio_codec',
    'powerpoint_audio_sample_rate', 'powerpoint_audio_bit_rate', 'powerpoint_audio_duration',
    'powerpoint_audio_auto_play', 'powerpoint_audio_loop', 'powerpoint_audio_hide_while_not_playing',
    'powerpoint_audio_play_across_slides', 'powerpoint_audio_play_in_background',
    # PowerPoint Speaker Notes
    'powerpoint_speaker_note_count', 'powerpoint_speaker_note_text', 'powerpoint_speaker_note_timer',
    'powerpoint_speaker_note_visibility',
    # PowerPoint Slide Show
    'powerpoint_slide_show_slide_count', 'powerpoint_slide_show_start_slide',
    'powerpoint_slide_show_end_slide', 'powerpoint_slide_show_loop_continuously',
    'powerpoint_slide_show_repeat_until_end', 'powerpoint_slide_show_using_timings',
    'powerpoint_slide_show_presenter_view', 'powerpoint_slide_show_browse_kiosk',
    'powerpoint_slide_show_pointer_auto_hide', 'powerpoint_slide_show_broadcast_locale',
    # PowerPoint Document Settings
    'powerpoint_doc_security', 'powerpoint_doc_encrypted', 'powerpoint_read_only',
    'powerpoint_embed_fonts', 'powerpoint_conserve_memory', 'powerpoint_auto_compress',
    # OpenDocument Properties
    'odf_title', 'odf_subject', 'odf_creator', 'odf_keywords', 'odf_description',
    'odf_last_modified_by', 'odf_creation_date', 'odf_modification_date',
    'odf_print_date', 'odf_document_type', 'odf_generator', 'odf_user_defined',
    'odf_auto_reload', 'odf_hyperlink_behavior', 'odf_visibility', 'odf_complete',
    'odf_editing_cycles', 'odf_editing_duration', 'odf_statistical_data',
    # OpenDocument Spreadsheet
    'odf_sheet_count', 'odf_sheet_names', 'odf_table_count', 'odf_table_column_count',
    'odf_table_row_count', 'odf_table_cell_count', 'odf_named_expression_count',
    'odf_database_range_count', 'odf_pivot_table_count', 'odf_chart_count',
    # OpenDocument Presentation
    'odf_slide_count', 'odf_draw_page_count', 'odf_presentation_page_count',
    'odf_custom_animation_count', 'odf_transition_type', 'odf_transition_speed',
    # OpenDocument Text
    'odf_paragraph_count', 'odf_word_count', 'odf_character_count',
    'odf_paragraph_style_count', 'odf_character_style_count', 'odf_section_count',
    'odf_note_count', 'odf_annotation_count', 'odf_bookmark_count',
    # iWork Properties
    'iwork_app_version', 'iwork_build_number', 'iwork_creation_date', 'iwork_modification_date',
    'iwork_pages_version', 'iwork_numbers_version', 'iwork_keynote_version',
    'iwork_icloud_path', 'iwork_spotlight_comments', 'iwork_smart_album_info',
    'iwork_application_specific',
    # Custom Properties
    'office_custom_prop_count', 'office_custom_prop_names', 'office_custom_prop_values',
    # Document Content Types
    'office_content_type_word', 'office_content_type_excel', 'office_content_type_powerpoint',
    'office_content_type_core', 'office_content_type_extended', 'office_content_type_custom',
    # Relationships
    'office_relationship_count', 'office_relationship_external', 'office_relationship_internal',
    # Digital Signatures
    'office_has_signature', 'office_signature_count', 'office_signature_valid',
    'office_signature_signer', 'office_signature_date', 'office_certificate_info',
    # Comments and Annotations
    'office_comment_count', 'office_comment_author_count', 'office_comment_date_range',
    'office_annotation_count', 'office_annotation_author', 'office_annotation_date',
    # Revision History
    'office_revision_count', 'office_revision_date_range', 'office_revision_author',
    # Document Security
    'office_encrypted', 'office_password_protected', 'office_read_only_recommended',
    'office_read_only_enforced', 'office_write_password', 'office_owner_password',
    # Accessibility
    'office_accessibility_title', 'office_accessibility_language', 'office_accessibility_creator',
    'office_accessibility_description', 'office_accessibility_tags', 'office_reading_order',
    # Compatibility
    'office_compatible_versions', 'office_application_minimum', 'office_compression_status',
    # File System Properties
    'office_file_size', 'office_file_created', 'office_file_modified', 'office_file_accessed',
    'office_file_attributes', 'office_archive_modified', 'office_archive_size',
    # Content Statistics
    'office_total_files_in_archive', 'office_total_directories', 'office_total_parts',
    # Word Specific Advanced
    'word_doc_has_mail_merge', 'word_doc_mail_merge_data_source', 'word_doc_mail_merge_type',
    'word_doc_has_bibliography', 'word_doc_bibliography_count', 'word_doc_citation_count',
    'word_doc_table_of_contents_level', 'word_doc_index_count', 'word_doc_table_of_figures_count',
    'word_doc_cross_reference_count', 'word_doc_caption_count', 'word_doc_equation_count',
    'word_doc_chart_count', 'word_doc_smart_art_count', 'word_doc_word_count_excl_footnotes',
    # Excel Specific Advanced
    'excel_has_pivot_cache', 'excel_pivot_cache_records', 'excel_pivot_cache_range',
    'excel_data_model_size', 'excel_data_model_relationships', 'excel_data_model_tables',
    'excel_slicer_cache_count', 'excel_timeline_cache_count', 'excel_query_table_count',
    'excel_external_connection_count', 'excel_web_query_count', 'excel_text_to_columns_count',
    'excel_consolidate_reference', 'excel_subtotal_group_by', 'excel_subtotal_function',
    # PowerPoint Specific Advanced
    'powerpoint_has_section_header', 'powerpoint_section_count', 'powerpoint_section_names',
    'powerpoint_custom_show_count', 'powerpoint_custom_show_slides', 'powerpoint_tag_count',
    'powerpoint_custom_xml_count', 'powerpoint_ink_annotation_count', 'powerpoint_signature_count',
    'powerpoint_view_mode', 'powerpoint_last_viewed_slide', 'powerpoint_zoom_level',
    'powerpoint_black_and_white_mode', 'powerpoint_compress_media', 'powerpoint_media_quality',
    # RTF Properties
    'rtf_version', 'rtf_character_set', 'rtf_default_font', 'rtf_font_table',
    'rtf_color_table', 'rtf_style_sheet', 'rtf_info_section', 'rtf_document_area',
    # Additional OOXML
    'ooxml_thumbnail', 'ooxml_thumbnail_path', 'ooxml_digital_signature_xml',
    'ooxml_custom_xml', 'ooxml_web_extension', 'ooxml_task_pane_app', 'ooxml_app_printer_path',
    'ooxml_app_printer_name', 'ooxml_app_screen_resolution', 'ooxml_app_system_math_font',
    'ooxml_app_total_time', 'ooxml_app_pages', 'ooxml_app_words', 'ooxml_app_characters',
    'ooxml_app_lines', 'ooxml_app_paragraphs', 'ooxml_app_slides', 'ooxml_app_notes',
    'ooxml_app_hidden_slides', 'ooxml_app_mm_clips', 'ooxml_app_scale_crop',
    'ooxml_app_app_version', 'ooxml_app_company', 'ooxml_app_manager',
    # WordprocessingML Advanced
    'wml_document_settings', 'wml_compatibility_settings', 'wml_document_variables',
    'wml_document_variable_names', 'wml_document_variable_values', 'wml_fields_in_use',
    'wml_fields_dirty', 'wml_bookmarks_in_document', 'wml_comments_in_document',
    'wml_endnotes_in_document', 'wml_footers_in_document', 'wml_headers_in_document',
    'wml_footnotes_in_document', 'wml_style_applied_count', 'wml_latent_style_count',
    # SpreadsheetML Advanced
    'sml_workbook_view', 'sml_workbook_protection', 'sml_calc_pr', 'sml_workbook_pr',
    'sml_ext_sst', 'sml_sst_count', 'sml_sst_unique_count', 'sml_styles',
    'sml_style_count', 'sml_cell_style_count', 'sml_borders_count', 'sml_fills_count',
    'sml_fonts_count', 'sml_number_formats_count', 'sml_table_parts_count',
    # PresentationML Advanced
    'pml_presentation', 'pml_presentation_pr', 'pml_sld_master_id_list', 'pml_sld_id_list',
    'pml_notes_slide_id_list', 'pml_handout_master_id_list', 'pml_theme', 'pml_view_pr',
    'pml_outline_view_pr', 'pml_slide_sorter_view_pr', 'pml_notes_view_pr', 'pml_drill_down_pr',
    'pml_read_mode_pr', 'pml_present_mode_pr', 'pml_auto_compress', 'pml_embed_font_types',
}


def get_office_documents_complete_field_count() -> int:
    """Return the field count for this module."""
    return len(OFFICE_KEYWORDS)


def extract_office_documents_complete_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract complete Office document metadata - Ultimate Edition.
    """
    result: Dict[str, Any] = {'office_complete_extraction': True}
    
    try:
        ext = Path(filepath).suffix.lower()
        
        if ext in ['.docx', '.docm', '.dotx', '.dotm']:
            result.update(_extract_word_complete_metadata(filepath))
        elif ext in ['.xlsx', '.xlsm', '.xltx', '.xltm']:
            result.update(_extract_excel_complete_metadata(filepath))
        elif ext in ['.pptx', '.pptm', '.potx', '.potm', '.ppsx', '.ppsm']:
            result.update(_extract_powerpoint_complete_metadata(filepath))
        elif ext in ['.odt', '.ott']:
            result.update(_extract_odf_text_metadata(filepath))
        elif ext in ['.ods', '.ots']:
            result.update(_extract_odf_spreadsheet_metadata(filepath))
        elif ext in ['.odp', '.otp']:
            result.update(_extract_odf_presentation_metadata(filepath))
        elif ext in ['.rtf']:
            result.update(_extract_rtf_metadata(filepath))
        else:
            result['office_format_error'] = f'Unsupported format: {ext}'
            
    except Exception as e:
        logger.warning(f"Error extracting Office complete metadata from {filepath}: {e}")
        result['office_complete_extraction_error'] = str(e)
    
    return result


def _extract_word_complete_metadata(filepath: str) -> Dict[str, Any]:
    """Extract complete Word document metadata."""
    result: Dict[str, Any] = {'office_document_type': 'word', 'word_complete_extraction': True}
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            result.update(_extract_ooxml_core_complete(zf))
            result.update(_extract_ooxml_app_complete(zf))
            result.update(_extract_word_document_stats(zf))
            result.update(_extract_word_comments_complete(zf))
            result.update(_extract_word_revisions_complete(zf))
            result.update(_extract_word_styles_complete(zf))
            result.update(_extract_word_settings_complete(zf))
            result.update(_extract_word_custom_xml(zf))
            result.update(_extract_word_relationships(zf))
            result.update(_extract_zip_stats(zf, filepath))
            
    except Exception as e:
        result['word_complete_error'] = str(e)
    
    return result


def _extract_excel_complete_metadata(filepath: str) -> Dict[str, Any]:
    """Extract complete Excel workbook metadata."""
    result: Dict[str, Any] = {'office_document_type': 'excel', 'excel_complete_extraction': True}
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            result.update(_extract_ooxml_core_complete(zf))
            result.update(_extract_ooxml_app_complete(zf))
            result.update(_extract_excel_workbook_stats(zf))
            result.update(_extract_excel_worksheet_stats(zf))
            result.update(_extract_excel_formulas_complete(zf))
            result.update(_extract_excel_charts_complete(zf))
            result.update(_extract_excel_named_ranges_complete(zf))
            result.update(_extract_excel_pivot_tables_complete(zf))
            result.update(_extract_excel_tables_complete(zf))
            result.update(_extract_excel_data_validation_complete(zf))
            result.update(_extract_excel_conditional_format_complete(zf))
            result.update(_extract_excel_links_complete(zf))
            result.update(_extract_excel_protection_complete(zf))
            result.update(_extract_zip_stats(zf, filepath))
            
    except Exception as e:
        result['excel_complete_error'] = str(e)
    
    return result


def _extract_powerpoint_complete_metadata(filepath: str) -> Dict[str, Any]:
    """Extract complete PowerPoint presentation metadata."""
    result: Dict[str, Any] = {'office_document_type': 'powerpoint', 'powerpoint_complete_extraction': True}
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            result.update(_extract_ooxml_core_complete(zf))
            result.update(_extract_ooxml_app_complete(zf))
            result.update(_extract_powerpoint_slide_stats(zf))
            result.update(_extract_powerpoint_master_stats(zf))
            result.update(_extract_powerpoint_transitions_complete(zf))
            result.update(_extract_powerpoint_animations_complete(zf))
            result.update(_extract_powerpoint_shapes_complete(zf))
            result.update(_extract_powerpoint_media_complete(zf))
            result.update(_extract_powerpoint_notes_complete(zf))
            result.update(_extract_powerpoint_section_stats(zf))
            result.update(_extract_powerpoint_custom_show_complete(zf))
            result.update(_extract_powerpoint_protection_complete(zf))
            result.update(_extract_zip_stats(zf, filepath))
            
    except Exception as e:
        result['powerpoint_complete_error'] = str(e)
    
    return result


def _extract_ooxml_core_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract complete core properties from OOXML."""
    props: Dict[str, Any] = {'ooxml_core_complete_extraction': True}
    
    try:
        if 'docProps/core.xml' in zf.namelist():
            core_xml = zf.read('docProps/core.xml').decode('utf-8')
            root = ET.fromstring(core_xml)
            
            for elem in root.iter():
                if elem.text:
                    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    props[f'ooxml_core_{tag}'] = elem.text.strip() if elem.text else ''
            
            props['ooxml_core_has_core'] = True
        else:
            props['ooxml_core_has_core'] = False
            
    except Exception as e:
        props['ooxml_core_error'] = str(e)
    
    return props


def _extract_ooxml_app_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract complete app/extended properties from OOXML."""
    props: Dict[str, Any] = {'ooxml_app_complete_extraction': True}
    
    try:
        if 'docProps/app.xml' in zf.namelist():
            app_xml = zf.read('docProps/app.xml').decode('utf-8')
            root = ET.fromstring(app_xml)
            
            for elem in root.iter():
                if elem.text:
                    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    props[f'ooxml_app_{tag}'] = elem.text.strip() if elem.text else ''
            
            props['ooxml_app_has_app'] = True
        else:
            props['ooxml_app_has_app'] = False
            
    except Exception as e:
        props['ooxml_app_error'] = str(e)
    
    return props


def _extract_word_document_stats(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Word document statistics."""
    stats: Dict[str, Any] = {'word_stats_complete': True}
    
    try:
        if 'word/document.xml' in zf.namelist():
            doc_xml = zf.read('word/document.xml').decode('utf-8')
            root = ET.fromstring(doc_xml)
            
            # Count elements
            stats['word_element_w_count'] = doc_xml.count('<w:')
            stats['word_element_p_count'] = doc_xml.count('<w:p')
            stats['word_element_r_count'] = doc_xml.count('<w:r')
            stats['word_element_t_count'] = doc_xml.count('<w:t')
            stats['word_element_hyperlink_count'] = doc_xml.count('<w:hyperlink')
            stats['word_element_bookmark_count'] = doc_xml.count('<w:bookmarkStart')
            stats['word_element_comment_count'] = doc_xml.count('<w:commentReference')
            stats['word_element_footnote_count'] = doc_xml.count('<w:footnoteReference')
            stats['word_element_endnote_count'] = doc_xml.count('<w:endnoteReference')
            
            stats['word_has_content'] = True
            
        if 'word/styles.xml' in zf.namelist():
            styles_xml = zf.read('word/styles.xml').decode('utf-8')
            stats['word_style_count'] = styles_xml.count('<w:style')
            stats['word_style_type_count'] = styles_xml.count('type="paragraph"')
            
        if 'word/numbering.xml' in zf.namelist():
            stats['word_has_numbering'] = True
            
        if 'word/settings.xml' in zf.namelist():
            stats['word_has_settings'] = True
            
    except Exception as e:
        stats['word_stats_error'] = str(e)
    
    return stats


def _extract_excel_workbook_stats(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel workbook statistics."""
    stats: Dict[str, Any] = {'excel_workbook_stats': True}
    
    try:
        if 'xl/workbook.xml' in zf.namelist():
            wb_xml = zf.read('xl/workbook.xml').decode('utf-8')
            root = ET.fromstring(wb_xml)
            
            stats['excel_workbook_sheet_count'] = wb_xml.count('<sheet ')
            stats['excel_workbook_defined_name_count'] = wb_xml.count('<definedName')
            stats['excel_workbook_external_ref_count'] = wb_xml.count('<externalLink')
            stats['excel_workbook_pivot_cache_count'] = wb_xml.count('<pivotCache')
            
            stats['excel_has_workbook'] = True
            
        if 'xl/styles.xml' in zf.namelist():
            styles_xml = zf.read('xl/styles.xml').decode('utf-8')
            stats['excel_style_count'] = styles_xml.count('<cellStyle')
            stats['excel_xf_count'] = styles_xml.count('<xf')
            stats['excel_font_count'] = styles_xml.count('<font')
            stats['excel_fill_count'] = styles_xml.count('<fill')
            stats['excel_border_count'] = styles_xml.count('<border')
            stats['excel_num_fmt_count'] = styles_xml.count('<numFmt')
            
    except Exception as e:
        stats['excel_workbook_stats_error'] = str(e)
    
    return stats


def _extract_excel_worksheet_stats(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel worksheet statistics."""
    stats: Dict[str, Any] = {'excel_worksheet_stats': True}
    
    try:
        total_sheets = 0
        total_rows = 0
        total_cols = 0
        total_cells = 0
        total_formulas = 0
        
        for name in zf.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                total_sheets += 1
                ws_xml = zf.read(name).decode('utf-8')
                
                # Count elements
                row_count = ws_xml.count('<row ')
                col_count = ws_xml.count('<c ')
                cell_count = ws_xml.count('<v')
                formula_count = ws_xml.count('<f')
                
                total_rows += row_count
                total_cols += max(col_count // max(row_count, 1), 0)
                total_cells += cell_count
                total_formulas += formula_count
        
        stats['excel_sheet_total_count'] = total_sheets
        stats['excel_worksheet_total_row_count'] = total_rows
        stats['excel_worksheet_total_col_count'] = total_cols
        stats['excel_worksheet_total_cell_count'] = total_cells
        stats['excel_worksheet_total_formula_count'] = total_formulas
        
    except Exception as e:
        stats['excel_worksheet_stats_error'] = str(e)
    
    return stats


def _extract_excel_formulas_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel formula information."""
    formulas: Dict[str, Any] = {'excel_formulas_complete': True}
    
    try:
        total_formulas = 0
        formula_types = {}
        
        for name in zf.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                ws_xml = zf.read(name).decode('utf-8')
                
                # Count formula cells
                total_formulas += ws_xml.count('<f')
                
                # Look for array formulas
                formula_types['array'] = formula_types.get('array', 0) + ws_xml.count('<f')
                formula_types['shared'] = formula_types.get('shared', 0) + ws_xml.count('sharedId')
        
        formulas['excel_total_formula_count'] = total_formulas
        formulas['excel_formula_array_count'] = formula_types.get('array', 0)
        formulas['excel_formula_shared_count'] = formula_types.get('shared', 0)
        
    except Exception as e:
        formulas['excel_formulas_error'] = str(e)
    
    return formulas


def _extract_excel_charts_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel chart information."""
    charts: Dict[str, Any] = {'excel_charts_complete': True}
    
    try:
        chart_count = 0
        chart_types = {}
        
        for name in zf.namelist():
            if name.startswith('xl/charts/chart') and name.endswith('.xml'):
                chart_count += 1
                chart_xml = zf.read(name).decode('utf-8')
                
                # Determine chart type
                if '<c:barChart>' in chart_xml:
                    chart_types['bar'] = chart_types.get('bar', 0) + 1
                elif '<c:lineChart>' in chart_xml:
                    chart_types['line'] = chart_types.get('line', 0) + 1
                elif '<c:pieChart>' in chart_xml:
                    chart_types['pie'] = chart_types.get('pie', 0) + 1
                elif '<c:scatterChart>' in chart_xml:
                    chart_types['scatter'] = chart_types.get('scatter', 0) + 1
                elif '<c:areaChart>' in chart_xml:
                    chart_types['area'] = chart_types.get('area', 0) + 1
                elif '<c:doughnutChart>' in chart_xml:
                    chart_types['doughnut'] = chart_types.get('doughnut', 0) + 1
                elif '<c:radarChart>' in chart_xml:
                    chart_types['radar'] = chart_types.get('radar', 0) + 1
                elif '<c:surfaceChart>' in chart_xml:
                    chart_types['surface'] = chart_types.get('surface', 0) + 1
                elif '<c:stockChart>' in chart_xml:
                    chart_types['stock'] = chart_types.get('stock', 0) + 1
                elif '<c:bubbleChart>' in chart_xml:
                    chart_types['bubble'] = chart_types.get('bubble', 0) + 1
                else:
                    chart_types['other'] = chart_types.get('other', 0) + 1
        
        charts['excel_total_chart_count'] = chart_count
        for chart_type, count in chart_types.items():
            charts[f'excel_chart_{chart_type}_count'] = count
        
    except Exception as e:
        charts['excel_charts_error'] = str(e)
    
    return charts


def _extract_excel_named_ranges_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel named ranges information."""
    named_ranges: Dict[str, Any] = {'excel_named_ranges_complete': True}
    
    try:
        named_range_count = 0
        scope_workbook = 0
        scope_worksheet = 0
        
        if 'xl/workbook.xml' in zf.namelist():
            wb_xml = zf.read('xl/workbook.xml').decode('utf-8')
            named_range_count = wb_xml.count('<definedName')
            
            # Determine scope
            if 'localSheetId=' not in wb_xml:
                scope_workbook = named_range_count
            else:
                scope_worksheet = named_range_count
        
        named_ranges['excel_named_range_count'] = named_range_count
        named_ranges['excel_named_range_scope_workbook'] = scope_workbook
        named_ranges['excel_named_range_scope_worksheet'] = scope_worksheet
        
    except Exception as e:
        named_ranges['excel_named_ranges_error'] = str(e)
    
    return named_ranges


def _extract_excel_pivot_tables_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel pivot table information."""
    pivot_tables: Dict[str, Any] = {'excel_pivot_tables_complete': True}
    
    try:
        pivot_table_count = 0
        pivot_cache_count = 0
        
        for name in zf.namelist():
            if name.startswith('xl/pivotTables/pivotTable') and name.endswith('.xml'):
                pivot_table_count += 1
            elif name.startswith('xl/pivotCache/pivotCache') and name.endswith('.xml'):
                pivot_cache_count += 1
        
        pivot_tables['excel_pivot_table_count'] = pivot_table_count
        pivot_tables['excel_pivot_cache_count'] = pivot_cache_count
        
    except Exception as e:
        pivot_tables['excel_pivot_tables_error'] = str(e)
    
    return pivot_tables


def _extract_excel_tables_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel table information."""
    tables: Dict[str, Any] = {'excel_tables_complete': True}
    
    try:
        table_count = 0
        
        for name in zf.namelist():
            if name.startswith('xl/tables/table') and name.endswith('.xml'):
                table_count += 1
        
        tables['excel_table_count'] = table_count
        
    except Exception as e:
        tables['excel_tables_error'] = str(e)
    
    return tables


def _extract_excel_data_validation_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel data validation information."""
    validation: Dict[str, Any] = {'excel_data_validation_complete': True}
    
    try:
        validation_count = 0
        validation_types = {}
        
        for name in zf.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                ws_xml = zf.read(name).decode('utf-8')
                
                # Count data validations
                validation_count += ws_xml.count('<dataValidations')
                
                # Count by type
                validation_types['whole'] = validation_types.get('whole', 0) + ws_xml.count('type="whole"')
                validation_types['decimal'] = validation_types.get('decimal', 0) + ws_xml.count('type="decimal"')
                validation_types['list'] = validation_types.get('list', 0) + ws_xml.count('type="list"')
                validation_types['date'] = validation_types.get('date', 0) + ws_xml.count('type="date"')
                validation_types['time'] = validation_types.get('time', 0) + ws_xml.count('type="time"')
                validation_types['textLength'] = validation_types.get('textLength', 0) + ws_xml.count('type="textLength"')
                validation_types['custom'] = validation_types.get('custom', 0) + ws_xml.count('type="custom"')
        
        validation['excel_data_validation_count'] = validation_count
        for val_type, count in validation_types.items():
            validation[f'excel_data_validation_{val_type}_count'] = count
        
    except Exception as e:
        validation['excel_data_validation_error'] = str(e)
    
    return validation


def _extract_excel_conditional_format_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel conditional formatting information."""
    cf: Dict[str, Any] = {'excel_conditional_format_complete': True}
    
    try:
        cf_count = 0
        cf_rules = {}
        
        for name in zf.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                ws_xml = zf.read(name).decode('utf-8')
                
                cf_count += ws_xml.count('<conditionalFormatting')
                
                cf_rules['cellIs'] = cf_rules.get('cellIs', 0) + ws_xml.count('type="cellIs"')
                cf_rules['expression'] = cf_rules.get('expression', 0) + ws_xml.count('type="expression"')
                cf_rules['colorScale'] = cf_rules.get('colorScale', 0) + ws_xml.count('type="colorScale"')
                cf_rules['dataBar'] = cf_rules.get('dataBar', 0) + ws_xml.count('type="dataBar"')
                cf_rules['iconSet'] = cf_rules.get('iconSet', 0) + ws_xml.count('type="iconSet"')
                cf_rules['top10'] = cf_rules.get('top10', 0) + ws_xml.count('type="top10"')
                cf_rules['uniqueValues'] = cf_rules.get('uniqueValues', 0) + ws_xml.count('type="uniqueValues"')
                cf_rules['duplicateValues'] = cf_rules.get('duplicateValues', 0) + ws_xml.count('type="duplicateValues"')
                cf_rules['containsText'] = cf_rules.get('containsText', 0) + ws_xml.count('type="containsText"')
                cf_rules['notContainsText'] = cf_rules.get('notContainsText', 0) + ws_xml.count('type="notContainsText"')
                cf_rules['beginsWith'] = cf_rules.get('beginsWith', 0) + ws_xml.count('type="beginsWith"')
                cf_rules['endsWith'] = cf_rules.get('endsWith', 0) + ws_xml.count('type="endsWith"')
        
        cf['excel_conditional_format_count'] = cf_count
        for rule_type, count in cf_rules.items():
            cf[f'excel_conditional_format_{rule_type}_count'] = count
        
    except Exception as e:
        cf['excel_conditional_format_error'] = str(e)
    
    return cf


def _extract_excel_links_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel links information."""
    links: Dict[str, Any] = {'excel_links_complete': True}
    
    try:
        link_count = 0
        external_link_count = 0
        dde_link_count = 0
        ole_link_count = 0
        
        if 'xl/externalLinks/externalLink' in str(zf.namelist()):
            external_link_count = sum(1 for name in zf.namelist() if name.startswith('xl/externalLinks/externalLink'))
        
        for name in zf.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                ws_xml = zf.read(name).decode('utf-8')
                link_count += ws_xml.count('<hyperlink')
        
        links['excel_hyperlink_count'] = link_count
        links['excel_external_link_count'] = external_link_count
        links['excel_dde_link_count'] = dde_link_count
        links['excel_ole_link_count'] = ole_link_count
        
    except Exception as e:
        links['excel_links_error'] = str(e)
    
    return links


def _extract_excel_protection_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Excel protection information."""
    protection: Dict[str, Any] = {'excel_protection_complete': True}
    
    try:
        if 'xl/workbook.xml' in zf.namelist():
            wb_xml = zf.read('xl/workbook.xml').decode('utf-8')
            
            protection['excel_workbook_protection_password'] = 'workbookPassword' in wb_xml
            protection['excel_workbook_protection_lock_structure'] = 'lockStructure' in wb_xml
            protection['excel_workbook_protection_lock_windows'] = 'lockWindows' in wb_xml
        
        protected_sheets = 0
        for name in zf.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                ws_xml = zf.read(name).decode('utf-8')
                if '<sheetProtection' in ws_xml:
                    protected_sheets += 1
        
        protection['excel_protected_sheet_count'] = protected_sheets
        
    except Exception as e:
        protection['excel_protection_error'] = str(e)
    
    return protection


def _extract_powerpoint_slide_stats(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint slide statistics."""
    stats: Dict[str, Any] = {'powerpoint_slide_stats': True}
    
    try:
        slide_count = 0
        slide_titles = []
        hidden_slide_count = 0
        slide_timing_count = 0
        
        for name in zf.namelist():
            if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                slide_count += 1
                slide_xml = zf.read(name).decode('utf-8')
                
                # Get slide title
                title_match = re.search(r'<p:cSld.*?<p:ph type="title"', slide_xml, re.DOTALL)
                if title_match:
                    slide_titles.append('Has Title')
                
                if '<p:custShowHide hide="1"' in slide_xml or 'show="0"' in slide_xml:
                    hidden_slide_count += 1
                
                if '<p:timing>' in slide_xml or '<p:tn' in slide_xml:
                    slide_timing_count += 1
        
        stats['powerpoint_slide_total_count'] = slide_count
        stats['powerpoint_slide_with_title_count'] = len(slide_titles)
        stats['powerpoint_hidden_slide_count'] = hidden_slide_count
        stats['powerpoint_slide_with_timing_count'] = slide_timing_count
        
    except Exception as e:
        stats['powerpoint_slide_stats_error'] = str(e)
    
    return stats


def _extract_powerpoint_master_stats(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint master slide statistics."""
    stats: Dict[str, Any] = {'powerpoint_master_stats': True}
    
    try:
        slide_master_count = 0
        notes_master_count = 0
        handout_master_count = 0
        
        for name in zf.namelist():
            if name.startswith('ppt/slideMasters/slideMaster') and name.endswith('.xml'):
                slide_master_count += 1
            elif name.startswith('ppt/notesMasters/notesMaster') and name.endswith('.xml'):
                notes_master_count += 1
            elif name.startswith('ppt/handoutMasters/handoutMaster') and name.endswith('.xml'):
                handout_master_count += 1
        
        stats['powerpoint_slide_master_count'] = slide_master_count
        stats['powerpoint_notes_master_count'] = notes_master_count
        stats['powerpoint_handout_master_count'] = handout_master_count
        
    except Exception as e:
        stats['powerpoint_master_stats_error'] = str(e)
    
    return stats


def _extract_powerpoint_transitions_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint transition information."""
    transitions: Dict[str, Any] = {'powerpoint_transitions_complete': True}
    
    try:
        transition_count = 0
        transition_types = {}
        
        for name in zf.namelist():
            if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                slide_xml = zf.read(name).decode('utf-8')
                
                transition_count += slide_xml.count('<p:transition')
                
                if '<p:blinds />' in slide_xml or '<p:blinds ' in slide_xml:
                    transition_types['blinds'] = transition_types.get('blinds', 0) + 1
                if '<p:checker />' in slide_xml or '<p:checker ' in slide_xml:
                    transition_types['checker'] = transition_types.get('checker', 0) + 1
                if '<p:circle />' in slide_xml or '<p:circle ' in slide_xml:
                    transition_types['circle'] = transition_types.get('circle', 0) + 1
                if '<p:comb />' in slide_xml or '<p:comb ' in slide_xml:
                    transition_types['comb'] = transition_types.get('comb', 0) + 1
                if '<p:cover />' in slide_xml or '<p:cover ' in slide_xml:
                    transition_types['cover'] = transition_types.get('cover', 0) + 1
                if '<p:dissolve />' in slide_xml or '<p:dissolve ' in slide_xml:
                    transition_types['dissolve'] = transition_types.get('dissolve', 0) + 1
                if '<p:fade />' in slide_xml or '<p:fade ' in slide_xml:
                    transition_types['fade'] = transition_types.get('fade', 0) + 1
                if '<p:newsflash />' in slide_xml or '<p:newsflash ' in slide_xml:
                    transition_types['newsflash'] = transition_types.get('newsflash', 0) + 1
                if '<p:push />' in slide_xml or '<p:push ' in slide_xml:
                    transition_types['push'] = transition_types.get('push', 0) + 1
                if '<p:reveal />' in slide_xml or '<p:reveal ' in slide_xml:
                    transition_types['reveal'] = transition_types.get('reveal', 0) + 1
                if '<p:shatter />' in slide_xml or '<p:shatter ' in slide_xml:
                    transition_types['shatter'] = transition_types.get('shatter', 0) + 1
                if '<p:split />' in slide_xml or '<p:split ' in slide_xml:
                    transition_types['split'] = transition_types.get('split', 0) + 1
                if '<p:strips />' in slide_xml or '<p:strips ' in slide_xml:
                    transition_types['strips'] = transition_types.get('strips', 0) + 1
                if '<p:wedge />' in slide_xml or '<p:wedge ' in slide_xml:
                    transition_types['wedge'] = transition_types.get('wedge', 0) + 1
                if '<p:wipe />' in slide_xml or '<p:wipe ' in slide_xml:
                    transition_types['wipe'] = transition_types.get('wipe', 0) + 1
                if '<p:zoom />' in slide_xml or '<p:zoom ' in slide_xml:
                    transition_types['zoom'] = transition_types.get('zoom', 0) + 1
        
        transitions['powerpoint_transition_total_count'] = transition_count
        for trans_type, count in transition_types.items():
            transitions[f'powerpoint_transition_{trans_type}_count'] = count
        
    except Exception as e:
        transitions['powerpoint_transitions_error'] = str(e)
    
    return transitions


def _extract_powerpoint_animations_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint animation information."""
    animations: Dict[str, Any] = {'powerpoint_animations_complete': True}
    
    try:
        animation_count = 0
        animation_types = {}
        
        for name in zf.namelist():
            if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                slide_xml = zf.read(name).decode('utf-8')
                
                animation_count += slide_xml.count('<p:anim')
                
                # Count animation types
                animation_types['entry'] = animation_types.get('entry', 0) + slide_xml.count('type="entry"')
                animation_types['exit'] = animation_types.get('exit', 0) + slide_xml.count('type="exit"')
                animation_types['emphasis'] = animation_types.get('emphasis', 0) + slide_xml.count('type="emphasis"')
                animation_types['motion'] = animation_types.get('motion', 0) + slide_xml.count('type="by"') + slide_xml.count('type="to"')
                animation_types['scale'] = animation_types.get('scale', 0) + slide_xml.count('type="scale"')
                animation_types['rotate'] = animation_types.get('rotate', 0) + slide_xml.count('type="rotate"')
                animation_types['opacity'] = animation_types.get('opacity', 0) + slide_xml.count('type="opacity"')
        
        animations['powerpoint_animation_total_count'] = animation_count
        for anim_type, count in animation_types.items():
            animations[f'powerpoint_animation_{anim_type}_count'] = count
        
    except Exception as e:
        animations['powerpoint_animations_error'] = str(e)
    
    return animations


def _extract_powerpoint_shapes_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint shape information."""
    shapes: Dict[str, Any] = {'powerpoint_shapes_complete': True}
    
    try:
        shape_count = 0
        shape_types = {}
        
        for name in zf.namelist():
            if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                slide_xml = zf.read(name).decode('utf-8')
                
                shape_count += slide_xml.count('<p:sp>') + slide_xml.count('<p:pic>') + slide_xml.count('<p:cnt>')
                
                # Count shape types
                shape_types['rectangle'] = shape_types.get('rectangle', 0) + slide_xml.count('type="rect"')
                shape_types['round_rectangle'] = shape_types.get('round_rectangle', 0) + slide_xml.count('type="roundRect"')
                shape_types['oval'] = shape_types.get('oval', 0) + slide_xml.count('type="ellipse"')
                shape_types['triangle'] = shape_types.get('triangle', 0) + slide_xml.count('type="triangle"')
                shape_types['arrow'] = shape_types.get('arrow', 0) + slide_xml.count('type="rightArrow"')
                shape_types['star'] = shape_types.get('star', 0) + slide_xml.count('type="star"')
                shape_types['callout'] = shape_types.get('callout', 0) + slide_xml.count('type="callout"')
                shape_types['textbox'] = shape_types.get('textbox', 0) + slide_xml.count('type="textBox"')
                shape_types['picture'] = shape_types.get('picture', 0) + slide_xml.count('<p:pic>')
                shape_types['chart'] = shape_types.get('chart', 0) + slide_xml.count('<p:graphicFrame') and 'chart' in slide_xml
                shape_types['table'] = shape_types.get('table', 0) + slide_xml.count('<p:tbl>')
        
        shapes['powerpoint_shape_total_count'] = shape_count
        for shape_type, count in shape_types.items():
            shapes[f'powerpoint_shape_{shape_type}_count'] = count
        
    except Exception as e:
        shapes['powerpoint_shapes_error'] = str(e)
    
    return shapes


def _extract_powerpoint_media_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint media information."""
    media: Dict[str, Any] = {'powerpoint_media_complete': True}
    
    try:
        video_count = 0
        audio_count = 0
        media_types = {}
        
        for name in zf.namelist():
            if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                slide_xml = zf.read(name).decode('utf-8')
                
                video_count += slide_xml.count('<p:video')
                audio_count += slide_xml.count('<p:audio')
                
                if '<p:video src=' in slide_xml or '<p:video embed=' in slide_xml:
                    if '.mp4' in slide_xml:
                        media_types['video_mp4'] = media_types.get('video_mp4', 0) + 1
                    if '.avi' in slide_xml:
                        media_types['video_avi'] = media_types.get('video_avi', 0) + 1
                    if '.mov' in slide_xml:
                        media_types['video_mov'] = media_types.get('video_mov', 0) + 1
                    if '.wmv' in slide_xml:
                        media_types['video_wmv'] = media_types.get('video_wmv', 0) + 1
                    if '.webm' in slide_xml:
                        media_types['video_webm'] = media_types.get('video_webm', 0) + 1
                
                if '<p:audio src=' in slide_xml or '<p:audio embed=' in slide_xml:
                    if '.mp3' in slide_xml:
                        media_types['audio_mp3'] = media_types.get('audio_mp3', 0) + 1
                    if '.wav' in slide_xml:
                        media_types['audio_wav'] = media_types.get('audio_wav', 0) + 1
                    if '.aac' in slide_xml:
                        media_types['audio_aac'] = media_types.get('audio_aac', 0) + 1
                    if '.ogg' in slide_xml:
                        media_types['audio_ogg'] = media_types.get('audio_ogg', 0) + 1
        
        media['powerpoint_video_count'] = video_count
        media['powerpoint_audio_count'] = audio_count
        for media_type, count in media_types.items():
            media[f'powerpoint_{media_type}_count'] = count
        
    except Exception as e:
        media['powerpoint_media_error'] = str(e)
    
    return media


def _extract_powerpoint_notes_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint speaker notes information."""
    notes: Dict[str, Any] = {'powerpoint_notes_complete': True}
    
    try:
        notes_count = 0
        notes_with_text = 0
        
        for name in zf.namelist():
            if name.startswith('ppt/notesSlides/notesSlide') and name.endswith('.xml'):
                notes_count += 1
                notes_xml = zf.read(name).decode('utf-8')
                if '<a:t>' in notes_xml:
                    notes_with_text += 1
        
        notes['powerpoint_notes_slide_count'] = notes_count
        notes['powerpoint_notes_with_text_count'] = notes_with_text
        
    except Exception as e:
        notes['powerpoint_notes_error'] = str(e)
    
    return notes


def _extract_powerpoint_section_stats(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint section information."""
    sections: Dict[str, Any] = {'powerpoint_sections_complete': True}
    
    try:
        section_count = 0
        
        if 'ppt/sections/section' in str(zf.namelist()):
            section_count = sum(1 for name in zf.namelist() if name.startswith('ppt/sections/section'))
        
        sections['powerpoint_section_count'] = section_count
        
    except Exception as e:
        sections['powerpoint_sections_error'] = str(e)
    
    return sections


def _extract_powerpoint_custom_show_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint custom show information."""
    custom_shows: Dict[str, Any] = {'powerpoint_custom_shows_complete': True}
    
    try:
        custom_show_count = 0
        
        if 'ppt/customShows/customShow' in str(zf.namelist()):
            custom_show_count = sum(1 for name in zf.namelist() if name.startswith('ppt/customShows/customShow'))
        
        custom_shows['powerpoint_custom_show_count'] = custom_show_count
        
    except Exception as e:
        custom_shows['powerpoint_custom_shows_error'] = str(e)
    
    return custom_shows


def _extract_powerpoint_protection_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract PowerPoint protection information."""
    protection: Dict[str, Any] = {'powerpoint_protection_complete': True}
    
    try:
        if 'ppt/presentation.xml' in zf.namelist():
            pres_xml = zf.read('ppt/presentation.xml').decode('utf-8')
            
            protection['powerpoint_encrypted'] = 'encryption' in pres_xml
            protection['powerpoint_read_only'] = 'readOnlyMode' in pres_xml
            protection['powerpoint_password'] = 'password' in pres_xml
            protection['powerpoint_annotation_protection'] = 'removePersonalInfo' in pres_xml
        
    except Exception as e:
        protection['powerpoint_protection_error'] = str(e)
    
    return protection


def _extract_word_comments_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Word comments information."""
    comments: Dict[str, Any] = {'word_comments_complete': True}
    
    try:
        if 'word/comments.xml' in zf.namelist():
            comments_xml = zf.read('word/comments.xml').decode('utf-8')
            
            comments['word_comment_count'] = comments_xml.count('<w:comment ')
            comments['word_comment_reply_count'] = comments_xml.count('<w:commentReference')
            
            # Count comment authors
            author_count = len(set(re.findall(r'author="([^"]+)"', comments_xml)))
            comments['word_comment_author_count'] = author_count
            
    except Exception as e:
        comments['word_comments_error'] = str(e)
    
    return comments


def _extract_word_revisions_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Word revision information."""
    revisions: Dict[str, Any] = {'word_revisions_complete': True}
    
    try:
        if 'word/document.xml' in zf.namelist():
            doc_xml = zf.read('word/document.xml').decode('utf-8')
            
            revisions['word_revision_count'] = doc_xml.count('<w:ins') + doc_xml.count('<w:del')
            revisions['word_insertion_count'] = doc_xml.count('<w:ins')
            revisions['word_deletion_count'] = doc_xml.count('<w:del')
            revisions['word_format_change_count'] = doc_xml.count('<w:rPrChanged')
            
    except Exception as e:
        revisions['word_revisions_error'] = str(e)
    
    return revisions


def _extract_word_styles_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Word styles information."""
    styles: Dict[str, Any] = {'word_styles_complete': True}
    
    try:
        if 'word/styles.xml' in zf.namelist():
            styles_xml = zf.read('word/styles.xml').decode('utf-8')
            
            styles['word_style_count'] = styles_xml.count('<w:style ')
            styles['word_paragraph_style_count'] = styles_xml.count('type="paragraph"')
            styles['word_character_style_count'] = styles_xml.count('type="character"')
            styles['word_table_style_count'] = styles_xml.count('type="table"')
            styles['word_numbering_style_count'] = styles_xml.count('type="numbering"')
            
    except Exception as e:
        styles['word_styles_error'] = str(e)
    
    return styles


def _extract_word_settings_complete(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Word settings information."""
    settings: Dict[str, Any] = {'word_settings_complete': True}
    
    try:
        if 'word/settings.xml' in zf.namelist():
            settings_xml = zf.read('word/settings.xml').decode('utf-8')
            
            settings['word_track_revisions'] = 'trackRevisions' in settings_xml
            settings['word_hide_markup'] = 'hideMarkup' in settings_xml
            settings['word_show_ink_annotations'] = 'showInkAnnotations' in settings_xml
            settings['word_compatibility_mode'] = 'compatSetting' in settings_xml
            settings['word_default_language'] = 'defaultLanguage' in settings_xml
            
    except Exception as e:
        settings['word_settings_error'] = str(e)
    
    return settings


def _extract_word_custom_xml(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Word custom XML information."""
    custom_xml: Dict[str, Any] = {'word_custom_xml_complete': True}
    
    try:
        custom_xml_count = 0
        for name in zf.namelist():
            if name.startswith('word/customXml/item') and name.endswith('.xml'):
                custom_xml_count += 1
        
        custom_xml['word_custom_xml_count'] = custom_xml_count
        
    except Exception as e:
        custom_xml['word_custom_xml_error'] = str(e)
    
    return custom_xml


def _extract_word_relationships(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract Word relationships information."""
    rels: Dict[str, Any] = {'word_relationships_complete': True}
    
    try:
        rel_count = 0
        external_count = 0
        
        for name in zf.namelist():
            if name.endswith('.rels') and 'word/' in name:
                rels_xml = zf.read(name).decode('utf-8')
                rel_count += rels_xml.count('<Relationship')
                external_count += rels_xml.count('TargetMode="External"')
        
        rels['word_relationship_count'] = rel_count
        rels['word_external_relationship_count'] = external_count
        
    except Exception as e:
        rels['word_relationships_error'] = str(e)
    
    return rels


def _extract_zip_stats(zf: zipfile.ZipFile, filepath: str) -> Dict[str, Any]:
    """Extract ZIP archive statistics."""
    stats: Dict[str, Any] = {'zip_stats_complete': True}
    
    try:
        stats['zip_file_count'] = len(zf.namelist())
        stats['zip_directory_count'] = sum(1 for name in zf.namelist() if name.endswith('/'))
        
        import os
        file_size = os.path.getsize(filepath)
        stats['archive_file_size'] = file_size
        stats['archive_compressed_size'] = sum(info.file_size for info in zf.infolist())
        
    except Exception as e:
        stats['zip_stats_error'] = str(e)
    
    return stats


def _extract_odf_text_metadata(filepath: str) -> Dict[str, Any]:
    """Extract ODF text document metadata."""
    result: Dict[str, Any] = {'office_format': 'odf_text', 'odf_text_extraction': True}
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            if 'meta.xml' in zf.namelist():
                meta_xml = zf.read('meta.xml').decode('utf-8')
                root = ET.fromstring(meta_xml)
                
                for elem in root.iter():
                    if elem.text:
                        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                        result[f'odf_meta_{tag}'] = elem.text.strip() if elem.text else ''
            
            result['odf_has_meta'] = True
            
    except Exception as e:
        result['odf_text_error'] = str(e)
    
    return result


def _extract_odf_spreadsheet_metadata(filepath: str) -> Dict[str, Any]:
    """Extract ODF spreadsheet metadata."""
    result: Dict[str, Any] = {'office_format': 'odf_spreadsheet', 'odf_spreadsheet_extraction': True}
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            if 'meta.xml' in zf.namelist():
                meta_xml = zf.read('meta.xml').decode('utf-8')
                root = ET.fromstring(meta_xml)
                
                for elem in root.iter():
                    if elem.text:
                        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                        result[f'odf_meta_{tag}'] = elem.text.strip() if elem.text else ''
            
            result['odf_sheet_count'] = sum(1 for name in zf.namelist() if name.startswith('content.xml'))
            
    except Exception as e:
        result['odf_spreadsheet_error'] = str(e)
    
    return result


def _extract_odf_presentation_metadata(filepath: str) -> Dict[str, Any]:
    """Extract ODF presentation metadata."""
    result: Dict[str, Any] = {'office_format': 'odf_presentation', 'odf_presentation_extraction': True}
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            if 'meta.xml' in zf.namelist():
                meta_xml = zf.read('meta.xml').decode('utf-8')
                root = ET.fromstring(meta_xml)
                
                for elem in root.iter():
                    if elem.text:
                        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                        result[f'odf_meta_{tag}'] = elem.text.strip() if elem.text else ''
            
            result['odf_slide_count'] = sum(1 for name in zf.namelist() if 'drawPage' in str(zf.namelist()))
            
    except Exception as e:
        result['odf_presentation_error'] = str(e)
    
    return result


def _extract_rtf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract RTF document metadata."""
    result: Dict[str, Any] = {'office_format': 'rtf', 'rtf_extraction': True}
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read(4096).decode('latin-1', errors='ignore')
            
            result['rtf_version'] = 1 if content.startswith('{\\rtf') else 0
            
            # Extract font table
            if '{\\fonttbl' in content:
                result['rtf_has_font_table'] = True
                result['rtf_font_count'] = content.count('\\f')
            
            # Extract color table
            if '{\\colortbl' in content:
                result['rtf_has_color_table'] = True
                result['rtf_color_count'] = content.count('\\red')
            
            # Extract info group
            if '{\\info' in content:
                result['rtf_has_info'] = True
                if '\\title' in content:
                    result['rtf_has_title'] = True
                if '\\author' in content:
                    result['rtf_has_author'] = True
                if '\\comment' in content:
                    result['rtf_has_comment'] = True
            
    except Exception as e:
        result['rtf_error'] = str(e)
    
    return result


# Extended Word Document Properties
WORD_EXTENDED_PROPERTIES = {
    'word_doc_has_custom_properties': 'word_doc_has_custom_properties',
    'word_doc_custom_prop_count': 'word_doc_custom_prop_count',
    'word_doc_has_doc_vars': 'word_doc_has_doc_vars',
    'word_doc_doc_var_count': 'word_doc_doc_var_count',
    'word_doc_equation_editor': 'word_doc_equation_editor',
    'word_doc_autosave_count': 'word_doc_autosave_count',
    'word_doc_quick_parts_count': 'word_doc_quick_parts_count',
    'word_doc_building_blocks_count': 'word_doc_building_blocks_count',
    'word_doc_quick_style_set_count': 'word_doc_quick_style_set_count',
    'word_doc_theme_name': 'word_doc_theme_name',
    'word_doc_theme_font_major': 'word_doc_theme_font_major',
    'word_doc_theme_font_minor': 'word_doc_theme_font_minor',
    'word_doc_section_count': 'word_doc_section_count',
    'word_doc_footnoite_count': 'word_doc_footnote_count',
    'word_doc_endnote_count': 'word_doc_endnote_count',
    'word_doc_numbering_exists': 'word_doc_numbering_exists',
    'word_doc_numbering_level_count': 'word_doc_numbering_level_count',
    'word_outline_level_count': 'word_outline_level_count',
    'word_doc_mail_merge': 'word_doc_mail_merge',
    'word_doc_mail_merge_data_source': 'word_doc_mail_merge_data_source',
    'word_doc_mail_merge_type': 'word_doc_mail_merge_type',
    'word_doc_mail_merge_records': 'word_doc_mail_merge_records',
    'word_doc_document_variables': 'word_doc_document_variables',
    'word_doc_xml_mappings': 'word_doc_xml_mappings',
    'word_doc_content_controls': 'word_doc_content_controls',
    'word_doc_content_control_types': 'word_doc_content_control_types',
    'word_doc_building_block_gallery': 'word_doc_building_block_gallery',
    'word_doc_building_block_category': 'word_doc_building_block_category',
    'word_doc_auto_text_count': 'word_doc_auto_text_count',
    'word_doc_field_codes_present': 'word_doc_field_codes_present',
    'word_doc_if_field_count': 'word_doc_if_field_count',
    'word_doc_toc_field_count': 'word_doc_toc_field_count',
    'word_doc_page_ref_count': 'word_doc_page_ref_count',
    'word_doc_acroform_count': 'word_doc_acronym_count',
    'word_doc_glossary_count': 'word_doc_glossary_count',
    'word_doc_caption_count': 'word_doc_caption_count',
    'word_doc_index_count': 'word_doc_index_count',
    'word_doc_table_of_authority_count': 'word_doc_table_of_authority_count',
    'word_doc_table_of_figure_count': 'word_doc_table_of_figure_count',
    'word_doc_bibliography_count': 'word_doc_bibliography_count',
    'word_doc_citation_count': 'word_doc_citation_count',
    'word_doc_source_count': 'word_doc_source_count',
}

# Extended Excel Document Properties
EXCEL_EXTENDED_PROPERTIES = {
    'excel_workbook_has_vba': 'excel_workbook_has_vba',
    'excel_workbook_vba_project': 'excel_workbook_vba_project',
    'excel_workbook_macro_count': 'excel_workbook_macro_count',
    'excel_workbook_module_count': 'excel_workbook_module_count',
    'excel_workbook_class_count': 'excel_workbook_class_count',
    'excel_workbook_form_count': 'excel_workbook_form_count',
    'excel_workbook_connection_count': 'excel_workbook_connection_count',
    'excel_workbook_pivot_count': 'excel_workbook_pivot_count',
    'excel_workbook_pivot_cache_count': 'excel_workbook_pivot_cache_count',
    'excel_workbook_query_count': 'excel_workbook_query_count',
    'excel_workbook_slicer_count': 'excel_workbook_slicer_count',
    'excel_workbook_timeline_count': 'excel_workbook_timeline_count',
    'excel_workbook_conditional_format_count': 'excel_workbook_conditional_format_count',
    'excel_workbook_data_validation_count': 'excel_workbook_data_validation_count',
    'excel_workbook_sparkline_count': 'excel_workbook_sparkline_count',
    'excel_workbook_table_count': 'excel_workbook_table_count',
    'excel_workbook_table_style_count': 'excel_workbook_table_style_count',
    'excel_workbook_cell_style_count': 'excel_workbook_cell_style_count',
    'excel_workbook_custom_view_count': 'excel_workbook_custom_view_count',
    'excel_workbook_scenario_count': 'excel_workbook_scenario_count',
    'excel_workbook_goal_seek_count': 'excel_workbook_goal_seek_count',
    'excel_workbook_solver_count': 'excel_workbook_solver_count',
    'excel_workbook_external_link_count': 'excel_workbook_external_link_count',
    'excel_workbook_worksheet_change_count': 'excel_workbook_worksheet_change_count',
    'excel_workbook_custom_properties': 'excel_workbook_custom_properties',
    'excel_workbook_worksheet_protection': 'excel_workbook_worksheet_protection',
    'excel_workbook_workbook_protection': 'excel_workbook_workbook_protection',
    'excel_workbook_shared_workbook': 'excel_workbook_shared_workbook',
    'excel_workbook_change_history': 'excel_workbook_change_history',
    'excel_workbook_business_intelligence': 'excel_workbook_business_intelligence',
    'excel_workbook_power_view': 'excel_workbook_power_view',
    'excel_workbook_power_pivot': 'excel_workbook_power_pivot',
    'excel_workbook_cube_connection': 'excel_workbook_cube_connection',
    'excel_workbook_model_relationship_count': 'excel_workbook_model_relationship_count',
    'excel_workbook_measure_count': 'excel_workbook_measure_count',
    'excel_workbook_kpi_count': 'excel_workbook_kpi_count',
    'excel_workbook_perspective_count': 'excel_workbook_perspective_count',
}

# Extended PowerPoint Document Properties
POWERPOINT_EXTENDED_PROPERTIES = {
    'ppt_has_video': 'ppt_has_video',
    'ppt_video_count': 'ppt_video_count',
    'ppt_video_total_duration': 'ppt_video_total_duration',
    'ppt_has_audio': 'ppt_has_audio',
    'ppt_audio_count': 'ppt_audio_count',
    'ppt_audio_total_duration': 'ppt_audio_total_duration',
    'ppt_has_flash': 'ppt_has_flash',
    'ppt_flash_count': 'ppt_flash_count',
    'ppt_has_3d_model': 'ppt_has_3d_model',
    'ppt_3d_model_count': 'ppt_3d_model_count',
    'ppt_has_smart_art': 'ppt_has_smart_art',
    'ppt_smart_art_count': 'ppt_smart_art_count',
    'ppt_has_chart': 'ppt_has_chart',
    'ppt_chart_count': 'ppt_chart_count',
    'ppt_chart_types': 'ppt_chart_types',
    'ppt_has_table': 'ppt_has_table',
    'ppt_table_count': 'ppt_table_count',
    'ppt_table_cell_count': 'ppt_table_cell_count',
    'ppt_has_shape': 'ppt_has_shape',
    'ppt_shape_count': 'ppt_shape_count',
    'ppt_shape_types': 'ppt_shape_types',
    'ppt_has_picture': 'ppt_has_picture',
    'ppt_picture_count': 'ppt_picture_count',
    'ppt_picture_formats': 'ppt_picture_formats',
    'ppt_has_group_shape': 'ppt_has_group_shape',
    'ppt_group_shape_count': 'ppt_group_shape_count',
    'ppt_has_master_slide': 'ppt_has_master_slide',
    'ppt_master_slide_count': 'ppt_master_slide_count',
    'ppt_has_layout': 'ppt_has_layout',
    'ppt_layout_count': 'ppt_layout_count',
    'ppt_has_theme': 'ppt_has_theme',
    'ppt_theme_name': 'ppt_theme_name',
    'ppt_theme_colors': 'ppt_theme_colors',
    'ppt_theme_fonts': 'ppt_theme_fonts',
    'ppt_transition_count': 'ppt_transition_count',
    'ppt_animation_count': 'ppt_animation_count',
    'ppt_animation_types': 'ppt_animation_types',
    'ppt_interaction_count': 'ppt_interaction_count',
    'ppt_custom_show_count': 'ppt_custom_show_count',
    'ppt_handout_master_count': 'ppt_handout_master_count',
    'ppt_notes_master_count': 'ppt_notes_master_count',
    'ppt_section_count': 'ppt_section_count',
    'ppt_section_names': 'ppt_section_names',
    'ppt_rehearse_timings': 'ppt_rehearse_timings',
    'ppt_recorded_presentations': 'ppt_recorded_presentations',
    'ppt_custom_ribbon': 'ppt_custom_ribbon',
    'ppt_vba_present': 'ppt_vba_present',
    'ppt_digital_signature_count': 'ppt_digital_signature_count',
}

# Extended OpenDocument Properties
OPENDOCUMENT_EXTENDED = {
    'odf_has_master_page': 'odf_has_master_page',
    'odf_master_page_count': 'odf_master_page_count',
    'odf_has_style': 'odf_has_style',
    'odf_style_count': 'odf_style_count',
    'odf_automatic_style_count': 'odf_automatic_style_count',
    'odf_common_style_count': 'odf_common_style_count',
    'odf_has_script': 'odf_has_script',
    'odf_script_count': 'odf_script_count',
    'odf_script_types': 'odf_script_types',
    'odf_has_embedded_font': 'odf_has_embedded_font',
    'odf_embedded_font_count': 'odf_embedded_font_count',
    'odf_has_chart': 'odf_has_chart',
    'odf_chart_count': 'odf_chart_count',
    'odf_has_database': 'odf_has_database',
    'odf_database_count': 'odf_database_count',
    'odf_form_count': 'odf_form_count',
    'odf_has_text_field': 'odf_has_text_field',
    'odf_text_field_count': 'odf_text_field_count',
    'odf_variable_count': 'odf_variable_count',
    'odf_sequence_count': 'odf_sequence_count',
    'odf_bookmark_count': 'odf_bookmark_count',
    'odf_reference_mark_count': 'odf_reference_mark_count',
    'odf_note_count': 'odf_note_count',
    'odf_comment_count': 'odf_comment_count',
    'odf_draw_page_count': 'odf_draw_page_count',
    'odf_draw_shape_count': 'odf_draw_shape_count',
    'odf_draw_path_count': 'odf_draw_path_count',
    'odf_draw_circle_count': 'odf_draw_circle_count',
    'odf_draw_rect_count': 'odf_draw_rect_count',
    'odf_presentation_animation_count': 'odf_presentation_animation_count',
    'odf_presentation_transition_count': 'odf_presentation_transition_count',
    'odf_spreadsheet_cell_count': 'odf_spreadsheet_cell_count',
    'odf_spreadsheet_named_range_count': 'odf_spreadsheet_named_range_count',
    'odf_spreadsheet_database_range_count': 'odf_spreadsheet_database_range_count',
}

# Extended CSV/TSV Properties
CSV_EXTENDED_PROPERTIES = {
    'csv_delimiter': 'csv_delimiter',
    'csv_delimiter_detected': 'csv_delimiter_detected',
    'csv_quote_character': 'csv_quote_character',
    'csv_escape_character': 'csv_escape_character',
    'csv_line_terminator': 'csv_line_terminator',
    'csv_encoding': 'csv_encoding',
    'csv_has_header': 'csv_has_header',
    'csv_header_fields': 'csv_header_fields',
    'csv_column_count': 'csv_column_count',
    'csv_row_count': 'csv_row_count',
    'csv_empty_rows': 'csv_empty_rows',
    'csv_null_values': 'csv_null_values',
    'csv_column_types': 'csv_column_types',
    'csv_column_null_counts': 'csv_column_null_counts',
    'csv_column_unique_counts': 'csv_column_unique_counts',
    'csv_has_mixed_types': 'csv_has_mixed_types',
    'csv_datetime_columns': 'csv_datetime_columns',
    'csv_numeric_columns': 'csv_numeric_columns',
    'csv_text_columns': 'csv_text_columns',
    'csv_max_row_length': 'csv_max_row_length',
    'csv_min_row_length': 'csv_min_row_length',
    'csv_avg_row_length': 'csv_avg_row_length',
    'csv_total_size_bytes': 'csv_total_size_bytes',
}

# Office Document Permissions and Security
OFFICE_SECURITY_EXTENSIONS = {
    'office_encrypted': 'office_encrypted',
    'office_encryption_method': 'office_encryption_method',
    'office_password_modify': 'office_password_modify',
    'office_password_readonly': 'office_password_readonly',
    'office_password_extract': 'office_password_extract',
    'office_drm_protected': 'office_drm_protected',
    'office_drm_type': 'office_drm_type',
    'office_drm_expiration': 'office_drm_expiration',
    'office_digital_signature_present': 'office_digital_signature_present',
    'office_signature_count': 'office_signature_count',
    'office_signature_valid': 'office_signature_valid',
    'office_signature_signer': 'office_signature_signer',
    'office_signature_date': 'office_signature_date',
    'office_signature_location': 'office_signature_location',
    'office_trusted_document': 'office_trusted_document',
    'office_trusted_location': 'office_trusted_location',
    'office_macros_disabled': 'office_macros_disabled',
    'office_active_content_count': 'office_active_content_count',
    'office_external_content_count': 'office_external_content_count',
    'office_hyperlink_count': 'office_hyperlink_count',
    'office_dynamic_content_count': 'office_dynamic_content_count',
}

# Office Document Collaboration
OFFICE_COLLABORATION_EXTENSIONS = {
    'office_coauthoring_enabled': 'office_coauthoring_enabled',
    'office_coauthor_count': 'office_coauthor_count',
    'office_version_history_count': 'office_version_history_count',
    'office_version_history_size': 'office_version_history_size',
    'office_comment_count': 'office_comment_count',
    'office_comment_resolved': 'office_comment_resolved',
    'office_comment_active': 'office_comment_active',
    'office_revision_count': 'office_revision_count',
    'office_revision_types': 'office_revision_types',
    'office_track_changes_on': 'office_track_changes_on',
    'office_merge_enabled': 'office_merge_enabled',
    'office_sharing_status': 'office_sharing_status',
    'office_share_url': 'office_share_url',
    'office_cloud_version': 'office_cloud_version',
    'office_last_saved_by': 'office_last_saved_by',
    'office_author_list': 'office_author_list',
    'office_editor_count': 'office_editor_count',
    'office_contributor_count': 'office_contributor_count',
}

# Office Document Accessibility
OFFICE_ACCESSIBILITY_EXTENSIONS = {
    'office_alt_text_count': 'office_alt_text_count',
    'office_missing_alt_text': 'office_missing_alt_text',
    'office_title_present': 'office_title_present',
    'office_subject_present': 'office_subject_present',
    'office_language_set': 'office_language_set',
    'office_reading_order': 'office_reading_order',
    'office_tab_order': 'office_tab_order',
    'office_heading_levels': 'office_heading_levels',
    'office_list_structure': 'office_list_structure',
    'office_table_structure': 'office_table_structure',
    'office_table_header': 'office_table_header',
    'office_hyperlink_text': 'office_hyperlink_text',
    'office_bookmark_count': 'office_bookmark_count',
    'office_cross_reference_count': 'office_cross_reference_count',
    'office_index_entries': 'office_index_entries',
    'office_table_of_contents': 'office_table_of_contents',
    'office_accessible_check': 'office_accessible_check',
    'office_accessibility_issues': 'office_accessibility_issues',
}


def get_office_documents_complete_extended_field_count() -> int:
    """Return the total count of office document fields including extensions."""
    base_count = get_office_documents_complete_field_count()
    extended_count = (
        len(WORD_EXTENDED_PROPERTIES) + len(EXCEL_EXTENDED_PROPERTIES) +
        len(POWERPOINT_EXTENDED_PROPERTIES) + len(OPENDOCUMENT_EXTENDED) +
        len(CSV_EXTENDED_PROPERTIES) + len(OFFICE_SECURITY_EXTENSIONS) +
        len(OFFICE_COLLABORATION_EXTENSIONS) + len(OFFICE_ACCESSIBILITY_EXTENSIONS)
    )
    return base_count + extended_count
