#!/usr/bin/env python3
"""
Document Extractor for MetaExtract.
Extracts metadata from EPUB, MOBI, CHM, and other document formats.
"""

import os
import sys
import json
import zipfile
import struct
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re

logger = logging.getLogger(__name__)


class EPUBExtractor:
    """Extract metadata from EPUB files."""

    def detect_epub(self, filepath: str) -> bool:
        """Check if file is a valid EPUB."""
        if not filepath.endswith('.epub'):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                names = z.namelist()
                return any('mimetype' in n for n in names)
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_epub_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "epub_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                metadata = {
                    "format": "epub",
                    "file_size": os.path.getsize(filepath),
                    "contents": z.namelist()[:50],
                }

                mimetype = None
                container_xml = None
                opf_file = None

                for name in z.namelist():
                    if 'mimetype' in name.lower():
                        try:
                            mimetype = z.read(name).decode('utf-8').strip()
                            metadata["mimetype"] = mimetype
                        except:
                            pass
                    if 'container.xml' in name.lower():
                        try:
                            container_xml = z.read(name).decode('utf-8')
                        except:
                            pass
                    if name.endswith('.opf'):
                        opf_file = name

                if opf_file:
                    opf_content = z.read(opf_file).decode('utf-8', errors='replace')
                    metadata["opf_file"] = opf_file

                    title_match = re.search(r'<dc:title[^>]*>(.*?)</dc:title>', opf_content, re.DOTALL)
                    if not title_match:
                        title_match = re.search(r'<title>(.*?)</title>', opf_content)
                    if title_match:
                        metadata["title"] = title_match.group(1).strip()

                    creator_match = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', opf_content, re.DOTALL)
                    if not creator_match:
                        creator_match = re.search(r'<creator>(.*?)</creator>', opf_content)
                    if creator_match:
                        metadata["creator"] = creator_match.group(1).strip()

                    lang_match = re.search(r'<dc:language>(.*?)</dc:language>', opf_content)
                    if lang_match:
                        metadata["language"] = lang_match.group(1).strip()

                    date_match = re.search(r'<dc:date[^>]*>(.*?)</dc:date>', opf_content, re.DOTALL)
                    if date_match:
                        metadata["date"] = date_match.group(1).strip()

                    publisher_match = re.search(r'<dc:publisher>(.*?)</dc:publisher>', opf_content)
                    if publisher_match:
                        metadata["publisher"] = publisher_match.group(1).strip()

                    isbn_match = re.search(r'<dc:identifier[^>]*>(.*?)</dc:identifier>', opf_content, re.DOTALL)
                    if isbn_match:
                        metadata["identifier"] = isbn_match.group(1).strip()

                    desc_match = re.search(r'<dc:description>(.*?)</dc:description>', opf_content, re.DOTALL)
                    if desc_match:
                        metadata["description"] = desc_match.group(1).strip()[:500]

                    subjects = re.findall(r'<dc:subject>(.*?)</dc:subject>', opf_content)
                    if subjects:
                        metadata["subjects"] = subjects[:10]

                if container_xml and 'META-INF' in container_xml:
                    metadata["has_container_xml"] = True

                html_files = [n for n in z.namelist() if n.endswith('.html') or n.endswith('.xhtml')]
                metadata["html_count"] = len(html_files)
                metadata["image_count"] = len([n for n in z.namelist() if n.endswith(('.png', '.jpg', '.jpeg', '.gif'))])

                result["format_detected"] = "epub"
                result["epub_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["epub_metadata"] = {"error": str(e)}

        return result


class MOBIExtractor:
    """Extract metadata from MOBI/PRC files."""

    def detect_mobi(self, filepath: str) -> bool:
        """Check if file is a valid MOBI file."""
        if not filepath.lower().endswith(('.mobi', '.prc', '.azw')):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header[:3] == b'TEX' or header[:4] in [b'\x00\x00\x00\x18', b'\xE9\x8E\x0D\xEA']
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_mobi_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "mobi_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                metadata = {
                    "format": "mobi",
                    "file_size": os.path.getsize(filepath),
                }

                header = f.read(68)

                if header[:3] == b'TEX':
                    metadata["type"] = "PalmDOC (TEX)"
                else:
                    metadata["type"] = "MOBI"

                text_offset = struct.unpack('>I', header[4:8])[0]
                text_length = struct.unpack('>I', header[8:12])[0]
                records_count = struct.unpack('>H', header[12:14])[0]

                metadata["text_offset"] = text_offset
                metadata["text_length"] = text_length
                metadata["records_count"] = records_count

                if len(header) >= 32:
                    title_offset = struct.unpack('>I', header[20:24])[0]
                    title_length = struct.unpack('>B', header[24])
                    f.seek(title_offset)
                    title = f.read(title_length * 2).decode('utf-16be', errors='replace').strip('\x00')
                    metadata["title"] = title

                if len(header) >= 36:
                    author_offset = struct.unpack('>I', header[28:32])[0]
                    author_length = struct.unpack('>B', header[32])
                    if author_offset > 0 and author_length > 0:
                        f.seek(author_offset)
                        try:
                            author = f.read(author_length * 2).decode('utf-16be', errors='replace').strip('\x00')
                            metadata["author"] = author
                        except:
                            pass

                encoding = header[3]
                metadata["encoding"] = "UTF-8" if encoding == 0xFF else "PalmDOC"

                result["format_detected"] = "mobi"
                result["mobi_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["mobi_metadata"] = {"error": str(e)}

        return result


class CHMExtractor:
    """Extract metadata from CHM (Compiled HTML) files."""

    def detect_chm(self, filepath: str) -> bool:
        """Check if file is a valid CHM file."""
        if not filepath.lower().endswith('.chm'):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header == b'ITSF'
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_chm_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "chm_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                metadata = {
                    "format": "chm",
                    "file_size": os.path.getsize(filepath),
                }

                header = f.read(0x60)

                if header[:4] != b'ITSF':
                    raise ValueError("Not a valid CHM file")

                version = struct.unpack('>I', header[4:8])[0]
                total_length = struct.unpack('>Q', header[8:16])[0]
                chunk_length = struct.unpack('>I', header[16:20])[0]
                language_id = struct.unpack('>I', header[20:24])[0]

                metadata["version"] = version
                metadata["total_length"] = total_length
                metadata["chunk_length"] = chunk_length
                metadata["language_id"] = language_id

                dir_offset = struct.unpack('>Q', header[24:32])[0]
                dir_length = struct.unpack('>Q', header[32:40])[0]

                metadata["directory_offset"] = dir_offset
                metadata["directory_length"] = dir_length

                sig = header[40:56]
                metadata["signature"] = sig[:8].hex()

                last_modified = header[56:64]
                metadata["last_modified_high"] = struct.unpack('>I', last_modified[:4])[0]
                metadata["last_modified_low"] = struct.unpack('>I', last_modified[4:8])[0]

                f.seek(0)
                content = f.read(min(100000, os.path.getsize(filepath)))
                content_str = content.decode('latin-1', errors='replace')

                title_match = re.search(r'<title>(.*?)</title>', content_str, re.DOTALL)
                if title_match:
                    metadata["title"] = title_match.group(1).strip()

                topic_match = re.search(r'<meta name="Topic"\s+content="([^"]+)"', content_str)
                if topic_match:
                    metadata["topic"] = topic_match.group(1)

                lang_match = re.search(r'<meta name="Language"\s+content="([^"]+)"', content_str)
                if lang_match:
                    metadata["language"] = lang_match.group(1)

                creator_match = re.search(r'<meta name="Creator"\s+content="([^"]+)"', content_str)
                if creator_match:
                    metadata["creator"] = creator_match.group(1)

                html_files = len(re.findall(r'\.html?', content_str, re.IGNORECASE))
                metadata["html_files_estimate"] = html_files

                result["format_detected"] = "chm"
                result["chm_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["chm_metadata"] = {"error": str(e)}

        return result


class PDFExtractor:
    """Extract metadata from PDF files (enhanced version)."""

    def detect_pdf(self, filepath: str) -> bool:
        """Check if file is a valid PDF."""
        if not filepath.lower().endswith('.pdf'):
            return False
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(8)
                return header[:4] == b'%PDF'
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_pdf_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "pdf_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'rb') as f:
                metadata = {
                    "format": "pdf",
                    "file_size": os.path.getsize(filepath),
                }

                header = f.read(8)
                if header[:4] == b'%PDF':
                    version = header[5:8].decode('ascii', errors='replace')
                    metadata["version"] = f"PDF {version}"

                f.seek(0)
                content = f.read(min(50000, os.path.getsize(filepath))).decode('latin-1', errors='replace')

                info_match = re.search(r'/Info\s+(\d+)\s+\d+\s+R', content)
                if info_match:
                    info_obj = int(info_match.group(1))
                    metadata["info_object"] = info_obj

                title_match = re.search(r'/Title\s*\(([^)]+)\)', content)
                if title_match:
                    metadata["title"] = title_match.group(1).strip()

                author_match = re.search(r'/Author\s*\(([^)]+)\)', content)
                if author_match:
                    metadata["author"] = author_match.group(1).strip()

                subject_match = re.search(r'/Subject\s*\(([^)]+)\)', content)
                if subject_match:
                    metadata["subject"] = subject_match.group(1).strip()

                keywords_match = re.search(r'/Keywords\s*\(([^)]+)\)', content)
                if keywords_match:
                    metadata["keywords"] = keywords_match.group(1).strip()

                creator_match = re.search(r'/Creator\s*\(([^)]+)\)', content)
                if creator_match:
                    metadata["creator"] = creator_match.group(1).strip()

                producer_match = re.search(r'/Producer\s*\(([^)]+)\)', content)
                if producer_match:
                    metadata["producer"] = producer_match.group(1).strip()

                creation_date_match = re.search(r'/CreationDate\s*\(([^)]+)\)', content)
                if creation_date_match:
                    metadata["creation_date"] = creation_date_match.group(1).strip()

                mod_date_match = re.search(r'/ModDate\s*\(([^)]+)\)', content)
                if mod_date_match:
                    metadata["modification_date"] = mod_date_match.group(1).strip()

                page_count_match = re.search(r'/Count\s+(\d+)', content)
                if page_count_match:
                    metadata["page_count"] = int(page_count_match.group(1))

                page_match = re.search(r'/Pages\s+(\d+)\s+\d+\s+R', content)
                if page_match:
                    metadata["pages_object"] = int(page_match.group(1))

                encrypted_match = re.search(r'/Encrypt', content)
                metadata["encrypted"] = encrypted_match is not None

                tagged_match = re.search(r'/StructTreeRoot', content)
                metadata["tagged"] = tagged_match is not None

                forms_match = re.search(r'/AcroForm', content)
                metadata["has_forms"] = forms_match is not None

                javascript_match = re.search(r'/JavaScript', content)
                metadata["has_javascript"] = javascript_match is not None

                images_count = len(re.findall(r'/Subtype\s*/Image', content))
                metadata["images_count"] = images_count

                result["format_detected"] = "pdf"
                result["pdf_metadata"] = metadata
                result["extraction_success"] = True

        except Exception as e:
            result["pdf_metadata"] = {"error": str(e)}

        return result


class DocumentExtractor:
    """Main document extractor that dispatches to specific format extractors."""

    def __init__(self):
        self.epub = EPUBExtractor()
        self.mobi = MOBIExtractor()
        self.chm = CHMExtractor()
        self.pdf = PDFExtractor()

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract document metadata from file."""
        ext = Path(filepath).suffix.lower()

        if ext == '.epub':
            return self.epub.extract(filepath)
        elif ext in ['.mobi', '.prc', '.azw']:
            return self.mobi.extract(filepath)
        elif ext == '.chm':
            return self.chm.extract(filepath)
        elif ext == '.pdf':
            return self.pdf.extract(filepath)

        for extractor, name in [(self.epub, 'epub'), (self.mobi, 'mobi'), (self.chm, 'chm'), (self.pdf, 'pdf')]:
            detect_method = getattr(extractor, 'detect_' + name)
            if detect_method(filepath):
                return extractor.extract(filepath)

        return {
            "source": "metaextract_document_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "error": "Unknown document format",
        }


def extract_document_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract document metadata."""
    extractor = DocumentExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python document_extractor.py <file.epub|mobi|chm|pdf>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_document_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))

def get_document_extractor_field_count() -> int:
    """
    Return the number of metadata fields extracted by document_extractor.
    
    Returns:
        Total field count
    """
    return 6  # source, filepath, format_detected, extraction_success, pdf_metadata, error


if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: python document_extractor.py <file.epub|mobi|chm|pdf>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_document_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
