"""
IPTC and XMP Fallback Libraries
Alternative extraction methods when pyexiv2 is unavailable
"""

from typing import Dict, Any, Optional, List


try:
    from iptcinfo3 import IPTCInfo
    IPTCINFO3_AVAILABLE = True
except ImportError:
    IPTCINFO3_AVAILABLE = False


try:
    from libxmp import XMPFiles
    from libxmp.utils import object_to_dict
    LIBXMP_AVAILABLE = True
except ImportError:
    LIBXMP_AVAILABLE = False


def extract_iptc_fallback(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract IPTC metadata using iptcinfo3 as fallback.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with IPTC metadata
    """
    if not IPTCINFO3_AVAILABLE:
        return {"error": "iptcinfo3 not installed"}
    
    try:
        info = IPTCInfo(filepath)
        
        result = {
            "core": {},
            "extension": {},
            "available": True
        }
        
        if info.data:
            core_keywords = [
                ('headline', 'headline'),
                ('caption', 'description'),
                ('keywords', 'keywords'),
                ('byline', 'creator'),
                ('byline_title', 'creator_title'),
                ('credit', 'credit'),
                ('copyright', 'copyright_notice'),
                ('source', 'source'),
                ('city', 'city'),
                ('province_state', 'state_province'),
                ('country_name', 'country'),
                ('country_code', 'country_code'),
                ('sub_location', 'location'),
            ]
            
            for iptc_key, output_key in core_keywords:
                if iptc_key in info.data:
                    value = info.data[iptc_key]
                    result["core"][output_key] = value[0] if isinstance(value, list) else value
            
            if 'date_created' in info.data:
                result["core"]["date_created"] = str(info.data['date_created'][0])
            
            if 'object_name' in info.data:
                result["core"]["intellectual_genre"] = info.data['object_name'][0]
            
            if 'subject_reference' in info.data:
                result["extension"]["subject_codes"] = info.data['subject_reference']
            
            if 'edit_status' in info.data:
                result["extension"]["edit_status"] = info.data['edit_status'][0]
            
            if 'fixture_identifier' in info.data:
                result["extension"]["fixture"] = info.data['fixture_identifier'][0]
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract IPTC: {str(e)}"}


def extract_xmp_fallback(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract XMP metadata using libxmp as fallback.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with XMP metadata organized by namespace
    """
    if not LIBXMP_AVAILABLE:
        return {"error": "libxmp (python-xmp-toolkit) not installed"}
    
    try:
        xmpfile = XMPFiles(file_path=filepath)
        xmp = xmpfile.get_xmp()
        
        if not xmp:
            return {"xmp": {}, "available": True}
        
        result = {
            "dublin_core": {},
            "photoshop": {},
            "rights": {},
            "dc_prefs": {},
            "available": True
        }
        
        try:
            xmp_dict = object_to_dict(xmp)
            
            for ns, props in xmp_dict.items():
                if not isinstance(props, dict):
                    continue
                
                if 'dc' in ns or ns == 'http://purl.org/dc/elements/1.1/':
                    for key, value in props.items():
                        result["dublin_core"][key] = value
                
                elif 'photoshop' in ns or ns == 'http://ns.adobe.com/photoshop/1.0/':
                    for key, value in props.items():
                        result["photoshop"][key] = value
                
                elif 'xmpRights' in ns or ns == 'http://ns.adobe.com/xap/1.0/rights/':
                    for key, value in props.items():
                        result["rights"][key] = value
                
                elif 'dcprefs' in ns:
                    for key, value in props.items():
                        result["dc_prefs"][key] = value
        
        except Exception as e:
            logger.debug(f"Failed to extract fallback metadata: {e}")
        
        xmpfile.close_file()
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract XMP: {str(e)}"}


def extract_all_metadata_with_fallbacks(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata using all available methods with fallbacks.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Combined metadata from all sources
    """
    result = {
        "iptc": {"core": {}, "extension": {}},
        "xmp": {
            "dublin_core": {},
            "photoshop": {},
            "dc_prefs": {},
            "rights": {}
        },
        "extraction_methods": [],
        "fields_extracted": 0
    }
    
    iptc_result = extract_iptc_fallback(filepath)
    if "error" not in iptc_result:
        result["iptc"] = iptc_result
        result["extraction_methods"].append("iptcinfo3")
    
    xmp_result = extract_xmp_fallback(filepath)
    if "error" not in xmp_result:
        result["xmp"] = xmp_result
        result["extraction_methods"].append("libxmp")
    
    total_fields = (
        len(result["iptc"]["core"]) +
        len(result["iptc"]["extension"]) +
        len(result["xmp"]["dublin_core"]) +
        len(result["xmp"]["photoshop"]) +
        len(result["xmp"]["dc_prefs"]) +
        len(result["xmp"]["rights"])
    )
    result["fields_extracted"] = total_fields
    
    return result


def get_fallback_field_count() -> int:
    """Return approximate number of fields from fallback methods."""
    return 50
