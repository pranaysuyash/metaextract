import pytest

from server.extractor.modules import pdf_metadata_complete as pmc


def test_pdf_forms_and_annotations(tmp_path):
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
    writer.add_blank_page(width=200, height=200)

    field = DictionaryObject()
    field.update({
        NameObject("/FT"): NameObject("/Tx"),
        NameObject("/T"): TextStringObject("field1"),
        NameObject("/V"): TextStringObject("value"),
        NameObject("/Ff"): NumberObject(0),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/Rect"): ArrayObject([NumberObject(0), NumberObject(0), NumberObject(10), NumberObject(10)]),
    })
    field_ref = writer.add_annotation(0, field)
    acroform = DictionaryObject()
    acroform.update({NameObject("/Fields"): ArrayObject([field_ref])})
    writer._root_object.update({NameObject("/AcroForm"): acroform})

    annot = DictionaryObject()
    annot.update({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Text"),
        NameObject("/Rect"): ArrayObject([NumberObject(20), NumberObject(20), NumberObject(40), NumberObject(40)]),
        NameObject("/Contents"): TextStringObject("Note"),
    })
    writer.add_annotation(0, annot)

    path = tmp_path / "forms.pdf"
    with open(path, "wb") as f:
        writer.write(f)

    result = pmc.extract_pdf_metadata_complete(str(path))
    assert result.get("pdf_form_field_count_pypdf", 0) == 1
    assert result.get("pdf_total_annotations_pypdf", 0) >= 1
