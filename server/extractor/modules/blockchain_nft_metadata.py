# server/extractor/modules/blockchain_nft_metadata.py

"""
Blockchain and NFT metadata extraction for Phase 4.

Extracts metadata from:
- NFT metadata files (JSON)
- Smart contract ABIs
- Blockchain transaction data
- Crypto wallet files
- Decentralized application configs
- Token standards (ERC-721, ERC-1155, etc.)
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Common blockchain file extensions
BLOCKCHAIN_EXTENSIONS = [
    '.json', '.abi', '.sol', '.vy', '.rs',  # Smart contracts
    '.keystore', '.key', '.pem', '.crt',   # Keys and certificates
    '.tx', '.trx', '.blk',                 # Transaction/block files
    '.config', '.env',                     # Configuration files
]

# NFT metadata standards
NFT_STANDARDS = {
    'ERC-721': 'erc721',
    'ERC-1155': 'erc1155',
    'ERC-20': 'erc20',
    'BEP-721': 'bep721',
    'BEP-20': 'bep20',
}

# Blockchain networks
BLOCKCHAIN_NETWORKS = {
    'ethereum': ['0x', 'ethereum'],
    'polygon': ['polygon', 'matic'],
    'bsc': ['bsc', 'binance'],
    'solana': ['solana', 'sol'],
    'avalanche': ['avalanche', 'avax'],
    'arbitrum': ['arbitrum'],
    'optimism': ['optimism'],
}


def extract_blockchain_nft_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract blockchain and NFT metadata from various crypto-related files.

    Supports NFT metadata, smart contracts, wallet files, and blockchain data.
    """
    result: Dict[str, Any] = {}

    try:
        if not Path(filepath).exists():
            return {"blockchain_extraction_error": f"File not found: {filepath}"}

        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Detect file type
        file_type = _detect_blockchain_file_type(filepath, filename, file_ext)

        if file_type:
            result['blockchain_file_type'] = file_type

        # Extract based on file type
        if file_type == 'nft_metadata':
            nft_data = _extract_nft_metadata(filepath)
            result.update(nft_data)

        elif file_type == 'smart_contract_abi':
            abi_data = _extract_smart_contract_abi(filepath)
            result.update(abi_data)

        elif file_type == 'smart_contract_source':
            source_data = _extract_smart_contract_source(filepath)
            result.update(source_data)

        elif file_type == 'wallet_keystore':
            wallet_data = _extract_wallet_keystore(filepath)
            result.update(wallet_data)

        elif file_type == 'transaction_data':
            tx_data = _extract_transaction_data(filepath)
            result.update(tx_data)

        elif file_type == 'blockchain_config':
            config_data = _extract_blockchain_config(filepath)
            result.update(config_data)

        # Extract general blockchain properties
        general_data = _extract_general_blockchain_properties(filepath)
        result.update(general_data)

        # Analyze for crypto addresses and tokens
        crypto_analysis = _analyze_crypto_content(filepath)
        result.update(crypto_analysis)

    except Exception as e:
        logger.warning(f"Error extracting blockchain/NFT metadata from {filepath}: {e}")
        result['blockchain_extraction_error'] = str(e)

    return result


def _detect_blockchain_file_type(filepath: str, filename: str, file_ext: str) -> Optional[str]:
    """Detect the type of blockchain-related file."""
    try:
        # Read file content for analysis
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10240)  # Read first 10KB

        # NFT metadata detection
        if file_ext == '.json':
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # Check for NFT metadata fields
                    nft_fields = ['name', 'description', 'image', 'attributes', 'properties']
                    if any(field in data for field in nft_fields):
                        # Check for token standard hints
                        if 'tokenId' in str(data) or 'token_id' in str(data):
                            return 'nft_metadata'
                        return 'nft_metadata'
            except json.JSONDecodeError:
                pass

        # Smart contract ABI detection
        if file_ext == '.abi' or (file_ext == '.json' and 'abi' in filename):
            if '"type":' in content and ('"function"' in content or '"event"' in content):
                return 'smart_contract_abi'

        # Smart contract source detection
        if file_ext in ['.sol', '.vy', '.rs']:
            return 'smart_contract_source'

        # Wallet keystore detection
        if 'keystore' in filename or 'wallet' in filename:
            if 'address' in content.lower() and ('crypto' in content.lower() or 'cipher' in content.lower()):
                return 'wallet_keystore'

        # Transaction data detection
        if file_ext in ['.tx', '.trx'] or 'transaction' in filename:
            return 'transaction_data'

        # Blockchain config detection
        if file_ext in ['.config', '.env'] or 'config' in filename:
            if any(network in content.lower() for network in ['ethereum', 'polygon', 'infura', 'alchemy']):
                return 'blockchain_config'

        # Generic blockchain file detection
        if any(keyword in content.lower() for keyword in ['0x', 'contract', 'token', 'nft', 'blockchain']):
            return 'blockchain_generic'

    except Exception:
        pass

    return None


def _extract_nft_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NFT metadata from JSON files."""
    nft_data: Dict[str, Any] = {'nft_metadata_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        data = json.loads(content)

        # Extract standard NFT fields
        nft_fields = {
            'name': 'nft_name',
            'description': 'nft_description',
            'image': 'nft_image',
            'animation_url': 'nft_animation_url',
            'external_url': 'nft_external_url',
            'background_color': 'nft_background_color',
        }

        for json_field, meta_field in nft_fields.items():
            if json_field in data:
                nft_data[meta_field] = data[json_field]

        # Extract attributes/traits
        if 'attributes' in data and isinstance(data['attributes'], list):
            nft_data['nft_attributes_count'] = len(data['attributes'])
            nft_data['nft_attributes'] = data['attributes']

            # Analyze trait types
            trait_types = []
            for attr in data['attributes']:
                if isinstance(attr, dict) and 'trait_type' in attr:
                    trait_types.append(attr['trait_type'])

            if trait_types:
                nft_data['nft_trait_types'] = list(set(trait_types))

        # Extract properties
        if 'properties' in data:
            nft_data['nft_properties'] = data['properties']

        # Detect token standard
        if 'tokenId' in str(data) or 'token_id' in str(data):
            nft_data['nft_standard_hint'] = 'ERC-721'

        # Extract creator information
        if 'creator' in data:
            nft_data['nft_creator'] = data['creator']

        # Extract collection information
        if 'collection' in data:
            nft_data['nft_collection'] = data['collection']

    except Exception as e:
        nft_data['nft_extraction_error'] = str(e)

    return nft_data


def _extract_smart_contract_abi(filepath: str) -> Dict[str, Any]:
    """Extract smart contract ABI metadata."""
    abi_data: Dict[str, Any] = {'smart_contract_abi_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        abi = json.loads(content)

        if isinstance(abi, list):
            abi_data['abi_entry_count'] = len(abi)

            # Analyze ABI entries
            functions = 0
            events = 0
            constructors = 0

            for entry in abi:
                if isinstance(entry, dict):
                    entry_type = entry.get('type', '')
                    if entry_type == 'function':
                        functions += 1
                    elif entry_type == 'event':
                        events += 1
                    elif entry_type == 'constructor':
                        constructors += 1

            abi_data['abi_function_count'] = functions
            abi_data['abi_event_count'] = events
            abi_data['abi_constructor_count'] = constructors

            # Extract function signatures
            function_names = []
            for entry in abi:
                if isinstance(entry, dict) and entry.get('type') == 'function':
                    name = entry.get('name', '')
                    if name:
                        inputs = entry.get('inputs', [])
                        input_types = [inp.get('type', '') for inp in inputs if isinstance(inp, dict)]
                        signature = f"{name}({','.join(input_types)})"
                        function_names.append(signature)

            if function_names:
                abi_data['abi_function_signatures'] = function_names[:10]  # First 10

    except Exception as e:
        abi_data['abi_extraction_error'] = str(e)

    return abi_data


def _extract_smart_contract_source(filepath: str) -> Dict[str, Any]:
    """Extract smart contract source code metadata."""
    source_data: Dict[str, Any] = {'smart_contract_source_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        file_ext = Path(filepath).suffix.lower()

        # Defaults (tests expect explicit booleans)
        for feature in ["onlyOwner", "require", "assert", "modifier"]:
            source_data[f"contract_has_{feature.lower()}"] = False

        # Language detection
        if file_ext == '.sol':
            source_data['contract_language'] = 'Solidity'
        elif file_ext == '.vy':
            source_data['contract_language'] = 'Vyper'
        elif file_ext == '.rs':
            source_data['contract_language'] = 'Rust'

        # Extract contract name
        if file_ext == '.sol':
            # Look for contract declaration
            contract_match = re.search(r'contract\s+(\w+)', content, re.IGNORECASE)
            if contract_match:
                source_data['contract_name'] = contract_match.group(1)

        # Count functions
        function_count = len(re.findall(r'\bfunction\s+\w+', content, re.IGNORECASE))
        source_data['contract_function_count'] = function_count

        # Check for token standards
        for standard, code in NFT_STANDARDS.items():
            if standard in content:
                source_data[f'contract_implements_{code}'] = True

        # Extract imports
        imports = re.findall(r'import\s+[^;]+;', content, re.IGNORECASE)
        if imports:
            source_data['contract_import_count'] = len(imports)

        # Check for security features
        security_features = ['onlyOwner', 'require', 'assert', 'modifier']
        for feature in security_features:
            if feature in content:
                source_data[f'contract_has_{feature.lower()}'] = True

        # Line count
        source_data['contract_line_count'] = len(content.split('\n'))

    except Exception as e:
        source_data['contract_extraction_error'] = str(e)

    return source_data


def _extract_wallet_keystore(filepath: str) -> Dict[str, Any]:
    """Extract wallet keystore metadata."""
    wallet_data: Dict[str, Any] = {'wallet_keystore_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        data = json.loads(content)

        # Extract address
        if 'address' in data:
            wallet_data['wallet_address'] = data['address']

        # Extract crypto information
        if 'crypto' in data:
            crypto = data['crypto']
            if 'cipher' in crypto:
                wallet_data['wallet_cipher'] = crypto['cipher']
            if 'kdf' in crypto:
                wallet_data['wallet_kdf'] = crypto['kdf']

        # Extract network information
        if 'network' in data:
            wallet_data['wallet_network'] = data['network']

    except Exception as e:
        wallet_data['wallet_extraction_error'] = str(e)

    return wallet_data


def _extract_transaction_data(filepath: str) -> Dict[str, Any]:
    """Extract blockchain transaction metadata."""
    tx_data: Dict[str, Any] = {'transaction_data_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10240)

        # Try to parse as JSON
        try:
            data = json.loads(content)
            tx_data['transaction_format'] = 'json'

            # Extract transaction fields
            tx_fields = ['hash', 'from', 'to', 'value', 'gas', 'gasPrice', 'nonce', 'blockNumber']
            for field in tx_fields:
                if field in data:
                    tx_data[f'transaction_{field}'] = data[field]

        except json.JSONDecodeError:
            # Raw transaction data
            tx_data['transaction_format'] = 'raw'

            # Look for Ethereum transaction patterns
            if content.startswith('0x'):
                tx_data['transaction_starts_with_0x'] = True

    except Exception as e:
        tx_data['transaction_extraction_error'] = str(e)

    return tx_data


def _extract_blockchain_config(filepath: str) -> Dict[str, Any]:
    """Extract blockchain configuration metadata."""
    config_data: Dict[str, Any] = {'blockchain_config_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for network configurations
        for network, keywords in BLOCKCHAIN_NETWORKS.items():
            if any(keyword in content.lower() for keyword in keywords):
                config_data[f'config_network_{network}'] = True

        # Look for API endpoints
        api_patterns = [
            r'https?://[^\'"\s]+\.infura\.io',
            r'https?://[^\'"\s]+\.alchemy\.com',
            r'https?://[^\'"\s]+\.moralis\.io',
        ]

        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            if matches:
                config_data['config_api_endpoints'] = matches

        # Look for private keys (security risk!)
        private_key_patterns = [
            r'0x[a-fA-F0-9]{64}',  # Ethereum private key
            r'[a-fA-F0-9]{64}',    # Generic 64-char hex
        ]

        for pattern in private_key_patterns:
            if re.search(pattern, content):
                config_data['config_contains_private_key'] = True
                break

    except Exception as e:
        config_data['config_extraction_error'] = str(e)

    return config_data


def _extract_general_blockchain_properties(filepath: str) -> Dict[str, Any]:
    """Extract general blockchain-related properties."""
    props = {}

    try:
        # File size
        props['blockchain_file_size'] = Path(filepath).stat().st_size

        # Filename analysis
        filename = Path(filepath).name
        props['blockchain_filename'] = filename

        # Look for addresses in filename
        address_match = re.search(r'0x[a-fA-F0-9]{40}', filename)
        if address_match:
            props['filename_contains_address'] = address_match.group()

    except Exception:
        pass

    return props


def _analyze_crypto_content(filepath: str) -> Dict[str, Any]:
    """Analyze file content for cryptocurrency addresses and tokens."""
    analysis: Dict[str, Any] = {"potential_token_amounts": 0}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10240)

        # Ethereum addresses (0x followed by 40 hex chars)
        eth_addresses = re.findall(r'0x[a-fA-F0-9]{40}', content)
        if eth_addresses:
            analysis['ethereum_addresses_found'] = len(eth_addresses)
            analysis['ethereum_addresses'] = list(set(eth_addresses))[:5]  # First 5 unique

        # Contract addresses (same pattern)
        if len(eth_addresses) > 0:
            analysis['potential_contract_addresses'] = len(eth_addresses)

        # Token amounts (numeric with ETH decimals)
        token_patterns = [
            r'\b\d+\.\d{1,18}\b',  # ETH-like decimals
            r'\b\d{1,3}(?:,\d{3})*\.\d{1,8}\b',  # USD-like decimals
            r'\b\d{10,}\b',  # Large integers (e.g., wei amounts)
        ]

        token_matches = []
        for pattern in token_patterns:
            token_matches.extend(re.findall(pattern, content))

        if token_matches:
            analysis['potential_token_amounts'] = len(token_matches)

        # Blockchain keywords
        blockchain_keywords = ['nft', 'token', 'contract', 'blockchain', 'crypto', 'defi', 'dao']
        found_keywords = [kw for kw in blockchain_keywords if kw in content.lower()]
        if found_keywords:
            analysis['blockchain_keywords'] = found_keywords

    except Exception:
        pass

    return analysis


def get_blockchain_nft_field_count() -> int:
    """Return the number of fields extracted by blockchain/NFT metadata."""
    # File type detection (5)
    type_fields = 5

    # NFT metadata (15)
    nft_fields = 15

    # Smart contract ABI (10)
    abi_fields = 10

    # Smart contract source (15)
    source_fields = 15

    # Wallet keystore (8)
    wallet_fields = 8

    # Transaction data (10)
    tx_fields = 10

    # Blockchain config (10)
    config_fields = 10

    # General properties (5)
    general_fields = 5

    # Crypto analysis (10)
    crypto_fields = 10

    return type_fields + nft_fields + abi_fields + source_fields + wallet_fields + tx_fields + config_fields + general_fields + crypto_fields


# Integration point for metadata_engine.py
def extract_blockchain_nft_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for blockchain/NFT metadata extraction."""
    return extract_blockchain_nft_metadata(filepath)
