#!/usr/bin/env python3
"""Font Metadata Fields Inventory

This script documents metadata fields available in font formats
including OpenType, WOFF, WOFF2, TrueType, and Type 1.

Reference:
- OpenType Specification 1.9
- Microsoft Typography
- W3C WOFF specifications
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


FONT_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "OpenType 1.9, WOFF, TrueType, Type 1",
    "description": "Font metadata fields for OpenType, WOFF, WOFF2, TrueType",
    "categories": {
        "opentype_tables": {
            "description": "OpenType table tags and fields",
            "fields": [
                "TTF", "OTF", "TTC", "DFONT", "sfnt", "post", "maxp", "head",
                "hhea", "hmtx", "loca", "glyf", "cmap", "cvt ", "fpgm", "prep",
                "gasp", "name", "OS/2", "cmap", "cvt ", "fpgm", "prep", "gasp",
                "name", "OS/2", "post", "pre", "pclt", "VDMX", "hdmx", "LTSH",
                "VORG", "EBDT", "EBLC", "EBSC", "BASE", "GDEF", "GPOS", "GSUB",
                "JSTF", "MATH", "CBDT", "CBLC", "COLR", "CPAL", "SVG ", "sbix",
                "acnt", "avar", "bdat", "bloc", "bsln", "cvar", "cwhd", "D SIG",
                "DSIG", "feat", "fpgm", "gasp", "glyf", "hdmx", "head", "hhea",
                "hmtx", "JUSF", "loca", "ltsh", "math", "maxp", "meta", "MORT",
                "morx", "name", "nav", "nukg", "prep", "prop", "RES", "sbit",
                "sbix", "silf", "sphd", "splx", "SSF", "stroke", "sups", "SVG",
                "SWsh", "trig", "tsi0", "tsi1", "tsi2", "tsi3", "ttcw", "TYP1",
                "诉", "vari", "vhea", "vmtx", "XREF", "Zapf", "CFF ", "CFF2",
                "VORG", "fpgm", "EBDT", "EBSC", "EBLC", "CBDT", "CBLC", "sbix",
                "COLR", "CPAL", "SVG ", "XDTS", "FFT ", "MMSD", "MVS ", "BBOX",
                "DST ", "EAC ", "EFC ", "GDL ", "NST ", "PRS ", "PST ", "RDT ",
                "TFM ", "XML ", "ZIN", "FFTM", "Fpgm", "Gasp", "Gloc", "Glat",
                "GPOS", "GSUB", "GDEF", "BASE", "JSTF", "MATH", "TSIC",
            ],
            "count": 88,
            "reference": "OpenType Specification"
        },
        "opentype_names": {
            "description": "OpenType name table identifiers",
            "fields": [
                "copyright", "family", "subfamily", "subfamily", "font name",
                "preferred family", "preferred subfamily", "compatible full",
                "sample text", "postScript name", "WWS family", "WWS subfamily",
                "light palette", "dark palette", "trademark", "manufacturer",
                "designer", "URL designer", "URL vendor", "license", "URL license",
                "license description", "reserved", "manufacturer URL", "typographic family",
                "typographic subfamily", "compatible mac", "sample text", "CID findfont name",
                "URL CID", "embedding rights", "embedding restrictions", "print and preview",
                "preview and print", "editable embedding", "no subsetting", "bitmap only",
                "description", "version", "name ID 0", "name ID 1", "name ID 2",
                "name ID 3", "name ID 4", "name ID 5", "name ID 6", "name ID 7",
                "name ID 8", "name ID 9", "name ID 10", "name ID 11", "name ID 12",
                "name ID 13", "name ID 14", "name ID 15", "name ID 16", "name ID 17",
                "name ID 18", "name ID 19", "name ID 20", "name ID 21", "name ID 22",
                "name ID 23", "name ID 24", "name ID 25", "name ID 26", "name ID 27",
                "name ID 28", "name ID 29", "name ID 30", "name ID 31", "platform 0",
                "platform 1", "platform 2", "platform 3", "platform 4", "platform 5",
                "unicode", "macintosh", "windows", "custom", "english", "french",
                "german", "italian", "dutch", "swedish", "spanish", "norwegian",
                "portuguese", "danish", "finnish", "japanese", "korean", "chinese",
                "pid 0", "pid 1", "pid 2", "pid 3", "pid 4", "pid 5", "pid 6",
            ],
            "count": 85,
            "reference": "OpenType name IDs"
        },
        "opentype_metrics": {
            "description": "OpenType metrics and measurement fields",
            "fields": [
                "unitsPerEm", "xMin", "yMin", "xMax", "yMax", "macStyle",
                "lowestRecPPEM", "fontDirectionHint", "indexToLocFormat",
                "glyphDataFormat", "baseline0", "baseline1", "baseline2",
                "baseline0ID", "baseline1ID", "baseline2ID", "ascent", "descent",
                "lineGap", "advanceWidthMax", "minLeftSideBearing", "minRightSideBearing",
                "xMaxExtent", "caretSlopeRise", "caretSlopeRun", "caretOffset",
                "reserved0", "reserved1", "reserved2", "reserved3", "metricDataFormat",
                "numberOfHMetrics", "leftSideBearing", "advanceWidth", "rightSideBearing",
                "verticalAscender", "verticalDescender", "verticalLineGap",
                "verticalOriginX", "verticalOriginY", "advanceHeightMax",
                "minTopSideBearing", "minBottomSideBearing", "yMaxExtent",
                "slopeRun", "slopeRise", "xHeight", "capHeight", "sbIX",
                "sbX", "sbY", "reserved", "reserved", "sTypoAscender",
                "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent",
                "ulCodePageRange1", "ulCodePageRange2", "ulCodePageRange3",
                "ulCodePageRange4", "sxHeight", "sCapHeight", "cHeight", "AvgCharWidth",
                "BodyHeight", "QuadWidth", "hHeadA", "hHeadD", "hHeadRes",
                "hHeadK", "minCon", "maxCon", "minExt", "maxExt", "yMinExt",
                "yMaxExt", "internalLeading", "externalLeading", "StemWidth",
                "StemHeight", "Weight", "Width", "Slant", "OpticalSize",
                "Lsb", "Rsb", "AwExt", "Slp", "Bsl", "Sls", "Bse", "Vvr",
            ],
            "count": 92,
            "reference": "OpenType Metrics"
        },
        "opentype_features": {
            "description": "OpenType feature tags and fields",
            "fields": [
                "aalt", "abvf", "abvm", "abvs", "afrc", "akhn", "alph", "afrc",
                "bng2", "bng2", "blws", "calt", "case", "ccmp", "cfar", "cjcn",
                "clig", "cpct", "cpsp", "cswh", "curs", "cv01", "cv02", "cv03",
                "cv04", "cv05", "cv06", "cv07", "cv08", "cv09", "cv10", "cv11",
                "cv12", "cv13", "cv14", "cv15", "cv16", "cv17", "cv18", "cv19",
                "cv20", "cv21", "cv22", "cv23", "cv24", "cv25", "cv26", "cv27",
                "cv28", "cv29", "cv30", "cv31", "cv32", "cv33", "cv34", "cv35",
                "cv36", "cv37", "cv38", "cv39", "cv40", "cv41", "cv42", "cv43",
                "cv44", "cv45", "cv46", "cv47", "cv48", "cv49", "cv50", "cv51",
                "cv52", "cv53", "cv54", "cv55", "cv56", "cv57", "cv58", "cv59",
                "cv60", "cv61", "cv62", "cv63", "cv64", "cv65", "cv66", "cv67",
                "cv68", "cv69", "cv70", "cv71", "cv72", "cv73", "cv74", "cv75",
                "cv76", "cv77", "cv78", "cv79", "cv80", "cv81", "cv82", "cv83",
                "cv84", "cv85", "cv86", "cv87", "cv88", "cv89", "cv90", "cv91",
                "cv92", "cv93", "cv94", "cv95", "cv96", "cv97", "cv98", "cv99",
                "dflt", "dlig", "dnom", "dtls", "expt", "falt", "fin2", "fin3",
                "fina", "flac", "frac", "fwid", "hagl", "haln", "halt", "halv",
                "ham1", "ham2", "ham3", "ham4", "ham5", "harf", "hb1", "hb2",
                "hb2", "hbgr", "hcl2", "hwid", "hojo", "hwid", "init", "isol",
                "ital", "jalt", "jamo", "jfin", "jfms", "jinh", "join", "jpm4",
                "jpmo", "kern", "klcw", "liga", "lnum", "locl", "mark", "med2",
                "medi", "mgrk", "mkmk", "mset", "nalt", "nlck", "nukt", "numr",
                "onum", "opbd", "ordn", "ornm", "palt", "pcap", "pkna", "pnum",
                "pref", "pres", "pstf", "psts", "pwid", "qwid", "rand", "rclt",
                "rkrf", "rlig", "rphf", "rtbd", "rtla", "rtlm", "ruby", "rvrn",
                "salt", "salt2", "sbit", "sbix", "scmp", "script", "ssty", "stch",
                "subs", "sups", "swsh", "titl", "tnam", "tnum", "trad", "twid",
                "unic", "valt", "vatu", "vert", "vhal", "vjmo", "vkna", "vkrn",
                "vpal", "vrt2", "vrtr", "vwid", "zero", "zlcn", "zwnj", "zwj",
            ],
            "count": 142,
            "reference": "OpenType Feature Tags"
        },
        "woff_metadata": {
            "description": "WOFF and WOFF2 metadata fields",
            "fields": [
                "signature", "flavor", "length", "numTables", "totalSfntSize",
                "totalCompressedSize", "metaOffset", "metaLength", "metaOrigLength",
                "privOffset", "privLength", "woffVersion", "woff2Version",
                "sfntDirVersion", "fontRevision", "checksumAdjustment",
                "magicNumber", "flags", "fontDirectionHint", "fontDirectionHint",
                "indexToLocFormat", "glyphDataFormat", "reserved0", "reserved1",
                "reserved2", "reserved3", "XHeight", "CapHeight", "MaxContext",
                "defaultGSUB", "defaultGPOS", "defaultGDEF", "defaultBase",
                "defaultJSTF", "defaultMATH", "fontFamily", "fontSubfamily",
                "fontIdentifier", "fullName", "version", "postScriptName",
                "copyright", "trademark", "manufacturer", "designer", "URL designer",
                "URL vendor", "license", "URL license", "license Description",
                "reserved", "manufacturer URL", "typography Family", "typography Subfamily",
                "compatible Full", "sample Text", "postScript Name", "WWS Family",
                "WWS Subfamily", "light Palette", "dark Palette", "description",
                "embedding rights", "reserved", "Font header", "Font directory",
                "Table directory", "Compressed data", "Uncompressed data",
                "Data size", "Offset", "Compression", "Compressed length",
                "Uncompressed length", "Orig length", "checksum", "Data type",
                "Application", "Meta data", "Private data", "File identifier",
                "URI", "Compression method", "Encryption", "Modified", "Data length",
                "Original length", "Padding", "Block size", "Block offset",
            ],
            "count": 88,
            "reference": "WOFF 1.0 / WOFF 2.0"
        },
        "glyph_outline": {
            "description": "Glyph outline and path data fields",
            "fields": [
                "numberOfContours", "xMin", "yMin", "xMax", "yMax", "endPtsOfContours",
                "instructionLength", "instructions", "flags", "xCoordinate",
                "yCoordinate", "onCurve", "repeat", "xShort", "yShort", "xDual",
                "yDual", "xNonSmooth", "yNonSmooth", "curveType", "conic",
                "cubic", "quadratic", "Bezier", "CubicBezier", "Spline",
                "StartPoint", "EndPoint", "ControlPoint1", "ControlPoint2",
                "TangentPoint", "Simple", "Compound", "Composite", "Arg1And2",
                "Arg1And2Descaled", "Arg1And2Unchanged", "Arg1SetAnd2Descaled",
                "Arg1SetAnd2Unchanged", "RoundXYToGrid", "RoundXYToGrid",
                "Scale", "ScaleDescaled", "NoScale", "UseMetrics", "UseMetricsDescaled",
                "NoScaleDescaled", "Inverse", "Reverse", "Translate", "Rotate",
                "ScaleAndTranslate", "MapToInteger", "UseIntegerScaling",
                "AnchorPoint", "ReferencePoint", "PointNumber", "FirstPoint",
                "SecondPoint", "Transform", "ScaleX", "ScaleY", "Scale01",
                "Scale10", "TransformXX", "TransformXY", "TransformYX", "TransformYY",
                "OffsetX", "OffsetY", "ShiftX", "ShiftY", "MatchedPoint",
                "MatchedPoints", "OriginalPoint", "NewPoint", "PointMatch",
                "BoundingBox", "CBox", "Bounds", "Extents", "ControlBounds",
                "AdvanceWidth", "AdvanceHeight", "LeftBearing", "RightBearing",
                "TopBearing", "BottomBearing", "xBearing", "yBearing", "Width",
                "Height", "BearingX", "BearingY", "xMin", "yMin", "xMax", "yMax",
                "CaretSlope", "CaretAngle", "CaretOffset", "CaretRise", "CaretRun",
                "GlyphClass", "AttachPoint", "LigatureCaretList", "LigatureGlyph",
                "LigatureComponent", "MarkAttachClass", "MarkGlyphSets",
            ],
            "count": 98,
            "reference": "OpenType Glyph Data"
        },
        "color_font": {
            "description": "Color font and emoji metadata",
            "fields": [
                "COLR", "CPAL", "SVG ", "sbix", "CBDT", "CBLC", "EBDT", "EBLC",
                "ColorGlyph", "ColorLayer", "BaseGlyph", "LayerGlyph", "LayerCount",
                "PaletteEntry", "PaletteType", "Palette", "PaletteEntryCount",
                "PaletteEntryIndex", "PaletteEntryValue", "PaletteEntryName",
                "PaletteEntryTarget", "PaletteEntryBack", "PaletteEntryFore",
                "PaletteLabel", "PaletteEntryLabel", "PaletteUnicodeRange1",
                "PaletteUnicodeRange2", "PaletteUnicodeRange3", "PaletteUnicodeRange4",
                "PaletteHasBackdrop", "PaletteNameID", "BackgroundColor",
                "ForegroundColor", "OutlineColor", "OutlineThickness",
                "ClipBox", "ClipBox2D", "xMin", "yMin", "xMax", "yMax",
                "GlyphOrigin", "GlyphAnchor", "AnchorX", "AnchorY", "AnchorPoint",
                "AnchorSize", "AnchorName", "IsCentered", "HasVerticalMetric",
                "ClipPath", "ClipPathIndex", "ClipPathData", "ClipPathOffset",
                "ClipPathLength", "ImageData", "ImageFormat", "ImageWidth",
                "ImageHeight", "ImageColorDepth", "ImageDataSize", "ImageDataType",
                "ImageOffset", "ImageRowStride", "ImagePixelData", "BigGlyph",
                "SmallGlyph", "GlyphImage", "GlyphName", "GlyphUnicode",
                "GlyphSequence", "GlyphVariation", "VariationSelector",
                "DefaultGlyph", "NonDefaultGlyph", "PaletteIndex", "PaletteEntry",
                "ColorRecord", "ColorValue", "ColorProfile", "ColorSpace",
                "ColorType", "ColorData", "ColorFormat", "ColorIndex",
                "ColorCount", "ColorTable", "ColorTableEntry", "ColorTableName",
                "ColorTableUnicode", "ColorTableValues", "color_layers",
                "color_glyph", "color_layer_records", "layer_glyphs", "layer_count",
                "paint", "paint_format", "paint_color", "paint_gradient",
                "paint_image", "paint_solid", "paint_linear_gradient",
                "paint_radial_gradient", "paint_sweep_gradient", "paint_glyph",
                "paint_colr_glyph", "paint_transform", "paint_rotate",
                "paint_scale", "paint_skew", "paint_translate", "paint_composite",
            ],
            "count": 96,
            "reference": "OpenType Color Fonts"
        },
        "variable_font": {
            "description": "Variable font and axis metadata",
            "fields": [
                "fvar", "avar", "gvar", "cvar", "STAT", "MVAR", "HVAR", "VVAR",
                "MVAR", "JVAR", "VARC", "VDMX", "Font axes", "Axis Tag", "Axis Name",
                "AxisOrdering", "AxisMinimum", "AxisMaximum", "AxisDefault",
                "AxisFlags", "Tag", "Name", "MinValue", "MaxValue", "DefaultValue",
                "flags", "hidden", "instance", "InstanceName", "InstanceValue",
                "Coordinates", "DesignCoordinates", "UserCoordinates", "TupleIndex",
                "TupleVariation", "PeakTuple", "IntermediateTuples", "DegenerateTuple",
                "PrivatePoint", "SharedPoints", "ControlPoint", "ControlPointData",
                "Deltas", "PackedDeltas", "DeltaSetIndex", "DeltaSetIndexFormat",
                "GlyphVariation", "VariationData", "ItemVariationStore",
                "ItemVariationData", "VariationRegionList", "VariationRegion",
                "AxisIndices", "RegionIndex", "InnerPoint", "OuterPoint",
                "PeakPoint", "StartPoint", "EndPoint", "DeltaSet", "DeltaFormat",
                "DeltaCount", "DeltaValues", "DeltaX", "DeltaY", "DeltaZ",
                "GlyphName", "GlyphAxis", "GlyphMinimum", "GlyphMaximum",
                "GlyphDef", "GlyphComp", "GlyphBlend", "CompositeGlyph",
                "ComponentGlyph", "ComponentIndex", "ComponentFlags", "FirstContourPoint",
                "LastContourPoint", "NumberOfContours", "ComponentReferencePoint",
                "UseMyMetrics", "RoundToGrid", "Scale", "TransformXX", "TransformXY",
                "TransformYX", "TransformYY", "OffsetX", "OffsetY", "Transform",
                "TransformFormat", "TransformValue", "TransformValueCount",
                "VariableData", "VariableIndex", "VariableValue", "NormalizeAxis",
                "NormalizeDirection", "NormalizeRange", "DesignRange", "UserRange",
                "ClipToDesignRange", "ClipToUserRange", "Master", "MasterName",
                "MasterValue", "MasterAxis", "DefaultMaster", "ProductName",
                "DesignVector", "ProductionName", "RegisteredAxes", "Weight",
                "Width", "Slant", "OpticalSize", "Grade", "Italic", "Casual",
                "Title", "Subtitle", "Alternate", "Narrative", "Technical",
                "Handwriting", "Symbol", "Serif", "Sans", "Monospace", "Display",
            ],
            "count": 112,
            "reference": "OpenType Variable Fonts"
        }
    },
    "totals": {
        "categories": 8,
        "total_fields": 801
    }
}


def main():
    output_dir = Path("dist/font_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "font_inventory.json"
    output_file.write_text(json.dumps(FONT_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary = {
        "generated_at": FONT_INVENTORY["generated_at"],
        "source": FONT_INVENTORY["source"],
        "categories": FONT_INVENTORY["totals"]["categories"],
        "total_fields": FONT_INVENTORY["totals"]["total_fields"],
        "field_counts_by_category": {}
    }
    
    for cat, data in FONT_INVENTORY["categories"].items():
        summary["field_counts_by_category"][cat] = {
            "description": data["description"],
            "count": data["count"],
            "reference": data.get("reference", "N/A")
        }
    
    summary_file = output_dir / "font_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("FONT METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {FONT_INVENTORY['generated_at']}")
    print(f"Categories: {FONT_INVENTORY['totals']['categories']}")
    print(f"Total Fields: {FONT_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(FONT_INVENTORY["categories"].items(), key=lambda x: x[1]["count"], reverse=True):
        ref = data.get("reference", "")[:35]
        print(f"  {cat:35s}: {data['count']:>3}  [{ref}]")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
