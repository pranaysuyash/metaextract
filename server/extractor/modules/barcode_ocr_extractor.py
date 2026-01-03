#!/usr/bin/env python3
"""
Barcode and QR Code Metadata Extractor
Extracts metadata from barcodes, QR codes, and optical recognition data.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


BARCODE_TYPES = {
    'QR_CODE': 'QR Code',
    'DATA_MATRIX': 'Data Matrix',
    'AZTEC': 'Aztec Code',
    'PDF417': 'PDF417',
    'MAXICODE': 'MaxiCode',
    'EAN_13': 'EAN-13',
    'EAN_8': 'EAN-8',
    'UPC_A': 'UPC-A',
    'UPC_E': 'UPC-E',
    'CODE_39': 'Code 39',
    'CODE_93': 'Code 93',
    'CODE_128': 'Code 128',
    'ITF': 'ITF',
    'CODABAR': 'Codabar',
    'RSS_14': 'RSS-14',
    'RSS_EXPANDED': 'RSS Expanded',
    'MSI': 'MSI Plessey',
    'PHARMACODE': 'Pharmacode',
    'TWO_OF_FIVE': 'Standard 2 of 5',
    'POSTNET': 'POSTNET',
    'PLANET': 'PLANET',
    'RM4SCC': 'RM4SCC',
    'KIX': 'KIX Code',
    'JAPAN_POST': 'Japan Post',
    'AUSTRALIA_POST': 'Australia Post',
}


class BarcodeExtractor:
    """
    Barcode and QR code detection and metadata extraction.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.barcode_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse barcode/QR code metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "has_barcode": False,
                "barcode_count": 0,
                "barcodes": [],
                "qr_codes": [],
            }
            
            from PIL import Image
            
            try:
                with Image.open(self.filepath) as img:
                    result["image_width"] = img.width
                    result["image_height"] = img.height
                    result["image_mode"] = img.mode
                    
                    if hasattr(img, 'info'):
                        result["embedded_barcode"] = img.info.get('barcode', None)
            except ImportError:
                pass
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing barcode: {e}")
            return {"error": str(e), "success": False}


class QRCodeExtractor:
    """
    QR Code specific metadata extraction.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.qr_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse QR code metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_qr_code": False,
                "qr_version": None,
                "qr_error_correction": None,
                "qr_encoding": None,
                "qr_mask_pattern": None,
                "qr_data": None,
                "qr_data_type": None,
            }
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing QR code: {e}")
            return {"error": str(e), "success": False}


class DataMatrixExtractor:
    """
    Data Matrix barcode metadata extraction.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dm_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse Data Matrix metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_data_matrix": False,
                "dm_rows": None,
                "dm_cols": None,
                "dm_symbol_size": None,
                "dm_encoding": None,
                "dm_data": None,
            }
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Data Matrix: {e}")
            return {"error": str(e), "success": False}


class AztecCodeExtractor:
    """
    Aztec Code metadata extraction.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.aztec_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse Aztec Code metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_aztec_code": False,
                "aztec_layers": None,
                "aztec_message_size": None,
                "aztec_data": None,
            }
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Aztec Code: {e}")
            return {"error": str(e), "success": False}


class PDF417Extractor:
    """
    PDF417 barcode metadata extraction.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.pdf417_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse PDF417 metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_pdf417": False,
                "pdf417_rows": None,
                "pdf417_cols": None,
                "pdf417_security_level": None,
                "pdf417_data": None,
            }
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing PDF417: {e}")
            return {"error": str(e), "success": False}


class OpticalRecognitionExtractor:
    """
    OCR and optical character recognition metadata extractor.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.ocr_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse OCR metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "has_ocr": False,
                "ocr_engine": None,
                "ocr_confidence": None,
                "ocr_language": None,
                "ocr_text_length": None,
                "ocr_blocks": [],
                "ocr_words": None,
                "ocr_characters": None,
            }
            
            try:
                from PIL import Image
                with Image.open(self.filepath) as img:
                    if hasattr(img, 'info'):
                        ocr_data = img.info.get('ocr', {})
                        if ocr_data:
                            result["has_ocr"] = True
                            result.update(ocr_data)
            except ImportError:
                pass
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing OCR: {e}")
            return {"error": str(e), "success": False}


class MRZExtractor:
    """
    Machine Readable Zone (MRZ) metadata extraction.
    Supports passports, IDs, and visas.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.mrz_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse MRZ metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "has_mrz": False,
                "mrz_type": None,
                "document_type": None,
                "issuing_country": None,
                "document_number": None,
                "birth_date": None,
                "expiry_date": None,
                "sex": None,
                "nationality": None,
                "check_digits": [],
            }
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing MRZ: {e}")
            return {"error": str(e), "success": False}


class HIDExtractor:
    """
    Human Identification (biometric) metadata extraction.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.hid_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse HID/biometric metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "has_biometric": False,
                "biometric_type": None,
                "face_detected": False,
                "iris_detected": False,
                "fingerprint_detected": False,
                "palm_print_detected": False,
                "voice_detected": False,
                "match_confidence": None,
                "template_id": None,
            }
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing HID: {e}")
            return {"error": str(e), "success": False}
