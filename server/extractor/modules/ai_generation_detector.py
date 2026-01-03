#!/usr/bin/env python3
"""
AI Generation Detector Module
Detects and extracts metadata from AI-generated images including:
- Stable Diffusion parameters (prompt, negative prompt, seed, CFG scale, steps, sampler, model, LoRAs)
- Midjourney detection (version, job ID, parameters, style, aspect ratio)
- DALL-E detection (generation ID, prompt)
- C2PA Content Credentials extraction
- AI artifact detection patterns

Author: MetaExtract Team
Version: 1.0.0
"""

import re
import json
import base64
import struct
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

STABLE_DIFFUSION_KEYWORDS = [
    "sd", "stable diffusion", "stability ai", "checkpoint", "lora", "lycoris",
    "dreamshaper", "revAnimated", "absolutereality", "realisticVision",
    "analogDiffusion", "stable_diffusion"
]

MIDJOURNEY_KEYWORDS = [
    "midjourney", "mj", "--v", "--ar", "--style", "--seed", "--tile", "--no"
]

DALLE_KEYWORDS = [
    "dall-e", "dalle", "openai", "dalle2", "dalle3"
]

C2PA_MANIFEST_SIG = b"c2pa"
XMP_C2PA_NAMESPACE = "https://c2pa.org/manifests"


class AIGenerationDetector:
    """
    AI generation detector for extracting AI-related metadata from images.
    Supports Stable Diffusion, Midjourney, DALL-E, and C2PA Content Credentials.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.xmp_data: Optional[str] = None
        self.exif_data: Optional[Dict[str, Any]] = None
        self.png_text_chunks: Dict[str, str] = {}
        self.webp_exif: Optional[Dict[str, Any]] = None

    def detect(self) -> Dict[str, Any]:
        """Main entry point - detect AI generation and extract all related metadata"""
        try:
            self._load_file_data()

            result = {
                "ai_detected": False,
                "ai_confidence": 0.0,
                "ai_models": [],
                "stable_diffusion": None,
                "midjourney": None,
                "dalle": None,
                "c2pa": None,
                "ai_artifacts": None,
            }

            sd_result = self._detect_stable_diffusion()
            if sd_result:
                result["stable_diffusion"] = sd_result
                result["ai_models"].append("stable_diffusion")

            mj_result = self._detect_midjourney()
            if mj_result:
                result["midjourney"] = mj_result
                result["ai_models"].append("midjourney")

            dalle_result = self._detect_dalle()
            if dalle_result:
                result["dalle"] = dalle_result
                result["ai_models"].append("dalle")

            c2pa_result = self._detect_c2pa()
            if c2pa_result:
                result["c2pa"] = c2pa_result
                result["ai_models"].append("c2pa")

            artifact_result = self._detect_ai_artifacts()
            if artifact_result:
                result["ai_artifacts"] = artifact_result

            result["ai_detected"] = len(result["ai_models"]) > 0 or artifact_result.get("artifacts_detected", False)
            result["ai_confidence"] = self._calculate_confidence(result)

            return result

        except Exception as e:
            logger.error(f"Error detecting AI generation: {e}")
            return {"error": str(e), "ai_detected": False}

    def _load_file_data(self):
        """Load file data for analysis"""
        file_path = Path(self.filepath)
        if not file_path.exists():
            return

        with open(self.filepath, 'rb') as f:
            self.file_data = f.read()

        if self.file_data[:8] == b'\x89PNG\r\n\x1a\n':
            self._parse_png_chunks()
        elif self.file_data[:4] == b'RIFF' and self.file_data[8:12] == b'WEBP':
            self._parse_webp_chunks()

        self._extract_xmp_from_png()

    def _parse_png_chunks(self):
        """Parse PNG chunks for metadata"""
        if not self.file_data or len(self.file_data) < 8:
            return

        offset = 8
        while offset < len(self.file_data) - 12:
            length = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
            chunk_type = self.file_data[offset + 4:offset + 8].decode('latin-1')

            chunk_data = self.file_data[offset + 8:offset + 8 + length]

            if chunk_type == 'tEXt':
                null_pos = chunk_data.find(b'\x00')
                if null_pos > 0:
                    keyword = chunk_data[:null_pos].decode('latin-1', errors='replace')
                    text_data = chunk_data[null_pos + 1:]
                    try:
                        self.png_text_chunks[keyword] = text_data.decode('latin-1', errors='replace')
                    except:
                        pass
            elif chunk_type == 'iTXt':
                null_pos = chunk_data.find(b'\x00')
                if null_pos > 0:
                    keyword = chunk_data[:null_pos].decode('latin-1', errors='replace')
                    self.png_text_chunks[keyword] = chunk_data.decode('latin-1', errors='replace')
            elif chunk_type == 'eXIf':
                self._parse_exif_from_png(chunk_data)

            offset += 12 + length

    def _parse_exif_from_png(self, data: bytes):
        """Parse EXIF data from PNG eXIf chunk"""
        try:
            if data[:4] == b'Exif':
                exif_data = data[4:]
                self.exif_data = self._parse_exif_bytes(exif_data)
        except Exception as e:
            logger.debug(f"Failed to parse PNG EXIF: {e}")

    def _parse_exif_bytes(self, data: bytes) -> Dict[str, Any]:
        """Parse EXIF data bytes"""
        result = {}
        try:
            if data[:2] != b'\xFF\xE1':
                return result

            length = struct.unpack('>H', data[2:4])[0]
            marker = data[4:6]

            if marker == b'II':
                is_little_endian = True
            elif marker == b'MM':
                is_little_endian = False
            else:
                return result

            tiff_start = 6
            if is_little_endian:
                ifd_offset = struct.unpack('<I', data[tiff_start:tiff_start + 4])[0]
            else:
                ifd_offset = struct.unpack('>I', data[tiff_start:tiff_start + 4])[0]

            result = self._parse_ifd(data, tiff_start, ifd_offset, is_little_endian)

        except Exception as e:
            logger.debug(f"Failed to parse EXIF bytes: {e}")

        return result

    def _parse_ifd(self, data: bytes, tiff_start: int, ifd_offset: int, is_little_endian: bool) -> Dict[str, Any]:
        """Parse IFD structure"""
        result = {}
        try:
            offset = tiff_start + ifd_offset
            num_entries = struct.unpack('<H' if is_little_endian else '>H',
                                        data[offset:offset + 2])[0]
            offset += 2

            for _ in range(num_entries):
                if offset + 12 > len(data):
                    break

                tag = struct.unpack('<H' if is_little_endian else '>H',
                                   data[offset:offset + 2])[0]
                tag_type = struct.unpack('<H' if is_little_endian else '>H',
                                        data[offset + 2:offset + 4])[0]
                count = struct.unpack('<I' if is_little_endian else '>I',
                                     data[offset + 4:offset + 8])[0]
                value_offset = struct.unpack('<I' if is_little_endian else '>I',
                                            data[offset + 8:offset + 12])[0]

                if tag == 0x010F:
                    result['Make'] = self._read_string(data, tiff_start, value_offset, count)
                elif tag == 0x0110:
                    result['Model'] = self._read_string(data, tiff_start, value_offset, count)
                elif tag == 0x0131:
                    result['Software'] = self._read_string(data, tiff_start, value_offset, count)
                elif tag == 0x8298:
                    result['Copyright'] = self._read_string(data, tiff_start, value_offset, count)

                offset += 12

        except Exception as e:
            logger.debug(f"Failed to parse IFD: {e}")

        return result

    def _read_string(self, data: bytes, tiff_start: int, offset: int, count: int) -> str:
        """Read string from EXIF data"""
        try:
            start = tiff_start + offset
            if start + count <= len(data):
                return data[start:start + count].decode('utf-8', errors='replace').rstrip('\x00')
        except:
            pass
        return ""

    def _parse_webp_chunks(self):
        """Parse WebP chunks for EXIF"""
        if not self.file_data or len(self.file_data) < 12:
            return

        offset = 12
        while offset < len(self.file_data) - 8:
            fourcc = self.file_data[offset:offset + 4].decode('latin-1', errors='replace')
            length = struct.unpack('<I', self.file_data[offset + 4:offset + 8])[0]

            if fourcc == 'EXIF':
                exif_data = self.file_data[offset + 8:offset + 8 + length]
                self.webp_exif = self._parse_exif_bytes(exif_data)
                break
            elif fourcc not in ['VP8 ', 'VP8L', 'VP8X', 'ANIM']:
                offset += 8 + length

    def _extract_xmp_from_png(self):
        """Extract XMP data from PNG"""
        if 'XML:com.adobe.xmp' in self.png_text_chunks:
            self.xmp_data = self.png_text_chunks['XML:com.adobe.xmp']

    def _detect_stable_diffusion(self) -> Optional[Dict[str, Any]]:
        """Detect and extract Stable Diffusion parameters"""
        result = {
            "detected": False,
            "prompt": "",
            "negative_prompt": "",
            "seed": None,
            "cfg_scale": None,
            "steps": None,
            "sampler": "",
            "model": "",
            "model_hash": "",
            "loras": [],
            "size": "",
            "batch_size": None,
        }

        sources_checked = []

        if self.xmp_data:
            sources_checked.append(self._parse_sd_from_xmp(result))

        if self.png_text_chunks:
            sources_checked.append(self._parse_sd_from_png_text(result))

        if self.exif_data or self.webp_exif:
            sources_checked.append(self._parse_sd_from_exif(result))

        for text_chunk in self.png_text_chunks.values():
            if any(kw.lower() in text_chunk.lower() for kw in STABLE_DIFFUSION_KEYWORDS):
                result["detected"] = True
                break

        if any(source.get("detected") for source in sources_checked):
            result["detected"] = True

        if result["detected"]:
            result["confidence"] = 0.85

        return result if result["detected"] else None

    def _parse_sd_from_xmp(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Stable Diffusion data from XMP"""
        if not self.xmp_data:
            return result

        try:
            if 'Prompt' in self.xmp_data or 'prompt' in self.xmp_data.lower():
                prompt_match = re.search(r'<rdf:li[^>]*>([^<]+)</rdf:li>',
                                         self.xmp_data, re.IGNORECASE)
                if prompt_match:
                    result["prompt"] = prompt_match.group(1).strip()

            seed_match = re.search(r'Seed["\s]*:?\s*(\d+)', self.xmp_data)
            if seed_match:
                result["seed"] = int(seed_match.group(1))

            steps_match = re.search(r'Steps["\s]*:?\s*(\d+)', self.xmp_data)
            if steps_match:
                result["steps"] = int(steps_match.group(1))

            cfg_match = re.search(r'CFG\s*Scale["\s]*:?\s*([\d.]+)', self.xmp_data)
            if cfg_match:
                result["cfg_scale"] = float(cfg_match.group(1))

            sampler_match = re.search(r'Sampler["\s]*:?\s*(\w+)', self.xmp_data)
            if sampler_match:
                result["sampler"] = sampler_match.group(1)

            model_match = re.search(r'Model["\s]*:?\s*([^,\n]+)', self.xmp_data)
            if model_match:
                result["model"] = model_match.group(1).strip()

            negative_match = re.search(r'Negative\s*prompt[:\s]*([^<]+)',
                                       self.xmp_data, re.IGNORECASE)
            if negative_match:
                result["negative_prompt"] = negative_match.group(1).strip()

            lora_matches = re.findall(r'<[^>]+lora:([^:<]+):([\d.]+)[^>]*>',
                                      self.xmp_data, re.IGNORECASE)
            for lora_name, lora_weight in lora_matches:
                result["loras"].append({
                    "name": lora_name.strip(),
                    "weight": float(lora_weight)
                })

            size_match = re.search(r'(\d+)\s*[xX×]\s*(\d+)', self.xmp_data)
            if size_match:
                result["size"] = f"{size_match.group(1)}x{size_match.group(2)}"

            result["detected"] = bool(result["prompt"] or result["model"])

        except Exception as e:
            logger.debug(f"Failed to parse SD from XMP: {e}")

        return result

    def _parse_sd_from_png_text(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Stable Diffusion data from PNG text chunks"""
        if not self.png_text_chunks:
            return result

        for key, value in self.png_text_chunks.items():
            value_lower = value.lower()

            if any(kw in value_lower for kw in ['prompt', 'parameters', 'negative']):
                if 'prompt' in key.lower() or 'parameters' in key.lower():
                    result["prompt"] = value

                if 'negative' in key.lower():
                    result["negative_prompt"] = value

                seed_match = re.search(r'Seed\s*[:=]?\s*(\d+)', value)
                if seed_match:
                    result["seed"] = int(seed_match.group(1))

                steps_match = re.search(r'Steps\s*[:=]?\s*(\d+)', value)
                if steps_match:
                    result["steps"] = int(steps_match.group(1))

                cfg_match = re.search(r'CFG\s*[Ss]cale\s*[:=]?\s*([\d.]+)', value)
                if cfg_match:
                    result["cfg_scale"] = float(cfg_match.group(1))

                sampler_match = re.search(r'Sampler\s*[:=]?\s*(\w+)', value)
                if sampler_match:
                    result["sampler"] = sampler_match.group(1)

                model_match = re.search(r'Model\s*[:=]?\s*([^,\n]+)', value)
                if model_match:
                    result["model"] = model_match.group(1).strip()

        if result["prompt"] or result["model"]:
            result["detected"] = True

        return result

    def _parse_sd_from_exif(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Stable Diffusion data from EXIF"""
        exif = self.exif_data or self.webp_exif or {}

        if not exif:
            return result

        software = exif.get('Software', '')
        if any(kw.lower() in software.lower() for kw in STABLE_DIFFUSION_KEYWORDS):
            result["detected"] = True
            result["model"] = software

        return result

    def _detect_midjourney(self) -> Optional[Dict[str, Any]]:
        """Detect and extract Midjourney parameters"""
        result = {
            "detected": False,
            "version": "",
            "job_id": "",
            "prompt": "",
            "style": "",
            "aspect_ratio": "",
            "seed": None,
            "tile": False,
            "no_params": [],
            "version_raw": "",
        }

        search_sources = []

        if self.xmp_data:
            search_sources.append(self.xmp_data)

        for text_chunk in self.png_text_chunks.values():
            search_sources.append(text_chunk)

        combined_text = ' '.join(search_sources)

        if not combined_text:
            return None

        mj_patterns = [
            (r'Midjourney\s*Model\s*[:=]?\s*([^\s,\n]+)', 'version'),
            (r'MJ\s*Version\s*[:=]?\s*([^\s,\n]+)', 'version'),
            (r'--v\s*([0-9.]+)', 'version_raw'),
            (r'--ar\s*([\d:]+)', 'aspect_ratio'),
            (r'--style\s*([^\s,\n]+)', 'style'),
            (r'--seed\s*(\d+)', 'seed'),
            (r'--tile', 'tile'),
            (r'--no\s*([^\s,\n]+)', 'no_params'),
            (r'Job\s*ID\s*[:=]?\s*([A-Za-z0-9-]+)', 'job_id'),
        ]

        for pattern, field in mj_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                if field == 'seed':
                    result["seed"] = int(match.group(1))
                elif field == 'tile':
                    result["tile"] = True
                elif field == 'no_params':
                    result["no_params"].append(match.group(1))
                elif field == 'version_raw':
                    result["version_raw"] = match.group(1)
                    result["version"] = f"v{match.group(1)}"
                else:
                    result[field] = match.group(1)

        prompt_patterns = [
            r'(?:Prompt|Job)\s*[:=]?\s*["\']?([^"\']+)',
            r'(?i)imagine\s+(?:prompt[:\s]+)?([^\n\r]+)',
        ]

        for pattern in prompt_patterns:
            prompt_match = re.search(pattern, combined_text)
            if prompt_match:
                prompt = prompt_match.group(1).strip()
                prompt = re.sub(r'--\w+(\s+[^-\s]+)?', '', prompt)
                result["prompt"] = prompt
                break

        if result["version"] or result["aspect_ratio"] or result["prompt"]:
            result["detected"] = True
            result["confidence"] = 0.9 if result["version"] else 0.7

        return result if result["detected"] else None

    def _detect_dalle(self) -> Optional[Dict[str, Any]]:
        """Detect and extract DALL-E parameters"""
        result = {
            "detected": False,
            "generation_id": "",
            "prompt": "",
            "version": "",
            "size": "",
        }

        search_sources = []

        if self.xmp_data:
            search_sources.append(self.xmp_data)

        for text_chunk in self.png_text_chunks.values():
            search_sources.append(text_chunk)

        combined_text = ' '.join(search_sources)

        dalle_patterns = [
            (r'DALL[·•]E\s*(v?[\d.]+)', 'version'),
            (r'Generation\s*ID\s*[:=]?\s*([A-Za-z0-9-]+)', 'generation_id'),
            (r'size\s*[:=]?\s*(\d+x\d+)', 'size'),
        ]

        for pattern, field in dalle_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                result[field] = match.group(1)

        prompt_patterns = [
            r'(?i)DALL[·•]E\s*(?:prompt)?[:\s]+([^\n\r]+)',
            r'(?i)(?:dalle|dall-e)\s+(?:generation\s+of\s+)?["\']?([^\n\r"\']+)',
        ]

        for pattern in prompt_patterns:
            prompt_match = re.search(pattern, combined_text)
            if prompt_match:
                result["prompt"] = prompt_match.group(1).strip()[:1000]
                break

        if result["version"] or result["generation_id"] or "dall-e" in combined_text.lower():
            result["detected"] = True
            result["confidence"] = 0.85

        return result if result["detected"] else None

    def _detect_c2pa(self) -> Optional[Dict[str, Any]]:
        """Detect and extract C2PA Content Credentials"""
        result = {
            "present": False,
            "version": "",
            "manifest": None,
            "claim_generator": "",
            "timestamp": "",
            "ingredients": [],
            "assertions": [],
        }

        c2pa_manifests = []

        if self.xmp_data and XMP_C2PA_NAMESPACE in self.xmp_data:
            result["present"] = True
            c2pa_manifests.append(self.xmp_data)

        for key, value in self.png_text_chunks.items():
            if 'c2pa' in key.lower() or 'content credentials' in key.lower():
                result["present"] = True
                c2pa_manifests.append(value)

        if c2pa_manifests:
            manifest_data = ' '.join(c2pa_manifests)

            generator_match = re.search(r'claimGenerator["\s]*:?\s*"([^"]+)"', manifest_data)
            if generator_match:
                result["claim_generator"] = generator_match.group(1)

            timestamp_match = re.search(r'"timestamp"\s*:\s*"([^"]+)"', manifest_data)
            if timestamp_match:
                result["timestamp"] = timestamp_match.group(1)

            version_match = re.search(r'c2pa[/\s]*([\d.]+)', manifest_data, re.IGNORECASE)
            if version_match:
                result["version"] = version_match.group(1)

            try:
                json_match = re.search(r'(\{["\s\S]*?"manifest"\s*:\s*\{["\s\S]*?\})',
                                        manifest_data)
                if json_match:
                    manifest_json = json.loads(json_match.group(1))
                    result["manifest"] = manifest_json

                    if "assertions" in manifest_json:
                        for assertion in manifest_json["assertions"]:
                            result["assertions"].append({
                                "label": assertion.get("label", ""),
                                "data": assertion.get("data", {}),
                            })

                    if "ingredients" in manifest_json:
                        result["ingredients"] = manifest_json["ingredients"]

            except (json.JSONDecodeError, AttributeError) as e:
                logger.debug(f"Failed to parse C2PA manifest JSON: {e}")

            if result["present"] and not result["version"]:
                result["version"] = "2.x"

        return result if result["present"] else None

    def _detect_ai_artifacts(self) -> Dict[str, Any]:
        """Detect AI generation artifacts through metadata patterns"""
        result = {
            "artifacts_detected": False,
            "patterns_found": [],
            "confidence_adjustment": 0.0,
        }

        patterns = []

        combined_text = ""
        if self.xmp_data:
            combined_text += self.xmp_data + " "
        combined_text += ' '.join(self.png_text_chunks.values())

        ai_patterns = [
            (r'ai-generated|ai\s*generated|artificial\s*intelligence', 'ai_generation_claim', 0.15),
            (r'generated\s+by\s+(?:ai|stable|midjourney|dalle)', 'generation_software_mentioned', 0.2),
            (r'stable\s*diffusion\s*v?[\d.]+', 'stable_diffusion_mentioned', 0.25),
            (r'midjourney\s*v?[\d.]+', 'midjourney_mentioned', 0.25),
            (r'dall[·•]e\s*v?[\d.]+', 'dalle_mentioned', 0.25),
            (r'checkpoint\s+model|model\s+checkpoint', 'checkpoint_model', 0.1),
            (r'negative\s+prompt', 'has_negative_prompt', 0.15),
            (r'cfg\s*scale|cfg\s*scale', 'has_cfg_scale', 0.15),
            (r'sampler\s*:\s*(?:euler|ddim|plms|lms|heun|ddpm|dpm\w*)', 'has_sampler', 0.1),
            (r'lor[ae]\s*:', 'has_lora', 0.15),
            (r'--v\s*\d+', 'midjourney_cli_style', 0.2),
            (r'--ar\s*[\d:]+', 'midjourney_aspect_ratio', 0.2),
        ]

        for pattern, name, weight in ai_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                patterns.append({
                    "pattern": name,
                    "weight": weight,
                })

        if self.exif_data:
            software = self.exif_data.get('Software', '')
            if any(kw.lower() in software.lower() for kw in STABLE_DIFFUSION_KEYWORDS):
                patterns.append({
                    "pattern": "software_matches_ai_tool",
                    "weight": 0.3,
                })

        if patterns:
            result["artifacts_detected"] = True
            result["patterns_found"] = patterns
            result["confidence_adjustment"] = sum(p["weight"] for p in patterns)

        return result

    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate overall AI detection confidence"""
        confidence = 0.0

        if result.get("stable_diffusion"):
            confidence += 0.35
        if result.get("midjourney"):
            confidence += 0.35
        if result.get("dalle"):
            confidence += 0.35
        if result.get("c2pa"):
            confidence += 0.4

        if result.get("ai_artifacts"):
            confidence += min(result["ai_artifacts"].get("confidence_adjustment", 0), 0.25)

        return min(confidence, 1.0)


def detect_ai_generation(filepath: str) -> Dict[str, Any]:
    """Convenience function to detect AI generation in an image"""
    detector = AIGenerationDetector(filepath)
    return detector.detect()


def get_ai_detection_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 60
