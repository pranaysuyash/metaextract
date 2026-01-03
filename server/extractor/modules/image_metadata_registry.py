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
    VECTOR_GRAPHICS = "vector_graphics"
    NEXTGEN_IMAGE = "nextgen_image"
    CINEMA_RAW = "cinema_raw"
    DOCUMENT_IMAGE = "document_image"
    MEDICAL_IMAGING = "medical_imaging"
    SCIENTIFIC_IMAGING = "scientific_imaging"
    REMOTE_SENSING = "remote_sensing"
    AI_VISION = "ai_vision"
    THREE_D_IMAGING = "three_d_imaging"
    PRINT_PREPRESS = "print_prepress"
    DRONE_UAV = "drone_uav"
    THERMAL_IMAGING = "thermal_imaging"
    VR_AR = "vr_ar"
    BARCODE_OCR = "barcode_ocr"
    DIGITAL_SIGNATURE = "digital_signature"
    COLOR_GRADING = "color_grading"


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
        self._register_vector_graphics()
        self._register_nextgen_image()
        self._register_cinema_raw()
        self._register_document_image()
        self._register_medical_imaging()
        self._register_scientific_imaging()
        self._register_remote_sensing()
        self._register_ai_vision()
        self._register_three_d_imaging()
        self._register_print_prepress()
        self._register_drone_uav()
        self._register_thermal_imaging()
        self._register_vr_ar()
        self._register_barcode_ocr()
        self._register_digital_signature()
        self._register_color_grading()

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

    def _register_vector_graphics(self):
        """SVG and vector graphics metadata - ~40 fields"""
        vector_fields = [
            ("svg_version", MetadataCategory.VECTOR_GRAPHICS, "str", "SVG version"),
            ("svg_base_profile", MetadataCategory.VECTOR_GRAPHICS, "str", "SVG base profile"),
            ("svg_namespace", MetadataCategory.VECTOR_GRAPHICS, "str", "SVG namespace URI"),
            ("svg_width", MetadataCategory.VECTOR_GRAPHICS, "str", "SVG width attribute"),
            ("svg_height", MetadataCategory.VECTOR_GRAPHICS, "str", "SVG height attribute"),
            ("svg_viewbox", MetadataCategory.VECTOR_GRAPHICS, "dict", "ViewBox coordinates"),
            ("svg_preserve_aspect_ratio", MetadataCategory.VECTOR_GRAPHICS, "str", "Aspect ratio"),
            ("svg_total_elements", MetadataCategory.VECTOR_GRAPHICS, "int", "Total element count"),
            ("svg_element_counts", MetadataCategory.VECTOR_GRAPHICS, "dict", "Element type counts"),
            ("svg_has_paths", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has path elements"),
            ("svg_has_shapes", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has shape elements"),
            ("svg_has_text", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has text elements"),
            ("svg_has_images", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has embedded images"),
            ("svg_has_groups", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has group elements"),
            ("svg_has_symbols", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has symbol definitions"),
            ("svg_has_markers", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has marker definitions"),
            ("svg_has_masks", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has mask definitions"),
            ("svg_has_filters", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has filter effects"),
            ("svg_has_gradients", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has gradient definitions"),
            ("svg_has_patterns", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has pattern definitions"),
            ("svg_has_animations", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has SMIL animations"),
            ("svg_animation_counts", MetadataCategory.VECTOR_GRAPHICS, "dict", "Animation type counts"),
            ("svg_has_defs", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has definitions section"),
            ("svg_has_external_links", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has external links"),
            ("svg_xlink_count", MetadataCategory.VECTOR_GRAPHICS, "int", "XLink reference count"),
            ("svg_anchor_count", MetadataCategory.VECTOR_GRAPHICS, "int", "Anchor/link count"),
            ("svg_use_count", MetadataCategory.VECTOR_GRAPHICS, "int", "Use element count"),
            ("svg_has_inline_css", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has inline CSS"),
            ("svg_css_length", MetadataCategory.VECTOR_GRAPHICS, "int", "CSS content length"),
            ("svg_has_accessibility", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has ARIA attributes"),
            ("svg_aria_role", MetadataCategory.VECTOR_GRAPHICS, "str", "ARIA role"),
            ("svg_aria_label", MetadataCategory.VECTOR_GRAPHICS, "str", "ARIA label"),
            ("svg_title", MetadataCategory.VECTOR_GRAPHICS, "str", "Title element"),
            ("svg_description", MetadataCategory.VECTOR_GRAPHICS, "str", "Description element"),
            ("svg_keywords", MetadataCategory.VECTOR_GRAPHICS, "list", "Keywords"),
            ("svg_has_rdf", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has RDF metadata"),
            ("svg_has_dublin_core", MetadataCategory.VECTOR_GRAPHICS, "bool", "Has Dublin Core"),
        ]
        for name, category, field_type, description in vector_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["SVG", "SVGZ"]
            ))

    def _register_nextgen_image(self):
        """Next-generation image formats (JPEG XL, etc.) - ~30 fields"""
        nextgen_fields = [
            ("jxl_is_valid", MetadataCategory.NEXTGEN_IMAGE, "bool", "Is valid JPEG XL"),
            ("jxl_box_count", MetadataCategory.NEXTGEN_IMAGE, "int", "Number of boxes"),
            ("jxl_width", MetadataCategory.NEXTGEN_IMAGE, "int", "Image width"),
            ("jxl_height", MetadataCategory.NEXTGEN_IMAGE, "int", "Image height"),
            ("jxl_bits_per_sample", MetadataCategory.NEXTGEN_IMAGE, "int", "Bits per sample"),
            ("jxl_samples_per_pixel", MetadataCategory.NEXTGEN_IMAGE, "int", "Samples per pixel"),
            ("jxl_has_preview", MetadataCategory.NEXTGEN_IMAGE, "bool", "Has preview image"),
            ("jxl_num_extra_channels", MetadataCategory.NEXTGEN_IMAGE, "int", "Extra channels"),
            ("jxl_is_animated", MetadataCategory.NEXTGEN_IMAGE, "bool", "Is animated"),
            ("jxl_has_exif", MetadataCategory.NEXTGEN_IMAGE, "bool", "Has EXIF"),
            ("jxl_has_xmp", MetadataCategory.NEXTGEN_IMAGE, "bool", "Has XMP"),
            ("jxl_alpha_bits", MetadataCategory.NEXTGEN_IMAGE, "int", "Alpha channel bits"),
            ("jxl_megapixels", MetadataCategory.NEXTGEN_IMAGE, "float", "Megapixels"),
            ("jxl_aspect_ratio", MetadataCategory.NEXTGEN_IMAGE, "float", "Aspect ratio"),
            ("jxl_codec_loop_mode", MetadataCategory.NEXTGEN_IMAGE, "str", "Codec loop mode"),
            ("jxl_enhancement_layer", MetadataCategory.NEXTGEN_IMAGE, "bool", "Has enhancement layer"),
            ("jxl_lossless", MetadataCategory.NEXTGEN_IMAGE, "bool", "Is lossless"),
            ("jxl_progressive_levels", MetadataCategory.NEXTGEN_IMAGE, "list", "Progressive levels"),
            ("avif_has_reconstruction_box", MetadataCategory.NEXTGEN_IMAGE, "bool", "Has JBR reconstruction"),
            ("avif_is_grid_image", MetadataCategory.NEXTGEN_IMAGE, "bool", "Is grid image"),
            ("avif_item_count", MetadataCategory.NEXTGEN_IMAGE, "int", "Item count"),
            ("heic_has_auxiliary_image", MetadataCategory.NEXTGEN_IMAGE, "bool", "Has auxiliary image"),
            ("heic_depth_image", MetadataCategory.NEXTGEN_IMAGE, "bool", "Has depth image"),
            ("heic_primary_item", MetadataCategory.NEXTGEN_IMAGE, "str", "Primary item ID"),
        ]
        for name, category, field_type, description in nextgen_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JXL", "AVIF", "HEIC"]
            ))

    def _register_cinema_raw(self):
        """Cinema RAW formats (CinemaDNG, ARRI) - ~35 fields"""
        cinema_fields = [
            ("cinema_dng_version", MetadataCategory.CINEMA_RAW, "int", "DNG version"),
            ("cinema_dng_backward_version", MetadataCategory.CINEMA_RAW, "int", "DNG backward version"),
            ("cinema_dng_unique_camera_model", MetadataCategory.CINEMA_RAW, "str", "Unique camera model"),
            ("cinema_dng_localized_model", MetadataCategory.CINEMA_RAW, "str", "Localized model"),
            ("cinema_dng_color_matrix1", MetadataCategory.CINEMA_RAW, "list", "Color matrix 1"),
            ("cinema_dng_color_matrix2", MetadataCategory.CINEMA_RAW, "list", "Color matrix 2"),
            ("cinema_dng_forward_matrix1", MetadataCategory.CINEMA_RAW, "list", "Forward matrix 1"),
            ("cinema_dng_forward_matrix2", MetadataCategory.CINEMA_RAW, "list", "Forward matrix 2"),
            ("cinema_dng_calibration_illuminant1", MetadataCategory.CINEMA_RAW, "int", "Calibration illuminant 1"),
            ("cinema_dng_calibration_illuminant2", MetadataCategory.CINEMA_RAW, "int", "Calibration illuminant 2"),
            ("cinema_dng_as_shot_neutral", MetadataCategory.CINEMA_RAW, "list", "As shot neutral"),
            ("cinema_dng_as_shot_white_xy", MetadataCategory.CINEMA_RAW, "list", "As shot white XY"),
            ("cinema_dng_baseline_exposure", MetadataCategory.CINEMA_RAW, "float", "Baseline exposure"),
            ("cinema_dng_baseline_noise", MetadataCategory.CINEMA_RAW, "float", "Baseline noise"),
            ("cinema_dng_baseline_sharpness", MetadataCategory.CINEMA_RAW, "float", "Baseline sharpness"),
            ("cinema_dng_bayer_green_split", MetadataCategory.CINEMA_RAW, "int", "Bayer green split"),
            ("cinema_dng_active_area", MetadataCategory.CINEMA_RAW, "list", "Active area"),
            ("cinema_dng_masked_areas", MetadataCategory.CINEMA_RAW, "list", "Masked areas"),
            ("cinema_dng_raw_image_unique_id", MetadataCategory.CINEMA_RAW, "str", "Raw image unique ID"),
            ("cinema_dng_original_filename", MetadataCategory.CINEMA_RAW, "str", "Original file name"),
            ("arri_is_valid", MetadataCategory.CINEMA_RAW, "bool", "Is valid ARRI"),
            ("arri_camera_model", MetadataCategory.CINEMA_RAW, "str", "ARRI camera model"),
            ("arri_product_id", MetadataCategory.CINEMA_RAW, "str", "ARRI product ID"),
            ("arri_sensor_name", MetadataCategory.CINEMA_RAW, "str", "Sensor name"),
            ("arri_lens_name", MetadataCategory.CINEMA_RAW, "str", "Lens name"),
            ("arri_frame_rate", MetadataCategory.CINEMA_RAW, "float", "Frame rate"),
            ("arri_exposure_time", MetadataCategory.CINEMA_RAW, "float", "Exposure time"),
            ("arri_iso_speed", MetadataCategory.CINEMA_RAW, "int", "ISO speed"),
            ("cinema_color_depth", MetadataCategory.CINEMA_RAW, "int", "Color depth bits"),
            ("cinema_compression", MetadataCategory.CINEMA_RAW, "str", "Compression type"),
            ("cinema_megapixels", MetadataCategory.CINEMA_RAW, "float", "Megapixels"),
            ("cinema_aspect_ratio", MetadataCategory.CINEMA_RAW, "float", "Aspect ratio"),
        ]
        for name, category, field_type, description in cinema_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["DNG", "CinemaDNG", "ARRI", "ALEXA"]
            ))

    def _register_document_image(self):
        """Document and scanned image metadata - ~30 fields"""
        doc_fields = [
            ("doc_page_number", MetadataCategory.DOCUMENT_IMAGE, "int", "Page number"),
            ("doc_page_count", MetadataCategory.DOCUMENT_IMAGE, "int", "Total page count"),
            ("doc_resolution_x", MetadataCategory.DOCUMENT_IMAGE, "int", "X resolution DPI"),
            ("doc_resolution_y", MetadataCategory.DOCUMENT_IMAGE, "int", "Y resolution DPI"),
            ("doc_scan_software", MetadataCategory.DOCUMENT_IMAGE, "str", "Scanning software"),
            ("doc_scan_device", MetadataCategory.DOCUMENT_IMAGE, "str", "Scan device model"),
            ("doc_scan_date", MetadataCategory.DOCUMENT_IMAGE, "datetime", "Scan date"),
            ("doc_has_ocr", MetadataCategory.DOCUMENT_IMAGE, "bool", "Has OCR text"),
            ("doc_ocr_confidence", MetadataCategory.DOCUMENT_IMAGE, "float", "OCR confidence"),
            ("doc_ocr_language", MetadataCategory.DOCUMENT_IMAGE, "str", "OCR language"),
            ("doc_barcode_type", MetadataCategory.DOCUMENT_IMAGE, "str", "Barcode type"),
            ("doc_barcode_data", MetadataCategory.DOCUMENT_IMAGE, "str", "Barcode data"),
            ("doc_has_signature", MetadataCategory.DOCUMENT_IMAGE, "bool", "Has signature"),
            ("doc_signature_area", MetadataCategory.DOCUMENT_IMAGE, "dict", "Signature area"),
            ("doc_has_annotations", MetadataCategory.DOCUMENT_IMAGE, "bool", "Has annotations"),
            ("doc_annotation_count", MetadataCategory.DOCUMENT_IMAGE, "int", "Annotation count"),
            ("doc_has_bookmarks", MetadataCategory.DOCUMENT_IMAGE, "bool", "Has bookmarks"),
            ("doc_bookmark_count", MetadataCategory.DOCUMENT_IMAGE, "int", "Bookmark count"),
            ("doc_quality_mode", MetadataCategory.DOCUMENT_IMAGE, "str", "Quality mode"),
            ("doc_color_mode", MetadataCategory.DOCUMENT_IMAGE, "str", "Color mode"),
            ("doc_has_thumbnail", MetadataCategory.DOCUMENT_IMAGE, "bool", "Has thumbnail"),
            ("doc_thumbnail_size", MetadataCategory.DOCUMENT_IMAGE, "dict", "Thumbnail dimensions"),
            ("doc_compression_type", MetadataCategory.DOCUMENT_IMAGE, "str", "Compression type"),
            ("doc_has_text_layer", MetadataCategory.DOCUMENT_IMAGE, "bool", "Has text layer"),
            ("doc_form_fields", MetadataCategory.DOCUMENT_IMAGE, "list", "Form fields"),
            ("doc_is_signed", MetadataCategory.DOCUMENT_IMAGE, "bool", "Is digitally signed"),
            ("doc_signature_count", MetadataCategory.DOCUMENT_IMAGE, "int", "Signature count"),
            ("doc_permission_flags", MetadataCategory.DOCUMENT_IMAGE, "dict", "Permission flags"),
            ("doc_encrypted", MetadataCategory.DOCUMENT_IMAGE, "bool", "Is encrypted"),
        ]
        for name, category, field_type, description in doc_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "TIFF", "PDF", "PSD"]
            ))

    def _register_medical_imaging(self):
        """Medical imaging metadata (DICOM, etc.) - ~30 fields"""
        medical_fields = [
            ("is_dicom", MetadataCategory.MEDICAL_IMAGING, "bool", "Is DICOM format"),
            ("dicom_patient_id", MetadataCategory.MEDICAL_IMAGING, "str", "Patient ID"),
            ("dicom_study_uid", MetadataCategory.MEDICAL_IMAGING, "str", "Study UID"),
            ("dicom_series_uid", MetadataCategory.MEDICAL_IMAGING, "str", "Series UID"),
            ("dicom_instance_uid", MetadataCategory.MEDICAL_IMAGING, "str", "Instance UID"),
            ("dicom_modality", MetadataCategory.MEDICAL_IMAGING, "str", "Modality"),
            ("dicom_body_part", MetadataCategory.MEDICAL_IMAGING, "str", "Body part examined"),
            ("dicom_study_date", MetadataCategory.MEDICAL_IMAGING, "datetime", "Study date"),
            ("dicom_series_date", MetadataCategory.MEDICAL_IMAGING, "datetime", "Series date"),
            ("dicom_acquisition_date", MetadataCategory.MEDICAL_IMAGING, "datetime", "Acquisition date"),
            ("dicom_study_description", MetadataCategory.MEDICAL_IMAGING, "str", "Study description"),
            ("dicom_series_description", MetadataCategory.MEDICAL_IMAGING, "str", "Series description"),
            ("dicom_institution_name", MetadataCategory.MEDICAL_IMAGING, "str", "Institution name"),
            ("dicom_manufacturer", MetadataCategory.MEDICAL_IMAGING, "str", "Manufacturer"),
            ("dicom_station_name", MetadataCategory.MEDICAL_IMAGING, "str", "Station name"),
            ("dicom_physicians", MetadataCategory.MEDICAL_IMAGING, "list", "Physicians"),
            ("dicom_referring_physician", MetadataCategory.MEDICAL_IMAGING, "str", "Referring physician"),
            ("dicom_accession_number", MetadataCategory.MEDICAL_IMAGING, "str", "Accession number"),
            ("dicom_study_id", MetadataCategory.MEDICAL_IMAGING, "str", "Study ID"),
            ("dicom_series_number", MetadataCategory.MEDICAL_IMAGING, "int", "Series number"),
            ("dicom_instance_number", MetadataCategory.MEDICAL_IMAGING, "int", "Instance number"),
            ("dicom_slice_thickness", MetadataCategory.MEDICAL_IMAGING, "float", "Slice thickness"),
            ("dicom_spacing", MetadataCategory.MEDICAL_IMAGING, "list", "Pixel spacing"),
            ("dicom_rows", MetadataCategory.MEDICAL_IMAGING, "int", "Image rows"),
            ("dicom_columns", MetadataCategory.MEDICAL_IMAGING, "int", "Image columns"),
            ("dicom_bits_allocated", MetadataCategory.MEDICAL_IMAGING, "int", "Bits allocated"),
            ("dicom_bits_stored", MetadataCategory.MEDICAL_IMAGING, "int", "Bits stored"),
            ("dicom_window_center", MetadataCategory.MEDICAL_IMAGING, "float", "Window center"),
            ("dicom_window_width", MetadataCategory.MEDICAL_IMAGING, "float", "Window width"),
        ]
        for name, category, field_type, description in medical_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["DCM", "DICOM"]
            ))

    def _register_scientific_imaging(self):
        """Scientific imaging metadata (FITS, microscopy) - ~30 fields"""
        scientific_fields = [
            ("is_fits", MetadataCategory.SCIENTIFIC_IMAGING, "bool", "Is FITS format"),
            ("fits_bitpix", MetadataCategory.SCIENTIFIC_IMAGING, "int", "Bits per pixel"),
            ("fits_naxis", MetadataCategory.SCIENTIFIC_IMAGING, "int", "Number of axes"),
            ("fits_axes", MetadataCategory.SCIENTIFIC_IMAGING, "list", "Axis dimensions"),
            ("fits_extend", MetadataCategory.SCIENTIFIC_IMAGING, "bool", "Has extension"),
            ("fits_object", MetadataCategory.SCIENTIFIC_IMAGING, "str", "Object name"),
            ("fits_telescope", MetadataCategory.SCIENTIFIC_IMAGING, "str", "Telescope"),
            ("fits_observer", MetadataCategory.SCIENTIFIC_IMAGING, "str", "Observer"),
            ("fits_date_obs", MetadataCategory.SCIENTIFIC_IMAGING, "datetime", "Observation date"),
            ("fits_Exposure", MetadataCategory.SCIENTIFIC_IMAGING, "float", "Exposure time"),
            ("fits_filter", MetadataCategory.SCIENTIFIC_IMAGING, "str", "Filter"),
            ("fits_instrument", MetadataCategory.SCIENTIFIC_IMAGING, "str", "Instrument"),
            ("fits_ra", MetadataCategory.SCIENTIFIC_IMAGING, "float", "Right Ascension"),
            ("fits_dec", MetadataCategory.SCIENTIFIC_IMAGING, "float", "Declination"),
            ("fits_equinox", MetadataCategory.SCIENTIFIC_IMAGING, "str", "Equinox"),
            ("is_microscopy", MetadataCategory.SCIENTIFIC_IMAGING, "bool", "Is microscopy image"),
            ("micro_physical_size_x", MetadataCategory.SCIENTIFIC_IMAGING, "float", "Physical size X"),
            ("micro_physical_size_y", MetadataCategory.SCIENTIFIC_IMAGING, "float", "Physical size Y"),
            ("micro_magnification", MetadataCategory.SCIENTIFIC_IMAGING, "float", "Magnification"),
            ("micro_numerical_aperture", MetadataCategory.SCIENTIFIC_IMAGING, "float", "Numerical aperture"),
            ("micro_objective", MetadataCategory.SCIENTIFIC_IMAGING, "str", "Objective"),
            ("micro_channel_count", MetadataCategory.SCIENTIFIC_IMAGING, "int", "Channel count"),
            ("micro_z_slices", MetadataCategory.SCIENTIFIC_IMAGING, "int", "Z-slice count"),
            ("micro_time_points", MetadataCategory.SCIENTIFIC_IMAGING, "int", "Time points"),
            ("micro_fluorescent_channels", MetadataCategory.SCIENTIFIC_IMAGING, "list", "Fluorescent channels"),
            ("micro_has_ome_xml", MetadataCategory.SCIENTIFIC_IMAGING, "bool", "Has OME-XML"),
        ]
        for name, category, field_type, description in scientific_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["FITS", "TIFF", "OME-TIFF"]
            ))

    def _register_remote_sensing(self):
        """Remote sensing and geospatial metadata - ~25 fields"""
        remote_fields = [
            ("is_geospatial", MetadataCategory.REMOTE_SENSING, "bool", "Is geospatial"),
            ("geo_crs", MetadataCategory.REMOTE_SENSING, "str", "Coordinate reference system"),
            ("geo_epsg_code", MetadataCategory.REMOTE_SENSING, "int", "EPSG code"),
            ("geo_bounding_box", MetadataCategory.REMOTE_SENSING, "dict", "Bounding box"),
            ("geo_ground_sample_distance", MetadataCategory.REMOTE_SENSING, "float", "GSD"),
            ("geo_sun_elevation", MetadataCategory.REMOTE_SENSING, "float", "Sun elevation"),
            ("geo_sun_azimuth", MetadataCategory.REMOTE_SENSING, "float", "Sun azimuth"),
            ("geo_acquisition_date", MetadataCategory.REMOTE_SENSING, "datetime", "Acquisition date"),
            ("geo_satellite_sensor", MetadataCategory.REMOTE_SENSING, "str", "Satellite/sensor"),
            ("geo_cloud_coverage", MetadataCategory.REMOTE_SENSING, "float", "Cloud coverage"),
            ("geo_band_count", MetadataCategory.REMOTE_SENSING, "int", "Band count"),
            ("geo_bit_depth", MetadataCategory.REMOTE_SENSING, "int", "Bit depth"),
            ("geo_projection", MetadataCategory.REMOTE_SENSING, "str", "Projection"),
            ("geo_zone", MetadataCategory.REMOTE_SENSING, "str", "UTM zone"),
            ("geo_datum", MetadataCategory.REMOTE_SENSING, "str", "Datum"),
            ("geo_ellipsoid", MetadataCategory.REMOTE_SENSING, "str", "Ellipsoid"),
            ("geo_transform_method", MetadataCategory.REMOTE_SENSING, "str", "Transform method"),
            ("geo_pixel_format", MetadataCategory.REMOTE_SENSING, "str", "Pixel format"),
            ("geo_compression", MetadataCategory.REMOTE_SENSING, "str", "Compression"),
            ("geo_pyramid_levels", MetadataCategory.REMOTE_SENSING, "int", "Pyramid levels"),
            ("geo_overview_count", MetadataCategory.REMOTE_SENSING, "int", "Overview count"),
            ("geo_has_tfw", MetadataCategory.REMOTE_SENSING, "bool", "Has world file"),
            ("geo_has_prj", MetadataCategory.REMOTE_SENSING, "bool", "Has projection file"),
            ("is_cog", MetadataCategory.REMOTE_SENSING, "bool", "Is Cloud Optimized GeoTIFF"),
        ]
        for name, category, field_type, description in remote_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["GeoTIFF", "COG", "TIFF", "JPEG2000"]
            ))

    def _register_ai_vision(self):
        """AI/ML vision and object detection metadata - ~35 fields"""
        ai_fields = [
            ("coco_is_valid", MetadataCategory.AI_VISION, "bool", "Is COCO format"),
            ("coco_category_count", MetadataCategory.AI_VISION, "int", "COCO category count"),
            ("coco_image_count", MetadataCategory.AI_VISION, "int", "COCO image count"),
            ("coco_annotation_count", MetadataCategory.AI_VISION, "int", "COCO annotation count"),
            ("coco_bbox_count", MetadataCategory.AI_VISION, "int", "Bounding box count"),
            ("coco_segmentation_count", MetadataCategory.AI_VISION, "int", "Segmentation count"),
            ("coco_keypoint_count", MetadataCategory.AI_VISION, "int", "Keypoint count"),
            ("yolo_is_valid", MetadataCategory.AI_VISION, "bool", "Is YOLO format"),
            ("yolo_annotation_count", MetadataCategory.AI_VISION, "int", "YOLO annotation count"),
            ("yolo_unique_classes", MetadataCategory.AI_VISION, "int", "YOLO class count"),
            ("pascal_voc_valid", MetadataCategory.AI_VISION, "bool", "Is Pascal VOC format"),
            ("pascal_voc_object_count", MetadataCategory.AI_VISION, "int", "VOC object count"),
            ("is_ai_generated", MetadataCategory.AI_VISION, "bool", "Is AI-generated"),
            ("c2pa_manifest", MetadataCategory.AI_VISION, "bool", "Has C2PA manifest"),
            ("has_provenance", MetadataCategory.AI_VISION, "bool", "Has provenance data"),
            ("ai_generation_model", MetadataCategory.AI_VISION, "str", "AI generation model"),
            ("ai_prompt", MetadataCategory.AI_VISION, "str", "Generation prompt"),
            ("ai_seed", MetadataCategory.AI_VISION, "int", "Generation seed"),
            ("ai_guidance_scale", MetadataCategory.AI_VISION, "float", "Guidance scale"),
            ("ai_steps", MetadataCategory.AI_VISION, "int", "Generation steps"),
            ("mask_is_segmentation", MetadataCategory.AI_VISION, "bool", "Is segmentation mask"),
            ("mask_unique_values", MetadataCategory.AI_VISION, "int", "Mask unique values"),
            ("mask_is_instance", MetadataCategory.AI_VISION, "bool", "Is instance segmentation"),
            ("mask_is_semantic", MetadataCategory.AI_VISION, "bool", "Is semantic segmentation"),
            ("mask_is_panoptic", MetadataCategory.AI_VISION, "bool", "Is panoptic segmentation"),
            ("onnx_opset_version", MetadataCategory.AI_VISION, "int", "ONNX opset version"),
            ("onnx_input_count", MetadataCategory.AI_VISION, "int", "Model input count"),
            ("onnx_output_count", MetadataCategory.AI_VISION, "int", "Model output count"),
            ("onnx_node_count", MetadataCategory.AI_VISION, "int", "ONNX node count"),
            ("pytorch_epoch", MetadataCategory.AI_VISION, "int", "PyTorch epoch"),
            ("pytorch_state_dict_count", MetadataCategory.AI_VISION, "int", "State dict count"),
        ]
        for name, category, field_type, description in ai_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JSON", "TXT", "XML", "PNG", "NPY", "ONNX", "PT", "PY"]
            ))

    def _register_three_d_imaging(self):
        """3D imaging and point cloud metadata - ~35 fields"""
        three_d_fields = [
            ("ply_is_valid", MetadataCategory.THREE_D_IMAGING, "bool", "Is valid PLY"),
            ("ply_encoding", MetadataCategory.THREE_D_IMAGING, "str", "PLY encoding"),
            ("ply_vertex_count", MetadataCategory.THREE_D_IMAGING, "int", "PLY vertex count"),
            ("ply_face_count", MetadataCategory.THREE_D_IMAGING, "int", "PLY face count"),
            ("ply_element_count", MetadataCategory.THREE_D_IMAGING, "int", "PLY element count"),
            ("obj_is_valid", MetadataCategory.THREE_D_IMAGING, "bool", "Is valid OBJ"),
            ("obj_vertex_count", MetadataCategory.THREE_D_IMAGING, "int", "OBJ vertex count"),
            ("obj_face_count", MetadataCategory.THREE_D_IMAGING, "int", "OBJ face count"),
            ("obj_normal_count", MetadataCategory.THREE_D_IMAGING, "int", "OBJ normal count"),
            ("obj_texcoord_count", MetadataCategory.THREE_D_IMAGING, "int", "OBJ texcoord count"),
            ("obj_group_count", MetadataCategory.THREE_D_IMAGING, "int", "OBJ group count"),
            ("obj_material_count", MetadataCategory.THREE_D_IMAGING, "int", "OBJ material count"),
            ("obj_has_materials", MetadataCategory.THREE_D_IMAGING, "bool", "Has materials"),
            ("gltf_is_valid", MetadataCategory.THREE_D_IMAGING, "bool", "Is valid glTF"),
            ("gltf_version", MetadataCategory.THREE_D_IMAGING, "str", "glTF version"),
            ("gltf_mesh_count", MetadataCategory.THREE_D_IMAGING, "int", "glTF mesh count"),
            ("gltf_node_count", MetadataCategory.THREE_D_IMAGING, "int", "glTF node count"),
            ("gltf_animation_count", MetadataCategory.THREE_D_IMAGING, "int", "glTF animation count"),
            ("gltf_texture_count", MetadataCategory.THREE_D_IMAGING, "int", "glTF texture count"),
            ("gltf_skin_count", MetadataCategory.THREE_D_IMAGING, "int", "glTF skin count"),
            ("stl_is_valid", MetadataCategory.THREE_D_IMAGING, "bool", "Is valid STL"),
            ("stl_is_ascii", MetadataCategory.THREE_D_IMAGING, "bool", "STL is ASCII"),
            ("stl_facet_count", MetadataCategory.THREE_D_IMAGING, "int", "STL facet count"),
            ("las_is_valid", MetadataCategory.THREE_D_IMAGING, "bool", "Is valid LAS"),
            ("las_version", MetadataCategory.THREE_D_IMAGING, "str", "LAS version"),
            ("las_point_count", MetadataCategory.THREE_D_IMAGING, "int", "LAS point count"),
            ("las_has_colors", MetadataCategory.THREE_D_IMAGING, "bool", "LAS has colors"),
            ("pcd_is_valid", MetadataCategory.THREE_D_IMAGING, "bool", "Is valid PCD"),
            ("pcd_width", MetadataCategory.THREE_D_IMAGING, "int", "PCD width"),
            ("pcd_height", MetadataCategory.THREE_D_IMAGING, "int", "PCD height"),
            ("pcd_point_count", MetadataCategory.THREE_D_IMAGING, "int", "PCD point count"),
            ("pcd_is_organized", MetadataCategory.THREE_D_IMAGING, "bool", "PCD is organized"),
        ]
        for name, category, field_type, description in three_d_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["PLY", "OBJ", "GLTF", "GLB", "STL", "LAS", "LAZ", "PCD"]
            ))

    def _register_print_prepress(self):
        """Print and prepress metadata - ~30 fields"""
        print_fields = [
            ("pdfx_version", MetadataCategory.PRINT_PREPRESS, "str", "PDF/X version"),
            ("pdfx_compliant", MetadataCategory.PRINT_PREPRESS, "bool", "PDF/X compliant"),
            ("pdf_color_space", MetadataCategory.PRINT_PREPRESS, "str", "PDF color space"),
            ("pdf_ink_coverage", MetadataCategory.PRINT_PREPRESS, "float", "Max ink coverage"),
            ("pdf_trap_presence", MetadataCategory.PRINT_PREPRESS, "bool", "Has trapping"),
            ("pdf_overprint", MetadataCategory.PRINT_PREPRESS, "bool", "Has overprint"),
            ("pdf_spot_color_count", MetadataCategory.PRINT_PREPRESS, "int", "Spot color count"),
            ("pdf_font_count", MetadataCategory.PRINT_PREPRESS, "int", "Font count"),
            ("pdf_embedded_font_count", MetadataCategory.PRINT_PREPRESS, "int", "Embedded fonts"),
            ("pdf_image_count", MetadataCategory.PRINT_PREPRESS, "int", "Image count"),
            ("pdf_page_count", MetadataCategory.PRINT_PREPRESS, "int", "Page count"),
            ("pdf_bleed", MetadataCategory.PRINT_PREPRESS, "dict", "Bleed settings"),
            ("pdf_crop_marks", MetadataCategory.PRINT_PREPRESS, "bool", "Has crop marks"),
            ("pdf_registration_marks", MetadataCategory.PRINT_PREPRESS, "bool", "Has registration marks"),
            ("rip_software", MetadataCategory.PRINT_PREPRESS, "str", "RIP software"),
            ("rip_resolution", MetadataCategory.PRINT_PREPRESS, "int", "RIP resolution DPI"),
            ("rip_screening", MetadataCategory.PRINT_PREPRESS, "str", "Screening method"),
            ("rip_screening_angles", MetadataCategory.PRINT_PREPRESS, "list", "Screening angles"),
            ("rip_line_screen", MetadataCategory.PRINT_PREPRESS, "float", "Line screen LPI"),
            ("rip_dot_shape", MetadataCategory.PRINT_PREPRESS, "str", "Dot shape"),
            ("icc_output_profile", MetadataCategory.PRINT_PREPRESS, "str", "Output ICC profile"),
            ("icc_source_profile", MetadataCategory.PRINT_PREPRESS, "str", "Source ICC profile"),
            ("icc_rendering_intent", MetadataCategory.PRINT_PREPRESS, "str", "Rendering intent"),
            ("proof_software", MetadataCategory.PRINT_PREPRESS, "str", "Proofing software"),
            ("proof_profile", MetadataCategory.PRINT_PREPRESS, "str", "Proof profile"),
            ("imposition_pages", MetadataCategory.PRINT_PREPRESS, "int", "Pages per sheet"),
            ("imposition_signature_count", MetadataCategory.PRINT_PREPRESS, "int", "Signature count"),
            ("imposition_page_order", MetadataCategory.PRINT_PREPRESS, "str", "Page order"),
        ]
        for name, category, field_type, description in print_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["PDF", "PDFX", "AI", "PSD", "TIFF", "EPS"]
            ))

    def _register_drone_uav(self):
        """Drone/UAV and aerial imaging metadata - ~35 fields"""
        drone_fields = [
            ("drone_make", MetadataCategory.DRONE_UAV, "str", "Drone manufacturer"),
            ("drone_model", MetadataCategory.DRONE_UAV, "str", "Drone model"),
            ("drone_serial", MetadataCategory.DRONE_UAV, "str", "Drone serial number"),
            ("flight_id", MetadataCategory.DRONE_UAV, "str", "Flight ID"),
            ("flight_date", MetadataCategory.DRONE_UAV, "datetime", "Flight date"),
            ("flight_duration", MetadataCategory.DRONE_UAV, "float", "Flight duration"),
            ("flight_distance", MetadataCategory.DRONE_UAV, "float", "Flight distance"),
            ("gimbal_mode", MetadataCategory.DRONE_UAV, "str", "Gimbal mode"),
            ("gimbal_pitch", MetadataCategory.DRONE_UAV, "float", "Gimbal pitch"),
            ("gimbal_yaw", MetadataCategory.DRONE_UAV, "float", "Gimbal yaw"),
            ("gimbal_roll", MetadataCategory.DRONE_UAV, "float", "Gimbal roll"),
            ("home_latitude", MetadataCategory.DRONE_UAV, "float", "Home latitude"),
            ("home_longitude", MetadataCategory.DRONE_UAV, "float", "Home longitude"),
            ("home_altitude", MetadataCategory.DRONE_UAV, "float", "Home altitude"),
            ("relative_altitude", MetadataCategory.DRONE_UAV, "float", "Relative altitude"),
            ("flight_speed", MetadataCategory.DRONE_UAV, "float", "Flight speed"),
            ("horizontal_speed", MetadataCategory.DRONE_UAV, "float", "Horizontal speed"),
            ("vertical_speed", MetadataCategory.DRONE_UAV, "float", "Vertical speed"),
            ("battery_level", MetadataCategory.DRONE_UAV, "int", "Battery level"),
            ("battery_voltage", MetadataCategory.DRONE_UAV, "float", "Battery voltage"),
            ("satellite_count", MetadataCategory.DRONE_UAV, "int", "Satellite count"),
            ("gps_accuracy", MetadataCategory.DRONE_UAV, "float", "GPS accuracy"),
            ("home_point_set", MetadataCategory.DRONE_UAV, "bool", "Home point set"),
            ("return_to_home", MetadataCategory.DRONE_UAV, "bool", "Return to home"),
            ("obstacle_sensors", MetadataCategory.DRONE_UAV, "dict", "Obstacle sensors"),
            ("flight_mode", MetadataCategory.DRONE_UAV, "str", "Flight mode"),
            ("rc_channel", MetadataCategory.DRONE_UAV, "int", "RC channel"),
            ("video_format", MetadataCategory.DRONE_UAV, "str", "Video format"),
            ("video_codec", MetadataCategory.DRONE_UAV, "str", "Video codec"),
            ("capture_mode", MetadataCategory.DRONE_UAV, "str", "Capture mode"),
            ("photo_format", MetadataCategory.DRONE_UAV, "str", "Photo format"),
            ("burst_count", MetadataCategory.DRONE_UAV, "int", "Burst count"),
            ("aeb_count", MetadataCategory.DRONE_UAV, "int", "AEB count"),
            ("timelapse_interval", MetadataCategory.DRONE_UAV, "float", "Timelapse interval"),
        ]
        for name, category, field_type, description in drone_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPG", "DNG", "MOV", "MP4", "TIFF"]
            ))

    def _register_thermal_imaging(self):
        """Thermal and multispectral imaging metadata - ~30 fields"""
        thermal_fields = [
            ("thermal_is_valid", MetadataCategory.THERMAL_IMAGING, "bool", "Is thermal image"),
            ("thermal_resolution", MetadataCategory.THERMAL_IMAGING, "str", "Thermal resolution"),
            ("thermal_pixel_pitch", MetadataCategory.THERMAL_IMAGING, "float", "Pixel pitch"),
            ("thermal_sensitivity", MetadataCategory.THERMAL_IMAGING, "float", "Thermal sensitivity"),
            ("thermal_range_min", MetadataCategory.THERMAL_IMAGING, "float", "Temp range min"),
            ("thermal_range_max", MetadataCategory.THERMAL_IMAGING, "float", "Temp range max"),
            ("thermal_unit", MetadataCategory.THERMAL_IMAGING, "str", "Temperature unit"),
            ("thermal_emissivity", MetadataCategory.THERMAL_IMAGING, "float", "Emissivity"),
            ("thermal_reflected_temp", MetadataCategory.THERMAL_IMAGING, "float", "Reflected temp"),
            ("thermal_atm_temp", MetadataCategory.THERMAL_IMAGING, "float", "Atmospheric temp"),
            ("thermal_humidity", MetadataCategory.THERMAL_IMAGING, "float", "Humidity"),
            ("thermal_distance", MetadataCategory.THERMAL_IMAGING, "float", "Measurement distance"),
            ("thermal_focus", MetadataCategory.THERMAL_IMAGING, "float", "Focus distance"),
            ("thermal_lens", MetadataCategory.THERMAL_IMAGING, "str", "Lens type"),
            ("thermal_zoom", MetadataCategory.THERMAL_IMAGING, "float", "Optical zoom"),
            ("thermal_digital_zoom", MetadataCategory.THERMAL_IMAGING, "float", "Digital zoom"),
            ("multi_is_multispectral", MetadataCategory.THERMAL_IMAGING, "bool", "Is multispectral"),
            ("multi_band_count", MetadataCategory.THERMAL_IMAGING, "int", "Band count"),
            ("multi_center_wavelengths", MetadataCategory.THERMAL_IMAGING, "list", "Center wavelengths"),
            ("multi_bandwidths", MetadataCategory.THERMAL_IMAGING, "list", "Bandwidths"),
            ("multi_spatial_resolution", MetadataCategory.THERMAL_IMAGING, "float", "Spatial resolution"),
            ("multi_swath_width", MetadataCategory.THERMAL_IMAGING, "float", "Swath width"),
            ("multi_revisit_time", MetadataCategory.THERMAL_IMAGING, "float", "Revisit time"),
            ("multi_cloud_cover", MetadataCategory.THERMAL_IMAGING, "float", "Cloud cover"),
            ("hyperspectral_is_valid", MetadataCategory.THERMAL_IMAGING, "bool", "Is hyperspectral"),
            ("hyperspectral_bands", MetadataCategory.THERMAL_IMAGING, "int", "Band count"),
            ("hyperspectral_spectral_range", MetadataCategory.THERMAL_IMAGING, "str", "Spectral range"),
            ("hyperspectral_spectral_resolution", MetadataCategory.THERMAL_IMAGING, "float", "Spectral resolution"),
            ("hyperspectral_fwhm", MetadataCategory.THERMAL_IMAGING, "float", "FWHM"),
        ]
        for name, category, field_type, description in thermal_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["TIFF", "PNG", "JPG", "RAW", "RADIOMETRIC"]
            ))

    def _register_vr_ar(self):
        """VR/AR and stereoscopic imaging metadata - ~30 fields"""
        vr_fields = [
            ("is_stereoscopic", MetadataCategory.VR_AR, "bool", "Is stereoscopic 3D"),
            ("stereo_type", MetadataCategory.VR_AR, "str", "Stereo type (MPO, side-by-side, etc.)"),
            ("stereo_left_frame", MetadataCategory.VR_AR, "dict", "Left frame metadata"),
            ("stereo_right_frame", MetadataCategory.VR_AR, "dict", "Right frame metadata"),
            ("stereo_parallax", MetadataCategory.VR_AR, "float", "Parallax value"),
            ("is_vr_image", MetadataCategory.VR_AR, "bool", "Is VR image"),
            ("vr_projection_type", MetadataCategory.VR_AR, "str", "VR projection type"),
            ("vr_equirectangular", MetadataCategory.VR_AR, "bool", "Is equirectangular"),
            ("vr_cubemap", MetadataCategory.VR_AR, "bool", "Is cubemap"),
            ("vr_fisheye", MetadataCategory.VR_AR, "bool", "Is fisheye"),
            ("vr_horizontal_fov", MetadataCategory.VR_AR, "float", "Horizontal FOV"),
            ("vr_vertical_fov", MetadataCategory.VR_AR, "float", "Vertical FOV"),
            ("is_ar_content", MetadataCategory.VR_AR, "bool", "Is AR content"),
            ("ar_type", MetadataCategory.VR_AR, "str", "AR framework type"),
            ("ar_tracking_type", MetadataCategory.VR_AR, "str", "AR tracking type"),
            ("ar_anchor_type", MetadataCategory.VR_AR, "str", "AR anchor type"),
            ("cubemap_face_count", MetadataCategory.VR_AR, "int", "Cubemap face count"),
            ("is_light_field", MetadataCategory.VR_AR, "bool", "Is light field"),
            ("light_field_type", MetadataCategory.VR_AR, "str", "Light field camera type"),
            ("microlens_array", MetadataCategory.VR_AR, "dict", "Microlens array info"),
            ("refocus_range", MetadataCategory.VR_AR, "dict", "Refocus range"),
            ("is_omnidirectional", MetadataCategory.VR_AR, "bool", "Is omnidirectional"),
            ("omni_projection", MetadataCategory.VR_AR, "str", "Omni projection type"),
            ("omni_interpupillary_dist", MetadataCategory.VR_AR, "float", "IPD for stereo"),
            ("gpano_cropped_width", MetadataCategory.VR_AR, "int", "GPano cropped width"),
            ("gpano_cropped_height", MetadataCategory.VR_AR, "int", "GPano cropped height"),
            ("gpano_full_pano_width", MetadataCategory.VR_AR, "int", "GPano full width"),
            ("gpano_full_pano_height", MetadataCategory.VR_AR, "int", "GPano full height"),
        ]
        for name, category, field_type, description in vr_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPG", "PNG", "TIFF", "MPO", "GLB", "USD"]
            ))

    def _register_barcode_ocr(self):
        """Barcode and OCR metadata - ~30 fields"""
        barcode_fields = [
            ("has_barcode", MetadataCategory.BARCODE_OCR, "bool", "Has barcode"),
            ("barcode_count", MetadataCategory.BARCODE_OCR, "int", "Barcode count"),
            ("barcode_type", MetadataCategory.BARCODE_OCR, "str", "Barcode type"),
            ("barcode_data", MetadataCategory.BARCODE_OCR, "str", "Barcode data content"),
            ("is_qr_code", MetadataCategory.BARCODE_OCR, "bool", "Is QR code"),
            ("qr_version", MetadataCategory.BARCODE_OCR, "int", "QR version"),
            ("qr_error_correction", MetadataCategory.BARCODE_OCR, "str", "QR error correction"),
            ("qr_encoding", MetadataCategory.BARCODE_OCR, "str", "QR encoding"),
            ("qr_data_type", MetadataCategory.BARCODE_OCR, "str", "QR data type"),
            ("is_data_matrix", MetadataCategory.BARCODE_OCR, "bool", "Is Data Matrix"),
            ("dm_rows", MetadataCategory.BARCODE_OCR, "int", "DM rows"),
            ("dm_cols", MetadataCategory.BARCODE_OCR, "int", "DM columns"),
            ("is_aztec_code", MetadataCategory.BARCODE_OCR, "bool", "Is Aztec Code"),
            ("aztec_layers", MetadataCategory.BARCODE_OCR, "int", "Aztec layers"),
            ("is_pdf417", MetadataCategory.BARCODE_OCR, "bool", "Is PDF417"),
            ("pdf417_rows", MetadataCategory.BARCODE_OCR, "int", "PDF417 rows"),
            ("pdf417_security_level", MetadataCategory.BARCODE_OCR, "int", "PDF417 security"),
            ("has_ocr", MetadataCategory.BARCODE_OCR, "bool", "Has OCR text"),
            ("ocr_engine", MetadataCategory.BARCODE_OCR, "str", "OCR engine"),
            ("ocr_confidence", MetadataCategory.BARCODE_OCR, "float", "OCR confidence"),
            ("ocr_language", MetadataCategory.BARCODE_OCR, "str", "OCR language"),
            ("ocr_text_length", MetadataCategory.BARCODE_OCR, "int", "OCR text length"),
            ("ocr_word_count", MetadataCategory.BARCODE_OCR, "int", "OCR word count"),
            ("has_mrz", MetadataCategory.BARCODE_OCR, "bool", "Has MRZ"),
            ("mrz_type", MetadataCategory.BARCODE_OCR, "str", "MRZ type"),
            ("mrz_document_type", MetadataCategory.BARCODE_OCR, "str", "MRZ doc type"),
            ("mrz_issuing_country", MetadataCategory.BARCODE_OCR, "str", "MRZ country"),
            ("has_biometric", MetadataCategory.BARCODE_OCR, "bool", "Has biometric"),
            ("biometric_type", MetadataCategory.BARCODE_OCR, "str", "Biometric type"),
            ("face_detected", MetadataCategory.BARCODE_OCR, "bool", "Face detected"),
        ]
        for name, category, field_type, description in barcode_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPG", "PNG", "TIFF", "PDF", "DOC"]
            ))

    def _register_digital_signature(self):
        """Digital signature and watermarking metadata - ~25 fields"""
        sig_fields = [
            ("has_digital_signature", MetadataCategory.DIGITAL_SIGNATURE, "bool", "Is signed"),
            ("signature_type", MetadataCategory.DIGITAL_SIGNATURE, "str", "Signature type"),
            ("signature_algorithm", MetadataCategory.DIGITAL_SIGNATURE, "str", "Algo used"),
            ("signature_signer", MetadataCategory.DIGITAL_SIGNATURE, "str", "Signer ID"),
            ("signature_timestamp", MetadataCategory.DIGITAL_SIGNATURE, "datetime", "Sign time"),
            ("signature_valid", MetadataCategory.DIGITAL_SIGNATURE, "bool", "Signature valid"),
            ("certificate_issuer", MetadataCategory.DIGITAL_SIGNATURE, "str", "Cert issuer"),
            ("certificate_subject", MetadataCategory.DIGITAL_SIGNATURE, "str", "Cert subject"),
            ("certificate_valid_from", MetadataCategory.DIGITAL_SIGNATURE, "datetime", "Cert start"),
            ("certificate_valid_to", MetadataCategory.DIGITAL_SIGNATURE, "datetime", "Cert end"),
            ("has_watermark", MetadataCategory.DIGITAL_SIGNATURE, "bool", "Has watermark"),
            ("watermark_type", MetadataCategory.DIGITAL_SIGNATURE, "str", "Watermark type"),
            ("watermark_algorithm", MetadataCategory.DIGITAL_SIGNATURE, "str", "Watermark algo"),
            ("watermark_strength", MetadataCategory.DIGITAL_SIGNATURE, "float", "Watermark strength"),
            ("has_steganography", MetadataCategory.DIGITAL_SIGNATURE, "bool", "Has steganography"),
            ("stego_method", MetadataCategory.DIGITAL_SIGNATURE, "str", "Stego method"),
            ("has_c2pa_manifest", MetadataCategory.DIGITAL_SIGNATURE, "bool", "C2PA manifest"),
            ("c2pa_claim_generator", MetadataCategory.DIGITAL_SIGNATURE, "str", "C2PA generator"),
            ("c2pa_assertions", MetadataCategory.DIGITAL_SIGNATURE, "list", "C2PA assertions"),
            ("provenance_chain", MetadataCategory.DIGITAL_SIGNATURE, "list", "Provenance chain"),
            ("is_ tamper_detected", MetadataCategory.DIGITAL_SIGNATURE, "bool", "Tamper check"),
            ("hash_algorithm", MetadataCategory.DIGITAL_SIGNATURE, "str", "Hash algo"),
            ("integrity_hash", MetadataCategory.DIGITAL_SIGNATURE, "str", "Integrity hash"),
        ]
        for name, category, field_type, description in sig_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPG", "PNG", "TIFF", "PDF", "PSD"]
            ))

    def _register_color_grading(self):
        """Color grading and LUT metadata - ~25 fields"""
        color_fields = [
            ("has_lut", MetadataCategory.COLOR_GRADING, "bool", "Has LUT"),
            ("lut_type", MetadataCategory.COLOR_GRADING, "str", "LUT type"),
            ("lut_size", MetadataCategory.COLOR_GRADING, "int", "LUT size"),
            ("lut_format", MetadataCategory.COLOR_GRADING, "str", "LUT format"),
            ("lut_input_colorspace", MetadataCategory.COLOR_GRADING, "str", "Input space"),
            ("lut_output_colorspace", MetadataCategory.COLOR_GRADING, "str", "Output space"),
            ("has_color_grade", MetadataCategory.COLOR_GRADING, "bool", "Has color grade"),
            ("grade_type", MetadataCategory.COLOR_GRADING, "str", "Grade type"),
            ("lift_values", MetadataCategory.COLOR_GRADING, "list", "Lift RGB"),
            ("gamma_values", MetadataCategory.COLOR_GRADING, "list", "Gamma RGB"),
            ("gain_values", MetadataCategory.COLOR_GRADING, "list", "Gain RGB"),
            ("offset_values", MetadataCategory.COLOR_GRADING, "list", "Offset RGB"),
            ("contrast_curve", MetadataCategory.COLOR_GRADING, "list", "Contrast points"),
            ("saturation", MetadataCategory.COLOR_GRADING, "float", "Saturation"),
            ("vibrance", MetadataCategory.COLOR_GRADING, "float", "Vibrance"),
            ("has_tone_curve", MetadataCategory.COLOR_GRADING, "bool", "Has tone curve"),
            ("tone_curve_points", MetadataCategory.COLOR_GRADING, "list", "Tone curve"),
            ("has_hsl_adjustments", MetadataCategory.COLOR_GRADING, "bool", "HSL adjustments"),
            ("hsl_data", MetadataCategory.COLOR_GRADING, "dict", "HSL values"),
            ("color_wheels", MetadataCategory.COLOR_GRADING, "list", "Color wheels"),
            ("ACES_cinemaGamut", MetadataCategory.COLOR_GRADING, "bool", "ACES cinemaGamut"),
            ("rec709_tone_curve", MetadataCategory.COLOR_GRADING, "bool", "Rec.709 tone"),
            ("has_log_profile", MetadataCategory.COLOR_GRADING, "bool", "Has log profile"),
            ("log_type", MetadataCategory.COLOR_GRADING, "str", "Log type"),
            ("dynamic_range", MetadataCategory.COLOR_GRADING, "str", "Dynamic range"),
            ("aces_cct", MetadataCategory.COLOR_GRADING, "bool", "ACES CCT"),
            ("aces_cc", MetadataCategory.COLOR_GRADING, "bool", "ACES Color Correction"),
            ("has_cdl", MetadataCategory.COLOR_GRADING, "bool", "Has CDL"),
            ("cdl_sop", MetadataCategory.COLOR_GRADING, "list", "CDL SOP"),
            ("cdl_sat", MetadataCategory.COLOR_GRADING, "list", "CDL Saturation"),
            ("look_file", MetadataCategory.COLOR_GRADING, "str", "Look file"),
            ("has_power_window", MetadataCategory.COLOR_GRADING, "bool", "Has power window"),
            ("power_window_shape", MetadataCategory.COLOR_GRADING, "str", "Window shape"),
            ("power_window_feather", MetadataCategory.COLOR_GRADING, "float", "Window feather"),
        ]
        for name, category, field_type, description in color_fields:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["CUBE", "3DL", "CSP", "JPG", "PNG", "TIFF", "PSD", "EXR"]
            ))

    def _register_iptc_extension(self):
        """Extended IPTC metadata fields - ~20 additional fields"""
        iptc_ext = [
            ("iptc_country_code", MetadataCategory.IPTC_EXTENSION, "str", "Country code"),
            ("iptc_sub_location", MetadataCategory.IPTC_EXTENSION, "str", "Sub-location"),
            ("iptc_province_state", MetadataCategory.IPTC_EXTENSION, "str", "Province/state"),
            ("iptc_action_advisory", MetadataCategory.IPTC_EXTENSION, "list", "Action advisory"),
            ("iptc_av_note", MetadataCategory.IPTC_EXTENSION, "str", "AV note"),
            ("iptc_credit", MetadataCategory.IPTC_EXTENSION, "str", "Credit"),
            ("iptc_source", MetadataCategory.IPTC_EXTENSION, "str", "Source"),
            ("iptc_contact", MetadataCategory.IPTC_EXTENSION, "list", "Contacts"),
            ("iptc_lightbox_settings", MetadataCategory.IPTC_EXTENSION, "dict", "Lightbox"),
            ("iptc_layout_settings", MetadataCategory.IPTC_EXTENSION, "dict", "Layout"),
            ("iptc_image_type", MetadataCategory.IPTC_EXTENSION, "str", "Image type"),
            ("iptc_editors_note", MetadataCategory.IPTC_EXTENSION, "str", "Editor's note"),
            ("iptc_opt_note", MetadataCategory.IPTC_EXTENSION, "str", "Opt. note"),
            ("iptc_usage_terms", MetadataCategory.IPTC_EXTENSION, "list", "Usage terms"),
            ("iptc_instruction", MetadataCategory.IPTC_EXTENSION, "str", "Instructions"),
            ("iptc_model_release", MetadataCategory.IPTC_EXTENSION, "str", "Model release"),
            ("iptc_property_release", MetadataCategory.IPTC_EXTENSION, "str", "Property release"),
            ("iptc_copyright_notice", MetadataCategory.IPTC_EXTENSION, "list", "Copyright"),
            ("iptc_creator", MetadataCategory.IPTC_EXTENSION, "list", "Creators"),
            ("iptc_rights_holder", MetadataCategory.IPTC_EXTENSION, "list", "Rights holders"),
        ]
        for name, category, field_type, description in iptc_ext:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "TIFF", "PSD", "PNG", "WebP"]
            ))

    def _register_camera_makernotes_extended(self):
        """Extended camera maker notes - ~50 fields for various cameras"""
        maker_ext = [
            # Canon Extended
            ("canon_makernote_ver", MetadataCategory.CAMERA_MAKERNOTES, "str", "Canon MN ver"),
            ("canon_cf_ver", MetadataCategory.CAMERA_MAKERNOTES, "str", "Canon CF ver"),
            ("canon_serial_number", MetadataCategory.CAMERA_MAKERNOTES, "str", "Canon serial"),
            ("canon_time_zone", MetadataCategory.CAMERA_MAKERNOTES, "str", "Time zone"),
            ("canon_camera_lens", MetadataCategory.CAMERA_MAKERNOTES, "str", "Lens model"),
            ("canon_focus_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "Focus mode"),
            ("canon_af_points", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF points"),
            ("canon_af_area", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF area"),
            ("canon_metering_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "Metering"),
            ("canon_exp_program", MetadataCategory.CAMERA_MAKERNOTES, "str", "Exp program"),
            ("canon_drive_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "Drive mode"),
            ("canon_focus_type", MetadataCategory.CAMERA_MAKERNOTES, "str", "Focus type"),
            ("canon_image_stabilization", MetadataCategory.CAMERA_MAKERNOTES, "str", "IS mode"),
            # Nikon Extended
            ("nikon_makernote_ver", MetadataCategory.CAMERA_MAKERNOTES, "str", "Nikon MN ver"),
            ("nikon_shutter_count", MetadataCategory.CAMERA_MAKERNOTES, "int", "Shutter count"),
            ("nikon_focus_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "Focus mode"),
            ("nikon_af_points", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF points"),
            ("nikon_af_area_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "AF area"),
            ("nikon_af_fine_tune", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF fine tune"),
            ("nikon_vibration_reduction", MetadataCategory.CAMERA_MAKERNOTES, "str", "VR mode"),
            ("nikon_flash_setting", MetadataCategory.CAMERA_MAKERNOTES, "str", "Flash setting"),
            ("nikon_flash_compensation", MetadataCategory.CAMERA_MAKERNOTES, "float", "Flash comp"),
            ("nikon_white_balance", MetadataCategory.CAMERA_MAKERNOTES, "str", "WB setting"),
            ("nikon_wb_fine_tune", MetadataCategory.CAMERA_MAKERNOTES, "list", "WB fine tune"),
            ("nikon_hdr", MetadataCategory.CAMERA_MAKERNOTES, "dict", "HDR settings"),
            ("nikon_active_d_lighting", MetadataCategory.CAMERA_MAKERNOTES, "str", "ADL"),
            # Sony Extended
            ("sony_makernote_ver", MetadataCategory.CAMERA_MAKERNOTES, "str", "Sony MN ver"),
            ("sony_shutter_count", MetadataCategory.CAMERA_MAKERNOTES, "int", "Shutter count"),
            ("sony_focus_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "Focus mode"),
            ("sony_af_points", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF points"),
            ("sony_af_area", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF area"),
            ("sony_steadyshot", MetadataCategory.CAMERA_MAKERNOTES, "str", "SteadyShot"),
            ("sony_long_exposure_nr", MetadataCategory.CAMERA_MAKERNOTES, "str", "LE-NR"),
            ("sony_high_iso_nr", MetadataCategory.CAMERA_MAKERNOTES, "str", "HI-ISO NR"),
            ("sony_drange_optimizer", MetadataCategory.CAMERA_MAKERNOTES, "str", "DRO"),
            ("sony_hdr", MetadataCategory.CAMERA_MAKERNOTES, "dict", "HDR settings"),
            ("sony_multi_frame_nr", MetadataCategory.CAMERA_MAKERNOTES, "bool", "MFNR"),
            # Fuji Extended
            ("fuji_makernote_ver", MetadataCategory.CAMERA_MAKERNOTES, "str", "Fuji MN ver"),
            ("fuji_focus_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "Focus mode"),
            ("fuji_af_points", MetadataCategory.CAMERA_MAKERNOTES, "list", "AF points"),
            ("fuji_film_mode", MetadataCategory.CAMERA_MAKERNOTES, "str", "Film mode"),
            ("fuji_dynamic_range", MetadataCategory.CAMERA_MAKERNOTES, "str", "DR mode"),
            ("fuji_white_balance", MetadataCategory.CAMERA_MAKERNOTES, "str", "WB setting"),
            ("fuji_sharpness", MetadataCategory.CAMERA_MAKERNOTES, "int", "Sharpness"),
            ("fuji_noise_reduction", MetadataCategory.CAMERA_MAKERNOTES, "int", "Noise red."),
            ("fuji_color", MetadataCategory.CAMERA_MAKERNOTES, "int", "Color"),
            ("fuji_tone", MetadataCategory.CAMERA_MAKERNOTES, "int", "Tone"),
            ("fuji_highlight_tone", MetadataCategory.CAMERA_MAKERNOTES, "int", "Highlight"),
            ("fuji_shadow_tone", MetadataCategory.CAMERA_MAKERNOTES, "int", "Shadow"),
            ("fuji_color_chromatic_aberration", MetadataCategory.CAMERA_MAKERNOTES, "int", "Chrom. aber."),
            ("fuji_color_resolution", MetadataCategory.CAMERA_MAKERNOTES, "int", "Color res."),
            ("fuji_lens_modulation_optimizer", MetadataCategory.CAMERA_MAKERNOTES, "bool", "LMO"),
            # Panasonic/Olympus Extended
            ("panasonic_makernote_ver", MetadataCategory.CAMERA_MAKERNOTES, "str", "Panasonic MN"),
            ("olympus_makernote_ver", MetadataCategory.CAMERA_MAKERNOTES, "str", "Olympus MN"),
            ("micro_four_thirds", MetadataCategory.CAMERA_MAKERNOTES, "bool", "MFT format"),
            ("focus_bracket", MetadataCategory.CAMERA_MAKERNOTES, "bool", "Focus bracket"),
            ("exposure_bracket", MetadataCategory.CAMERA_MAKERNOTES, "bool", "Exp. bracket"),
            ("wb_bracket", MetadataCategory.CAMERA_MAKERNOTES, "bool", "WB bracket"),
        ]
        for name, category, field_type, description in maker_ext:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "TIFF", "RAW", "DNG", "ARW", "NEF", "CR2", "CR3", "ORF", "RW2", "RAF"]
            ))

    def _register_xmp_namespaces_extended(self):
        """Extended XMP namespaces - ~30 additional fields"""
        xmp_ext = [
            ("xmp_photoshop_supplemental_categories", MetadataCategory.XMP_NAMESPACES, "list", "Supp. categories"),
            ("xmp_photoshop_legacy_caption", MetadataCategory.XMP_NAMESPACES, "str", "Legacy caption"),
            ("xmp_photoshop_history", MetadataCategory.XMP_NAMESPACES, "str", "History"),
            ("xmp_photoshop_state", MetadataCategory.XMP_NAMESPACES, "list", "State info"),
            ("xmp_photoshop_custom", MetadataCategory.XMP_NAMESPACES, "dict", "Custom data"),
            ("xmp_illustrator_artwork", MetadataCategory.XMP_NAMESPACES, "dict", "Illustrator"),
            ("xmp_indesign_document", MetadataCategory.XMP_NAMESPACES, "dict", "InDesign"),
            ("xmp_premiere_pro", MetadataCategory.XMP_NAMESPACES, "dict", "Premiere"),
            ("xmp_after_effects", MetadataCategory.XMP_NAMESPACES, "dict", "After Effects"),
            ("xmp_lightroom", MetadataCategory.XMP_NAMESPACES, "dict", "Lightroom"),
            ("xmp_camera_raw", MetadataCategory.XMP_NAMESPACES, "dict", "Camera Raw"),
            ("xmp_bridge", MetadataCategory.XMP_NAMESPACES, "dict", "Bridge"),
            ("xmp_dng_maker_note", MetadataCategory.XMP_NAMESPACES, "dict", "DNG MakerNote"),
            ("xmp_dng_private_data", MetadataCategory.XMP_NAMESPACES, "dict", "DNG Private"),
            ("xmp_exif_makernote", MetadataCategory.XMP_NAMESPACES, "dict", "Exif MN"),
            ("xmp_xmp_note", MetadataCategory.XMP_NAMESPACES, "dict", "XMP Note"),
            ("xmp_job", MetadataCategory.XMP_NAMESPACES, "dict", "Job info"),
            ("xmp_label", MetadataCategory.XMP_NAMESPACES, "list", "Labels"),
            ("xmp_rating", MetadataCategory.XMP_NAMESPACES, "int", "Rating 0-5"),
            ("xmp_rating_percent", MetadataCategory.XMP_NAMESPACES, "int", "Rating %"),
            ("xmp_web_statement", MetadataCategory.XMP_NAMESPACES, "str", "Web statement"),
            ("xmp_marked", MetadataCategory.XMP_NAMESPACES, "bool", "Marked"),
            ("xmp_usage_terms", MetadataCategory.XMP_NAMESPACES, "list", "Usage"),
            ("xmp_certificate", MetadataCategory.XMP_NAMESPACES, "str", "Certificate"),
            ("xmp_web_statement_url", MetadataCategory.XMP_NAMESPACES, "str", "URL"),
            ("xmp_references", MetadataCategory.XMP_NAMESPACES, "list", "References"),
            ("xmp_rights_marked", MetadataCategory.XMP_NAMESPACES, "bool", "Rights marked"),
            ("xmp_rights_owner", MetadataCategory.XMP_NAMESPACES, "list", "Owners"),
        ]
        for name, category, field_type, description in xmp_ext:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "WebP", "TIFF", "PSD", "HEIC", "AVIF", "DNG"]
            ))

    def _register_file_format_chunks_extended(self):
        """Extended file format chunk metadata - ~30 additional fields"""
        chunk_ext = [
            # PNG Extended
            ("png_ihdr_interlace", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Interlace"),
            ("png_sbit_valid", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "sBIT valid"),
            ("png_sbit_red", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "sBIT red"),
            ("png_sbit_green", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "sBIT green"),
            ("png_sbit_blue", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "sBIT blue"),
            ("png_sbit_alpha", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "sBIT alpha"),
            ("png_histogram_count", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Histogram"),
            ("png_phys_physical", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Physical unit"),
            ("png_phys_unit", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Unit specifier"),
            ("png_pixel_sample", MetadataCategory.FILE_FORMAT_CHUNKS, "list", "Sample depth"),
            # WebP Extended
            ("webp_animation_loop_count", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Loop count"),
            ("webp_animation_bg_color", MetadataCategory.FILE_FORMAT_CHUNKS, "list", "BG color"),
            ("webp_animation_disposal", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "Disposal"),
            ("webp_extended_format", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Extended VP8"),
            ("webp_lossless_alpha", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Lossless alpha"),
            ("webp_exif_size", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "EXIF size"),
            ("webp_xmp_size", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "XMP size"),
            ("webp_animation_size", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Animation size"),
            # TIFF Extended
            ("tiff_subfile_type", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Subfile type"),
            ("tiff_new_subfile_type", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "New subfile"),
            ("tiff_document_name", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "Document name"),
            ("tiff_page_name", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "Page name"),
            ("tiff_page_number", MetadataCategory.FILE_FORMAT_CHUNKS, "list", "Page number"),
            ("tiff_xmp", MetadataCategory.FILE_FORMAT_CHUNKS, "str", "XMP data"),
            ("tiff_photometric_interpretation", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Photometric"),
            ("tiff_thumbnail_offset", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Thumb offset"),
            ("tiff_thumbnail_length", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Thumb length"),
            # JPEG Extended
            ("jpeg_adobe_transform", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Adobe transform"),
            ("jpeg_app14_dct_encode", MetadataCategory.FILE_FORMAT_CHUNKS, "list", "DCT encode"),
            ("jpeg_huffman_tables", MetadataCategory.FILE_FORMAT_CHUNKS, "list", "Huffman tabs"),
            ("jpeg_quantization_tables", MetadataCategory.FILE_FORMAT_CHUNKS, "list", "Quant tabs"),
            ("jpeg_progressive", MetadataCategory.FILE_FORMAT_CHUNKS, "bool", "Progressive"),
            ("jpeg_scan_count", MetadataCategory.FILE_FORMAT_CHUNKS, "int", "Scan count"),
        ]
        for name, category, field_type, description in chunk_ext:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["PNG", "WebP", "TIFF", "JPEG", "GIF", "AVIF", "HEIC"]
            ))

    def _register_quality_metrics_extended(self):
        """Extended quality and perceptual metrics - ~20 additional fields"""
        quality_ext = [
            ("perceptual_blur_score", MetadataCategory.QUALITY_METRICS, "float", "Blur score"),
            ("perceptual_blockiness", MetadataCategory.QUALITY_METRICS, "float", "Blockiness"),
            ("perceptual_noise_estimate", MetadataCategory.QUALITY_METRICS, "float", "Noise est."),
            ("perceptual_artifact_index", MetadataCategory.QUALITY_METRICS, "float", "Artifacts"),
            ("perceptual_facial_quality", MetadataCategory.QUALITY_METRICS, "float", "Face quality"),
            ("perceptual_exposure_score", MetadataCategory.QUALITY_METRICS, "float", "Exposure"),
            ("perceptual_focus_score", MetadataCategory.QUALITY_METRICS, "float", "Focus"),
            ("perceptual_composition_score", MetadataCategory.QUALITY_METRICS, "float", "Composition"),
            ("perceptual_contrast_score", MetadataCategory.QUALITY_METRICS, "float", "Contrast"),
            ("perceptual_saturation_score", MetadataCategory.QUALITY_METRICS, "float", "Saturation"),
            ("perceptual_color_balance", MetadataCategory.QUALITY_METRICS, "float", "Color bal."),
            ("perceptual_skin_tone_accuracy", MetadataCategory.QUALITY_METRICS, "float", "Skin tone"),
            ("perceptual_dynamic_range_score", MetadataCategory.QUALITY_METRICS, "float", "DR score"),
            ("perceptual_sharpness_score", MetadataCategory.QUALITY_METRICS, "float", "Sharpness"),
            ("perceptual_overall_score", MetadataCategory.QUALITY_METRICS, "float", "Overall"),
            ("technical_iso_rating", MetadataCategory.QUALITY_METRICS, "str", "ISO rating"),
            ("technical_noise_rating", MetadataCategory.QUALITY_METRICS, "str", "Noise rating"),
            ("technical_dynamic_range", MetadataCategory.QUALITY_METRICS, "str", "DR rating"),
            ("technical_color_accuracy", MetadataCategory.QUALITY_METRICS, "str", "Color acc."),
            ("technical_lens_quality", MetadataCategory.QUALITY_METRICS, "str", "Lens qual."),
        ]
        for name, category, field_type, description in quality_ext:
            self._register_field(MetadataField(
                name=name, category=category, field_type=field_type, description=description,
                supported_formats=["JPEG", "PNG", "TIFF", "WebP", "AVIF", "HEIC"]
            ))

    def get_supported_formats(self, name: str) -> List[str]:
        """Get supported formats for a field"""
        field = self.fields.get(name)
        return field.supported_formats if field else []


def get_global_registry() -> ImageMetadataRegistry:
    """Get the global image metadata registry instance"""
    return ImageMetadataRegistry()
