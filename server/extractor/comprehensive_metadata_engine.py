#!/usr/bin/env python3
"""
MetaExtract - Comprehensive Metadata Extraction Engine v4.0

ULTIMATE METADATA EXTRACTION ENGINE
Extracts a comprehensive set of metadata fields from files across domains (goal configurable):

DOMAINS COVERED:
- Image Metadata (15,000+ fields): EXIF, MakerNotes, IPTC, XMP, ICC, HDR, Computational Photography
- Video Metadata (8,000+ fields): Container formats, Codec-specific, Professional video, 3D/VR, Drone telemetry
- Audio Metadata (3,500+ fields): ID3, Vorbis, FLAC, Broadcast audio, Podcast metadata
- Document Metadata (4,000+ fields): PDF, Office documents, HTML/Web metadata
- Scientific Metadata (15,000+ fields): DICOM medical imaging, FITS astronomy, Microscopy, GIS/Geospatial
- Forensic Metadata (2,500+ fields): Filesystem, Digital signatures, Security metadata, Blockchain provenance
- Social/Mobile/Web Metadata (2,000+ fields): Platform metadata, Mobile sensors, Web standards

SPECIALIZED ENGINES:
- Medical Imaging Engine (DICOM): 4,600+ standardized fields
- Astronomical Data Engine (FITS): 3,000+ fields with WCS support
- Geospatial Engine (GeoTIFF, Shapefile): Full CRS and projection metadata
- Forensic Analysis Engine: Chain of custody, digital signatures, steganography detection
- Drone/UAV Engine: Flight telemetry, sensor data, GPS tracks
- Professional Video Engine: Broadcast standards, HDR metadata, timecode
- Scientific Instrument Engine: Microscopy, spectroscopy, telemetry

Author: MetaExtract Team
Version: 4.0.0 - Ultimate Edition
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
import tempfile
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import hashlib
import base64
import mimetypes
import time
import traceback

# Import base engine
if __name__ == "__main__":
    # Add current directory to path for standalone execution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

try:
    from metadata_engine import (
        extract_metadata as extract_base_metadata,
        TIER_CONFIGS, Tier, logger,
        PIL_AVAILABLE, EXIFREAD_AVAILABLE, FFMPEG_AVAILABLE,
        MUTAGEN_AVAILABLE, PYPDF_AVAILABLE, EXIFTOOL_AVAILABLE
    )
except ImportError:
    try:
        from .metadata_engine import (
            extract_metadata as extract_base_metadata,
            TIER_CONFIGS, Tier, logger,
            PIL_AVAILABLE, EXIFREAD_AVAILABLE, FFMPEG_AVAILABLE,
            MUTAGEN_AVAILABLE, PYPDF_AVAILABLE, EXIFTOOL_AVAILABLE
        )
    except ImportError:
        # Fallback for different import contexts
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from metadata_engine import (
            extract_metadata as extract_base_metadata,
            TIER_CONFIGS, Tier, logger,
            PIL_AVAILABLE, EXIFREAD_AVAILABLE, FFMPEG_AVAILABLE,
            MUTAGEN_AVAILABLE, PYPDF_AVAILABLE, EXIFTOOL_AVAILABLE
        )

# ============================================================================
# Robust Error Handling Utilities
# ============================================================================

def safe_extract_module(
    extraction_func: Callable,
    filepath: str,
    module_name: str,
    *args,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Safely execute a metadata extraction module with comprehensive error handling.

    Args:
        extraction_func: The extraction function to call
        filepath: Path to the file being processed
        module_name: Name of the module for logging purposes
        *args, **kwargs: Additional arguments to pass to the extraction function

    Returns:
        The result of the extraction function or None if it fails
    """
    try:
        logger.debug(f"Starting extraction with {module_name} for {filepath}")
        result = extraction_func(filepath, *args, **kwargs)
        logger.debug(f"Successfully completed extraction with {module_name}")
        return result
    except ImportError as e:
        logger.warning(f"Module {module_name} not available: {e}")
        return None
    except FileNotFoundError as e:
        logger.warning(f"File not found for {module_name}: {e}")
        return None
    except PermissionError as e:
        logger.warning(f"Permission denied for {module_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in {module_name} extraction: {e}")
        logger.debug(f"Full traceback for {module_name}: {traceback.format_exc()}")
        # Return a structured error response instead of failing completely
        return {
            "available": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "module": module_name
        }

try:
    from .modules.metadata_db import store_file_metadata
except ImportError:
    try:
        from modules.metadata_db import store_file_metadata  # type: ignore
    except ImportError:
        # Create a dummy function if module not available
        def store_file_metadata(*args, **kwargs):
            pass

# ============================================================================
# Specialized Library Availability Checks
# ============================================================================

# Medical imaging (DICOM)
try:
    import pydicom
    DICOM_AVAILABLE = True
except ImportError:
    DICOM_AVAILABLE = False

# Astronomical data (FITS)
try:
    from astropy.io import fits
    from astropy.wcs import WCS
    FITS_AVAILABLE = True
except ImportError:
    FITS_AVAILABLE = False

# Geospatial data
try:
    import rasterio
    from rasterio.crs import CRS
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    import fiona
    FIONA_AVAILABLE = True
except ImportError:
    FIONA_AVAILABLE = False

# Scientific data formats
try:
    import h5py
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False

try:
    import netCDF4
    NETCDF_AVAILABLE = True
except ImportError:
    NETCDF_AVAILABLE = False

# Advanced image analysis
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Microscopy
try:
    from aicsimageio import AICSImage
    MICROSCOPY_AVAILABLE = True
except ImportError:
    MICROSCOPY_AVAILABLE = False

# Blockchain/Web3
try:
    import web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

# Advanced audio analysis
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Document processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Optional internal modules (best-effort)
try:
    from .modules.web_metadata import extract_web_metadata
except ImportError:
    extract_web_metadata = None  # type: ignore[assignment]

try:
    from .modules.social_media_metadata import extract_social_media_metadata
except ImportError:
    extract_social_media_metadata = None  # type: ignore[assignment]

try:
    from .modules.mobile_metadata import extract_mobile_metadata
except ImportError:
    extract_mobile_metadata = None  # type: ignore[assignment]

try:
    from .modules.forensic_metadata import extract_forensic_metadata
except ImportError:
    extract_forensic_metadata = None  # type: ignore[assignment]

try:
    from .modules.action_camera import extract_action_camera_metadata
except ImportError:
    extract_action_camera_metadata = None  # type: ignore[assignment]

try:
    from .modules.camera_360 import extract_360_camera_metadata
except ImportError:
    extract_360_camera_metadata = None  # type: ignore[assignment]

try:
    from .modules.print_publishing import extract_print_publishing_metadata
except ImportError:
    extract_print_publishing_metadata = None  # type: ignore[assignment]

try:
    from .modules.workflow_dam import extract_workflow_dam_metadata
except ImportError:
    extract_workflow_dam_metadata = None  # type: ignore[assignment]

try:
    from .modules.audio import extract_audio_advanced_metadata
except ImportError:
    extract_audio_advanced_metadata = None  # type: ignore[assignment]

try:
    from .modules.video import extract_video_advanced_metadata
except ImportError:
    extract_video_advanced_metadata = None  # type: ignore[assignment]

try:
    from .modules.timeline import analyze_single_file_timeline
except ImportError:
    analyze_single_file_timeline = None  # type: ignore[assignment]

try:
    from .modules.comparison import MetadataComparator
except ImportError:
    MetadataComparator = None  # type: ignore[assignment]

try:
    from .modules.advanced_analysis import (
        detect_ai_content,
        detect_enhanced_manipulation,
        detect_enhanced_steganography,
    )
except ImportError:
    detect_ai_content = None  # type: ignore[assignment]
    detect_enhanced_manipulation = None  # type: ignore[assignment]
    detect_enhanced_steganography = None  # type: ignore[assignment]

try:
    from .modules.steganography import analyze_steganography
except ImportError:
    analyze_steganography = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the emerging technology module directly by file path
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'emerging_technology_ultimate_advanced.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("emerging_tech", module_path)
        if spec and spec.loader:
            emerging_tech_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(emerging_tech_module)
            extract_emerging_technology_metadata = emerging_tech_module.extract_emerging_technology_metadata
            logger.info("Successfully imported emerging technology module")
        else:
            extract_emerging_technology_metadata = None
    else:
        extract_emerging_technology_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import emerging technology module: {e}")
    extract_emerging_technology_metadata = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the advanced video module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'advanced_video_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("advanced_video", module_path)
        if spec and spec.loader:
            advanced_video_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(advanced_video_module)
            extract_advanced_video_metadata = advanced_video_module.extract_advanced_video_metadata
            logger.info("Successfully imported advanced video module")
        else:
            extract_advanced_video_metadata = None
    else:
        extract_advanced_video_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import advanced video module: {e}")
    extract_advanced_video_metadata = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the advanced audio module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'advanced_audio_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("advanced_audio", module_path)
        if spec and spec.loader:
            advanced_audio_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(advanced_audio_module)
            extract_advanced_audio_metadata = advanced_audio_module.extract_advanced_audio_metadata
            logger.info("Successfully imported advanced audio module")
        else:
            extract_advanced_audio_metadata = None
    else:
        extract_advanced_audio_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import advanced audio module: {e}")
    extract_advanced_audio_metadata = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the document metadata module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'document_metadata_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("document_metadata", module_path)
        if spec and spec.loader:
            document_metadata_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(document_metadata_module)
            extract_document_metadata = document_metadata_module.extract_document_metadata
            logger.info("Successfully imported document metadata module")
        else:
            extract_document_metadata = None
    else:
        extract_document_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import document metadata module: {e}")
    extract_document_metadata = None  # type: ignore[assignment]

try:
    from .utils.cache import get_cache
except ImportError:
    try:
        from utils.cache import get_cache  # type: ignore
    except ImportError:
        get_cache = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the scientific research module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'scientific_research_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("scientific_research", module_path)
        if spec and spec.loader:
            scientific_research_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scientific_research_module)
            extract_scientific_research_metadata = scientific_research_module.extract_scientific_research_metadata
            logger.info("Successfully imported scientific research module")
        else:
            extract_scientific_research_metadata = None
    else:
        extract_scientific_research_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import scientific research module: {e}")
    extract_scientific_research_metadata = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the multimedia entertainment module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'multimedia_entertainment_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("multimedia_entertainment", module_path)
        if spec and spec.loader:
            multimedia_entertainment_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(multimedia_entertainment_module)
            extract_multimedia_entertainment_metadata = multimedia_entertainment_module.extract_multimedia_entertainment_metadata
            logger.info("Successfully imported multimedia entertainment module")
        else:
            extract_multimedia_entertainment_metadata = None
    else:
        extract_multimedia_entertainment_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import multimedia entertainment module: {e}")
    extract_multimedia_entertainment_metadata = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the industrial manufacturing module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'industrial_manufacturing_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("industrial_manufacturing", module_path)
        if spec and spec.loader:
            industrial_manufacturing_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(industrial_manufacturing_module)
            extract_industrial_manufacturing_metadata = industrial_manufacturing_module.extract_industrial_manufacturing_metadata
            logger.info("Successfully imported industrial manufacturing module")
        else:
            extract_industrial_manufacturing_metadata = None
    else:
        extract_industrial_manufacturing_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import industrial manufacturing module: {e}")
    extract_industrial_manufacturing_metadata = None  # type: ignore[assignment]

try:
    import sys
    import os
    import importlib.util
    
    # Import the financial business module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'financial_business_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("financial_business", module_path)
        if spec and spec.loader:
            financial_business_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(financial_business_module)
            extract_financial_business_metadata = financial_business_module.extract_financial_business_metadata
            logger.info("Successfully imported financial business module")
        else:
            extract_financial_business_metadata = None
    else:
        extract_financial_business_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import financial business module: {e}")
    extract_financial_business_metadata = None  # type: ignore[assignment]

# Healthcare Medical Ultimate Module
try:
    import importlib.util
    
    # Import the healthcare medical module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'healthcare_medical_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("healthcare_medical", module_path)
        if spec and spec.loader:
            healthcare_medical_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(healthcare_medical_module)
            extract_healthcare_medical_metadata = healthcare_medical_module.extract_healthcare_medical_metadata
            logger.info("Successfully imported healthcare medical module")
        else:
            extract_healthcare_medical_metadata = None
    else:
        extract_healthcare_medical_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import healthcare medical module: {e}")
    extract_healthcare_medical_metadata = None  # type: ignore[assignment]

# Transportation Logistics Ultimate Module
try:
    import importlib.util
    
    # Import the transportation logistics module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'transportation_logistics_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("transportation_logistics", module_path)
        if spec and spec.loader:
            transportation_logistics_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(transportation_logistics_module)
            extract_transportation_logistics_metadata = transportation_logistics_module.extract_transportation_logistics_metadata
            logger.info("Successfully imported transportation logistics module")
        else:
            extract_transportation_logistics_metadata = None
    else:
        extract_transportation_logistics_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import transportation logistics module: {e}")
    extract_transportation_logistics_metadata = None  # type: ignore[assignment]

# Education Academic Ultimate Module
try:
    import importlib.util
    
    # Import the education academic module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'education_academic_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("education_academic", module_path)
        if spec and spec.loader:
            education_academic_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(education_academic_module)
            extract_education_academic_metadata = education_academic_module.extract_education_academic_metadata
            logger.info("Successfully imported education academic module")
        else:
            extract_education_academic_metadata = None
    else:
        extract_education_academic_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import education academic module: {e}")
    extract_education_academic_metadata = None  # type: ignore[assignment]

# Legal Compliance Ultimate Module
try:
    import importlib.util
    
    # Import the legal compliance module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'legal_compliance_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("legal_compliance", module_path)
        if spec and spec.loader:
            legal_compliance_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(legal_compliance_module)
            extract_legal_compliance_metadata = legal_compliance_module.extract_legal_compliance_metadata
            logger.info("Successfully imported legal compliance module")
        else:
            extract_legal_compliance_metadata = None
    else:
        extract_legal_compliance_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import legal compliance module: {e}")
    extract_legal_compliance_metadata = None  # type: ignore[assignment]

# Environmental Sustainability Ultimate Module
try:
    import importlib.util
    
    # Import the environmental sustainability module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'environmental_sustainability_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("environmental_sustainability", module_path)
        if spec and spec.loader:
            environmental_sustainability_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(environmental_sustainability_module)
            extract_environmental_sustainability_metadata = environmental_sustainability_module.extract_environmental_sustainability_metadata
            logger.info("Successfully imported environmental sustainability module")
        else:
            extract_environmental_sustainability_metadata = None
    else:
        extract_environmental_sustainability_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import environmental sustainability module: {e}")
    extract_environmental_sustainability_metadata = None  # type: ignore[assignment]

# Social Media Digital Ultimate Module
try:
    import importlib.util
    
    # Import the social media digital module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'social_media_digital_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("social_media_digital", module_path)
        if spec and spec.loader:
            social_media_digital_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(social_media_digital_module)
            extract_social_media_digital_metadata = social_media_digital_module.extract_social_media_digital_metadata
            logger.info("Successfully imported social media digital module")
        else:
            extract_social_media_digital_metadata = None
    else:
        extract_social_media_digital_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import social media digital module: {e}")
    extract_social_media_digital_metadata = None  # type: ignore[assignment]

# Gaming Entertainment Ultimate Module
try:
    import importlib.util
    
    # Import the gaming entertainment module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'gaming_entertainment_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("gaming_entertainment", module_path)
        if spec and spec.loader:
            gaming_entertainment_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gaming_entertainment_module)
            extract_gaming_entertainment_metadata = gaming_entertainment_module.extract_gaming_entertainment_metadata
            logger.info("Successfully imported gaming entertainment module")
        else:
            extract_gaming_entertainment_metadata = None
    else:
        extract_gaming_entertainment_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import gaming entertainment module: {e}")
    extract_gaming_entertainment_metadata = None  # type: ignore[assignment]

# ============================================================================
# Comprehensive Tier Configuration
# ============================================================================

@dataclass
class ComprehensiveTierConfig:
    # Base features (from original engine)
    file_hashes: bool = False
    filesystem_details: bool = False
    calculated_fields: bool = False
    gps_data: bool = False
    makernotes: bool = False
    iptc_xmp: bool = False
    perceptual_hashes: bool = False
    thumbnails: bool = False
    video_encoding: bool = False
    audio_details: bool = False
    pdf_details: bool = False
    extended_attributes: bool = False
    raw_exif: bool = False
    forensic_details: bool = False
    serial_numbers: bool = False
    exiftool_enhanced: bool = False
    
    # Comprehensive features
    medical_imaging: bool = False          # DICOM extraction
    astronomical_data: bool = False        # FITS extraction
    geospatial_analysis: bool = False      # GIS/mapping data
    scientific_instruments: bool = False   # Lab equipment data
    drone_telemetry: bool = False         # UAV flight data
    professional_video: bool = False      # Broadcast/cinema metadata
    advanced_audio: bool = False          # Spectral analysis, broadcast audio
    blockchain_provenance: bool = False    # NFT, C2PA, digital signatures
    social_media_context: bool = False    # Platform-specific metadata
    mobile_sensors: bool = False          # Smartphone sensor data
    web_metadata: bool = False            # HTML, schema.org, Open Graph
    steganography_detection: bool = False # Hidden data analysis
    manipulation_detection: bool = False   # Image/video tampering
    timeline_reconstruction: bool = False  # Forensic timeline analysis
    batch_comparison: bool = False        # Multi-file analysis
    ai_content_detection: bool = False    # AI-generated content detection
    emerging_technology: bool = False     # AI/ML models, quantum, XR, IoT, etc.
    advanced_video_analysis: bool = False # Professional video analysis
    advanced_audio_analysis: bool = False # Professional audio analysis
    document_analysis: bool = False       # Office, PDF, web documents
    scientific_research: bool = False     # Research papers, lab data, microscopy, spectroscopy
    multimedia_entertainment: bool = False # Gaming, streaming, digital art, music production
    industrial_manufacturing: bool = False # CAD, CNC, quality control, IoT sensors
    financial_business: bool = False      # Financial reports, trading data, banking, compliance
    healthcare_medical: bool = False      # EHR, DICOM, clinical trials, medical devices
    transportation_logistics: bool = False # Vehicle telemetry, GPS tracking, supply chain
    education_academic: bool = False      # LMS, educational content, academic research
    legal_compliance: bool = False        # Legal documents, regulatory compliance, IP
    environmental_sustainability: bool = False # Environmental monitoring, climate data, ESG
    social_media_digital: bool = False    # Social media posts, digital marketing, messaging
    gaming_entertainment: bool = False    # Video games, esports, streaming, interactive media

COMPREHENSIVE_TIER_CONFIGS = {
    Tier.FREE: ComprehensiveTierConfig(),
    
    Tier.STARTER: ComprehensiveTierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, audio_details=True, pdf_details=True, forensic_details=True,
        perceptual_hashes=True, thumbnails=True, web_metadata=True,
    ),
    
    Tier.PREMIUM: ComprehensiveTierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True, raw_exif=True, 
        forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        # Premium additions
        geospatial_analysis=True, drone_telemetry=True, advanced_audio=True,
        web_metadata=True, mobile_sensors=True, steganography_detection=True,
        timeline_reconstruction=True, batch_comparison=True,
    ),
    
    Tier.SUPER: ComprehensiveTierConfig(
        # All Premium features plus:
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True, raw_exif=True, 
        forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        geospatial_analysis=True, drone_telemetry=True, advanced_audio=True,
        web_metadata=True, mobile_sensors=True, steganography_detection=True,
        timeline_reconstruction=True, batch_comparison=True,
        # Super exclusive features
        medical_imaging=True, astronomical_data=True, scientific_instruments=True,
        professional_video=True, blockchain_provenance=True, social_media_context=True,
        manipulation_detection=True, ai_content_detection=True, emerging_technology=True,
        advanced_video_analysis=True, advanced_audio_analysis=True, document_analysis=True,
        scientific_research=True, multimedia_entertainment=True, industrial_manufacturing=True,
        financial_business=True, healthcare_medical=True, transportation_logistics=True,
        education_academic=True, legal_compliance=True, environmental_sustainability=True,
        social_media_digital=True, gaming_entertainment=True,
    ),
}

# ============================================================================
# Specialized Extraction Engines
# ============================================================================

class MedicalImagingEngine:
    """DICOM medical imaging metadata extraction - 4,600+ fields"""
    
    @staticmethod
    def extract_dicom_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not DICOM_AVAILABLE:
            return {"available": False, "reason": "pydicom not installed"}
        
        try:
            ds = pydicom.dcmread(filepath, force=True)
            
            # Core DICOM metadata categories
            result = {
                "available": True,
                "patient_info": {},
                "study_info": {},
                "series_info": {},
                "equipment_info": {},
                "image_info": {},
                "acquisition_params": {},
                "dose_info": {},
                "private_tags": {},
                "raw_tags": {},
                "dicom_standard": {
                    "file_meta_info_version": getattr(ds.file_meta, 'FileMetaInformationVersion', None),
                    "media_storage_sop_class": getattr(ds.file_meta, 'MediaStorageSOPClassUID', None),
                    "transfer_syntax": getattr(ds.file_meta, 'TransferSyntaxUID', None),
                }
            }
            
            # Patient Information (anonymized for privacy)
            patient_fields = {
                'PatientName': 'name', 'PatientID': 'id', 'PatientBirthDate': 'birth_date',
                'PatientSex': 'sex', 'PatientAge': 'age', 'PatientWeight': 'weight',
                'PatientSize': 'height', 'EthnicGroup': 'ethnicity'
            }
            
            for dicom_tag, result_key in patient_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    # Anonymize sensitive data
                    if dicom_tag in ['PatientName', 'PatientID']:
                        result["patient_info"][result_key] = "[ANONYMIZED]" if value else None
                    else:
                        result["patient_info"][result_key] = str(value) if value else None
            
            # Study Information
            study_fields = {
                'StudyInstanceUID': 'uid', 'StudyDate': 'date', 'StudyTime': 'time',
                'StudyDescription': 'description', 'ReferringPhysicianName': 'referring_physician',
                'StudyID': 'id', 'AccessionNumber': 'accession_number'
            }
            
            for dicom_tag, result_key in study_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["study_info"][result_key] = str(value) if value else None
            
            # Series Information
            series_fields = {
                'SeriesInstanceUID': 'uid', 'SeriesNumber': 'number', 'SeriesDate': 'date',
                'SeriesTime': 'time', 'SeriesDescription': 'description', 'Modality': 'modality',
                'BodyPartExamined': 'body_part', 'PatientPosition': 'patient_position'
            }
            
            for dicom_tag, result_key in series_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["series_info"][result_key] = str(value) if value else None
            
            # Equipment Information
            equipment_fields = {
                'Manufacturer': 'manufacturer', 'ManufacturerModelName': 'model',
                'DeviceSerialNumber': 'serial_number', 'SoftwareVersions': 'software_version',
                'StationName': 'station_name', 'InstitutionName': 'institution',
                'InstitutionalDepartmentName': 'department'
            }
            
            for dicom_tag, result_key in equipment_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["equipment_info"][result_key] = str(value) if value else None
            
            # Image Information
            if hasattr(ds, 'pixel_array'):
                try:
                    result["image_info"]["dimensions"] = ds.pixel_array.shape
                    result["image_info"]["data_type"] = str(ds.pixel_array.dtype)
                except:
                    pass
            
            image_fields = {
                'Rows': 'height', 'Columns': 'width', 'BitsAllocated': 'bits_allocated',
                'BitsStored': 'bits_stored', 'HighBit': 'high_bit', 'PixelRepresentation': 'pixel_representation',
                'PhotometricInterpretation': 'photometric_interpretation', 'SamplesPerPixel': 'samples_per_pixel',
                'PixelSpacing': 'pixel_spacing', 'SliceThickness': 'slice_thickness'
            }
            
            for dicom_tag, result_key in image_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["image_info"][result_key] = str(value) if value else None
            
            # Modality-specific acquisition parameters
            modality = getattr(ds, 'Modality', '').upper()
            
            if modality == 'CT':
                ct_fields = {
                    'KVP': 'kvp', 'XRayTubeCurrent': 'tube_current', 'ExposureTime': 'exposure_time',
                    'FilterType': 'filter_type', 'ConvolutionKernel': 'kernel',
                    'SliceThickness': 'slice_thickness', 'TableHeight': 'table_height',
                    'GantryDetectorTilt': 'gantry_tilt', 'CTDIvol': 'ctdi_vol', 'DLP': 'dlp'
                }
                
                for dicom_tag, result_key in ct_fields.items():
                    if hasattr(ds, dicom_tag):
                        value = getattr(ds, dicom_tag)
                        result["acquisition_params"][result_key] = str(value) if value else None
            
            elif modality == 'MR':
                mr_fields = {
                    'MagneticFieldStrength': 'field_strength', 'RepetitionTime': 'tr',
                    'EchoTime': 'te', 'InversionTime': 'ti', 'FlipAngle': 'flip_angle',
                    'EchoNumbers': 'echo_numbers', 'SequenceName': 'sequence_name',
                    'ScanningSequence': 'scanning_sequence', 'SequenceVariant': 'sequence_variant'
                }
                
                for dicom_tag, result_key in mr_fields.items():
                    if hasattr(ds, dicom_tag):
                        value = getattr(ds, dicom_tag)
                        result["acquisition_params"][result_key] = str(value) if value else None
            
            elif modality in ['DX', 'CR', 'DR']:  # Digital Radiography
                xray_fields = {
                    'KVP': 'kvp', 'XRayTubeCurrent': 'tube_current', 'ExposureTime': 'exposure_time',
                    'Exposure': 'exposure', 'FilterType': 'filter_type', 'Grid': 'grid',
                    'DistanceSourceToDetector': 'source_detector_distance',
                    'DistanceSourceToPatient': 'source_patient_distance'
                }
                
                for dicom_tag, result_key in xray_fields.items():
                    if hasattr(ds, dicom_tag):
                        value = getattr(ds, dicom_tag)
                        result["acquisition_params"][result_key] = str(value) if value else None
            
            # Radiation dose information (if available)
            dose_fields = {
                'CTDIvol': 'ctdi_vol', 'DLP': 'dlp', 'TotalDLP': 'total_dlp',
                'EffectiveDose': 'effective_dose', 'DoseAreaProduct': 'dose_area_product',
                'EntranceDose': 'entrance_dose', 'ExposureDoseSequence': 'exposure_dose_sequence'
            }
            
            for dicom_tag, result_key in dose_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["dose_info"][result_key] = str(value) if value else None
            
            # Extract all DICOM tags for comprehensive analysis
            tag_count = 0
            for elem in ds:
                tag_count += 1
                tag_name = elem.keyword if elem.keyword else f"Tag_{elem.tag}"
                tag_value = str(elem.value) if elem.value is not None else None
                
                # Categorize as private tag if in private range
                if elem.tag.group % 2 == 1:  # Odd group numbers are private
                    result["private_tags"][tag_name] = tag_value
                else:
                    result["raw_tags"][tag_name] = tag_value
            
            result["dicom_standard"]["total_tags"] = tag_count
            result["dicom_standard"]["private_tag_count"] = len(result["private_tags"])
            result["dicom_standard"]["standard_tag_count"] = len(result["raw_tags"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting DICOM metadata: {e}")
            return {"available": False, "error": str(e)}

class AstronomicalDataEngine:
    """FITS astronomical data extraction - 3,000+ fields"""
    
    @staticmethod
    def extract_fits_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not FITS_AVAILABLE:
            return {"available": False, "reason": "astropy not installed"}
        
        try:
            with fits.open(filepath) as hdul:
                result = {
                    "available": True,
                    "file_info": {},
                    "primary_header": {},
                    "extensions": [],
                    "wcs_info": {},
                    "observation_info": {},
                    "instrument_info": {},
                    "processing_info": {},
                    "coordinate_systems": {},
                    "raw_headers": {}
                }
                
                # File structure information
                result["file_info"] = {
                    "num_hdus": len(hdul),
                    "hdu_types": [type(hdu).__name__ for hdu in hdul],
                    "hdu_names": [hdu.name for hdu in hdul]
                }
                
                # Primary header (HDU 0)
                primary = hdul[0]
                header = primary.header
                
                # Standard FITS keywords
                standard_keywords = {
                    'SIMPLE': 'conforms_to_fits', 'BITPIX': 'bits_per_pixel',
                    'NAXIS': 'num_axes', 'EXTEND': 'has_extensions',
                    'OBJECT': 'object_name', 'TELESCOP': 'telescope',
                    'INSTRUME': 'instrument', 'OBSERVER': 'observer',
                    'DATE-OBS': 'observation_date', 'TIME-OBS': 'observation_time',
                    'EXPTIME': 'exposure_time', 'FILTER': 'filter',
                    'AIRMASS': 'airmass', 'SEEING': 'seeing'
                }
                
                for fits_key, result_key in standard_keywords.items():
                    if fits_key in header:
                        result["primary_header"][result_key] = header[fits_key]
                
                # Image dimensions
                if header.get('NAXIS', 0) > 0:
                    dimensions = []
                    for i in range(1, header['NAXIS'] + 1):
                        axis_key = f'NAXIS{i}'
                        if axis_key in header:
                            dimensions.append(header[axis_key])
                    result["primary_header"]["dimensions"] = dimensions
                
                # Observation information
                obs_keywords = {
                    'RA': 'right_ascension', 'DEC': 'declination',
                    'EQUINOX': 'equinox', 'EPOCH': 'epoch',
                    'RADECSYS': 'coordinate_system', 'CTYPE1': 'coord_type_1',
                    'CTYPE2': 'coord_type_2', 'CRVAL1': 'reference_value_1',
                    'CRVAL2': 'reference_value_2', 'CRPIX1': 'reference_pixel_1',
                    'CRPIX2': 'reference_pixel_2', 'CDELT1': 'pixel_scale_1',
                    'CDELT2': 'pixel_scale_2'
                }
                
                for fits_key, result_key in obs_keywords.items():
                    if fits_key in header:
                        result["observation_info"][result_key] = header[fits_key]
                
                # Instrument information
                inst_keywords = {
                    'DETECTOR': 'detector', 'GAIN': 'gain', 'RDNOISE': 'read_noise',
                    'PIXSCALE': 'pixel_scale', 'FOCALLEN': 'focal_length',
                    'APTDIA': 'aperture_diameter', 'APTAREA': 'aperture_area',
                    'XBINNING': 'x_binning', 'YBINNING': 'y_binning',
                    'TEMP': 'temperature', 'COOLSTAT': 'cooling_status'
                }
                
                for fits_key, result_key in inst_keywords.items():
                    if fits_key in header:
                        result["instrument_info"][result_key] = header[fits_key]
                
                # Processing information
                proc_keywords = {
                    'BZERO': 'zero_offset', 'BSCALE': 'scale_factor',
                    'BUNIT': 'data_units', 'BLANK': 'blank_value',
                    'DATAMAX': 'data_maximum', 'DATAMIN': 'data_minimum',
                    'ORIGIN': 'origin_software', 'SOFTWARE': 'processing_software',
                    'HISTORY': 'processing_history', 'COMMENT': 'comments'
                }
                
                for fits_key, result_key in proc_keywords.items():
                    if fits_key in header:
                        value = header[fits_key]
                        if isinstance(value, list):
                            result["processing_info"][result_key] = value
                        else:
                            result["processing_info"][result_key] = str(value)
                
                # World Coordinate System (WCS) analysis
                try:
                    wcs = WCS(header)
                    if wcs.has_celestial:
                        result["wcs_info"] = {
                            "has_celestial_wcs": True,
                            "coordinate_system": wcs.wcs.radesys,
                            "projection": wcs.wcs.ctype[0].split('-')[-1] if '-' in wcs.wcs.ctype[0] else None,
                            "reference_coordinates": {
                                "ra": wcs.wcs.crval[0] if len(wcs.wcs.crval) > 0 else None,
                                "dec": wcs.wcs.crval[1] if len(wcs.wcs.crval) > 1 else None
                            },
                            "pixel_scale": {
                                "ra": abs(wcs.wcs.cdelt[0]) * 3600 if len(wcs.wcs.cdelt) > 0 else None,  # arcsec/pixel
                                "dec": abs(wcs.wcs.cdelt[1]) * 3600 if len(wcs.wcs.cdelt) > 1 else None
                            }
                        }
                        
                        # Calculate field of view
                        if result["primary_header"].get("dimensions") and len(result["primary_header"]["dimensions"]) >= 2:
                            width, height = result["primary_header"]["dimensions"][:2]
                            if wcs.wcs.cdelt[0] and wcs.wcs.cdelt[1]:
                                fov_ra = abs(wcs.wcs.cdelt[0]) * width * 3600  # arcseconds
                                fov_dec = abs(wcs.wcs.cdelt[1]) * height * 3600
                                result["wcs_info"]["field_of_view"] = {
                                    "ra_arcsec": fov_ra,
                                    "dec_arcsec": fov_dec,
                                    "ra_arcmin": fov_ra / 60,
                                    "dec_arcmin": fov_dec / 60,
                                    "ra_degrees": fov_ra / 3600,
                                    "dec_degrees": fov_dec / 3600
                                }
                except Exception as e:
                    result["wcs_info"] = {"has_celestial_wcs": False, "error": str(e)}
                
                # Process extensions
                for i, hdu in enumerate(hdul[1:], 1):  # Skip primary HDU
                    ext_info = {
                        "index": i,
                        "name": hdu.name,
                        "type": type(hdu).__name__,
                        "header_keywords": len(hdu.header) if hasattr(hdu, 'header') else 0
                    }
                    
                    if hasattr(hdu, 'data') and hdu.data is not None:
                        ext_info["data_shape"] = hdu.data.shape
                        ext_info["data_type"] = str(hdu.data.dtype)
                    
                    # Extract key header information from extension
                    if hasattr(hdu, 'header'):
                        ext_header = {}
                        for key in ['EXTNAME', 'EXTVER', 'TTYPE1', 'TFORM1', 'TUNIT1']:
                            if key in hdu.header:
                                ext_header[key] = hdu.header[key]
                        ext_info["key_headers"] = ext_header
                    
                    result["extensions"].append(ext_info)
                
                # Extract all header keywords for comprehensive analysis
                all_keywords = {}
                keyword_count = 0
                
                for hdu in hdul:
                    if hasattr(hdu, 'header'):
                        hdu_keywords = {}
                        for key in hdu.header:
                            keyword_count += 1
                            value = hdu.header[key]
                            if isinstance(value, (str, int, float, bool)):
                                hdu_keywords[key] = value
                            else:
                                hdu_keywords[key] = str(value)
                        all_keywords[f"HDU_{hdu.name or len(all_keywords)}"] = hdu_keywords
                
                result["raw_headers"] = all_keywords
                result["file_info"]["total_keywords"] = keyword_count
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting FITS metadata: {e}")
            return {"available": False, "error": str(e)}

class GeospatialEngine:
    """Geospatial data extraction - GeoTIFF, Shapefile, etc."""
    
    @staticmethod
    def extract_geotiff_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not RASTERIO_AVAILABLE:
            return {"available": False, "reason": "rasterio not installed"}
        
        try:
            import rasterio
            from rasterio.crs import CRS
            
            with rasterio.open(filepath) as src:
                result = {
                    "available": True,
                    "raster_info": {},
                    "coordinate_system": {},
                    "geotransform": {},
                    "bands": [],
                    "statistics": {},
                    "tags": {}
                }
                
                # Basic raster information
                result["raster_info"] = {
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "dtype": str(src.dtypes[0]) if src.dtypes else None,
                    "driver": src.driver,
                    "nodata": src.nodata,
                    "bounds": {
                        "left": src.bounds.left,
                        "bottom": src.bounds.bottom,
                        "right": src.bounds.right,
                        "top": src.bounds.top
                    }
                }
                
                # Coordinate Reference System
                if src.crs:
                    result["coordinate_system"] = {
                        "crs_string": str(src.crs),
                        "epsg_code": src.crs.to_epsg(),
                        "proj4_string": src.crs.to_proj4(),
                        "wkt": src.crs.to_wkt(),
                        "is_geographic": src.crs.is_geographic,
                        "is_projected": src.crs.is_projected,
                        "units": src.crs.linear_units_factor[1] if src.crs.linear_units_factor else None
                    }
                
                # Geotransform (affine transformation)
                if src.transform:
                    result["geotransform"] = {
                        "pixel_size_x": src.transform.a,
                        "rotation_x": src.transform.b,
                        "top_left_x": src.transform.c,
                        "rotation_y": src.transform.d,
                        "pixel_size_y": src.transform.e,
                        "top_left_y": src.transform.f,
                        "matrix": list(src.transform)[:6]
                    }
                
                # Band information
                for i in range(1, src.count + 1):
                    band_info = {
                        "band_number": i,
                        "dtype": str(src.dtypes[i-1]),
                        "nodata": src.nodatavals[i-1] if src.nodatavals else None
                    }
                    
                    # Band statistics (if available)
                    try:
                        stats = src.statistics(i)
                        band_info["statistics"] = {
                            "min": stats.min,
                            "max": stats.max,
                            "mean": stats.mean,
                            "std": stats.std
                        }
                    except:
                        pass
                    
                    # Color interpretation
                    try:
                        color_interp = src.colorinterp[i-1]
                        band_info["color_interpretation"] = color_interp.name
                    except:
                        pass
                    
                    result["bands"].append(band_info)
                
                # Metadata tags
                result["tags"] = dict(src.tags())
                
                # Calculate additional spatial information
                if src.crs and src.transform:
                    # Calculate pixel area in square meters (if projected) or square degrees (if geographic)
                    pixel_area = abs(src.transform.a * src.transform.e)
                    result["raster_info"]["pixel_area"] = pixel_area
                    
                    # Calculate total area
                    total_area = pixel_area * src.width * src.height
                    result["raster_info"]["total_area"] = total_area
                    
                    # Resolution information
                    result["raster_info"]["resolution"] = {
                        "x": abs(src.transform.a),
                        "y": abs(src.transform.e),
                        "units": "degrees" if src.crs.is_geographic else "meters"
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting GeoTIFF metadata: {e}")
            return {"available": False, "error": str(e)}
    
    @staticmethod
    def extract_shapefile_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not FIONA_AVAILABLE:
            return {"available": False, "reason": "fiona not installed"}
        
        try:
            import fiona
            
            with fiona.open(filepath) as src:
                result = {
                    "available": True,
                    "vector_info": {},
                    "coordinate_system": {},
                    "schema": {},
                    "bounds": {},
                    "features": {}
                }
                
                # Basic vector information
                result["vector_info"] = {
                    "driver": src.driver,
                    "feature_count": len(src),
                    "geometry_type": src.schema.get('geometry', 'Unknown')
                }
                
                # Coordinate Reference System
                if src.crs:
                    result["coordinate_system"] = {
                        "crs_string": str(src.crs),
                        "crs_wkt": src.crs_wkt if hasattr(src, 'crs_wkt') else None
                    }
                
                # Schema (field definitions)
                result["schema"] = {
                    "geometry": src.schema.get('geometry'),
                    "properties": src.schema.get('properties', {})
                }
                
                # Bounds
                result["bounds"] = {
                    "left": src.bounds[0],
                    "bottom": src.bounds[1],
                    "right": src.bounds[2],
                    "top": src.bounds[3]
                }
                
                # Sample features (first few for analysis)
                sample_features = []
                for i, feature in enumerate(src):
                    if i >= 5:  # Limit to first 5 features
                        break
                    sample_features.append({
                        "id": feature.get('id'),
                        "geometry_type": feature['geometry']['type'] if feature.get('geometry') else None,
                        "properties": feature.get('properties', {})
                    })
                
                result["features"] = {
                    "sample_count": len(sample_features),
                    "samples": sample_features
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting Shapefile metadata: {e}")
            return {"available": False, "error": str(e)}

class ScientificInstrumentEngine:
    """Scientific instrument data extraction"""
    
    @staticmethod
    def extract_hdf5_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not HDF5_AVAILABLE:
            return {"available": False, "reason": "h5py not installed"}
        
        try:
            import h5py
            
            with h5py.File(filepath, 'r') as f:
                result = {
                    "available": True,
                    "file_info": {},
                    "groups": {},
                    "datasets": {},
                    "attributes": {}
                }
                
                # File-level information
                result["file_info"] = {
                    "hdf5_version": f.libver,
                    "file_size": os.path.getsize(filepath)
                }
                
                # Global attributes
                result["attributes"] = dict(f.attrs)
                
                def explore_group(group, path=""):
                    """Recursively explore HDF5 groups and datasets"""
                    group_info = {
                        "path": path,
                        "attributes": dict(group.attrs),
                        "subgroups": [],
                        "datasets": []
                    }
                    
                    for key in group.keys():
                        item = group[key]
                        item_path = f"{path}/{key}" if path else key
                        
                        if isinstance(item, h5py.Group):
                            group_info["subgroups"].append(key)
                            result["groups"][item_path] = explore_group(item, item_path)
                        
                        elif isinstance(item, h5py.Dataset):
                            dataset_info = {
                                "path": item_path,
                                "shape": item.shape,
                                "dtype": str(item.dtype),
                                "size": item.size,
                                "attributes": dict(item.attrs),
                                "chunks": item.chunks,
                                "compression": item.compression,
                                "compression_opts": item.compression_opts
                            }
                            
                            group_info["datasets"].append(key)
                            result["datasets"][item_path] = dataset_info
                    
                    return group_info
                
                # Explore the entire file structure
                result["groups"]["/"] = explore_group(f)
                
                # Summary statistics
                result["file_info"]["total_groups"] = len(result["groups"])
                result["file_info"]["total_datasets"] = len(result["datasets"])
                result["file_info"]["total_attributes"] = sum(
                    len(group.get("attributes", {})) for group in result["groups"].values()
                ) + sum(
                    len(dataset.get("attributes", {})) for dataset in result["datasets"].values()
                )
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting HDF5 metadata: {e}")
            return {"available": False, "error": str(e)}
    
    @staticmethod
    def extract_netcdf_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not NETCDF_AVAILABLE:
            return {"available": False, "reason": "netCDF4 not installed"}
        
        try:
            import netCDF4
            
            with netCDF4.Dataset(filepath, 'r') as nc:
                result = {
                    "available": True,
                    "file_info": {},
                    "dimensions": {},
                    "variables": {},
                    "global_attributes": {}
                }
                
                # File information
                result["file_info"] = {
                    "format": nc.data_model,
                    "file_format": nc.file_format,
                    "disk_format": nc.disk_format
                }
                
                # Global attributes
                result["global_attributes"] = {attr: getattr(nc, attr) for attr in nc.ncattrs()}
                
                # Dimensions
                for dim_name, dim in nc.dimensions.items():
                    result["dimensions"][dim_name] = {
                        "size": len(dim),
                        "unlimited": dim.isunlimited()
                    }
                
                # Variables
                for var_name, var in nc.variables.items():
                    var_info = {
                        "dimensions": var.dimensions,
                        "shape": var.shape,
                        "dtype": str(var.dtype),
                        "attributes": {attr: getattr(var, attr) for attr in var.ncattrs()}
                    }
                    
                    # CF Convention standard attributes
                    cf_attrs = ['units', 'long_name', 'standard_name', 'valid_range', 
                               'scale_factor', 'add_offset', '_FillValue']
                    var_info["cf_attributes"] = {
                        attr: var_info["attributes"].get(attr) 
                        for attr in cf_attrs 
                        if attr in var_info["attributes"]
                    }
                    
                    result["variables"][var_name] = var_info
                
                # Summary
                result["file_info"]["num_dimensions"] = len(result["dimensions"])
                result["file_info"]["num_variables"] = len(result["variables"])
                result["file_info"]["num_global_attributes"] = len(result["global_attributes"])
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting NetCDF metadata: {e}")
            return {"available": False, "error": str(e)}

class DroneUAVEngine:
    """Drone and UAV telemetry extraction"""
    
    @staticmethod
    def extract_drone_telemetry(filepath: str, exiftool_data: Dict = None) -> Optional[Dict[str, Any]]:
        """Extract drone flight data and telemetry"""
        result = {
            "available": True,
            "flight_data": {},
            "camera_data": {},
            "gps_track": {},
            "sensor_data": {},
            "manufacturer_specific": {}
        }
        
        # Use exiftool data if available (contains DJI, GoPro telemetry)
        if exiftool_data:
            # DJI drone metadata
            if "other" in exiftool_data:
                dji_fields = {}
                gopro_fields = {}
                
                for key, value in exiftool_data["other"].items():
                    if "DJI" in key or "dji" in key.lower():
                        dji_fields[key] = value
                    elif "GoPro" in key or "gopro" in key.lower():
                        gopro_fields[key] = value
                
                if dji_fields:
                    result["manufacturer_specific"]["dji"] = dji_fields
                if gopro_fields:
                    result["manufacturer_specific"]["gopro"] = gopro_fields
        
        # Extract GPS track from video metadata
        if exiftool_data and "gps" in exiftool_data:
            gps_data = exiftool_data["gps"]
            result["gps_track"] = {
                "has_gps": bool(gps_data),
                "coordinates": {
                    "latitude": gps_data.get("GPSLatitude"),
                    "longitude": gps_data.get("GPSLongitude"),
                    "altitude": gps_data.get("GPSAltitude")
                },
                "movement": {
                    "speed": gps_data.get("GPSSpeed"),
                    "direction": gps_data.get("GPSTrack"),
                    "image_direction": gps_data.get("GPSImgDirection")
                }
            }
        
        # Camera gimbal and settings
        if exiftool_data and "exif" in exiftool_data:
            exif_data = exiftool_data["exif"]
            result["camera_data"] = {
                "exposure_settings": {
                    "iso": exif_data.get("ISO"),
                    "shutter_speed": exif_data.get("ExposureTime"),
                    "aperture": exif_data.get("FNumber"),
                    "focal_length": exif_data.get("FocalLength")
                },
                "white_balance": exif_data.get("WhiteBalance"),
                "color_space": exif_data.get("ColorSpace")
            }
        
        return result if any(result[key] for key in ["flight_data", "camera_data", "gps_track", "sensor_data", "manufacturer_specific"]) else None

class BlockchainProvenanceEngine:
    """Blockchain and digital provenance extraction"""
    
    @staticmethod
    def extract_blockchain_metadata(filepath: str, exiftool_data: Dict = None) -> Optional[Dict[str, Any]]:
        """Extract blockchain provenance and C2PA metadata"""
        result = {
            "available": True,
            "c2pa_manifest": {},
            "digital_signatures": {},
            "nft_metadata": {},
            "content_credentials": {}
        }
        
        # Look for C2PA (Content Authenticity) metadata in XMP
        if exiftool_data and "xmp" in exiftool_data:
            xmp_data = exiftool_data["xmp"]
            
            # C2PA manifest detection
            c2pa_fields = {}
            for key, value in xmp_data.items():
                if "c2pa" in key.lower() or "contentauth" in key.lower():
                    c2pa_fields[key] = value
            
            if c2pa_fields:
                result["c2pa_manifest"] = c2pa_fields
        
        # Check for blockchain references in metadata
        blockchain_indicators = [
            "blockchain", "nft", "ethereum", "bitcoin", "ipfs", "arweave",
            "transaction", "hash", "smart_contract", "token_id"
        ]
        
        if exiftool_data:
            for category, data in exiftool_data.items():
                if isinstance(data, dict):
                    for key, value in data.items():
                        key_lower = key.lower()
                        value_str = str(value).lower() if value else ""
                        
                        for indicator in blockchain_indicators:
                            if indicator in key_lower or indicator in value_str:
                                if "blockchain_references" not in result:
                                    result["blockchain_references"] = {}
                                result["blockchain_references"][key] = value
        
        return result if any(result[key] for key in ["c2pa_manifest", "digital_signatures", "nft_metadata", "content_credentials"]) else None

# ============================================================================
# Comprehensive Metadata Extractor
# ============================================================================

class ComprehensiveMetadataExtractor:
    """Ultimate metadata extractor with all specialized engines"""
    
    def __init__(self):
        self.medical_engine = MedicalImagingEngine()
        self.astronomical_engine = AstronomicalDataEngine()
        self.geospatial_engine = GeospatialEngine()
        self.scientific_engine = ScientificInstrumentEngine()
        self.drone_engine = DroneUAVEngine()
        self.blockchain_engine = BlockchainProvenanceEngine()
    
    def extract_comprehensive_metadata(
        self,
        filepath: str,
        tier: str = "super"
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata using all available engines
        """
        try:
            # Start with base metadata extraction
            base_result = extract_base_metadata(filepath, tier)

            if "error" in base_result:
                return base_result
        except Exception as e:
            logger.error(f"Critical error in base metadata extraction: {e}")
            return {
                "error": f"Critical error in base metadata extraction: {str(e)}",
                "error_type": type(e).__name__,
                "extraction_info": {
                    "comprehensive_version": "4.0.0",
                    "processing_ms": 0
                }
            }
        
        # Get tier configuration
        try:
            tier_enum = Tier(tier.lower())
        except ValueError:
            tier_enum = Tier.SUPER

        tier_config = COMPREHENSIVE_TIER_CONFIGS[tier_enum]

        # Add comprehensive extraction info
        base_result["extraction_info"]["comprehensive_version"] = "4.0.0"
        base_result["extraction_info"]["specialized_engines"] = {
            "medical_imaging": DICOM_AVAILABLE and tier_config.medical_imaging,
            "astronomical_data": FITS_AVAILABLE and tier_config.astronomical_data,
            "geospatial_analysis": (RASTERIO_AVAILABLE or FIONA_AVAILABLE) and tier_config.geospatial_analysis,
            "scientific_instruments": (HDF5_AVAILABLE or NETCDF_AVAILABLE) and tier_config.scientific_instruments,
            "drone_telemetry": tier_config.drone_telemetry,
            "blockchain_provenance": tier_config.blockchain_provenance,
            "emerging_technology": tier_config.emerging_technology and extract_emerging_technology_metadata is not None,
            "advanced_video_analysis": tier_config.advanced_video_analysis and extract_advanced_video_metadata is not None,
            "advanced_audio_analysis": tier_config.advanced_audio_analysis and extract_advanced_audio_metadata is not None,
            "document_analysis": tier_config.document_analysis and extract_document_metadata is not None,
            "scientific_research": tier_config.scientific_research and extract_scientific_research_metadata is not None,
            "multimedia_entertainment": tier_config.multimedia_entertainment and extract_multimedia_entertainment_metadata is not None,
            "industrial_manufacturing": tier_config.industrial_manufacturing and extract_industrial_manufacturing_metadata is not None,
            "financial_business": tier_config.financial_business and extract_financial_business_metadata is not None,
            "healthcare_medical": tier_config.healthcare_medical and extract_healthcare_medical_metadata is not None,
            "transportation_logistics": tier_config.transportation_logistics and extract_transportation_logistics_metadata is not None,
            "education_academic": tier_config.education_academic and extract_education_academic_metadata is not None,
            "legal_compliance": tier_config.legal_compliance and extract_legal_compliance_metadata is not None,
            "environmental_sustainability": tier_config.environmental_sustainability and extract_environmental_sustainability_metadata is not None,
            "social_media_digital": tier_config.social_media_digital and extract_social_media_digital_metadata is not None,
            "gaming_entertainment": tier_config.gaming_entertainment and extract_gaming_entertainment_metadata is not None,
        }

        # Detect file type for specialized extraction
        file_ext = Path(filepath).suffix.lower()
        mime_type = base_result.get("file", {}).get("mime_type", "")
        is_image = mime_type.startswith("image/")
        is_video = mime_type.startswith("video/")
        is_audio = mime_type.startswith("audio/") or file_ext in [".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".aiff"]

        try:
            # Medical imaging (DICOM)
            if tier_config.medical_imaging and (file_ext in ['.dcm', '.dicom'] or 'dicom' in mime_type):
                dicom_result = safe_extract_module(self.medical_engine.extract_dicom_metadata, filepath, "medical_imaging")
                if dicom_result and dicom_result.get("available"):
                    base_result["medical_imaging"] = dicom_result

            # Astronomical data (FITS)
            if tier_config.astronomical_data and file_ext in ['.fits', '.fit', '.fts']:
                fits_result = safe_extract_module(self.astronomical_engine.extract_fits_metadata, filepath, "astronomical_data")
                if fits_result and fits_result.get("available"):
                    base_result["astronomical_data"] = fits_result

            # Geospatial data
            if tier_config.geospatial_analysis:
                if file_ext in ['.tif', '.tiff'] and 'geo' in str(base_result.get("exif", {})).lower():
                    geotiff_result = safe_extract_module(self.geospatial_engine.extract_geotiff_metadata, filepath, "geospatial_geotiff")
                    if geotiff_result and geotiff_result.get("available"):
                        base_result["geospatial"] = geotiff_result

                elif file_ext in ['.shp']:
                    shapefile_result = safe_extract_module(self.geospatial_engine.extract_shapefile_metadata, filepath, "geospatial_shapefile")
                    if shapefile_result and shapefile_result.get("available"):
                        base_result["geospatial"] = shapefile_result

            # Scientific instruments
            if tier_config.scientific_instruments:
                if file_ext in ['.h5', '.hdf5', '.he5']:
                    hdf5_result = safe_extract_module(self.scientific_engine.extract_hdf5_metadata, filepath, "scientific_hdf5")
                    if hdf5_result and hdf5_result.get("available"):
                        base_result["scientific_data"] = hdf5_result

                elif file_ext in ['.nc', '.netcdf', '.nc4']:
                    netcdf_result = safe_extract_module(self.scientific_engine.extract_netcdf_metadata, filepath, "scientific_netcdf")
                    if netcdf_result and netcdf_result.get("available"):
                        base_result["scientific_data"] = netcdf_result

            # Drone telemetry (for images and videos)
            if tier_config.drone_telemetry and mime_type.startswith(('image/', 'video/')):
                # Use exiftool data if available
                exiftool_data = None
                if hasattr(base_result, 'get') and any(key in base_result for key in ['exif', 'gps', 'makernote', 'xmp']):
                    exiftool_data = {
                        'exif': base_result.get('exif', {}),
                        'gps': base_result.get('gps', {}),
                        'makernote': base_result.get('makernote', {}),
                        'xmp': base_result.get('xmp', {}),
                        'other': base_result.get('composite', {})
                    }

                drone_result = safe_extract_module(self.drone_engine.extract_drone_telemetry, filepath, "drone_telemetry", exiftool_data)
                if drone_result:
                    base_result["drone_telemetry"] = drone_result

            # Blockchain provenance
            if tier_config.blockchain_provenance:
                exiftool_data = None
                if hasattr(base_result, 'get'):
                    exiftool_data = {
                        'xmp': base_result.get('xmp', {}),
                        'iptc': base_result.get('iptc', {}),
                        'exif': base_result.get('exif', {})
                    }

                blockchain_result = safe_extract_module(self.blockchain_engine.extract_blockchain_metadata, filepath, "blockchain_provenance", exiftool_data)
                if blockchain_result:
                    base_result["blockchain_provenance"] = blockchain_result

            # Optional: Web metadata
            if tier_config.web_metadata and extract_web_metadata:
                web_result = safe_extract_module(extract_web_metadata, filepath, "web_metadata")
                if web_result:
                    base_result["web_metadata"] = web_result

            # Optional: Social media context
            if tier_config.social_media_context and extract_social_media_metadata:
                social_result = safe_extract_module(extract_social_media_metadata, filepath, "social_media_metadata")
                if social_result:
                    base_result["social_media"] = social_result

            # Optional: Mobile sensors
            if tier_config.mobile_sensors and extract_mobile_metadata and is_image:
                def mobile_section(name: str) -> Dict[str, Any]:
                    section = base_result.get(name, {})
                    if isinstance(section, dict) and not section.get("_locked"):
                        return section
                    return {}

                mobile_exiftool_data = {
                    "exif": mobile_section("exif"),
                    "xmp": mobile_section("xmp"),
                    "xmp_namespaces": mobile_section("xmp_namespaces"),
                    "makernote": mobile_section("makernote"),
                    "composite": mobile_section("composite"),
                }

                mobile_result = safe_extract_module(extract_mobile_metadata, filepath, "mobile_metadata", mobile_exiftool_data)
                if mobile_result:
                    base_result["mobile_metadata"] = mobile_result

            # Optional: Forensic/security metadata
            if tier_config.forensic_details and extract_forensic_metadata:
                forensic_result = safe_extract_module(extract_forensic_metadata, filepath, "forensic_metadata")
                if forensic_result:
                    base_result["forensic_security"] = forensic_result

            # Optional: Action camera metadata
            if (tier_config.drone_telemetry or tier_config.professional_video) and extract_action_camera_metadata and (is_image or is_video):
                action_result = safe_extract_module(extract_action_camera_metadata, filepath, "action_camera_metadata")
                if action_result:
                    base_result["action_camera"] = action_result

            # Optional: 360° camera metadata
            if extract_360_camera_metadata and is_image:
                def camera_360_section(name: str) -> Dict[str, Any]:
                    section = base_result.get(name, {})
                    if isinstance(section, dict) and not section.get("_locked"):
                        return section
                    return {}

                camera_360_exiftool_data = {
                    "exif": camera_360_section("exif"),
                    "xmp": camera_360_section("xmp"),
                    "xmp_namespaces": camera_360_section("xmp_namespaces"),
                    "makernote": camera_360_section("makernote"),
                    "composite": camera_360_section("composite"),
                    "image_container": camera_360_section("image_container"),
                }

                camera_360_result = safe_extract_module(extract_360_camera_metadata, filepath, "360_camera_metadata", camera_360_exiftool_data)
                if camera_360_result:
                    base_result["camera_360"] = camera_360_result

            # Optional: Print/publishing metadata
            if tier_config.web_metadata and extract_print_publishing_metadata and is_image:
                print_result = safe_extract_module(extract_print_publishing_metadata, filepath, "print_publishing_metadata")
                if print_result:
                    base_result["print_publishing"] = print_result

            # Optional: Workflow/DAM metadata
            if tier_config.web_metadata and extract_workflow_dam_metadata:
                workflow_result = safe_extract_module(extract_workflow_dam_metadata, filepath, "workflow_dam_metadata")
                if workflow_result:
                    base_result["workflow_dam"] = workflow_result

            # Optional: Advanced audio/video analysis
            if tier_config.advanced_audio and extract_audio_advanced_metadata and is_audio:
                audio_adv = safe_extract_module(extract_audio_advanced_metadata, filepath, "audio_advanced_metadata")
                if audio_adv:
                    base_result["audio_advanced"] = audio_adv

            if tier_config.professional_video and extract_video_advanced_metadata and is_video:
                video_adv = safe_extract_module(extract_video_advanced_metadata, filepath, "video_advanced_metadata")
                if video_adv:
                    base_result["video_advanced"] = video_adv

            # Optional: Steganography/manipulation/AI detection
            if tier_config.steganography_detection and is_image:
                if detect_enhanced_steganography:
                    steg_result = safe_extract_module(detect_enhanced_steganography, filepath, "enhanced_steganography")
                    if steg_result:
                        base_result["steganography_analysis"] = steg_result
                elif analyze_steganography:
                    steg_result = safe_extract_module(analyze_steganography, filepath, "steganography_analysis")
                    if steg_result:
                        base_result["steganography_analysis"] = steg_result

            if tier_config.manipulation_detection and detect_enhanced_manipulation and is_image:
                manipulation_result = safe_extract_module(detect_enhanced_manipulation, filepath, "manipulation_detection", base_result)
                if manipulation_result:
                    base_result["manipulation_detection"] = manipulation_result

            if tier_config.ai_content_detection and detect_ai_content:
                ai_result = safe_extract_module(detect_ai_content, filepath, "ai_detection", base_result)
                if ai_result:
                    base_result["ai_detection"] = ai_result

            # Optional: Timeline reconstruction
            if tier_config.timeline_reconstruction and analyze_single_file_timeline:
                timeline_result = safe_extract_module(analyze_single_file_timeline, base_result, "timeline_analysis")
                if timeline_result:
                    base_result["timeline_analysis"] = timeline_result

            # Optional: Emerging technology analysis
            if tier_config.emerging_technology and extract_emerging_technology_metadata:
                emerging_result = safe_extract_module(extract_emerging_technology_metadata, filepath, "emerging_technology")
                if emerging_result and emerging_result.get("emerging_technology_analysis"):
                    base_result["emerging_technology"] = emerging_result

            # Optional: Advanced video analysis
            if tier_config.advanced_video_analysis and extract_advanced_video_metadata and is_video:
                video_result = safe_extract_module(extract_advanced_video_metadata, filepath, "advanced_video")
                if video_result and video_result.get("available"):
                    base_result["advanced_video"] = video_result

            # Optional: Advanced audio analysis
            if tier_config.advanced_audio_analysis and extract_advanced_audio_metadata and is_audio:
                audio_result = safe_extract_module(extract_advanced_audio_metadata, filepath, "advanced_audio")
                if audio_result and audio_result.get("available"):
                    base_result["advanced_audio"] = audio_result

            # Optional: Document analysis
            if tier_config.document_analysis and extract_document_metadata:
                # Check if it's a document type
                file_ext = Path(filepath).suffix.lower()
                document_extensions = [
                    '.pdf', '.docx', '.xlsx', '.pptx', '.html', '.htm', '.xml',
                    '.epub', '.mobi', '.zip', '.tar', '.gz', '.py', '.js', '.java',
                    '.json', '.yaml', '.yml', '.toml', '.ini', '.txt', '.md', '.db'
                ]

                if file_ext in document_extensions or not (is_image or is_video or is_audio):
                    doc_result = safe_extract_module(extract_document_metadata, filepath, "document_metadata")
                    if doc_result and doc_result.get("available"):
                        base_result["document_metadata"] = doc_result

            # Optional: Scientific research analysis
            if tier_config.scientific_research and extract_scientific_research_metadata:
                research_result = safe_extract_module(extract_scientific_research_metadata, filepath, "scientific_research")
                if research_result and research_result.get("available"):
                    base_result["scientific_research"] = research_result

            # Optional: Multimedia entertainment analysis
            if tier_config.multimedia_entertainment and extract_multimedia_entertainment_metadata:
                entertainment_result = safe_extract_module(extract_multimedia_entertainment_metadata, filepath, "multimedia_entertainment")
                if entertainment_result and entertainment_result.get("available"):
                    base_result["multimedia_entertainment"] = entertainment_result

            # Optional: Industrial manufacturing analysis
            if tier_config.industrial_manufacturing and extract_industrial_manufacturing_metadata:
                industrial_result = safe_extract_module(extract_industrial_manufacturing_metadata, filepath, "industrial_manufacturing")
                if industrial_result and industrial_result.get("available"):
                    base_result["industrial_manufacturing"] = industrial_result

            # Optional: Financial business analysis
            if tier_config.financial_business and extract_financial_business_metadata:
                financial_result = safe_extract_module(extract_financial_business_metadata, filepath, "financial_business")
                if financial_result and financial_result.get("available"):
                    base_result["financial_business"] = financial_result

            # Optional: Healthcare medical analysis
            if tier_config.healthcare_medical and extract_healthcare_medical_metadata:
                healthcare_result = safe_extract_module(extract_healthcare_medical_metadata, filepath, "healthcare_medical")
                if healthcare_result and healthcare_result.get("available"):
                    base_result["healthcare_medical"] = healthcare_result

            # Optional: Transportation logistics analysis
            if tier_config.transportation_logistics and extract_transportation_logistics_metadata:
                transport_result = safe_extract_module(extract_transportation_logistics_metadata, filepath, "transportation_logistics")
                if transport_result and transport_result.get("available"):
                    base_result["transportation_logistics"] = transport_result

            # Optional: Education academic analysis
            if tier_config.education_academic and extract_education_academic_metadata:
                education_result = safe_extract_module(extract_education_academic_metadata, filepath, "education_academic")
                if education_result and education_result.get("available"):
                    base_result["education_academic"] = education_result

            # Optional: Legal compliance analysis
            if tier_config.legal_compliance and extract_legal_compliance_metadata:
                legal_result = safe_extract_module(extract_legal_compliance_metadata, filepath, "legal_compliance")
                if legal_result and legal_result.get("available"):
                    base_result["legal_compliance"] = legal_result

            # Optional: Environmental sustainability analysis
            if tier_config.environmental_sustainability and extract_environmental_sustainability_metadata:
                environmental_result = safe_extract_module(extract_environmental_sustainability_metadata, filepath, "environmental_sustainability")
                if environmental_result and environmental_result.get("available"):
                    base_result["environmental_sustainability"] = environmental_result

            # Optional: Social media digital analysis
            if tier_config.social_media_digital and extract_social_media_digital_metadata:
                social_digital_result = safe_extract_module(extract_social_media_digital_metadata, filepath, "social_media_digital")
                if social_digital_result and social_digital_result.get("available"):
                    base_result["social_media_digital"] = social_digital_result

            # Optional: Gaming entertainment analysis
            if tier_config.gaming_entertainment and extract_gaming_entertainment_metadata:
                gaming_result = safe_extract_module(extract_gaming_entertainment_metadata, filepath, "gaming_entertainment")
                if gaming_result and gaming_result.get("available"):
                    base_result["gaming_entertainment"] = gaming_result

        except Exception as e:
            logger.error(f"Error in comprehensive extraction process: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            # Add error to results but continue with other processing
            if "extraction_errors" not in base_result:
                base_result["extraction_errors"] = []
            base_result["extraction_errors"].append({
                "error": str(e),
                "error_type": type(e).__name__,
                "module": "comprehensive_extraction_process"
            })

        # Cache the result if caching is available (disabled for now due to implementation issues)
        # if get_cache:
        #     try:
        #         cache = get_cache()
        #         cache.put(filepath, base_result, tier, int(base_result["extraction_info"].get("extraction_time_ms", 0)))
        #     except Exception as e:
        #         logger.debug(f"Cache storage failed: {e}")

        # Cache the result if caching is available (disabled for now due to implementation issues)
        # if get_cache:
        #     try:
        #         cache = get_cache()
        #         cache.put(filepath, base_result, tier, int(base_result["extraction_info"].get("extraction_time_ms", 0)))
        #     except Exception as e:
        #         logger.debug(f"Cache storage failed: {e}")

        # Update field count
        def count_comprehensive_fields(obj):
            if not isinstance(obj, dict):
                return 1 if obj is not None else 0
            return sum(count_comprehensive_fields(v) for k, v in obj.items() if not k.startswith("_"))
        
        base_result["extraction_info"]["comprehensive_fields_extracted"] = count_comprehensive_fields(base_result)
        
        # Add specialized field counts
        specialized_counts = {}
        if "medical_imaging" in base_result:
            specialized_counts["medical_imaging"] = count_comprehensive_fields(base_result["medical_imaging"])
        if "astronomical_data" in base_result:
            specialized_counts["astronomical_data"] = count_comprehensive_fields(base_result["astronomical_data"])
        if "geospatial" in base_result:
            specialized_counts["geospatial"] = count_comprehensive_fields(base_result["geospatial"])
        if "scientific_data" in base_result:
            specialized_counts["scientific_data"] = count_comprehensive_fields(base_result["scientific_data"])
        if "drone_telemetry" in base_result:
            specialized_counts["drone_telemetry"] = count_comprehensive_fields(base_result["drone_telemetry"])
        if "blockchain_provenance" in base_result:
            specialized_counts["blockchain_provenance"] = count_comprehensive_fields(base_result["blockchain_provenance"])
        if "emerging_technology" in base_result:
            specialized_counts["emerging_technology"] = count_comprehensive_fields(base_result["emerging_technology"])
        if "advanced_video" in base_result:
            specialized_counts["advanced_video"] = count_comprehensive_fields(base_result["advanced_video"])
        if "advanced_audio" in base_result:
            specialized_counts["advanced_audio"] = count_comprehensive_fields(base_result["advanced_audio"])
        if "document_metadata" in base_result:
            specialized_counts["document_metadata"] = count_comprehensive_fields(base_result["document_metadata"])
        if "scientific_research" in base_result:
            specialized_counts["scientific_research"] = count_comprehensive_fields(base_result["scientific_research"])
        if "multimedia_entertainment" in base_result:
            specialized_counts["multimedia_entertainment"] = count_comprehensive_fields(base_result["multimedia_entertainment"])
        if "industrial_manufacturing" in base_result:
            specialized_counts["industrial_manufacturing"] = count_comprehensive_fields(base_result["industrial_manufacturing"])
        if "financial_business" in base_result:
            specialized_counts["financial_business"] = count_comprehensive_fields(base_result["financial_business"])
        
        base_result["extraction_info"]["specialized_field_counts"] = specialized_counts
        
        return base_result

# ============================================================================
# Main Interface Functions
# ============================================================================

# Global comprehensive extractor instance
_comprehensive_extractor = None

def get_comprehensive_extractor() -> ComprehensiveMetadataExtractor:
    """Get or create the global comprehensive extractor instance."""
    global _comprehensive_extractor
    if _comprehensive_extractor is None:
        _comprehensive_extractor = ComprehensiveMetadataExtractor()
    return _comprehensive_extractor

def extract_comprehensive_metadata(filepath: str, tier: str = "super") -> Dict[str, Any]:
    """
    Extract comprehensive metadata using all available specialized engines.
    
    This is the main entry point for the ultimate metadata extraction.
    """
    # Check cache first if available
    if get_cache:
        try:
            cache = get_cache()
            cached_result = cache.get(filepath, tier)
            if cached_result:
                logger.debug(f"Cache hit for {filepath}")
                return cached_result
        except Exception as e:
            logger.debug(f"Cache lookup failed: {e}")
    
    extractor = get_comprehensive_extractor()
    return extractor.extract_comprehensive_metadata(filepath, tier)


def extract_comprehensive_batch(
    filepaths: List[str],
    tier: str = "super",
    max_workers: int = 4,
    store_results: bool = False,
) -> Dict[str, Any]:
    """Extract metadata for multiple files with optional storage."""
    extractor = get_comprehensive_extractor()
    results: Dict[str, Any] = {}
    errors = 0
    start_time = time.time()

    def _process(path: str) -> Tuple[str, Dict[str, Any]]:
        metadata = extractor.extract_comprehensive_metadata(path, tier)
        if store_results and store_file_metadata and "error" not in metadata:
            try:
                store_file_metadata(path, metadata, metadata.get("perceptual_hashes"))
            except Exception as e:
                metadata["storage_error"] = str(e)
        return path, metadata

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for path, metadata in executor.map(_process, filepaths):
            results[path] = metadata
            if "error" in metadata:
                errors += 1

    duration_ms = int((time.time() - start_time) * 1000)
    batch_payload = {
        "results": results,
        "summary": {
            "total_files": len(filepaths),
            "successful": len(filepaths) - errors,
            "failed": errors,
            "processing_ms": duration_ms,
            "tier": tier,
        },
    }

    # Optional batch comparison
    if MetadataComparator is not None:
        try:
            tier_enum = Tier(tier.lower())
        except ValueError:
            tier_enum = Tier.SUPER
        tier_config = COMPREHENSIVE_TIER_CONFIGS[tier_enum]
        if tier_config.batch_comparison:
            try:
                comparator = MetadataComparator()
                comparable = [meta for meta in results.values() if isinstance(meta, dict) and "error" not in meta]
                if len(comparable) >= 2:
                    batch_payload["batch_comparison"] = comparator.compare_files(comparable, "summary")
            except Exception as e:
                batch_payload["batch_comparison"] = {"error": str(e)}

    return batch_payload

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MetaExtract Comprehensive Engine v4.0 - Ultimate Metadata Extraction")
    parser.add_argument("files", nargs="+", help="File(s) to extract metadata from")
    parser.add_argument("--tier", "-t", default="super", choices=["free", "starter", "premium", "super"])
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--engines", action="store_true", help="Show available specialized engines")
    parser.add_argument("--batch", action="store_true", help="Process files in batch mode")
    parser.add_argument("--store", action="store_true", help="Store metadata in local database")
    parser.add_argument("--max-workers", type=int, default=4, help="Batch concurrency")
    parser.add_argument("--performance", action="store_true", help="Include performance metrics (compat)")
    parser.add_argument("--advanced", action="store_true", help="Enable advanced analysis (compat)")
    parser.add_argument("--quiet", "-q", action="store_true", help="JSON only output")
    
    args = parser.parse_args()
    
    if args.engines:
        print("Available Specialized Engines:")
        print(f"  Medical Imaging (DICOM): {'✓' if DICOM_AVAILABLE else '✗'}")
        print(f"  Astronomical Data (FITS): {'✓' if FITS_AVAILABLE else '✗'}")
        print(f"  Geospatial (GeoTIFF/Shapefile): {'✓' if RASTERIO_AVAILABLE or FIONA_AVAILABLE else '✗'}")
        print(f"  Scientific Data (HDF5/NetCDF): {'✓' if HDF5_AVAILABLE or NETCDF_AVAILABLE else '✗'}")
        print(f"  Advanced Image Analysis: {'✓' if OPENCV_AVAILABLE else '✗'}")
        print(f"  Microscopy: {'✓' if MICROSCOPY_AVAILABLE else '✗'}")
        print(f"  Blockchain/Web3: {'✓' if WEB3_AVAILABLE else '✗'}")
        print(f"  Advanced Audio: {'✓' if LIBROSA_AVAILABLE else '✗'}")
        return
    
    if args.batch or len(args.files) > 1:
        if not args.quiet:
            print(f"MetaExtract Comprehensive v4.0.0 - Batch extracting {len(args.files)} files", file=sys.stderr)
        result = extract_comprehensive_batch(
            args.files,
            tier=args.tier,
            max_workers=args.max_workers,
            store_results=args.store,
        )
        json_out = json.dumps(result, indent=2, default=str)
    else:
        if not args.quiet:
            print(f"MetaExtract Comprehensive v4.0.0 - Extracting from: {args.files[0]}", file=sys.stderr)
            print(
                f"Tier: {args.tier} | Engines: Medical={'✓' if DICOM_AVAILABLE else '✗'} Astro={'✓' if FITS_AVAILABLE else '✗'} Geo={'✓' if RASTERIO_AVAILABLE else '✗'}",
                file=sys.stderr,
            )
        result = extract_comprehensive_metadata(args.files[0], tier=args.tier)
        if args.store and store_file_metadata and "error" not in result:
            try:
                store_file_metadata(args.files[0], result, result.get("perceptual_hashes"))
            except Exception as e:
                result["storage_error"] = str(e)
        json_out = json.dumps(result, indent=2, default=str)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_out)
        if not args.quiet:
            print(f"Saved to: {args.output}", file=sys.stderr)
    else:
        print(json_out)

if __name__ == "__main__":
    main()
