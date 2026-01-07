"""
MetaExtract Document Forensics Utility
Advanced extraction of JavaScript, macros, and hidden streams from PDF/Office.
"""

from typing import Dict, Any, List, Optional
import re
import zipfile
import xml.etree.ElementTree as ET

class PDFForensics:
    """Forensic analysis for PDF files."""
    
    @staticmethod
    def extract_js_artifacts(filepath: str) -> Dict[str, Any]:
        """Detect and extract JavaScript snippets from PDF objects."""
        artifacts = {"js_present": False, "snippets": [], "risk_level": "low"}
        
        try:
            with open(filepath, "rb") as f:
                content = f.read()
                
            # Look for /JS or /JavaScript markers
            js_matches = re.findall(b"/JS\s*(\([^)]*\)|<[^>]*>)", content)
            if js_matches:
                artifacts["js_present"] = True
                artifacts["snippets"] = [m.decode("utf-8", errors="replace") for m in js_matches[:10]]
                artifacts["risk_level"] = "high" if len(js_matches) > 5 else "medium"
                
            # Look for OpenAction with JS
            if b"/OpenAction" in content and b"/JS" in content:
                artifacts["has_auto_execute_js"] = True
                artifacts["risk_level"] = "critical"
                
        except Exception as e:
            artifacts["error"] = str(e)
            
        return artifacts

class OfficeForensics:
    """Forensic analysis for Office (OOXML) documents."""
    
    @staticmethod
    def analyze_vba_macros(filepath: str) -> Dict[str, Any]:
        """Detect VBA macros and sensitive API calls."""
        results = {"has_vba": False, "vba_parts": [], "suspicious_apis": []}
        
        try:
            if not zipfile.is_zipfile(filepath):
                return results
                
            with zipfile.ZipFile(filepath, "r") as zf:
                names = zf.namelist()
                vba_files = [n for n in names if "vbaProject.bin" in n or "vbaData.xml" in n]
                
                if vba_files:
                    results["has_vba"] = True
                    results["vba_parts"] = vba_files
                    
                    # Heuristic for suspicious strings in binary project
                    for vba_file in vba_files:
                        if vba_file.endswith(".bin"):
                            vba_content = zf.read(vba_file)
                            suspicious = [
                                b"Shell", b"Execute", b"AutoOpen", b"Workbook_Open", 
                                b"CreateObject", b"WScript", b"WinHttp"
                            ]
                            for api in suspicious:
                                if api in vba_content:
                                    results["suspicious_apis"].append(api.decode())
                                    
        except Exception as e:
            results["error"] = str(e)
            
        return results

def get_doc_forensics_field_count() -> int:
    """Return estimated field count for doc forensics utility."""
    return 80
