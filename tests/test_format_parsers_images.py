from __future__ import annotations

from server.extractor.formats.gif_structure import extract_gif_container_metadata
from server.extractor.formats.png_chunks import extract_png_container_metadata
from server.extractor.formats.webp_riff import extract_webp_container_metadata
from server.extractor.metadata_engine import extract_metadata


def test_png_chunk_parser_extracts_ihdr() -> None:
    meta = extract_png_container_metadata("test-data/test_png.png")
    assert meta is not None
    assert meta["format"] == "PNG"
    assert meta["ihdr"] is not None
    assert meta["ihdr"]["width"] == 100
    assert meta["ihdr"]["height"] == 100
    assert meta["chunks_total"] > 0
    assert "IHDR" in meta["chunk_counts"]


def test_gif_parser_extracts_logical_screen_and_frames() -> None:
    meta = extract_gif_container_metadata("test-data/test_sample.gif")
    assert meta is not None
    assert meta["format"] == "GIF"
    assert meta["logical_screen"]["width"] == 200
    assert meta["logical_screen"]["height"] == 200
    assert meta["frames"] >= 1


def test_webp_parser_detects_riff_container() -> None:
    meta = extract_webp_container_metadata("test-data/test_webp.webp")
    assert meta is not None
    assert meta["format"] == "WEBP"
    assert isinstance(meta["chunk_counts"], dict)


def test_engine_includes_container_metadata_for_free_tier_images() -> None:
    out = extract_metadata("test-data/test_png.png", tier="free")
    cm = out.get("container_metadata")
    assert isinstance(cm, dict)
    assert "png" in cm
