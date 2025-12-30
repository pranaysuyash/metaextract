import pytest

from server.extractor.modules import pdf_metadata_complete as pmc


def test_pdf_metadata_complete_with_pypdf(tmp_path):
    if not pmc.PYPDF_AVAILABLE:
        pytest.skip("pypdf not available")

    from pypdf import PdfWriter
    from pypdf.generic import (
        ArrayObject,
        DictionaryObject,
        NameObject,
        NumberObject,
        TextStringObject,
    )

    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    writer.add_metadata({"/Title": "Demo", "/Author": "Codex"})
    writer.add_outline_item("Chapter 1", 0)

    annot = DictionaryObject()
    annot.update({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Text"),
        NameObject("/Rect"): ArrayObject([NumberObject(0), NumberObject(0), NumberObject(10), NumberObject(10)]),
        NameObject("/Contents"): TextStringObject("Note"),
    })
    page[NameObject("/Annots")] = ArrayObject([annot])

    path = tmp_path / "sample.pdf"
    with open(path, "wb") as f:
        writer.write(f)

    result = pmc.extract_pdf_metadata_complete(str(path))
    assert result.get("pdf_outline_count_pypdf", 0) >= 1
    assert result.get("pdf_total_annotations_pypdf", 0) == 1
