"""
Accessibility Metadata Extraction
Alt text, transcripts, subtitles, and accessibility features
"""

from typing import Dict, Any, Optional, List


ACCESSIBILITY_TAGS = {
    # IPTC Accessibility
    "Iptc.Application2.AltText": "alt_text",
    "Iptc.Application2.LongDescription": "long_description",
    "Iptc.Application2.Caption": "caption",
    
    # XMP Accessibility
    "Xmp.acdsee.accessibility.description": "acdsee_description",
    "Xmp.acdsee.accessibility.version": "acdsee_version",
    
    # Dublin Core Accessibility
    "Xmp.dc.description": "description",
    "Xmp.dc.title": "title",
    "Xmp.dc.subject": "subject",
    
    # Accessibility Features/Hazards (PLUS/IPTC)
    "Iptc.Application2.AccessibilityFeature": "accessibility_features",
    "Iptc.Application2.Accessibility Hazard": "accessibility_hazards",
    
    # Transcript (for audio/video)
    "Xmp.transcript": "transcript",
    "Xmp.dublincore.description": "audio_description",
    
    # Subtitle Languages
    "Xmp.media.subtitleLanguage": "subtitle_languages",
    "Xmp.iptcExt.Subtitle": "subtitle_content",
}

WEB_ACCESSIBILITY_TAGS = {
    # HTML Alt Text
    "HTML_Alt": "html_alt_text",
    "HTML_Title": "html_title",
    "HTML_Longdesc": "html_long_description",
    
    # ARIA Labels
    "ARIA_Label": "aria_label",
    "ARIA_Description": "aria_description",
    "ARIA_Role": "aria_role",
    
    # Schema.org Accessibility
    "Schema_AccessMode": "access_mode",
    "Schema_AccessModeSufficient": "access_mode_sufficient",
    "Schema_AccessibilityFeature": "accessibility_features",
    "Schema_AccessibilityHazard": "accessibility_hazards",
    "Schema_AccessibilityControl": "accessibility_controls",
    "Schema_AccessibilityAPI": "accessibility_api",
    "Schema_Requires": "requires",
    "Schema_Canonical": "canonical_url",
    "Schema_IsAccessibleForFree": "is_accessible_for_free",
    "Schema_Publisher": "publisher",
    "Schema_BeforeContent": "before_content",
    "Schema_AfterContent": "after_content",
}

AUDIO_VIDEO_ACCESSIBILITY = {
    # Audio Description
    "HasAudioDescription": "audio_description_available",
    "AudioDescription": "audio_description_content",
    
    # Sign Language
    "HasSignLanguage": "sign_language_available",
    "SignLanguageInterpretation": "sign_language_interpretation",
    
    # Closed Captions
    "ClosedCaptions": "closed_captions_available",
    "CaptionLanguage": "caption_language",
    "CC_Format": "caption_format",
    
    # Transcript
    "HasTranscript": "transcript_available",
    "Transcript": "transcript_content",
    "TranscriptLanguage": "transcript_language",
    
    # Subtitles
    "HasSubtitles": "subtitles_available",
    "SubtitleLanguage": "subtitle_language",
    "SubtitleFormat": "subtitle_format",
    
    # Audio Tracks
    "AudioTrackType": "audio_track_type",
    "CleanAudioTrack": "clean_audio_track",
    "ExtendedAudioTrack": "extended_audio_track",
}


def extract_accessibility_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract accessibility metadata from media files.
    
    Args:
        filepath: Path to image/video/audio file
    
    Returns:
        Dictionary with accessibility metadata
    """
    result = {
        "accessibility": {
            "text_alternatives": {},
            "visual_descriptions": {},
            "features": [],
            "hazards": []
        },
        "multimedia_accessibility": {},
        "web_accessibility": {},
        "compliance": {
            "wcag_level": None,
            "issues": []
        },
        "fields_extracted": 0
    }
    
    try:
        from .exif import extract_exif_metadata
        from .iptc_xmp import extract_iptc_xmp_metadata
        
        exif_data = extract_exif_metadata(filepath)
        iptc_data = extract_iptc_xmp_metadata(filepath)
        
        all_tags = {}
        
        if exif_data and "error" not in exif_data:
            for category in ["image", "photo", "gps", "interoperability"]:
                if category in exif_data and isinstance(exif_data[category], dict):
                    all_tags.update(exif_data[category])
        
        if iptc_data and "error" not in iptc_data:
            if isinstance(iptc_data, dict):
                for section in iptc_data.values():
                    if isinstance(section, dict):
                        all_tags.update(section)
        
        for tag, value in all_tags.items():
            tag_str = str(tag)
            
            if tag_str in ACCESSIBILITY_TAGS:
                key = ACCESSIBILITY_TAGS[tag_str]
                if "alt" in key.lower() or "description" in key.lower() or "caption" in key.lower():
                    result["accessibility"]["text_alternatives"][key] = str(value)
                elif "accessibility" in key.lower():
                    if "feature" in key.lower() or "hazard" in key.lower():
                        result["accessibility"]["features"].append(str(value))
                    else:
                        result["accessibility"]["visual_descriptions"][key] = str(value)
            
            elif tag_str in WEB_ACCESSIBILITY_TAGS:
                key = WEB_ACCESSIBILITY_TAGS[tag_str]
                result["web_accessibility"][key] = str(value)
            
            elif tag_str in AUDIO_VIDEO_ACCESSIBILITY:
                key = AUDIO_VIDEO_ACCESSIBILITY[tag_str]
                result["multimedia_accessibility"][key] = str(value)
        
        if not result["multimedia_accessibility"]:
            result["multimedia_accessibility"]["audio_description_available"] = False
            result["multimedia_accessibility"]["transcript_available"] = False
            result["multimedia_accessibility"]["closed_captions_available"] = False
            result["multimedia_accessibility"]["subtitles_available"] = False
        
        if result["web_accessibility"]:
            result["compliance"]["issues"] = []
            if not result["web_accessibility"].get("access_mode"):
                result["compliance"]["issues"].append("Missing access mode declaration")
            if not result["web_accessibility"].get("accessibility_features"):
                result["compliance"]["issues"].append("Missing accessibility features list")
            
            if not result["compliance"]["issues"]:
                result["compliance"]["wcag_level"] = "AA"
            elif len(result["compliance"]["issues"]) <= 2:
                result["compliance"]["wcag_level"] = "A"
            else:
                result["compliance"]["wcag_level"] = "Non-compliant"
        
        total_fields = (
            len(result["accessibility"]["text_alternatives"]) +
            len(result["accessibility"]["visual_descriptions"]) +
            len(result["accessibility"]["features"]) +
            len(result["accessibility"]["hazards"]) +
            len(result["multimedia_accessibility"]) +
            len(result["web_accessibility"]) +
            2
        )
        result["fields_extracted"] = total_fields
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract accessibility metadata: {str(e)}"}


def analyze_accessibility_compliance(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Analyze accessibility compliance for media file.
    
    Args:
        filepath: Path to file
    
    Returns:
        Dictionary with compliance analysis
    """
    result = {
        "overall_score": 0,
        "wcag_conformance": None,
        "issues": [],
        "recommendations": [],
        "missing_elements": []
    }
    
    accessibility_data = extract_accessibility_metadata(filepath)
    
    if "error" in accessibility_data:
        return {"error": accessibility_data["error"]}
    
    accessibility = accessibility_data.get("accessibility", {})
    web = accessibility_data.get("web_accessibility", {})
    multimedia = accessibility_data.get("multimedia_accessibility", {})
    
    score = 0
    max_score = 100
    
    has_alt_text = bool(accessibility.get("text_alternatives"))
    has_long_desc = "long_description" in accessibility.get("text_alternatives", {})
    
    if has_alt_text:
        score += 20
    if has_long_desc:
        score += 15
    
    features = accessibility.get("features", [])
    if features:
        score += 10
    else:
        result["missing_elements"].append("Accessibility features not declared")
    
    if multimedia.get("audio_description_available"):
        score += 15
    else:
        result["missing_elements"].append("No audio description")
    
    if multimedia.get("transcript_available"):
        score += 15
    else:
        result["missing_elements"].append("No transcript available")
    
    if multimedia.get("closed_captions_available") or multimedia.get("subtitles_available"):
        score += 15
    
    if web.get("access_mode"):
        score += 10
    
    if web.get("accessibility_features"):
        features_list = web["accessibility_features"]
        if isinstance(features_list, list):
            for f in features_list:
                if "text" in f.lower() or "audio" in f.lower():
                    score += 5
                    break
    
    result["overall_score"] = min(max_score, score)
    
    if result["overall_score"] >= 80:
        result["wcag_conformance"] = "AAA"
    elif result["overall_score"] >= 60:
        result["wcag_conformance"] = "AA"
    elif result["overall_score"] >= 40:
        result["wcag_conformance"] = "A"
    else:
        result["wcag_conformance"] = "Non-compliant"
    
    for missing in result["missing_elements"]:
        result["recommendations"].append(f"Add {missing} to improve accessibility")
    
    if not web.get("access_mode"):
        result["recommendations"].append("Add schema.org accessMode declaration")
    
    return result


def get_accessibility_field_count() -> int:
    """Return approximate number of accessibility fields."""
    return 20
