#!/usr/bin/env python3
"""
Extended XMP Namespaces Module
Comprehensive XMP namespace parsing including:
- Dublin Core extensions
- Photoshop extended namespaces
- Camera Raw namespaces
- Rights management
- Digital Asset Management (DAM)
- Geographic/Location extensions
- Social media extensions
- Accessibility metadata
- Mixed Reality (MR) metadata

Author: MetaExtract Team
Version: 1.0.0
"""

import re
import logging
from typing import Dict, Any, Optional, List
from typing import Optional as TypingOptional
from pathlib import Path

logger = logging.getLogger(__name__)


class ExtendedXMPExtractor:
    """
    Extended XMP metadata extractor for comprehensive XMP parsing.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.xmp_data: Optional[str] = None
        self.namespaces: Dict[str, str] = {}

    def extract(self) -> Dict[str, Any]:
        """Main entry point - extract extended XMP metadata"""
        try:
            self._load_xmp()

            result: Dict[str, Any] = {
                "xmp_present": False,
                "namespaces": {},
                "dublin_core_extended": {},
                "photoshop_extended": {},
                "camera_raw": {},
                "rights_management": {},
                "dam_metadata": {},
                "geographic_extended": {},
                "social_media": {},
                "accessibility": {},
                "mixed_reality": {},
                "custom_namespaces": {},
            }

            if not self.xmp_data:
                return result

            result["xmp_present"] = True

            self.namespaces = self._extract_namespaces()
            result["namespaces"] = self.namespaces

            result["dublin_core_extended"] = self._parse_dublin_core_extended()
            result["photoshop_extended"] = self._parse_photoshop_extended()
            result["camera_raw"] = self._parse_camera_raw()
            result["rights_management"] = self._parse_rights_management()
            result["dam_metadata"] = self._parse_dam_metadata()
            result["geographic_extended"] = self._parse_geographic_extended()
            result["social_media"] = self._parse_social_media()
            result["accessibility"] = self._parse_accessibility()
            result["mixed_reality"] = self._parse_mixed_reality()
            result["custom_namespaces"] = self._parse_custom_namespaces()

            return result

        except Exception as e:
            logger.error(f"Error extracting XMP: {e}")
            return {"error": str(e), "xmp_present": False}

    def _load_xmp(self):
        """Load XMP data from file"""
        file_path = Path(self.filepath)
        if not file_path.exists():
            return

        try:
            if str(self.filepath).endswith('.png'):
                self._extract_xmp_from_png()
            elif str(self.filepath).endswith(('.jpg', '.jpeg', '.webp', '.psd', '.tiff', '.tif')):
                self._extract_xmp_embedded()
            else:
                self._extract_xmp_embedded()
        except Exception:
            self.xmp_data = None

    def _extract_xmp_from_png(self):
        """Extract XMP from PNG file"""
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()

            if len(data) < 16 or data[:8] != b'\x89PNG\r\n\x1a\n':
                return

            offset = 8
            while offset < len(data) - 12:
                length = struct.unpack('>I', data[offset:offset + 4])[0]
                chunk_type = data[offset + 4:offset + 8].decode('latin-1', errors='replace')

                if chunk_type == 'tEXt':
                    chunk_data = data[offset + 8:offset + 8 + length]
                    null_pos = chunk_data.find(b'\x00')
                    if null_pos > 0:
                        keyword = chunk_data[:null_pos].decode('latin-1', errors='replace')
                        if keyword == 'XML:com.adobe.xmp':
                            self.xmp_data = chunk_data[null_pos + 1:].decode('utf-8', errors='replace')

                offset += 12 + length
        except Exception:
            self.xmp_data = None

    def _extract_xmp_embedded(self):
        """Extract embedded XMP from various file formats"""
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read(8192)

            xmp_start = data.find(b'<?xpacket begin=')
            if xmp_start > 0:
                xmp_end = data.find(b'</x:xmpmeta>', xmp_start)
                if xmp_end > 0:
                    self.xmp_data = data[xmp_start:xmp_end + 12].decode('utf-8', errors='replace')
        except Exception:
            self.xmp_data = None

    def _extract_namespaces(self) -> Dict[str, str]:
        """Extract XMP namespace definitions"""
        namespaces: Dict[str, str] = {}

        ns_patterns = [
            (r'xmlns:(\w+)="([^"]+)"', 2),
            (r'xmlns:(\w+)=\'([^\']+)\'', 2),
        ]

        for pattern, _ in ns_patterns:
            matches = re.findall(pattern, self.xmp_data)
            for prefix, uri in matches:
                namespaces[prefix] = uri

        return namespaces

    def _parse_dublin_core_extended(self) -> Dict[str, Any]:
        """Parse extended Dublin Core metadata"""
        dc: Dict[str, Any] = {}

        patterns = [
            (r'dc:title["\s]*:?\s*<rdf:Alt[^>]*>([\s\S]*?)</rdf:Alt>', 'title'),
            (r'dc:description["\s]*:?\s*<rdf:Alt[^>]*>([\s\S]*?)</rdf:Alt>', 'description'),
            (r'dc:subject["\s]*:?\s*<rdf:Bag[^>]*>([\s\S]*?)</rdf:Bag>', 'subject'),
            (r'dc:creator["\s]*:?\s*<rdf:Seq[^>]*>([\s\S]*?)</rdf:Seq>', 'creator'),
            (r'dc:contributor["\s]*:?\s*<rdf:Bag[^>]*>([\s\S]*?)</rdf:Bag>', 'contributor'),
            (r'dc:publisher["\s]*:?\s*<rdf:Seq[^>]*>([\s\S]*?)</rdf:Seq>', 'publisher'),
            (r'dc:coverage["\s]*:?\s*["\']?([^"\']+)', 'coverage'),
            (r'dc:format["\s]*:?\s*["\']?([^"\']+)', 'format'),
            (r'dc:identifier["\s]*:?\s*["\']?([^"\']+)', 'identifier'),
            (r'dc:source["\s]*:?\s*["\']?([^"\']+)', 'source'),
            (r'dc:relation["\s]*:?\s*<rdf:Bag[^>]*>([\s\S]*?)</rdf:Bag>', 'relation'),
            (r'dc:language["\s]*:?\s*["\']?([^"\']+)', 'language'),
            (r'dc:rights["\s]*:?\s*<rdf:Alt[^>]*>([\s\S]*?)</rdf:Alt>', 'rights'),
            (r'dc:audience["\s]*:?\s*<rdf:Bag[^>]*>([\s\S]*?)</rdf:Bag>', 'audience'),
            (r'dc:provenance["\s]*:?\s*["\']?([^"\']+)', 'provenance'),
            (r'dc:rightsHolder["\s]*:?\s*["\']?([^"\']+)', 'rights_holder'),
            (r'dc:instructions["\s]*:?\s*["\']?([^"\']+)', 'instructions'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if 'rdf:' in value.lower():
                    li_matches = re.findall(r'<rdf:li[^>]*>([^<]+)</rdf:li>', value)
                    if li_matches:
                        dc[field] = [li.strip() for li in li_matches]
                    else:
                        clean_value = re.sub(r'<[^>]+>', '', value)
                        dc[field] = clean_value.strip()
                else:
                    dc[field] = value

        if not dc:
            return {}

        return dc

    def _parse_photoshop_extended(self) -> Dict[str, Any]:
        """Parse extended Photoshop metadata"""
        ps: Dict[str, Any] = {}

        patterns = [
            (r'photoshop:ColorMode["\s]*:?\s*(\d+)', 'color_mode'),
            (r'photoshop:ICCProfile["\s]*:?\s*["\']?([^"\']+)', 'icc_profile'),
            (r'photoshop:History["\s]*:?\s*["\']?([^"\']+)', 'history'),
            (r'photoshop:DocumentAncestors["\s]*:?\s*<rdf:Bag[^>]*>([\s\S]*?)</rdf:Bag>', 'document_ancestors'),
            (r'photoshop:DocumentHistory["\s]*:?\s*<rdf:Bag[^>]*>([\s\S]*?)</rdf:Bag>', 'document_history'),
            (r'photoshop:CaptionWriter["\s]*:?\s*["\']?([^"\']+)', 'caption_writer'),
            (r'photoshop:Instructions["\s]*:?\s*["\']?([^"\']+)', 'instructions'),
            (r'photoshop:AuthorsPosition["\s]*:?\s*["\']?([^"\']+)', 'authors_position'),
            (r'photoshop:Title["\s]*:?\s*["\']?([^"\']+)', 'title'),
            (r'photoshop:WebStatement["\s]*:?\s*["\']?([^"\']+)', 'web_statement'),
            (r'photoshop:Category["\s]*:?\s*["\']?([^"\']+)', 'category'),
            (r'photoshop:SupplementalCategories["\s]*:?\s*<rdf:Bag[^>]*>([\s\S]*?)</rdf:Bag>', 'supplemental_categories'),
            (r'photoshop:Urgency["\s]*:?\s*(\d+)', 'urgency'),
            (r'photoshop:DateCreated["\s]*:?\s*["\']?([^"\']+)', 'date_created'),
            (r'photoshop:City["\s]*:?\s*["\']?([^"\']+)', 'city'),
            (r'photoshop:State["\s]*:?\s*["\']?([^"\']+)', 'state'),
            (r'photoshop:Country["\s]*:?\s*["\']?([^"\']+)', 'country'),
            (r'photoshop:Headline["\s]*:?\s*["\']?([^"\']+)', 'headline'),
            (r'photoshop:Credit["\s]*:?\s*["\']?([^"\']+)', 'credit'),
            (r'photoshop:Source["\s]*:?\s*["\']?([^"\']+)', 'source'),
            (r'photoshop:CopyrightStatus["\s]*:?\s*["\']?([^"\']+)', 'copyright_status'),
            (r'photoshop:CopyrightNotice["\s]*:?\s*["\']?([^"\']+)', 'copyright_notice'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if 'rdf:' in value.lower():
                    li_matches = re.findall(r'<rdf:li[^>]*>([^<]+)</rdf:li>', value)
                    if li_matches:
                        ps[field] = [li.strip() for li in li_matches]
                    else:
                        clean_value = re.sub(r'<[^>]+>', '', value)
                        ps[field] = clean_value.strip()
                elif field in ['urgency', 'color_mode']:
                    ps[field] = int(value)
                else:
                    ps[field] = value

        return ps

    def _parse_camera_raw(self) -> Dict[str, Any]:
        """Parse Camera Raw / Lightroom metadata"""
        cr: Dict[str, Any] = {}

        patterns = [
            (r'crs:Version["\s]*:?\s*["\']?([^"\']+)', 'version'),
            (r'crs:ProcessVersion["\s]*:?\s*["\']?([^"\']+)', 'process_version'),
            (r'crs:WhiteBalance["\s]*:?\s*["\']?([^"\']+)', 'white_balance'),
            (r'crs:Temperature["\s]*:?\s*(\d+)', 'temperature'),
            (r'crs:Tint["\s]*:?\s*([-\d.]+)', 'tint'),
            (r'crs:Exposure["\s]*:?\s*([-\d.]+)', 'exposure'),
            (r'crs:Contrast["\s]*:?\s*(\d+)', 'contrast'),
            (r'crs:Highlights["\s]*:?\s*(\d+)', 'highlights'),
            (r'crs:Shadows["\s]*:?\s*(\d+)', 'shadows'),
            (r'crs:Whites["\s]*:?\s*(\d+)', 'whites'),
            (r'crs:Blacks["\s]*:?\s*(\d+)', 'blacks'),
            (r'crs:Texture["\s]*:?\s*(\d+)', 'texture'),
            (r'crs:Clarity["\s]*:?\s*(\d+)', 'clarity'),
            (r'crs:Dehaze["\s]*:?\s*(\d+)', 'dehaze'),
            (r'crs:VignetteAmount["\s]*:?\s*([-\d.]+)', 'vignette_amount'),
            (r'crs:VignetteMidpoint["\s]*:?\s*(\d+)', 'vignette_midpoint'),
            (r'crs:VignetteStyle["\s]*:?\s*["\']?([^"\']+)', 'vignette_style'),
            (r'crs:GrainAmount["\s]*:?\s*([-\d.]+)', 'grain_amount'),
            (r'crs:GrainSize["\s]*:?\s*["\']?([^"\']+)', 'grain_size'),
            (r'crs:GrainRoughness["\s]*:?\s*([-\d.]+)', 'grain_roughness'),
            (r'crs:ColorNoiseReduction["\s]*:?\s*(\d+)', 'color_noise_reduction'),
            (r'crs:SharpenRadius["\s]*:?\s*["\']?([^"\']+)', 'sharpen_radius'),
            (r'crs:SharpenDetail["\s]*:?\s*(\d+)', 'sharpen_detail'),
            (r'crs:SharpenEdgeMasking["\s]*:?\s*(\d+)', 'sharpen_edge_masking'),
            (r'crs:LensProfileEnable["\s]*:?\s*(\d+)', 'lens_profile_enable'),
            (r'crs:LensManualDistortionAmount["\s]*:?\s*([-\d.]+)', 'lens_manual_distortion'),
            (r'crs:PerspectiveVertical["\s]*:?\s*([-\d.]+)', 'perspective_vertical'),
            (r'crs:PerspectiveHorizontal["\s]*:?\s*([-\d.]+)', 'perspective_horizontal'),
            (r'crs:PerspectiveRotate["\s]*:?\s*([-\d.]+)', 'perspective_rotate'),
            (r'crs:PerspectiveScale["\s]*:?\s*([-\d.]+)', 'perspective_scale'),
            (r'crs:CropAngle["\s]*:?\s*([-\d.]+)', 'crop_angle'),
            (r'crs:CropConstrainToWarp["\s]*:?\s*(\d+)', 'crop_constrain_to_warp'),
            (r'crs:AutoLateralCA["\s]*:?\s*(\d+)', 'auto_lateral_ca'),
            (r'crs:Exposure2012["\s]*:?\s*([-\d.]+)', 'exposure_2012'),
            (r'crs:Contrast2012["\s]*:?\s*(\d+)', 'contrast_2012'),
            (r'crs:Highlights2012["\s]*:?\s*(\d+)', 'highlights_2012'),
            (r'crs:Shadows2012["\s]*:?\s*(\d+)', 'shadows_2012'),
            (r'crs:Whites2012["\s]*:?\s*(\d+)', 'whites_2012'),
            (r'crs:Blacks2012["\s]*:?\s*(\d+)', 'blacks_2012'),
            (r'crs:Texture2012["\s]*:?\s*(\d+)', 'texture_2012'),
            (r'crs:Clarity2012["\s]*:?\s*(\d+)', 'clarity_2012'),
            (r'crs:Dehaze2012["\s]*:?\s*(\d+)', 'dehaze_2012'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field in ['temperature', 'contrast', 'highlights', 'shadows', 'whites',
                            'blacks', 'clarity', 'texture', 'dehaze', 'vignette_midpoint',
                            'sharpen_detail', 'sharpen_edge_masking', 'lens_profile_enable',
                            'crop_constrain_to_warp', 'auto_lateral_ca', 'color_noise_reduction']:
                    cr[field] = int(value)
                elif field in ['exposure', 'tint', 'vignette_amount', 'grain_amount',
                              'grain_roughness', 'lens_manual_distortion', 'perspective_vertical',
                              'perspective_horizontal', 'perspective_rotate', 'perspective_scale',
                              'crop_angle', 'exposure_2012', 'contrast_2012', 'highlights_2012',
                              'shadows_2012', 'whites_2012', 'blacks_2012', 'texture_2012',
                              'clarity_2012', 'dehaze_2012']:
                    try:
                        cr[field] = float(value)
                    except ValueError:
                        cr[field] = value
                else:
                    cr[field] = value

        return cr

    def _parse_rights_management(self) -> Dict[str, Any]:
        """Parse rights management metadata"""
        rights: Dict[str, Any] = {}

        patterns = [
            (r'xmpRights:WebStatement["\s]*:?\s*["\']?([^"\']+)', 'web_statement'),
            (r'xmpRights:Marked["\s]*:?\s*(true|false)', 'marked'),
            (r'xmpRights:Owner["\s]*:?\s*<rdf:Alt[^>]*>([\s\S]*?)</rdf:Alt>', 'owner'),
            (r'xmpRights:UsageTerms["\s]*:?\s*<rdf:Alt[^>]*>([\s\S]*?)</rdf:Alt>', 'usage_terms'),
            (r'xmpRights:Certificate["\s]*:?\s*["\']?([^"\']+)', 'certificate'),
            (r'xmpRights:Jurisdiction["\s]*:?\s*["\']?([^"\']+)', 'jurisdiction'),
            (r'xmpRights:AssetURL["\s]*:?\s*["\']?([^"\']+)', 'asset_url'),
            (r'cc:license["\s]*:?\s*["\']?([^"\']+)', 'creative_commons_license'),
            (r'cc:morePermissions["\s]*:?\s*["\']?([^"\']+)', 'more_permissions'),
            (r'cc:attributionName["\s]*:?\s*["\']?([^"\']+)', 'attribution_name'),
            (r'cc:attributionURL["\s]*:?\s*["\']?([^"\']+)', 'attribution_url'),
            (r'cc:deprecated["\s]*:?\s*(true|false)', 'deprecated'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field in ['marked', 'deprecated']:
                    rights[field] = value.lower() == 'true'
                elif 'rdf:' in value.lower():
                    li_matches = re.findall(r'<rdf:li[^>]*>([^<]+)</rdf:li>', value)
                    if li_matches:
                        rights[field] = [li.strip() for li in li_matches]
                    else:
                        clean_value = re.sub(r'<[^>]+>', '', value)
                        rights[field] = clean_value.strip()
                else:
                    rights[field] = value

        return rights

    def _parse_dam_metadata(self) -> Dict[str, Any]:
        """Parse Digital Asset Management metadata"""
        dam: Dict[str, Any] = {}

        patterns = [
            (r'xmpDM:scene["\s]*:?\s*["\']?([^"\']+)', 'scene'),
            (r'xmpDM:shotNumber["\s]*:?\s*(\d+)', 'shot_number'),
            (r'xmpDM:shotName["\s]*:?\s*["\']?([^"\']+)', 'shot_name'),
            (r'xmpDM:takeNumber["\s]*:?\s*(\d+)', 'take_number'),
            (r'xmpDM:takeName["\s]*:?\s*["\']?([^"\']+)', 'take_name'),
            (r'xmpDM:artist["\s]*:?\s*["\']?([^"\']+)', 'artist'),
            (r'xmpDM:album["\s]*:?\s*["\']?([^"\']+)', 'album'),
            (r'xmpDM:genre["\s]*:?\s*["\']?([^"\']+)', 'genre'),
            (r'xmpDM:logComment["\s]*:?\s*["\']?([^"\']+)', 'log_comment'),
            (r'xmpDM:project["\s]*:?\s*["\']?([^"\']+)', 'project'),
            (r'xmpDM:tempo["\s]*:?\s*["\']?([^"\']+)', 'tempo'),
            (r'xmpDM:timeSignature["\s]*:?\s*["\']?([^"\']+)', 'time_signature'),
            (r'xmpDM:audioSampleRate["\s]*:?\s*(\d+)', 'audio_sample_rate'),
            (r'xmpDM:audioSampleType["\s]*:?\s*["\']?([^"\']+)', 'audio_sample_type'),
            (r'xmpDM:audioChannelType["\s]*:?\s*["\']?([^"\']+)', 'audio_channel_type'),
            (r'xmpDM:videoFrameRate["\s]*:?\s*["\']?([^"\']+)', 'video_frame_rate'),
            (r'xmpDM:videoFrameSize["\s]*:?\s*["\']?([^"\']+)', 'video_frame_size'),
            (r'xmpDM:videoPixelAspectRatio["\s]*:?\s*["\']?([^"\']+)', 'video_pixel_aspect_ratio'),
            (r'xmpDM:videoColorSpace["\s]*:?\s*["\']?([^"\']+)', 'video_color_space'),
            (r'xmpDM:videoAlphaMode["\s]*:?\s*["\']?([^"\']+)', 'video_alpha_mode'),
            (r'xmpDM:videoAlphaUnitySize["\s]*:?\s*([-\d.]+)', 'video_alpha_unity_size'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field in ['shot_number', 'take_number', 'audio_sample_rate']:
                    dam[field] = int(value)
                elif field == 'video_alpha_unity_size':
                    try:
                        dam[field] = float(value)
                    except ValueError:
                        dam[field] = value
                else:
                    dam[field] = value

        return dam

    def _parse_geographic_extended(self) -> Dict[str, Any]:
        """Parse extended geographic/metadata"""
        geo: Dict[str, Any] = {}

        patterns = [
            (r'exif:GPSAltitudeRef["\s]*:?\s*(\d+)', 'gps_altitude_ref'),
            (r'exif:GPSSpeedRef["\s]*:?\s*["\']?([^"\']+)', 'gps_speed_ref'),
            (r'exif:GPSSpeed["\s]*:?\s*([-\d.]+)', 'gps_speed'),
            (r'exif:GPSImgDirectionRef["\s]*:?\s*["\']?([^"\']+)', 'gps_img_direction_ref'),
            (r'exif:GPSImgDirection["\s]*:?\s*([-\d.]+)', 'gps_img_direction'),
            (r'exif:GPSDestLatitude["\s]*:?\s*["\']?([^"\']+)', 'gps_dest_latitude'),
            (r'exif:GPSDestLongitude["\s]*:?\s*["\']?([^"\']+)', 'gps_dest_longitude'),
            (r'exif:GPSDestBearingRef["\s]*:?\s*["\']?([^"\']+)', 'gps_dest_bearing_ref'),
            (r'exif:GPSDestBearing["\s]*:?\s*([-\d.]+)', 'gps_dest_bearing'),
            (r'exif:GPSDestDistanceRef["\s]*:?\s*["\']?([^"\']+)', 'gps_dest_distance_ref'),
            (r'exif:GPSDestDistance["\s]*:?\s*([-\d.]+)', 'gps_dest_distance'),
            (r'exif:GPSMapDatum["\s]*:?\s*["\']?([^"\']+)', 'gps_map_datum'),
            (r'exif:GPSDestLatitudeRef["\s]*:?\s*["\']?([^"\']+)', 'gps_dest_latitude_ref'),
            (r'exif:GPSDestLongitudeRef["\s]*:?\s*["\']?([^"\']+)', 'gps_dest_longitude_ref'),
            (r'xmp:Location["\s]*:?\s*["\']?([^"\']+)', 'location'),
            (r'xmp:City["\s]*:?\s*["\']?([^"\']+)', 'city'),
            (r'xmp:State["\s]*:?\s*["\']?([^"\']+)', 'state'),
            (r'xmp:Country["\s]*:?\s*["\']?([^"\']+)', 'country'),
            (r'xmp:CountryCode["\s]*:?\s*["\']?([^"\']+)', 'country_code'),
            (r'xmp:LocationShown["\s]*:?\s*<rdf:Description[^>]*>([\s\S]*?)</rdf:Description>', 'location_shown'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field in ['gps_altitude_ref', 'gps_speed', 'gps_img_direction', 'gps_dest_bearing', 'gps_dest_distance']:
                    try:
                        geo[field] = float(value)
                    except ValueError:
                        geo[field] = value
                else:
                    geo[field] = value

        return geo

    def _parse_social_media(self) -> Dict[str, Any]:
        """Parse social media metadata"""
        social: Dict[str, Any] = {}

        patterns = [
            (r'facebook:image["\s]*:?\s*["\']?([^"\']+)', 'facebook_image'),
            (r'instagram:filterName["\s]*:?\s*["\']?([^"\']+)', 'instagram_filter'),
            (r'instagram:filterStrength["\s]*:?\s*([-\d.]+)', 'instagram_filter_strength'),
            (r'twitter:image["\s]*:?\s*["\']?([^"\']+)', 'twitter_image'),
            (r'twitter:card["\s]*:?\s*["\']?([^"\']+)', 'twitter_card'),
            (r'twitter:site["\s]*:?\s*["\']?([^"\']+)', 'twitter_site'),
            (r'twitter:creator["\s]*:?\s*["\']?([^"\']+)', 'twitter_creator'),
            (r'og:image["\s]*:?\s*["\']?([^"\']+)', 'og_image'),
            (r'og:title["\s]*:?\s*["\']?([^"\']+)', 'og_title'),
            (r'og:description["\s]*:?\s*["\']?([^"\']+)', 'og_description'),
            (r'medium["\s]*:?\s*["\']?([^"\']+)', 'medium'),
            (r'title["\s]*:?\s*["\']?([^"\']+)', 'title'),
            (r'description["\s]*:?\s*["\']?([^"\']+)', 'description'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field == 'instagram_filter_strength':
                    try:
                        social[field] = float(value)
                    except ValueError:
                        social[field] = value
                else:
                    social[field] = value

        return social

    def _parse_accessibility(self) -> Dict[str, Any]:
        """Parse accessibility metadata"""
        accessibility: Dict[str, Any] = {}

        patterns = [
            (r'pdf:Keywords["\s]*:?\s*["\']?([^"\']+)', 'pdf_keywords'),
            (r'accessibility:transcript["\s]*:?\s*["\']?([^"\']+)', 'transcript'),
            (r'accessibility:audioDescription["\s]*:?\s*["\']?([^"\']+)', 'audio_description'),
            (r'accessibility:closedCaptions["\s]*:?\s*(true|false)', 'closed_captions'),
            (r'accessibility:visualDescription["\s]*:?\s*["\']?([^"\']+)', 'visual_description'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field == 'closed_captions':
                    accessibility[field] = value.lower() == 'true'
                else:
                    accessibility[field] = value

        return accessibility

    def _parse_mixed_reality(self) -> Dict[str, Any]:
        """Parse Mixed Reality / 360 metadata"""
        mr: Dict[str, Any] = {}

        patterns = [
            (r'gphoto: сфера["\s]*:?\s*(true|false)', 'is_360_sphere'),
            (r'gphoto:croppedAreaImageWidthPixels["\s]*:?\s*(\d+)', 'cropped_area_width'),
            (r'gphoto:croppedAreaImageHeightPixels["\s]*:?\s*(\d+)', 'cropped_area_height'),
            (r'gphoto:croppedAreaLeftPixels["\s]*:?\s*(\d+)', 'cropped_area_left'),
            (r'gphoto:croppedAreaTopPixels["\s]*:?\s*(\d+)', 'cropped_area_top'),
            (r'gphoto:fullPanoWidthPixels["\s]*:?\s*(\d+)', 'full_pano_width'),
            (r'gphoto:fullPanoHeightPixels["\s]*:?\s*(\d+)', 'full_pano_height'),
            (r'gphoto:projectionType["\s]*:?\s*["\']?([^"\']+)', 'projection_type'),
            (r'GPano:ProjectionType["\s]*:?\s*["\']?([^"\']+)', 'g pano_projection_type'),
            (r'GPano:Validated["\s]*:?\s*(\d+)', 'validated'),
            (r'GPano:CroppedAreaImageWidth["\s]*:?\s*(\d+)', 'cropped_area_image_width'),
            (r'GPano:CroppedAreaImageHeight["\s]*:?\s*(\d+)', 'cropped_area_image_height'),
            (r'GPano:FullPanoWidth["\s]*:?\s*(\d+)', 'full_pano_width'),
            (r'GPano:FullPanoHeight["\s]*:?\s*(\d+)', 'full_pano_height'),
            (r'GPano:InitialViewHeadingDegrees["\s]*:?\s*([-\d.]+)', 'initial_view_heading'),
            (r'GPano:InitialViewPitchDegrees["\s]*:?\s*([-\d.]+)', 'initial_view_pitch'),
            (r'GPano:InitialViewRollDegrees["\s]*:?\s*([-\d.]+)', 'initial_view_roll'),
            (r'GPano:InitialHorizontalFOVDegrees["\s]*:?\s*([-\d.]+)', 'initial_horizontal_fov'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field in ['is_360_sphere', 'validated']:
                    mr[field] = value.lower() == 'true'
                elif field in ['cropped_area_width', 'cropped_area_height', 'cropped_area_left', 'cropped_area_top',
                              'full_pano_width', 'full_pano_height', 'cropped_area_image_width', 'cropped_area_image_height']:
                    mr[field] = int(value)
                elif field in ['initial_view_heading', 'initial_view_pitch', 'initial_view_roll', 'initial_horizontal_fov']:
                    try:
                        mr[field] = float(value)
                    except ValueError:
                        mr[field] = value
                else:
                    mr[field] = value

        return mr

    def _parse_custom_namespaces(self) -> Dict[str, Any]:
        """Parse any custom/unknown namespaces"""
        custom: Dict[str, Any] = {}

        for prefix, uri in self.namespaces.items():
            if prefix not in ['xmp', 'xmpDM', 'xmpRights', 'dc', 'photoshop', 'crs', 'cc', 'exif', 'tiff', 'rdf',
                             'gphoto', 'GPano', 'facebook', 'instagram', 'twitter', 'og', 'pdf', 'accessibility']:
                pattern = prefix + r':([a-zA-Z0-9]+)="([^"]+)"'
                matches = re.findall(pattern, self.xmp_data)
                for match in matches:
                    field, value = match
                    custom_key = prefix + '_' + field
                    custom[custom_key] = value

        return custom


def extract_extended_xmp(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract extended XMP metadata"""
    extractor = ExtendedXMPExtractor(filepath)
    return extractor.extract()


def get_xmp_extended_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 150
