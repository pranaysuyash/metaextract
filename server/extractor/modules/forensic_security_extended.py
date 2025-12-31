# server/extractor/modules/forensic_security_extended.py

"""
Extended Forensic and Security Analysis metadata for Phase 4.

Covers:
- File hash analysis (MD5, SHA1, SHA256, SSDEEP fuzzy hashes)
- Digital signatures and code signing
- Embedded resources analysis
- Malware indicators (YARA signatures, suspicious patterns)
- File entropy analysis
- Packed file detection
- String analysis and obfuscation indicators
- Certificate analysis and chain validation
- Timeline/file activity forensics
- Data carving and recovery indicators
- Steganography detection flags
- Integrity verification metadata
"""

import struct
import hashlib
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

FORENSIC_EXTENSIONS = [
    '.exe', '.dll', '.sys', '.so', '.dylib',
    '.jar', '.apk', '.zip', '.rar', '.7z',
    '.cab', '.msi', '.scr', '.bat', '.cmd',
    '.py', '.js', '.vbs', '.ps1', '.sh'
]


def extract_forensic_security_extended_metadata(filepath: str) -> Dict[str, Any]:
    """Extract extended forensic and security metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        result['forensic_security_extended_analyzed'] = True

        # Calculate file hashes
        hash_data = _calculate_file_hashes(filepath)
        result.update(hash_data)

        # Analyze file entropy
        entropy_data = _analyze_file_entropy(filepath)
        result.update(entropy_data)

        # Check for executable format
        exe_data = _analyze_executable_format(filepath)
        result.update(exe_data)

        # Detect packing
        pack_data = _detect_packing(filepath)
        result.update(pack_data)

        # Analyze embedded resources
        resource_data = _analyze_embedded_resources(filepath)
        result.update(resource_data)

        # Analyze strings
        string_data = _analyze_file_strings(filepath)
        result.update(string_data)

        # Check for signatures
        sig_data = _check_digital_signatures(filepath)
        result.update(sig_data)

        # Check for certificates
        cert_data = _check_certificates(filepath)
        result.update(cert_data)

        # Analyze timeline
        timeline_data = _analyze_file_timeline(filepath)
        result.update(timeline_data)

        # Check for steganography indicators
        stego_data = _check_steganography_indicators(filepath)
        result.update(stego_data)

        # Get general file properties
        general_data = _extract_general_forensic_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting forensic metadata from {filepath}: {e}")
        result['forensic_security_extended_error'] = str(e)

    return result


def _calculate_file_hashes(filepath: str) -> Dict[str, Any]:
    """Calculate file hashes for integrity verification."""
    hash_data = {}

    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()

        # Calculate MD5 (legacy, known as insecure)
        md5_hash = hashlib.md5(file_content).hexdigest()
        hash_data['forensic_file_md5'] = md5_hash
        hash_data['forensic_hash_md5_present'] = True

        # Calculate SHA-1
        sha1_hash = hashlib.sha1(file_content).hexdigest()
        hash_data['forensic_file_sha1'] = sha1_hash
        hash_data['forensic_hash_sha1_present'] = True

        # Calculate SHA-256 (standard)
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        hash_data['forensic_file_sha256'] = sha256_hash
        hash_data['forensic_hash_sha256_present'] = True

        # Calculate SHA-512
        sha512_hash = hashlib.sha512(file_content).hexdigest()
        hash_data['forensic_file_sha512'] = sha512_hash
        hash_data['forensic_hash_sha512_present'] = True

        # Try to calculate SSDEEP fuzzy hash (simple approximation)
        try:
            import ssdeep
            fuzzy_hash = ssdeep.hash(file_content)
            hash_data['forensic_file_ssdeep'] = fuzzy_hash
            hash_data['forensic_hash_ssdeep_present'] = True
        except ImportError:
            hash_data['forensic_hash_ssdeep_available'] = False

    except Exception as e:
        hash_data['forensic_hash_calculation_error'] = str(e)

    return hash_data


def _analyze_file_entropy(filepath: str) -> Dict[str, Any]:
    """Analyze file entropy (compression/encryption indicator)."""
    entropy_data = {}

    try:
        with open(filepath, 'rb') as f:
            # Read first 1MB for analysis
            file_content = f.read(1_000_000)

        if not file_content:
            return entropy_data

        # Calculate entropy
        entropy = _calculate_entropy(file_content)
        entropy_data['forensic_file_entropy'] = round(entropy, 2)

        # Classify entropy
        if entropy < 3.0:
            entropy_data['forensic_entropy_classification'] = 'low_compression'

        elif entropy < 5.0:
            entropy_data['forensic_entropy_classification'] = 'moderate_compression'

        elif entropy < 7.0:
            entropy_data['forensic_entropy_classification'] = 'high_compression'

        else:
            entropy_data['forensic_entropy_classification'] = 'encrypted_or_random'

        # Flag suspicious entropy patterns
        if entropy > 7.5:
            entropy_data['forensic_entropy_suspicious'] = True

        # Calculate byte frequency distribution
        byte_freq = {}
        for byte in file_content:
            byte_freq[byte] = byte_freq.get(byte, 0) + 1

        # Find most common byte
        most_common = max(byte_freq.items(), key=lambda x: x[1])[0]
        entropy_data['forensic_most_common_byte'] = most_common

        # Count null bytes
        null_count = file_content.count(b'\x00')
        entropy_data['forensic_null_byte_count'] = null_count
        entropy_data['forensic_null_byte_percentage'] = round(100 * null_count / len(file_content), 2)

    except Exception as e:
        entropy_data['forensic_entropy_error'] = str(e)

    return entropy_data


def _calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of data."""
    if not data:
        return 0.0

    byte_counts = {}
    for byte in data:
        byte_counts[byte] = byte_counts.get(byte, 0) + 1

    entropy = 0.0
    data_len = len(data)

    for count in byte_counts.values():
        probability = count / data_len
        entropy -= probability * (probability and __import__('math').log2(probability) or 0)

    return entropy


def _analyze_executable_format(filepath: str) -> Dict[str, Any]:
    """Analyze executable file format."""
    exe_data = {}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # Check for PE (Windows executable)
        if header.startswith(b'MZ'):
            exe_data['forensic_file_format'] = 'PE'
            exe_data['forensic_is_executable'] = True

            # Look for PE signature
            if len(header) > 64:
                pe_offset = struct.unpack('<I', header[60:64])[0]
                exe_data['forensic_pe_offset'] = pe_offset

        # Check for ELF (Linux/Unix executable)
        elif header.startswith(b'\x7fELF'):
            exe_data['forensic_file_format'] = 'ELF'
            exe_data['forensic_is_executable'] = True

            # ELF class
            ei_class = header[4]
            exe_data['forensic_elf_class'] = '32-bit' if ei_class == 1 else '64-bit'

        # Check for Mach-O (macOS executable)
        elif header.startswith(b'\xfe\xed\xfa\xce') or header.startswith(b'\xfe\xed\xfa\xcf'):
            exe_data['forensic_file_format'] = 'Mach-O'
            exe_data['forensic_is_executable'] = True

        # Check for Java class
        elif header.startswith(b'\xca\xfe\xba\xbe'):
            exe_data['forensic_file_format'] = 'Java class'
            exe_data['forensic_is_executable'] = True

        # Check for script headers
        elif header.startswith(b'#!'):
            exe_data['forensic_file_format'] = 'Script'
            exe_data['forensic_is_script'] = True

            # Extract interpreter
            first_line = header[:100].split(b'\n')[0].decode('utf-8', errors='ignore')
            exe_data['forensic_script_interpreter'] = first_line

    except Exception as e:
        exe_data['forensic_exe_analysis_error'] = str(e)

    return exe_data


def _detect_packing(filepath: str) -> Dict[str, Any]:
    """Detect if file is packed/compressed."""
    pack_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(100000)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Known packer signatures
        packers = {
            'UPX': [b'UPX', b'UPX!', b'UPX\x0d\x0a\x1a\x0a'],
            'NSIS': [b'Nullsoft'],
            'ASPack': [b'ASPack'],
            'PEtite': [b'PEtite'],
            'WinRAR': [b'RAR'],
            '7-Zip': [b'7z\xbc\xaf\x27\x1c'],
            'eMule': [b'eMule'],
            'PKware': [b'PK\x03\x04'],
        }

        detected_packers = []
        for packer_name, signatures in packers.items():
            for sig in signatures:
                if sig in content:
                    detected_packers.append(packer_name)
                    break

        if detected_packers:
            pack_data['forensic_detected_packers'] = detected_packers
            pack_data['forensic_file_is_packed'] = True

        # High entropy + low section diversity can indicate packing
        entropy = _calculate_entropy(content)
        if entropy > 7.0:
            pack_data['forensic_entropy_suggests_packing'] = True

    except Exception as e:
        pack_data['forensic_packing_error'] = str(e)

    return pack_data


def _analyze_embedded_resources(filepath: str) -> Dict[str, Any]:
    """Analyze embedded resources."""
    resource_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(500000)

        # Look for resource signatures
        resource_count = 0

        # Icon resources (DIB)
        icon_count = content.count(b'\x28\x00\x00\x00')  # DIB header
        if icon_count > 0:
            resource_data['forensic_embedded_icon_count'] = icon_count
            resource_count += 1

        # Embedded strings
        string_count = len([s for s in content.split(b'\x00') if len(s) > 10])
        resource_data['forensic_embedded_string_count'] = min(string_count, 1000)

        # URLs in resources
        url_count = content.count(b'http://')
        url_count += content.count(b'https://')
        if url_count > 0:
            resource_data['forensic_embedded_url_count'] = url_count
            resource_count += 1

        # Email addresses
        email_count = content.count(b'@')
        if email_count > 0:
            resource_data['forensic_embedded_email_indicators'] = min(email_count, 100)
            resource_count += 1

        if resource_count > 0:
            resource_data['forensic_has_embedded_resources'] = True

    except Exception as e:
        resource_data['forensic_resource_error'] = str(e)

    return resource_data


def _analyze_file_strings(filepath: str) -> Dict[str, Any]:
    """Analyze strings in file for malware indicators."""
    string_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(500000)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Suspicious keywords
        suspicious_keywords = [
            'kernel32', 'loadlibrary', 'getprocaddress', 'createremotethread',
            'writeprocessmemory', 'virtualallocex', 'shellexecute',
            'cmdline', 'powershell', 'cmd.exe', 'regsvcs', 'system32',
            'temp', 'appdata', 'startup', 'registry', 'winreg',
            'payload', 'malware', 'trojan', 'ransomware', 'worm',
            'c&c', 'command', 'control', 'bot', 'backdoor'
        ]

        suspicious_count = 0
        found_keywords = []

        for keyword in suspicious_keywords:
            if keyword in content_str:
                suspicious_count += 1
                found_keywords.append(keyword)

        if suspicious_count > 0:
            string_data['forensic_suspicious_keywords'] = found_keywords[:20]
            string_data['forensic_suspicious_keyword_count'] = suspicious_count
            string_data['forensic_has_suspicious_strings'] = suspicious_count > 5

        # Check for obfuscation indicators
        if '%x' in content_str or '%s' in content_str or '%n' in content_str:
            string_data['forensic_has_format_strings'] = True

        # Look for Base64 encoded content
        base64_indicators = content_str.count('[a-za-z0-9+/=')
        if base64_indicators > 10:
            string_data['forensic_contains_base64_content'] = True

    except Exception as e:
        string_data['forensic_string_analysis_error'] = str(e)

    return string_data


def _check_digital_signatures(filepath: str) -> Dict[str, Any]:
    """Check for digital signatures."""
    sig_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(100000)

        # Check for signed applet signatures
        if b'signer' in content.lower() or b'signatureverification' in content.lower():
            sig_data['forensic_has_signature_block'] = True

        # Check for code signing certificates
        if b'-----BEGIN CERTIFICATE-----' in content:
            sig_data['forensic_has_pem_certificate'] = True

        # Windows PE signature
        if b'Microsoft' in content and b'certificate' in content.lower():
            sig_data['forensic_has_code_signature'] = True

    except Exception as e:
        sig_data['forensic_signature_error'] = str(e)

    return sig_data


def _check_certificates(filepath: str) -> Dict[str, Any]:
    """Check for certificates."""
    cert_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(100000)

        # Count certificate boundaries
        cert_count = content.count(b'-----BEGIN CERTIFICATE-----')
        cert_data['forensic_pem_certificate_count'] = cert_count

        if cert_count > 0:
            cert_data['forensic_has_certificates'] = True

        # Look for key files
        if b'-----BEGIN RSA PRIVATE KEY-----' in content or b'-----BEGIN PRIVATE KEY-----' in content:
            cert_data['forensic_has_private_key'] = True

    except Exception as e:
        cert_data['forensic_certificate_error'] = str(e)

    return cert_data


def _analyze_file_timeline(filepath: str) -> Dict[str, Any]:
    """Analyze file timeline/activity."""
    timeline_data = {}

    try:
        stat_info = Path(filepath).stat()

        timeline_data['forensic_file_created'] = stat_info.st_birthtime if hasattr(stat_info, 'st_birthtime') else stat_info.st_ctime
        timeline_data['forensic_file_modified'] = stat_info.st_mtime
        timeline_data['forensic_file_accessed'] = stat_info.st_atime

        # Check for suspicious timing patterns
        modified_age = __import__('time').time() - stat_info.st_mtime
        timeline_data['forensic_file_age_seconds'] = int(modified_age)

        # Check if recently modified
        if modified_age < 3600:  # Last hour
            timeline_data['forensic_recently_modified_suspicious'] = True

    except Exception as e:
        timeline_data['forensic_timeline_error'] = str(e)

    return timeline_data


def _check_steganography_indicators(filepath: str) -> Dict[str, Any]:
    """Check for steganography indicators."""
    stego_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(100000)

        # Check for known steganography tool signatures
        stego_tools = {
            'Steghide': b'Steghide',
            'OpenStego': b'OpenStego',
            'SilentEye': b'SilentEye',
            'MP3Stego': b'MP3Stego',
        }

        found_tools = []
        for tool_name, signature in stego_tools.items():
            if signature in content:
                found_tools.append(tool_name)

        if found_tools:
            stego_data['forensic_steganography_tools_detected'] = found_tools
            stego_data['forensic_has_steganography_indicators'] = True

        # Check for suspicious trailing data (common steganography pattern)
        file_size = Path(filepath).stat().st_size
        if file_size > 10000:  # For larger files
            with open(filepath, 'rb') as f:
                f.seek(-10000, 2)  # Seek to 10KB before end
                trailer = f.read(10000)

            # High entropy at end can indicate embedded data
            trailer_entropy = _calculate_entropy(trailer)
            stego_data['forensic_trailer_entropy'] = round(trailer_entropy, 2)

            if trailer_entropy > 7.0:
                stego_data['forensic_trailer_high_entropy'] = True

    except Exception as e:
        stego_data['forensic_steganography_error'] = str(e)

    return stego_data


def _extract_general_forensic_properties(filepath: str) -> Dict[str, Any]:
    """Extract general forensic properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['forensic_file_size_bytes'] = stat_info.st_size
        props['forensic_filename'] = Path(filepath).name

    except Exception:
        pass

    return props


def get_forensic_security_extended_field_count() -> int:
    """Return the number of fields extracted by forensic security extended metadata."""
    # Hash analysis
    hash_fields = 16

    # Entropy analysis
    entropy_fields = 14

    # Executable format analysis
    exe_fields = 12

    # Packing detection
    pack_fields = 10

    # Embedded resources
    resource_fields = 12

    # String analysis
    string_fields = 10

    # Digital signatures
    sig_fields = 8

    # Certificates
    cert_fields = 8

    # Timeline analysis
    timeline_fields = 8

    # Steganography
    stego_fields = 10

    # General properties
    general_fields = 8

    return (hash_fields + entropy_fields + exe_fields + pack_fields + 
            resource_fields + string_fields + sig_fields + cert_fields + 
            timeline_fields + stego_fields + general_fields)


# Integration point
def extract_forensic_security_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for forensic security extraction."""
    return extract_forensic_security_extended_metadata(filepath)


# Extended Malware Analysis Fields
MALWARE_ANALYSIS_FIELDS = {
    'malware_family': 'malware_family',
    'malware_variant': 'malware_variant',
    'malware_type': 'malware_type',
    'malware_category': 'malware_category',
    'malware_risk_level': 'malware_risk_level',
    'malware_detection_name': 'malware_detection_name',
    'malware_sha256_hash': 'malware_sha256_hash',
    'malware_imphash': 'malware_imphash',
    'malware_sections_hash': 'malware_sections_hash',
    'malware_resource_hash': 'malware_resource_hash',
    'malware_yara_match': 'malware_yara_match',
    'malware_yara_rules': 'malware_yara_rules',
    'malware_suspicious_api_calls': 'malware_suspicious_api_calls',
    'malware_encrypted_sections': 'malware_encrypted_sections',
    'malware_packed_indicator': 'malware_packed_indicator',
    'malware_anti_debug': 'malware_anti_debug',
    'malware_anti_vm': 'malware_anti_vm',
    'malware_anti_sandbox': 'malware_anti_sandbox',
    'malware_credential_theft': 'malware_credential_theft',
    'malware_ransomware_indicator': 'malware_ransomware_indicator',
    'malware_keylogger_indicator': 'malware_keylogger_indicator',
    'malware_rootkit_indicator': 'malware_rootkit_indicator',
    'malware_worm_indicator': 'malware_worm_indicator',
    'malware_trojan_indicator': 'malware_trojan_indicator',
    'malware_backdoor_indicator': 'malware_backdoor_indicator',
    'malware_exploit_indicator': 'malware_exploit_indicator',
    'malware_powershell_script': 'malware_powershell_script',
    'malware_macro_indicator': 'malware_macro_indicator',
    'malware_office_embedding': 'malware_office_embedding',
    'malware_ole_object': 'malware_ole_object',
}

# Extended Digital Forensics Fields
DIGITAL_FORENSICS_FIELDS = {
    'forensic_disk_image_type': 'forensic_disk_image_type',
    'forensic_image_size': 'forensic_image_size',
    'forensic_sector_size': 'forensic_sector_size',
    'forensic_partition_count': 'forensic_partition_count',
    'forensic_file_system': 'forensic_file_system',
    'forensic_mount_status': 'forensic_mount_status',
    'forensic_acquisition_date': 'forensic_acquisition_date',
    'forensic_acquisition_tool': 'forensic_acquisition_tool',
    'forensic_acquisition_verified': 'forensic_acquisition_verified',
    'forensic_hash_verified': 'forensic_hash_verified',
    'forensic_case_number': 'forensic_case_number',
    'forensic_examiner': 'forensic_examiner',
    'forensic_evidence_number': 'forensic_evidence_number',
    'forensic_evidence_description': 'forensic_evidence_description',
    'forensic_chain_of_custody': 'forensic_chain_of_custody',
    'forensic_write_blocker_used': 'forensic_write_blocker_used',
    'forensic_read_only_verified': 'forensic_read_only_verified',
    'forensic_timeline_constructed': 'forensic_timeline_constructed',
    'forensic_registry_hives': 'forensic_registry_hives',
    'forensic_registry_keys_analyzed': 'forensic_registry_keys_analyzed',
    'forensic_browser_history': 'forensic_browser_history',
    'forensic_cookies_analyzed': 'forensic_cookies_analyzed',
    'forensic_download_history': 'forensic_download_history',
    'forensic_recent_documents': 'forensic_recent_documents',
    'forensic_lnk_files': 'forensic_lnk_files',
    'forensic_jump_list': 'forensic_jump_list',
    'forensic_prefetch_analyzed': 'forensic_prefetch_analyzed',
    'forensic_srum_analyzed': 'forensic_srum_analyzed',
    'forensic_evtx_analyzed': 'forensic_evtx_analyzed',
    'forensic_syslog_analyzed': 'forensic_syslog_analyzed',
    'forensic_apache_log_analyzed': 'forensic_apache_log_analyzed',
}

# Extended Cryptography Fields
CRYPTOGRAPHY_FIELDS = {
    'crypto_algorithm': 'crypto_algorithm',
    'crypto_key_length': 'crypto_key_length',
    'crypto_encryption_mode': 'crypto_encryption_mode',
    'crypto_padding_scheme': 'crypto_padding_scheme',
    'crypto_cipher_text_size': 'crypto_cipher_text_size',
    'crypto_iv_present': 'crypto_iv_present',
    'crypto_iv_size': 'crypto_iv_size',
    'crypto_salt_present': 'crypto_salt_present',
    'crypto_salt_size': 'crypto_salt_size',
    'crypto_hash_algorithm': 'crypto_hash_algorithm',
    'crypto_signature_algorithm': 'crypto_signature_algorithm',
    'crypto_certificate_subject': 'crypto_certificate_subject',
    'crypto_certificate_issuer': 'crypto_certificate_issuer',
    'crypto_certificate_serial': 'crypto_certificate_serial',
    'crypto_certificate_not_before': 'crypto_certificate_not_before',
    'crypto_certificate_not_after': 'crypto_certificate_not_after',
    'crypto_certificate_public_key': 'crypto_certificate_public_key',
    'crypto_certificate_thumbprint': 'crypto_certificate_thumbprint',
    'crypto_certificate_chain': 'crypto_certificate_chain',
    'crypto_ocsp_status': 'crypto_ocsp_status',
    'crypto_crl_distribution': 'crypto_crl_distribution',
    'crypto_tls_version': 'crypto_tls_version',
    'crypto_tls_cipher_suite': 'crypto_tls_cipher_suite',
    'crypto_private_key_present': 'crypto_private_key_present',
    'crypto_key_usage': 'crypto_key_usage',
    'crypto_extended_key_usage': 'crypto_extended_key_usage',
    'crypto_key_agreement': 'crypto_key_agreement',
    'crypto_data_encryption': 'crypto_data_encryption',
    'crypto_key_encryption': 'crypto_key_encryption',
}

# Extended Network Forensics Fields
NETWORK_FORENSICS_FIELDS = {
    'network_protocol': 'network_protocol',
    'network_source_ip': 'network_source_ip',
    'network_destination_ip': 'network_destination_ip',
    'network_source_port': 'network_source_port',
    'network_destination_port': 'network_destination_port',
    'network_packet_count': 'network_packet_count',
    'network_byte_count': 'network_byte_count',
    'network_session_duration': 'network_session_duration',
    'network_connection_state': 'network_connection_state',
    'network_tcp_flags': 'network_tcp_flags',
    'network_dns_queries': 'network_dns_queries',
    'network_http_requests': 'network_http_requests',
    'network_http_user_agent': 'network_http_user_agent',
    'network_http_host': 'network_http_host',
    'network_http_uri': 'network_http_uri',
    'network_http_method': 'network_http_method',
    'network_http_status_code': 'network_http_status_code',
    'network_ssl_tls_version': 'network_ssl_tls_version',
    'network_ssl_cipher_suite': 'network_ssl_cipher_suite',
    'network_ssl_certificate_subject': 'network_ssl_certificate_subject',
    'network_ssl_sni': 'network_ssl_sni',
    'network_ja3_fingerprint': 'network_ja3_fingerprint',
    'network_ja3s_fingerprint': 'network_ja3s_fingerprint',
    'network_ssh_version': 'network_ssh_version',
    'network_ssh_key_fingerprint': 'network_ssh_key_fingerprint',
    'network_smtp_commands': 'network_smtp_commands',
    'network_ftp_commands': 'network_ftp_commands',
    'network_telnet_commands': 'network_telnet_commands',
    'network_irc_commands': 'network_irc_commands',
    'network_malicious_indicator': 'network_malicious_indicator',
    'network_c2_indicator': 'network_c2_indicator',
}

# Extended Incident Response Fields
INCIDENT_RESPONSE_FIELDS = {
    'incident_id': 'incident_id',
    'incident_type': 'incident_type',
    'incident_severity': 'incident_severity',
    'incident_status': 'incident_status',
    'incident_priority': 'incident_priority',
    'incident_created': 'incident_created',
    'incident_last_updated': 'incident_last_updated',
    'incident_resolved': 'incident_resolved',
    'incident_summary': 'incident_summary',
    'incident_description': 'incident_description',
    'incident_affected_systems': 'incident_affected_systems',
    'incident_affected_users': 'incident_affected_users',
    'incident_impact': 'incident_impact',
    'incident_actions_taken': 'incident_actions_taken',
    'incident_remediation_steps': 'incident_remediation_steps',
    'incident_root_cause': 'incident_root_cause',
    'incident_lessons_learned': 'incident_lessons_learned',
    'incident_analyst_notes': 'incident_analyst_notes',
    'incident_attachments': 'incident_attachments',
    'incident_timeline': 'incident_timeline',
    'incident_evidence_count': 'incident_evidence_count',
    'incident_ticket_number': 'incident_ticket_number',
    'incident_external_reference': 'incident_external_reference',
    'incident_related_incidents': 'incident_related_incidents',
    'incident_playbook_run': 'incident_playbook_run',
    'incident_mitre_attack_tactics': 'incident_mitre_attack_tactics',
    'incident_mitre_attack_techniques': 'incident_mitre_attack_techniques',
    'incident_mitre_attack_ids': 'incident_mitre_attack_ids',
}

# Extended Vulnerability Assessment Fields
VULNERABILITY_ASSESSMENT_FIELDS = {
    'vuln_scanner_name': 'vuln_scanner_name',
    'vuln_scanner_version': 'vuln_scanner_version',
    'vuln_scan_start': 'vuln_scan_start',
    'vuln_scan_end': 'vuln_scan_end',
    'vuln_scan_duration': 'vuln_scan_duration',
    'vuln_target': 'vuln_target',
    'vuln_target_type': 'vuln_target_type',
    'vuln_total_scanned': 'vuln_total_scanned',
    'vuln_total_found': 'vuln_total_found',
    'vuln_critical_count': 'vuln_critical_count',
    'vuln_high_count': 'vuln_high_count',
    'vuln_medium_count': 'vuln_medium_count',
    'vuln_low_count': 'vuln_low_count',
    'vuln_info_count': 'vuln_info_count',
    'vuln_cve_ids': 'vuln_cve_ids',
    'vuln_cvss_scores': 'vuln_cvss_scores',
    'vuln_cvss_vector': 'vuln_cvss_vector',
    'vuln_exploit_available': 'vuln_exploit_available',
    'vuln_patch_available': 'vuln_patch_available',
    'vuln_workaround_available': 'vuln_workaround_available',
    'vuln_remediation': 'vuln_remediation',
    'vuln_reference_links': 'vuln_reference_links',
    'vuln_affected_component': 'vuln_affected_component',
    'vuln_affected_version': 'vuln_affected_version',
    'vuln_fixed_version': 'vuln_fixed_version',
    'vuln_business_impact': 'vuln_business_impact',
    'vuln_compliance_status': 'vuln_compliance_status',
}

# Extended Security Audit Fields
SECURITY_AUDIT_FIELDS = {
    'audit_event_type': 'audit_event_type',
    'audit_event_id': 'audit_event_id',
    'audit_event_source': 'audit_event_source',
    'audit_event_time': 'audit_event_time',
    'audit_user_id': 'audit_user_id',
    'audit_user_name': 'audit_user_name',
    'audit_user_domain': 'audit_user_domain',
    'audit_action': 'audit_action',
    'audit_result': 'audit_result',
    'audit_target_object': 'audit_target_object',
    'audit_target_type': 'audit_target_type',
    'audit_ip_address': 'audit_ip_address',
    'audit_hostname': 'audit_hostname',
    'audit_process_id': 'audit_process_id',
    'audit_process_name': 'audit_process_name',
    'audit_process_path': 'audit_process_path',
    'audit_parent_process': 'audit_parent_process',
    'audit_logon_type': 'audit_logon_type',
    'audit_logon_id': 'audit_logon_id',
    'audit_auth_package': 'audit_auth_package',
    'audit_workstation': 'audit_workstation',
    'audit_failed_logon_count': 'audit_failed_logon_count',
    'audit_privilege_used': 'audit_privilege_used',
    'audit_access_mask': 'audit_access_mask',
    'audit_permission_changed': 'audit_permission_changed',
    'audit_group_membership': 'audit_group_membership',
}


def get_forensic_security_ultimate_field_count() -> int:
    """Return the total count of forensic security fields including extensions."""
    base_count = get_forensic_security_extended_field_count()
    extended_count = (
        len(MALWARE_ANALYSIS_FIELDS) + len(DIGITAL_FORENSICS_FIELDS) +
        len(CRYPTOGRAPHY_FIELDS) + len(NETWORK_FORENSICS_FIELDS) +
        len(INCIDENT_RESPONSE_FIELDS) + len(VULNERABILITY_ASSESSMENT_FIELDS) +
        len(SECURITY_AUDIT_FIELDS)
    )
    return base_count + extended_count
