# tests/test_phase3_web_social.py

import pytest
import os
import tempfile
from server.extractor.modules import web_social_metadata as wsm


def test_web_social_module_imports():
    """Test that the web_social_metadata module can be imported and has expected functions."""
    assert hasattr(wsm, 'extract_web_social_metadata')
    assert hasattr(wsm, 'extract_web_social_complete')
    assert hasattr(wsm, 'get_web_social_field_count')


def test_web_social_field_count():
    """Test that get_web_social_field_count returns a reasonable number."""
    count = wsm.get_web_social_field_count()
    assert isinstance(count, int)
    assert count > 50  # Should have at least 50+ fields


def test_extract_web_social_with_invalid_file():
    """Test extraction with non-existent file."""
    result = wsm.extract_web_social_complete('/nonexistent/file.html')
    assert isinstance(result, dict)
    assert 'web_social_extraction_error' in result


def test_extract_web_social_with_empty_html():
    """Test extraction with minimal HTML."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = wsm.extract_web_social_complete(temp_path)
        assert isinstance(result, dict)
        assert 'web_social_extraction_error' not in result
    finally:
        os.unlink(temp_path)


def test_extract_open_graph():
    """Test Open Graph metadata extraction."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta property="og:title" content="Open Graph Title" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://example.com" />
    <meta property="og:image" content="https://example.com/image.jpg" />
    <meta property="og:description" content="Open Graph Description" />
    <meta property="og:site_name" content="Example Site" />
</head>
<body></body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = wsm.extract_web_social_complete(temp_path)
        assert result['opengraph_present'] is True
        assert result['opengraph_title'] == 'Open Graph Title'
        assert result['opengraph_type'] == 'website'
        assert result['opengraph_url'] == 'https://example.com'
        assert result['opengraph_image'] == 'https://example.com/image.jpg'
        assert result['opengraph_description'] == 'Open Graph Description'
        assert result['opengraph_site_name'] == 'Example Site'
    finally:
        os.unlink(temp_path)


def test_extract_twitter_cards():
    """Test Twitter Card metadata extraction."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="@example" />
    <meta name="twitter:title" content="Twitter Card Title" />
    <meta name="twitter:description" content="Twitter Card Description" />
    <meta name="twitter:image" content="https://example.com/twitter-image.jpg" />
</head>
<body></body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = wsm.extract_web_social_complete(temp_path)
        assert result['twitter_cards_present'] is True
        assert result['twitter_card_type'] == 'summary_large_image'
        assert result['twitter_site'] == '@example'
        assert result['twitter_title'] == 'Twitter Card Title'
        assert result['twitter_description'] == 'Twitter Card Description'
        assert result['twitter_image'] == 'https://example.com/twitter-image.jpg'
    finally:
        os.unlink(temp_path)


def test_extract_schema_org_json_ld():
    """Test Schema.org JSON-LD extraction."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "name": "Schema.org Article",
        "description": "Schema.org Description",
        "url": "https://example.com/article",
        "image": "https://example.com/schema-image.jpg",
        "datePublished": "2023-01-01",
        "author": {
            "@type": "Person",
            "name": "John Doe"
        }
    }
    </script>
</head>
<body></body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = wsm.extract_web_social_complete(temp_path)
        assert result['schema_org_present'] is True
        assert result['schema_org_json_ld_count'] == 1
        assert 'schema_type_article' in result
        assert result['schema_name'] == 'Schema.org Article'
        assert result['schema_description'] == 'Schema.org Description'
        assert result['schema_url'] == 'https://example.com/article'
        assert result['schema_image'] == 'https://example.com/schema-image.jpg'
        assert result['schema_datePublished'] == '2023-01-01'
    finally:
        os.unlink(temp_path)


def test_extract_web_manifest():
    """Test Web App Manifest extraction."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <link rel="manifest" href="/manifest.json" />
    <meta name="theme-color" content="#ffffff" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
</head>
<body></body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = wsm.extract_web_social_complete(temp_path)
        assert result['web_manifest_present'] is True
        assert result['web_manifest_url'] == '/manifest.json'
        assert result['web_theme_color'] == '#ffffff'
        assert result['web_apple_touch_icon'] == '/apple-touch-icon.png'
    finally:
        os.unlink(temp_path)


def test_extract_social_embeds():
    """Test social media embed detection."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <blockquote class="twitter-tweet">
        <p>Tweet content</p>
    </blockquote>
    <div class="fb-post" data-href="https://www.facebook.com/example"></div>
    <blockquote class="instagram-media" data-instgrm-permalink="https://www.instagram.com/p/example/"></blockquote>
    <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>
    <iframe src="https://player.vimeo.com/video/123456789"></iframe>
</body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = wsm.extract_web_social_complete(temp_path)
        assert result['social_embed_twitter'] is True
        assert result['social_embed_facebook'] is True
        assert result['social_embed_instagram'] is True
        assert result['social_embed_youtube'] is True
        assert result['social_embed_vimeo'] is True
        assert 'dQw4w9WgXcQ' in result['youtube_video_ids']
        assert '123456789' in result['vimeo_video_ids']
    finally:
        os.unlink(temp_path)


def test_extract_microdata():
    """Test microdata extraction."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <div itemscope itemtype="https://schema.org/Person">
        <span itemprop="name">John Doe</span>
    </div>
    <div itemscope itemtype="https://schema.org/Organization">
        <span itemprop="name">Example Corp</span>
    </div>
</body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = wsm.extract_web_social_complete(temp_path)
        assert result['microdata_present'] is True
        assert result['microdata_item_count'] == 2
        assert 'https://schema.org/Person' in result['microdata_types']
        assert 'https://schema.org/Organization' in result['microdata_types']
    finally:
        os.unlink(temp_path)