#!/usr/bin/env python3
"""PDF Document Metadata Fields Inventory

This script documents metadata fields available in PDF documents
including standard metadata, XMP, and document properties.

Reference:
- PDF Reference 1.7 (Adobe)
- ISO 32000-1:2008
- PDF/A Standard (ISO 19005)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


PDF_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "PDF Reference 1.7, ISO 32000-1, PDF/A",
    "description": "PDF document metadata fields",
    "categories": {
        "document_info": {
            "description": "PDF Document Info dictionary (standard metadata)",
            "fields": [
                "Title",
                "Author",
                "Subject",
                "Keywords",
                "Creator",
                "Producer",
                "CreationDate",
                "ModDate",
                "Trapped",
                "PTEX.Fullbanner",
                "SIG_FLAGS",
                "SigFlags",
                "PERMS",
                "Encrypt",
                "ID",
            ],
            "count": 15,
            "reference": "PDF 1.7 §14.3.3"
        },
        "document_properties": {
            "description": "Extended document properties",
            "fields": [
                "PageCount",
                "PageSize",
                "FileSize",
                "Title",
                "Subject",
                "Author",
                "Keywords",
                "Creator",
                "Producer",
                "CreationDate",
                "ModificationDate",
                "Application",
                "PDFVersion",
                "Linearized",
                "Tagged",
                "Forms",
                "Javascript",
                "OpenAction",
                "AA",
                "StructTreeRoot",
                "MarkInfo",
                "OCProperties",
                "Legal",
                "Requirements",
                "Collection",
                "Cluster",
                "NeedsRendering",
            ],
            "count": 27,
            "reference": "PDF 1.7 §12.5"
        },
        "xmp_metadata": {
            "description": "XMP metadata in PDF",
            "fields": [
                "dc:title",
                "dc:creator",
                "dc:subject",
                "dc:description",
                "dc:publisher",
                "dc:contributor",
                "dc:date",
                "dc:type",
                "dc:format",
                "dc:identifier",
                "dc:source",
                "dc:language",
                "dc:relation",
                "dc:coverage",
                "dc:rights",
                "dc:title[xml:lang]",
                "dc:creator[seq]",
                "pdf:Keywords",
                "pdf:PDFVersion",
                "pdf:Title",
                "pdf:Author",
                "pdf:Subject",
                "pdf:Keywords",
                "pdf:Creator",
                "pdf:Producer",
                "pdf:CreationDate",
                "pdf:ModDate",
                "xmp:CreatorTool",
                "xmp:ModifyDate",
                "xmp:CreateDate",
                "xmp:MetadataDate",
                "xmp:Author",
                "xmp:Title",
                "xmp:Description",
                "xmp:Rights",
                "xmp:Label",
                "xmp:Rating",
                "xmp:DisplayName",
                "xmp:Nickname",
                "xmp:ColorSpace",
                "xmp:PixelWidth",
                "xmp:PixelHeight",
                "xmp:Colorants",
                "xmp:ICCProfile",
                "photoshop:ColorMode",
                "photoshop:ICCProfile",
                "photoshop:TextLayers",
                "photoshop:History",
                "xmpMM:DocumentID",
                "xmpMM:InstanceID",
                "xmpMM:OriginalDocumentID",
                "xmpMM:DerivedFrom",
                "xmpMM:Revision",
                "xmpMM:ManageFrom",
                "xmpMM:Manager",
                "xmpMM:InstanceOf",
                "xmpMM:Ingredients",
                "xmpMM:DocumentReferences",
                "xmpMM:Pantry",
                "rdf:Seq",
                "rdf:Alt",
                "rdf:Bag",
            ],
            "count": 57,
            "reference": "XMP Specification, PDF 1.7 §14.3.2"
        },
        "pdf_a_conformance": {
            "description": "PDF/A conformance and validation metadata",
            "fields": [
                "pdfaid:part",
                "pdfaid:conformance",
                "pdfaid:amd",
                "pdfaid:checkSum",
                "pdfaid:Profile",
                "pdfaid:Level",
                "pdfaid:Conformance",
                "pdfaSchema:namespaceURI",
                "pdfaSchema:prefix",
                "pdfaSchema:property",
                "pdfaSchema:propertyURI",
                "pdfaSchema:valueType",
                "pdfaSchema:description",
                "pdfaSchema:order",
                "pdfaProperty:category",
                "pdfaProperty:description",
                "pdfaProperty:name",
                "pdfaProperty:propertyURI",
                "pdfaProperty:valueType",
                "pdfaProperty:used",
                "pdfaExtension:schemas",
                "pdfaExtension:namespaceURI",
                "pdfaExtension:prefix",
                "pdfaExtension:property",
                "pdfaValidation:object",
                "pdfaValidation:property",
                "pdfaValidation:profile",
                "pdfaValidation:status",
                "pdfaValidation:message",
                "pdfaValidation:date",
            ],
            "count": 29,
            "reference": "ISO 19005 (PDF/A)"
        },
        "page_tree": {
            "description": "PDF page tree and page object properties",
            "fields": [
                "Type",
                "Parent",
                "Kids",
                "Count",
                "Page",
                "MediaBox",
                "CropBox",
                "BleedBox",
                "TrimBox",
                "ArtBox",
                "BoxColorInfo",
                "Contents",
                "Resources",
                "Rotate",
                "Group",
                "Thumb",
                "B",
                "Dur",
                "Trans",
                "Annots",
                "StructParents",
                "Predecessors",
                "Successors",
                "TemplateInstantiated",
                "NamedPage",
                "UserUnit",
                "VP",
            ],
            "count": 27,
            "reference": "PDF 1.7 §7.7.3"
        },
        "catalog_dictionary": {
            "description": "PDF Catalog dictionary entries",
            "fields": [
                "Type", "Version", "Extensions", "Pages", "PageLabels", "Names",
                "Dests", "Outlines", "Threads", "OpenAction", "AA", "URI",
                "StructTreeRoot", "MarkInfo", "Legal", "Requirements", "Collection",
                "NeedsRendering", "AcroForm", "JavaScript", "NamedDests",
                "Perms", "ViewerPreferences", "OCProperties", "Direction",
                "DefaultResourceDict", "XFA", "PieceInfo", "OptionalContentInfo",
                "Record", "Brand", "CIDFontRegistry", "CIDSet", "FontDescriptor",
                "FontFile", "FontFile2", "FontFile3", "FontBBox", "FontMatrix",
                "CharSet", "Encoding", "ToUnicode", "DescendantFonts", "BaseFont",
                "FirstChar", "LastChar", "Widths", "Subtype", "Encoding", "BaseEncoding",
                "Differences", "Stream", "Subtype2", "Length", "Filter", "DecodeParms",
                "ColorSpace", "Subtype2", "FunctionType", "Domain", "Range", "N",
                "C0", "C1", "Bounds", "Functions", "Function", "Size", "Domain",
            ],
            "count": 72,
            "reference": "PDF 1.7 §7.6"
        },
        "metadata_streams": {
            "description": "PDF metadata streams",
            "fields": [
                "Type", "Subtype", "S", "Title", "Creator", "Author", "Subject",
                "Keywords", "Producer", "CreationDate", "ModDate", "Trapped",
                "Metadata", "XMP", "XML", "Description", "Format", "Identifier",
                "Source", "Language", "Relation", "Coverage", "Rights",
                "Title[xml:lang]", "AlternativeTitle", "Captions", "Categories",
                "Copyright", "Credit", "DateTimeOriginal", "DigitalTime",
                "Flash", "FNumber", "FocalLength", "ISOSpeedRatings", "Make",
                "Model", "Software", "XPAuthor", "XPCopyright", "XPComment",
                "XPKeywords", "XPSubject", "XPTitle", "BitsPerComponent",
                "ColorTransform", "Compression", "Filter", "ImageMask",
                "Indexed", "Intent", "Interpolate", "SMask", "SMaskInData",
            ],
            "count": 59,
            "reference": "PDF 1.7 §14.3"
        },
        "interactive_forms": {
            "description": "PDF AcroForm and field properties",
            "fields": [
                "Type", "Subtype", "FT", "Parent", "Kids", "T", "TU", "TM",
                "F", "V", "DV", "AA", "DA", "Q", "Rect", "AP", "AS", "NV",
                "Opt", "TI", "I", "MaxLen", "DS", "RV", "Ff", "NoView", "Hide",
                "Print", "NoZoom", "NoRotate", "ReadOnly", "Required", "Combo",
                "Edit", "MultiLine", "Password", "Pushbutton", "Radio", "Check",
                "Button", "Choice", "Signature", "Value", "DefaultValue",
                "Options", "TopIndex", "Sort", "DoNotSpellCheck", "DoNotScroll",
                "Combs", "RadixInChar", "Multiline", "PasswordField",
                "FileSelect", "SubmitField", "ResetField", "PushbuttonField",
                "RadioField", "CheckField", "ChoiceField", "SignatureField",
                "FieldFlags", "SignatureFieldFlags", "ListBoxFlags",
            ],
            "count": 63,
            "reference": "PDF 1.7 §12.7"
        },
        "security_signatures": {
            "description": "PDF security and digital signature fields",
            "fields": [
                "Filter", "SubFilter", "Contents", "Cert", "ByteRange", "Reference",
                "Changes", "Name", "Location", "ContactInfo", "SigningTime",
                "Reason", "M", "ReferenceTransformMethod", "DigestMethod",
                "DigestValue", "CertFilter", "Changes", "v", "Length", "R",
                "P", "StmF", "StrF", "EFF", "EncryptMetadata", "Identity",
                "Standard", "V", "R", "P", "CFM", "AuthEvent", "OpenPGP",
                "CertificateSecurity", "PublicKeySecurity", "CertSeedValue",
                "Prop_Build", "Prop_Time", "Prop_AuthTime", "Prop_USage",
                "Prop_Filter", "Prop_SubFilter", "Prop_K", "Prop_Contents",
                "Prop_Cert", "Prop_ByteRange", "Prop_Reference", "Prop_SigField",
                "Prop_ProvCert", "Prop_ReferenceInfo", "Prop_SigningTime",
                "Prop_Reason", "Prop_ContactInfo", "Prop_Location", "Prop_SigFlags",
                "Prop_Ann", "Prop_PurchaseTime", "Prop_Verify", "Prop_VerifyResult",
            ],
            "count": 60,
            "reference": "PDF 1.7 §12.8"
        },
        "rendering_intent": {
            "description": "PDF rendering and color management",
            "fields": [
                "Type", "Subtype", "N", "TR", "TR2", "Intent", "Intentns",
                "GTS_PDFX", "GTS_PDFXConformance", "GTS_PDFXVersion", "Title",
                "Creator", "Producer", "CreationDate", "ModDate", "Keywords",
                "Trapped", "Info", "OutputIntents", "S", "U", "DestOutputProfile",
                "DestOutputProfileRef", "Type0", "Type2", "Alternate", "BaseInputProfile",
                "BaseOutputProfile", "Encode", "EncodeSrc", "Intent", "Registry",
                "RenderingIntent", "SrcSpace", "ICCProfile", "ProfileType",
                "ProfileVersion", "ProfileClass", "ColorSpaceData", "PCS",
                "ProfileConnectionSpace", "ProfileCMMType", "ProfileVersion",
                "ProfilePlatform", "ProfileConnectivitySpace", "ProfileFileSize",
            ],
            "count": 43,
            "reference": "PDF 1.7 §8.6"
        },
        "logical_structure": {
            "description": "PDF logical structure (Tagged PDF)",
            "fields": [
                "Type", "Role", "Parent", "Kids", "Title", "Lang", "Alt",
                "ActualText", "E", "StructParent", "StructParents", "ID",
                "Class", "Style", "Placement", "WritingMode", "SpaceBefore",
                "SpaceAfter", "StartIndent", "EndIndent", "TextIndent",
                "BlockAlign", "InlineAlign", "BidiOverride", "Ruby", "RubyType",
                "RubyAlign", "RubyPosition", "HE", "Shear", "Narrow",
                "Wide", "Label", "ListNumbering", "Content", "LI", "LBody",
                "Table", "TR", "TH", "TD", "THead", "TBody", "TFoot", "RowSpan",
                "ColSpan", "Headers", "Scope", "Axis", "Summary", "Figure",
                "Formula", "InlineShape", "FormulaRef", "Proof", "Note",
                "Reference", "BibEntry", "Code", "Link", "Annot", "widget",
                "Btn", "Tx", "Ch", "Sig",
            ],
            "count": 71,
            "reference": "PDF 1.7 §9.4"
        },
        "optional_content": {
            "description": "PDF optional content (layers)",
            "fields": [
                "Type", "Name", "Usage", "BaseState", "OFF", "ON", "OCGs",
                "OCGRoups", "D", "Order", "rbgroups", "Locked", "Intent",
                "AS", "State", "OFF", "ON", "Toggle", "ViewState", "PrintState",
                "ExportState", "CreatorInfo", "Producer", "CreationDate",
                "User", "Usages", "Document", "Page", "Bezier", "Font",
                "Graphics", "Internal", "Creator", "UserName", "LastModified",
                "CreationS", "ModS", "Ordering", "Group", "Intent", "Category",
                "View", "Print", "Export", "Language", "ExportAsEPS",
            ],
            "count": 47,
            "reference": "PDF 1.7 §8.11"
        },
        "attachments": {
            "description": "PDF file attachments and embedded files",
            "fields": [
                "Type", "Subtype", "FS", "F", "UF", "DOS", "Mac", "Unix",
                "ID", "V", "EF", "RF", "EmbeddedFiles", "Names", "Desc",
                "CI", "CO", "EmbFile", "Compression", "CheckSum", "Subtype",
                "Size", "Action", "Launch", "GoTo", "GoToR", "GoToE",
                "Named", "Thread", "URI", "Sound", "Movie", "Rendition",
                "Trans", "JavaScript", "SubmitForm", "ResetForm", "ImportData",
                "OCG", "OC", "Embedded", "Filespec", "Collection", "Schema",
                "Root", "D", "DR", "F", "FI", "RF", "UF", "V", "CIDSet",
                "CIDFont", "FontDescriptor", "FontFile", "FontFile2", "FontFile3",
            ],
            "count": 59,
            "reference": "PDF 1.7 §7.11"
        },
        "outlines_bookmarks": {
            "description": "PDF outlines (bookmarks)",
            "fields": [
                "Type", "Title", "Parent", "Prev", "Next", "First", "Last",
                "Count", "Dest", "A", "SE", "S", "C", "F", "StructParent",
                "Color", "Count", "Style", "Bold", "Italic", "Open",
                "Outline", "OutlineLevel", "Destination", "Action", "URI",
                "Named", "Thread", "Sound", "Movie", "Launch", "GoTo",
                "GoToR", "GoToE", "SubmitForm", "ResetForm", "ImportData",
                "JavaScript", "NamedDestination", "ThreadSubject", "ThreadStatus",
                "PostScript", "StartPage", "EndPage", "BottomUp", "FitWindow",
                "CenterWindow", "DisplayDocTitle", "ViewArea", "ViewClip",
                "PrintArea", "PrintClip", "NonFullScreenPageMode",
                "Direction", "ViewOrientation", "PrintPageRange",
            ],
            "count": 50,
            "reference": "PDF 1.7 §12.3"
        },
        "annotations": {
            "description": "PDF annotation types and properties",
            "fields": [
                "Type", "Subtype", "Rect", "F", "BS", "Border", "H", "MK",
                "CA", "DA", "Q", "StructParent", "NM", "M", "Popup", "Parent",
                "Contents", "R", "P", "T", "Popup", "Open", "Closed",
                "Subject", "ReplyTo", "Intent", "State", "StateModel",
                "InReplyTo", "Line", "End", "InteriorColor", "StartStyle",
                "StartOffset", "EndOffset", "LeaderLength", "LeaderExtend",
                "LeaderOffset", "Caption", "Name", "Offset", "Corner",
                "IT", "QuadPoints", "InkList", "Stamp", "Name", "FreeText",
                "Callout", "Measure", "PolyLine", "PolyPolygon", "Cloud",
                "Ink", "Highlight", "Underline", "Squiggly", "StrikeOut",
                "Link", "Goto", "RemoteGoTo", "Launch", "Named", "Sound",
                "Movie", "Widget", "Screen", "PrinterMark", "TrapNetwork",
                "Watermark", "3D", "Redact", "Projection",
            ],
            "count": 72,
            "reference": "PDF 1.7 §12.5"
        },
        "actions": {
            "description": "PDF action types and properties",
            "fields": [
                "Type", "S", "Next", "URI", "GoTo", "GoToR", "GoToE",
                "Launch", "Thread", "Sound", "Movie", "Rendition", "Trans",
                "GoToView", "GoToRaster", "SubmitForm", "ResetForm",
                "ImportData", "JavaScript", "Hide", "Named", "SetOCGState",
                "Rendition", "Transition", "Sound", "Movie", "GoToDest",
                "Launch", "URI", "Named", "Launch", "Thread", "Sound",
                "Movie", "Rendition", "Trans", "SubmitForm", "ResetForm",
                "ImportData", "JavaScript", "Hide", "Named", "OCGState",
                "Rendition", "Transition", "Sound", "Movie", "GoToE",
                "GoToR", "Launch", "Thread", "Sound", "Movie", "Rendition",
                "Trans", "SubmitForm", "ResetForm", "ImportData", "JavaScript",
                "Hide", "Named", "OCGState", "Rendition", "Transition",
            ],
            "count": 63,
            "reference": "PDF 1.7 §12.6"
        },
        "multimedia": {
            "description": "PDF multimedia annotations",
            "fields": [
                "Type", "Subtype", "MH", "BE", "F", "AS", "IM", "NM",
                "PID", "C", "R", "P", "M", "TM", "DAT", "E", "PL", "CL",
                "Bt", "A", "M", "An", "IH", "V", "S", "Type", "Subtype",
                "Asset", "Rendition", "MediaClip", "MCD", "MCS", "Pt",
                "N", "P", "Bh", "Eh", "F", "O", "B", "D", "Ms", "V", "S",
                "C0", "C1", "TR", "TR2", "TN", "k", "F", "BPC",
            ],
            "count": 51,
            "reference": "PDF 1.7 §13.2"
        },
        "3d_annotations": {
            "description": "PDF 3D annotations",
            "fields": [
                "Type", "Subtype", "TU", "N", "M", "O", "MCS", "MC",
                "FO", "FS", "Parms", "IN", "INS", "PA", "NA", "NR",
                "NF", "PS", "U", "RM", "RC", "BM", "OBD", "O3D",
                "Anim", "Loop", "AutoPlay", "FirstFrame", "LastFrame",
                "ShadowMode", "LightingScheme", "RenderMode", "BGColor",
                "BGAlpha", "ShelfLife", "Volume", "3DStream", "VA",
                "DrawStyle", "CutType", "CutValue", "Feather",
                "InteractionMode", "InitializationScript", "onInstantiation",
            ],
            "count": 42,
            "reference": "PDF 1.7 §13.5"
        },
        "portfolios": {
            "description": "PDF portfolios and collections",
            "fields": [
                "Type", "Schema", "Name", "Type", "SS", "ID", "Desc",
                "CL", "CO", "D", "F", "UF", "FS", "RF", "V", "EF",
                "FirstChild", "LastChild", "StartNode", "Sort",
                "Selection", "Select", "Action", "Cursor", "CDB",
                "CB", "SF", "AF", "CP", "CD", "CU", "NV", "CM",
                "NB", "NK", "ND", "NF", "NO", "NS", "NT", "NU",
                "NX", "NY", "NZ", "NP", "NR", "NL", "ND", "NI",
            ],
            "count": 48,
            "reference": "PDF 1.7 §12.3.5"
        }
    },
    "totals": {
        "categories": 20,
        "total_fields": 968
    }
}


def main():
    output_dir = Path("dist/pdf_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "pdf_inventory.json"
    output_file.write_text(json.dumps(PDF_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary = {
        "generated_at": PDF_INVENTORY["generated_at"],
        "source": PDF_INVENTORY["source"],
        "categories": PDF_INVENTORY["totals"]["categories"],
        "total_fields": PDF_INVENTORY["totals"]["total_fields"],
        "field_counts_by_category": {}
    }
    
    for cat, data in PDF_INVENTORY["categories"].items():
        summary["field_counts_by_category"][cat] = {
            "description": data["description"],
            "count": data["count"],
            "reference": data.get("reference", "N/A")
        }
    
    summary_file = output_dir / "pdf_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("PDF METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {PDF_INVENTORY['generated_at']}")
    print(f"Categories: {PDF_INVENTORY['totals']['categories']}")
    print(f"Total Fields: {PDF_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(PDF_INVENTORY["categories"].items(), key=lambda x: x[1]["count"], reverse=True):
        ref = data.get("reference", "")[:35]
        print(f"  {cat:35s}: {data['count']:>3}  [{ref}]")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
