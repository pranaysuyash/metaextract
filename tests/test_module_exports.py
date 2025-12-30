import importlib

def test_module_exports():
    m = importlib.import_module("server.extractor.modules")
    expected = [
        "parse_vendor_makernote",
        "detect_vendor_from_tags",
        "get_video_codec_field_count",
        "get_perceptual_comparison_field_count",
    ]

    for name in expected:
        assert hasattr(m, name), f"Export missing: {name}"

    # ensure __all__ includes these names
    module_all = getattr(m, "__all__", None)
    assert module_all is not None, "__all__ is not defined in server.extractor.modules"
    for name in expected:
        assert name in module_all, f"{name} not present in __all__"