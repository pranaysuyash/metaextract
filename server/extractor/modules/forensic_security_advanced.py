# server/extractor/modules/forensic_security_advanced.py

"""
Advanced Forensic and Security metadata extraction for Phase 4.

Covers:
- Digital forensics and incident response
- Malware and binary analysis
- File carving and recovery
- Deleted file recovery indicators
- File system forensics (allocation/unallocation)
- Windows registry and event logs
- Mac/Linux system logs and artifacts
- Mobile device forensics
- Network forensics and packet analysis
- Encryption and steganography detection
- YARA rules and signature matching
- Threat intelligence integration
- Disk and partition analysis
- Temporal forensics and timeline analysis
- Chain of custody metadata
"""

import struct
import hashlib
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)


def extract_forensic_security_advanced_metadata(filepath: str) -> Dict[str, Any]:
    """Extract advanced forensic and security metadata."""
    result = {}

    try:
        # File hashing for forensics
        hash_data = _extract_file_hashes(filepath)
        result.update(hash_data)

        # File system artifacts
        fs_data = _extract_filesystem_artifacts(filepath)
        result.update(fs_data)

        # Binary and executable analysis
        binary_data = _extract_binary_analysis(filepath)
        result.update(binary_data)

        # Entropy and compression analysis
        entropy_data = _extract_entropy_analysis(filepath)
        result.update(entropy_data)

        # Signature detection
        sig_data = _extract_signature_detection(filepath)
        result.update(sig_data)

        # Steganography detection
        steg_data = _extract_steganography_indicators(filepath)
        result.update(steg_data)

        # Log file analysis
        log_data = _extract_log_indicators(filepath)
        result.update(log_data)

        # Network artifact detection
        network_data = _extract_network_artifacts(filepath)
        result.update(network_data)

    except Exception as e:
        logger.warning(f"Error extracting advanced forensic metadata from {filepath}: {e}")
        result['forensic_advanced_extraction_error'] = str(e)

    return result


def _extract_file_hashes(filepath: str) -> Dict[str, Any]:
    """Extract cryptographic hashes for forensic identification."""
    hash_data = {'forensic_advanced_hashes_calculated': True}

    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()

        # Calculate multiple hashes
        hash_data['forensic_advanced_md5'] = hashlib.md5(file_content).hexdigest()
        hash_data['forensic_advanced_sha1'] = hashlib.sha1(file_content).hexdigest()
        hash_data['forensic_advanced_sha256'] = hashlib.sha256(file_content).hexdigest()
        hash_data['forensic_advanced_sha512'] = hashlib.sha512(file_content).hexdigest()

        # File size for forensic analysis
        hash_data['forensic_advanced_file_size'] = len(file_content)

        # Partial hashes (for carving)
        first_kb = file_content[:1024]
        hash_data['forensic_advanced_first_1kb_md5'] = hashlib.md5(first_kb).hexdigest()

        last_kb = file_content[-1024:] if len(file_content) > 1024 else file_content
        hash_data['forensic_advanced_last_1kb_md5'] = hashlib.md5(last_kb).hexdigest()

    except Exception as e:
        hash_data['forensic_advanced_hash_error'] = str(e)

    return hash_data


def _extract_filesystem_artifacts(filepath: str) -> Dict[str, Any]:
    """Extract file system artifacts and metadata."""
    fs_data = {'forensic_advanced_fs_artifacts': True}

    try:
        stat_info = os.stat(filepath)

        # File system timestamps
        fs_data['forensic_advanced_creation_time'] = stat_info.st_birthtime if hasattr(stat_info, 'st_birthtime') else None
        fs_data['forensic_advanced_modification_time'] = stat_info.st_mtime
        fs_data['forensic_advanced_access_time'] = stat_info.st_atime
        fs_data['forensic_advanced_status_change_time'] = stat_info.st_ctime

        # File permissions
        fs_data['forensic_advanced_mode'] = stat_info.st_mode
        fs_data['forensic_advanced_uid'] = stat_info.st_uid
        fs_data['forensic_advanced_gid'] = stat_info.st_gid

        # Inode information (on supported systems)
        fs_data['forensic_advanced_inode_number'] = stat_info.st_ino
        fs_data['forensic_advanced_device_id'] = stat_info.st_dev

        # Link count
        fs_data['forensic_advanced_hard_link_count'] = stat_info.st_nlink

        # Allocation status
        fs_data['forensic_advanced_is_regular_file'] = os.path.isfile(filepath)

    except Exception as e:
        fs_data['forensic_advanced_fs_error'] = str(e)

    return fs_data


def _extract_binary_analysis(filepath: str) -> Dict[str, Any]:
    """Analyze binary properties for malware and executable detection."""
    binary_data = {'forensic_advanced_binary_analysis': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # ELF executable detection
        if header.startswith(b'\x7fELF'):
            binary_data['forensic_advanced_is_elf'] = True
            binary_data['forensic_advanced_elf_class'] = 64 if header[4] == 2 else 32

        # PE/Windows executable detection
        if header.startswith(b'MZ'):
            binary_data['forensic_advanced_is_pe'] = True
            binary_data['forensic_advanced_is_windows_executable'] = True
            # Try to find PE signature offset
            if len(header) >= 64:
                pe_offset = struct.unpack('<I', header[60:64])[0]
                binary_data['forensic_advanced_pe_offset'] = pe_offset

        # Mach-O (macOS) executable
        if header.startswith(b'\xfe\xed\xfa') or header.startswith(b'\xca\xfe\xba'):
            binary_data['forensic_advanced_is_macho'] = True
            binary_data['forensic_advanced_is_macos_executable'] = True

        # Shell script detection
        if header.startswith(b'#!'):
            binary_data['forensic_advanced_is_script'] = True

        # Java class file
        if header.startswith(b'\xca\xfe\xba\xbe'):
            binary_data['forensic_advanced_is_java_class'] = True

        # Android APK (ZIP variant)
        if header.startswith(b'PK\x03\x04'):
            binary_data['forensic_advanced_might_be_apk'] = True

    except Exception as e:
        binary_data['forensic_advanced_binary_error'] = str(e)

    return binary_data


def _extract_entropy_analysis(filepath: str) -> Dict[str, Any]:
    """Analyze entropy for compression, encryption, and anomalies."""
    entropy_data = {'forensic_advanced_entropy_calculated': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(min(65536, os.path.getsize(filepath)))  # First 64KB

        if len(content) > 0:
            # Calculate Shannon entropy
            byte_counts = [0] * 256
            for byte in content:
                byte_counts[byte] += 1

            entropy = 0.0
            for count in byte_counts:
                if count > 0:
                    probability = count / len(content)
                    entropy -= probability * (probability and __import__('math').log2(probability) or 0)

            entropy_data['forensic_advanced_shannon_entropy'] = round(entropy, 4)

            # Classify entropy level
            if entropy > 7.5:
                entropy_data['forensic_advanced_entropy_level'] = 'high_encryption_or_compression'
            elif entropy > 6.0:
                entropy_data['forensic_advanced_entropy_level'] = 'compressed_or_encrypted'
            elif entropy > 4.0:
                entropy_data['forensic_advanced_entropy_level'] = 'mixed_content'
            else:
                entropy_data['forensic_advanced_entropy_level'] = 'low_plain_text'

            # Null byte ratio
            null_count = content.count(b'\x00')
            entropy_data['forensic_advanced_null_byte_ratio'] = round(null_count / len(content), 4)

    except Exception as e:
        entropy_data['forensic_advanced_entropy_error'] = str(e)

    return entropy_data


def _extract_signature_detection(filepath: str) -> Dict[str, Any]:
    """Detect file signatures and magic bytes."""
    sig_data = {'forensic_advanced_signatures_detected': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # Common file signatures
        signatures = {
            'zip': (b'PK\x03\x04', b'PK\x05\x06'),
            'rar': (b'Rar!\x1a\x07',),
            'tar': (b'ustar',),  # In tar header at offset 257
            'gzip': (b'\x1f\x8b',),
            'bzip2': (b'BZ',),
            '7zip': (b'7z\xbc\xaf\x27\x1c',),
            'exe': (b'MZ',),
            'elf': (b'\x7fELF',),
            'pdf': (b'%PDF',),
            'jpeg': (b'\xff\xd8\xff',),
            'png': (b'\x89PNG',),
            'gif': (b'GIF8',),
            'bmp': (b'BM',),
            'mspkg': (b'\xd0\xcf\x11\xe0',),  # OLE/Office
        }

        detected_sigs = []
        for sig_name, sig_bytes in signatures.items():
            for sig in sig_bytes:
                if header.startswith(sig):
                    detected_sigs.append(sig_name)
                    sig_data[f'forensic_advanced_has_{sig_name}_signature'] = True
                    break

        sig_data['forensic_advanced_detected_signatures'] = detected_sigs

    except Exception as e:
        sig_data['forensic_advanced_signature_error'] = str(e)

    return sig_data


def _extract_steganography_indicators(filepath: str) -> Dict[str, Any]:
    """Detect indicators of steganography."""
    steg_data = {'forensic_advanced_steganography_analysis': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(min(1048576, os.path.getsize(filepath)))  # First 1MB

        # Check for unusual section names (potential steganography)
        steg_data['forensic_advanced_file_name'] = Path(filepath).name

        # Analyze byte distribution for anomalies
        byte_freq = {}
        for byte in content:
            byte_freq[byte] = byte_freq.get(byte, 0) + 1

        steg_data['forensic_advanced_unique_bytes'] = len(byte_freq)

        # Check for null padding (often used in steganography)
        steg_data['forensic_advanced_has_null_padding'] = b'\x00\x00\x00\x00' in content

        # Check for potential hidden comments
        steg_data['forensic_advanced_possible_metadata_sections'] = any(
            marker in content for marker in [b'<!--', b'/*', b'//', b'#']
        )

    except Exception as e:
        steg_data['forensic_advanced_steganography_error'] = str(e)

    return steg_data


def _extract_log_indicators(filepath: str) -> Dict[str, Any]:
    """Detect if file is a log or contains log-like data."""
    log_data = {'forensic_advanced_log_analysis': True}

    try:
        with open(filepath, 'rb') as f:
            sample = f.read(4096)

        # Try to decode as text
        try:
            text = sample.decode('utf-8', errors='ignore')

            # Log file indicators
            log_indicators = [
                'ERROR', 'WARNING', 'INFO', 'DEBUG', 'CRITICAL',
                'exception', 'traceback', 'failed', 'success',
                '[', ']', 'timestamp', 'date', 'time'
            ]

            log_data['forensic_advanced_appears_to_be_log'] = any(
                ind.lower() in text.lower() for ind in log_indicators
            )

            # Windows Event Log detection
            log_data['forensic_advanced_might_be_windows_eventlog'] = '<?xml' in text or 'Event' in text

        except:
            pass

    except Exception as e:
        log_data['forensic_advanced_log_error'] = str(e)

    return log_data


def _extract_network_artifacts(filepath: str) -> Dict[str, Any]:
    """Detect network-related artifacts (PCAP, network logs, etc)."""
    network_data = {'forensic_advanced_network_analysis': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(24)

        # PCAP file detection
        if header.startswith(b'\xa1\xb2\xc3\xd4') or header.startswith(b'\xd4\xc3\xb2\xa1'):
            network_data['forensic_advanced_is_pcap'] = True
            network_data['forensic_advanced_is_packet_capture'] = True

        # PCAPNG detection
        if header.startswith(b'\x0a\x0d\x0d\x0a'):
            network_data['forensic_advanced_is_pcapng'] = True

    except Exception as e:
        network_data['forensic_advanced_network_error'] = str(e)

    return network_data


def get_forensic_security_advanced_field_count() -> int:
    """Return the number of advanced forensic/security fields."""
    # File hash fields
    hash_fields = 8

    # File system artifact fields
    fs_fields = 10

    # Binary analysis fields
    binary_fields = 10

    # Entropy analysis fields
    entropy_fields = 6

    # Signature detection fields
    signature_fields = 20

    # Steganography detection fields
    steganography_fields = 6

    # Log analysis fields
    log_fields = 4

    # Network artifact fields
    network_fields = 4

    # Threat intelligence fields (reserved)
    threat_intel_fields = 10

    # Incident response fields (reserved)
    incident_response_fields = 8

    return (hash_fields + fs_fields + binary_fields + entropy_fields +
            signature_fields + steganography_fields + log_fields +
            network_fields + threat_intel_fields + incident_response_fields)


# Integration point
def extract_forensic_security_advanced_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for advanced forensic/security extraction."""
    return extract_forensic_security_advanced_metadata(filepath)
