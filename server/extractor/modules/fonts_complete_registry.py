
"""
Fonts Complete Registry
Registry of font metadata fields, including names, styles, features, and metrics.
Target: ~2,000 fields
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import struct
import os
from datetime import datetime, timezone, timedelta


NAME_ID_MAP = {
    0: "font_copyright",
    1: "font_family_name",
    2: "font_subfamily_name",
    3: "font_unique_identifier",
    4: "font_full_name",
    5: "font_version_string",
    6: "font_postscript_name",
    7: "font_trademark",
    8: "font_manufacturer",
    9: "font_designer",
    10: "font_description",
    11: "font_vendor_url",
    12: "font_designer_url",
    13: "font_license_description",
    14: "font_license_url",
    16: "font_typographic_family_name",
    17: "font_typographic_subfamily_name",
    18: "font_compatible_full_name",
    19: "font_sample_text",
    20: "font_postscript_cid_name",
    21: "font_wws_family_name",
    22: "font_wws_subfamily_name",
    23: "font_light_background_palette",
    24: "font_dark_background_palette",
    25: "font_variations_postscript_name_prefix",
}

def get_font_fields():
    fields = list(NAME_ID_MAP.values())
    fields.extend([
        "font_format_tag",
        "font_num_tables",
        "font_table_tags",
        "head_font_revision",
        "head_check_sum_adjustment",
        "head_flags",
        "head_units_per_em",
        "head_created",
        "head_modified",
        "head_x_min",
        "head_y_min",
        "head_x_max",
        "head_y_max",
        "head_mac_style",
        "head_lowest_rec_ppem",
        "head_font_direction_hint",
        "head_index_to_loc_format",
        "head_glyph_data_format",
        "hhea_ascender",
        "hhea_descender",
        "hhea_line_gap",
        "hhea_advance_width_max",
        "hhea_min_left_side_bearing",
        "hhea_min_right_side_bearing",
        "hhea_x_max_extent",
        "hhea_caret_slope_rise",
        "hhea_caret_slope_run",
        "hhea_caret_offset",
        "hhea_metric_data_format",
        "hhea_number_of_hmetrics",
        "maxp_num_glyphs",
        "post_version",
        "post_italic_angle",
        "post_underline_position",
        "post_underline_thickness",
        "post_is_fixed_pitch",
        "post_min_mem_type42",
        "post_max_mem_type42",
        "post_min_mem_type1",
        "post_max_mem_type1",
        "os2_version",
        "os2_x_avg_char_width",
        "os2_us_weight_class",
        "os2_us_width_class",
        "os2_fs_type",
        "os2_y_subscript_x_size",
        "os2_y_subscript_y_size",
        "os2_y_subscript_x_offset",
        "os2_y_subscript_y_offset",
        "os2_y_superscript_x_size",
        "os2_y_superscript_y_size",
        "os2_y_superscript_x_offset",
        "os2_y_superscript_y_offset",
        "os2_y_strikeout_size",
        "os2_y_strikeout_position",
        "os2_s_family_class",
        "os2_panose",
        "os2_unicode_range1",
        "os2_unicode_range2",
        "os2_unicode_range3",
        "os2_unicode_range4",
        "os2_ach_vend_id",
        "os2_fs_selection",
        "os2_us_first_char_index",
        "os2_us_last_char_index",
        "os2_s_typo_ascender",
        "os2_s_typo_descender",
        "os2_s_typo_line_gap",
        "os2_us_win_ascent",
        "os2_us_win_descent",
        "os2_ul_code_page_range1",
        "os2_ul_code_page_range2",
        "os2_sx_height",
        "os2_s_cap_height",
        "os2_us_default_char",
        "os2_us_break_char",
        "os2_us_max_context",
        "cmap_subtable_count",
    ])
    return fields


def get_fonts_complete_registry_field_count():
    return len(get_font_fields())


def _read_fixed_16_16(data: bytes) -> float:
    value = struct.unpack(">l", data)[0]
    return value / 65536.0


def _read_longdatetime(data: bytes) -> Optional[str]:
    if len(data) != 8:
        return None
    value = struct.unpack(">Q", data)[0]
    base = datetime(1904, 1, 1, tzinfo=timezone.utc)
    try:
        dt = base + timedelta(seconds=value)
        return dt.isoformat()
    except Exception:
        return None


def _decode_name_string(raw: bytes, platform_id: int, encoding_id: int) -> str:
    if platform_id == 3:
        return raw.decode("utf-16-be", errors="ignore").strip("\x00").strip()
    if platform_id == 1:
        return raw.decode("mac_roman", errors="ignore").strip("\x00").strip()
    return raw.decode("latin-1", errors="ignore").strip("\x00").strip()


def extract_fonts_complete_registry_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract fonts_complete_registry metadata from files'''
    result = {
        "metadata": {},
        "registry": {
            "available": False,
            "fields_extracted": 0,
            "tags": {},
        },
        "fields_extracted": 0,
        "is_valid_fonts_complete_registry": False,
        "extraction_method": "basic"
    }

    try:
        if not filepath or not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        # Try format-specific extraction
        try:
            path = Path(filepath)
            data = path.read_bytes()
            if len(data) < 12:
                result["error"] = "Invalid font file"
                return result

            scaler_type = data[0:4]
            num_tables = struct.unpack(">H", data[4:6])[0]
            table_records = {}
            offset = 12
            for _ in range(num_tables):
                if offset + 16 > len(data):
                    break
                tag = data[offset:offset + 4].decode("ascii", errors="ignore")
                checksum, table_offset, length = struct.unpack(">III", data[offset + 4:offset + 16])
                table_records[tag] = {"offset": table_offset, "length": length}
                offset += 16

            registry = result["registry"]
            registry["available"] = True

            registry["tags"]["font_format_tag"] = {"value": scaler_type.hex().upper()}
            registry["tags"]["font_num_tables"] = {"value": num_tables}
            registry["tags"]["font_table_tags"] = {"value": sorted(table_records.keys())}

            if "name" in table_records:
                name_info = table_records["name"]
                table = data[name_info["offset"]:name_info["offset"] + name_info["length"]]
                if len(table) >= 6:
                    count = struct.unpack(">H", table[2:4])[0]
                    string_offset = struct.unpack(">H", table[4:6])[0]
                    for i in range(count):
                        rec_offset = 6 + i * 12
                        if rec_offset + 12 > len(table):
                            break
                        platform_id, encoding_id, language_id, name_id, length, str_offset = struct.unpack(
                            ">HHHHHH", table[rec_offset:rec_offset + 12]
                        )
                        string_start = string_offset + str_offset
                        raw = table[string_start:string_start + length]
                        value = _decode_name_string(raw, platform_id, encoding_id)
                        key = NAME_ID_MAP.get(name_id, f"font_name_id_{name_id}")
                        if value:
                            registry["tags"].setdefault(key, {"value": []})
                            registry["tags"][key]["value"].append(value)

            if "head" in table_records:
                head = table_records["head"]
                table = data[head["offset"]:head["offset"] + head["length"]]
                if len(table) >= 54:
                    registry["tags"]["head_font_revision"] = {"value": _read_fixed_16_16(table[4:8])}
                    registry["tags"]["head_check_sum_adjustment"] = {"value": struct.unpack(">I", table[8:12])[0]}
                    registry["tags"]["head_flags"] = {"value": struct.unpack(">H", table[16:18])[0]}
                    registry["tags"]["head_units_per_em"] = {"value": struct.unpack(">H", table[18:20])[0]}
                    registry["tags"]["head_created"] = {"value": _read_longdatetime(table[20:28])}
                    registry["tags"]["head_modified"] = {"value": _read_longdatetime(table[28:36])}
                    registry["tags"]["head_x_min"] = {"value": struct.unpack(">h", table[36:38])[0]}
                    registry["tags"]["head_y_min"] = {"value": struct.unpack(">h", table[38:40])[0]}
                    registry["tags"]["head_x_max"] = {"value": struct.unpack(">h", table[40:42])[0]}
                    registry["tags"]["head_y_max"] = {"value": struct.unpack(">h", table[42:44])[0]}
                    registry["tags"]["head_mac_style"] = {"value": struct.unpack(">H", table[44:46])[0]}
                    registry["tags"]["head_lowest_rec_ppem"] = {"value": struct.unpack(">H", table[46:48])[0]}
                    registry["tags"]["head_font_direction_hint"] = {"value": struct.unpack(">h", table[48:50])[0]}
                    registry["tags"]["head_index_to_loc_format"] = {"value": struct.unpack(">h", table[50:52])[0]}
                    registry["tags"]["head_glyph_data_format"] = {"value": struct.unpack(">h", table[52:54])[0]}

            if "hhea" in table_records:
                hhea = table_records["hhea"]
                table = data[hhea["offset"]:hhea["offset"] + hhea["length"]]
                if len(table) >= 36:
                    registry["tags"]["hhea_ascender"] = {"value": struct.unpack(">h", table[4:6])[0]}
                    registry["tags"]["hhea_descender"] = {"value": struct.unpack(">h", table[6:8])[0]}
                    registry["tags"]["hhea_line_gap"] = {"value": struct.unpack(">h", table[8:10])[0]}
                    registry["tags"]["hhea_advance_width_max"] = {"value": struct.unpack(">H", table[10:12])[0]}
                    registry["tags"]["hhea_min_left_side_bearing"] = {"value": struct.unpack(">h", table[12:14])[0]}
                    registry["tags"]["hhea_min_right_side_bearing"] = {"value": struct.unpack(">h", table[14:16])[0]}
                    registry["tags"]["hhea_x_max_extent"] = {"value": struct.unpack(">h", table[16:18])[0]}
                    registry["tags"]["hhea_caret_slope_rise"] = {"value": struct.unpack(">h", table[18:20])[0]}
                    registry["tags"]["hhea_caret_slope_run"] = {"value": struct.unpack(">h", table[20:22])[0]}
                    registry["tags"]["hhea_caret_offset"] = {"value": struct.unpack(">h", table[22:24])[0]}
                    registry["tags"]["hhea_metric_data_format"] = {"value": struct.unpack(">h", table[32:34])[0]}
                    registry["tags"]["hhea_number_of_hmetrics"] = {"value": struct.unpack(">H", table[34:36])[0]}

            if "maxp" in table_records:
                maxp = table_records["maxp"]
                table = data[maxp["offset"]:maxp["offset"] + maxp["length"]]
                if len(table) >= 6:
                    registry["tags"]["maxp_num_glyphs"] = {"value": struct.unpack(">H", table[4:6])[0]}

            if "post" in table_records:
                post = table_records["post"]
                table = data[post["offset"]:post["offset"] + post["length"]]
                if len(table) >= 32:
                    registry["tags"]["post_version"] = {"value": _read_fixed_16_16(table[0:4])}
                    registry["tags"]["post_italic_angle"] = {"value": _read_fixed_16_16(table[4:8])}
                    registry["tags"]["post_underline_position"] = {"value": struct.unpack(">h", table[8:10])[0]}
                    registry["tags"]["post_underline_thickness"] = {"value": struct.unpack(">h", table[10:12])[0]}
                    registry["tags"]["post_is_fixed_pitch"] = {"value": struct.unpack(">I", table[12:16])[0]}
                    registry["tags"]["post_min_mem_type42"] = {"value": struct.unpack(">I", table[16:20])[0]}
                    registry["tags"]["post_max_mem_type42"] = {"value": struct.unpack(">I", table[20:24])[0]}
                    registry["tags"]["post_min_mem_type1"] = {"value": struct.unpack(">I", table[24:28])[0]}
                    registry["tags"]["post_max_mem_type1"] = {"value": struct.unpack(">I", table[28:32])[0]}

            if "OS/2" in table_records:
                os2 = table_records["OS/2"]
                table = data[os2["offset"]:os2["offset"] + os2["length"]]
                if len(table) >= 78:
                    registry["tags"]["os2_version"] = {"value": struct.unpack(">H", table[0:2])[0]}
                    registry["tags"]["os2_x_avg_char_width"] = {"value": struct.unpack(">h", table[2:4])[0]}
                    registry["tags"]["os2_us_weight_class"] = {"value": struct.unpack(">H", table[4:6])[0]}
                    registry["tags"]["os2_us_width_class"] = {"value": struct.unpack(">H", table[6:8])[0]}
                    registry["tags"]["os2_fs_type"] = {"value": struct.unpack(">H", table[8:10])[0]}
                    registry["tags"]["os2_y_subscript_x_size"] = {"value": struct.unpack(">h", table[10:12])[0]}
                    registry["tags"]["os2_y_subscript_y_size"] = {"value": struct.unpack(">h", table[12:14])[0]}
                    registry["tags"]["os2_y_subscript_x_offset"] = {"value": struct.unpack(">h", table[14:16])[0]}
                    registry["tags"]["os2_y_subscript_y_offset"] = {"value": struct.unpack(">h", table[16:18])[0]}
                    registry["tags"]["os2_y_superscript_x_size"] = {"value": struct.unpack(">h", table[18:20])[0]}
                    registry["tags"]["os2_y_superscript_y_size"] = {"value": struct.unpack(">h", table[20:22])[0]}
                    registry["tags"]["os2_y_superscript_x_offset"] = {"value": struct.unpack(">h", table[22:24])[0]}
                    registry["tags"]["os2_y_superscript_y_offset"] = {"value": struct.unpack(">h", table[24:26])[0]}
                    registry["tags"]["os2_y_strikeout_size"] = {"value": struct.unpack(">h", table[26:28])[0]}
                    registry["tags"]["os2_y_strikeout_position"] = {"value": struct.unpack(">h", table[28:30])[0]}
                    registry["tags"]["os2_s_family_class"] = {"value": struct.unpack(">h", table[30:32])[0]}
                    registry["tags"]["os2_panose"] = {"value": table[32:42].hex()}
                    registry["tags"]["os2_unicode_range1"] = {"value": struct.unpack(">I", table[42:46])[0]}
                    registry["tags"]["os2_unicode_range2"] = {"value": struct.unpack(">I", table[46:50])[0]}
                    registry["tags"]["os2_unicode_range3"] = {"value": struct.unpack(">I", table[50:54])[0]}
                    registry["tags"]["os2_unicode_range4"] = {"value": struct.unpack(">I", table[54:58])[0]}
                    registry["tags"]["os2_ach_vend_id"] = {"value": table[58:62].decode("latin-1", errors="ignore").strip()}
                    registry["tags"]["os2_fs_selection"] = {"value": struct.unpack(">H", table[62:64])[0]}
                    registry["tags"]["os2_us_first_char_index"] = {"value": struct.unpack(">H", table[64:66])[0]}
                    registry["tags"]["os2_us_last_char_index"] = {"value": struct.unpack(">H", table[66:68])[0]}
                    registry["tags"]["os2_s_typo_ascender"] = {"value": struct.unpack(">h", table[68:70])[0]}
                    registry["tags"]["os2_s_typo_descender"] = {"value": struct.unpack(">h", table[70:72])[0]}
                    registry["tags"]["os2_s_typo_line_gap"] = {"value": struct.unpack(">h", table[72:74])[0]}
                    registry["tags"]["os2_us_win_ascent"] = {"value": struct.unpack(">H", table[74:76])[0]}
                    registry["tags"]["os2_us_win_descent"] = {"value": struct.unpack(">H", table[76:78])[0]}
                    if len(table) >= 86:
                        registry["tags"]["os2_ul_code_page_range1"] = {"value": struct.unpack(">I", table[78:82])[0]}
                        registry["tags"]["os2_ul_code_page_range2"] = {"value": struct.unpack(">I", table[82:86])[0]}
                    if len(table) >= 96:
                        registry["tags"]["os2_sx_height"] = {"value": struct.unpack(">h", table[86:88])[0]}
                        registry["tags"]["os2_s_cap_height"] = {"value": struct.unpack(">h", table[88:90])[0]}
                        registry["tags"]["os2_us_default_char"] = {"value": struct.unpack(">H", table[90:92])[0]}
                        registry["tags"]["os2_us_break_char"] = {"value": struct.unpack(">H", table[92:94])[0]}
                        registry["tags"]["os2_us_max_context"] = {"value": struct.unpack(">H", table[94:96])[0]}

            if "cmap" in table_records:
                cmap = table_records["cmap"]
                table = data[cmap["offset"]:cmap["offset"] + cmap["length"]]
                if len(table) >= 4:
                    registry["tags"]["cmap_subtable_count"] = {"value": struct.unpack(">H", table[2:4])[0]}

            for key, value in registry["tags"].items():
                result["metadata"][key] = value.get("value")

            registry["fields_extracted"] = len(registry["tags"])
            result["fields_extracted"] = len(result["metadata"])
            result["is_valid_fonts_complete_registry"] = True
            result["extraction_method"] = "sfnt_basic"
        except Exception as e:
            result["error"] = f"fonts_complete_registry extraction failed: {str(e)[:200]}"

    except Exception as e:
        result["error"] = f"fonts_complete_registry metadata extraction failed: {str(e)[:200]}"

    return result
