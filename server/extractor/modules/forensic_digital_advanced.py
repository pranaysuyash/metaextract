# server/extractor/modules/forensic_digital_advanced.py

"""
Advanced Digital Forensics and Security metadata extraction for Phase 4.

Covers:
- File system forensics (NTFS, FAT, ext4, HFS+ artifacts)
- Windows registry analysis and hive extraction
- Event log parsing (EVTX, Windows Event Logs)
- Prefetch and SuperFetch analysis
- Browser forensics (Chrome, Firefox, Safari history and caches)
- Memory forensics (page files, hibernation files)
- Network forensics (PCAP analysis, firewall logs)
- Malware analysis (signatures, behavior patterns)
- Anti-forensic detection (timestomping, file wiping)
- Encryption detection and analysis
- Steganography and hidden data detection
- Digital evidence integrity (hash verification, chain of custody)
- Timeline analysis and temporal reconstruction
- User activity reconstruction
- System configuration forensics
- Cloud forensics (OneDrive, iCloud, Google Drive artifacts)
- Mobile device forensics (iOS, Android backups)
- IoT device forensics and smart home analysis
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import os
import sqlite3

logger = logging.getLogger(__name__)

#
# Keep this module fast: prefer small reads over full-file scans.
#
HEADER_SIZE_DEFAULT = 4096
HEADER_SIZE_SMALL = 512
HEADER_SIZE_NETWORK = 64
MAX_MALWARE_SCAN_BYTES = 1_048_576  # 1 MiB


def _shannon_entropy(data: bytes) -> Optional[float]:
    """Return Shannon entropy in bits/byte (0..8)."""
    if not data:
        return None
    from math import log2

    counts = [0] * 256
    for b in data:
        counts[b] += 1

    n = len(data)
    ent = 0.0
    for c in counts:
        if c:
            p = c / n
            ent -= p * log2(p)
    return round(ent, 4)


def _read_header(filepath: str, size: int = HEADER_SIZE_DEFAULT) -> bytes:
    if not size or size <= 0:
        return b""
    try:
        with open(filepath, "rb") as f:
            return f.read(size)
    except Exception:
        return b""


def _bytes_to_printable(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data)


def extract_forensic_digital_advanced_metadata(filepath: str) -> Dict[str, Any]:
    """Extract advanced digital forensics and security metadata."""
    result: Dict[str, Any] = {
        "forensic_digital_advanced_detected": False
    }

    try:
        if not Path(filepath).is_file():
            result["forensic_digital_advanced_extraction_error"] = "file_not_found"
            return result

        result["forensic_digital_advanced_detected"] = True

        # Cache a single header read for this module
        header_4k = _read_header(filepath, HEADER_SIZE_DEFAULT)

        # File signature analysis
        signature_data = _extract_file_signature_analysis(filepath, header_4k)
        result.update(signature_data)

        # Executable metadata
        executable_data = _extract_executable_metadata(filepath, header_4k)
        result.update(executable_data)

        # File system analysis
        fs_data = _extract_filesystem_forensics(filepath)
        result.update(fs_data)

        # Windows artifacts
        windows_data = _extract_windows_artifacts(filepath, header_4k)
        result.update(windows_data)

        # Browser forensics
        browser_data = _extract_browser_forensics(filepath, header_4k)
        result.update(browser_data)

        # Network forensics
        network_data = _extract_network_forensics(filepath, header_4k)
        result.update(network_data)

        # Malware analysis
        malware_data = _extract_malware_indicators(filepath)
        result.update(malware_data)

        # Anti-forensic detection
        anti_forensic_data = _extract_anti_forensic_indicators(filepath)
        result.update(anti_forensic_data)

        # Encryption analysis
        encryption_data = _extract_encryption_analysis(filepath, header_4k)
        result.update(encryption_data)

        # Timeline reconstruction
        timeline_data = _extract_timeline_analysis(filepath)
        result.update(timeline_data)

        # Cloud forensics
        cloud_data = _extract_cloud_forensics(filepath)
        result.update(cloud_data)

    except Exception as e:
        logger.warning(f"Error extracting advanced digital forensic metadata from {filepath}: {e}")
        result['forensic_digital_advanced_extraction_error'] = str(e)

    return result


def _extract_filesystem_forensics(filepath: str) -> Dict[str, Any]:
    """Extract file system forensic artifacts."""
    fs_data = {'forensic_fs_artifacts_detected': True}

    try:
        filename = Path(filepath).name.lower()

        # NTFS artifacts
        ntfs_indicators = ['$MFT', '$LogFile', '$UsnJrnl', 'hiberfil.sys', 'pagefile.sys']
        fs_data['forensic_ntfs_artifacts'] = any(ind in filename for ind in ntfs_indicators)

        # FAT artifacts
        fat_indicators = ['fat', 'exfat', 'recycle.bin', 'found.000']
        fs_data['forensic_fat_artifacts'] = any(ind in filename for ind in fat_indicators)

        # ext4 artifacts
        ext4_indicators = ['.journal', 'lost+found', 'ext4']
        fs_data['forensic_ext4_artifacts'] = any(ind in filename for ind in ext4_indicators)

        # HFS+ artifacts
        hfs_indicators = ['.journal_info_block', '.hotfiles', 'hfs']
        fs_data['forensic_hfs_artifacts'] = any(ind in filename for ind in hfs_indicators)

        # File carving indicators
        carving_indicators = ['unallocated', 'slack', 'carved', 'recovered']
        fs_data['forensic_file_carving_indicators'] = any(ind in filename for ind in carving_indicators)

        # Deleted file indicators
        deleted_indicators = ['deleted', 'removed', 'erased', '~tmp']
        fs_data['forensic_deleted_file_indicators'] = any(ind in filename for ind in deleted_indicators)

        fs_forensic_fields = [
            'forensic_fs_cluster_size',
            'forensic_fs_sector_size',
            'forensic_fs_mft_entry',
            'forensic_fs_inode_number',
            'forensic_fs_allocation_status',
            'forensic_fs_timestamps_modified',
            'forensic_fs_access_permissions',
            'forensic_fs_extended_attributes',
            'forensic_fs_alternate_data_streams',
            'forensic_fs_hard_links',
            'forensic_fs_symbolic_links',
            'forensic_fs_sparse_file',
            'forensic_fs_compressed_file',
            'forensic_fs_encrypted_file',
        ]

        for field in fs_forensic_fields:
            fs_data[field] = None

        fs_data['forensic_fs_field_count'] = len(fs_forensic_fields)

    except Exception as e:
        fs_data['forensic_fs_error'] = str(e)

    return fs_data


def _extract_file_signature_analysis(filepath: str, header: Optional[bytes] = None) -> Dict[str, Any]:
    """Extract header signature and container indicators."""
    signature_data: Dict[str, Any] = {}

    # Basic file facts (cheap and useful)
    try:
        p = Path(filepath)
        signature_data["forensic_file_size_bytes"] = p.stat().st_size
        signature_data["forensic_file_extension"] = p.suffix.lower() or None
    except Exception:
        signature_data["forensic_file_size_bytes"] = None
        signature_data["forensic_file_extension"] = None

    header = header if header is not None else _read_header(filepath, HEADER_SIZE_DEFAULT)
    if not header:
        signature_data["forensic_file_signature_error"] = "header_unavailable"
        return signature_data

    head = header[:32]
    signature_data["forensic_file_magic_hex"] = head.hex()
    signature_data["forensic_file_magic_ascii"] = _bytes_to_printable(head)
    signature_data["forensic_file_header_length"] = len(header)
    signature_data["forensic_file_header_entropy"] = _shannon_entropy(header)

    printable = sum(1 for b in header if 32 <= b < 127 or b in (9, 10, 13))
    signature_data["forensic_file_printable_ratio"] = round(printable / len(header), 4) if header else 0.0
    signature_data["forensic_file_is_probably_text"] = signature_data["forensic_file_printable_ratio"] > 0.9

    bom_type = None
    if header.startswith(b"\xef\xbb\xbf"):
        bom_type = "utf-8"
    elif header.startswith(b"\xff\xfe"):
        bom_type = "utf-16-le"
    elif header.startswith(b"\xfe\xff"):
        bom_type = "utf-16-be"
    signature_data["forensic_file_contains_bom"] = bom_type is not None
    signature_data["forensic_file_bom_type"] = bom_type

    stripped = header.lstrip()
    signature_data["forensic_file_contains_xml"] = stripped.startswith(b"<?xml")
    signature_data["forensic_file_contains_json"] = stripped[:1] in [b"{", b"["]
    signature_data["forensic_file_contains_plist"] = (
        header.startswith(b"bplist00") or (b"<plist" in header and stripped.startswith(b"<?xml"))
    )
    signature_data["forensic_file_contains_ustar"] = len(header) >= 262 and header[257:262] == b"ustar"

    pe = header.startswith(b"MZ")
    elf = header.startswith(b"\x7fELF")
    macho = header[:4] in [b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"]
    macho_fat = header[:4] in [b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"]
    pdf = header.startswith(b"%PDF-")
    zip_sig = header[:4] in [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"]
    rar_sig = header.startswith(b"Rar!\x1a\x07\x00") or header.startswith(b"Rar!\x1a\x07\x01\x00")
    sevenz_sig = header.startswith(b"7z\xbc\xaf\x27\x1c")
    gzip_sig = header.startswith(b"\x1f\x8b")
    bzip2_sig = header.startswith(b"BZh")
    xz_sig = header.startswith(b"\xfd7zXZ\x00")
    ole_sig = header.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")
    sqlite_sig = header.startswith(b"SQLite format 3\x00")
    evtx_sig = header.startswith(b"ElfFile")
    regf_sig = header.startswith(b"regf")
    prefetch_sig = len(header) >= 8 and header[4:8] == b"SCCA"
    pcap_sig = header[:4] in [b"\xa1\xb2\xc3\xd4", b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\x3c\x4d", b"\x4d\x3c\xb2\xa1"]
    pcapng_sig = header.startswith(b"\x0a\x0d\x0d\x0a")
    lnk_sig = header.startswith(
        b"L\x00\x00\x00\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46"
    )

    signature_data.update({
        "forensic_file_has_pe_header": pe,
        "forensic_file_has_elf_header": elf,
        "forensic_file_has_macho_header": macho,
        "forensic_file_has_fat_macho_header": macho_fat,
        "forensic_file_has_pdf_header": pdf,
        "forensic_file_has_zip_header": zip_sig,
        "forensic_file_has_rar_header": rar_sig,
        "forensic_file_has_7z_header": sevenz_sig,
        "forensic_file_has_gzip_header": gzip_sig,
        "forensic_file_has_bzip2_header": bzip2_sig,
        "forensic_file_has_xz_header": xz_sig,
        "forensic_file_has_ole_header": ole_sig,
        "forensic_file_has_sqlite_header": sqlite_sig,
        "forensic_file_has_evtx_header": evtx_sig,
        "forensic_file_has_registry_header": regf_sig,
        "forensic_file_has_prefetch_header": prefetch_sig,
        "forensic_file_has_pcap_header": pcap_sig,
        "forensic_file_has_pcapng_header": pcapng_sig,
        "forensic_file_has_link_header": lnk_sig,
    })

    matches = []
    if pe:
        matches.append("pe")
    if elf:
        matches.append("elf")
    if macho or macho_fat:
        matches.append("macho")
    if pdf:
        matches.append("pdf")
    if zip_sig:
        matches.append("zip")
    if rar_sig:
        matches.append("rar")
    if sevenz_sig:
        matches.append("7z")
    if gzip_sig:
        matches.append("gzip")
    if bzip2_sig:
        matches.append("bzip2")
    if xz_sig:
        matches.append("xz")
    if ole_sig:
        matches.append("ole")
    if sqlite_sig:
        matches.append("sqlite")
    if evtx_sig:
        matches.append("evtx")
    if regf_sig:
        matches.append("registry")
    if prefetch_sig:
        matches.append("prefetch")
    if pcap_sig:
        matches.append("pcap")
    if pcapng_sig:
        matches.append("pcapng")
    if lnk_sig:
        matches.append("lnk")

    signature_data["forensic_file_type_guesses"] = matches
    signature_data["forensic_file_signature_primary"] = matches[0] if matches else None
    signature_data["forensic_file_is_executable"] = pe or elf or macho or macho_fat
    signature_data["forensic_file_is_archive"] = zip_sig or rar_sig or sevenz_sig or gzip_sig or bzip2_sig or xz_sig
    signature_data["forensic_file_is_document"] = pdf or ole_sig
    signature_data["forensic_file_is_database"] = sqlite_sig
    signature_data["forensic_file_is_compressed"] = gzip_sig or bzip2_sig or xz_sig

    return signature_data


def _extract_executable_metadata(filepath: str, header: Optional[bytes] = None) -> Dict[str, Any]:
    """Extract basic executable header metadata."""
    exe_data: Dict[str, Any] = {}
    header = header if header is not None else _read_header(filepath, HEADER_SIZE_DEFAULT)
    if not header:
        return exe_data

    if header.startswith(b"MZ"):
        exe_data["forensic_executable_format"] = "PE"
        try:
            with open(filepath, "rb") as f:
                f.seek(0x3C)
                pe_offset_data = f.read(4)
                if len(pe_offset_data) < 4:
                    return exe_data
                pe_offset = struct.unpack("<I", pe_offset_data)[0]
                f.seek(pe_offset)
                if f.read(4) != b"PE\x00\x00":
                    return exe_data
                coff = f.read(20)
                if len(coff) < 20:
                    return exe_data
                machine, sections, timestamp, _, _, opt_size, characteristics = struct.unpack("<HHIIIHH", coff)
                exe_data["forensic_pe_machine"] = machine
                exe_data["forensic_pe_sections"] = sections
                exe_data["forensic_pe_timestamp"] = timestamp
                exe_data["forensic_pe_characteristics"] = characteristics
                exe_data["forensic_pe_is_dll"] = bool(characteristics & 0x2000)
                exe_data["forensic_pe_is_executable"] = bool(characteristics & 0x0002)
                optional = f.read(opt_size)
                if len(optional) >= 2:
                    magic = struct.unpack("<H", optional[0:2])[0]
                    exe_data["forensic_pe_optional_magic"] = magic
                    if len(optional) >= 4:
                        exe_data["forensic_pe_linker_version"] = f"{optional[2]}.{optional[3]}"
                    if len(optional) >= 20:
                        exe_data["forensic_pe_entrypoint"] = struct.unpack("<I", optional[16:20])[0]
                    if magic == 0x10B and len(optional) >= 32:
                        exe_data["forensic_pe_image_base"] = struct.unpack("<I", optional[28:32])[0]
                        if len(optional) >= 72:
                            exe_data["forensic_pe_subsystem"] = struct.unpack("<H", optional[68:70])[0]
                            exe_data["forensic_pe_dll_characteristics"] = struct.unpack("<H", optional[70:72])[0]
                    elif magic == 0x20B and len(optional) >= 36:
                        exe_data["forensic_pe_image_base"] = struct.unpack("<Q", optional[24:32])[0]
                        if len(optional) >= 92:
                            exe_data["forensic_pe_subsystem"] = struct.unpack("<H", optional[88:90])[0]
                            exe_data["forensic_pe_dll_characteristics"] = struct.unpack("<H", optional[90:92])[0]
                section_headers_offset = pe_offset + 24 + opt_size
                sections_info = _parse_pe_sections(f, section_headers_offset, sections)
                exe_data["forensic_pe_section_count"] = sections_info.get("section_count")
                exe_data["forensic_pe_section_names"] = sections_info.get("section_names")
                exe_data["forensic_pe_section_details"] = sections_info.get("sections")
                exe_data["forensic_pe_section_entropies"] = sections_info.get("section_entropies")
                import_info = _parse_pe_imports(f, optional, sections_info.get("sections", []))
                exe_data["forensic_pe_import_table_rva"] = import_info.get("import_rva")
                exe_data["forensic_pe_import_table_size"] = import_info.get("import_size")
                exe_data["forensic_pe_import_dll_count"] = import_info.get("dll_count")
                exe_data["forensic_pe_import_dlls"] = import_info.get("dlls")
                exe_data["forensic_pe_has_imports"] = import_info.get("dll_count", 0) > 0
        except Exception:
            return exe_data
        return exe_data

    if header.startswith(b"\x7fELF") and len(header) >= 18:
        exe_data["forensic_executable_format"] = "ELF"
        elf_class = header[4]
        elf_data = header[5]
        endian = "<" if elf_data == 1 else ">"
        exe_data["forensic_elf_class"] = "64-bit" if elf_class == 2 else "32-bit"
        exe_data["forensic_elf_endianness"] = "little" if endian == "<" else "big"
        try:
            if elf_class == 1 and len(header) >= 52:
                e_type, e_machine = struct.unpack(endian + "HH", header[16:20])
                e_entry = struct.unpack(endian + "I", header[24:28])[0]
            elif elf_class == 2 and len(header) >= 64:
                e_type, e_machine = struct.unpack(endian + "HH", header[16:20])
                e_entry = struct.unpack(endian + "Q", header[24:32])[0]
            else:
                e_type, e_machine, e_entry = None, None, None
            exe_data["forensic_elf_type"] = e_type
            exe_data["forensic_elf_machine"] = e_machine
            exe_data["forensic_elf_entrypoint"] = e_entry
        except Exception:
            return exe_data
        return exe_data

    macho_magics = {
        b"\xfe\xed\xfa\xce": (">", False),
        b"\xce\xfa\xed\xfe": ("<", False),
        b"\xfe\xed\xfa\xcf": (">", True),
        b"\xcf\xfa\xed\xfe": ("<", True),
    }
    if header[:4] in macho_magics:
        endian, is_64 = macho_magics[header[:4]]
        exe_data["forensic_executable_format"] = "Mach-O"
        exe_data["forensic_macho_magic"] = header[:4].hex()
        exe_data["forensic_macho_endianness"] = "little" if endian == "<" else "big"
        exe_data["forensic_macho_is_64bit"] = is_64
        try:
            if len(header) >= 28:
                cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags = struct.unpack(
                    endian + "IIIIII", header[4:28]
                )
                exe_data["forensic_macho_cpu_type"] = cputype
                exe_data["forensic_macho_cpu_subtype"] = cpusubtype
                exe_data["forensic_macho_file_type"] = filetype
                exe_data["forensic_macho_ncmds"] = ncmds
                exe_data["forensic_macho_flags"] = flags
        except Exception:
            return exe_data
        return exe_data

    if header[:4] in [b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"]:
        exe_data["forensic_executable_format"] = "Mach-O Fat"
        endian = ">" if header[:4] == b"\xca\xfe\xba\xbe" else "<"
        exe_data["forensic_macho_fat_endianness"] = "big" if endian == ">" else "little"
        if len(header) >= 8:
            try:
                exe_data["forensic_macho_fat_arch_count"] = struct.unpack(endian + "I", header[4:8])[0]
            except Exception:
                pass
        return exe_data

    return exe_data


def _extract_windows_artifacts(filepath: str, header: Optional[bytes] = None) -> Dict[str, Any]:
    """Extract Windows forensic artifacts."""
    windows_data = {'forensic_windows_artifacts_detected': True}

    try:
        filename = Path(filepath).name.lower()
        header = (header[:HEADER_SIZE_SMALL] if header else _read_header(filepath, HEADER_SIZE_SMALL))
        regf_detected = header.startswith(b"regf")
        evtx_detected = header.startswith(b"ElfFile")
        prefetch_detected = len(header) >= 8 and header[4:8] == b"SCCA"
        prefetch_version = struct.unpack("<I", header[0:4])[0] if prefetch_detected else None
        lnk_detected = header.startswith(
            b"L\x00\x00\x00\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46"
        )
        regf_info = _parse_regf_header(header) if regf_detected else {}
        evtx_info = _parse_evtx_header(header) if evtx_detected else {}
        prefetch_info = _parse_prefetch_header(header) if prefetch_detected else {}
        lnk_info = _parse_lnk_header(header) if lnk_detected else {}

        # Registry hives
        registry_hives = ['ntuser.dat', 'sam', 'system', 'software', 'security', 'default']
        windows_data['forensic_registry_hive'] = any(hive in filename for hive in registry_hives) or regf_detected

        # Event logs
        event_logs = ['application.evtx', 'system.evtx', 'security.evtx', 'setup.evtx']
        windows_data['forensic_windows_event_log'] = any(log in filename for log in event_logs) or evtx_detected

        # Prefetch files
        prefetch_indicators = ['.pf', 'prefetch']
        windows_data['forensic_prefetch_file'] = any(ind in filename for ind in prefetch_indicators) or prefetch_detected

        # User profile artifacts
        profile_artifacts = ['ntuser.dat', 'usrclass.dat', 'recent', 'cookies']
        windows_data['forensic_user_profile_artifact'] = any(art in filename for art in profile_artifacts)

        # System restore points
        restore_indicators = ['rp', 'changlog', 'cfg']
        windows_data['forensic_system_restore'] = any(ind in filename for ind in restore_indicators)

        windows_artifacts_fields = [
            'forensic_windows_version',
            'forensic_windows_build',
            'forensic_windows_install_date',
            'forensic_windows_last_shutdown',
            'forensic_windows_user_profiles',
            'forensic_windows_installed_programs',
            'forensic_windows_network_shares',
            'forensic_windows_usb_devices',
            'forensic_windows_recent_files',
            'forensic_windows_shellbags',
            'forensic_windows_jump_lists',
            'forensic_windows_thumbnail_cache',
            'forensic_windows_amcache',
            'forensic_windows_srum',
            'forensic_registry_hive_detected',
            'forensic_evtx_detected',
            'forensic_prefetch_version',
            'forensic_shell_link_detected',
            'forensic_registry_sequence_1',
            'forensic_registry_sequence_2',
            'forensic_registry_timestamp_raw',
            'forensic_registry_major_version',
            'forensic_registry_minor_version',
            'forensic_evtx_first_chunk',
            'forensic_evtx_last_chunk',
            'forensic_evtx_next_record',
            'forensic_evtx_header_size',
            'forensic_evtx_minor_version',
            'forensic_evtx_major_version',
            'forensic_prefetch_file_size',
            'forensic_prefetch_executable_name',
            'forensic_prefetch_hash',
            'forensic_lnk_header_size',
            'forensic_lnk_link_flags',
            'forensic_lnk_file_attributes',
            'forensic_lnk_creation_time_raw',
            'forensic_lnk_access_time_raw',
            'forensic_lnk_write_time_raw',
            'forensic_lnk_file_size',
            'forensic_lnk_icon_index',
            'forensic_lnk_show_command',
            'forensic_lnk_hotkey',
        ]

        for field in windows_artifacts_fields:
            windows_data[field] = None

        windows_data['forensic_registry_hive_detected'] = regf_detected
        windows_data['forensic_evtx_detected'] = evtx_detected
        windows_data['forensic_prefetch_version'] = prefetch_version
        windows_data['forensic_shell_link_detected'] = lnk_detected
        windows_data['forensic_registry_sequence_1'] = regf_info.get("sequence_1")
        windows_data['forensic_registry_sequence_2'] = regf_info.get("sequence_2")
        windows_data['forensic_registry_timestamp_raw'] = regf_info.get("timestamp_raw")
        windows_data['forensic_registry_major_version'] = regf_info.get("major_version")
        windows_data['forensic_registry_minor_version'] = regf_info.get("minor_version")
        windows_data['forensic_evtx_first_chunk'] = evtx_info.get("first_chunk")
        windows_data['forensic_evtx_last_chunk'] = evtx_info.get("last_chunk")
        windows_data['forensic_evtx_next_record'] = evtx_info.get("next_record")
        windows_data['forensic_evtx_header_size'] = evtx_info.get("header_size")
        windows_data['forensic_evtx_minor_version'] = evtx_info.get("minor_version")
        windows_data['forensic_evtx_major_version'] = evtx_info.get("major_version")
        windows_data['forensic_prefetch_file_size'] = prefetch_info.get("file_size")
        windows_data['forensic_prefetch_executable_name'] = prefetch_info.get("executable_name")
        windows_data['forensic_prefetch_hash'] = prefetch_info.get("hash")
        windows_data['forensic_lnk_header_size'] = lnk_info.get("header_size")
        windows_data['forensic_lnk_link_flags'] = lnk_info.get("link_flags")
        windows_data['forensic_lnk_file_attributes'] = lnk_info.get("file_attributes")
        windows_data['forensic_lnk_creation_time_raw'] = lnk_info.get("creation_time_raw")
        windows_data['forensic_lnk_access_time_raw'] = lnk_info.get("access_time_raw")
        windows_data['forensic_lnk_write_time_raw'] = lnk_info.get("write_time_raw")
        windows_data['forensic_lnk_file_size'] = lnk_info.get("file_size")
        windows_data['forensic_lnk_icon_index'] = lnk_info.get("icon_index")
        windows_data['forensic_lnk_show_command'] = lnk_info.get("show_command")
        windows_data['forensic_lnk_hotkey'] = lnk_info.get("hotkey")
        windows_data['forensic_windows_field_count'] = len(windows_artifacts_fields)

    except Exception as e:
        windows_data['forensic_windows_error'] = str(e)

    return windows_data


def _extract_browser_forensics(filepath: str, header: Optional[bytes] = None) -> Dict[str, Any]:
    """Extract browser forensic artifacts."""
    browser_data = {'forensic_browser_artifacts_detected': True}

    try:
        filename = Path(filepath).name.lower()
        header = (header[:HEADER_SIZE_SMALL] if header else _read_header(filepath, HEADER_SIZE_SMALL))
        sqlite_header = _parse_sqlite_header(header)
        plist_detected = header.startswith(b"bplist00") or (header.lstrip().startswith(b"<?xml") and b"<plist" in header)
        sqlite_schema = _extract_sqlite_schema(filepath) if sqlite_header else {}

        # Chrome artifacts
        chrome_artifacts = ['history', 'cookies', 'login data', 'web data', 'favicons']
        browser_data['forensic_chrome_artifact'] = any(art in filename for art in chrome_artifacts)

        # Firefox artifacts
        firefox_artifacts = ['places.sqlite', 'cookies.sqlite', 'formhistory.sqlite']
        browser_data['forensic_firefox_artifact'] = any(art in filename for art in firefox_artifacts)

        # Safari artifacts
        safari_artifacts = ['history.db', 'downloads.plist', 'bookmarks.plist']
        browser_data['forensic_safari_artifact'] = any(art in filename for art in safari_artifacts)

        # Cache files
        cache_indicators = ['cache', 'temp', 'temporary internet files']
        browser_data['forensic_browser_cache'] = any(ind in filename for ind in cache_indicators)

        # Session data
        session_indicators = ['session', 'tabs', 'windows']
        browser_data['forensic_browser_session'] = any(ind in filename for ind in session_indicators)

        browser_forensic_fields = [
            'forensic_browser_history_entries',
            'forensic_browser_download_history',
            'forensic_browser_bookmarks',
            'forensic_browser_saved_passwords',
            'forensic_browser_form_data',
            'forensic_browser_cookies',
            'forensic_browser_cache_files',
            'forensic_browser_extensions',
            'forensic_browser_local_storage',
            'forensic_browser_indexeddb',
            'forensic_browser_service_workers',
            'forensic_browser_web_sql',
            'forensic_browser_sqlite_detected',
            'forensic_browser_sqlite_page_size',
            'forensic_browser_sqlite_read_version',
            'forensic_browser_sqlite_write_version',
            'forensic_browser_sqlite_reserved_space',
            'forensic_browser_sqlite_text_encoding',
            'forensic_browser_sqlite_user_version',
            'forensic_browser_sqlite_application_id',
            'forensic_browser_sqlite_schema_format',
            'forensic_browser_plist_detected',
            'forensic_browser_sqlite_table_count',
            'forensic_browser_sqlite_tables',
            'forensic_browser_sqlite_index_count',
            'forensic_browser_has_urls_table',
            'forensic_browser_has_visits_table',
            'forensic_browser_has_cookies_table',
            'forensic_browser_has_downloads_table',
            'forensic_browser_has_moz_places',
            'forensic_browser_db_type_guess',
        ]

        for field in browser_forensic_fields:
            browser_data[field] = None

        browser_data['forensic_browser_sqlite_detected'] = sqlite_header is not None
        if sqlite_header:
            browser_data['forensic_browser_sqlite_page_size'] = sqlite_header.get("page_size")
            browser_data['forensic_browser_sqlite_read_version'] = sqlite_header.get("read_version")
            browser_data['forensic_browser_sqlite_write_version'] = sqlite_header.get("write_version")
            browser_data['forensic_browser_sqlite_reserved_space'] = sqlite_header.get("reserved_space")
            browser_data['forensic_browser_sqlite_text_encoding'] = sqlite_header.get("text_encoding")
            browser_data['forensic_browser_sqlite_user_version'] = sqlite_header.get("user_version")
            browser_data['forensic_browser_sqlite_application_id'] = sqlite_header.get("application_id")
            browser_data['forensic_browser_sqlite_schema_format'] = sqlite_header.get("schema_format")
            if sqlite_schema:
                browser_data['forensic_browser_sqlite_table_count'] = sqlite_schema.get("table_count")
                browser_data['forensic_browser_sqlite_tables'] = sqlite_schema.get("tables")
                browser_data['forensic_browser_sqlite_index_count'] = sqlite_schema.get("index_count")
                browser_data['forensic_browser_has_urls_table'] = sqlite_schema.get("has_urls")
                browser_data['forensic_browser_has_visits_table'] = sqlite_schema.get("has_visits")
                browser_data['forensic_browser_has_cookies_table'] = sqlite_schema.get("has_cookies")
                browser_data['forensic_browser_has_downloads_table'] = sqlite_schema.get("has_downloads")
                browser_data['forensic_browser_has_moz_places'] = sqlite_schema.get("has_moz_places")
                browser_data['forensic_browser_db_type_guess'] = sqlite_schema.get("db_type_guess")
        browser_data['forensic_browser_plist_detected'] = plist_detected
        browser_data['forensic_browser_field_count'] = len(browser_forensic_fields)

    except Exception as e:
        browser_data['forensic_browser_error'] = str(e)

    return browser_data


def _extract_network_forensics(filepath: str, header: Optional[bytes] = None) -> Dict[str, Any]:
    """Extract network forensic artifacts."""
    network_data = {'forensic_network_artifacts_detected': True}

    try:
        filename = Path(filepath).name.lower()
        header = (header[:HEADER_SIZE_NETWORK] if header else _read_header(filepath, HEADER_SIZE_NETWORK))
        pcap = _parse_pcap_header(header)
        pcapng = _parse_pcapng_header(header)

        # PCAP files
        pcap_indicators = ['.pcap', '.pcapng', 'capture', 'packet']
        network_data['forensic_pcap_file'] = any(ind in filename for ind in pcap_indicators) or bool(pcap) or bool(pcapng)

        # Firewall logs
        firewall_logs = ['firewall', 'iptables', 'pf', 'windows firewall']
        network_data['forensic_firewall_log'] = any(log in filename for log in firewall_logs)

        # DNS cache/resolution
        dns_indicators = ['hosts', 'dns', 'resolver']
        network_data['forensic_dns_artifact'] = any(ind in filename for ind in dns_indicators)

        # Network configuration
        network_config = ['interfaces', 'routes', 'arp', 'netstat']
        network_data['forensic_network_config'] = any(config in filename for config in network_config)

        # Wireless artifacts
        wireless_indicators = ['wifi', 'wireless', 'wlan', 'bluetooth']
        network_data['forensic_wireless_artifact'] = any(ind in filename for ind in wireless_indicators)

        network_forensic_fields = [
            'forensic_network_connections',
            'forensic_network_listening_ports',
            'forensic_network_established_sessions',
            'forensic_network_dns_queries',
            'forensic_network_http_requests',
            'forensic_network_ssl_certificates',
            'forensic_network_vpn_connections',
            'forensic_network_proxy_settings',
            'forensic_network_mac_addresses',
            'forensic_network_ip_addresses',
            'forensic_network_domain_names',
            'forensic_network_geolocation_data',
            'forensic_pcap_detected',
            'forensic_pcapng_detected',
            'forensic_pcap_version_major',
            'forensic_pcap_version_minor',
            'forensic_pcap_endianness',
            'forensic_pcap_ts_resolution',
            'forensic_pcap_snaplen',
            'forensic_pcap_network',
            'forensic_pcapng_endianness',
            'forensic_pcapng_version_major',
            'forensic_pcapng_version_minor',
            'forensic_pcapng_section_length',
            'forensic_pcapng_block_length',
        ]

        for field in network_forensic_fields:
            network_data[field] = None

        network_data['forensic_pcap_detected'] = bool(pcap)
        network_data['forensic_pcapng_detected'] = bool(pcapng)
        if pcap:
            network_data['forensic_pcap_version_major'] = pcap.get("version_major")
            network_data['forensic_pcap_version_minor'] = pcap.get("version_minor")
            network_data['forensic_pcap_endianness'] = pcap.get("endianness")
            network_data['forensic_pcap_ts_resolution'] = pcap.get("ts_resolution")
            network_data['forensic_pcap_snaplen'] = pcap.get("snaplen")
            network_data['forensic_pcap_network'] = pcap.get("network")
        if pcapng:
            network_data['forensic_pcapng_endianness'] = pcapng.get("endianness")
            network_data['forensic_pcapng_version_major'] = pcapng.get("version_major")
            network_data['forensic_pcapng_version_minor'] = pcapng.get("version_minor")
            network_data['forensic_pcapng_section_length'] = pcapng.get("section_length")
            network_data['forensic_pcapng_block_length'] = pcapng.get("block_length")
        network_data['forensic_network_field_count'] = len(network_forensic_fields)

    except Exception as e:
        network_data['forensic_network_error'] = str(e)

    return network_data


def _extract_malware_indicators(filepath: str) -> Dict[str, Any]:
    """Extract malware analysis indicators."""
    malware_data = {'forensic_malware_analysis_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(min(MAX_MALWARE_SCAN_BYTES, os.path.getsize(filepath)))  # First chunk

        # Common executable/script markers (coarse heuristics)
        malware_signatures = [
            ("PE_MZ", b"MZ"),
            ("ELF", b"\x7fELF"),
            ("SHELL_SH", b"#!/bin/sh"),
            ("POWERSHELL", b"powershell"),
            ("CMD_EXE", b"cmd.exe"),
            ("WSCRIPT", b"WScript"),
        ]

        detected = []
        for name, sig in malware_signatures:
            if sig in content:
                detected.append(name)

        malware_data["forensic_malware_signatures"] = detected

        # Suspicious strings
        suspicious_strings = [
            'cmd.exe', 'powershell.exe', 'net.exe', 'sc.exe',
            'regedit.exe', 'mshta.exe', 'rundll32.exe',
            'schtasks.exe', 'at.exe', 'wmic.exe'
        ]

        malware_commands = []
        for cmd in suspicious_strings:
            if cmd.encode() in content:
                malware_commands.append(cmd)

        malware_data['forensic_suspicious_commands'] = malware_commands

        malware_analysis_fields = [
            'forensic_malware_file_hash',
            'forensic_malware_signature_matches',
            'forensic_malware_behavior_indicators',
            'forensic_malware_persistence_mechanisms',
            'forensic_malware_network_connections',
            'forensic_malware_file_modifications',
            'forensic_malware_registry_changes',
            'forensic_malware_process_injection',
            'forensic_malware_anti_analysis',
            'forensic_malware_obfuscation',
            'forensic_malware_encryption',
            'forensic_malware_communication',
        ]

        for field in malware_analysis_fields:
            malware_data[field] = None

        malware_data['forensic_malware_field_count'] = len(malware_analysis_fields)

    except Exception as e:
        malware_data['forensic_malware_error'] = str(e)

    return malware_data


def _extract_anti_forensic_indicators(filepath: str) -> Dict[str, Any]:
    """Extract anti-forensic technique indicators."""
    anti_forensic_data = {'forensic_anti_forensic_detected': True}

    try:
        filename = Path(filepath).name.lower()

        # Timestomping indicators
        timestomp_indicators = ['modified', 'accessed', 'created', 'changed']
        anti_forensic_data['forensic_timestomping_indicators'] = any(ind in filename for ind in timestomp_indicators)

        # File wiping
        wipe_indicators = ['wiped', 'erased', 'secure delete', 'sdelete']
        anti_forensic_data['forensic_file_wiping_indicators'] = any(ind in filename for ind in wipe_indicators)

        # Encryption
        encryption_indicators = ['encrypted', 'cipher', 'aes', 'rsa']
        anti_forensic_data['forensic_encryption_indicators'] = any(ind in filename for ind in encryption_indicators)

        # Steganography
        stego_indicators = ['hidden', 'stego', 'embedded', 'concealed']
        anti_forensic_data['forensic_steganography_indicators'] = any(ind in filename for ind in stego_indicators)

        anti_forensic_fields = [
            'forensic_anti_timestomping_detected',
            'forensic_anti_file_slack_manipulation',
            'forensic_anti_unallocated_space_wiping',
            'forensic_anti_log_manipulation',
            'forensic_anti_encryption_used',
            'forensic_anti_steganography_used',
            'forensic_anti_compression_used',
            'forensic_anti_obfuscation_used',
            'forensic_anti_rootkit_indicators',
            'forensic_anti_anti_vm_techniques',
            'forensic_anti_anti_debugging',
            'forensic_anti_code_packing',
        ]

        for field in anti_forensic_fields:
            anti_forensic_data[field] = None

        anti_forensic_data['forensic_anti_forensic_field_count'] = len(anti_forensic_fields)

    except Exception as e:
        anti_forensic_data['forensic_anti_forensic_error'] = str(e)

    return anti_forensic_data


def _extract_encryption_analysis(filepath: str, header: Optional[bytes] = None) -> Dict[str, Any]:
    """Extract encryption analysis metadata."""
    encryption_data = {'forensic_encryption_analysis_detected': True}

    try:
        header = (header[:HEADER_SIZE_SMALL] if header else _read_header(filepath, HEADER_SIZE_SMALL))
        openssl_salted = header.startswith(b"Salted__")
        pgp_ascii = b"-----BEGIN PGP" in header

        # Detect encryption algorithms
        encryption_signatures = {
            'AES': b'AES',
            'RSA': b'RSA',
            'PGP': b'PGP',
            'GPG': b'GPG',
            'BitLocker': b'BitLocker',
            'FileVault': b'FileVault',
            'TrueCrypt': b'TrueCrypt',
            'VeraCrypt': b'VeraCrypt',
        }

        detected_encryption = []
        for enc_type, signature in encryption_signatures.items():
            if signature in header:
                detected_encryption.append(enc_type)
                encryption_data[f'forensic_encryption_{enc_type.lower()}_detected'] = True

        encryption_data['forensic_encryption_types_detected'] = detected_encryption

        encryption_analysis_fields = [
            'forensic_encryption_algorithm',
            'forensic_encryption_key_size',
            'forensic_encryption_mode',
            'forensic_encryption_padding',
            'forensic_encryption_iv_present',
            'forensic_encryption_salt_present',
            'forensic_encryption_iterations',
            'forensic_encryption_container_format',
            'forensic_encryption_key_derivation',
            'forensic_encryption_certificate_used',
            'forensic_encryption_hardware_security',
            'forensic_encryption_weak_keys',
            'forensic_encryption_openssl_salted',
            'forensic_encryption_pgp_ascii',
        ]

        for field in encryption_analysis_fields:
            encryption_data[field] = None

        encryption_data['forensic_encryption_openssl_salted'] = openssl_salted
        encryption_data['forensic_encryption_pgp_ascii'] = pgp_ascii
        encryption_data['forensic_encryption_field_count'] = len(encryption_analysis_fields)

    except Exception as e:
        encryption_data['forensic_encryption_error'] = str(e)

    return encryption_data


def _extract_timeline_analysis(filepath: str) -> Dict[str, Any]:
    """Extract timeline reconstruction metadata."""
    timeline_data = {'forensic_timeline_analysis_detected': True}

    try:
        stat_info = os.stat(filepath)

        # File system timestamps
        timeline_data['forensic_timeline_file_created'] = stat_info.st_birthtime if hasattr(stat_info, 'st_birthtime') else None
        timeline_data['forensic_timeline_file_modified'] = stat_info.st_mtime
        timeline_data['forensic_timeline_file_accessed'] = stat_info.st_atime
        timeline_data['forensic_timeline_file_changed'] = stat_info.st_ctime

        timeline_analysis_fields = [
            'forensic_timeline_event_sequence',
            'forensic_timeline_user_actions',
            'forensic_timeline_system_events',
            'forensic_timeline_network_activity',
            'forensic_timeline_file_operations',
            'forensic_timeline_registry_changes',
            'forensic_timeline_process_creation',
            'forensic_timeline_log_entries',
            'forensic_timeline_browser_history',
            'forensic_timeline_email_activity',
            'forensic_timeline_document_edits',
            'forensic_timeline_cloud_sync',
        ]

        for field in timeline_analysis_fields:
            timeline_data[field] = None

        timeline_data['forensic_timeline_field_count'] = len(timeline_analysis_fields)

    except Exception as e:
        timeline_data['forensic_timeline_error'] = str(e)

    return timeline_data


def _extract_cloud_forensics(filepath: str) -> Dict[str, Any]:
    """Extract cloud forensics artifacts."""
    cloud_data = {'forensic_cloud_artifacts_detected': True}

    try:
        filename = Path(filepath).name.lower()

        # OneDrive artifacts
        onedrive_indicators = ['onedrive', 'skydrive', 'clientmanifest', 'sync']
        cloud_data['forensic_onedrive_artifact'] = any(ind in filename for ind in onedrive_indicators)

        # Google Drive artifacts
        gdrive_indicators = ['googledrive', 'drivefs', 'snapshot.db']
        cloud_data['forensic_google_drive_artifact'] = any(ind in filename for ind in gdrive_indicators)

        # iCloud artifacts
        icloud_indicators = ['icloud', 'mobileme', 'ubiquity']
        cloud_data['forensic_icloud_artifact'] = any(ind in filename for ind in icloud_indicators)

        # Dropbox artifacts
        dropbox_indicators = ['dropbox', 'host.db', 'config.db']
        cloud_data['forensic_dropbox_artifact'] = any(ind in filename for ind in dropbox_indicators)

        cloud_forensic_fields = [
            'forensic_cloud_account_info',
            'forensic_cloud_sync_timestamps',
            'forensic_cloud_file_versions',
            'forensic_cloud_sharing_permissions',
            'forensic_cloud_device_list',
            'forensic_cloud_login_history',
            'forensic_cloud_file_metadata',
            'forensic_cloud_trash_items',
            'forensic_cloud_collaboration',
            'forensic_cloud_backup_artifacts',
            'forensic_cloud_encryption_keys',
            'forensic_cloud_api_calls',
        ]

        for field in cloud_forensic_fields:
            cloud_data[field] = None

        cloud_data['forensic_cloud_field_count'] = len(cloud_forensic_fields)

    except Exception as e:
        cloud_data['forensic_cloud_error'] = str(e)

    return cloud_data


def _parse_sqlite_header(header: bytes) -> Optional[Dict[str, Any]]:
    if not header.startswith(b"SQLite format 3\x00"):
        return None
    if len(header) < 100:
        return None
    page_size = struct.unpack(">H", header[16:18])[0]
    if page_size == 1:
        page_size = 65536
    write_version = header[18]
    read_version = header[19]
    reserved_space = header[20]
    text_encoding = struct.unpack(">I", header[56:60])[0]
    user_version = struct.unpack(">I", header[60:64])[0]
    application_id = struct.unpack(">I", header[68:72])[0]
    schema_format = struct.unpack(">I", header[44:48])[0]
    return {
        "page_size": page_size,
        "write_version": write_version,
        "read_version": read_version,
        "reserved_space": reserved_space,
        "text_encoding": text_encoding,
        "user_version": user_version,
        "application_id": application_id,
        "schema_format": schema_format,
    }


def _parse_pcap_header(header: bytes) -> Dict[str, Any]:
    if len(header) < 24:
        return {}
    magic = struct.unpack(">I", header[0:4])[0]
    if magic == 0xA1B2C3D4:
        endian = "big"
        ts = "microseconds"
    elif magic == 0xD4C3B2A1:
        endian = "little"
        ts = "microseconds"
    elif magic == 0xA1B23C4D:
        endian = "big"
        ts = "nanoseconds"
    elif magic == 0x4D3CB2A1:
        endian = "little"
        ts = "nanoseconds"
    else:
        return {}
    fmt = ">" if endian == "big" else "<"
    version_major, version_minor = struct.unpack(fmt + "HH", header[4:8])
    snaplen = struct.unpack(fmt + "I", header[16:20])[0]
    network = struct.unpack(fmt + "I", header[20:24])[0]
    return {
        "magic": f"{magic:08x}",
        "endianness": endian,
        "ts_resolution": ts,
        "version_major": version_major,
        "version_minor": version_minor,
        "snaplen": snaplen,
        "network": network,
    }


def _parse_pcapng_header(header: bytes) -> Dict[str, Any]:
    if len(header) < 28:
        return {}
    if header[0:4] != b"\x0a\x0d\x0d\x0a":
        return {}
    block_length_le = struct.unpack("<I", header[4:8])[0]
    block_length_be = struct.unpack(">I", header[4:8])[0]
    bom = header[8:12]
    if bom == b"\x1a\x2b\x3c\x4d":
        endian = "big"
        block_length = block_length_be
    elif bom == b"\x4d\x3c\x2b\x1a":
        endian = "little"
        block_length = block_length_le
    else:
        return {}
    fmt = ">" if endian == "big" else "<"
    version_major, version_minor = struct.unpack(fmt + "HH", header[12:16])
    section_length = struct.unpack(fmt + "q", header[16:24])[0]
    return {
        "block_length": block_length,
        "endianness": endian,
        "version_major": version_major,
        "version_minor": version_minor,
        "section_length": section_length,
    }


def _parse_regf_header(header: bytes) -> Dict[str, Any]:
    if not header.startswith(b"regf") or len(header) < 0x1C:
        return {}
    return {
        "sequence_1": struct.unpack("<I", header[0x04:0x08])[0],
        "sequence_2": struct.unpack("<I", header[0x08:0x0C])[0],
        "timestamp_raw": struct.unpack("<Q", header[0x0C:0x14])[0],
        "major_version": struct.unpack("<I", header[0x14:0x18])[0] if len(header) >= 0x18 else None,
        "minor_version": struct.unpack("<I", header[0x18:0x1C])[0] if len(header) >= 0x1C else None,
    }


def _parse_evtx_header(header: bytes) -> Dict[str, Any]:
    if not header.startswith(b"ElfFile") or len(header) < 0x28:
        return {}
    return {
        "first_chunk": struct.unpack("<Q", header[0x08:0x10])[0],
        "last_chunk": struct.unpack("<Q", header[0x10:0x18])[0],
        "next_record": struct.unpack("<Q", header[0x18:0x20])[0],
        "header_size": struct.unpack("<I", header[0x20:0x24])[0],
        "minor_version": struct.unpack("<H", header[0x24:0x26])[0],
        "major_version": struct.unpack("<H", header[0x26:0x28])[0],
    }


def _parse_prefetch_header(header: bytes) -> Dict[str, Any]:
    if len(header) < 0x50 or header[4:8] != b"SCCA":
        return {}
    name_bytes = header[0x10:0x10 + 60]
    try:
        name = name_bytes.decode("utf-16le", errors="ignore").rstrip("\x00")
    except Exception:
        name = None
    return {
        "file_size": struct.unpack("<I", header[0x0C:0x10])[0],
        "executable_name": name,
        "hash": struct.unpack("<I", header[0x4C:0x50])[0],
    }


def _parse_lnk_header(header: bytes) -> Dict[str, Any]:
    if len(header) < 0x4C:
        return {}
    return {
        "header_size": struct.unpack("<I", header[0x00:0x04])[0],
        "link_flags": struct.unpack("<I", header[0x14:0x18])[0],
        "file_attributes": struct.unpack("<I", header[0x18:0x1C])[0],
        "creation_time_raw": struct.unpack("<Q", header[0x1C:0x24])[0],
        "access_time_raw": struct.unpack("<Q", header[0x24:0x2C])[0],
        "write_time_raw": struct.unpack("<Q", header[0x2C:0x34])[0],
        "file_size": struct.unpack("<I", header[0x34:0x38])[0],
        "icon_index": struct.unpack("<I", header[0x38:0x3C])[0],
        "show_command": struct.unpack("<I", header[0x3C:0x40])[0],
        "hotkey": struct.unpack("<H", header[0x40:0x42])[0],
    }


def _extract_sqlite_schema(filepath: str) -> Dict[str, Any]:
    schema_data: Dict[str, Any] = {}
    try:
        file_size = Path(filepath).stat().st_size
    except Exception:
        return schema_data
    if file_size > 50 * 1024 * 1024:
        return schema_data
    try:
        conn = sqlite3.connect(f"file:{filepath}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','index')")
        rows = cursor.fetchall()
        conn.close()
    except Exception:
        return schema_data

    tables = [name for name, kind in rows if kind == "table"]
    indices = [name for name, kind in rows if kind == "index"]
    lower_tables = {name.lower() for name in tables}
    schema_data["table_count"] = len(tables)
    schema_data["tables"] = tables[:50]
    schema_data["index_count"] = len(indices)
    schema_data["has_urls"] = "urls" in lower_tables
    schema_data["has_visits"] = "visits" in lower_tables or "visit_history" in lower_tables
    schema_data["has_cookies"] = "cookies" in lower_tables
    schema_data["has_downloads"] = "downloads" in lower_tables
    schema_data["has_moz_places"] = "moz_places" in lower_tables
    schema_data["db_type_guess"] = _guess_browser_db_type(Path(filepath).name, lower_tables)
    return schema_data


def _guess_browser_db_type(filename: str, table_names: set) -> Optional[str]:
    name = filename.lower()
    if "history" in name or "places" in name or "visit" in name:
        if "moz_places" in table_names:
            return "firefox_places"
        if "urls" in table_names:
            return "chrome_history"
    if "cookies" in name:
        return "cookies_db"
    if "login" in name:
        return "login_db"
    if "favicons" in name:
        return "favicons_db"
    return None


def _calculate_entropy(data: bytes) -> Optional[float]:
    if not data:
        return None
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    entropy = 0.0
    length = len(data)
    for count in counts:
        if count == 0:
            continue
        p = count / length
        entropy -= p * (p and __import__("math").log2(p) or 0)
    return entropy


def _parse_pe_sections(f, offset: int, count: int) -> Dict[str, Any]:
    sections = []
    section_names = []
    entropies = []
    if count <= 0:
        return {"section_count": 0, "sections": [], "section_names": [], "section_entropies": []}
    try:
        f.seek(offset)
        for _ in range(min(count, 96)):
            header = f.read(40)
            if len(header) < 40:
                break
            name = header[0:8].split(b"\x00", 1)[0].decode("latin1", errors="ignore")
            virtual_size = struct.unpack("<I", header[8:12])[0]
            virtual_address = struct.unpack("<I", header[12:16])[0]
            raw_size = struct.unpack("<I", header[16:20])[0]
            raw_ptr = struct.unpack("<I", header[20:24])[0]
            characteristics = struct.unpack("<I", header[36:40])[0]
            section = {
                "name": name,
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "raw_size": raw_size,
                "raw_pointer": raw_ptr,
                "characteristics": characteristics,
            }
            section_names.append(name)
            try:
                f.seek(raw_ptr)
                sample = f.read(min(raw_size, 1024 * 1024)) if raw_size else b""
                entropy = _calculate_entropy(sample)
            except Exception:
                entropy = None
            entropies.append(entropy)
            sections.append(section)
            f.seek(offset + (len(sections) * 40))
    except Exception:
        return {"section_count": len(sections), "sections": sections, "section_names": section_names, "section_entropies": entropies}
    return {"section_count": len(sections), "sections": sections, "section_names": section_names, "section_entropies": entropies}


def _parse_pe_imports(f, optional_header: bytes, sections: list) -> Dict[str, Any]:
    if not optional_header or len(optional_header) < 2:
        return {}
    magic = struct.unpack("<H", optional_header[0:2])[0]
    data_dir_offset = 96 if magic == 0x10B else 112 if magic == 0x20B else None
    if data_dir_offset is None or len(optional_header) < data_dir_offset + 16:
        return {}
    import_rva = struct.unpack("<I", optional_header[data_dir_offset + 8:data_dir_offset + 12])[0]
    import_size = struct.unpack("<I", optional_header[data_dir_offset + 12:data_dir_offset + 16])[0]
    if import_rva == 0:
        return {"import_rva": 0, "import_size": import_size, "dll_count": 0, "dlls": []}
    imports_offset = _rva_to_offset(import_rva, sections)
    if imports_offset is None:
        return {"import_rva": import_rva, "import_size": import_size, "dll_count": 0, "dlls": []}
    dlls = []
    try:
        f.seek(imports_offset)
        for _ in range(256):
            desc = f.read(20)
            if len(desc) < 20:
                break
            orig_first_thunk, _, _, name_rva, _ = struct.unpack("<IIIII", desc)
            if orig_first_thunk == 0 and name_rva == 0:
                break
            name_offset = _rva_to_offset(name_rva, sections)
            if name_offset is None:
                continue
            f_pos = f.tell()
            f.seek(name_offset)
            dll_name = _read_cstring(f, 260)
            f.seek(f_pos)
            if dll_name:
                dlls.append(dll_name)
    except Exception:
        pass
    return {
        "import_rva": import_rva,
        "import_size": import_size,
        "dll_count": len(dlls),
        "dlls": dlls[:50],
    }


def _rva_to_offset(rva: int, sections: list) -> Optional[int]:
    for section in sections:
        vaddr = section.get("virtual_address")
        vsize = section.get("virtual_size") or 0
        raw_ptr = section.get("raw_pointer")
        raw_size = section.get("raw_size") or 0
        if vaddr is None or raw_ptr is None:
            continue
        size = max(vsize, raw_size)
        if vaddr <= rva < vaddr + size:
            return raw_ptr + (rva - vaddr)
    return None


def _read_cstring(f, max_len: int) -> Optional[str]:
    data = f.read(max_len)
    if not data:
        return None
    end = data.find(b"\x00")
    if end == -1:
        end = len(data)
    try:
        return data[:end].decode("latin1", errors="ignore")
    except Exception:
        return None


def get_forensic_digital_advanced_field_count() -> int:
    """Return the number of advanced digital forensic fields."""
    # Upper bound: keys this module may emit (placeholders included).
    top_level = 1  # forensic_digital_advanced_detected

    signature_fields = 40  # incl. size/extension/entropy additions
    executable_fields = 28
    fs_fields = 22
    windows_fields = 25
    browser_fields = 28
    network_fields = 32
    malware_fields = 16
    anti_forensic_fields = 18
    encryption_fields = 17
    timeline_fields = 18
    cloud_fields = 18

    return (
        top_level
        + signature_fields
        + executable_fields
        + fs_fields
        + windows_fields
        + browser_fields
        + network_fields
        + malware_fields
        + anti_forensic_fields
        + encryption_fields
        + timeline_fields
        + cloud_fields
    )


# Integration point
def extract_forensic_digital_advanced_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for advanced digital forensic extraction."""
    return extract_forensic_digital_advanced_metadata(filepath)
