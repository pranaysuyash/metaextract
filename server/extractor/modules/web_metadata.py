"""
Web and Open Graph Metadata Extraction
Open Graph Protocol, Twitter Cards, Schema.org, and web metadata
"""

from typing import Dict, Any, Optional


# Open Graph Protocol Tags
OPEN_GRAPH_TAGS = {
    "OG_Title": "og_title",
    "OG_Description": "og_description",
    "OG_Type": "og_type",
    "OG_URL": "og_url",
    "OG_Image": "og_image",
    "OG_Image_SecureURL": "og_image_secure_url",
    "OG_Image_Type": "og_image_type",
    "OG_Image_Width": "og_image_width",
    "OG_Image_Height": "og_image_height",
    "OG_SiteName": "og_site_name",
    "OG_Locale": "og_locale",
    "OG_Locale_Alternate": "og_locale_alternate",
    "OG_Video": "og_video",
    "OG_Video_SecureURL": "og_video_secure_url",
    "OG_Video_Type": "og_video_type",
    "OG_Video_Width": "og_video_width",
    "OG_Video_Height": "og_video_height",
    "OG_Audio": "og_audio",
    "OG_Audio_SecureURL": "og_audio_secure_url",
    "OG_Determiner": "og_determiner",
    "OG_Updated_Time": "og_updated_time",
    "OG_See_Also": "og_see_also",
    "OG_FB_AppID": "og_fb_app_id",
}

# Twitter Card Tags
TWITTER_CARD_TAGS = {
    "Twitter_Card": "twitter_card_type",
    "Twitter_Site": "twitter_site",
    "Twitter_Site_ID": "twitter_site_id",
    "Twitter_Creator": "twitter_creator",
    "Twitter_Creator_ID": "twitter_creator_id",
    "Twitter_Title": "twitter_title",
    "Twitter_Description": "twitter_description",
    "Twitter_Image": "twitter_image",
    "Twitter_Image_Alt": "twitter_image_alt",
    "Twitter_Image_Width": "twitter_image_width",
    "Twitter_Image_Height": "twitter_image_height",
    "Twitter_Player": "twitter_player",
    "Twitter_Player_Width": "twitter_player_width",
    "Twitter_Player_Height": "twitter_player_height",
    "Twitter_Player_Stream": "twitter_player_stream",
    "Twitter_Player_Stream_HTTPS": "twitter_player_stream_https",
    "Twitter_Donation_Amount": "twitter_donation_amount",
    "Twitter_Donation_Currency": "twitter_donation_currency",
    "Twitter_App_ID_Country": "twitter_app_country",
    "Twitter_App_Name_IPhone": "twitter_app_name_iphone",
    "Twitter_App_ID_IPhone": "twitter_app_id_iphone",
    "Twitter_App_Name_IPad": "twitter_app_name_ipad",
    "Twitter_App_ID_IPad": "twitter_app_id_ipad",
    "Twitter_App_Name_GooglePlay": "twitter_app_name_googleplay",
    "Twitter_App_ID_GooglePlay": "twitter_app_id_googleplay",
    "Twitter_URL_GooglePlay": "twitter_url_googleplay",
}

# Schema.org Tags
SCHEMA_ORG_TAGS = {
    "Schema_Type": "schema_type",
    "Schema_Name": "schema_name",
    "Schema_Description": "schema_description",
    "Schema_Image": "schema_image",
    "Schema_URL": "schema_url",
    "Schema_DatePublished": "schema_date_published",
    "Schema_DateModified": "schema_date_modified",
    "Schema_Author": "schema_author",
    "Schema_Publisher": "schema_publisher",
    "Schema_Creator": "schema_creator",
    "Schema_Headline": "schema_headline",
    "Schema_Body": "schema_body",
    "Schema_Keywords": "schema_keywords",
    "Schema_ArticleSection": "schema_article_section",
    "Schema_InLanguage": "schema_language",
    "Schema_Version": "schema_version",
    "Schema_MainEntityOfPage": "schema_main_entity",
    "Schema_PotentialAction": "schema_potential_action",
    "Schema_Identifier": "schema_identifier",
    "Schema_SameAs": "schema_same_as",
    "Schema_About": "schema_about",
    "Schema_Event": "schema_event",
    "Schema_Organization": "schema_organization",
    "Schema_Person": "schema_person",
    "Schema_Place": "schema_place",
    "Schema_Product": "schema_product",
    "Schema_Offer": "schema_offer",
    "Schema_AggregateRating": "schema_aggregate_rating",
    "Schema_Review": "schema_review",
    "Schema_RatingValue": "schema_rating_value",
    "Schema_RatingCount": "schema_rating_count",
    "Schema_BestRating": "schema_best_rating",
    "Schema_WorstRating": "schema_worst_rating",
    "Schema_Price": "schema_price",
    "Schema_PriceCurrency": "schema_price_currency",
    "Schema_PriceValidUntil": "schema_price_valid_until",
    "Schema_Availability": "schema_availability",
}

# Web Manifest Tags
WEB_MANIFEST_TAGS = {
    "WebManifest_Name": "web_manifest_name",
    "WebManifest_ShortName": "web_manifest_short_name",
    "WebManifest_Description": "web_manifest_description",
    "WebManifest_StartURL": "web_manifest_start_url",
    "WebManifest_Display": "web_manifest_display",
    "WebManifest_BackgroundColor": "web_manifest_bg_color",
    "WebManifest_ThemeColor": "web_manifest_theme_color",
    "WebManifest_Icons": "web_manifest_icons",
    "WebManifest_Screenshot": "web_manifest_screenshot",
    "WebManifest_Categories": "web_manifest_categories",
    "WebManifest_Orientation": "web_manifest_orientation",
    "WebManifest_Scope": "web_manifest_scope",
    "WebManifest_Shortcuts": "web_manifest_shortcuts",
    "WebManifest_RelatedApplications": "web_manifest_related_apps",
    "WebManifest_PreferRelatedApplications": "web_manifest_prefer_related",
    "WebManifest_ProtocolHandler": "web_manifest_protocol_handler",
}

# Dublin Core for Web
DC_WEB_TAGS = {
    "DC_Title": "dc_title",
    "DC_Creator": "dc_creator",
    "DC_Subject": "dc_subject",
    "DC_Description": "dc_description",
    "DC_Publisher": "dc_publisher",
    "DC_Contributor": "dc_contributor",
    "DC_Date": "dc_date",
    "DC_Type": "dc_type",
    "DC_Format": "dc_format",
    "DC_Identifier": "dc_identifier",
    "DC_Source": "dc_source",
    "DC_Language": "dc_language",
    "DC_Relation": "dc_relation",
    "DC_Coverage": "dc_coverage",
    "DC_Rights": "dc_rights",
    "DC_Medium": "dc_medium",
    "DC_Extent": "dc_extent",
}


def extract_web_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract web and Open Graph metadata from files.
    
    Args:
        filepath: Path to image/file
    
    Returns:
        Dictionary with web metadata
    """
    result = {
        "web": {
            "open_graph": {},
            "twitter_cards": {},
            "schema_org": {},
            "web_manifest": {},
            "dublin_core": {}
        },
        "social_sharing": {
            "optimized": False,
            "platforms": []
        },
        "fields_extracted": 0
    }
    
    try:
        from .exif import extract_exif_metadata
        from .iptc_xmp import extract_iptc_xmp_metadata
        
        all_tags = {}
        
        exif_data = extract_exif_metadata(filepath)
        if exif_data and "error" not in exif_data:
            for category in ["image", "photo", "gps", "interoperability"]:
                if category in exif_data and isinstance(exif_data[category], dict):
                    all_tags.update(exif_data[category])
        
        iptc_data = extract_iptc_xmp_metadata(filepath)
        if iptc_data and "error" not in iptc_data and isinstance(iptc_data, dict):
            for section in iptc_data.values():
                if isinstance(section, dict):
                    all_tags.update(section)
        
        for tag, value in all_tags.items():
            tag_str = str(tag)
            
            if tag_str.startswith("OG_") or "OpenGraph" in tag_str:
                key = tag_str.replace("OG_", "").replace("Xmp.exif.", "")
                if key in [t.replace("OG_", "") for t in OPEN_GRAPH_TAGS.keys()]:
                    result["web"]["open_graph"][key.lower()] = str(value)
            
            elif tag_str.startswith("Twitter_") or "twitter" in tag_str.lower():
                key = tag_str.replace("Twitter_", "").replace("Xmp.exif.", "")
                if key in [t.replace("Twitter_", "") for t in TWITTER_CARD_TAGS.keys()]:
                    result["web"]["twitter_cards"][key.lower()] = str(value)
            
            elif tag_str.startswith("Schema_") or "schema" in tag_str.lower():
                key = tag_str.replace("Schema_", "").replace("Xmp.", "")
                result["web"]["schema_org"][key.lower()] = str(value)
            
            elif "WebManifest" in tag_str or "manifest" in tag_str.lower():
                key = tag_str.replace("WebManifest_", "").replace("Xmp.", "")
                result["web"]["web_manifest"][key.lower()] = str(value)
            
            elif tag_str.startswith("DC_") or "DublinCore" in tag_str:
                key = tag_str.replace("DC_", "").replace("Xmp.dc.", "")
                result["web"]["dublin_core"][key.lower()] = str(value)
        
        platforms = []
        if result["web"]["open_graph"]:
            platforms.append("facebook")
            platforms.append("linkedin")
        if result["web"]["twitter_cards"]:
            platforms.append("twitter")
            platforms.append("slack")
        if result["web"]["schema_org"]:
            platforms.append("google")
            platforms.append("pinterest")
        if result["web"]["web_manifest"]:
            platforms.append("pwa")
        
        result["social_sharing"]["platforms"] = list(set(platforms))
        if platforms:
            result["social_sharing"]["optimized"] = True
        
        total_fields = sum(len(v) for v in result["web"].values())
        result["fields_extracted"] = total_fields
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract web metadata: {str(e)}"}


def analyze_web_presence(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Analyze web and social sharing readiness.
    
    Args:
        filepath: Path to file
    
    Returns:
        Dictionary with web presence analysis
    """
    result = {
        "web_readiness": {
            "score": 0,
            "grade": "Not Ready",
            "issues": []
        },
        "social_platforms": {},
        "recommendations": []
    }
    
    web_data = extract_web_metadata(filepath)
    
    if "error" in web_data:
        return {"error": web_data["error"]}
    
    og = web_data.get("web", {}).get("open_graph", {})
    twitter = web_data.get("web", {}).get("twitter_cards", {})
    schema = web_data.get("web", {}).get("schema_org", {})
    
    score = 0
    max_score = 100
    
    if og.get("title"):
        score += 10
    else:
        result["web_readiness"]["issues"].append("Missing Open Graph title")
    
    if og.get("description"):
        score += 10
    else:
        result["web_readiness"]["issues"].append("Missing Open Graph description")
    
    if og.get("image"):
        score += 15
    else:
        result["web_readiness"]["issues"].append("Missing Open Graph image")
    
    if twitter.get("twitter_card_type"):
        score += 10
        if twitter["twitter_card_type"] in ["summary_large_image", "player"]:
            score += 10
    else:
        result["web_readiness"]["issues"].append("Missing Twitter Card type")
    
    if schema.get("type"):
        score += 15
        if schema["type"] in ["ImageObject", "Photograph"]:
            score += 5
    else:
        result["web_readiness"]["issues"].append("Missing Schema.org type")
    
    if og.get("site_name"):
        score += 5
    
    if og.get("locale"):
        score += 5
    
    if og.get("url"):
        score += 5
    
    result["web_readiness"]["score"] = score
    
    if score >= 80:
        result["web_readiness"]["grade"] = "Excellent"
    elif score >= 60:
        result["web_readiness"]["grade"] = "Good"
    elif score >= 40:
        result["web_readiness"]["grade"] = "Fair"
    elif score >= 20:
        result["web_readiness"]["grade"] = "Poor"
    else:
        result["web_readiness"]["grade"] = "Not Ready"
    
    result["social_platforms"]["facebook"] = bool(og.get("title") and og.get("image"))
    result["social_platforms"]["twitter"] = bool(twitter.get("twitter_card_type"))
    result["social_platforms"]["linkedin"] = bool(og.get("title") and og.get("description"))
    result["social_platforms"]["pinterest"] = bool(schema.get("image"))
    result["social_platforms"]["slack"] = bool(og.get("title") and og.get("image"))
    
    for issue in result["web_readiness"]["issues"]:
        if "title" in issue:
            result["recommendations"].append("Add <meta property='og:title' content='...'/>")
        if "description" in issue:
            result["recommendations"].append("Add <meta property='og:description' content='...'/>")
        if "image" in issue:
            result["recommendations"].append("Add <meta property='og:image' content='...'/>")
    
    return result


def get_web_metadata_field_count() -> int:
    """Return approximate number of web metadata fields."""
    return 75
