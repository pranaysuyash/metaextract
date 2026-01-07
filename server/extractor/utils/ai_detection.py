"""
MetaExtract AI-Generation Detection Utility
Heuristic analysis to detect AI-generated or manipulated media.
"""

from typing import Dict, Any, Optional, List
import re


class AIGenerationDetector:
    """Detect AI-generated content through metadata heuristics."""
    
    AI_TOOL_SIGNATURES = {
        "midjourney": ["midjourney", "mj_", "job_id"],
        "dalle": ["dall-e", "dalle", "openai"],
        "stable_diffusion": ["stable diffusion", "sd_", "stablediffusion", "automatic1111", "comfyui", "invoke"],
        "adobe_firefly": ["firefly", "adobe firefly"],
        "runway": ["runway", "gen-2", "gen-3"],
        "leonardo": ["leonardo.ai", "leonardo"],
        "flux": ["flux", "black forest labs"],
        "ideogram": ["ideogram"],
        "anthropic": ["claude", "anthropic"],
        "google": ["imagen", "gemini"],
        "meta": ["llama", "emu"],
    }
    
    AI_GENERATION_MARKERS = [
        "ai_generated",
        "ai-generated",
        "synthetically_generated",
        "machine_generated",
        "generative_ai",
        "text_to_image",
        "diffusion_model",
        "gan_generated",
    ]
    
    SUSPICIOUS_SOFTWARE_PATTERNS = [
        r"python.*pil",
        r"comfyui",
        r"automatic1111",
        r"invoke.*ai",
        r"diffusers",
        r"transformers",
    ]
    
    @staticmethod
    def analyze_metadata_for_ai_markers(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze metadata dictionary for AI generation indicators.
        
        Args:
            metadata: Full metadata dictionary from extraction.
            
        Returns:
            AI detection results with confidence scores.
        """
        result = {
            "ai_generated_likelihood": "low",
            "confidence_score": 0.0,
            "detected_markers": [],
            "detected_tools": [],
            "suspicious_patterns": [],
            "recommendation": "No strong AI generation indicators found."
        }
        
        score = 0.0
        markers = []
        tools = []
        patterns = []
        
        metadata_str = str(metadata).lower()
        
        for tool_name, signatures in AIGenerationDetector.AI_TOOL_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in metadata_str:
                    tools.append(tool_name)
                    score += 0.3
                    markers.append(f"AI tool signature: {sig}")
                    break
                    
        for marker in AIGenerationDetector.AI_GENERATION_MARKERS:
            if marker in metadata_str:
                markers.append(f"AI marker: {marker}")
                score += 0.25
                
        for pattern in AIGenerationDetector.SUSPICIOUS_SOFTWARE_PATTERNS:
            if re.search(pattern, metadata_str, re.IGNORECASE):
                patterns.append(pattern)
                score += 0.15
                
        software = metadata.get("software", "") or metadata.get("Software", "") or ""
        if isinstance(software, str):
            software_lower = software.lower()
            if any(tool in software_lower for tool in ["midjourney", "dall-e", "stable diffusion", "firefly"]):
                score += 0.4
                markers.append(f"Software field indicates AI: {software}")
                
        comment = metadata.get("comment", "") or metadata.get("Comment", "") or metadata.get("UserComment", "") or ""
        if isinstance(comment, str):
            comment_lower = comment.lower()
            if any(m in comment_lower for m in ["prompt:", "negative_prompt", "cfg_scale", "sampler", "steps:"]):
                score += 0.35
                markers.append("Comment contains generation parameters")
                patterns.append("Generation parameters in comment")
                
        xmp = metadata.get("xmp", {}) or {}
        if isinstance(xmp, dict):
            history = xmp.get("history", []) or []
            if isinstance(history, list) and len(history) == 0:
                pass
            elif isinstance(history, list) and len(history) == 1:
                score += 0.1
                patterns.append("Single-step edit history (possible generation)")
                
        exif = metadata.get("exif", {}) or {}
        if isinstance(exif, dict):
            make = exif.get("Make", "") or exif.get("make", "") or ""
            model = exif.get("Model", "") or exif.get("model", "") or ""
            if not make and not model:
                score += 0.1
                patterns.append("Missing camera make/model")
            elif "ai" in str(make).lower() or "ai" in str(model).lower():
                score += 0.2
                markers.append(f"Camera field suggests AI: {make} {model}")
                
        score = min(score, 1.0)
        
        if score >= 0.7:
            result["ai_generated_likelihood"] = "high"
            result["recommendation"] = "Strong indicators of AI generation detected. Verify provenance."
        elif score >= 0.4:
            result["ai_generated_likelihood"] = "medium"
            result["recommendation"] = "Some AI generation indicators present. Further verification recommended."
        elif score >= 0.15:
            result["ai_generated_likelihood"] = "low"
            result["recommendation"] = "Minor indicators detected, but likely authentic."
        else:
            result["ai_generated_likelihood"] = "very_low"
            result["recommendation"] = "No significant AI generation indicators found."
            
        result["confidence_score"] = round(score, 2)
        result["detected_markers"] = list(set(markers))
        result["detected_tools"] = list(set(tools))
        result["suspicious_patterns"] = list(set(patterns))
        
        return result

    @staticmethod
    def check_image_authenticity_heuristics(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check image authenticity through EXIF and metadata heuristics.
        
        Returns authenticity assessment based on metadata consistency.
        """
        result = {
            "authenticity_score": 1.0,
            "issues": [],
            "strengths": [],
            "assessment": "authentic"
        }
        
        score = 1.0
        issues = []
        strengths = []
        
        exif = metadata.get("exif", {}) or {}
        if isinstance(exif, dict):
            if exif.get("Make") and exif.get("Model"):
                strengths.append("Camera make/model present")
            else:
                score -= 0.1
                issues.append("Missing camera identification")
                
            if exif.get("DateTimeOriginal") or exif.get("CreateDate"):
                strengths.append("Original capture date present")
            else:
                score -= 0.1
                issues.append("No original capture timestamp")
                
            if exif.get("GPSLatitude") or exif.get("GPSLongitude"):
                strengths.append("GPS coordinates present")
                
            if exif.get("LensModel") or exif.get("LensMake"):
                strengths.append("Lens information present")
                score += 0.05
                
            if exif.get("ExposureTime") and exif.get("FNumber") and exif.get("ISO"):
                strengths.append("Complete exposure triangle")
                score += 0.05
            else:
                score -= 0.05
                issues.append("Incomplete exposure data")
                
        xmp = metadata.get("xmp", {}) or {}
        if isinstance(xmp, dict):
            history = xmp.get("history", [])
            if isinstance(history, list) and len(history) > 1:
                strengths.append(f"Edit history with {len(history)} steps")
            elif isinstance(history, list) and len(history) == 1:
                issues.append("Single edit step (possible generation)")
                score -= 0.1
                
        thumbnail = metadata.get("thumbnail") or metadata.get("ThumbnailImage")
        if thumbnail:
            strengths.append("Embedded thumbnail present")
            
        score = max(0.0, min(1.0, score))
        
        if score >= 0.8:
            result["assessment"] = "likely_authentic"
        elif score >= 0.6:
            result["assessment"] = "possibly_authentic"
        elif score >= 0.4:
            result["assessment"] = "uncertain"
        else:
            result["assessment"] = "possibly_synthetic"
            
        result["authenticity_score"] = round(score, 2)
        result["issues"] = issues
        result["strengths"] = strengths
        
        return result


def get_ai_detection_field_count() -> int:
    """Return estimated field count for AI detection utility."""
    return 25
