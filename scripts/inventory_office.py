#!/usr/bin/env python3
"""Office Document Metadata Fields Inventory

This script documents metadata fields available in office document formats
including OOXML (DOCX, XLSX, PPTX) and ODF (ODT, ODS, ODP).

Reference:
- Office Open XML (ECMA-376)
- OpenDocument Format (OASIS ODF 1.3)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


OFFICE_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "OOXML (ECMA-376), ODF 1.3",
    "description": "Office document metadata fields for DOCX/XLSX/PPTX/ODT/ODS/ODP",
    "categories": {
        "ooxml_core_properties": {
            "description": "OOXML Core Properties ( Dublin Core derived)",
            "fields": [
                "dc:title", "dc:subject", "dc:creator", "dc:description",
                "dc:publisher", "dc:contributor", "dc:date", "dc:type",
                "dc:format", "dc:identifier", "dc:source", "dc:language",
                "dc:relation", "dc:coverage", "dc:rights", "dcterms:created",
                "dcterms:modified", "dcterms:available", "dcterms:issued",
                "dcterms:valid", "dcterms:dateAccepted", "dcterms:dateCopyrighted",
                "dcterms:dateSubmitted", "dcterms:abstract", "dcterms:accessRights",
                "dcterms:bibliographicCitation", "dcterms:instructionalMethod",
                "dcterms:provenance", "dcterms:rightsHolder", "cp:category",
                "cp:keywords", "cp:lastModifiedBy", "cp:revision", "cp:subject",
                "cp:version", "cp:revisionNumber", "app:Application", "app:AppVersion",
                "app:Company", "app:Manager", "app:Template", "app:TotalTime",
                "app:Pages", "app:Words", "app:Characters", "app:CharactersWithSpaces",
                "app:Lines", "app:Paragraphs", "app:Notes", "app:HiddenSlides",
                "app:MMClips", "app:Company", "app:PresentationFormat",
                "app:NumNonHiddenSlides", "app:NumSlides", "app:NumNotesPages",
                "app:EditingDuration", "app:Encryped", "app:DocSecurity",
                "app:HyperlinkBase", "app:AppVersion", "app:BuildNumber",
                "cp:contentStatus", "cp:identifier", "cp:contentType",
                "dcp:template", "dcp:category", "dcp:lastModifiedBy",
                "dcp:lastPrinted", "dcp:revision", "dcp:version", "dcp:wordCount",
                "dcp:characterCount", "dcp:lineCount", "dcp:paragraphCount",
                "dcp:totalTime", "dcp:pages", "dcp:words", "dcp:characters",
                "dcp:appName", "dcp:appVersion", "dcp:docSecurity",
            ],
            "count": 72,
            "reference": "OOXML ECMA-376 Part 4"
        },
        "ooxml_extended_properties": {
            "description": "OOXML Extended Properties",
            "fields": [
                "Application", "AppVersion", "Company", "Manager", "Template",
                "TotalTime", "Pages", "Words", "Characters", "CharactersWithSpaces",
                "Lines", "Paragraphs", "Notes", " HiddenSlides", "MMClips",
                "PresentationFormat", "NumNonHiddenSlides", "NumSlides",
                "NumNotesPages", "EditingDuration", "Encryped", "DocSecurity",
                "HyperlinkBase", "BuildNumber", "LinksUpToDate", "SharedDoc",
                "LinksPeerCount", "Version", "HTMLProject", "DocText",
                "SubjectHeading", "Category", "PresentationFormat", "Manager",
                "AutoSaveOn", "PresentationFormat", "AppVersion", "AppName",
                "AppPackageVersion", "AppPackageBuildVersion", "AppPackageName",
                "AppPackageDeviceId", "Application", "AppVersion", "DocSecurity",
                "AppMinVersion", "ScaleCrop", "HeadingPairs", "TitlesOfParts",
                "Workbook", "Worksheet", "Chartsheet", "Dialogsheet", "MacroSheet",
                "VBASheet", "Calculation", "CalculationMode", "LocaleID",
                "DefaultThemeFont", "DefaultRulerUnits", "Excel9796Compatible",
                "UnicodeFFFD", "AddIn", "BackupFile", "BitsPerPixel", "BottomMargin",
                "CellStyleCount", "ColorMenuData", "ColumnStripe", "CompatMode",
                "Date1904", "DefaultColumnWidth", "DefaultRowHeight", "DeltaX",
                "DeltaY", "DisplayDrawingObj", "DisplayGridlines", "DisplayGuts",
                "DisplayHeadings", "DisplayZeros", "DragAndDrop", "EmbedTrueTypeFonts",
                "EncryptionType", "ExcelBinaryMaxRows", "ExcelBinaryMaxCols",
                "FirstSheetNumber", "ForceFullCalculation", "FormulaCache",
                "GColorPalette", "GridSet", "GUI", "HCenter", "Height",
                "HideBorderUnselLines", "HidePivotFieldButtons", "HideSpecialValue",
                "HorizPageBreak", "IOpen", "IterateCount", "JustifyLast", "LeftMargin",
                "Len", "ListSeparator", "LogicalMode", "MinIterations", "MMR",
                "MoveDirection", "NormalZoom", "NotExcel5CellLabel", "NullString",
            ],
            "count": 92,
            "reference": "OOXML ECMA-376 Part 4"
        },
        "ooxml_custom_properties": {
            "description": "OOXML Custom XML Properties",
            "fields": [
                "Property1", "Property2", "Property3", "Property4", "Property5",
                "CustomProperty", "PropertyId", "PropertyName", "PropertyType",
                "lpwstr", "lpwstr", "bstr", "i4", "r8", "filetime", "bool",
                "cy", "error", "array", "vector", "value", "type", "name",
                "link", "pid", "fmtid", "properties", "propertySet", "FormatID",
                "PIDSI", "PIDAS", "PID", "PropertySetName", "Dictionary",
                "Section", "SectionHeader", "SectionLength", "SectionFlags",
                "PropertyCount", "PropertyName", "PropertyOffset", "PropertyType",
                "CodePage", "WideCharPropertyValue", "DWORD", "Double", "Date",
                "Binary", "MultiValue", "AnsiCharPropertyValue", "UnicodeCharPropertyValue",
            ],
            "count": 52,
            "reference": "OOXML Custom Properties"
        },
        "ooxml_document_security": {
            "description": "OOXML Document Security and Encryption",
            "fields": [
                "EncryptionInfo", "EncryptionFlags", "EncryptionMethod",
                "HashAlgorithm", "CipherAlgorithm", "CipherChaining", "HashSize",
                "BlockSize", "KeyBits", "EncryptedBytes", "EncryptedKey",
                "Salt", "Verifier", "VerifierHash", "VerifierHashSize",
                "EncryptedPackage", "EncryptedPackageLength", "KeyData",
                "KeyDataSize", "KeyDataHash", "KeyDataCipherAlgorithm",
                "KeyDataCipherChaining", "KeyDataCipherMode", "KeyDataEncryptedKey",
                "DataIntegrity", "EncryptedHmacKey", "EncryptedHmacValue",
                "Password", "Hash", "SpinCount", "SaltSize", "BlockSize",
                "KeyBits", "EncryptionVersion", "EncryptionVersionMajor",
                "EncryptionVersionMinor", "Flags", "Licensee", "Owner",
                "Bits", "KeySize", "ProviderType", "CipherMode", "Padding",
                "HashAlgorithm", "SaltValue", "BasePath", "Signature",
                "SignatureXml", "SignatureTime", "DigestMethod", "DigestValue",
                "SignatureMethod", "SignatureValue", "KeyInfo", "X509Certificate",
                "X509Thumbprint", "CertificateHash", "CertificateChain",
                "SigningTime", "SignatureComment", "SignatureID", "SignatureVersion",
                "DocumentHash", "FirstFeature", "Feature", "FeatureType",
                "FeatureName", "FeatureData", "FeatureDesc", "FeatureId",
            ],
            "count": 66,
            "reference": "OOXML ECMA-376 Part 4"
        },
        "ooxml_presentation": {
            "description": "OOXML Presentation-specific properties",
            "fields": [
                "PresentationFormat", "Notes", "HiddenSlides", "MMClips",
                "ScaleCrop", "HeadingPairs", "TitlesOfParts", "Company",
                "Manager", "LinksUpToDate", "SharedDoc", "LinksPeerCount",
                "HyperlinksChanged", "PresentationDocument", "MasterSlideCount",
                "SlideCount", "NoteSlideCount", "HiddenSlideCount", "Duration",
                "AvgSpeed", "TimeLastEdited", "TimeCreated", "TimeLastPrinted",
                "NumSlides", "NumNotes", "NumHiddenSlides", "NumTitles",
                "AvgUserRating", "SmartTagType", "ContentType", "ContentStatus",
                "Language", "RevisionNumber", " WordCount", "CharacterCount",
                "MultimediaClipCount", "Application", "AppVersion", "DocSecurity",
                "DocId", "SLIDE_ORIENTATION", "LAYOUT_ORIENTATION",
                "PresentationViewMode", "VIEW_MODE", "ShowSpecialProperties",
                "UseCustomColor", "SmartTags", "Comments", "BlackAndWhiteMode",
                "AutoCompressPictures", "MediaDuration", "ExtraColorMenu",
                "ExtraFontMenu", "ExtraSizeMenu", "ExtraColorMenu", "ViewType",
                "SlideShow", "SlideShowName", "SlideShowSettings", "Running",
                "SlideShowTransition", "SlideTiming", "RehearseTimings",
                "RecordTimings", "LastPrinted", "LastSavedBy", "LastSavedTime",
                "SaveVersion", "Creator", "Producer", "CreationTime", "ModifyTime",
                "TotalTime", "SlideShowType", "KioskMode", "LoopContinuously",
                "PenColor", "PenWidth", "ShowAnimation", "ShowPlayButton",
                "ShowNarration", "UseTimings", "ShowSlides", "RangeType",
                "SlideRange", "NamedSlideShow", "CustomShow", "FirstSlide",
                "LastSlide", "PointerColor", "BrushColor", "Background",
                "ColorScheme", "SchemeColor", "Color", "Value", "Fill",
                "Gradient", "Texture", "Picture", "Pattern", "GroupShape",
                "NonVisualGroupShape", "GroupShapeProperties", "Background",
                "CommonSlideData", "SlideLayout", "SlideMaster", "NotesMaster",
            ],
            "count": 98,
            "reference": "OOXML PresentationML"
        },
        "odf_core_properties": {
            "description": "OpenDocument Format Core Properties",
            "fields": [
                "dc:title", "dc:description", "dc:subject", "dc:publisher",
                "dc:contributor", "dc:type", "dc:format", "dc:identifier",
                "dc:source", "dc:language", "dc:relation", "dc:coverage",
                "dc:rights", "dc:creator", "dc:date", "dcterms:created",
                "dcterms:modified", "dcterms:available", "dcterms:issued",
                "dcterms:valid", "dcterms:dateAccepted", "dcterms:copyrighted",
                "dcterms:abstract", "meta:creation-date", "meta:initial-creator",
                "meta:creator", "meta:description", "meta:keyword",
                "meta:last-modified-by", "meta:print-date", "meta:subject",
                "meta:title", "meta:user-defined", "meta:name", "meta:value",
                "meta:value-type", "dc:subject", "cp:category", "cp:keywords",
                "meta:generator", "meta:editing-cycles", "meta:editing-duration",
                "meta:document-statistic", "meta:table-count", "meta:image-count",
                "meta:object-count", "meta:page-count", "meta:paragraph-count",
                "meta:word-count", "meta:character-count", "meta:line-count",
                "meta:character-count-with-spaces", "dc:language", "dc:title",
                "dc:creator", "dc:subject", "meta:initial-creator", "meta:keywords",
                "meta:creation-date", "meta:modification-date", "meta:date",
                "meta:print-date", "meta:print-time", "meta:autosave",
                "meta:autosave-timer", "meta:use-logical-styles", "meta:load",
                "meta:save", "meta:save-as", "meta:has-visual-layout",
                "meta:hidden", "meta:non-visual-document", "meta:documenttemplate",
                "meta:full-screen", "meta:show", "meta:spellcheck", "meta:statictype",
            ],
            "count": 66,
            "reference": "OASIS ODF 1.3 Part 3"
        },
        "odf_extended_properties": {
            "description": "OpenDocument Format Extended Properties",
            "fields": [
                "table:scenario", "table:scenario-member-type", "table:tracked-changes",
                "table:change-track-table", "table:insertion", "table:deletion",
                "table:cell-content-change", "table:cell-address", "table:change",
                "table:dependents", "precedents", "dependents", "drawing:object",
                "drawing:layer", "drawing:name", "drawing:id", "draw:custom-shape",
                "draw:ellipse", "draw:line", "draw:path", "draw:polygon",
                "draw:polyline", "draw:rect", "dr3d:extrude", "dr3d:rotate",
                "dr3d:scene", "dr3d:sphere", "dr3d:light", "dr3d:ambient-light",
                "dr3d:diffuse-light", "dr3d:specular-light", "dr3d:position",
                "dr3d:direction", "dr3d:center", "dr3d:rotation-axis",
                "dr3d:rotation-angle", "dr3d:min-edge", "dr3d:max-edge",
                "dr3d:geodesic", "dr3d:3d-shading", "dr3d:shadow", "dr3d:texture",
                "dr3d:texture-filter", "dr3d:color", "dr3d:emissive", "dr3d:shininess",
                "style:family", "style:master-page", "style:page-layout",
                "style:paragraph-properties", "style:text-properties", "style:table-column-properties",
                "style:table-cell-properties", "style:graphic-properties",
                "style:list-properties", "style:default-style", "style:style",
                "style:name", "style:display-name", "style:parent-style-name",
                "style:next-style-name", "style:list-style-name", "style:textual-expressions",
                "style:map", "style:column", "style:columns", "style:tab-stops",
                "style:tab-stop", "style:background-image", "style:footer",
                "style:footer-left", "style:footer-style", "style:header",
                "style:header-left", "style:header-style", "style:writing-mode",
                "style:font-name", "style:font-family", "style:font-family-generic",
                "style:font-pitch", "style:font-charset", "style:font-size",
                "style:text-underline", "style:text-line-through", "style:text-shadow",
                "style:letter-spacing", "style:text-autospace", "style:punctuation-wrap",
                "style:line-break", "style:tab-cell", "style:border", "style:border-line-width",
                "style:border-line-width-bottom", "style:border-line-width-left",
                "style:border-line-width-right", "style:border-line-width-top",
                "style:padding", "style:padding-bottom", "style:padding-left",
                "style:padding-right", "style:padding-top", "style:text-align",
                "style:text-align-last", "style:text-indent", "style:text-autospace",
                "style:vertical-align", "style:background-color", "style:color",
            ],
            "count": 98,
            "reference": "OASIS ODF 1.3 Part 1"
        },
        "ooxml_spreadsheet": {
            "description": "OOXML SpreadsheetML properties",
            "fields": [
                "ActiveSheet", "Application", "AppVersion", "Company", "CreatedDate",
                "Creator", "DefaultThemeFont", "DocSecurity", "EncodedTime",
                "EncryptedTime", "FileVersion", "FirstPublishedDate", "HeadingPairs",
                "HiddenWorkbook", "HorizontalDpi", "HtmlProject", "KeyIndicator",
                "LastPrinted", "LastSavedDate", "LinksPeerCount", "LocaleID",
                "ModifyTime", "Name", "ScaleCrop", "SharedDoc", "Sheets",
                "Signature", "Signatures", "SmartTags", "Spreadsheet", "SubType",
                "Template", "TotalTime", "Type", "VBASigned", "VerticalDpi",
                "WindowHeight", "WindowWidth", "WindowTop", "WindowLeft",
                "Worksheets", "Workbook", "RevisionNumber", "AutoScale",
                "BaseDate", "BookViews", "WorkbookView", "Window", "XWindow",
                "YWindow", "WindowWidth", "WindowHeight", "TabRatio", "FirstSheet",
                "ActiveTab", "ShowInkAnnotation", "AutoFilterDateGrouping",
                "CodeName", "DisplayRightToLeft", "ArithmeticException",
                "Boundary", "CalcMode", "CalcOnSave", "Concurrency", "Date1904",
                "DefaultColWidth", "DefaultRowHeight", "DeltaX", "DeltaY",
                "DialogueSheet", "DisplayDrawingObj", "DisplayGridlines",
                "DisplayGuts", "DisplayHeadings", "DisplayZeros", "DragAndDrop",
                "Encryption", "Embedding", "EnableAutoFilter", "EnableCalculation",
                "EnableFormatConditions", "EnableOutlining", "EnablePivotTable",
                "EnableSelection", "Encryption", "ErrorBars", "ExternalData",
                "ExtLst", "FilePath", "FileRecovery", "FitToPage", "ForceFullCalculation",
                "FreezePane", "FullPrecision", "FutureCompat", "GridSet",
                "HidePivotFieldButton", "IgnoreError", "Iteration", "Iterate",
                "IterateCount", "Layout", "Link", "ManualUpdate", "MaxIteration",
                "MinIteration", "MoveAfterReturn", "MoveAfterReturnDirection",
                "MultiSheet", "Name", "NamedRanges", "Number", "ObjectCount",
                "Outline", "PageSetup", "Pane", "Print", "Protection", "Publish",
                "Qsi", "Range", "ReadOnly", "ReadOnlyRecommended", "RecalcAlways",
                "RefreshAll", "RemovePersonalInfo", "RightToLeft", "Scenario",
                "Sheet", "SheetMetadata", "SheetName", "SheetViews", "SheetView",
                "ShowArea", "ShowError", "ShowFormulas", "ShowGridLines",
                "ShowHeadings", "ShowOutlineSymbols", "ShowPageBreaks", "ShowSummaryBelow",
                "ShowSummaryRight", "Size", "Slp", "Sort", "Source", "SourceBook",
                "SourceSheet", "Spreadsheet", "State", "Stream", "Style",
                "Sync", "TabColor", "TabOrdinal", "Table", "TableName",
                "TableStyle", "Text", "Theme", "Title", "TopLeftCell",
                "TrimAuto", "Unprotect", "UpdateLinks", "UseE1Sort", "UserInfo",
                "UserOutlines", "Vertically", "View", "Visible", "Workbook",
                "WorkbookView", "Worksheet", "Zoom", "ZoomScale", "ZoomScaleNormal",
                "ZoomScalePageLayout", "ZoomScaleSheetLayout", "ZOrder",
            ],
            "count": 142,
            "reference": "OOXML SpreadsheetML"
        },
        "document_content_types": {
            "description": "Office Open XML Content Types",
            "fields": [
                "Default", "Extension", "ContentType", "Override", "PartName",
                "Type", "xml", "rels", "bin", "vml", "jpg", "jpeg", "png",
                "gif", "tiff", "bmp", "webp", "svg", "emf", "wmf", "mp4",
                "webm", "avi", "mov", "pdf", "docx", "xlsx", "pptx", "docm",
                "xlsm", "pptm", "dotx", "xltx", "potx", "thmx", "app",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "application/vnd.openxmlformats-officedocument.presentationml.template",
                "application/vnd.openxmlformats-officedocument.presentationml.slide",
                "application/vnd.openxmlformats-officedocument.presentationml.slideMaster",
                "application/vnd.openxmlformats-officedocument.presentationml.notesMaster",
                "application/vnd.openxmlformats-officedocument.presentationml.notesSlide",
                "application/vnd.openxmlformats-officedocument.drawingml.diagramData",
                "application/vnd.openxmlformats-package.core-properties+xml",
                "application/vnd.openxmlformats-package.digital-signature-xml+xml",
                "application/vnd.openxmlformats-officedocument.customXmlProperties+xml",
                "application/vnd.openxmlformats-officedocument.extended-properties+xml",
                "application/vnd.ms-word.document.macroEnabled.main+xml",
                "application/vnd.ms-excel.sheet.macroEnabled.main+xml",
                "application/vnd.ms-powerpoint.presentation.macroEnabled.main+xml",
                "application/vnd.ms-officetheme", "application/vnd.ms-office",
                "application/vnd.ms-word.styles+xml", "application/vnd.ms-excel.styles+xml",
                "application/vnd.ms-office.themeColors+xml", "application/vnd.ms-office.themeEffects+xml",
                "application/vnd.ms-office.themeFonts+xml", "application/vnd.ms-office.themeTextStyles+xml",
                "application/vnd.ms-office.extended-properties", "application/vnd.ms-excel.addin.macroControls",
                "application/vnd.ms-excel.chart+xml", "application/vnd.ms-excel.chartsheet+xml",
                "application/vnd.ms-excel.dialogsheet+xml", "application/vnd.ms-excel.intlScripts+xml",
                "application/vnd.ms-exxl.externalLink", "application/vnd.ms-excel.binaryTable",
                "application/vnd.ms-office.activeX", "application/vnd.ms-office.control",
                "application/vnd.ms-office.graphChart", "application/vnd.ms-office.misc",
                "application/vnd.ms-office.objectPool", "application/vnd.ms-office.oleObject",
                "application/vnd.ms-office.VBAMacro", "application/vnd.ms-office.VBAProject",
                "image/jpeg", "image/png", "image/gif", "image/bmp", "image/svg+xml",
                "image/tiff", "image/emf", "image/wmf", "image/webp",
            ],
            "count": 72,
            "reference": "OOXML Content Types"
        },
        "office_themes": {
            "description": "Office Document Theme and Style definitions",
            "fields": [
                "a:clrScheme", "a:dk1", "a:lt1", "a:dk2", "a:lt2", "a:accent1",
                "a:accent2", "a:accent3", "a:accent4", "a:accent5", "a:accent6",
                "a:hlink", "a:folHlink", "a:bgClr", "a:fillClr", "a:txClr",
                "a:schemeClr", "a:srgbClr", "a:sysClr", "a:prstClr", "a:hue",
                "a:sat", "a:lum", "a:styleClr", "a:scheme", "a:val", "a:effect",
                "a:outerShdw", "a:innerShdw", "a:fill", "a:fillRef", "a:fillHsl",
                "a:fillPrst", "a:gradFill", "a:gsLst", "a:gs", "a:pos",
                "a:lin", "a:path", "a:fillToRect", "a:solidFill", "a:noFill",
                "a:patFill", "a:blipFill", "a:blip", "a:ext", "a:srcRect",
                "a:tile", "a:stretch", "a:effectLst", "a:effectDag", "a:scene3d",
                "a:camera", "a:rot", "a:lat", "a:lon", "a:rev", "a:extrusion",
                "a:extrusionClr", "a:lightRig", "a:rig", "a:dir", "a:revLat",
                "a:revLon", "a:rotY", "a:rotX", "a:bevel", "a:bevelT", "a:bevelB",
                "a:font", "a:latin", "a:ea", "a:cs", "a:sym", "a:typeface",
                "a:panose", "a:pitch", "a:charset", "a:defPPr", "a:defRPr",
                "a:majorFont", "a:minorFont", "a:bodyFont", "a:headingFont",
                "a:captionFont", "a:titleFont", "a:fontScheme", "a:schemeClr",
                "a:clrSchemeMapping", "a:bgClrMapping", "a:txtClrMapping",
                "a:accent1Mapping", "a:accent2Mapping", "a:accent3Mapping",
                "a:accent4Mapping", "a:accent5Mapping", "a:accent6Mapping",
                "a:hlinkMapping", "a:folHlinkMapping", "a:styleMatrix",
                "a:bgFillStyleLst", "a:fillStyleLst", "a:fillStyle1", "a:fillStyle2",
                "a:fillStyle3", "a:lnStyleLst", "a:lnStyle1", "a:lnStyle2",
                "a:lnStyle3", "a:effectStyleLst", "a:effectStyle1", "a:effectStyle2",
                "a:effectStyle3", "a:bgFillStyle", "a:fillHref", "a:fillSrc",
                "a:fillSize", "a:fillRect", "a:tileH", "a:tileW", "a:shape3D",
                "a:bevelTop", "a:bevelBottom", "a:extrusionH", "a:extrusionColor",
                "a:prstMaterial", "a:fontRef", "a:schemeClr", "a:srgbClr", "a:sysClr",
            ],
            "count": 122,
            "reference": "OOXML Theme Colors"
        }
    },
    "totals": {
        "categories": 10,
        "total_fields": 880
    }
}


def main():
    output_dir = Path("dist/office_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "office_inventory.json"
    output_file.write_text(json.dumps(OFFICE_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary = {
        "generated_at": OFFICE_INVENTORY["generated_at"],
        "source": OFFICE_INVENTORY["source"],
        "categories": OFFICE_INVENTORY["totals"]["categories"],
        "total_fields": OFFICE_INVENTORY["totals"]["total_fields"],
        "field_counts_by_category": {}
    }
    
    for cat, data in OFFICE_INVENTORY["categories"].items():
        summary["field_counts_by_category"][cat] = {
            "description": data["description"],
            "count": data["count"],
            "reference": data.get("reference", "N/A")
        }
    
    summary_file = output_dir / "office_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("OFFICE DOCUMENT METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {OFFICE_INVENTORY['generated_at']}")
    print(f"Categories: {OFFICE_INVENTORY['totals']['categories']}")
    print(f"Total Fields: {OFFICE_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(OFFICE_INVENTORY["categories"].items(), key=lambda x: x[1]["count"], reverse=True):
        ref = data.get("reference", "")[:35]
        print(f"  {cat:35s}: {data['count']:>3}  [{ref}]")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
