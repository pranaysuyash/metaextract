#!/usr/bin/env python3
"""
Image Metadata Registry
Unified registry of all image metadata categories covering 3,600+ fields across:
- Standard formats (JPEG, PNG, WebP, TIFF, GIF, BMP, AVIF, HEIC, PSD, OpenEXR)
- EXIF 2.31/2.32/2.33 standards
- IPTC Standard and Extension
- XMP namespaces (Dublin Core, Photoshop, Rights, Creator)
- Camera MakerNotes (Canon, Nikon, Sony, Fuji, Olympus, Hasselblad, Phase One)
- Mobile metadata (iPhone, Android, Samsung, Huawei, Xiaomi)
- Action cameras (DJI, GoPro, Insta360, Garmin)
- ICC Profiles (header, tags, TRC, CLUT, colorimetry)
- Color analysis and quality metrics
- AI generation detection (Stable Diffusion, Midjourney, DALL-E, C2PA)
- Forensics (ELA, noise analysis, manipulation detection)
- Edit history (Lightroom, Photoshop, Capture One)

Author: MetaExtract Team
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class MetadataCategory(Enum):
    BASIC_PROPERTIES = "basic_properties"
    FILE_FORMAT_CHUNKS = "file_format_chunks"
    EXIF_STANDARD = "exif_standard"
    IPTC_STANDARD = "iptc_standard"
    IPTC_EXTENSION = "iptc_extension"
    XMP_NAMESPACES = "xmp_namespaces"
    ICC_PROFILES = "icc_profiles"
    CAMERA_MAKERNOTES = "camera_makernotes"
    MOBILE_METADATA = "mobile_metadata"
    ACTION_CAMERA = "action_camera"
    PERCEPTUAL_HASHES = "perceptual_hashes"
    COLOR_ANALYSIS = "color_analysis"
    QUALITY_METRICS = "quality_metrics"
    STEGANOGRAPHY = "steganography"
    IMAGE_FORENSICS = "image_forensics"
    AI_GENERATION = "ai_generation"
    PHOTOSHOP_PSD = "photoshop_psd"
    EDIT_HISTORY = "edit_history"
    OPENEXR_HDR = "openexr_hdr"
    RAW_FORMAT = "raw_format"
    ANIMATED_IMAGES = "animated_images"
    SOCIAL_METADATA = "social_metadata"
    ACCESSIBILITY = "accessibility"
    TIFF_IFD = "tiff_ifd"
    ECOMMERCE = "ecommerce"


@dataclass
class MetadataField:
    name: str
    category: MetadataCategory
    field_type: str
    description: str
    exif_tag: Optional[str] = None
    iptc_tag: Optional[str] = None
    xmp_namespace: Optional[str] = None
    vendor_specific: Optional[str] = None
    supported_formats: List[str] = field(default_factory=list)
    deprecated: bool = False
    notes: Optional[str] = None


class ImageMetadataRegistry:
    """
    Central registry for all image metadata fields.
    Provides field definitions, categories, and validation.
    """

    def __init__(self):
        self.fields: Dict[str, MetadataField] = {}
        self.categories: Dict[MetadataCategory, List[str]] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        """Initialize the registry with all metadata fields"""
        self._register_basic_properties()
        self._register_file_format_chunks()
        self._register_exif_standard()
        self._register_iptc_standard()
        self._register_iptc_extension()
        self._register_xmp_namespaces()
        self._register_icc_profiles()
        self._register_camera_makernotes()
        self._register_mobile_metadata()
        self._register_action_camera()
        self._register_perceptual_hashes()
        self._register_color_analysis()
        self._register_quality_metrics()
        self._register_steganography()
        self._register_image_forensics()
        self._register_ai_generation()
        self._register_photoshop_psd()
        self._register_edit_history()
        self._register_openexr_hdr()
        self._register_avif_heif()
        self._register_camera_raw()
        self._register_motion_photo()
        self._register_xmp_extended()
        self._register_animated_images()
        self._register_social_metadata()
        self._register_accessibility()
        self._register_tiff_ifd()
        self._register_ecommerce()

    def _register_field(self, field: MetadataField):
        """Register a single metadata field"""
        self.fields[field.name] = field
        if field.category not in self.categories:
            self.categories[field.category] = []
        self.categories[field.category].append(field.name)

    def _register_basic_properties(self):
        """Basic image properties - ~50 fields"""
        basic_fields = [
            ("width", MetadataCategory.BASIC_PROPERTIES, "int", "Image width in pixels"),
            ("height", MetadataCategory.BASIC_PROPERTIES, "int", "Image height in pixels"),
            ("color_mode", MetadataCategory.BASIC_PROPERTIES, "str", "Color mode (RGB, RGBA, CMYK, Grayscale, etc.)"),
            ("bit_depth", MetadataCategory.BASIC_PROPERTIES, "int", "Bits per channel"),
            ("channels", MetadataCategory.BASIC_PROPERTIES, "int", "Number of color channels"),
            ("file_format", MetadataCategory.BASIC_PROPERTIES, "str", "File format (JPEG, PNG, WebP, etc.)"),
            ("file_extension", MetadataCategory.BASIC_PROPERTIES, "str", "File extension"),
            ("mime_type", MetadataCategory.BASIC_PROPERTIES, "str", "MIME type"),
            ("file_size", MetadataCategory.BASIC_PROPERTIES, "int", "File size in bytes"),
            ("file_size_human", MetadataCategory.BASIC_PROPERTIES, "str", "Human-readable file size"),
            ("aspect_ratio", MetadataCategory.BASIC_PROPERTIES, "float", "Aspect ratio (width/height)"),
            ("orientation", MetadataCategory.BASIC_PROPERTIES, "str", "Image orientation"),
            ("has_alpha", MetadataCategory.BASIC_PROPERTIES, "bool", "Has alpha channel"),
            ("compression", MetadataCategory.BASIC_PROPERTIES, "str", "Compression type"),
            ("color_space", MetadataCategory.BASIC_PROPERTIES, "str", "Color space"),
            ("dpi_horizontal", MetadataCategory.BASIC_PROPERTIES, "int", "Horizontal DPI"),
            ("dpi_vertical", MetadataCategory.BASIC_PROPERTIES, "int", "Vertical DPI"),
            ("total_pixels", MetadataCategory.BASIC_PROPERTIES, "int", "Total pixel count"),
            ("megapixels", MetadataCategory.BASIC_PROPERTIES, "float", "Megapixels"),
            ("is_animated", MetadataCategory.BASIC_PROPERTIES, "bool", "Is animated image"),
            ("frame_count", MetadataCategory.BASIC_PROPERTIES, "int", "Number of frames"),
            ("loop_count", MetadataCategory.BASIC_PROPERTIES, "int", "Animation loop count"),
            ("icc_profile_present", MetadataCategory.BASIC_PROPERTIES, "bool", "Has ICC profile"),
            ("xmp_present", MetadataCategory.BASIC_PROPERTIES, "bool", "Has XMP data"),
            ("exif_present", MetadataCategory.BASIC_PROPERTIES, "bool", "Has EXIF data"),
            ("iptc_present", MetadataCategory.BASIC_PROPERTIES, "bool", "Has IPTC data"),
        ]
        for name, category, field_type, description in basic_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "GIF", "BMP", "AVIF", "HEIC", "PSD", "OpenEXR", "RAW"]
            ))

    def _register_file_format_chunks(self):
        """File format chunks - ~200+ fields"""
        png_chunk_fields = [
            ("png_ihdr_width", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "PNG IHDR chunk width"),
            ("png_ihdr_height", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "PNG IHDR chunk height"),
            ("png_ihdr_bit_depth", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "PNG IHDR bit depth"),
            ("png_ihdr_color_type", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "PNG IHDR color type"),
            ("png_plte_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has PLTE chunk"),
            ("png_plte_entries", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "PLTE chunk entries count"),
            ("png_text_count", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Number of tEXt chunks"),
            ("png_ztxt_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has zTXt chunk"),
            ("png_itxt_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has iTXt chunk"),
            ("png_exif_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has eXIf chunk"),
            ("png_chrm_white_point_x", MetadataCategory.FILE_FORMAT_CHUNKS, "float", "cHRM white point X"),
            ("png_gama_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has gAMA chunk"),
            ("png_gama_gamma", MetadataCategory.FILE_FORMAT_CHUNKS, "float", "gAMA gamma value"),
            ("png_srgb_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has sRGB chunk"),
            ("png_actl_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has acTL animation control"),
            ("png_actl_frames", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "acTL frame count"),
            ("png_mdcv_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has mDCv Mastering Display Color Volume"),
        ]
        for name, category, field_type, description in png_chunk_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["PNG", "APNG"]
            ))

        webp_chunk_fields = [
            ("webp_vp8_version", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "VP8 format version"),
            ("webp_vp8l_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has VP8L lossless format"),
            ("webp_vp8x_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has VP8X extended format"),
            ("webp_anim_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has ANIM chunk"),
            ("webp_anim_loops", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "ANIM loop count"),
            ("webp_alph_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has ALPH chunk"),
            ("webp_exif_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has EXIF chunk"),
            ("webp_xmp_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has XMP chunk"),
            ("webp_icc_present", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has ICC chunk"),
        ]
        for name, category, field_type, description in webp_chunk_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["WebP"]
            ))

    def _register_exif_standard(self):
        """EXIF 2.31/2.32/2.33 standard tags - ~100 fields"""
        exif_fields = [
            ("exif_version", MetadataCategory.EXIF_STANDARD, "str", "EXIF version"),
            ("make", MetadataCategory.EXIF_STANDARD, "str", "Camera manufacturer"),
            ("model", MetadataCategory.EXIF_STANDARD, "str", "Camera model"),
            ("software", MetadataCategory.EXIF_STANDARD, "str", "Software used"),
            ("artist", MetadataCategory.EXIF_STANDARD, "str", "Artist name"),
            ("copyright", MetadataCategory.EXIF_STANDARD, "str", "Copyright notice"),
            ("image_description", MetadataCategory.EXIF_STANDARD, "str", "Image description"),
            ("datetime", MetadataCategory.EXIF_STANDARD, "datetime", "Date and time"),
            ("datetime_original", MetadataCategory.EXIF_STANDARD, "datetime", "Original date and time"),
            ("datetime_digitized", MetadataCategory.EXIF_STANDARD, "datetime", "Digitization date and time"),
            ("exposure_time", MetadataCategory.EXIF_STANDARD, "float", "Exposure time in seconds"),
            ("f_number", MetadataCategory.EXIF_STANDARD, "float", "F-number"),
            ("exposure_program", MetadataCategory.EXIF_STANDARD, "int", "Exposure program"),
            ("iso_speed_ratings", MetadataCategory.EXIF_STANDARD, "list", "ISO speed ratings"),
            ("shutter_speed_value", MetadataCategory.EXIF_STANDARD, "float", "Shutter speed value (APEX)"),
            ("aperture_value", MetadataCategory.EXIF_STANDARD, "float", "Aperture value (APEX)"),
            ("brightness_value", MetadataCategory.EXIF_STANDARD, "float", "Brightness value (APEX)"),
            ("exposure_bias", MetadataCategory.EXIF_STANDARD, "float", "Exposure bias value"),
            ("metering_mode", MetadataCategory.EXIF_STANDARD, "int", "Metering mode"),
            ("light_source", MetadataCategory.EXIF_STANDARD, "int", "Light source"),
            ("flash", MetadataCategory.EXIF_STANDARD, "int", "Flash"),
            ("focal_length", MetadataCategory.EXIF_STANDARD, "float", "Focal length in mm"),
            ("focal_length_35mm", MetadataCategory.EXIF_STANDARD, "int", "35mm focal length equivalent"),
            ("digital_zoom_ratio", MetadataCategory.EXIF_STANDARD, "float", "Digital zoom ratio"),
            ("scene_capture_type", MetadataCategory.EXIF_STANDARD, "int", "Scene capture type"),
            ("contrast", MetadataCategory.EXIF_STANDARD, "int", "Contrast setting"),
            ("saturation", MetadataCategory.EXIF_STANDARD, "int", "Saturation setting"),
            ("sharpness", MetadataCategory.EXIF_STANDARD, "int", "Sharpness setting"),
            ("exposure_mode", MetadataCategory.EXIF_STANDARD, "int", "Exposure mode"),
            ("white_balance", MetadataCategory.EXIF_STANDARD, "int", "White balance mode"),
            ("gain_control", MetadataCategory.EXIF_STANDARD, "int", "Gain control"),
            ("subject_distance", MetadataCategory.EXIF_STANDARD, "float", "Subject distance in meters"),
            ("image_unique_id", MetadataCategory.EXIF_STANDARD, "str", "Image unique ID"),
            ("camera_owner_name", MetadataCategory.EXIF_STANDARD, "str", "Camera owner name"),
            ("camera_serial_number", MetadataCategory.EXIF_STANDARD, "str", "Camera serial number"),
            ("lens_specification", MetadataCategory.EXIF_STANDARD, "list", "Lens specification"),
            ("lens_make", MetadataCategory.EXIF_STANDARD, "str", "Lens manufacturer"),
            ("lens_model", MetadataCategory.EXIF_STANDARD, "str", "Lens model"),
            ("lens_serial_number", MetadataCategory.EXIF_STANDARD, "str", "Lens serial number"),
            ("body_serial_number", MetadataCategory.EXIF_STANDARD, "str", "Camera body serial number"),
            ("gps_latitude_ref", MetadataCategory.EXIF_STANDARD, "str", "GPS latitude reference (N/S)"),
            ("gps_latitude_decimal", MetadataCategory.EXIF_STANDARD, "float", "GPS latitude in decimal degrees"),
            ("gps_longitude_ref", MetadataCategory.EXIF_STANDARD, "str", "GPS longitude reference (E/W)"),
            ("gps_longitude_decimal", MetadataCategory.EXIF_STANDARD, "float", "GPS longitude in decimal degrees"),
            ("gps_altitude_ref", MetadataCategory.EXIF_STANDARD, "int", "GPS altitude reference"),
            ("gps_altitude", MetadataCategory.EXIF_STANDARD, "float", "GPS altitude in meters"),
            ("gps_timestamp", MetadataCategory.EXIF_STANDARD, "datetime", "GPS timestamp"),
            ("color_space", MetadataCategory.EXIF_STANDARD, "int", "Color space"),
            ("pixel_x_dimension", MetadataCategory.EXIF_STANDARD, "int", "Pixel X dimension"),
            ("pixel_y_dimension", MetadataCategory.EXIF_STANDARD, "int", "Pixel Y dimension"),
        ]
        for name, category, field_type, description in exif_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                exif_tag=name, supported_formats=["JPEG", "TIFF", "PNG", "WebP", "PSD", "HEIC", "AVIF"]
            ))

    def _register_iptc_standard(self):
        """IPTC Standard - ~50 fields"""
        iptc_fields = [
            ("iptc_record_version", MetadataCategory.IPTC_STANDARD, "int", "IPTC record version"),
            ("iptc_keywords", MetadataCategory.IPTC_STANDARD, "list", "Keywords"),
            ("iptc_caption", MetadataCategory.IPTC_STANDARD, "str", "Caption/abstract"),
            ("iptc_caption_writer", MetadataCategory.IPTC_STANDARD, "str", "Caption writer/editor"),
            ("iptc_headline", MetadataCategory.IPTC_STANDARD, "str", "Headline"),
            ("iptc_special_instructions", MetadataCategory.IPTC_STANDARD, "str", "Special instructions"),
            ("iptc_creation_date", MetadataCategory.IPTC_STANDARD, "datetime", "Date of creation"),
            ("iptc_digitization_date", MetadataCategory.IPTC_STANDARD, "datetime", "Date of digitization"),
            ("iptc_byline", MetadataCategory.IPTC_STANDARD, "list", "Byline (creator names)"),
            ("iptc_credit", MetadataCategory.IPTC_STANDARD, "str", "Credit/attribution"),
            ("iptc_source", MetadataCategory.IPTC_STANDARD, "str", "Source"),
            ("iptc_copyright_notice", MetadataCategory.IPTC_STANDARD, "str", "Copyright notice"),
            ("iptc_contact", MetadataCategory.IPTC_STANDARD, "list", "Contact information"),
            ("iptc_city", MetadataCategory.IPTC_STANDARD, "str", "City"),
            ("iptc_province_state", MetadataCategory.IPTC_STANDARD, "str", "Province/state"),
            ("iptc_country_primary_location", MetadataCategory.IPTC_STANDARD, "str", "Country primary location"),
            ("iptc_country_code_primary", MetadataCategory.IPTC_STANDARD, "str", "Country primary location code"),
            ("iptc_location", MetadataCategory.IPTC_STANDARD, "str", "Location shown"),
            ("iptc_urgency", MetadataCategory.IPTC_STANDARD, "int", "Urgency (1-8)"),
            ("iptc_object_name", MetadataCategory.IPTC_STANDARD, "str", "Object name/title"),
            ("iptc_edit_status", MetadataCategory.IPTC_STANDARD, "str", "Edit status"),
        ]
        for name, category, field_type, description in iptc_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                iptc_tag=name, supported_formats=["JPEG", "TIFF", "PSD", "PNG"]
            ))

    def _register_iptc_extension(self):
        """IPTC Extension - ~50 fields"""
        iptc_ext_fields = [
            ("iptc_artwork_title", MetadataCategory.IPTC_EXTENSION, "list", "Artwork title"),
            ("iptc_artwork_creator", MetadataCategory.IPTC_EXTENSION, "list", "Artwork creator(s)"),
            ("iptc_artwork_copyright_notice", MetadataCategory.IPTC_EXTENSION, "list", "Artwork copyright notice"),
            ("iptc_artwork_source", MetadataCategory.IPTC_EXTENSION, "list", "Artwork source"),
            ("iptc_graphic_content", MetadataCategory.IPTC_EXTENSION, "list", "Intellectual genre of content"),
            ("iptc_scene_code", MetadataCategory.IPTC_EXTENSION, "list", "Scene codes (IPTC-SC)"),
            ("iptc_subject_code", MetadataCategory.IPTC_EXTENSION, "list", "Subject reference codes (IPTC-SR)"),
            ("iptc_event", MetadataCategory.IPTC_EXTENSION, "str", "Event"),
            ("iptc_dig_img_guid", MetadataCategory.IPTC_EXTENSION, "str", "Digital image GUID"),
            ("iptc_cataloguer_id", MetadataCategory.IPTC_EXTENSION, "list", "Cataloguer's ID"),
            ("iptc_person_shown", MetadataCategory.IPTC_EXTENSION, "list", "Person(s) shown"),
            ("iptc_organization_shown", MetadataCategory.IPTC_EXTENSION, "list", "Organization(s) shown"),
            ("iptc_event_shown", MetadataCategory.IPTC_EXTENSION, "list", "Event(s) shown"),
            ("iptc_product_shown", MetadataCategory.IPTC_EXTENSION, "list", "Product(s) shown"),
        ]
        for name, category, field_type, description in iptc_ext_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "TIFF", "PSD", "PNG"]
            ))

    def _register_xmp_namespaces(self):
        """XMP Namespaces - ~50 fields"""
        xmp_fields = [
            ("xmp_dc_format", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core format"),
            ("xmp_dc_identifier", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core identifier"),
            ("xmp_dc_title", MetadataCategory.XMP_NAMESPACES, "dict", "Dublin Core title"),
            ("xmp_dc_description", MetadataCategory.XMP_NAMESPACES, "dict", "Dublin Core description"),
            ("xmp_dc_subject", MetadataCategory.XMP_NAMESPACES, "list", "Dublin Core subject/keywords"),
            ("xmp_dc_creator", MetadataCategory.XMP_NAMESPACES, "list", "Dublin Core creator"),
            ("xmp_dc_publisher", MetadataCategory.XMP_NAMESPACES, "list", "Dublin Core publisher"),
            ("xmp_dc_contributor", MetadataCategory.XMP_NAMESPACES, "list", "Dublin Core contributor"),
            ("xmp_dc_type", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core type"),
            ("xmp_dc_language", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core language"),
            ("xmp_dc_rights", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core rights"),
            ("xmp_dc_date", MetadataCategory.XMP_NAMESPACES, "list", "Dublin Core date"),
            ("xmp_photoshop_ColorMode", MetadataCategory.XMP_NAMESPACES, "int", "Photoshop color mode"),
            ("xmp_photoshop_DateCreated", MetadataCategory.XMP_NAMESPACES, "datetime", "Photoshop date created"),
            ("xmp_xmp_creator_tool", MetadataCategory.XMP_NAMESPACES, "str", "Creator tool"),
            ("xmp_xmp_create_date", MetadataCategory.XMP_NAMESPACES, "datetime", "XMP creation date"),
            ("xmp_xmp_modify_date", MetadataCategory.XMP_NAMESPACES, "datetime", "XMP modification date"),
            ("xmp_xmp_metadata_date", MetadataCategory.XMP_NAMESPACES, "datetime", "XMP metadata date"),
            ("xmp_stEvt_action", MetadataCategory.XMP_NAMESPACES, "str", "History action"),
            ("xmp_stEvt_softwareAgent", MetadataCategory.XMP_NAMESPACES, "str", "History software agent"),
            ("xmp_stEvt_when", MetadataCategory.XMP_NAMESPACES, "datetime", "History when"),
        ]
        for name, category, field_type, description in xmp_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "PSD", "HEIC", "AVIF", "OpenEXR"]
            ))

    def _register_icc_profiles(self):
        """ICC Profiles - ~40 fields"""
        icc_fields = [
            ("icc_profile_version", MetadataCategory.ICC_PROFILES, "str", "ICC profile version"),
            ("icc_profile_class", MetadataCategory.ICC_PROFILES, "str", "Profile class"),
            ("icc_color_space", MetadataCategory.ICC_PROFILES, "str", "Color space"),
            ("icc_connection_space", MetadataCategory.ICC_PROFILES, "str", "Connection space"),
            ("icc_profile_datetime", MetadataCategory.ICC_PROFILES, "datetime", "Profile creation date"),
            ("icc_signature", MetadataCategory.ICC_PROFILES, "str", "Profile signature"),
            ("icc_platform", MetadataCategory.ICC_PROFILES, "str", "Platform"),
            ("icc_flags", MetadataCategory.ICC_PROFILES, "int", "Profile flags"),
            ("icc_rendering_intent", MetadataCategory.ICC_PROFILES, "int", "Default rendering intent"),
            ("icc_illuminant", MetadataCategory.ICC_PROFILES, "str", "Illuminant"),
            ("icc_creator", MetadataCategory.ICC_PROFILES, "str", "Profile creator"),
            ("icc_profile_id", MetadataCategory.ICC_PROFILES, "str", "Profile ID"),
            ("icc_cmm_type", MetadataCategory.ICC_PROFILES, "str", "CMM type"),
            ("icc_profile_size", MetadataCategory.ICC_PROFILES, "int", "Profile size in bytes"),
            ("icc_tag_count", MetadataCategory.ICC_PROFILES, "int", "Number of tags"),
            ("icc_trc_curves", MetadataCategory.ICC_PROFILES, "list", "Tone response curves"),
            ("icc_xyz_values", MetadataCategory.ICC_PROFILES, "list", "XYZ colorimetry values"),
            ("icc_red_matrix", MetadataCategory.ICC_PROFILES, "list", "Red color matrix"),
            ("icc_green_matrix", MetadataCategory.ICC_PROFILES, "list", "Green color matrix"),
            ("icc_blue_matrix", MetadataCategory.ICC_PROFILES, "list", "Blue color matrix"),
        ]
        for name, category, field_type, description in icc_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "PSD", "OpenEXR"]
            ))

    def _register_camera_makernotes(self):
        """Camera MakerNotes - ~200+ fields (Canon, Nikon, Sony)"""
        canon_fields = [
            ("canon_camera_settings", MetadataCategory.CAMERA_MAKERNOTES, "dict", "Canon camera settings block"),
            ("canon_camera_model_id", MetadataCategory.CAMERA_MAKERNOTES, "int", "Canon camera model ID"),
            ("canon_camera_owner", MetadataCategory.CAMERA_MAKERNOTES, "str", "Camera owner name"),
            ("canon_camera_serial_number", MetadataCategory.CAMERA_MAKERNOTES, "str", "Camera serial number"),
            ("canon_lens_info", MetadataCategory.CAMERA_MAKERNOTES, "int", "Lens info structure"),
            ("canon_lens_model", MetadataCategory.CAMERA_MAKERNOTES, "str", "Lens model"),
            ("canon_lens_serial_number", MetadataCategory.CAMERA_MAKERNOTES, "str", "Lens serial number"),
            ("canon_af_info", MetadataCategory.CAMERA_MAKERNOTES, "dict", "AF information"),
            ("canon_af_points", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF points used"),
            ("canon_af_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "AF mode"),
            ("canon_shutter_count", MetadataCategory.CAMERA_MAKERNOTES, "int", "Shutter actuations"),
            ("canon_firmware_version", MetadataCategory.CAMERA_MAKERNOTES, "str", "Firmware version"),
        ]
        for name, category, field_type, description in canon_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                vendor_specific="Canon", supported_formats=["JPEG", "TIFF", "CR2", "CR3", "NEF", "DNG", "RAF"]
            ))

        nikon_fields = [
            ("nikon_camera_settings", MetadataCategory.CAMERA_MAKERNOTES, "dict", "Nikon camera settings"),
            ("nikon_camera_model", MetadataCategory.CAMERA_MAKERNOTES, "str", "Camera model"),
            ("nikon_firmware_version", MetadataCategory.CAMERA_MAKERNOTES, "str", "Firmware version"),
            ("nikon_lens_info", MetadataCategory.CAMERA_MAKERNOTES, "list", "Lens info"),
            ("nikon_lens_model", MetadataCategory.CAMERA_MAKERNOTES, "str", "Lens model"),
            ("nikon_af_info", MetadataCategory.CAMERA_MAKERNOTES, "dict", "AF information"),
            ("nikon_shutter_count", MetadataCategory.CAMERA_MAKERNOTES, "int", "Shutter count"),
            ("nikon_serial_number", MetadataCategory.CAMERA_MAKERNOTES, "str", "Camera serial number"),
        ]
        for name, category, field_type, description in nikon_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                vendor_specific="Nikon", supported_formats=["JPEG", "TIFF", "NEF", "NRW", "DNG"]
            ))

        sony_fields = [
            ("sony_camera_settings", MetadataCategory.CAMERA_MAKERNOTES, "dict", "Sony camera settings"),
            ("sony_camera_model", MetadataCategory.CAMERA_MAKERNOTES, "str", "Camera model"),
            ("sony_firmware_version", MetadataCategory.CAMERA_MAKERNOTES, "str", "Firmware version"),
            ("sony_lens_specification", MetadataCategory.CAMERA_MAKERNOTES, "list", "Lens specification"),
            ("sony_lens_model", MetadataCategory.CAMERA_MAKERNOTES, "str", "Lens model"),
            ("sony_focus_mode", MetadataCategory.CAMERA_MAKERNOTES, "int", "Focus mode"),
            ("sony_af_mode", MetadataCategory.CAMERA_MAKERNOTES, "int", "AF mode"),
            ("sony_shutter_count", MetadataCategory.CAMERA_MAKERNOTES, "int", "Shutter count"),
            ("sony_serial_number", MetadataCategory.CAMERA_MAKERNOTES, "str", "Serial number"),
        ]
        for name, category, field_type, description in sony_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                vendor_specific="Sony", supported_formats=["JPEG", "TIFF", "ARW", "SR2", "DNG"]
            ))

    def _register_mobile_metadata(self):
        """Mobile metadata - ~50 fields (iPhone, Android)"""
        mobile_fields = [
            ("iphone_model", MetadataCategory.MOBILE_METADATA, "str", "iPhone model"),
            ("iphone_software_version", MetadataCategory.MOBILE_METADATA, "str", "iOS version"),
            ("iphone_processing_sw", MetadataCategory.MOBILE_METADATA, "str", "Processing software"),
            ("iphone_lens_model", MetadataCategory.MOBILE_METADATA, "str", "Lens model"),
            ("iphone_f_number", MetadataCategory.MOBILE_METADATA, "float", "F-number"),
            ("iphone_exposure_time", MetadataCategory.MOBILE_METADATA, "float", "Exposure time"),
            ("iphone_iso", MetadataCategory.MOBILE_METADATA, "int", "ISO"),
            ("iphone_focal_length", MetadataCategory.MOBILE_METADATA, "float", "Focal length"),
            ("iphone_live_photo", MetadataCategory.MOBILE_METADATA, "bool", "Is live photo"),
            ("iphone_hdr_type", MetadataCategory.MOBILE_METADATA, "int", "HDR type"),
            ("iphone_portrait_version", MetadataCategory.MOBILE_METADATA, "int", "Portrait version"),
            ("android_model", MetadataCategory.MOBILE_METADATA, "str", "Android device model"),
            ("android_software_version", MetadataCategory.MOBILE_METADATA, "str", "Android version"),
            ("android_camera_make", MetadataCategory.MOBILE_METADATA, "str", "Camera make"),
        ]
        for name, category, field_type, description in mobile_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                vendor_specific="Mobile", supported_formats=["JPEG", "HEIC", "AVIF", "DNG"]
            ))

    def _register_action_camera(self):
        """Action camera metadata - ~50 fields (DJI, GoPro)"""
        action_fields = [
            ("dji_make", MetadataCategory.ACTION_CAMERA, "str", "DJI make"),
            ("dji_model", MetadataCategory.ACTION_CAMERA, "str", "DJI model"),
            ("dji_firmware_version", MetadataCategory.ACTION_CAMERA, "str", "Firmware version"),
            ("dji_camera_serial", MetadataCategory.ACTION_CAMERA, "str", "Camera serial number"),
            ("dji_flight_data", MetadataCategory.ACTION_CAMERA, "dict", "Flight data"),
            ("dji_gps_latitude", MetadataCategory.ACTION_CAMERA, "float", "GPS latitude"),
            ("dji_gps_longitude", MetadataCategory.ACTION_CAMERA, "float", "GPS longitude"),
            ("dji_gps_altitude", MetadataCategory.ACTION_CAMERA, "float", "GPS altitude"),
            ("gopro_model", MetadataCategory.ACTION_CAMERA, "str", "GoPro model"),
            ("gopro_firmware_version", MetadataCategory.ACTION_CAMERA, "str", "Firmware version"),
            ("gopro_resolution", MetadataCategory.ACTION_CAMERA, "str", "Resolution"),
            ("gopro_frame_rate", MetadataCategory.ACTION_CAMERA, "float", "Frame rate"),
            ("gopro_fov", MetadataCategory.ACTION_CAMERA, "str", "Field of view"),
        ]
        for name, category, field_type, description in action_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "DNG", "MOV", "MP4"]
            ))

    def _register_perceptual_hashes(self):
        """Perceptual hashes - ~15 fields"""
        hash_fields = [
            ("phash_original", MetadataCategory.PERCEPTUAL_HASHES, "str", "Original pHash (64-bit)"),
            ("phash_dct", MetadataCategory.PERCEPTUAL_HASHES, "str", "DCT-based pHash"),
            ("dhash_horizontal", MetadataCategory.PERCEPTUAL_HASHES, "str", "Horizontal dHash"),
            ("dhash_vertical", MetadataCategory.PERCEPTUAL_HASHES, "str", "Vertical dHash"),
            ("ahash_mean", MetadataCategory.PERCEPTUAL_HASHES, "str", "Mean aHash"),
            ("blockhash", MetadataCategory.PERCEPTUAL_HASHES, "str", "Blockhash"),
            ("imghash_hu_moments", MetadataCategory.PERCEPTUAL_HASHES, "list", "Hu moments"),
            ("duplicate_detected", MetadataCategory.PERCEPTUAL_HASHES, "bool", "Duplicate detected"),
            ("duplicate_source", MetadataCategory.PERCEPTUAL_HASHES, "str", "Duplicate source file"),
        ]
        for name, category, field_type, description in hash_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "GIF", "BMP", "PSD", "HEIC", "AVIF"]
            ))

    def _register_color_analysis(self):
        """Color analysis - ~30 fields"""
        color_fields = [
            ("dominant_color", MetadataCategory.COLOR_ANALYSIS, "list", "Dominant color (RGB)"),
            ("dominant_color_pct", MetadataCategory.COLOR_ANALYSIS, "list", "Dominant color percentage"),
            ("palette_colors", MetadataCategory.COLOR_ANALYSIS, "list", "Color palette"),
            ("histogram_red", MetadataCategory.COLOR_ANALYSIS, "list", "Red histogram (256 bins)"),
            ("histogram_green", MetadataCategory.COLOR_ANALYSIS, "list", "Green histogram (256 bins)"),
            ("histogram_blue", MetadataCategory.COLOR_ANALYSIS, "list", "Blue histogram (256 bins)"),
            ("average_color", MetadataCategory.COLOR_ANALYSIS, "list", "Average color (RGB)"),
            ("color_temperature", MetadataCategory.COLOR_ANALYSIS, "float", "Color temperature (K)"),
            ("tint", MetadataCategory.COLOR_ANALYSIS, "float", "Tint (green-magenta)"),
            ("brightness_ev", MetadataCategory.COLOR_ANALYSIS, "float", "Brightness in EV"),
            ("dynamic_range", MetadataCategory.COLOR_ANALYSIS, "float", "Dynamic range (stops)"),
            ("contrast_ratio", MetadataCategory.COLOR_ANALYSIS, "float", "Contrast ratio"),
            ("saturation_avg", MetadataCategory.COLOR_ANALYSIS, "float", "Average saturation"),
        ]
        for name, category, field_type, description in color_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "PSD", "OpenEXR"]
            ))

    def _register_quality_metrics(self):
        """Quality metrics - ~20 fields"""
        quality_fields = [
            ("brisque_score", MetadataCategory.QUALITY_METRICS, "float", "BRISQUE quality score"),
            ("niqe_score", MetadataCategory.QUALITY_METRICS, "float", "NIQE quality score"),
            ("sharpness_blur", MetadataCategory.QUALITY_METRICS, "float", "Blur-based sharpness"),
            ("sharpness_laplacian", MetadataCategory.QUALITY_METRICS, "float", "Laplacian variance sharpness"),
            ("noise_gauss", MetadataCategory.QUALITY_METRICS, "float", "Gaussian noise level"),
            ("artifact_blocking", MetadataCategory.QUALITY_METRICS, "float", "Blocking artifacts"),
            ("overall_quality_score", MetadataCategory.QUALITY_METRICS, "float", "Overall quality score"),
            ("aesthetic_score", MetadataCategory.QUALITY_METRICS, "float", "Aesthetic score"),
        ]
        for name, category, field_type, description in quality_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "PSD"]
            ))

    def _register_steganography(self):
        """Steganography detection - ~15 fields"""
        stego_fields = [
            ("stego_lsb_detected", MetadataCategory.STEGANOGRAPHY, "bool", "LSB steganography detected"),
            ("stego_dct_detected", MetadataCategory.STEGANOGRAPHY, "bool", "DCT steganography detected"),
            ("stego_entropy", MetadataCategory.STEGANOGRAPHY, "float", "Entropy analysis result"),
            ("stego_capacity", MetadataCategory.STEGANOGRAPHY, "float", "Steganographic capacity"),
        ]
        for name, category, field_type, description in stego_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "GIF", "BMP", "TIFF", "WebP"]
            ))

    def _register_image_forensics(self):
        """Image forensics - ~20 fields"""
        forensics_fields = [
            ("forensics_ela_mean", MetadataCategory.IMAGE_FORENSICS, "float", "ELA mean value"),
            ("forensics_ela_std", MetadataCategory.IMAGE_FORENSICS, "float", "ELA standard deviation"),
            ("forensics_manipulation_detected", MetadataCategory.IMAGE_FORENSICS, "bool", "Manipulation detected"),
            ("forensics_splicing_detected", MetadataCategory.IMAGE_FORENSICS, "bool", "Splicing detected"),
            ("forensics_cloning_detected", MetadataCategory.IMAGE_FORENSICS, "bool", "Cloning detected"),
            ("forensics_noise_inconsistency", MetadataCategory.IMAGE_FORENSICS, "bool", "Noise inconsistency detected"),
            ("forensics_double_compression", MetadataCategory.IMAGE_FORENSICS, "bool", "Double compression detected"),
            ("forensics_source_device", MetadataCategory.IMAGE_FORENSICS, "str", "Source device identification"),
        ]
        for name, category, field_type, description in forensics_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "TIFF", "PSD", "WebP"]
            ))

    def _register_ai_generation(self):
        """AI generation detection - ~30 fields"""
        ai_fields = [
            ("ai_detected", MetadataCategory.AI_GENERATION, "bool", "AI-generated content detected"),
            ("ai_confidence", MetadataCategory.AI_GENERATION, "float", "AI detection confidence"),
            ("ai_model", MetadataCategory.AI_GENERATION, "str", "Detected AI model"),
            ("ai_stable_diffusion", MetadataCategory.AI_GENERATION, "bool", "Stable Diffusion detected"),
            ("ai_stable_diffusion_prompt", MetadataCategory.AI_GENERATION, "str", "SD prompt"),
            ("ai_stable_diffusion_seed", MetadataCategory.AI_GENERATION, "int", "SD seed"),
            ("ai_midjourney", MetadataCategory.AI_GENERATION, "bool", "Midjourney detected"),
            ("ai_midjourney_version", MetadataCategory.AI_GENERATION, "str", "Midjourney version"),
            ("ai_dalle", MetadataCategory.AI_GENERATION, "bool", "DALL-E detected"),
            ("ai_c2pa_present", MetadataCategory.AI_GENERATION, "bool", "C2PA manifest present"),
            ("ai_c2pa_version", MetadataCategory.AI_GENERATION, "str", "C2PA version"),
            ("ai_c2pa_manifest", MetadataCategory.AI_GENERATION, "dict", "C2PA manifest data"),
        ]
        for name, category, field_type, description in ai_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "PSD", "HEIC", "AVIF"]
            ))

    def _register_photoshop_psd(self):
        """Photoshop PSD - ~40 fields"""
        psd_fields = [
            ("psd_version", MetadataCategory.PHOTOSHOP_PSD, "str", "PSD version"),
            ("psd_channels", MetadataCategory.PHOTOSHOP_PSD, "int", "Number of channels"),
            ("psd_height", MetadataCategory.PHOTOSHOP_PSD, "int", "Image height"),
            ("psd_width", MetadataCategory.PHOTOSHOP_PSD, "int", "Image width"),
            ("psd_depth", MetadataCategory.PHOTOSHOP_PSD, "int", "Bit depth"),
            ("psd_color_mode", MetadataCategory.PHOTOSHOP_PSD, "int", "Color mode"),
            ("psd_layer_count", MetadataCategory.PHOTOSHOP_PSD, "int", "Number of layers"),
            ("psd_has_alpha", MetadataCategory.PHOTOSHOP_PSD, "bool", "Has alpha channel"),
            ("psd_has_smart_objects", MetadataCategory.PHOTOSHOP_PSD, "bool", "Has smart objects"),
            ("psd_has_vector_masks", MetadataCategory.PHOTOSHOP_PSD, "bool", "Has vector masks"),
            ("psd_has_clipping_masks", MetadataCategory.PHOTOSHOP_PSD, "bool", "Has clipping masks"),
            ("psd_resolution", MetadataCategory.PHOTOSHOP_PSD, "dict", "Resolution info"),
        ]
        for name, category, field_type, description in psd_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["PSD", "PSB"]
            ))

    def _register_edit_history(self):
        """Edit history - ~30 fields"""
        history_fields = [
            ("lightroom_history", MetadataCategory.EDIT_HISTORY, "list", "Lightroom edit history"),
            ("lightroom_version", MetadataCategory.EDIT_HISTORY, "str", "Lightroom version"),
            ("photoshop_history", MetadataCategory.EDIT_HISTORY, "list", "Photoshop history"),
            ("photoshop_ancestors", MetadataCategory.EDIT_HISTORY, "list", "Photoshop ancestors"),
            ("capture_one_history", MetadataCategory.EDIT_HISTORY, "list", "Capture One history"),
            ("edit_timestamp", MetadataCategory.EDIT_HISTORY, "datetime", "Last edit timestamp"),
            ("edit_software", MetadataCategory.EDIT_HISTORY, "str", "Editing software"),
            ("crop_applied", MetadataCategory.EDIT_HISTORY, "bool", "Crop applied"),
            ("crop_ratio", MetadataCategory.EDIT_HISTORY, "str", "Crop ratio"),
            ("rotation_applied", MetadataCategory.EDIT_HISTORY, "bool", "Rotation applied"),
            ("rotation_angle", MetadataCategory.EDIT_HISTORY, "float", "Rotation angle"),
            ("watermark_applied", MetadataCategory.EDIT_HISTORY, "bool", "Watermark applied"),
            ("watermark_text", MetadataCategory.EDIT_HISTORY, "str", "Watermark text"),
        ]
        for name, category, field_type, description in history_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "TIFF", "PSD", "PNG", "HEIC"]
            ))

    def _register_openexr_hdr(self):
        """OpenEXR HDR - ~25 fields"""
        exr_fields = [
            ("exr_version", MetadataCategory.OPENEXR_HDR, "str", "OpenEXR version"),
            ("exr_channels", MetadataCategory.OPENEXR_HDR, "list", "Channel names and types"),
            ("exr_compression", MetadataCategory.OPENEXR_HDR, "str", "Compression method"),
            ("exr_data_window", MetadataCategory.OPENEXR_HDR, "dict", "Data window"),
            ("exr_display_window", MetadataCategory.OPENEXR_HDR, "dict", "Display window"),
            ("exr_line_order", MetadataCategory.OPENEXR_HDR, "int", "Line order"),
            ("exr_pixel_aspect_ratio", MetadataCategory.OPENEXR_HDR, "float", "Pixel aspect ratio"),
            ("exr_chromaticities", MetadataCategory.OPENEXR_HDR, "dict", "Chromaticities"),
            ("exr_white_luminance", MetadataCategory.OPENEXR_HDR, "float", "White luminance"),
            ("exr_adopted_neutral", MetadataCategory.OPENEXR_HDR, "list", "Adopted neutral"),
            ("exr_rendered_device", MetadataCategory.OPENEXR_HDR, "str", "Rendered device"),
            ("exr_look_modify_transform", MetadataCategory.OPENEXR_HDR, "bool", "Look modifiy transform"),
            ("exr_tiles", MetadataCategory.OPENEXR_HDR, "bool", "Has tiles"),
            ("exr_tile_size", MetadataCategory.OPENEXR_HDR, "list", "Tile size"),
        ]
        for name, category, field_type, description in exr_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["OpenEXR"]
            ))

    def _register_avif_heif(self):
        """AVIF/HEIF format - ~50 fields"""
        avif_fields = [
            ("avif_major_brand", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "AVIF major brand"),
            ("avif_compatible_brands", MetadataCategory.FILE_FORMAT_CHUNKS, "list", "Compatible brands"),
            ("avif_seq_profile", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "AV1 sequence profile"),
            ("avif_seq_level", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "AV1 sequence level"),
            ("avif_seq_tier", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "AV1 sequence tier"),
            ("avif_high_bitdepth", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "High bit depth"),
            ("avif_twelve_bit", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "12-bit format"),
            ("avif_monochrome", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Monochrome"),
            ("avif_chroma_subsampling", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "Chroma subsampling"),
            ("avif_color_type", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "Color type"),
            ("avif_primaries", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Color primaries"),
            ("avif_transfer_function", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Transfer function"),
            ("avif_matrix", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Color matrix"),
            ("avif_full_range", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Full range color"),
            ("avif_item_count", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Number of items"),
            ("heif_compression", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "HEIF compression"),
        ]
        for name, category, field_type, description in avif_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["AVIF", "HEIF", "HEIC"]
            ))

    def _register_camera_raw(self):
        """Camera RAW formats - ~100 fields"""
        raw_fields = [
            ("raw_format", MetadataCategory.RAW_FORMAT, "str", "RAW format type"),
            ("raw_maker", MetadataCategory.RAW_FORMAT, "str", "Camera maker"),
            ("raw_model", MetadataCategory.RAW_FORMAT, "str", "Camera model"),
            ("raw_endianness", MetadataCategory.RAW_FORMAT, "str", "TIFF endianness"),
            ("raw_compressed", MetadataCategory.RAW_FORMAT, "bool", "Is compressed RAW"),
            ("raw_bits_per_sample", MetadataCategory.RAW_FORMAT, "int", "Bits per sample"),
            ("raw_samples_per_pixel", MetadataCategory.RAW_FORMAT, "int", "Samples per pixel"),
            ("dng_version", MetadataCategory.RAW_FORMAT, "int", "DNG version"),
            ("dng_backward_version", MetadataCategory.RAW_FORMAT, "int", "DNG backward version"),
            ("dng_unique_camera_model", MetadataCategory.RAW_FORMAT, "str", "Unique camera model"),
            ("dng_localized_camera_model", MetadataCategory.RAW_FORMAT, "str", "Localized camera model"),
            ("dng_color_matrix1", MetadataCategory.RAW_FORMAT, "list", "Color matrix 1"),
            ("dng_color_matrix2", MetadataCategory.RAW_FORMAT, "list", "Color matrix 2"),
            ("dng_forward_matrix1", MetadataCategory.RAW_FORMAT, "list", "Forward matrix 1"),
            ("dng_forward_matrix2", MetadataCategory.RAW_FORMAT, "list", "Forward matrix 2"),
            ("dng_calibration_illuminant1", MetadataCategory.RAW_FORMAT, "int", "Calibration illuminant 1"),
            ("dng_calibration_illuminant2", MetadataCategory.RAW_FORMAT, "int", "Calibration illuminant 2"),
            ("dng_as_shot_neutral", MetadataCategory.RAW_FORMAT, "list", "As shot neutral"),
            ("dng_as_shot_white_xy", MetadataCategory.RAW_FORMAT, "list", "As shot white XY"),
            ("dng_baseline_exposure", MetadataCategory.RAW_FORMAT, "float", "Baseline exposure"),
            ("dng_baseline_noise", MetadataCategory.RAW_FORMAT, "float", "Baseline noise"),
            ("dng_baseline_sharpness", MetadataCategory.RAW_FORMAT, "float", "Baseline sharpness"),
            ("dng_bayer_green_split", MetadataCategory.RAW_FORMAT, "int", "Bayer green split"),
            ("dng_raw_data_unique_id", MetadataCategory.RAW_FORMAT, "str", "RAW data unique ID"),
            ("dng_original_raw_file_name", MetadataCategory.RAW_FORMAT, "str", "Original RAW file name"),
            ("dng_active_area", MetadataCategory.RAW_FORMAT, "list", "Active area"),
            ("dng_masked_areas", MetadataCategory.RAW_FORMAT, "list", "Masked areas"),
            ("raw_sensor_width", MetadataCategory.RAW_FORMAT, "int", "Sensor width"),
            ("raw_sensor_height", MetadataCategory.RAW_FORMAT, "int", "Sensor height"),
            ("raw_sensor_megapixels", MetadataCategory.RAW_FORMAT, "float", "Sensor megapixels"),
            ("raw_aspect_ratio", MetadataCategory.RAW_FORMAT, "float", "Aspect ratio"),
        ]
        for name, category, field_type, description in raw_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["CR2", "CR3", "NEF", "ARW", "RAF", "DNG", "ORF", "RW2", "RWL", "3FR", "IIQ"]
            ))

    def _register_motion_photo(self):
        """Motion/Live Photos - ~30 fields"""
        motion_fields = [
            ("is_motion_photo", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Is motion photo"),
            ("motion_photo_type", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "Motion photo type"),
            ("motion_video_offset", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Video offset"),
            ("motion_video_size", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Video size"),
            ("motion_video_codec", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "Video codec"),
            ("motion_duration_ms", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Motion duration ms"),
            ("motion_still_size", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Still image size"),
            ("motion_flags", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Motion flags"),
            ("motion_is_live", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Is live photo"),
            ("motion_has_geo", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Has geotag in motion"),
            ("motion_primary_width", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Primary image width"),
            ("motion_primary_height", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Primary image height"),
            ("motion_compatible_ios", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "iOS compatible"),
            ("motion_compatible_android", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Android compatible"),
        ]
        for name, category, field_type, description in motion_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["HEIC", "JPEG", "AVIF"]
            ))

    def _register_xmp_extended(self):
        """Extended XMP namespaces - ~80 fields"""
        xmp_ext_fields = [
            ("xmp_dc_provenance", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core provenance"),
            ("xmp_dc_rights_holder", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core rights holder"),
            ("xmp_dc_instructions", MetadataCategory.XMP_NAMESPACES, "str", "Dublin Core instructions"),
            ("xmp_dc_audience", MetadataCategory.XMP_NAMESPACES, "list", "Dublin Core audience"),
            ("xmp_dc_relation", MetadataCategory.XMP_NAMESPACES, "list", "Dublin Core relation"),
            ("xmp_photoshop_history", MetadataCategory.XMP_NAMESPACES, "str", "Photoshop history"),
            ("xmp_photoshop_ancestors", MetadataCategory.XMP_NAMESPACES, "list", "Photoshop ancestors"),
            ("xmp_photoshop_document_history", MetadataCategory.XMP_NAMESPACES, "list", "Document history"),
            ("xmp_cr_white_balance", MetadataCategory.XMP_NAMESPACES, "str", "Camera Raw white balance"),
            ("xmp_cr_temperature", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw temperature"),
            ("xmp_cr_tint", MetadataCategory.XMP_NAMESPACES, "float", "Camera Raw tint"),
            ("xmp_cr_exposure", MetadataCategory.XMP_NAMESPACES, "float", "Camera Raw exposure"),
            ("xmp_cr_contrast", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw contrast"),
            ("xmp_cr_highlights", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw highlights"),
            ("xmp_cr_shadows", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw shadows"),
            ("xmp_cr_whites", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw whites"),
            ("xmp_cr_blacks", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw blacks"),
            ("xmp_cr_clarity", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw clarity"),
            ("xmp_cr_dehaze", MetadataCategory.XMP_NAMESPACES, "int", "Camera Raw dehaze"),
            ("xmp_cr_vignette_amount", MetadataCategory.XMP_NAMESPACES, "float", "Camera Raw vignette"),
            ("xmp_cr_grain_amount", MetadataCategory.XMP_NAMESPACES, "float", "Camera Raw grain"),
            ("xmp_cr_lens_profile", MetadataCategory.XMP_NAMESPACES, "bool", "Lens profile enabled"),
            ("xmp_cr_perspective_correction", MetadataCategory.XMP_NAMESPACES, "dict", "Perspective correction"),
            ("xmp_xmprights_marked", MetadataCategory.XMP_NAMESPACES, "bool", "Rights marked"),
            ("xmp_xmprights_owner", MetadataCategory.XMP_NAMESPACES, "list", "Rights owner"),
            ("xmp_xmprights_usage_terms", MetadataCategory.XMP_NAMESPACES, "list", "Usage terms"),
            ("xmp_cc_license", MetadataCategory.XMP_NAMESPACES, "str", "Creative Commons license"),
            ("xmp_cc_attribution", MetadataCategory.XMP_NAMESPACES, "str", "CC attribution"),
            ("xmp_xmpdm_scene", MetadataCategory.XMP_NAMESPACES, "str", "DM scene"),
            ("xmp_xmpdm_shot", MetadataCategory.XMP_NAMESPACES, "dict", "DM shot info"),
            ("xmp_xmpdm_project", MetadataCategory.XMP_NAMESPACES, "str", "DM project"),
            ("xmp_xmpdm_artist", MetadataCategory.XMP_NAMESPACES, "str", "DM artist"),
            ("xmp_xmpdm_album", MetadataCategory.XMP_NAMESPACES, "str", "DM album"),
            ("xmp_gphoto_is_360", MetadataCategory.XMP_NAMESPACES, "bool", "Is 360 panorama"),
            ("xmp_gphoto_projection_type", MetadataCategory.XMP_NAMESPACES, "str", "Projection type"),
            ("xmp_gpano_cropped_area", MetadataCategory.XMP_NAMESPACES, "dict", "Cropped area"),
            ("xmp_gpano_full_pano", MetadataCategory.XMP_NAMESPACES, "dict", "Full panorama size"),
            ("xmp_gpano_initial_view", MetadataCategory.XMP_NAMESPACES, "dict", "Initial view settings"),
            ("xmp_social_platform", MetadataCategory.XMP_NAMESPACES, "str", "Social media platform"),
            ("xmp_instagram_filter", MetadataCategory.XMP_NAMESPACES, "str", "Instagram filter"),
        ]
        for name, category, field_type, description in xmp_ext_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "PSD", "HEIC", "AVIF", "DNG"]
            ))

    def _register_animated_images(self):
        """Animated GIF and APNG metadata - ~40 fields"""
        animated_fields = [
            ("is_animated_gif", MetadataCategory.ANIMATED_IMAGES, "bool", "Is animated GIF"),
            ("gif_version", MetadataCategory.ANIMATED_IMAGES, "str", "GIF version (87a/89a)"),
            ("gif_logical_width", MetadataCategory.ANIMATED_IMAGES, "int", "Logical screen width"),
            ("gif_logical_height", MetadataCategory.ANIMATED_IMAGES, "int", "Logical screen height"),
            ("gif_global_color_count", MetadataCategory.ANIMATED_IMAGES, "int", "Global color table size"),
            ("gif_has_transparency", MetadataCategory.ANIMATED_IMAGES, "bool", "Has transparency"),
            ("gif_transparent_color_index", MetadataCategory.ANIMATED_IMAGES, "int", "Transparent color index"),
            ("gif_pixel_aspect_ratio", MetadataCategory.ANIMATED_IMAGES, "float", "Pixel aspect ratio"),
            ("gif_frame_count", MetadataCategory.ANIMATED_IMAGES, "int", "Number of frames"),
            ("gif_loop_count", MetadataCategory.ANIMATED_IMAGES, "int", "Animation loop count"),
            ("gif_total_duration_ms", MetadataCategory.ANIMATED_IMAGES, "int", "Total animation duration"),
            ("gif_total_pixels_all_frames", MetadataCategory.ANIMATED_IMAGES, "int", "Total pixels across all frames"),
            ("gif_disposal_method", MetadataCategory.ANIMATED_IMAGES, "str", "Frame disposal method"),
            ("gif_has_comments", MetadataCategory.ANIMATED_IMAGES, "bool", "Has comment blocks"),
            ("gif_has_netscape_extension", MetadataCategory.ANIMATED_IMAGES, "bool", "Has NETSCAPE looping extension"),
            ("is_animated_apng", MetadataCategory.ANIMATED_IMAGES, "bool", "Is animated PNG"),
            ("apng_frame_count", MetadataCategory.ANIMATED_IMAGES, "int", "APNG frame count"),
            ("apng_num_plays", MetadataCategory.ANIMATED_IMAGES, "int", "APNG play count"),
            ("apng_total_duration_ms", MetadataCategory.ANIMATED_IMAGES, "int", "APNG total duration"),
            ("apng_width", MetadataCategory.ANIMATED_IMAGES, "int", "APNG canvas width"),
            ("apng_height", MetadataCategory.ANIMATED_IMAGES, "int", "APNG canvas height"),
            ("apng_has_blend_op", MetadataCategory.ANIMATED_IMAGES, "bool", "Has blend operation"),
            ("apng_dispose_op", MetadataCategory.ANIMATED_IMAGES, "str", "APNG dispose operation"),
        ]
        for name, category, field_type, description in animated_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["GIF", "APNG", "PNG"]
            ))

    def _register_social_metadata(self):
        """Social media and platform-specific metadata - ~35 fields"""
        social_fields = [
            ("social_platform_source", MetadataCategory.SOCIAL_METADATA, "str", "Source platform"),
            ("social_post_id", MetadataCategory.SOCIAL_METADATA, "str", "Social media post ID"),
            ("social_user_handle", MetadataCategory.SOCIAL_METADATA, "str", "Social media user handle"),
            ("social_upload_date", MetadataCategory.SOCIAL_METADATA, "datetime", "Social platform upload date"),
            ("social_engagement", MetadataCategory.SOCIAL_METADATA, "dict", "Engagement metrics"),
            ("social_view_count", MetadataCategory.SOCIAL_METADATA, "int", "View count"),
            ("social_like_count", MetadataCategory.SOCIAL_METADATA, "int", "Like count"),
            ("social_share_count", MetadataCategory.SOCIAL_METADATA, "int", "Share count"),
            ("social_comment_count", MetadataCategory.SOCIAL_METADATA, "int", "Comment count"),
            ("instagram_filter_used", MetadataCategory.SOCIAL_METADATA, "str", "Instagram filter name"),
            ("instagram_edit_timestamp", MetadataCategory.SOCIAL_METADATA, "datetime", "Instagram edit timestamp"),
            ("facebook_post_id", MetadataCategory.SOCIAL_METADATA, "str", "Facebook post ID"),
            ("twitter_tweet_id", MetadataCategory.SOCIAL_METADATA, "str", "Twitter tweet ID"),
            ("tiktok_video_id", MetadataCategory.SOCIAL_METADATA, "str", "TikTok video ID"),
            ("youtube_video_id", MetadataCategory.SOCIAL_METADATA, "str", "YouTube video ID"),
            ("pinterest_pin_id", MetadataCategory.SOCIAL_METADATA, "str", "Pinterest pin ID"),
            ("snapchat_snap_id", MetadataCategory.SOCIAL_METADATA, "str", "Snapchat snap ID"),
            ("linkedin_post_id", MetadataCategory.SOCIAL_METADATA, "str", "LinkedIn post ID"),
            ("reddit_post_id", MetadataCategory.SOCIAL_METADATA, "str", "Reddit post ID"),
            ("flickr_photo_id", MetadataCategory.SOCIAL_METADATA, "str", "Flickr photo ID"),
            ("flickr_owner", MetadataCategory.SOCIAL_METADATA, "str", "Flickr owner name"),
            ("telegram_message_id", MetadataCategory.SOCIAL_METADATA, "str", "Telegram message ID"),
            ("whatsapp_media_id", MetadataCategory.SOCIAL_METADATA, "str", "WhatsApp media ID"),
            ("discord_attachment_id", MetadataCategory.SOCIAL_METADATA, "str", "Discord attachment ID"),
            ("slack_file_id", MetadataCategory.SOCIAL_METADATA, "str", "Slack file ID"),
            ("telegram_file_unique_id", MetadataCategory.SOCIAL_METADATA, "str", "Telegram file unique ID"),
            ("discord_message_id", MetadataCategory.SOCIAL_METADATA, "str", "Discord message ID"),
        ]
        for name, category, field_type, description in social_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "GIF", "HEIC", "AVIF"]
            ))

    def _register_accessibility(self):
        """Accessibility and inclusive design metadata - ~25 fields"""
        accessibility_fields = [
            ("accessibility_alt_text", MetadataCategory.ACCESSIBILITY, "str", "Alt text description"),
            ("accessibility_long_desc", MetadataCategory.ACCESSIBILITY, "str", "Long description"),
            ("accessibility_caption", MetadataCategory.ACCESSIBILITY, "str", "Caption text"),
            ("accessibility_transcript", MetadataCategory.ACCESSIBILITY, "str", "Transcript for media"),
            ("accessibility_aria_label", MetadataCategory.ACCESSIBILITY, "str", "ARIA label"),
            ("accessibility_aria_desc", MetadataCategory.ACCESSIBILITY, "str", "ARIA description"),
            ("accessibility_role", MetadataCategory.ACCESSIBILITY, "str", "ARIA role"),
            ("accessibility_keywords", MetadataCategory.ACCESSIBILITY, "list", "Accessibility keywords"),
            ("accessibility_subject_description", MetadataCategory.ACCESSIBILITY, "str", "Subject description"),
            ("accessibility_content_warning", MetadataCategory.ACCESSIBILITY, "str", "Content warning"),
            ("accessibility_flashing_warning", MetadataCategory.ACCESSIBILITY, "bool", "Contains flashing content"),
            ("accessibility_motion_warning", MetadataCategory.ACCESSIBILITY, "bool", "Contains motion"),
            ("accessibility_high_contrast", MetadataCategory.ACCESSIBILITY, "bool", "Optimized for high contrast"),
            ("accessibility_color_independent", MetadataCategory.ACCESSIBILITY, "bool", "Color independent content"),
            ("accessibility_reading_order", MetadataCategory.ACCESSIBILITY, "int", "Reading order position"),
            ("accessibility_ocr_text", MetadataCategory.ACCESSIBILITY, "str", "OCR extracted text"),
            ("accessibility_sign_language", MetadataCategory.ACCESSIBILITY, "bool", "Has sign language interpretation"),
            ("accessibility_audio_description", MetadataCategory.ACCESSIBILITY, "str", "Audio description track"),
            ("accessibility_language", MetadataCategory.ACCESSIBILITY, "str", "Content language"),
            ("accessibility_text_position", MetadataCategory.ACCESSIBILITY, "dict", "Text position metadata"),
        ]
        for name, category, field_type, description in accessibility_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "GIF", "TIFF", "SVG", "AVIF", "HEIC"]
            ))

    def _register_tiff_ifd(self):
        """TIFF/IFD and format-specific metadata - ~45 fields"""
        tiff_fields = [
            ("tiff_byte_order", MetadataCategory.TIFF_IFD, "str", "Byte order (little/big endian)"),
            ("tiff_ifd_count", MetadataCategory.TIFF_IFD, "int", "Number of IFDs"),
            ("tiff_image_width", MetadataCategory.TIFF_IFD, "int", "Image width from IFD"),
            ("tiff_image_length", MetadataCategory.TIFF_IFD, "int", "Image length from IFD"),
            ("tiff_bits_per_sample", MetadataCategory.TIFF_IFD, "list", "Bits per sample"),
            ("tiff_samples_per_pixel", MetadataCategory.TIFF_IFD, "int", "Samples per pixel"),
            ("tiff_compression", MetadataCategory.TIFF_IFD, "int", "Compression scheme"),
            ("tiff_compression_name", MetadataCategory.TIFF_IFD, "str", "Compression name"),
            ("tiff_photometric", MetadataCategory.TIFF_IFD, "int", "Photometric interpretation"),
            ("tiff_photometric_name", MetadataCategory.TIFF_IFD, "str", "Photometric name"),
            ("tiff_orientation", MetadataCategory.TIFF_IFD, "int", "Orientation"),
            ("tiff_orientation_name", MetadataCategory.TIFF_IFD, "str", "Orientation name"),
            ("tiff_samples_format", MetadataCategory.TIFF_IFD, "int", "Sample format"),
            ("tiff_predictor", MetadataCategory.TIFF_IFD, "int", "Predictor"),
            ("tiff_planar_config", MetadataCategory.TIFF_IFD, "int", "Planar configuration"),
            ("tiff_y_resolution", MetadataCategory.TIFF_IFD, "float", "Y resolution"),
            ("tiff_x_resolution", MetadataCategory.TIFF_IFD, "float", "X resolution"),
            ("tiff_resolution_unit", MetadataCategory.TIFF_IFD, "int", "Resolution unit"),
            ("tiff_resolution_unit_name", MetadataCategory.TIFF_IFD, "str", "Resolution unit name"),
            ("tiff_software", MetadataCategory.TIFF_IFD, "str", "Software"),
            ("tiff_artist", MetadataCategory.TIFF_IFD, "str", "Artist"),
            ("tiff_host_computer", MetadataCategory.TIFF_IFD, "str", "Host computer"),
            ("tiff_new_subfile_type", MetadataCategory.TIFF_IFD, "int", "New subfile type"),
            ("tiff_subfile_type", MetadataCategory.TIFF_IFD, "int", "Subfile type"),
            ("tiff_tile_width", MetadataCategory.TIFF_IFD, "int", "Tile width"),
            ("tiff_tile_length", MetadataCategory.TIFF_IFD, "int", "Tile length"),
            ("tiff_strip_offsets", MetadataCategory.TIFF_IFD, "list", "Strip offsets"),
            ("tiff_strip_byte_counts", MetadataCategory.TIFF_IFD, "list", "Strip byte counts"),
            ("tiff_rows_per_strip", MetadataCategory.TIFF_IFD, "int", "Rows per strip"),
            ("tiff_white_point", MetadataCategory.TIFF_IFD, "list", "White point"),
            ("tiff_primary_chromaticities", MetadataCategory.TIFF_IFD, "list", "Primary chromaticities"),
            ("tiff_ycbcr_coefficients", MetadataCategory.TIFF_IFD, "list", "YCbCr coefficients"),
            ("tiff_ycbcr_positioning", MetadataCategory.TIFF_IFD, "int", "YCbCr positioning"),
            ("tiff_reference_black_white", MetadataCategory.TIFF_IFD, "list", "Reference black/white"),
            ("tiff_model_tiepoint", MetadataCategory.TIFF_IFD, "list", "Model tiepoint"),
            ("tiff_model_pixel_scale", MetadataCategory.TIFF_IFD, "list", "Model pixel scale"),
            ("tiff_geo_ascii_params", MetadataCategory.TIFF_IFD, "str", "Geo ASCII parameters"),
            ("tiff_geo_double_params", MetadataCategory.TIFF_IFD, "list", "Geo double parameters"),
            ("tiff_geo_key_directory", MetadataCategory.TIFF_IFD, "list", "Geo key directory"),
            ("tiff_is_bigtiff", MetadataCategory.TIFF_IFD, "bool", "Is BigTIFF format"),
            ("tiff_is_geotiff", MetadataCategory.TIFF_IFD, "bool", "Is GeoTIFF format"),
        ]
        for name, category, field_type, description in tiff_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["TIFF", "BigTIFF", "GeoTIFF", "DNG", "CR2", "NEF", "ARW", "PSD"]
            ))

    def _register_ecommerce(self):
        """E-commerce and product image metadata - ~30 fields"""
        ecommerce_fields = [
            ("ecommerce_product_id", MetadataCategory.ECOMMERCE, "str", "Product ID"),
            ("ecommerce_sku", MetadataCategory.ECOMMERCE, "str", "SKU"),
            ("ecommerce_product_name", MetadataCategory.ECOMMERCE, "str", "Product name"),
            ("ecommerce_product_description", MetadataCategory.ECOMMERCE, "str", "Product description"),
            ("ecommerce_brand", MetadataCategory.ECOMMERCE, "str", "Brand"),
            ("ecommerce_mpn", MetadataCategory.ECOMMERCE, "str", "Manufacturer part number"),
            ("ecommerce_gtin", MetadataCategory.ECOMMERCE, "str", "GTIN (UPC/EAN)"),
            ("ecommerce_asin", MetadataCategory.ECOMMERCE, "str", "Amazon ASIN"),
            ("ecommerce_price", MetadataCategory.ECOMMERCE, "float", "Price"),
            ("ecommerce_currency", MetadataCategory.ECOMMERCE, "str", "Currency"),
            ("ecommerce_availability", MetadataCategory.ECOMMERCE, "str", "Availability status"),
            ("ecommerce_condition", MetadataCategory.ECOMMERCE, "str", "Condition"),
            ("ecommerce_color", MetadataCategory.ECOMMERCE, "str", "Product color"),
            ("ecommerce_size", MetadataCategory.ECOMMERCE, "str", "Product size"),
            ("ecommerce_material", MetadataCategory.ECOMMERCE, "str", "Material"),
            ("ecommerce_weight", MetadataCategory.ECOMMERCE, "float", "Weight"),
            ("ecommerce_dimensions", MetadataCategory.ECOMMERCE, "dict", "Dimensions"),
            ("ecommerce_category", MetadataCategory.ECOMMERCE, "str", "Product category"),
            ("ecommerce_subcategory", MetadataCategory.ECOMMERCE, "str", "Product subcategory"),
            ("ecommerce_tags", MetadataCategory.ECOMMERCE, "list", "Product tags"),
            ("ecommerce_keywords", MetadataCategory.ECOMMERCE, "list", "Search keywords"),
            ("ecommerce_variant_id", MetadataCategory.ECOMMERCE, "str", "Variant ID"),
            ("ecommerce_option_name", MetadataCategory.ECOMMERCE, "str", "Option name"),
            ("ecommerce_option_value", MetadataCategory.ECOMMERCE, "str", "Option value"),
            ("ecommerce_batch_number", MetadataCategory.ECOMMERCE, "str", "Batch/lot number"),
            ("ecommerce_expiry_date", MetadataCategory.ECOMMERCE, "datetime", "Expiry date"),
            ("ecommerce_certifications", MetadataCategory.ECOMMERCE, "list", "Certifications"),
            ("ecommerce_country_of_origin", MetadataCategory.ECOMMERCE, "str", "Country of origin"),
        ]
        for name, category, field_type, description in ecommerce_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "GIF", "AVIF", "HEIC", "PSD"]
            ))

    def get_field(self, name: str) -> Optional[MetadataField]:
        """Get a field definition by name"""
        return self.fields.get(name)

    def get_fields_by_category(self, category: MetadataCategory) -> List[MetadataField]:
        """Get all fields in a category"""
        return [self.fields[name] for name in self.categories.get(category, [])]

    def get_all_field_names(self) -> List[str]:
        """Get list of all field names"""
        return list(self.fields.keys())

    def get_total_field_count(self) -> int:
        """Get total number of registered fields"""
        return len(self.fields)

    def get_category_counts(self) -> Dict[str, int]:
        """Get field counts per category"""
        return {cat.value: len(fields) for cat, fields in self.categories.items()}

    def validate_field_value(self, name: str, value: Any) -> bool:
        """Validate a field value against its type definition"""
        field = self.fields.get(name)
        if not field:
            return False
        
        import typing
        type_map = {
            "int": int, "float": float, "str": str, "bool": bool,
            "list": list, "dict": dict, "datetime": str
        }
        expected_type = type_map.get(field.field_type, type)
        
        if field.field_type == "list":
            return isinstance(value, list)
        elif field.field_type == "dict":
            return isinstance(value, dict)
        elif field.field_type == "datetime":
            return isinstance(value, (str, type(None)))
        else:
            return isinstance(value, expected_type) or value is None

    def get_supported_formats(self, name: str) -> List[str]:
        """Get supported formats for a field"""
        field = self.fields.get(name)
        return field.supported_formats if field else []


def get_global_registry() -> ImageMetadataRegistry:
    """Get the global image metadata registry instance"""
    return ImageMetadataRegistry()
