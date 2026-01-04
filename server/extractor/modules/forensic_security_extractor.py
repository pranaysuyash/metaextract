#!/usr/bin/env python3
"""
Forensic and Security Metadata Extractor Module

Extracts forensic metadata, security indicators, steganography detection,
and other security-related information from files.
"""

import logging
import hashlib
import binascii
from typing import Dict, Any, List
from pathlib import Path
import os
import time
import stat

logger = logging.getLogger(__name__)

def extract_forensic_security_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract forensic and security metadata from files.
    
    Args:
        filepath: Path to the file to extract metadata from
        
    Returns:
        Dictionary containing forensic/security metadata
    """
    result = {
        'forensic_analysis': {},
        'security_indicators': {},
        'steganography_analysis': {},
        'file_integrity': {},
        'filesystem_metadata': {},
        'extraction_success': False,
        'errors': []
    }
    
    try:
        # Extract filesystem metadata
        result['filesystem_metadata'] = extract_filesystem_metadata(filepath)
        
        # Extract file integrity information
        result['file_integrity'] = extract_file_integrity(filepath)
        
        # Perform forensic analysis
        result['forensic_analysis'] = extract_forensic_analysis(filepath)
        
        # Extract security indicators
        result['security_indicators'] = extract_security_indicators(filepath)
        
        # Perform steganography analysis
        result['steganography_analysis'] = extract_steganography_analysis(filepath)
        
        result['extraction_success'] = True
        logger.info(f"Successfully extracted forensic/security metadata from {filepath}")
        
    except Exception as e:
        error_msg = f"Error extracting forensic/security metadata from {filepath}: {str(e)}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    return result


def extract_filesystem_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract filesystem metadata from the file.
    
    Args:
        filepath: Path to the file to extract filesystem metadata from
        
    Returns:
        Dictionary containing filesystem metadata
    """
    fs_metadata = {
        'creation_time': None,
        'modification_time': None,
        'access_time': None,
        'change_time': None,
        'file_size': None,
        'permissions': None,
        'owner_info': {},
        'filesystem_info': {},
        'inode': None,
        'device': None
    }
    
    try:
        file_stat = os.stat(filepath)
        
        # Time information
        fs_metadata['creation_time'] = time.ctime(file_stat.st_ctime) if hasattr(file_stat, 'st_ctime') else None
        fs_metadata['modification_time'] = time.ctime(file_stat.st_mtime)
        fs_metadata['access_time'] = time.ctime(file_stat.st_atime)
        fs_metadata['change_time'] = time.ctime(file_stat.st_ctime)  # On Unix, this is inode change time
        
        # Size and other info
        fs_metadata['file_size'] = file_stat.st_size
        fs_metadata['inode'] = file_stat.st_ino
        fs_metadata['device'] = file_stat.st_dev
        
        # Permissions
        fs_metadata['permissions'] = oct(stat.S_IMODE(file_stat.st_mode))
        
        # Owner information
        fs_metadata['owner_info']['uid'] = file_stat.st_uid
        fs_metadata['owner_info']['gid'] = file_stat.st_gid
        
        # File type
        if stat.S_ISREG(file_stat.st_mode):
            fs_metadata['filesystem_info']['type'] = 'regular_file'
        elif stat.S_ISDIR(file_stat.st_mode):
            fs_metadata['filesystem_info']['type'] = 'directory'
        elif stat.S_ISLNK(file_stat.st_mode):
            fs_metadata['filesystem_info']['type'] = 'symbolic_link'
        else:
            fs_metadata['filesystem_info']['type'] = 'other'
    
    except Exception as e:
        logger.error(f"Error extracting filesystem metadata: {str(e)}")
        fs_metadata['errors'] = [f'Error: {str(e)}']
    
    return fs_metadata


def extract_file_integrity(filepath: str) -> Dict[str, Any]:
    """
    Extract file integrity information including hashes.
    
    Args:
        filepath: Path to the file to extract integrity info from
        
    Returns:
        Dictionary containing file integrity information
    """
    integrity_info = {
        'hashes': {},
        'checksums': {},
        'file_signature': None,
        'entropy': None,
        'file_consistency': {}
    }
    
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        # Calculate various hashes
        integrity_info['hashes']['md5'] = hashlib.md5(file_content).hexdigest()
        integrity_info['hashes']['sha1'] = hashlib.sha1(file_content).hexdigest()
        integrity_info['hashes']['sha256'] = hashlib.sha256(file_content).hexdigest()
        integrity_info['hashes']['sha512'] = hashlib.sha512(file_content).hexdigest()
        
        # Calculate entropy (measure of randomness)
        if len(file_content) > 0:
            byte_counts = {}
            for byte in file_content:
                byte_counts[byte] = byte_counts.get(byte, 0) + 1
            
            entropy = 0
            file_len = len(file_content)
            for count in byte_counts.values():
                probability = count / file_len
                if probability > 0:
                    entropy -= probability * (probability.bit_length() - 1)  # Simplified log2 calculation
            
            integrity_info['entropy'] = entropy
        
        # Get file signature (first few bytes)
        if len(file_content) >= 8:
            integrity_info['file_signature'] = file_content[:8].hex()
        
        # Check for common file consistency issues
        file_path = Path(filepath)
        actual_size = os.path.getsize(filepath)
        reported_size = len(file_content)
        
        integrity_info['file_consistency']['size_match'] = actual_size == reported_size
        integrity_info['file_consistency']['actual_size'] = actual_size
        integrity_info['file_consistency']['reported_size'] = reported_size
    
    except Exception as e:
        logger.error(f"Error extracting file integrity info: {str(e)}")
        integrity_info['errors'] = [f'Error: {str(e)}']
    
    return integrity_info


def extract_forensic_analysis(filepath: str) -> Dict[str, Any]:
    """
    Perform forensic analysis on the file.
    
    Args:
        filepath: Path to the file to analyze forensically
        
    Returns:
        Dictionary containing forensic analysis results
    """
    forensic_analysis = {
        'file_carving_indicators': {},
        'hidden_data_detection': {},
        'metadata_anomalies': {},
        'tampering_indicators': {},
        'chain_of_custody': {},
        'file_timeline': {},
        'anomaly_detection': {}
    }
    
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        # Look for common file carving signatures
        file_signatures = {
            'jpeg': {'start': b'\xff\xd8\xff', 'end': b'\xff\xd9'},
            'png': {'start': b'\x89PNG\r\n\x1a\n', 'end': b'IEND\xaeB`\x82'},
            'gif': {'start': b'GIF87a', 'end': b''},
            'pdf': {'start': b'%PDF-', 'end': b'%%EOF'},
            'zip': {'start': b'PK\x03\x04', 'end': b''},
            'rar': {'start': b'Rar!\x1a\x07\x00', 'end': b''},
            'docx': {'start': b'PK\x03\x04', 'end': b''},  # ZIP-based format
            'exe': {'start': b'MZ', 'end': b'PE\x00\x00'},  # Simplified
        }
        
        for format_name, signatures in file_signatures.items():
            start_sig = signatures['start']
            end_sig = signatures['end']
            
            has_start = file_content.startswith(start_sig)
            has_end = end_sig and file_content.endswith(end_sig)
            
            forensic_analysis['file_carving_indicators'][format_name] = {
                'has_valid_start': has_start,
                'has_valid_end': has_end,
                'signature_match': has_start and (not end_sig or has_end)
            }
        
        # Check for hidden data in padding or unused space
        zero_count = file_content.count(b'\x00')
        total_size = len(file_content)
        zero_ratio = zero_count / total_size if total_size > 0 else 0
        
        forensic_analysis['hidden_data_detection']['zero_byte_ratio'] = zero_ratio
        forensic_analysis['hidden_data_detection']['potential_padding'] = zero_ratio > 0.3  # More than 30% zeros might indicate padding
        
        # Look for embedded strings that might indicate tampering
        suspicious_patterns = [
            b'password', b'login', b'username', b'private', b'secret',
            b'key', b'cert', b'pem', b'rsa', b'dsa', b'pgp', b'gpg'
        ]
        
        found_patterns = []
        for pattern in suspicious_patterns:
            if pattern in file_content.lower():
                found_patterns.append(pattern.decode('utf-8', errors='ignore'))
        
        forensic_analysis['tampering_indicators']['suspicious_strings'] = found_patterns
        
        # Check for anomalies in file structure
        file_path = Path(filepath)
        file_ext = file_path.suffix.lower()
        
        # Compare actual file signature with expected based on extension
        expected_formats = {
            '.jpg': ['jpeg'],
            '.jpeg': ['jpeg'],
            '.png': ['png'],
            '.gif': ['gif'],
            '.pdf': ['pdf'],
            '.zip': ['zip'],
            '.rar': ['rar'],
            '.docx': ['docx'],
            '.exe': ['exe']
        }
        
        if file_ext in expected_formats:
            expected_format = expected_formats[file_ext][0]
            actual_matches = []
            for fmt, sigs in file_signatures.items():
                if file_content.startswith(sigs['start']):
                    actual_matches.append(fmt)
            
            forensic_analysis['metadata_anomalies']['extension_vs_signature_match'] = expected_format in actual_matches
            forensic_analysis['metadata_anomalies']['expected_format'] = expected_format
            forensic_analysis['metadata_anomalies']['actual_formats_detected'] = actual_matches
    
    except Exception as e:
        logger.error(f"Error in forensic analysis: {str(e)}")
        forensic_analysis['errors'] = [f'Error: {str(e)}']
    
    return forensic_analysis


def extract_security_indicators(filepath: str) -> Dict[str, Any]:
    """
    Extract security indicators from the file.
    
    Args:
        filepath: Path to the file to extract security indicators from
        
    Returns:
        Dictionary containing security indicators
    """
    security_indicators = {
        'malware_indicators': {},
        'suspicious_patterns': {},
        'encryption_indicators': {},
        'obfuscation_detection': {},
        'threat_assessment': {}
    }
    
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        # Check for common malware indicators
        malware_indicators = {
            'executable_code': file_content.startswith(b'MZ'),  # DOS/Windows executable
            'shellcode_patterns': any(pattern in file_content for pattern in [
                b'\xeb\xfe',  # Jump to self (infinite loop)
                b'\xe8\x00\x00\x00\x00',  # Call instruction with zero offset
            ]),
            'suspicious_headers': any(header in file_content[:100] for header in [
                b'Virus', b'Worm', b'Trojan'
            ]),  # These are usually not in legitimate files
        }
        
        security_indicators['malware_indicators'] = malware_indicators
        
        # Look for obfuscation patterns
        printable_chars = sum(1 for byte in file_content if 32 <= byte <= 126 or byte in [9, 10, 13])
        total_chars = len(file_content)
        printable_ratio = printable_chars / total_chars if total_chars > 0 else 0
        
        security_indicators['obfuscation_detection']['printable_character_ratio'] = printable_ratio
        security_indicators['obfuscation_detection']['likely_obfuscated'] = printable_ratio < 0.7  # Less than 70% printable chars
        
        # Check for encryption indicators
        # Highly random data (high entropy) can indicate encryption
        entropy = 0
        if total_chars > 0:
            byte_counts = {}
            for byte in file_content:
                byte_counts[byte] = byte_counts.get(byte, 0) + 1
            
            for count in byte_counts.values():
                probability = count / total_chars
                if probability > 0:
                    entropy -= probability * (probability.bit_length() - 1)  # Simplified log2 calculation
        
        security_indicators['encryption_indicators']['entropy'] = entropy
        security_indicators['encryption_indicators']['likely_encrypted'] = entropy > 7.5  # Very high entropy
        
        # Basic threat assessment
        risk_factors = []
        if malware_indicators.get('executable_code', False):
            risk_factors.append('executable_file')
        if security_indicators['obfuscation_detection'].get('likely_obfuscated', False):
            risk_factors.append('obfuscated_content')
        if security_indicators['encryption_indicators'].get('likely_encrypted', False):
            risk_factors.append('encrypted_content')
        
        security_indicators['threat_assessment']['risk_factors'] = risk_factors
        security_indicators['threat_assessment']['risk_level'] = 'high' if len(risk_factors) > 1 else 'medium' if risk_factors else 'low'
    
    except Exception as e:
        logger.error(f"Error extracting security indicators: {str(e)}")
        security_indicators['errors'] = [f'Error: {str(e)}']
    
    return security_indicators


def extract_steganography_analysis(filepath: str) -> Dict[str, Any]:
    """
    Perform steganography analysis on the file.
    
    Args:
        filepath: Path to the file to analyze for steganography
        
    Returns:
        Dictionary containing steganography analysis results
    """
    stego_analysis = {
        'statistical_analysis': {},
        'spatial_domain_analysis': {},
        'frequency_domain_analysis': {},
        'steganography_detection': {},
        'recommendations': []
    }
    
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        # Statistical analysis
        byte_freq = {}
        for byte in file_content:
            byte_freq[byte] = byte_freq.get(byte, 0) + 1
        
        # Calculate chi-square test for randomness
        expected_freq = len(file_content) / 256  # Expected frequency for uniform distribution
        chi_square = sum(((observed - expected_freq) ** 2) / expected_freq for observed in byte_freq.values())
        
        stego_analysis['statistical_analysis']['chi_square'] = chi_square
        stego_analysis['statistical_analysis']['uniform_distribution_likelihood'] = chi_square < 293  # Approximate threshold for 255 degrees of freedom
        
        # LSB (Least Significant Bit) analysis
        lsb_sequence = ''.join([bin(byte)[-1] for byte in file_content[:1000]])  # First 1000 bytes
        lsb_runs = []
        current_run = 1
        
        for i in range(1, len(lsb_sequence)):
            if lsb_sequence[i] == lsb_sequence[i-1]:
                current_run += 1
            else:
                lsb_runs.append(current_run)
                current_run = 1
        lsb_runs.append(current_run)
        
        avg_run_length = sum(lsb_runs) / len(lsb_runs) if lsb_runs else 0
        stego_analysis['statistical_analysis']['lsb_avg_run_length'] = avg_run_length
        stego_analysis['statistical_analysis']['lsb_runs'] = lsb_runs[:10]  # First 10 runs
        
        # Check for common steganography file signatures
        stego_signatures = {
            'outguess': b'OUTGUESS',
            'jsteg': b'JSTEG',
            'f5': b'F5',
            'matroska': b'\x1a\x45\xdf\xa3',  # Matroska container often used for hiding data
        }
        
        detected_tools = []
        for tool, signature in stego_signatures.items():
            if signature in file_content:
                detected_tools.append(tool)
        
        stego_analysis['steganography_detection']['potential_tools'] = detected_tools
        stego_analysis['steganography_detection']['has_known_signatures'] = bool(detected_tools)
        
        # Recommendations based on analysis
        if avg_run_length > 2.5:  # Higher than expected for random data
            stego_analysis['recommendations'].append("High LSB run length detected - possible LSB steganography")
        
        if chi_square < 200:  # Much lower than expected, suggesting non-randomness
            stego_analysis['recommendations'].append("Low chi-square value detected - possible steganography")
        
        if not detected_tools:
            stego_analysis['recommendations'].append("No known steganography tool signatures detected")
    
    except Exception as e:
        logger.error(f"Error in steganography analysis: {str(e)}")
        stego_analysis['errors'] = [f'Error: {str(e)}']
    
    return stego_analysis


# Module-level function to be called by the extraction engine
def extract_forensic_security_extended(filepath: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extended forensic and security metadata extraction function that integrates with the main extraction engine.
    
    Args:
        filepath: Path to the file to extract metadata from
        result: The main result dictionary to update
        
    Returns:
        Updated result dictionary with forensic/security metadata
    """
    try:
        forensic_result = extract_forensic_security_metadata(filepath)
        
        # Add forensic metadata to the main result
        if forensic_result.get('extraction_success', False):
            result['forensic_analysis'] = forensic_result.get('forensic_analysis', {})
            result['security_indicators'] = forensic_result.get('security_indicators', {})
            result['steganography_analysis'] = forensic_result.get('steganography_analysis', {})
            result['file_integrity'] = forensic_result.get('file_integrity', {})
            result['filesystem_metadata'] = forensic_result.get('filesystem_metadata', {})
        
        # Add any errors to the main result
        errors = forensic_result.get('errors', [])
        if errors:
            if 'extraction_errors' not in result:
                result['extraction_errors'] = {}
            result['extraction_errors']['forensic_extraction'] = errors
    
    except Exception as e:
        logger.error(f"Error in extended forensic metadata extraction: {str(e)}")
        if 'extraction_errors' not in result:
            result['extraction_errors'] = {}
        result['extraction_errors']['forensic_extraction'] = [f"Extended extraction error: {str(e)}"]
    
    return result


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_forensic_security_metadata(filepath)
        import json
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python forensic_security_extractor.py <filepath>")