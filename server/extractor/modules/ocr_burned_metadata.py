#!/usr/bin/env python3
"""
OCR-based Burned-in Metadata Extractor

Handles images/videos where metadata is visually overlaid on pixels:
- GPS map overlays (like GPS Map Camera app)
- Timestamp watermarks
- Location/address text
- Weather data overlays
- Camera app watermarks
- Social media overlays

Uses OCR (Tesseract) and pattern matching to extract burned-in data.
"""

import os
import re
import shutil
import subprocess
import tempfile
import uuid
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
import logging
from datetime import datetime

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_extraction_event(
    event_type: str,
    filepath: str,
    module_name: str,
    status: str = "info",
    details: Optional[Dict[str, Any]] = None,
    duration: Optional[float] = None
) -> None:
    """
    Log a comprehensive extraction event with detailed information.

    Args:
        event_type: Type of event (e.g., 'extraction_start', 'extraction_complete', 'error')
        filepath: Path to the file being processed
        module_name: Name of the module processing the file
        status: Log level ('debug', 'info', 'warning', 'error', 'critical')
        details: Additional details about the event
        duration: Processing duration in seconds (if applicable)
    """
    file_size = "unknown"
try:
        if Path(filepath).exists():
            file_size = Path(filepath).stat().st_size
    except:
        pass

    log_message = f"[{event_type}] File: {filepath}, Module: {module_name}, Size: {file_size}"
    if duration is not None:
        log_message += f", Duration: {duration:.3f}s"
    if details:
        log_message += f", Details: {details}"

    # Map status to appropriate logger method
    if status.lower() == 'debug':
        logger.debug(log_message)
    elif status.lower() == 'warning':
        logger.warning(log_message)
    elif status.lower() == 'error':
        logger.error(log_message)
    elif status.lower() == 'critical':
        logger.critical(log_message)
    else:  # default to info
        logger.info(log_message)


class BurnedMetadataExtractor:
    """Extracts metadata that is visually burned into image pixels."""

    _MAX_REASONABLE_SPEED_KMH = 200.0
    
    def __init__(self):
        self.tesseract_available = self._check_tesseract()
        
    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is installed."""
        try:
            result = subprocess.run(
                ['tesseract', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def extract(self, filepath: str) -> Dict[str, Any]:
        """
        Extract burned-in metadata from image.

        Args:
            filepath: Path to image file

        Returns:
            Dictionary containing extracted burned-in metadata
        """
        start_time = datetime.now()

        # Log the start of the extraction
        log_extraction_event(
            event_type="burned_metadata_extraction_start",
            filepath=filepath,
            module_name="ocr_burned_metadata",
            status="info",
            details={"tesseract_available": self.tesseract_available}
        )

        try:
            result = {
                "has_burned_metadata": False,
                "ocr_available": self.tesseract_available,
                "extracted_text": None,
                "parsed_data": {},
                "confidence": "none",  # none, low, medium, high
                "processing_errors": []
            }

            if not self.tesseract_available:
                result["warning"] = "Tesseract OCR not installed - cannot extract burned-in metadata"
                log_extraction_event(
                    event_type="burned_metadata_extraction_complete",
                    filepath=filepath,
                    module_name="ocr_burned_metadata",
                    status="warning",
                    duration=(datetime.now() - start_time).total_seconds(),
                    details={"tesseract_available": False}
                )
                return result

            # Extract text using OCR
            ocr_text = self._run_ocr(filepath)
            if not ocr_text:
                log_extraction_event(
                    event_type="burned_metadata_extraction_complete",
                    filepath=filepath,
                    module_name="ocr_burned_metadata",
                    status="info",
                    duration=(datetime.now() - start_time).total_seconds(),
                    details={"tesseract_available": True, "ocr_text_found": False}
                )
                return result

            result["extracted_text"] = ocr_text
            result["has_burned_metadata"] = True

            # Parse extracted text for structured data
            try:
                parsed = self._parse_ocr_text(ocr_text)
                result["parsed_data"] = parsed
            except Exception as e:
                logger.error(f"Error parsing OCR text for {filepath}: {e}")
                result["processing_errors"].append({
                    "component": "text_parsing",
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                parsed = {}

            # Determine confidence based on what we found
            try:
                result["confidence"] = self._calculate_confidence(parsed)
            except Exception as e:
                logger.error(f"Error calculating confidence for {filepath}: {e}")
                result["processing_errors"].append({
                    "component": "confidence_calculation",
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                result["confidence"] = "none"

            duration = (datetime.now() - start_time).total_seconds()
            log_extraction_event(
                event_type="burned_metadata_extraction_complete",
                filepath=filepath,
                module_name="ocr_burned_metadata",
                status="info",
                duration=duration,
                details={
                    "tesseract_available": True,
                    "has_burned_metadata": result["has_burned_metadata"],
                    "confidence": result["confidence"],
                    "parsed_data_count": len(result["parsed_data"])
                }
            )

            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Critical error in burned metadata extraction for {filepath}: {e}")
            logger.debug(f"Full traceback: {__import__('traceback').format_exc()}")

            log_extraction_event(
                event_type="burned_metadata_extraction_error",
                filepath=filepath,
                module_name="ocr_burned_metadata",
                status="error",
                duration=duration,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )

            return {
                "error": f"Critical error in burned metadata extraction: {str(e)}",
                "error_type": type(e).__name__,
                "file": {"path": filepath},
                "has_burned_metadata": False,
                "ocr_available": self.tesseract_available,
                "extracted_text": None,
                "parsed_data": {},
                "confidence": "none"
            }
    
    def _run_ocr(self, filepath: str) -> Optional[str]:
        """Run Tesseract OCR on image."""
        start_time = datetime.now()

        log_extraction_event(
            event_type="ocr_start",
            filepath=filepath,
            module_name="ocr_burned_metadata_ocr",
            status="info",
            details={"file_path": filepath}
        )

        path = Path(filepath)
        if not path.exists():
            logger.warning(f"OCR file missing: {filepath}")
            log_extraction_event(
                event_type="ocr_error",
                filepath=filepath,
                module_name="ocr_burned_metadata_ocr",
                status="warning",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": "File not found", "error_type": "FileNotFoundError"}
            )
            return None

        try:
            resized_path = self._prepare_ocr_image(path)
            text, error = self._run_tesseract(resized_path)
            if text is not None:
                duration = (datetime.now() - start_time).total_seconds()
                log_extraction_event(
                    event_type="ocr_complete",
                    filepath=filepath,
                    module_name="ocr_burned_metadata_ocr",
                    status="info",
                    duration=duration,
                    details={"success": True, "output_length": len(text.strip())}
                )
                return text
            if not self._should_retry_with_copy(path, error):
                duration = (datetime.now() - start_time).total_seconds()
                if error:
                    logger.warning(f"Tesseract failed for {filepath}: {error}")
                log_extraction_event(
                    event_type="ocr_error",
                    filepath=filepath,
                    module_name="ocr_burned_metadata_ocr",
                    status="warning",
                    duration=duration,
                    details={"error": error or "Tesseract failed", "success": False}
                )
                return None

            fallback_path = self._copy_for_ocr(path)
            if not fallback_path:
                duration = (datetime.now() - start_time).total_seconds()
                if error:
                    logger.warning(f"Tesseract failed for {filepath}: {error}")
                log_extraction_event(
                    event_type="ocr_error",
                    filepath=filepath,
                    module_name="ocr_burned_metadata_ocr",
                    status="warning",
                    duration=duration,
                    details={"error": error or "Failed to create fallback copy", "success": False}
                )
                return None
            try:
                fallback_text, fallback_error = self._run_tesseract(fallback_path)
                if fallback_text is not None:
                    duration = (datetime.now() - start_time).total_seconds()
                    log_extraction_event(
                        event_type="ocr_complete",
                        filepath=filepath,
                        module_name="ocr_burned_metadata_ocr",
                        status="info",
                        duration=duration,
                        details={"success": True, "output_length": len(fallback_text.strip()), "method": "fallback_copy"}
                    )
                    return fallback_text
                if fallback_error:
                    logger.warning(f"Tesseract failed on fallback copy for {filepath}: {fallback_error}")
                duration = (datetime.now() - start_time).total_seconds()
                log_extraction_event(
                    event_type="ocr_error",
                    filepath=filepath,
                    module_name="ocr_burned_metadata_ocr",
                    status="warning",
                    duration=duration,
                    details={"error": fallback_error or "Tesseract failed on fallback", "success": False, "method": "fallback_copy"}
                )
                return None
            finally:
                try:
                    fallback_path.unlink()
                except OSError:
                    logger.debug(f"Failed to clean up OCR temp file: {fallback_path}")

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"OCR timeout for {filepath} after {duration:.2f}s")
            log_extraction_event(
                event_type="ocr_timeout",
                filepath=filepath,
                module_name="ocr_burned_metadata_ocr",
                status="error",
                duration=duration,
                details={"timeout": True}
            )
            return None
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"OCR error for {filepath}: {e}")
            log_extraction_event(
                event_type="ocr_error",
                filepath=filepath,
                module_name="ocr_burned_metadata_ocr",
                status="error",
                duration=duration,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            return None

    def _run_tesseract(self, path: Path) -> Tuple[Optional[str], Optional[str]]:
        """Run tesseract and return (text, error)."""
        result = subprocess.run(
            ['tesseract', str(path), 'stdout'],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )

        if result.returncode == 0:
            text = result.stdout.strip()
            return (text if text else None), None

        error = result.stderr.strip() if result.stderr else "tesseract failed"
        return None, error

    def _prepare_ocr_image(self, path: Path) -> Path:
        """
        Prepare a resized, orientation-corrected image for OCR.
        Returns a temp file path (original if resize not possible).
        """
        max_dim_env = os.getenv("METAEXTRACT_MAX_DIM")
        try:
            max_dim = int(max_dim_env) if max_dim_env and max_dim_env.isdigit() else 2048
        except Exception:
            max_dim = 2048

        if Image is None:
            return path

        try:
            with Image.open(path) as img:
                if ImageOps:
                    try:
                        img = ImageOps.exif_transpose(img)
                    except Exception:
                        pass
                img = img.convert("RGB")

                if max(img.size) > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

                temp_dir = Path(tempfile.gettempdir()) / "metaextract-ocr"
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_path = temp_dir / f"ocr-{uuid.uuid4().hex}.png"
                img.save(temp_path, format="PNG")
                return temp_path
        except Exception as e:
            logger.debug(f"Failed to prepare resized OCR image, using original: {e}")

        return path

    def _should_retry_with_copy(self, path: Path, error: Optional[str]) -> bool:
        """Retry OCR from a readable temp location when paths are problematic."""
        if self._is_tmp_path(path):
            return True
        if not error:
            return False
        lowered = error.lower()
        return "permission" in lowered or "not found" in lowered or "unable to open" in lowered or "cannot open" in lowered

    def _is_tmp_path(self, path: Path) -> bool:
        """Check if the file resides in a temp directory that may be unreadable."""
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        resolved_str = str(resolved)
        return resolved_str.startswith("/tmp/") or resolved_str.startswith("/private/tmp/")

    def _copy_for_ocr(self, path: Path) -> Optional[Path]:
        """Copy file to a readable temp dir for OCR."""
        fallback_dir = self._get_ocr_tmp_dir()
        if not fallback_dir:
            return None
        try:
            with tempfile.NamedTemporaryFile(
                dir=str(fallback_dir),
                suffix=path.suffix,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
            shutil.copy2(path, temp_path)
            return temp_path
        except OSError as e:
            logger.warning(f"Failed to create OCR temp copy: {e}")
            return None

    def _get_ocr_tmp_dir(self) -> Optional[Path]:
        """Resolve OCR temp directory, falling back to repo-local temp."""
        env_dir = os.environ.get("METAEXTRACT_OCR_TMP_DIR")
        if env_dir:
            target = Path(env_dir).expanduser()
        else:
            target = Path(__file__).resolve().parents[3] / "tmp_ocr"
        try:
            target.mkdir(parents=True, exist_ok=True)
            return target
        except OSError as e:
            logger.warning(f"Failed to create OCR temp dir {target}: {e}")
            return None
    
    def _parse_ocr_text(self, text: str) -> Dict[str, Any]:
        """Parse OCR text to extract structured metadata."""
        parsed = {}
        errors = []
        normalized_text = ""

        try:
            normalized_text = re.sub(r'\s+', ' ', text).strip()
        except re.error as e:
            errors.append({
                "component": "text_normalization",
                "error": str(e),
                "error_type": type(e).__name__
            })

        try:
            # GPS Coordinates (various formats)
            gps_patterns = [
                # "Lat 12.923974° Long 77.625419°"
                r'Lat\s+([-+]?\d+\.?\d*)[°]?\s+Long\s+([-+]?\d+\.?\d*)[°]?',
                # "12.923974, 77.625419"
                r'([-+]?\d+\.\d+)[,\s]+([-+]?\d+\.\d+)',
                # "N 12°55'26.3" E 77°37'31.5""
                r'([NS])\s*(\d+)°\s*(\d+)[\'′]\s*([\d.]+)[\"″].*?([EW])\s*(\d+)°\s*(\d+)[\'′]\s*([\d.]+)[\"″]',
            ]

            for pattern in gps_patterns:
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        parsed["gps"] = self._parse_gps_match(match, pattern)
                        break
                except re.error as e:
                    errors.append({
                        "component": "gps_parsing",
                        "pattern": pattern,
                        "error": str(e),
                        "error_type": type(e).__name__
                    })

            # Location/Address
            # Look for common location patterns
            location_pattern = r'([A-Za-z][A-Za-z .\'-]+?),\s*([A-Za-z][A-Za-z .\'-]+?),\s*([A-Za-z][A-Za-z .\'-]+)'
            location_match = None
            try:
                for line in text.splitlines():
                    match = re.search(location_pattern, line)
                    if match and not re.search(r'\d', ''.join(match.groups())):
                        location_match = match
                        break
                if not location_match:
                    match = re.search(location_pattern, normalized_text)
                    if match and not re.search(r'\d', ''.join(match.groups())):
                        location_match = match
                if location_match:
                    parsed["location"] = {
                        "city": location_match.group(1).strip(),
                        "state": location_match.group(2).strip(),
                        "country": location_match.group(3).strip()
                    }
            except re.error as e:
                errors.append({
                    "component": "location_parsing",
                    "error": str(e),
                    "error_type": type(e).__name__
                })

            try:
                plus_match = re.search(r'Plus\s*Code\s*:?\s*([A-Z0-9+ ]{6,})', normalized_text, re.IGNORECASE)
                if plus_match:
                    plus_code_raw = plus_match.group(1).upper()
                    plus_code = re.sub(r'[^A-Z0-9+]', '', plus_code_raw)
                    if plus_code:
                        parsed["plus_code"] = plus_code
            except re.error as e:
                errors.append({
                    "component": "plus_code_parsing",
                    "error": str(e),
                    "error_type": type(e).__name__
                })

            # Full address (more flexible)
            if "location" not in parsed:
                # Try to find address-like text
                address_match = None
                try:
                    for line in text.splitlines():
                        if re.search(r'\d{5,6}', line) and line.count(',') >= 2:
                            address_match = line.strip()
                            break
                    if not address_match:
                        match = re.search(
                            r'([A-Za-z0-9][A-Za-z0-9 .,\-/]{10,}\b\d{5,6}\b[ A-Za-z0-9.,\-/]{0,80})',
                            normalized_text
                        )
                        if match:
                            address_match = match.group(1).strip()
                    if address_match:
                        parsed["address"] = address_match
                except re.error as e:
                    errors.append({
                        "component": "address_parsing",
                        "error": str(e),
                        "error_type": type(e).__name__
                    })

            # Timestamp
            timestamp_patterns = [
                r'(\w+day),\s*(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)\s*GMT\s*([-+]\d{2}:\d{2})',
                r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})',
                r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)',
            ]

            for pattern in timestamp_patterns:
                try:
                    match = re.search(pattern, text)
                    if match:
                        parsed["timestamp"] = match.group(0)
                        break
                except re.error as e:
                    errors.append({
                        "component": "timestamp_parsing",
                        "pattern": pattern,
                        "error": str(e),
                        "error_type": type(e).__name__
                    })

            # Weather data
            weather_patterns = {
                "temperature": r'([-+]?\d+\.?\d*)[°]?\s*[CF]',
                "humidity": r'(\d+)%',
                "speed": r'([\d.]+)\s*km/h',
                "altitude": r'(\d+)\s*m',
            }

            for key, pattern in weather_patterns.items():
                try:
                    match = re.search(pattern, text)
                    if match:
                        if "weather" not in parsed:
                            parsed["weather"] = {}
                        value = match.group(1)
                        if key == "speed":
                            try:
                                speed = float(value)
                            except ValueError:
                                continue
                            if speed > self._MAX_REASONABLE_SPEED_KMH:
                                continue
                        parsed["weather"][key] = value
                except re.error as e:
                    errors.append({
                        "component": f"weather_{key}_parsing",
                        "pattern": pattern,
                        "error": str(e),
                        "error_type": type(e).__name__
                    })

            # Compass direction
            try:
                compass_match = re.search(r'(\d+)\s*°\s*([NSEW]{1,2})', normalized_text, re.IGNORECASE)
                if compass_match:
                    parsed["compass"] = {
                        "degrees": compass_match.group(1),
                        "direction": compass_match.group(2).upper()
                    }
            except re.error as e:
                errors.append({
                    "component": "compass_parsing",
                    "error": str(e),
                    "error_type": type(e).__name__
                })

            # Camera/App watermark
            camera_apps = [
                'GPS Map Camera', 'Timestamp Camera', 'GPS Camera',
                'GeoTag', 'Camera+', 'ProCamera', 'Halide'
            ]
            for app in camera_apps:
                if app.lower() in text.lower():
                    parsed["camera_app"] = app
                    break

        except Exception as e:
            errors.append({
                "component": "general_parsing",
                "error": str(e),
                "error_type": type(e).__name__
            })

        # Add errors to result if any occurred
        if errors:
            parsed["parsing_errors"] = errors

        return parsed
    
    def _parse_gps_match(self, match, pattern_used: str) -> Dict[str, Any]:
        """Parse GPS coordinates from regex match."""
        gps = {}
        
        if 'Lat' in pattern_used:
            # Decimal format
            gps["latitude"] = float(match.group(1))
            gps["longitude"] = float(match.group(2))
        elif '[-+]?\\d+\\.\\d+' in pattern_used and 'Long' not in pattern_used:
            # Simple decimal pair
            gps["latitude"] = float(match.group(1))
            gps["longitude"] = float(match.group(2))
        elif '[NS]' in pattern_used:
            # DMS format
            lat_deg = int(match.group(2))
            lat_min = int(match.group(3))
            lat_sec = float(match.group(4))
            lat_dir = match.group(1)
            
            lon_deg = int(match.group(6))
            lon_min = int(match.group(7))
            lon_sec = float(match.group(8))
            lon_dir = match.group(5)
            
            # Convert to decimal
            lat = lat_deg + lat_min/60 + lat_sec/3600
            if lat_dir == 'S':
                lat = -lat
            
            lon = lon_deg + lon_min/60 + lon_sec/3600
            if lon_dir == 'W':
                lon = -lon
            
            gps["latitude"] = lat
            gps["longitude"] = lon
            gps["format"] = "dms"
        
        # Add Google Maps URL
        if "latitude" in gps and "longitude" in gps:
            gps["google_maps_url"] = f"https://www.google.com/maps?q={gps['latitude']},{gps['longitude']}"
        
        return gps
    
    def _calculate_confidence(self, parsed: Dict[str, Any]) -> str:
        """Calculate confidence level based on extracted data."""
        score = 0
        
        if "gps" in parsed:
            score += 3
        if "location" in parsed or "address" in parsed:
            score += 2
        if "timestamp" in parsed:
            score += 2
        if "weather" in parsed:
            score += 1
        if "camera_app" in parsed:
            score += 1
        
        if score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        elif score >= 1:
            return "low"
        else:
            return "none"


def extract_burned_metadata(filepath: str) -> Dict[str, Any]:
    """
    Main entry point for burned-in metadata extraction.

    Args:
        filepath: Path to image file

    Returns:
        Dictionary with burned-in metadata
    """
    extractor = BurnedMetadataExtractor()
    return extractor.extract(filepath)


async def extract_burned_metadata_async(filepath: str) -> Dict[str, Any]:
    """
    Async entry point for burned-in metadata extraction.

    Args:
        filepath: Path to image file

    Returns:
        Dictionary with burned-in metadata
    """
    import asyncio
    loop = asyncio.get_event_loop()

    start_time = datetime.now()

    log_extraction_event(
        event_type="async_burned_metadata_extraction_start",
        filepath=filepath,
        module_name="ocr_burned_metadata_async",
        status="info",
        details={"file_path": filepath}
    )

    try:
        # Run the synchronous extraction in a thread pool to avoid blocking the event loop
        extractor = BurnedMetadataExtractor()
        result = await loop.run_in_executor(
            None,
            extractor.extract,
            filepath
        )

        duration = (datetime.now() - start_time).total_seconds()
        log_extraction_event(
            event_type="async_burned_metadata_extraction_complete",
            filepath=filepath,
            module_name="ocr_burned_metadata_async",
            status="info",
            duration=duration,
            details={
                "success": "error" not in result,
                "has_burned_metadata": result.get("has_burned_metadata", False),
                "confidence": result.get("confidence", "none")
            }
        )

        return result
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Critical error in async burned metadata extraction for {filepath}: {e}")
        logger.debug(f"Full traceback: {__import__('traceback').format_exc()}")

        log_extraction_event(
            event_type="async_burned_metadata_extraction_error",
            filepath=filepath,
            module_name="ocr_burned_metadata_async",
            status="error",
            duration=duration,
            details={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )

        return {
            "error": f"Critical error in async burned metadata extraction: {str(e)}",
            "error_type": type(e).__name__,
            "file": {"path": filepath},
            "has_burned_metadata": False,
            "ocr_available": False,
            "extracted_text": None,
            "parsed_data": {},
            "confidence": "none"
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_burned_metadata(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python ocr_burned_metadata.py <image_file>")
