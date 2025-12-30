# tests/test_phase4_blockchain_nft.py

import pytest
import os
import tempfile
import json
from server.extractor.modules import blockchain_nft_metadata as bc_nft


def test_blockchain_nft_module_imports():
    """Test that the blockchain_nft_metadata module can be imported and has expected functions."""
    assert hasattr(bc_nft, 'extract_blockchain_nft_metadata')
    assert hasattr(bc_nft, 'extract_blockchain_nft_complete')
    assert hasattr(bc_nft, 'get_blockchain_nft_field_count')


def test_blockchain_nft_field_count():
    """Test that get_blockchain_nft_field_count returns a reasonable number."""
    count = bc_nft.get_blockchain_nft_field_count()
    assert isinstance(count, int)
    assert count > 60  # Should have at least 60+ fields


def test_extract_blockchain_nft_with_invalid_file():
    """Test extraction with non-existent file."""
    result = bc_nft.extract_blockchain_nft_complete('/nonexistent/file.json')
    assert isinstance(result, dict)
    assert 'blockchain_extraction_error' in result


def test_extract_nft_metadata():
    """Test NFT metadata extraction."""
    nft_data = {
        "name": "CryptoPunk #1234",
        "description": "A unique CryptoPunk",
        "image": "ipfs://QmABC123...",
        "attributes": [
            {"trait_type": "Background", "value": "Blue"},
            {"trait_type": "Eyes", "value": "Green"},
            {"trait_type": "Mouth", "value": "Smile"}
        ],
        "properties": {
            "category": "image",
            "creators": [{"address": "0x1234567890123456789012345678901234567890", "share": 100}]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(nft_data, f)
        temp_path = f.name

    try:
        result = bc_nft.extract_blockchain_nft_complete(temp_path)
        assert isinstance(result, dict)
        assert 'blockchain_extraction_error' not in result
        assert result['blockchain_file_type'] == 'nft_metadata'
        assert result['nft_metadata_present'] is True
        assert result['nft_name'] == 'CryptoPunk #1234'
        assert result['nft_description'] == 'A unique CryptoPunk'
        assert result['nft_image'] == 'ipfs://QmABC123...'
        assert result['nft_attributes_count'] == 3
        assert len(result['nft_attributes']) == 3
        assert 'Background' in result['nft_trait_types']
    finally:
        os.unlink(temp_path)


def test_extract_smart_contract_abi():
    """Test smart contract ABI extraction."""
    abi_data = [
        {
            "type": "function",
            "name": "transfer",
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"}
            ],
            "outputs": []
        },
        {
            "type": "event",
            "name": "Transfer",
            "inputs": [
                {"name": "from", "type": "address", "indexed": True},
                {"name": "to", "type": "address", "indexed": True},
                {"name": "value", "type": "uint256"}
            ]
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.abi', delete=False) as f:
        json.dump(abi_data, f)
        temp_path = f.name

    try:
        result = bc_nft.extract_blockchain_nft_complete(temp_path)
        assert result['blockchain_file_type'] == 'smart_contract_abi'
        assert result['smart_contract_abi_present'] is True
        assert result['abi_entry_count'] == 2
        assert result['abi_function_count'] == 1
        assert result['abi_event_count'] == 1
        assert 'transfer(address,uint256)' in result['abi_function_signatures']
    finally:
        os.unlink(temp_path)


def test_extract_smart_contract_source():
    """Test smart contract source code extraction."""
    solidity_code = '''
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract MyNFT is ERC721 {
    uint256 private _tokenIdCounter;

    constructor() ERC721("MyNFT", "MNFT") {}

    function mint(address to) public returns (uint256) {
        _tokenIdCounter++;
        _mint(to, _tokenIdCounter);
        return _tokenIdCounter;
    }

    function _baseURI() internal pure override returns (string memory) {
        return "https://myapi.com/api/token/";
    }
}
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
        f.write(solidity_code)
        temp_path = f.name

    try:
        result = bc_nft.extract_blockchain_nft_complete(temp_path)
        assert result['blockchain_file_type'] == 'smart_contract_source'
        assert result['smart_contract_source_present'] is True
        assert result['contract_language'] == 'Solidity'
        assert result['contract_name'] == 'MyNFT'
        assert result['contract_function_count'] == 2  # mint and _baseURI
        assert result['contract_has_modifier'] is False  # No custom modifiers
    finally:
        os.unlink(temp_path)


def test_analyze_crypto_content():
    """Test cryptocurrency content analysis."""
    content_with_addresses = '''
    {
        "owner": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "contract": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
        "tokenId": "1234",
        "value": "1000000000000000000"
    }
    '''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(content_with_addresses)
        temp_path = f.name

    try:
        result = bc_nft.extract_blockchain_nft_complete(temp_path)
        assert result['ethereum_addresses_found'] >= 2
        assert '0x742d35Cc6634C0532925a3b844Bc454e4438f44e' in result['ethereum_addresses']
        assert '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D' in result['ethereum_addresses']
        assert result['potential_token_amounts'] >= 1
    finally:
        os.unlink(temp_path)


def test_detect_blockchain_file_type():
    """Test blockchain file type detection."""
    # Test NFT metadata detection
    nft_data = {"name": "Test NFT", "description": "A test", "image": "test.png"}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(nft_data, f)
        temp_path = f.name

    try:
        file_type = bc_nft._detect_blockchain_file_type(temp_path, 'nft.json', '.json')
        assert file_type == 'nft_metadata'
    finally:
        os.unlink(temp_path)