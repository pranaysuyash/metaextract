"""
MetaExtract C2PA (Content Credentials) Provenance Utility
Verifies and extracts Content Authenticity Initiative (CAI) manifests.
"""

from typing import Dict, Any, Optional, List
import json

try:
    import c2pa
    C2PA_AVAILABLE = True
except ImportError:
    C2PA_AVAILABLE = False

class C2PAProvenanceExtractor:
    """Extract and verify C2PA content credentials from media files."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if C2PA library is available."""
        return C2PA_AVAILABLE
    
    @staticmethod
    def extract_manifest(filepath: str) -> Dict[str, Any]:
        """
        Extract C2PA manifest from a media file.
        
        Returns:
            Dictionary containing manifest data and validation status.
        """
        result = {
            "c2pa_detected": False,
            "c2pa_available": C2PA_AVAILABLE,
            "manifest": None,
            "validation_status": "unknown",
            "claim_generator": None,
            "assertions": [],
            "signature_info": None,
            "provenance_chain": []
        }
        
        if not C2PA_AVAILABLE:
            result["error"] = "C2PA library not installed"
            return result
            
        try:
            reader = c2pa.Reader.from_file(filepath)
            
            if reader is None:
                result["validation_status"] = "no_manifest"
                return result
                
            result["c2pa_detected"] = True
            
            manifest_json = reader.json()
            manifest_data = json.loads(manifest_json) if isinstance(manifest_json, str) else manifest_json
            
            result["manifest"] = manifest_data
            
            if "active_manifest" in manifest_data:
                active = manifest_data["active_manifest"]
                result["claim_generator"] = manifest_data.get("manifests", {}).get(active, {}).get("claim_generator")
                
            if "validation_status" in manifest_data:
                val_status = manifest_data["validation_status"]
                if not val_status or len(val_status) == 0:
                    result["validation_status"] = "valid"
                else:
                    result["validation_status"] = "invalid"
                    result["validation_errors"] = val_status
            else:
                result["validation_status"] = "valid"
                
            manifests = manifest_data.get("manifests", {})
            for manifest_id, manifest in manifests.items():
                assertions = manifest.get("assertions", [])
                for assertion in assertions:
                    result["assertions"].append({
                        "label": assertion.get("label"),
                        "data": assertion.get("data")
                    })
                    
                signature = manifest.get("signature_info", {})
                if signature:
                    result["signature_info"] = {
                        "issuer": signature.get("issuer"),
                        "time": signature.get("time"),
                        "cert_serial_number": signature.get("cert_serial_number")
                    }
                    
            result["provenance_summary"] = C2PAProvenanceExtractor._generate_summary(result)
            
        except Exception as e:
            result["error"] = str(e)
            result["validation_status"] = "error"
            
        return result
    
    @staticmethod
    def _generate_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a human-readable provenance summary."""
        summary = {
            "has_provenance": data["c2pa_detected"],
            "is_verified": data["validation_status"] == "valid",
            "origin": "unknown"
        }
        
        if data.get("claim_generator"):
            summary["origin"] = data["claim_generator"]
            
        assertions = data.get("assertions", [])
        for assertion in assertions:
            label = assertion.get("label", "")
            if "ai_generative_training" in label:
                summary["ai_training_policy"] = assertion.get("data", {}).get("use", "unknown")
            if "c2pa.actions" in label:
                summary["has_edit_history"] = True
                
        return summary

    @staticmethod
    def check_ai_generation_markers(filepath: str) -> Dict[str, Any]:
        """
        Check for AI generation markers in C2PA manifest.
        
        Returns indicators if the content was AI-generated.
        """
        result = {
            "ai_generated": False,
            "ai_tool": None,
            "confidence": "low"
        }
        
        manifest_data = C2PAProvenanceExtractor.extract_manifest(filepath)
        
        if not manifest_data.get("c2pa_detected"):
            return result
            
        for assertion in manifest_data.get("assertions", []):
            label = assertion.get("label", "")
            data = assertion.get("data", {})
            
            if "c2pa.ai_generated" in label or "ai_generated" in str(data).lower():
                result["ai_generated"] = True
                result["confidence"] = "high"
                
            if "claim_generator" in str(manifest_data.get("claim_generator", "")).lower():
                generator = manifest_data.get("claim_generator", "")
                ai_tools = ["midjourney", "dall-e", "stable diffusion", "adobe firefly", "runway"]
                for tool in ai_tools:
                    if tool in generator.lower():
                        result["ai_generated"] = True
                        result["ai_tool"] = generator
                        result["confidence"] = "high"
                        break
                        
        return result


def get_c2pa_field_count() -> int:
    """Return estimated field count for C2PA provenance utility."""
    return 45
