"""
MetaExtract Security Module

This module provides security measures for handling potentially malicious files,
including file validation, sandboxing, and security scanning.
"""

import os
import tempfile
import subprocess
import hashlib
import magic
import logging
from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path
from enum import Enum
import mimetypes
import re
import json


class SecurityLevel(Enum):
    """Security levels for file processing."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"


class SecurityCheckResult:
    """Result of a security check."""
    def __init__(self, is_safe: bool, check_name: str, details: str = "", severity: str = "low"):
        self.is_safe = is_safe
        self.check_name = check_name
        self.details = details
        self.severity = severity  # "low", "medium", "high", "critical"
    
    def __repr__(self):
        return f"SecurityCheckResult(is_safe={self.is_safe}, check_name='{self.check_name}', severity='{self.severity}')"


class SecurityValidator:
    """Main security validation class."""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.STANDARD):
        self.security_level = security_level
        self.logger = logging.getLogger(__name__)
        
        # Known malicious file signatures (simplified for example)
        self.malicious_signatures = [
            b"MZ",  # DOS executable
            b"PE\x00\x00",  # Windows PE header
        ]
        
        # Dangerous file extensions
        self.dangerous_extensions = {
            '.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.lnk', '.inf',
            '.reg', '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh', '.msi',
            '.msp', '.hta', '.cpl', '.ocx', '.dll', '.sys', '.bin', '.elf'
        }
        
        # Dangerous MIME types
        self.dangerous_mime_types = {
            'application/x-dosexec',
            'application/x-executable',
            'application/x-msdownload',
            'application/x-sh',
            'application/x-shellscript'
        }
    
    def validate_file(self, filepath: str) -> List[SecurityCheckResult]:
        """Perform all security checks on a file."""
        results = []
        
        # Run all checks based on security level
        checks_to_run = self._get_checks_for_level(self.security_level)
        
        for check_func, check_name in checks_to_run:
            try:
                result = check_func(filepath)
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.warning(f"Security check {check_name} failed: {e}")
                results.append(SecurityCheckResult(
                    is_safe=False, 
                    check_name=check_name, 
                    details=f"Check failed: {str(e)}", 
                    severity="medium"
                ))
        
        return results
    
    def _get_checks_for_level(self, level: SecurityLevel) -> List[Tuple[Callable, str]]:
        """Get the appropriate checks for the security level."""
        basic_checks = [
            (self._check_file_extension, "File Extension Check"),
            (self._check_file_size, "File Size Check"),
            (self._check_mime_type, "MIME Type Check"),
        ]
        
        standard_checks = basic_checks + [
            (self._check_file_signature, "File Signature Check"),
            (self._check_file_integrity, "File Integrity Check"),
        ]
        
        strict_checks = standard_checks + [
            (self._scan_for_malicious_content, "Malicious Content Scan"),
            (self._check_embedded_scripts, "Embedded Scripts Check"),
        ]
        
        paranoid_checks = strict_checks + [
            (self._deep_file_analysis, "Deep File Analysis"),
            (self._sandbox_analysis, "Sandbox Analysis"),
        ]
        
        if level == SecurityLevel.BASIC:
            return basic_checks
        elif level == SecurityLevel.STANDARD:
            return standard_checks
        elif level == SecurityLevel.STRICT:
            return strict_checks
        else:  # PARANOID
            return paranoid_checks
    
    def _check_file_extension(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Check if file extension is dangerous."""
        ext = Path(filepath).suffix.lower()
        
        if ext in self.dangerous_extensions:
            return SecurityCheckResult(
                is_safe=False,
                check_name="File Extension Check",
                details=f"Dangerous file extension detected: {ext}",
                severity="high"
            )
        
        return SecurityCheckResult(
            is_safe=True,
            check_name="File Extension Check",
            details=f"Safe file extension: {ext}"
        )
    
    def _check_file_size(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Check if file size is within reasonable limits."""
        try:
            size = os.path.getsize(filepath)
            
            # Set limits based on security level
            if self.security_level == SecurityLevel.BASIC:
                max_size = 100 * 1024 * 1024  # 100MB
            elif self.security_level == SecurityLevel.STANDARD:
                max_size = 50 * 1024 * 1024   # 50MB
            elif self.security_level == SecurityLevel.STRICT:
                max_size = 10 * 1024 * 1024   # 10MB
            else:  # PARANOID
                max_size = 5 * 1024 * 1024    # 5MB
            
            if size > max_size:
                return SecurityCheckResult(
                    is_safe=False,
                    check_name="File Size Check",
                    details=f"File size {size} bytes exceeds limit {max_size} bytes",
                    severity="medium"
                )
            
            return SecurityCheckResult(
                is_safe=True,
                check_name="File Size Check",
                details=f"File size {size} bytes is within limits"
            )
        except OSError as e:
            return SecurityCheckResult(
                is_safe=False,
                check_name="File Size Check",
                details=f"Could not get file size: {str(e)}",
                severity="medium"
            )
    
    def _check_mime_type(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Check if MIME type is dangerous."""
        try:
            # Use python-magic to detect MIME type
            mime_type = magic.from_file(filepath, mime=True)
            
            if mime_type in self.dangerous_mime_types:
                return SecurityCheckResult(
                    is_safe=False,
                    check_name="MIME Type Check",
                    details=f"Dangerous MIME type detected: {mime_type}",
                    severity="high"
                )
            
            return SecurityCheckResult(
                is_safe=True,
                check_name="MIME Type Check",
                details=f"Safe MIME type: {mime_type}"
            )
        except Exception as e:
            return SecurityCheckResult(
                is_safe=False,
                check_name="MIME Type Check",
                details=f"Could not determine MIME type: {str(e)}",
                severity="medium"
            )
    
    def _check_file_signature(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Check file signature against known malicious patterns."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(1024)  # Read first 1KB
            
            for sig in self.malicious_signatures:
                if sig in header:
                    return SecurityCheckResult(
                        is_safe=False,
                        check_name="File Signature Check",
                        details=f"Malicious signature detected in file header",
                        severity="high"
                    )
            
            return SecurityCheckResult(
                is_safe=True,
                check_name="File Signature Check",
                details="No known malicious signatures detected"
            )
        except Exception as e:
            return SecurityCheckResult(
                is_safe=False,
                check_name="File Signature Check",
                details=f"Could not read file header: {str(e)}",
                severity="medium"
            )
    
    def _check_file_integrity(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Check file integrity using hash comparison."""
        try:
            # Calculate file hash
            hash_sha256 = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            file_hash = hash_sha256.hexdigest()
            
            # Check against known malicious hashes (simplified)
            # In a real system, this would check against a database of known malicious hashes
            known_bad_hashes = set()  # This would be populated from a threat database
            
            if file_hash in known_bad_hashes:
                return SecurityCheckResult(
                    is_safe=False,
                    check_name="File Integrity Check",
                    details=f"File matches known malicious hash: {file_hash[:16]}...",
                    severity="critical"
                )
            
            return SecurityCheckResult(
                is_safe=True,
                check_name="File Integrity Check",
                details=f"File integrity verified, hash: {file_hash[:16]}..."
            )
        except Exception as e:
            return SecurityCheckResult(
                is_safe=False,
                check_name="File Integrity Check",
                details=f"Could not calculate file hash: {str(e)}",
                severity="medium"
            )
    
    def _scan_for_malicious_content(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Scan file for malicious content."""
        try:
            # This is a simplified check - in a real system, you'd integrate with
            # antivirus software or threat intelligence services
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Look for common malicious patterns
            malicious_patterns = [
                rb'<script',  # Potential script injection
                rb'javascript:',  # JavaScript
                rb'vbscript:',  # VBScript
                rb'eval\s*\(',  # Code evaluation
                rb'exec\s*\(',  # Code execution
                rb'system\s*\(',  # System calls
            ]
            
            content_lower = content.lower()
            for pattern in malicious_patterns:
                if pattern in content_lower:
                    return SecurityCheckResult(
                        is_safe=False,
                        check_name="Malicious Content Scan",
                        details=f"Potentially malicious content pattern found: {pattern.decode()[:20]}",
                        severity="high"
                    )
            
            return SecurityCheckResult(
                is_safe=True,
                check_name="Malicious Content Scan",
                details="No malicious content patterns detected"
            )
        except Exception as e:
            return SecurityCheckResult(
                is_safe=False,
                check_name="Malicious Content Scan",
                details=f"Could not scan file content: {str(e)}",
                severity="medium"
            )
    
    def _check_embedded_scripts(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Check for embedded scripts in documents/images."""
        try:
            ext = Path(filepath).suffix.lower()
            
            # Check for embedded scripts in common document formats
            if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                # This is a simplified check - in a real system, you'd use specialized tools
                # to extract and analyze embedded content
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                script_indicators = [
                    b'/JS ',  # PDF JavaScript
                    b'/JavaScript',  # PDF JavaScript
                    b'/AA ',  # PDF Additional Actions
                    b'/OpenAction',  # PDF Open Action
                ]
                
                for indicator in script_indicators:
                    if indicator in content:
                        return SecurityCheckResult(
                            is_safe=False,
                            check_name="Embedded Scripts Check",
                            details=f"Potential embedded script found: {indicator.decode()}",
                            severity="high"
                        )
            
            # For image formats, check for embedded metadata that might contain scripts
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.svg']:
                # SVG files are particularly vulnerable to script injection
                if ext == '.svg':
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if '<script' in content.lower() or 'javascript:' in content.lower():
                        return SecurityCheckResult(
                            is_safe=False,
                            check_name="Embedded Scripts Check",
                            details="Potential script in SVG file",
                            severity="high"
                        )
            
            return SecurityCheckResult(
                is_safe=True,
                check_name="Embedded Scripts Check",
                details="No embedded scripts detected"
            )
        except Exception as e:
            return SecurityCheckResult(
                is_safe=False,
                check_name="Embedded Scripts Check",
                details=f"Could not check for embedded scripts: {str(e)}",
                severity="medium"
            )
    
    def _deep_file_analysis(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Perform deep file analysis (simplified version)."""
        try:
            # This would typically involve more sophisticated analysis
            # like disassembling executables, analyzing document structure, etc.
            # For this example, we'll just do a more thorough content check
            
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Look for more sophisticated malicious patterns
            advanced_patterns = [
                rb'%PDF-\d\.\d.*?/EmbeddedFile',  # PDF embedded files
                rb'(?i)<iframe',  # HTML iframes
                rb'(?i)<object',  # HTML objects
                rb'(?i)<embed',  # HTML embeds
                rb'(?i)onload\s*=',  # Event handlers
                rb'(?i)onerror\s*=',  # Event handlers
            ]
            
            for pattern in advanced_patterns:
                import re
                if re.search(pattern, content, re.IGNORECASE):
                    return SecurityCheckResult(
                        is_safe=False,
                        check_name="Deep File Analysis",
                        details=f"Advanced malicious pattern detected",
                        severity="high"
                    )
            
            return SecurityCheckResult(
                is_safe=True,
                check_name="Deep File Analysis",
                details="No advanced malicious patterns detected"
            )
        except Exception as e:
            return SecurityCheckResult(
                is_safe=False,
                check_name="Deep File Analysis",
                details=f"Could not perform deep analysis: {str(e)}",
                severity="medium"
            )
    
    def _sandbox_analysis(self, filepath: str) -> Optional[SecurityCheckResult]:
        """Perform sandbox analysis (simulated)."""
        # In a real system, this would submit the file to a sandbox environment
        # for behavioral analysis. For this example, we'll just return a safe result.
        
        return SecurityCheckResult(
            is_safe=True,
            check_name="Sandbox Analysis",
            details="File would be analyzed in sandbox environment (simulated)"
        )
    
    def is_file_safe(self, filepath: str) -> Tuple[bool, List[SecurityCheckResult]]:
        """Check if a file is safe to process."""
        results = self.validate_file(filepath)
        
        # Determine if file is safe based on results
        unsafe_results = [r for r in results if not r.is_safe]
        
        is_safe = len(unsafe_results) == 0
        
        # For security levels above BASIC, consider HIGH or CRITICAL severity as unsafe
        if self.security_level in [SecurityLevel.STANDARD, SecurityLevel.STRICT, SecurityLevel.PARANOID]:
            critical_results = [r for r in results if not r.is_safe and r.severity in ["high", "critical"]]
            is_safe = len(critical_results) == 0
        
        return is_safe, results


# Global security validator instance
_security_validator = None


def get_security_validator(security_level: SecurityLevel = SecurityLevel.STANDARD) -> SecurityValidator:
    """Get the security validator instance."""
    global _security_validator
    if _security_validator is None or _security_validator.security_level != security_level:
        _security_validator = SecurityValidator(security_level)
    return _security_validator


def validate_file_security(filepath: str, security_level: SecurityLevel = SecurityLevel.STANDARD) -> Tuple[bool, List[SecurityCheckResult]]:
    """Convenience function to validate file security."""
    validator = get_security_validator(security_level)
    return validator.is_file_safe(filepath)


def get_security_report(filepath: str, security_level: SecurityLevel = SecurityLevel.STANDARD) -> Dict:
    """Get a detailed security report for a file."""
    validator = get_security_validator(security_level)
    results = validator.validate_file(filepath)
    
    report = {
        "filepath": filepath,
        "security_level": security_level.value,
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "checks_performed": len(results),
        "safe": all(r.is_safe for r in results),
        "results": [
            {
                "check_name": r.check_name,
                "is_safe": r.is_safe,
                "details": r.details,
                "severity": r.severity
            }
            for r in results
        ]
    }
    
    # Add summary statistics
    safe_checks = sum(1 for r in results if r.is_safe)
    unsafe_checks = len(results) - safe_checks
    
    report["summary"] = {
        "safe_checks": safe_checks,
        "unsafe_checks": unsafe_checks,
        "overall_risk": "low" if safe_checks > unsafe_checks * 2 else 
                      "medium" if safe_checks > unsafe_checks else 
                      "high"
    }
    
    return report


# Example usage and testing
if __name__ == "__main__":
    import tempfile
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write("This is a safe test file.")
        test_file = f.name
    
    try:
        print("Testing security validation...")
        
        # Test with different security levels
        for level in [SecurityLevel.BASIC, SecurityLevel.STANDARD, SecurityLevel.STRICT]:
            print(f"\n--- Testing with {level.value} security level ---")
            is_safe, results = validate_file_security(test_file, level)
            
            print(f"File is safe: {is_safe}")
            for result in results:
                print(f"  {result}")
        
        # Get detailed report
        print(f"\n--- Detailed Security Report ---")
        report = get_security_report(test_file)
        print(json.dumps(report, indent=2))
        
    finally:
        # Clean up
        os.unlink(test_file)