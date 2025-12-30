"""
IPTC and XMP Metadata Extraction
Professional metadata for stock photography, editorial use, and DAM
"""

from typing import Dict, Any, Optional


import json
import shutil
import subprocess

try:
    from pyexiv2 import Image as ExivImage
    EXIV2_AVAILABLE = True
except ImportError:
    ExivImage = None
    EXIV2_AVAILABLE = False


EXIFTOOL_PATH = shutil.which("exiftool")
EXIFTOOL_AVAILABLE = EXIFTOOL_PATH is not None


def _run_exiftool_iptc_xmp(filepath: str) -> Optional[Dict[str, Any]]:
    if not EXIFTOOL_AVAILABLE or EXIFTOOL_PATH is None:
        return None

    try:
        cmd = [
            EXIFTOOL_PATH,
            "-j",
            "-n",
            "-G1",
            "-s",
            "-a",
            "-u",
            "-f",
            "-IPTC:all",
            "-XMP:all",
            filepath,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return None
        parsed = json.loads(result.stdout)
        if isinstance(parsed, list) and parsed:
            return parsed[0]
        return None
    except Exception as e:
        return None


def _safe_str(value: Any) -> str:
    try:
        return str(value)
    except Exception as e:
        return ""


IPTC_CORE_FIELDS = {
    "Iptc.Application2.Headline": "headline",
    "Iptc.Application2.Caption": "description",
    "Iptc.Application2.Keywords": "keywords",
    "Iptc.Application2.Byline": "creator",
    "Iptc.Application2.BylineTitle": "creator_title",
    "Iptc.Application2.Credit": "credit",
    "Iptc.Application2.Copyright": "copyright_notice",
    "Iptc.Application2.Source": "source",
    "Iptc.Application2.City": "city",
    "Iptc.Application2.ProvinceState": "state_province",
    "Iptc.Application2.CountryName": "country",
    "Iptc.Application2.CountryCode": "country_code",
    "Iptc.Application2.SubLocation": "location",
    "Iptc.Application2.TransmissionReference": "transmission_reference",
    "Iptc.Application2.SpecialInstructions": "instructions",
    "Iptc.Application2.DateCreated": "date_created",
    "Iptc.Application2.ObjectType": "intellectual_genre",
    "Iptc.Application2.SubjectCode": "subject_codes",
}


IPTC_EXTENSION_FIELDS = {
    "Iptc.Application2.PersonInImage": "persons_shown",
    "Iptc.Application2.DigitalSourceType": "digital_source_type",
    "Iptc.Application2.OrganisationInImageName": "organizations",
    "Iptc.Application2.Event": "event",
    "Iptc.Application2.MaxAvailWidth": "max_available_width",
    "Iptc.Application2.MaxAvailHeight": "max_available_height",
    "Iptc.Application2.ModelReleaseStatus": "model_release_status",
    "Iptc.Application2.PropertyReleaseStatus": "property_release_status",
    "Iptc.Application2.CopyrightNotice": "copyright_notice",
    "Iptc.Application2.UsageTerms": "usage_terms",
    "Iptc.Application2.WebStatement": "web_statement",
    "Iptc.Application2.ImageType": "image_type",
    "Iptc.Application2.Urgency": "urgency",
    "Iptc.Application2.Scene": "scene_codes",
    "Iptc.Application2.SubjectReference": "subject_reference",
    "Iptc.Application2.LocationCreated": "location_created",
    "Iptc.Application2.LocationShown": "location_shown",
}


IPTC_CREATOR_CONTACT_INFO = {
    "Iptc.Application2.Contact": "creator_contact",
    "Iptc.Application2.Phone1": "phone_1",
    "Iptc.Application2.Phone2": "phone_2",
    "Iptc.Application2.Email1": "email_1",
    "Iptc.Application2.Email2": "email_2",
    "Iptc.Application2.WebURL": "web_url",
}


IPTC_LICENSOR = {
    "Iptc.Application2.Licensor": "licensor",
    "Iptc.Application2.LicensorName": "licensor_name",
    "Iptc.Application2.LicensorURL": "licensor_url",
    "Iptc.Application2.LicensorEmail": "licensor_email",
    "Iptc.Application2.LicensorTelephone1": "licensor_phone_1",
    "Iptc.Application2.LicensorTelephone2": "licensor_phone_2",
    "Iptc.Application2.LicensorAddress": "licensor_address",
    "Iptc.Application2.LicensorCity": "licensor_city",
    "Iptc.Application2.LicensorState": "licensor_state",
    "Iptc.Application2.LicensorPostalCode": "licensor_postal_code",
    "Iptc.Application2.LicensorCountry": "licensor_country",
}


XMP_DUBLIN_CORE_FIELDS = {
    "Xmp.dc.title": "title",
    "Xmp.dc.description": "description",
    "Xmp.dc.creator": "creator",
    "Xmp.dc.subject": "subject",
    "Xmp.dc.rights": "rights",
    "Xmp.dc.date": "date",
    "Xmp.dc.format": "format",
    "Xmp.dc.language": "language",
    "Xmp.dc.publisher": "publisher",
    "Xmp.dc.contributor": "contributor",
    "Xmp.dc.type": "type",
    "Xmp.dc.identifier": "identifier",
    "Xmp.dc.source": "source",
    "Xmp.dc.coverage": "coverage",
    "Xmp.dc.relation": "relation",
    "Xmp.dc.medium": "medium",
    "Xmp.dc.extent": "extent",
    "Xmp.dc.provenance": "provenance",
    "Xmp.dc.rightsHolder": "rights_holder",
    "Xmp.dc.audience": "audience",
    "Xmp.dc.abstract": "abstract",
    "Xmp.dc.tableOfContents": "table_of_contents",
}


XMP_PHOTOSHOP_FIELDS = {
    "Xmp.photoshop.Headline": "headline",
    "Xmp.photoshop.Credit": "credit",
    "Xmp.photoshop.Source": "source",
    "Xmp.photoshop.CaptionWriter": "caption_writer",
    "Xmp.photoshop.Instructions": "instructions",
    "Xmp.photoshop.DateCreated": "date_created",
    "Xmp.photoshop.City": "city",
    "Xmp.photoshop.State": "state",
    "Xmp.photoshop.Country": "country",
    "Xmp.photoshop.AuthorsPosition": "authors_position",
    "Xmp.photoshop.TransmissionReference": "transmission_reference",
    "Xmp.photoshop.Category": "category",
    "Xmp.photoshop.SupplementalCategories": "supplemental_categories",
    "Xmp.photoshop.Urgency": "urgency",
    "Xmp.photoshop.Version": "photoshop_version",
    "Xmp.photoshop.ColorMode": "color_mode",
    "Xmp.photoshop.ICCProfile": "icc_profile",
    "Xmp.photoshop.Animated": "animated",
    "Xmp.photoshop.Timing": "timing",
}


XMP_DC_PREFS_FIELDS = {
    "Xmp.dcprefs.History": "edit_history",
    "Xmp.dcprefs.Rating": "rating",
    "Xmp.dcprefs.WebStatement": "web_statement",
}


XMP_RIGHTS_MANAGEMENT = {
    "Xmp.xmpRights.Marked": "rights_marked",
    "Xmp.xmpRights.WebStatement": "rights_web_statement",
    "Xmp.xmpRights.Certificate": "rights_certificate",
    "Xmp.xmpRights.UsageTerms": "rights_usage_terms",
    "Xmp.xmpRights.Adobe": "rights_adobe",
}


XMP_CREATOR_CONTACT = {
    "Xmp.creatorContactInfo.CiAdrCity": "contact_city",
    "Xmp.creatorContactInfo.CiAdrCtry": "contact_country",
    "Xmp.creatorContactInfo.CiAdrExtadr": "contact_address",
    "Xmp.creatorContactInfo.CiAdrPcode": "contact_postal_code",
    "Xmp.creatorContactInfo.CiAdrRegion": "contact_region",
    "Xmp.creatorContactInfo.CiTelWork": "contact_phone",
    "Xmp.creatorContactInfo.CiEmailWork": "contact_email",
    "Xmp.creatorContactInfo.CiUrlWork": "contact_url",
}


XMP_ADOBE_STOCK = {
    "Xmp.adobe stock.AssetId": "stock_asset_id",
    "Xmp.adobe stock.Url": "stock_url",
    "Xmp.adobe stock.PreviewUrl": "stock_preview_url",
    "Xmp.adobe stock.CreationDate": "stock_creation_date",
    "Xmp.adobe stock.ModificationDate": "stock_modification_date",
}


def extract_iptc_xmp_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """Extract IPTC and XMP professional metadata from images."""
    if not EXIV2_AVAILABLE or ExivImage is None:
        # Fallback to exiftool when available.
        raw = _run_exiftool_iptc_xmp(filepath)
        if not raw:
            # Preserve existing behavior when neither `pyexiv2` nor exiftool are available.
            raise ImportError("pyexiv2 is required but not installed")

        result: Dict[str, Any] = {
            "iptc": {},
            "xmp": {},
            "xmp_namespaces": {},
            "available": True,
            "fields_extracted": 0,
        }

        for key, value in raw.items():
            if value is None or value == "" or value == "-":
                continue

            if ":" not in key:
                continue

            group, tag = key.split(":", 1)
            if group.startswith("IPTC"):
                result["iptc"][tag] = value
                continue

            if group.startswith("XMP"):
                result["xmp"][key] = value
                ns = group.replace("XMP-", "") if group.startswith("XMP-") else "xmp"
                if ns not in result["xmp_namespaces"]:
                    result["xmp_namespaces"][ns] = {}
                if isinstance(result["xmp_namespaces"][ns], dict):
                    result["xmp_namespaces"][ns][tag] = value

        result["fields_extracted"] = len(result["iptc"]) + len(result["xmp"])
        return result
    
    result = {
        "iptc": {"core": {}, "extension": {}, "contact": {}, "licensor": {}},
        "xmp": {
            "dublin_core": {},
            "photoshop": {},
            "dc_prefs": {},
            "rights_management": {},
            "creator_contact": {},
            "adobe_stock": {}
        },
        "available": True,
        "fields_extracted": 0
    }
    
    try:
        img = ExivImage(filepath)
        
        # Extract IPTC Core
        for tag, field in IPTC_CORE_FIELDS.items():
            try:
                value = img.read_iptc(tag)
                if value:
                    result["iptc"]["core"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract IPTC Extension
        for tag, field in IPTC_EXTENSION_FIELDS.items():
            try:
                value = img.read_iptc(tag)
                if value:
                    result["iptc"]["extension"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract IPTC Creator Contact
        for tag, field in IPTC_CREATOR_CONTACT_INFO.items():
            try:
                value = img.read_iptc(tag)
                if value:
                    result["iptc"]["contact"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract IPTC Licensor
        for tag, field in IPTC_LICENSOR.items():
            try:
                value = img.read_iptc(tag)
                if value:
                    result["iptc"]["licensor"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract XMP Dublin Core
        for tag, field in XMP_DUBLIN_CORE_FIELDS.items():
            try:
                value = img.read_xmp(tag)
                if value:
                    result["xmp"]["dublin_core"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract XMP Photoshop
        for tag, field in XMP_PHOTOSHOP_FIELDS.items():
            try:
                value = img.read_xmp(tag)
                if value:
                    result["xmp"]["photoshop"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract XMP DC Prefs
        for tag, field in XMP_DC_PREFS_FIELDS.items():
            try:
                value = img.read_xmp(tag)
                if value:
                    result["xmp"]["dc_prefs"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract XMP Rights Management
        for tag, field in XMP_RIGHTS_MANAGEMENT.items():
            try:
                value = img.read_xmp(tag)
                if value:
                    result["xmp"]["rights_management"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract XMP Creator Contact
        for tag, field in XMP_CREATOR_CONTACT.items():
            try:
                value = img.read_xmp(tag)
                if value:
                    result["xmp"]["creator_contact"][field] = str(value)
            except Exception as e:
                continue
        
        # Extract XMP Adobe Stock
        for tag, field in XMP_ADOBE_STOCK.items():
            try:
                value = img.read_xmp(tag)
                if value:
                    result["xmp"]["adobe_stock"][field] = str(value)
            except Exception as e:
                continue
        
        # Count fields
        total_fields = (
            len(result["iptc"]["core"]) +
            len(result["iptc"]["extension"]) +
            len(result["iptc"]["contact"]) +
            len(result["iptc"]["licensor"]) +
            len(result["xmp"]["dublin_core"]) +
            len(result["xmp"]["photoshop"]) +
            len(result["xmp"]["dc_prefs"]) +
            len(result["xmp"]["rights_management"]) +
            len(result["xmp"]["creator_contact"]) +
            len(result["xmp"]["adobe_stock"])
        )
        result["fields_extracted"] = total_fields
        
        return result
        
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except Exception as e:
        return {
            "error": f"Failed to extract IPTC/XMP: {str(e)}",
            "available": True
        }


def get_iptc_field_count() -> int:
    """Return approximate number of IPTC/XMP fields.

    Notes:
        When `exiftool` is available, MetaExtract can expose far more IPTC and XMP
        tags than the in-module curated subset.
    """
    # Derived from `exiftool -listx -IPTC:All` and `exiftool -listx -XMP:All`.
    return 117 + 4250
