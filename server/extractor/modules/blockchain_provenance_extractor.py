#!/usr/bin/env python3
"""
Blockchain and Provenance Metadata Extractor Module

Extracts metadata related to blockchain provenance, NFT information,
digital signatures, and content authenticity from various file formats.
"""

import logging
import json
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_blockchain_provenance_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract blockchain and provenance metadata from files.
    
    Args:
        filepath: Path to the file to extract metadata from
        
    Returns:
        Dictionary containing blockchain/provenance metadata
    """
    result = {
        'blockchain_provenance': {},
        'nft_metadata': {},
        'digital_signatures': [],
        'c2pa_metadata': {},
        'content_credentials': {},
        'extraction_success': False,
        'errors': []
    }
    
    try:
        # Extract NFT metadata if available
        result['nft_metadata'] = extract_nft_metadata(filepath)
        
        # Extract C2PA (Content Authenticity Initiative) metadata
        result['c2pa_metadata'] = extract_c2pa_metadata(filepath)
        
        # Extract digital signatures
        result['digital_signatures'] = extract_digital_signatures(filepath)
        
        # Extract blockchain provenance info
        result['blockchain_provenance'] = extract_blockchain_info(filepath)
        
        result['extraction_success'] = True
        logger.info(f"Successfully extracted blockchain/provenance metadata from {filepath}")
        
    except Exception as e:
        error_msg = f"Error extracting blockchain/provenance metadata from {filepath}: {str(e)}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    return result


def extract_nft_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract NFT-related metadata from files.
    
    Args:
        filepath: Path to the file to extract NFT metadata from
        
    Returns:
        Dictionary containing NFT metadata
    """
    nft_metadata = {
        'nft_info': {},
        'blockchain_info': {},
        'token_details': {},
        'provenance': {},
        'smart_contract': {},
        'traits': [],
        'collection_info': {}
    }
    
    try:
        # Calculate file hash for provenance tracking
        with open(filepath, 'rb') as f:
            file_content = f.read()
            nft_metadata['provenance']['file_hash_sha256'] = hashlib.sha256(file_content).hexdigest()
            nft_metadata['provenance']['file_hash_md5'] = hashlib.md5(file_content).hexdigest()
        
        # File size and basic info
        file_path = Path(filepath)
        nft_metadata['provenance']['file_size'] = file_path.stat().st_size
        nft_metadata['provenance']['file_name'] = file_path.name
        nft_metadata['provenance']['file_extension'] = file_path.suffix.lower()
        
        # Look for embedded NFT metadata in JSON files or metadata sections
        if file_path.suffix.lower() in ['.json']:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    
                    # Look for common NFT metadata fields
                    nft_fields = [
                        'name', 'description', 'image', 'external_url', 'animation_url',
                        'background_color', 'youtube_url', 'attributes', 'collection',
                        'tokenId', 'contract_address', 'blockchain'
                    ]
                    
                    for field in nft_fields:
                        if field in content:
                            nft_metadata['nft_info'][field] = content[field]
                    
                    # Extract attributes as traits
                    if 'attributes' in content:
                        for attr in content['attributes']:
                            if isinstance(attr, dict) and 'trait_type' in attr and 'value' in attr:
                                nft_metadata['traits'].append({
                                    'trait_type': attr['trait_type'],
                                    'value': attr['value']
                                })
                
            except json.JSONDecodeError:
                logger.info(f"File {filepath} is not a valid JSON file")
            except Exception as e:
                logger.warning(f"Could not parse JSON metadata from {filepath}: {str(e)}")
        
        # For image files, we might look for embedded NFT metadata in EXIF or other metadata sections
        # This would require additional libraries like PIL/Pillow for image processing
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            try:
                from PIL import Image
                img = Image.open(filepath)
                
                # Check for embedded metadata
                if hasattr(img, 'info') and img.info:
                    nft_metadata['embedded_metadata'] = img.info
                    
                    # Look for specific NFT-related keys in embedded metadata
                    for key, value in img.info.items():
                        if 'nft' in key.lower() or 'token' in key.lower() or 'blockchain' in key.lower():
                            nft_metadata['nft_info'][key] = value
            
            except ImportError:
                logger.warning("Pillow not available - image NFT metadata extraction limited")
                nft_metadata['errors'] = ['Pillow library not available']
            except Exception as e:
                logger.warning(f"Could not extract image metadata from {filepath}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error extracting NFT metadata: {str(e)}")
        nft_metadata['errors'] = [f'Error: {str(e)}']
    
    return nft_metadata


def extract_c2pa_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract C2PA (Content Authenticity Initiative) metadata from files.
    
    Args:
        filepath: Path to the file to extract C2PA metadata from
        
    Returns:
        Dictionary containing C2PA metadata
    """
    c2pa_metadata = {
        'c2pa_info': {},
        'content_credentials': [],
        'provenance_statements': [],
        'ingredient_info': {},
        'assertions': [],
        'signing_info': {},
        'validation_status': {}
    }
    
    try:
        # C2PA requires the c2pa library which may not be available
        # For now, we'll implement a basic check for C2PA markers
        # In a real implementation, we would use the c2pa-python library
        
        # Calculate file hash to check against known C2PA signatures
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        # Look for C2PA markers in the file
        # C2PA content typically has specific markers in the file
        file_hex = file_content.hex()
        
        # Common C2PA markers in hex format
        c2pa_markers = [
            '63327061',  # 'c2pa' in hex
            '41444f42',  # 'ADOBE' in hex (Adobe's C2PA implementation)
        ]
        
        for marker in c2pa_markers:
            if marker.lower() in file_hex.lower():
                c2pa_metadata['c2pa_info']['has_c2pa_marker'] = True
                c2pa_metadata['c2pa_info']['detected_marker'] = marker
                break
        
        # File hash for C2PA verification
        c2pa_metadata['c2pa_info']['file_hash_sha256'] = hashlib.sha256(file_content).hexdigest()
        
        # If c2pa-python library was available, we would do:
        # import c2pa
        # manifest_store = c2pa.read(filepath)
        # c2pa_metadata['content_credentials'] = [manifest.to_dict() for manifest in manifest_store.manifests]
        
    except ImportError:
        logger.warning("c2pa library not available - C2PA metadata extraction limited")
        c2pa_metadata['errors'] = ['c2pa library not available']
    except Exception as e:
        logger.error(f"Error extracting C2PA metadata: {str(e)}")
        c2pa_metadata['errors'] = [f'Error: {str(e)}']
    
    return c2pa_metadata


def extract_digital_signatures(filepath: str) -> List[Dict[str, Any]]:
    """
    Extract digital signature information from files.
    
    Args:
        filepath: Path to the file to extract digital signatures from
        
    Returns:
        List of dictionaries containing digital signature information
    """
    signatures = []
    
    try:
        # Calculate file hash
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Basic signature detection based on file type
        file_path = Path(filepath)
        file_ext = file_path.suffix.lower()
        
        signature_info = {
            'signature_type': 'unknown',
            'algorithm': 'unknown',
            'valid': None,
            'timestamp': None,
            'signer_info': {},
            'certificate_info': {},
            'file_hash': file_hash,
            'file_extension': file_ext
        }
        
        # Different signature detection based on file type
        if file_ext in ['.pdf']:
            # PDF signature detection
            signature_info['signature_type'] = 'PDF_Digital_Signature'
            try:
                import PyPDF2
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfFileReader(f)
                    if pdf_reader.isEncrypted:
                        signature_info['encrypted'] = True
                    
                    # Check for signature fields
                    if '/Sig' in str(pdf_reader.getPage(0).getContents()):
                        signature_info['detected'] = True
                        signature_info['signature_type'] = 'PDF_Digital_Signature'
                    else:
                        signature_info['detected'] = False
                        
            except ImportError:
                logger.warning("PyPDF2 not available - PDF signature detection limited")
                signature_info['library_missing'] = True
            except Exception as e:
                logger.warning(f"Could not analyze PDF signatures: {str(e)}")
        
        elif file_ext in ['.docx', '.xlsx', '.pptx']:
            # Office document signature detection
            signature_info['signature_type'] = 'Office_Digital_Signature'
            # Office signatures are stored in specific XML parts
            # This would require python-docx, openpyxl, or python-pptx libraries
        
        elif file_ext in ['.exe', '.dll', '.sys']:
            # Windows executable signature detection
            signature_info['signature_type'] = 'Authenticode_Signature'
            # Authenticode signatures require specialized tools like signtool or python libraries
        
        signatures.append(signature_info)
    
    except Exception as e:
        logger.error(f"Error extracting digital signatures: {str(e)}")
        signatures.append({'error': str(e)})
    
    return signatures


def extract_blockchain_info(filepath: str) -> Dict[str, Any]:
    """
    Extract blockchain-related information from files.
    
    Args:
        filepath: Path to the file to extract blockchain info from
        
    Returns:
        Dictionary containing blockchain information
    """
    blockchain_info = {
        'blockchain_networks': [],
        'token_standards': [],
        'smart_contract_addresses': [],
        'transaction_hashes': [],
        'provenance_records': [],
        'hash_registrations': [],
        'metadata_uris': []
    }
    
    try:
        # Calculate file hash
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        file_hash_sha256 = hashlib.sha256(file_content).hexdigest()
        file_hash_md5 = hashlib.md5(file_content).hexdigest()
        
        blockchain_info['file_hashes'] = {
            'sha256': file_hash_sha256,
            'md5': file_hash_md5
        }
        
        # Look for blockchain-related patterns in the file
        file_text = file_content.decode('utf-8', errors='ignore')
        
        import re
        
        # Common blockchain address patterns
        patterns = {
            'ethereum_address': r'0x[a-fA-F0-9]{40}',
            'bitcoin_address': r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$',
            'solana_address': r'[1-9A-HJ-NP-Za-km-z]{32,44}',
            'transaction_hash': r'0x[a-fA-F0-9]{64}',
            'ipfs_hash': r'Qm[1-9A-Za-z]{44}',
            'arweave_id': r'[a-zA-Z0-9_-]{43}'
        }
        
        for name, pattern in patterns.items():
            matches = re.findall(pattern, file_text, re.MULTILINE | re.IGNORECASE)
            if matches:
                blockchain_info[f'{name}_matches'] = matches
        
        # Look for common NFT metadata fields that might contain blockchain info
        if '.json' in filepath:
            try:
                content = json.loads(file_text)
                
                # Look for blockchain-specific fields
                blockchain_fields = [
                    'contract_address', 'token_id', 'blockchain', 'network',
                    'mint_transaction', 'owner_address', 'creator_address',
                    'metadata_uri', 'token_standard', 'collection_address'
                ]
                
                for field in blockchain_fields:
                    if field in content:
                        blockchain_info[field] = content[field]
                        
            except json.JSONDecodeError:
                # Not a JSON file, continue
                pass
    
    except Exception as e:
        logger.error(f"Error extracting blockchain info: {str(e)}")
        blockchain_info['errors'] = [f'Error: {str(e)}']
    
    return blockchain_info


# Module-level function to be called by the extraction engine
def extract_blockchain_provenance_extended(filepath: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extended blockchain and provenance metadata extraction function that integrates with the main extraction engine.
    
    Args:
        filepath: Path to the file to extract metadata from
        result: The main result dictionary to update
        
    Returns:
        Updated result dictionary with blockchain/provenance metadata
    """
    try:
        blockchain_result = extract_blockchain_provenance_metadata(filepath)
        
        # Add blockchain metadata to the main result
        if blockchain_result.get('extraction_success', False):
            result['blockchain_provenance'] = blockchain_result.get('blockchain_provenance', {})
            result['nft_metadata'] = blockchain_result.get('nft_metadata', {})
            result['c2pa_metadata'] = blockchain_result.get('c2pa_metadata', {})
            
            # Add digital signatures if any were found
            if blockchain_result.get('digital_signatures'):
                result['digital_signatures'] = blockchain_result['digital_signatures']
        
        # Add any errors to the main result
        errors = blockchain_result.get('errors', [])
        if errors:
            if 'extraction_errors' not in result:
                result['extraction_errors'] = {}
            result['extraction_errors']['blockchain_extraction'] = errors
    
    except Exception as e:
        logger.error(f"Error in extended blockchain metadata extraction: {str(e)}")
        if 'extraction_errors' not in result:
            result['extraction_errors'] = {}
        result['extraction_errors']['blockchain_extraction'] = [f"Extended extraction error: {str(e)}"]
    
    return result


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_blockchain_provenance_metadata(filepath)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python blockchain_provenance_extractor.py <filepath>")