from server.extractor.modules.web_social_metadata import extract_web_social_metadata_metadata


def test_extract_web_social_metadata_metadata_basic(tmp_path):
    html = """
    <html>
      <head>
        <meta property="og:title" content="Hello World" />
        <meta name="twitter:card" content="summary" />
        <script type="application/ld+json">{"@type":"Article","name":"Test Article"}</script>
        <link rel="manifest" href="manifest.json" />
      </head>
      <body>
        <div itemscope itemtype="http://schema.org/Thing"></div>
      </body>
    </html>
    """
    path = tmp_path / "sample.html"
    path.write_text(html, encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"name":"Test App","short_name":"App","start_url":"/"}', encoding="utf-8")

    result = extract_web_social_metadata_metadata(str(path))

    assert result["is_valid_web_social_metadata"] is True
    extracted = result["extracted_fields"]
    assert extracted.get("opengraph_present") is True
    assert extracted.get("opengraph_title") == "Hello World"
    assert extracted.get("twitter_cards_present") is True
    assert extracted.get("schema_org_present") is True
    assert extracted.get("web_manifest_present") is True
    assert extracted.get("manifest.name") == "Test App"
    assert result["fields_extracted"] == len(extracted) + len(result["registry_fields"])
