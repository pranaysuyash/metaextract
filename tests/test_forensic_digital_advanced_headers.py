import sqlite3
import struct

from server.extractor.modules.forensic_digital_advanced import (
    extract_forensic_digital_advanced_metadata,
)


def _write_file(path, data: bytes) -> None:
    with open(path, "wb") as f:
        f.write(data)


def test_pdf_signature_detection(tmp_path):
    path = tmp_path / "sample.pdf"
    _write_file(path, b"%PDF-1.7\n%EOF\n")
    result = extract_forensic_digital_advanced_metadata(str(path))
    assert result.get("forensic_file_has_pdf_header") is True
    assert result.get("forensic_file_is_document") is True
    assert "pdf" in (result.get("forensic_file_type_guesses") or [])


def test_pcap_header_detection(tmp_path):
    path = tmp_path / "capture.pcap"
    header = struct.pack(
        ">IHHIIII",
        0xA1B2C3D4,
        2,
        4,
        0,
        0,
        65535,
        1,
    )
    _write_file(path, header + b"\x00" * 64)
    result = extract_forensic_digital_advanced_metadata(str(path))
    assert result.get("forensic_pcap_detected") is True
    assert result.get("forensic_pcap_version_major") == 2
    assert result.get("forensic_pcap_version_minor") == 4
    assert result.get("forensic_pcap_endianness") == "big"
    assert result.get("forensic_pcap_ts_resolution") == "microseconds"
    assert result.get("forensic_pcap_snaplen") == 65535


def test_pcapng_header_detection(tmp_path):
    path = tmp_path / "capture.pcapng"
    header = b"\x0a\x0d\x0d\x0a"  # block type
    header += struct.pack("<I", 28)  # block length
    header += b"\x1a\x2b\x3c\x4d"  # BOM
    header += struct.pack(">HH", 1, 0)  # version 1.0 (big endian)
    header += struct.pack(">q", -1)  # section length
    header += struct.pack("<I", 28)  # block length (trailer)
    _write_file(path, header)
    result = extract_forensic_digital_advanced_metadata(str(path))
    assert result.get("forensic_pcapng_detected") is True
    assert result.get("forensic_pcapng_endianness") == "big"
    assert result.get("forensic_pcapng_version_major") == 1
    assert result.get("forensic_pcapng_version_minor") == 0


def test_sqlite_header_detection(tmp_path):
    path = tmp_path / "History"
    header = bytearray(100)
    header[0:16] = b"SQLite format 3\x00"
    header[16:18] = struct.pack(">H", 4096)
    header[18] = 1
    header[19] = 1
    header[20] = 0
    header[44:48] = struct.pack(">I", 4)
    header[56:60] = struct.pack(">I", 1)
    header[60:64] = struct.pack(">I", 99)
    header[68:72] = struct.pack(">I", 77)
    _write_file(path, bytes(header))
    result = extract_forensic_digital_advanced_metadata(str(path))
    assert result.get("forensic_browser_sqlite_detected") is True
    assert result.get("forensic_browser_sqlite_page_size") == 4096
    assert result.get("forensic_browser_sqlite_read_version") == 1
    assert result.get("forensic_browser_sqlite_write_version") == 1
    assert result.get("forensic_browser_sqlite_schema_format") is None or isinstance(
        result.get("forensic_browser_sqlite_schema_format"), int
    )
    assert result.get("forensic_browser_sqlite_user_version") == 99
    assert result.get("forensic_browser_sqlite_application_id") == 77


def test_sqlite_schema_detection(tmp_path):
    path = tmp_path / "History"
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT)")
    cursor.execute("CREATE TABLE visits (id INTEGER PRIMARY KEY, url_id INTEGER)")
    cursor.execute("CREATE TABLE cookies (id INTEGER PRIMARY KEY, host TEXT)")
    cursor.execute("CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url TEXT)")
    cursor.execute("CREATE TABLE downloads (id INTEGER PRIMARY KEY, target TEXT)")
    cursor.execute("CREATE INDEX idx_urls ON urls(url)")
    conn.commit()
    conn.close()

    result = extract_forensic_digital_advanced_metadata(str(path))
    assert result.get("forensic_browser_sqlite_detected") is True
    assert result.get("forensic_browser_sqlite_table_count") >= 5
    assert result.get("forensic_browser_has_urls_table") is True
    assert result.get("forensic_browser_has_visits_table") is True
    assert result.get("forensic_browser_has_cookies_table") is True
    assert result.get("forensic_browser_has_downloads_table") is True
    assert result.get("forensic_browser_has_moz_places") is True


def test_windows_artifact_headers(tmp_path):
    regf = tmp_path / "ntuser.dat"
    evtx = tmp_path / "System.evtx"
    prefetch = tmp_path / "APP.PF"
    lnk = tmp_path / "Shortcut.lnk"

    regf_header = bytearray(64)
    regf_header[0:4] = b"regf"
    regf_header[4:8] = struct.pack("<I", 10)
    regf_header[8:12] = struct.pack("<I", 10)
    regf_header[12:20] = struct.pack("<Q", 123456789)
    regf_header[20:24] = struct.pack("<I", 1)
    regf_header[24:28] = struct.pack("<I", 3)
    _write_file(regf, bytes(regf_header))

    evtx_header = bytearray(64)
    evtx_header[0:7] = b"ElfFile"
    evtx_header[8:16] = struct.pack("<Q", 2)
    evtx_header[16:24] = struct.pack("<Q", 8)
    evtx_header[24:32] = struct.pack("<Q", 1024)
    evtx_header[32:36] = struct.pack("<I", 128)
    evtx_header[36:38] = struct.pack("<H", 1)
    evtx_header[38:40] = struct.pack("<H", 3)
    _write_file(evtx, bytes(evtx_header))

    prefetch_header = bytearray(96)
    prefetch_header[0:4] = struct.pack("<I", 30)
    prefetch_header[4:8] = b"SCCA"
    prefetch_header[12:16] = struct.pack("<I", 4096)
    name = "APP.EXE".encode("utf-16le")
    prefetch_header[16:16 + len(name)] = name
    prefetch_header[76:80] = struct.pack("<I", 0xDEADBEEF)
    _write_file(prefetch, bytes(prefetch_header))

    lnk_header = bytearray(80)
    lnk_header[0:4] = struct.pack("<I", 0x4C)
    lnk_header[4:20] = b"\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46"
    lnk_header[20:24] = struct.pack("<I", 0x25)
    lnk_header[24:28] = struct.pack("<I", 0x20)
    lnk_header[28:36] = struct.pack("<Q", 111)
    lnk_header[36:44] = struct.pack("<Q", 222)
    lnk_header[44:52] = struct.pack("<Q", 333)
    lnk_header[52:56] = struct.pack("<I", 4096)
    lnk_header[56:60] = struct.pack("<I", 7)
    lnk_header[60:64] = struct.pack("<I", 1)
    lnk_header[64:66] = struct.pack("<H", 0x1234)
    _write_file(lnk, bytes(lnk_header))

    regf_res = extract_forensic_digital_advanced_metadata(str(regf))
    assert regf_res.get("forensic_registry_hive_detected") is True
    assert regf_res.get("forensic_registry_hive") is True
    assert regf_res.get("forensic_registry_sequence_1") == 10
    assert regf_res.get("forensic_registry_sequence_2") == 10
    assert regf_res.get("forensic_registry_major_version") == 1
    assert regf_res.get("forensic_registry_minor_version") == 3

    evtx_res = extract_forensic_digital_advanced_metadata(str(evtx))
    assert evtx_res.get("forensic_evtx_detected") is True
    assert evtx_res.get("forensic_windows_event_log") is True
    assert evtx_res.get("forensic_evtx_first_chunk") == 2
    assert evtx_res.get("forensic_evtx_last_chunk") == 8
    assert evtx_res.get("forensic_evtx_header_size") == 128
    assert evtx_res.get("forensic_evtx_major_version") == 3

    prefetch_res = extract_forensic_digital_advanced_metadata(str(prefetch))
    assert prefetch_res.get("forensic_prefetch_file") is True
    assert prefetch_res.get("forensic_prefetch_version") == 30
    assert prefetch_res.get("forensic_prefetch_file_size") == 4096
    assert prefetch_res.get("forensic_prefetch_executable_name") == "APP.EXE"
    assert prefetch_res.get("forensic_prefetch_hash") == 0xDEADBEEF

    lnk_res = extract_forensic_digital_advanced_metadata(str(lnk))
    assert lnk_res.get("forensic_shell_link_detected") is True
    assert lnk_res.get("forensic_lnk_header_size") == 0x4C
    assert lnk_res.get("forensic_lnk_link_flags") == 0x25
    assert lnk_res.get("forensic_lnk_file_attributes") == 0x20
    assert lnk_res.get("forensic_lnk_file_size") == 4096


def test_executable_header_detection(tmp_path):
    pe_path = tmp_path / "sample.exe"
    pe = bytearray(0x400)
    pe[0:2] = b"MZ"
    pe[0x3C:0x40] = struct.pack("<I", 0x80)
    pe[0x80:0x84] = b"PE\x00\x00"
    coff = struct.pack("<HHIIIHH", 0x14C, 1, 0x5F3759DF, 0, 0, 0xE0, 0x0002)
    pe[0x84:0x84 + 20] = coff
    optional = bytearray(0xE0)
    optional[0:2] = struct.pack("<H", 0x10B)
    optional[2:4] = bytes([14, 25])
    optional[16:20] = struct.pack("<I", 0x1000)
    optional[28:32] = struct.pack("<I", 0x400000)
    optional[68:72] = struct.pack("<HH", 2, 0x8140)
    pe[0x98:0x98 + len(optional)] = optional
    section_offset = 0x80 + 24 + 0xE0
    section_header = bytearray(40)
    section_header[0:8] = b".text\x00\x00\x00"
    section_header[8:12] = struct.pack("<I", 0x200)
    section_header[12:16] = struct.pack("<I", 0x1000)
    section_header[16:20] = struct.pack("<I", 0x80)
    section_header[20:24] = struct.pack("<I", 0x200)
    section_header[36:40] = struct.pack("<I", 0x60000020)
    pe[section_offset:section_offset + 40] = section_header
    pe[0x200:0x280] = b"\x90" * 0x80
    _write_file(pe_path, bytes(pe))

    pe_result = extract_forensic_digital_advanced_metadata(str(pe_path))
    assert pe_result.get("forensic_executable_format") == "PE"
    assert pe_result.get("forensic_pe_machine") == 0x14C
    assert pe_result.get("forensic_pe_sections") == 1
    assert pe_result.get("forensic_pe_entrypoint") == 0x1000
    assert pe_result.get("forensic_pe_section_count") == 1
    assert pe_result.get("forensic_pe_section_names") == [".text"]

    elf_path = tmp_path / "sample.elf"
    elf = bytearray(64)
    elf[0:4] = b"\x7fELF"
    elf[4] = 2  # 64-bit
    elf[5] = 1  # little-endian
    elf[6] = 1
    elf[16:18] = struct.pack("<H", 2)
    elf[18:20] = struct.pack("<H", 0x3E)
    elf[24:32] = struct.pack("<Q", 0x401000)
    _write_file(elf_path, bytes(elf))

    elf_result = extract_forensic_digital_advanced_metadata(str(elf_path))
    assert elf_result.get("forensic_executable_format") == "ELF"
    assert elf_result.get("forensic_elf_class") == "64-bit"
    assert elf_result.get("forensic_elf_machine") == 0x3E
    assert elf_result.get("forensic_elf_entrypoint") == 0x401000
