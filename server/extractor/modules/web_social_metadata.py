# server/extractor/modules/web_social_metadata.py

"""
Web and Social Media metadata extraction for Phase 3.

Extracts metadata from:
- Open Graph protocol
- Twitter Cards
- Schema.org structured data
- Web App Manifest
- Microdata
- Social media embeds
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from urllib.parse import urlparse
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location

logger = logging.getLogger(__name__)

# Common social media domains and their metadata patterns
SOCIAL_DOMAINS = {
    'twitter.com': 'twitter',
    'x.com': 'twitter',
    'facebook.com': 'facebook',
    'instagram.com': 'instagram',
    'linkedin.com': 'linkedin',
    'youtube.com': 'youtube',
    'tiktok.com': 'tiktok',
    'pinterest.com': 'pinterest',
    'reddit.com': 'reddit',
    'tumblr.com': 'tumblr',
}

# Open Graph property mappings
OPEN_GRAPH_PROPERTIES = {
    'og:title': 'opengraph_title',
    'og:type': 'opengraph_type',
    'og:image': 'opengraph_image',
    'og:image:width': 'opengraph_image_width',
    'og:image:height': 'opengraph_image_height',
    'og:image:alt': 'opengraph_image_alt',
    'og:url': 'opengraph_url',
    'og:description': 'opengraph_description',
    'og:site_name': 'opengraph_site_name',
    'og:locale': 'opengraph_locale',
    'og:video': 'opengraph_video',
    'og:video:width': 'opengraph_video_width',
    'og:video:height': 'opengraph_video_height',
    'og:audio': 'opengraph_audio',
    'og:determiner': 'opengraph_determiner',
    'article:author': 'article_author',
    'article:publisher': 'article_publisher',
    'article:published_time': 'article_published_time',
    'article:modified_time': 'article_modified_time',
    'article:section': 'article_section',
    'article:tag': 'article_tags',
    'book:author': 'book_author',
    'book:isbn': 'book_isbn',
    'book:release_date': 'book_release_date',
    'profile:first_name': 'profile_first_name',
    'profile:last_name': 'profile_last_name',
    'profile:username': 'profile_username',
    'profile:gender': 'profile_gender',
    'music:song': 'music_song',
    'music:album': 'music_album',
    'music:musician': 'music_musician',
    'video:actor': 'video_actor',
    'video:director': 'video_director',
    'video:writer': 'video_writer',
    'video:duration': 'video_duration',
    'video:release_date': 'video_release_date',
    'video:tag': 'video_tag',
}

# Twitter Card properties
TWITTER_CARD_PROPERTIES = {
    'twitter:card': 'twitter_card_type',
    'twitter:site': 'twitter_site',
    'twitter:site:id': 'twitter_site_id',
    'twitter:creator': 'twitter_creator',
    'twitter:creator:id': 'twitter_creator_id',
    'twitter:title': 'twitter_title',
    'twitter:description': 'twitter_description',
    'twitter:image': 'twitter_image',
    'twitter:image:alt': 'twitter_image_alt',
    'twitter:player': 'twitter_player',
    'twitter:player:width': 'twitter_player_width',
    'twitter:player:height': 'twitter_player_height',
    'twitter:player:stream': 'twitter_player_stream',
    'twitter:app:name:iphone': 'twitter_app_iphone_name',
    'twitter:app:id:iphone': 'twitter_app_iphone_id',
    'twitter:app:url:iphone': 'twitter_app_iphone_url',
    'twitter:app:name:ipad': 'twitter_app_ipad_name',
    'twitter:app:id:ipad': 'twitter_app_ipad_id',
    'twitter:app:url:ipad': 'twitter_app_ipad_url',
    'twitter:app:name:googleplay': 'twitter_app_googleplay_name',
    'twitter:app:id:googleplay': 'twitter_app_googleplay_id',
    'twitter:app:url:googleplay': 'twitter_app_googleplay_url',
    'twitter:app:country': 'twitter_app_country',
}


@lru_cache(maxsize=1)
def _load_web_standards_fields() -> List[str]:
    root = Path(__file__).resolve().parents[3]
    inventory_path = root / "scripts" / "inventory_web_standards.py"
    normalized_fields: List[str] = [
        "opengraph_present",
        "opengraph_property_count",
        "twitter_cards_present",
        "twitter_card_property_count",
        "schema_org_present",
        "schema_org_json_ld_count",
        "schema_org_objects",
        "schema_name",
        "schema_description",
        "schema_url",
        "schema_image",
        "schema_datePublished",
        "schema_dateModified",
        "schema_author",
        "schema_publisher",
        "web_manifest_url",
        "web_manifest_present",
        "web_theme_color",
        "web_apple_touch_icon",
        "manifest_keys",
        "manifest.name",
        "manifest.short_name",
        "manifest.start_url",
        "manifest.display",
        "manifest.display_override",
        "manifest.orientation",
        "manifest.background_color",
        "manifest.theme_color",
        "manifest.lang",
        "manifest.dir",
        "manifest.description",
        "manifest.scope",
        "manifest.icons.count",
        "manifest.icons.types",
        "manifest.screenshots.count",
        "manifest.shortcuts.count",
        "manifest.related_applications.count",
        "manifest.serviceworker.src",
        "manifest.serviceworker.scope",
        "manifest.serviceworker.update_via_cache",
        "social_embed_twitter",
        "social_embed_facebook",
        "social_embed_instagram",
        "social_embed_youtube",
        "social_embed_vimeo",
        "social_embed_tiktok",
        "social_embed_linkedin",
        "microdata_present",
        "microdata_item_count",
        "microdata_types",
        "url_domain",
        "url_path",
        "url_query",
        "twitter_status_id",
        "instagram_post_id",
    ]
    normalized_fields.extend(list(OPEN_GRAPH_PROPERTIES.values()))
    normalized_fields.extend(list(TWITTER_CARD_PROPERTIES.values()))
    if inventory_path.exists():
        try:
            spec = spec_from_file_location("inventory_web_standards", inventory_path)
            if spec and spec.loader:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                fields: List[str] = []
                for name in [
                    "OPEN_GRAPH_FIELDS",
                    "TWITTER_CARDS_FIELDS",
                    "SCHEMA_ORG_FIELDS",
                    "WEB_APP_MANIFEST_FIELDS",
                    "PWA_FIELDS",
                    "SECURITY_FIELDS",
                ]:
                    values = getattr(module, name, None)
                    if isinstance(values, list):
                        fields.extend([str(value) for value in values])
                fields.extend(normalized_fields)
                if fields:
                    return sorted(set(fields))
        except Exception:
            pass
    if normalized_fields:
        return sorted(set(normalized_fields))
    return []


def get_web_standards_registry_fields() -> List[str]:
    return _load_web_standards_fields()


def extract_web_social_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract web and social media metadata from HTML files.

    Supports Open Graph, Twitter Cards, Schema.org, and other web standards.
    """
    result: Dict[str, Any] = {}

    try:
        # Read HTML content
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        # Extract meta tags
        meta_tags = _extract_meta_tags(html_content)
        result.update(meta_tags)

        # Extract Open Graph data
        og_data = _extract_open_graph(html_content)
        result.update(og_data)

        # Extract Twitter Cards
        twitter_data = _extract_twitter_cards(html_content)
        result.update(twitter_data)

        # Extract Schema.org structured data
        schema_data = _extract_schema_org(html_content)
        result.update(schema_data)

        # Extract Web App Manifest references
        manifest_data = _extract_web_manifest(html_content, Path(filepath).parent)
        result.update(manifest_data)

        # Extract social media embeds
        social_embeds = _extract_social_embeds(html_content)
        result.update(social_embeds)

        # Extract microdata
        microdata = _extract_microdata(html_content)
        result.update(microdata)

        # Analyze URL structure if available
        url_analysis = _analyze_url_structure(filepath)
        result.update(url_analysis)

        registry_fields = get_web_standards_registry_fields()
        registry = {
            "available": True,
            "fields_extracted": 0,
            "tags": {},
            "unknown_tags": {},
            "field_catalog": registry_fields,
        }
        for key, value in result.items():
            registry["tags"][key] = {"name": key, "value": value}
            if registry_fields and key not in registry_fields:
                registry["unknown_tags"][key] = {"name": key, "value": value}
        registry["fields_extracted"] = len(registry["tags"])
        result["registry"] = registry

    except Exception as e:
        logger.warning(f"Error extracting web/social metadata from {filepath}: {e}")
        result['web_social_extraction_error'] = str(e)

    return result


def _extract_meta_tags(html: str) -> Dict[str, Any]:
    """Extract all meta tags from HTML."""
    meta_data = {}

    # Find all meta tags
    meta_pattern = r'<meta[^>]+>'
    meta_tags = re.findall(meta_pattern, html, re.IGNORECASE)

    for tag in meta_tags:
        # Extract name/content or property/content pairs
        name_match = re.search(r'name=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        property_match = re.search(r'property=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        content_match = re.search(r'content=["\']([^"\']*)["\']', tag, re.IGNORECASE)

        if content_match:
            content = content_match.group(1)

            if name_match:
                name = name_match.group(1).lower()
                meta_data[f'meta_{name}'] = content
            elif property_match:
                prop = property_match.group(1)
                meta_data[f'meta_property_{prop}'] = content

    return meta_data


def _extract_open_graph(html: str) -> Dict[str, Any]:
    """Extract Open Graph protocol metadata."""
    og_data = {'opengraph_present': False}

    # Find Open Graph meta tags
    og_pattern = r'<meta[^>]*property=["\']og:([^"\']+)["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
    og_matches = re.findall(og_pattern, html, re.IGNORECASE)

    if og_matches:
        og_data['opengraph_present'] = True
        og_data['opengraph_property_count'] = len(og_matches)

        for prop, content in og_matches:
            field_name = OPEN_GRAPH_PROPERTIES.get(f'og:{prop}', f'opengraph_{prop.replace(":", "_")}')
            og_data[field_name] = content
            og_data[f'og:{prop}'] = content

    # Also check for article: and other prefixes
    for prefix in ['article:', 'book:', 'profile:', 'music:', 'video:']:
        prefix_pattern = f'<meta[^>]*property=["\']{prefix}([^"\']+)["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
        prefix_matches = re.findall(prefix_pattern, html, re.IGNORECASE)

        for prop, content in prefix_matches:
            field_name = OPEN_GRAPH_PROPERTIES.get(f'{prefix}{prop}', f'{prefix.replace(":", "")}_{prop.replace(":", "_")}')
            og_data[field_name] = content
            og_data[f'{prefix}{prop}'] = content

    return og_data


def _extract_twitter_cards(html: str) -> Dict[str, Any]:
    """Extract Twitter Card metadata."""
    twitter_data = {'twitter_cards_present': False}

    # Find Twitter Card meta tags
    twitter_pattern = r'<meta[^>]*name=["\']twitter:([^"\']+)["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
    twitter_matches = re.findall(twitter_pattern, html, re.IGNORECASE)

    if twitter_matches:
        twitter_data['twitter_cards_present'] = True
        twitter_data['twitter_card_property_count'] = len(twitter_matches)

        for prop, content in twitter_matches:
            field_name = TWITTER_CARD_PROPERTIES.get(f'twitter:{prop}', f'twitter_{prop.replace(":", "_")}')
            twitter_data[field_name] = content
            twitter_data[f'twitter:{prop}'] = content

    return twitter_data


def _extract_schema_org(html: str) -> Dict[str, Any]:
    """Extract Schema.org structured data (JSON-LD and Microdata)."""
    schema_data = {'schema_org_present': False}

    # JSON-LD extraction
    json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    json_ld_scripts = re.findall(json_ld_pattern, html, re.IGNORECASE | re.DOTALL)

    schema_objects = []
    for script in json_ld_scripts:
        try:
            # Clean up the JSON
            script = script.strip()
            if script:
                data = json.loads(script)
                schema_objects.append(data)
                schema_data['schema_org_present'] = True
        except json.JSONDecodeError:
            continue

    if schema_objects:
        schema_data['schema_org_json_ld_count'] = len(schema_objects)
        schema_data['schema_org_objects'] = schema_objects

        # Extract common Schema.org properties
        for obj in schema_objects:
            if isinstance(obj, dict):
                schema_type = obj.get('@type', obj.get('type', 'Unknown'))
                schema_data[f'schema_type_{schema_type.lower().replace(".", "_")}'] = True

                # Extract common properties
                for prop in ['name', 'description', 'url', 'image', 'datePublished', 'dateModified', 'author', 'publisher']:
                    if prop in obj:
                        schema_data[f'schema_{prop}'] = obj[prop]

    return schema_data


def _extract_web_manifest(html: str, base_path: Optional[Path] = None) -> Dict[str, Any]:
    """Extract Web App Manifest references."""
    manifest_data = {}

    # Look for manifest link tag
    manifest_pattern = r'<link[^>]*rel=["\']manifest["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
    manifest_match = re.search(manifest_pattern, html, re.IGNORECASE)

    if manifest_match:
        manifest_data['web_manifest_url'] = manifest_match.group(1)
        manifest_data['web_manifest_present'] = True
        if base_path:
            manifest_path = _resolve_local_manifest_path(base_path, manifest_match.group(1))
            if manifest_path and manifest_path.exists():
                manifest_payload = _load_manifest_json(manifest_path)
                if manifest_payload:
                    manifest_data.update(_extract_manifest_fields(manifest_payload))

    # Look for theme-color meta tag
    theme_pattern = r'<meta[^>]*name=["\']theme-color["\'][^>]*content=["\']([^"\']+)["\'][^>]*>'
    theme_match = re.search(theme_pattern, html, re.IGNORECASE)

    if theme_match:
        manifest_data['web_theme_color'] = theme_match.group(1)

    # Look for apple-touch-icon
    apple_icon_pattern = r'<link[^>]*rel=["\']apple-touch-icon[^"\']*["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
    apple_icon_match = re.search(apple_icon_pattern, html, re.IGNORECASE)

    if apple_icon_match:
        manifest_data['web_apple_touch_icon'] = apple_icon_match.group(1)

    return manifest_data


def _resolve_local_manifest_path(base_path: Path, manifest_url: str) -> Optional[Path]:
    if not manifest_url:
        return None
    parsed = urlparse(manifest_url)
    if parsed.scheme or parsed.netloc:
        return None
    candidate = Path(manifest_url)
    if not candidate.is_absolute():
        candidate = (base_path / candidate).resolve()
    return candidate


def _load_manifest_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if path.stat().st_size > 1_000_000:
            return None
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def _extract_manifest_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
    manifest_fields: Dict[str, Any] = {}
    if not isinstance(payload, dict):
        return manifest_fields

    manifest_fields["manifest_keys"] = sorted(payload.keys())
    for key in [
        "name",
        "short_name",
        "start_url",
        "display",
        "display_override",
        "orientation",
        "background_color",
        "theme_color",
        "lang",
        "dir",
        "description",
        "scope",
    ]:
        if key in payload:
            manifest_fields[f"manifest.{key}"] = payload.get(key)

    for list_key in ["icons", "screenshots", "shortcuts", "related_applications"]:
        if list_key in payload and isinstance(payload.get(list_key), list):
            manifest_fields[f"manifest.{list_key}.count"] = len(payload[list_key])
            if list_key == "icons":
                manifest_fields["manifest.icons.types"] = list(
                    {entry.get("type") for entry in payload[list_key] if isinstance(entry, dict) and entry.get("type")}
                )

    service_worker = payload.get("serviceworker")
    if isinstance(service_worker, dict):
        for sub_key in ["src", "scope", "update_via_cache"]:
            if sub_key in service_worker:
                manifest_fields[f"manifest.serviceworker.{sub_key}"] = service_worker.get(sub_key)

    return manifest_fields


def _extract_social_embeds(html: str) -> Dict[str, Any]:
    """Extract social media embed information."""
    embeds = {}

    # Twitter embeds - check for Twitter classes or twitter.com domain
    if 'twitter.com' in html or 'x.com' in html or 'twitter-tweet' in html or 'twitter-timeline' in html:
        embeds['social_embed_twitter'] = True

    # Facebook embeds - check for Facebook classes or facebook.com domain
    if 'facebook.com' in html or 'fb-post' in html or 'fb-root' in html or 'facebook-jssdk' in html:
        embeds['social_embed_facebook'] = True

    # Instagram embeds - check for Instagram classes or instagram.com domain
    if 'instagram.com' in html or 'instagram-media' in html or 'instgrm' in html:
        embeds['social_embed_instagram'] = True

    # YouTube embeds
    if 'youtube.com' in html or 'youtu.be' in html:
        youtube_pattern = r'youtube\.com/embed/([a-zA-Z0-9_-]+)'
        youtube_matches = re.findall(youtube_pattern, html)
        if youtube_matches:
            embeds['social_embed_youtube'] = True
            embeds['youtube_video_ids'] = youtube_matches

    # Vimeo embeds
    if 'vimeo.com' in html:
        vimeo_pattern = r'vimeo\.com/video/(\d+)'
        vimeo_matches = re.findall(vimeo_pattern, html)
        if vimeo_matches:
            embeds['social_embed_vimeo'] = True
            embeds['vimeo_video_ids'] = vimeo_matches

    # TikTok embeds
    if 'tiktok.com' in html or 'tiktok-embed' in html:
        embeds['social_embed_tiktok'] = True

    # LinkedIn embeds
    if 'linkedin.com' in html and ('embed' in html or 'li-embed' in html):
        embeds['social_embed_linkedin'] = True

    return embeds


def _extract_microdata(html: str) -> Dict[str, Any]:
    """Extract microdata from HTML."""
    microdata = {'microdata_present': False}

    # Look for itemscope attributes
    itemscope_pattern = r'<[^>]*itemscope[^>]*>'
    microdata_tags = re.findall(itemscope_pattern, html, re.IGNORECASE)

    if microdata_tags:
        microdata['microdata_present'] = True
        microdata['microdata_item_count'] = len(microdata_tags)

        # Extract itemtype attributes
        itemtype_pattern = r'itemtype=["\']([^"\']+)["\']'
        itemtypes = re.findall(itemtype_pattern, html, re.IGNORECASE)
        if itemtypes:
            microdata['microdata_types'] = list(set(itemtypes))

    return microdata


def _analyze_url_structure(filepath: str) -> Dict[str, Any]:
    """Analyze URL structure and social media patterns."""
    analysis = {}

    # Extract filename which might be a URL
    filename = Path(filepath).name

    # Check if filename looks like a URL
    if 'http' in filename or filename.count('.') >= 2:
        try:
            # Try to parse as URL
            parsed = urlparse(filename)
            if parsed.netloc:
                analysis['url_domain'] = parsed.netloc
                analysis['url_path'] = parsed.path
                analysis['url_query'] = parsed.query

                # Check if it's a social media domain
                domain_key = parsed.netloc.lower().replace('www.', '')
                if domain_key in SOCIAL_DOMAINS:
                    analysis['social_platform'] = SOCIAL_DOMAINS[domain_key]
                    analysis['is_social_media_url'] = True

                # Extract social media IDs from path
                if 'twitter.com' in parsed.netloc or 'x.com' in parsed.netloc:
                    path_parts = parsed.path.strip('/').split('/')
                    if len(path_parts) >= 2 and path_parts[0] in ['i', path_parts[0]]:
                        if path_parts[1] == 'status' and len(path_parts) >= 3:
                            analysis['twitter_status_id'] = path_parts[2]

                elif 'instagram.com' in parsed.netloc:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0] == 'p':
                        analysis['instagram_post_id'] = path_parts[1]

        except:
            pass

    return analysis


def get_web_social_field_count() -> int:
    """Return the number of fields extracted by web/social metadata."""
    registry_fields = get_web_standards_registry_fields()
    if registry_fields:
        return len(registry_fields)
    # Meta tags (variable, estimate 20 common ones)
    meta_fields = 20

    # Open Graph (30+ properties)
    og_fields = len(OPEN_GRAPH_PROPERTIES)

    # Twitter Cards (20+ properties)
    twitter_fields = len(TWITTER_CARD_PROPERTIES)

    # Schema.org (variable, estimate 15 common properties)
    schema_fields = 15

    # Web manifest (5 properties)
    manifest_fields = 5

    # Social embeds (10 properties)
    embed_fields = 10

    # Microdata (5 properties)
    microdata_fields = 5

    # URL analysis (10 properties)
    url_fields = 10

    return meta_fields + og_fields + twitter_fields + schema_fields + manifest_fields + embed_fields + microdata_fields + url_fields


# Integration point for metadata_engine.py
def extract_web_social_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for web/social metadata extraction."""
    return extract_web_social_metadata(filepath)

def extract_web_social_metadata_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract comprehensive web_social_metadata metadata from files.

    Args:
        filepath: Path to the file

    Returns:
        Dictionary containing extracted web_social_metadata metadata
    '''
    result = {
        "extracted_fields": {},
        "registry_fields": {},
        "fields_extracted": 0,
        "is_valid_web_social_metadata": False
    }

    try:
        # TODO: Implement specific extraction logic for web_social_metadata
        # This is a template that needs to be customized based on file format

        # Basic file validation
        if not filepath or not os.path.exists(filepath):
            result["error"] = "File path not provided or file doesn't exist"
            return result

        result["is_valid_web_social_metadata"] = True

        # Template structure - customize based on actual format requirements
        try:
            # Add format-specific extraction logic here
            # Examples:
            # - Read file headers
            # - Parse binary structures
            # - Extract metadata fields
            # - Map to registry definitions

            pass  # Replace with actual implementation

        except Exception as e:
            result["error"] = f"web_social_metadata extraction failed: {str(e)[:200]}"

        # Count extracted fields
        total_fields = len(result["extracted_fields"]) + len(result["registry_fields"])
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["error"] = f"web_social_metadata metadata extraction failed: {str(e)[:200]}"

    return result
