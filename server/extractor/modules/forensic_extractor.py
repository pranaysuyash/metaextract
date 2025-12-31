#!/usr/bin/env python3
"""
Network/Forensics Extractor for MetaExtract.
Extracts metadata from packet captures, forensic images, and security formats.
"""

import os
import sys
import json
import struct
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import hashlib

logger = logging.getLogger(__name__)


class PCAPExtractor:
    """Extract metadata from PCAP/PCAPNG files."""

    def detect_pcap(self, filepath: str) -> bool:
        """Check if file is a valid PCAP file."""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(24)
                magic = struct.unpack('<I', header[:4])[0]
                valid_magic = [0xa1b2c3d4, 0xd4c3b2a1, 0xa1b23c4d, 0x4d3cb2a1]
                if magic in valid_magic:
                    return True
                if header[:4] == b'\x0a\x0d\x0d\x0a':
                    return True
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_pcap_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "pcap_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                header = f.read(24)
                magic = struct.unpack('<I', header[:4])[0]
                
                is_pcapng = header[:4] == b'\x0a\x0d\x0d\x0a'
                
                metadata = {
                    "format": "pcapng" if is_pcapng else "pcap",
                    "file_size": os.path.getsize(filepath),
                }

                if is_pcapng:
                    major = struct.unpack('<H', header[4:6])[0]
                    minor = struct.unpack('<H', header[6:8])[0]
                    section_len = struct.unpack('<Q', header[8:16])[0]
                    metadata["version"] = f"{major}.{minor}"
                    metadata["section_length"] = section_len
                    
                    f.seek(0)
                    content = f.read(min(100000, os.path.getsize(filepath)))
                    blocks = content.count(b'\x01\x00\x00\x00')
                    metadata["section_blocks"] = blocks
                    
                    interfaces = content.count(b'\x02\x00\x00\x00')
                    metadata["interface_count"] = interfaces
                    
                else:
                    version_major = struct.unpack('<H', header[4:6])[0]
                    version_minor = struct.unpack('<H', header[6:8])[0]
                    thiszone = struct.unpack('<i', header[8:12])[0]
                    sigfigs = struct.unpack('<I', header[12:16])[0]
                    snaplen = struct.unpack('<I', header[16:20])[0]
                    network = struct.unpack('<I', header[20:24])[0]
                    
                    metadata["version"] = f"{version_major}.{version_minor}"
                    metadata["timezone"] = thiszone
                    metadata["snaplen"] = snaplen
                    
                    network_names = {
                        1: "Ethernet",
                        0x86dd: "IPv6",
                        0x0800: "IPv4",
                        0x0806: "ARP",
                        0x8847: "MPLS",
                    }
                    metadata["link_type"] = network
                    metadata["link_type_name"] = network_names.get(network, f"Unknown({network})")

                result["format_detected"] = "pcapng" if is_pcapng else "pcap"
                result["pcap_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["pcap_metadata"] = {"error": str(e)}

        return result


class SQLiteExtractor:
    """Extract metadata from SQLite database files."""

    def detect_sqlite(self, filepath: str) -> bool:
        """Check if file is a valid SQLite database."""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(16)
                return header[:16] == b'SQLite format 3\x00'
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_sqlite_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "sqlite_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                header = f.read(100)
                
                metadata = {
                    "format": "sqlite",
                    "file_size": os.path.getsize(filepath),
                }

                page_size = struct.unpack('>H', header[16:18])[0]
                if page_size == 1:
                    page_size = 65536
                metadata["page_size"] = page_size

                file_change_counter = struct.unpack('>I', header[24:28])[0]
                metadata["change_counter"] = file_change_counter

                page_count = struct.unpack('>I', header[28:32])[0]
                metadata["page_count"] = page_count
                metadata["database_size"] = page_count * page_size

                encoding = struct.unpack('>I', header[56:60])[0]
                encoding_names = {1: "UTF-8", 2: "UTF-16le", 3: "UTF-16be"}
                metadata["encoding"] = encoding_names.get(encoding, "Unknown")

                version = struct.unpack('>I', header[60:64])[0]
                metadata["user_version"] = version

                result["format_detected"] = "sqlite"
                result["sqlite_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["sqlite_metadata"] = {"error": str(e)}

        return result


class ParquetExtractor:
    """Extract metadata from Apache Parquet files."""

    def detect_parquet(self, filepath: str) -> bool:
        """Check if file is a valid Parquet file."""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                magic = f.read(4)
                return magic == b'PAR1'
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_parquet_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "parquet_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                magic = f.read(4)
                f.seek(-4, 2)
                footer_magic = f.read(4)
                
                metadata = {
                    "format": "parquet",
                    "file_size": os.path.getsize(filepath),
                }

                f.seek(8)
                metadata_length = struct.unpack('<I', f.read(4))[0]
                f.seek(-metadata_length - 12, 2)
                metadata_bytes = f.read(metadata_length)
                metadata_str = metadata_bytes.decode('utf-8', errors='replace')

                try:
                    import json
                    metadata_json = json.loads(metadata_str)
                    if 'schema' in metadata_json:
                        schemas = metadata_json['schema']
                        metadata["schema_nodes"] = len(schemas) if isinstance(schemas, list) else 1
                    if 'row_groups' in metadata_json:
                        metadata["row_groups"] = len(metadata_json['row_groups'])
                    if 'columns' in metadata_json:
                        metadata["columns"] = len(metadata_json['columns'])
                    if 'created_by' in metadata_json:
                        metadata["created_by"] = metadata_json['created_by']
                    if 'version' in metadata_json:
                        metadata["version"] = metadata_json['version']
                except:
                    pass

                result["format_detected"] = "parquet"
                result["parquet_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["parquet_metadata"] = {"error": str(e)}

        return result


class ArrowExtractor:
    """Extract metadata from Apache Arrow files."""

    def detect_arrow(self, filepath: str) -> bool:
        """Check if file is a valid Arrow file."""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                magic = f.read(8)
                return magic == b'ARROW\x00\x00\x00\x00'
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_arrow_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "arrow_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                magic = f.read(8)
                f.seek(0)
                
                metadata = {
                    "format": "arrow",
                    "file_size": os.path.getsize(filepath),
                }

                try:
                    footer_start = os.path.getsize(f.read(8)) - 8
                    f.seek(footer_start)
                    footer_length = struct.unpack('<I', f.read(4))[0]
                    f.seek(footer_start + 4)
                    metadata_length = struct.unpack('<I', f.read(4))[0]
                    f.seek(footer_start + 8)
                    schema_length = struct.unpack('<I', f.read(4))[0]
                    f.seek(footer_start + 12)
                    dict_metadata_length = struct.unpack('<I', f.read(4))[0]
                    record_batches = struct.unpack('<I', f.read(4))[0]
                    total_rows = struct.unpack('<Q', f.read(8))[0]
                    
                    metadata["footer_length"] = footer_length
                    metadata["schema_length"] = schema_length
                    metadata["dictionary_metadata_length"] = dict_metadata_length
                    metadata["record_batches"] = record_batches
                    metadata["total_rows"] = total_rows
                except:
                    pass

                result["format_detected"] = "arrow"
                result["arrow_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["arrow_metadata"] = {"error": str(e)}

        return result


class ForensicExtractor:
    """Main forensic extractor for network and database formats."""

    def __init__(self):
        self.pcap = PCAPExtractor()
        self.sqlite = SQLiteExtractor()
        self.parquet = ParquetExtractor()
        self.arrow = ArrowExtractor()

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract forensic/network/database metadata from file."""
        ext = Path(filepath).suffix.lower()

        if ext in ['.pcap', '.pcapng', '.cap']:
            return self.pcap.extract(filepath)
        elif ext in ['.sqlite', '.db', '.s3db', '.sqlite3']:
            return self.sqlite.extract(filepath)
        elif ext == '.parquet':
            return self.parquet.extract(filepath)
        elif ext in ['.arrow', '.feather']:
            return self.arrow.extract(filepath)

        for extractor, name in [(self.pcap, 'pcap'), (self.sqlite, 'sqlite'), 
                                (self.parquet, 'parquet'), (self.arrow, 'arrow')]:
            detect_method = getattr(extractor, 'detect_' + name)
            if detect_method(filepath):
                return extractor.extract(filepath)

        return {
            "source": "metaextract_forensic_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "error": "Unknown forensic/database format",
        }


def extract_forensic_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract forensic metadata."""
    extractor = ForensicExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python forensic_extractor.py <file.pcap|sqlite|parquet>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_forensic_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
