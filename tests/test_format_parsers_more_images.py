from __future__ import annotations

from server.extractor.formats.bmp_headers import extract_bmp_container_metadata
from server.extractor.formats.dds_header import extract_dds_container_metadata
from server.extractor.formats.exr_header import extract_exr_container_metadata
from server.extractor.formats.fits_header import extract_fits_container_metadata
from server.extractor.formats.icns_structure import extract_icns_container_metadata
from server.extractor.formats.ico_headers import extract_ico_container_metadata
from server.extractor.formats.isobmff_boxes import extract_isobmff_box_metadata
from server.extractor.formats.jpeg_markers import extract_jpeg_container_metadata
from server.extractor.formats.jp2_boxes import extract_jp2_container_metadata
from server.extractor.formats.jxl_signatures import extract_jxl_container_metadata
from server.extractor.formats.pnm_header import extract_pnm_container_metadata
from server.extractor.formats.psd_structure import extract_psd_container_metadata
from server.extractor.formats.radiance_hdr import extract_radiance_hdr_container_metadata
from server.extractor.formats.svg_xml import extract_svg_container_metadata
from server.extractor.formats.tga_header import extract_tga_container_metadata
from server.extractor.formats.tiff_ifd import extract_tiff_container_metadata
from server.extractor.metadata_engine import extract_metadata


def test_jpeg_marker_parser_finds_sof_dimensions() -> None:
    meta = extract_jpeg_container_metadata("test-data/test_jpg.jpg")
    assert meta is not None
    assert meta["format"] == "JPEG"
    assert meta["sof"] is not None
    assert meta["sof"]["width"] > 0
    assert meta["sof"]["height"] > 0


def test_bmp_header_parser_reads_dimensions() -> None:
    meta = extract_bmp_container_metadata("test-data/test_bmp.bmp")
    assert meta is not None
    assert meta["format"] == "BMP"
    assert meta["width"] == 64
    assert abs(meta["height"]) == 64


def test_tiff_parser_counts_ifds() -> None:
    meta = extract_tiff_container_metadata("test-data/test_tiff.tiff")
    assert meta is not None
    assert meta["format"] == "TIFF"
    assert meta["ifd_count"] >= 1


def test_psd_parser_reads_header() -> None:
    meta = extract_psd_container_metadata("test-data/test_minimal.psd")
    assert meta is not None
    assert meta["width"] == 1
    assert meta["height"] == 1
    assert meta["channels"] == 3


def test_isobmff_parser_reads_ftyp() -> None:
    meta = extract_isobmff_box_metadata("test-data/test_minimal.heic")
    assert meta is not None
    assert meta["container"] == "isobmff"
    assert meta["ftyp"] is not None
    assert meta["ftyp"]["major_brand"] == "heic"


def test_exr_parser_reads_header() -> None:
    meta = extract_exr_container_metadata("test-data/test_minimal.exr")
    assert meta is not None
    assert meta["format"] == "EXR"

def test_fits_parser_reads_basic_header_cards() -> None:
    meta = extract_fits_container_metadata("test-data/test_fits.fits")
    assert meta is not None
    assert meta["format"] == "FITS"
    assert meta["naxis"] is not None
    assert meta["dimensions"] == [3, 2]


def test_ico_parser_reads_directory_entries() -> None:
    meta = extract_ico_container_metadata("test-data/test_ico.ico")
    assert meta is not None
    assert meta["format"] == "ICO"
    assert meta["count"] == 1
    assert meta["images"][0]["width"] == 16
    assert meta["images"][0]["height"] == 16


def test_icns_parser_reads_element_table() -> None:
    meta = extract_icns_container_metadata("test-data/test_icns.icns")
    assert meta is not None
    assert meta["format"] == "ICNS"
    assert meta["elements"].get("icp4") == 1


def test_jp2_parser_reads_signature_and_ftyp() -> None:
    meta = extract_jp2_container_metadata("test-data/test_jp2.jp2")
    assert meta is not None
    assert meta["format"] in ("JP2", "JPEG2000")
    assert meta.get("ftyp") is not None
    assert meta["ftyp"]["major_brand"] == "jp2 "


def test_jxl_detector_identifies_codestream() -> None:
    meta = extract_jxl_container_metadata("test-data/test_jxl_codestream.jxl")
    assert meta is not None
    assert meta["format"] == "JXL"
    assert meta["container"] == "codestream"


def test_dds_parser_reads_dimensions_and_fourcc() -> None:
    meta = extract_dds_container_metadata("test-data/test_dds.dds")
    assert meta is not None
    assert meta["format"] == "DDS"
    assert meta["width"] == 8
    assert meta["height"] == 4
    assert meta["fourcc"] == "DXT1"


def test_tga_parser_reads_header_dimensions() -> None:
    meta = extract_tga_container_metadata("test-data/test_tga.tga")
    assert meta is not None
    assert meta["format"] == "TGA"
    assert meta["width"] == 2
    assert meta["height"] == 3


def test_pnm_parser_reads_magic_and_dimensions() -> None:
    meta = extract_pnm_container_metadata("test-data/test_ppm.ppm")
    assert meta is not None
    assert meta["format"] == "PNM"
    assert meta["magic"] == "P6"
    assert meta["width"] == 2
    assert meta["height"] == 3
    assert meta["maxval"] == 255


def test_radiance_hdr_parser_reads_resolution_line() -> None:
    meta = extract_radiance_hdr_container_metadata("test-data/test_radiance.hdr")
    assert meta is not None
    assert meta["format"] == "HDR"
    assert meta["resolution"] == "-Y 2 +X 3"


def test_svg_parser_extracts_dimensions_and_security_signals() -> None:
    meta = extract_svg_container_metadata("test-data/test_svg.svg")
    assert meta is not None
    assert meta["format"] == "SVG"
    assert meta["width"] == "10"
    assert meta["height"] == "20"
    assert meta["security"]["external_link_count"] == 1
    assert meta["embedded_images"] == 1


def test_engine_container_metadata_for_added_formats() -> None:
    out = extract_metadata("test-data/test_bmp.bmp", tier="free")
    assert "container_metadata" in out
    assert "bmp" in out["container_metadata"]

    out2 = extract_metadata("test-data/test_ico.ico", tier="free")
    assert "container_metadata" in out2
    assert "ico" in out2["container_metadata"]

    out3 = extract_metadata("test-data/test_svg.svg", tier="free")
    assert "container_metadata" in out3
    assert "svg" in out3["container_metadata"]

    out4 = extract_metadata("test-data/test_dng.dng", tier="free")
    assert "container_metadata" in out4
    assert "tiff" in out4["container_metadata"]
    assert out4["container_metadata"].get("raw", {}).get("container_family") == "TIFF"

    out5 = extract_metadata("test-data/test_cr3.cr3", tier="free")
    assert "container_metadata" in out5
    assert "isobmff" in out5["container_metadata"]
    assert out5["container_metadata"].get("raw", {}).get("container_family") == "ISOBMFF"

    out6 = extract_metadata("test-data/test_fits.fits", tier="free")
    assert "container_metadata" in out6
    assert "fits" in out6["container_metadata"]
