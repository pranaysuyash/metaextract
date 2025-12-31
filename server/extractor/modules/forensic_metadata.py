"""
Forensic and Security Metadata
Comprehensive digital signatures, C2PA/Content Authenticity, blockchain, watermarking,
steganography detection, filesystem forensics, and security analysis
"""

from typing import Dict, Any, Optional, List
import os
import stat
import platform
import subprocess
import hashlib
import json
from datetime import datetime


# C2PA (Content Authenticity Initiative) Tags - Expanded
C2PA_TAGS = {
    "C2PA_ManifestPresent": "c2pa_manifest_present",
    "C2PA_ClaimGenerator": "c2pa_claim_generator",
    "C2PA_SignatureValid": "c2pa_signature_valid",
    "C2PA_Assertions": "c2pa_assertions",
    "C2PA_ActionsTaken": "c2pa_actions_taken",
    "C2PA_Ingredients": "c2pa_ingredients",
    "C2PA_Credentials": "c2pa_credentials",
    "C2PA_Timestamp": "c2pa_timestamp",
    "C2PA_Algorithm": "c2pa_algorithm",
    "C2PA_Digest": "c2pa_digest",
    "C2PA_Thumbprint": "c2pa_thumbprint",
    "C2PA_Claim": "c2pa_claim",
    "C2PA_Assertion": "c2pa_assertion",
    "C2PA_SoftwareAgent": "c2pa_software_agent",
    "C2PA_WhenGenerated": "c2pa_when_generated",
    "C2PA_Thumbnail": "c2pa_thumbnail",
    "C2PA_DataHash": "c2pa_data_hash",
    "C2PA_BoxHash": "c2pa_box_hash",
    "C2PA_Exclusion": "c2pa_exclusion",
    "C2PA_UpdateManifest": "c2pa_update_manifest",
}

# Digital Signature Tags - Expanded
DIGITAL_SIGNATURE_TAGS = {
    "Digital_Signature_Present": "digital_signature_present",
    "Digital_Signature_Valid": "digital_signature_valid",
    "Digital_Signature_Issuer": "digital_signature_issuer",
    "Digital_Signature_Subject": "digital_signature_subject",
    "Digital_Signature_Timestamp": "digital_signature_timestamp",
    "Digital_Signature_SerialNumber": "digital_signature_serial",
    "Digital_Signature_Algorithm": "digital_signature_algorithm",
    "Digital_Signature_CertificateChain": "digital_signature_cert_chain",
    "Digital_Signature_OCSP": "digital_signature_ocsp",
    "Digital_Signature_CRL": "digital_signature_crl",
    "Digital_Signature_TrustLevel": "digital_signature_trust_level",
    "Digital_Signature_Expiration": "digital_signature_expiration",
    "Digital_Signature_KeySize": "digital_signature_key_size",
    "Digital_Signature_KeyUsage": "digital_signature_key_usage",
    "Digital_Signature_ExtendedKeyUsage": "digital_signature_extended_key_usage",
    "Digital_Signature_Policy": "digital_signature_policy",
    "Digital_Signature_AuthorityInfoAccess": "digital_signature_authority_info",
    "Digital_Signature_SubjectAltName": "digital_signature_subject_alt_name",
    "Digital_Signature_IssuerAltName": "digital_signature_issuer_alt_name",
    "Digital_Signature_CRLDistributionPoints": "digital_signature_crl_distribution",
}

# Blockchain/NFT Tags - Expanded
BLOCKCHAIN_TAGS = {
    "NFT_ContractAddress": "nft_contract_address",
    "NFT_TokenID": "nft_token_id",
    "NFT_Blockchain": "nft_blockchain",
    "NFT_MintedDate": "nft_minted_date",
    "NFT_CreatorWallet": "nft_creator_wallet",
    "NFT_CurrentOwner": "nft_current_owner",
    "NFT_TransactionHash": "nft_transaction_hash",
    "IPFS_Hash": "ipfs_hash",
    "Arweave_Hash": "arweave_hash",
    "NFT_MetadataURL": "nft_metadata_url",
    "NFT_CollectionName": "nft_collection_name",
    "NFT_TokenStandard": "nft_token_standard",
    "NFT_RoyaltyPercentage": "nft_royalty_percentage",
    "NFT_Attributes": "nft_attributes",
    "NFT_Description": "nft_description",
    "NFT_ImageURL": "nft_image_url",
    "NFT_AnimationURL": "nft_animation_url",
    "NFT_ExternalURL": "nft_external_url",
    "NFT_BackgroundColor": "nft_background_color",
    "NFT_YoutubeURL": "nft_youtube_url",
    "NFT_BlockNumber": "nft_block_number",
    "NFT_GasUsed": "nft_gas_used",
    "NFT_GasPrice": "nft_gas_price",
    "NFT_TransactionFee": "nft_transaction_fee",
    "NFT_Confirmations": "nft_confirmations",
    "NFT_TransferCount": "nft_transfer_count",
    "NFT_LastTransfer": "nft_last_transfer",
    "NFT_RarityScore": "nft_rarity_score",
    "NFT_RarityRank": "nft_rarity_rank",
    "NFT_OpenSeaSlug": "nft_opensea_slug",
    "NFT_TraitCount": "nft_trait_count",
    "NFT_FloorPrice": "nft_floor_price",
    "NFT_LastSalePrice": "nft_last_sale_price",
    "NFT_LastSaleDate": "nft_last_sale_date",
}

# Watermarking & Steganography Tags - Expanded
WATERMARK_TAGS = {
    "Watermark_Detected": "watermark_detected",
    "Watermark_Type": "watermark_type",
    "Watermark_Strength": "watermark_strength",
    "Watermark_Message": "watermark_message",
    "Watermark_Invisible": "watermark_invisible",
    "Watermark_Visible": "watermark_visible",
    "Watermark_Algorithm": "watermark_algorithm",
    "Watermark_Key": "watermark_key",
    "Watermark_EmbeddingStrength": "watermark_embedding_strength",
    "Watermark_DetectionConfidence": "watermark_detection_confidence",
    "Steganography_Detected": "steganography_detected",
    "Steganography_Type": "steganography_type",
    "Steganography_Message": "steganography_message",
    "Steganography_Method": "steganography_method",
    "Steganography_Capacity": "steganography_capacity",
    "Steganography_Key": "steganography_key",
    "Steganography_Algorithm": "steganography_algorithm",
    "Steganography_DetectionConfidence": "steganography_detection_confidence",
    "LSB_Steganography": "lsb_steganography",
    "DCT_Steganography": "dct_steganography",
    "DWT_Steganography": "dwt_steganography",
    "Echo_Hiding": "echo_hiding",
    "Phase_Coding": "phase_coding",
    "Spread_Spectrum": "spread_spectrum",
}

# Adobe Content Credentials - Expanded
ADOBE_CREDENTIALS_TAGS = {
    "Adobe_ContentCredentials_Present": "adobe_credentials_present",
    "Adobe_ClaimGenerator": "adobe_claim_generator",
    "Adobe_SignatureValid": "adobe_signature_valid",
    "Adobe_Actions": "adobe_actions",
    "Adobe_Ingredients": "adobe_ingredients",
    "Adobe_Timestamp": "adobe_timestamp",
    "Adobe_Certificates": "adobe_certificates",
    "Adobe_HashAlgorithm": "adobe_hash_algorithm",
    "Adobe_ClaimGeneratorHints": "adobe_claim_generator_hints",
    "Adobe_AssertionStore": "adobe_assertion_store",
    "Adobe_ManifestStore": "adobe_manifest_store",
    "Adobe_ValidationStatus": "adobe_validation_status",
    "Adobe_ContentBinding": "adobe_content_binding",
    "Adobe_HardBinding": "adobe_hard_binding",
    "Adobe_SoftBinding": "adobe_soft_binding",
    "Adobe_UpdateManifest": "adobe_update_manifest",
}

# Filesystem Forensics Tags
FILESYSTEM_TAGS = {
    "File_Created": "file_created",
    "File_Modified": "file_modified",
    "File_Accessed": "file_accessed",
    "File_Changed": "file_changed",
    "File_Birth": "file_birth",
    "File_Size": "file_size",
    "File_Permissions": "file_permissions",
    "File_Owner": "file_owner",
    "File_Group": "file_group",
    "File_Inode": "file_inode",
    "File_Device": "file_device",
    "File_HardLinks": "file_hardlinks",
    "File_SymlinkTarget": "file_symlink_target",
    "File_ExtendedAttributes": "file_extended_attributes",
    "File_ACL": "file_acl",
    "File_MacTimes": "file_mactimes",
    "File_Deleted": "file_deleted",
    "File_Carved": "file_carved",
    "File_SlackSpace": "file_slack_space",
    "File_UnallocatedSpace": "file_unallocated_space",
    "File_TimestampsModified": "file_timestamps_modified",
    "File_TimestampsAnomaly": "file_timestamps_anomaly",
    "File_Hash_MD5": "file_hash_md5",
    "File_Hash_SHA1": "file_hash_sha1",
    "File_Hash_SHA256": "file_hash_sha256",
    "File_Hash_SHA512": "file_hash_sha512",
    "File_CRC32": "file_crc32",
    "File_SSDeep": "file_ssdeep",
    "File_TLHash": "file_tlhash",
    "File_Entropy": "file_entropy",
    "File_CompressionRatio": "file_compression_ratio",
    "File_EmbeddedFiles": "file_embedded_files",
    "File_AlternateDataStreams": "file_alternate_data_streams",
    "File_ResourceFork": "file_resource_fork",
}

# Device & Hardware Tags
DEVICE_TAGS = {
    "Device_SerialNumber": "device_serial_number",
    "Device_Model": "device_model",
    "Device_Manufacturer": "device_manufacturer",
    "Device_FirmwareVersion": "device_firmware_version",
    "Device_HardwareVersion": "device_hardware_version",
    "Device_BootloaderVersion": "device_bootloader_version",
    "Device_OSVersion": "device_os_version",
    "Device_IMEI": "device_imei",
    "Device_IMSI": "device_imsi",
    "Device_ICCID": "device_iccid",
    "Device_MACAddress": "device_mac_address",
    "Device_BluetoothAddress": "device_bluetooth_address",
    "Device_UUID": "device_uuid",
    "Device_UDID": "device_udid",
    "Device_AndroidID": "device_android_id",
    "Device_AdvertisingID": "device_advertising_id",
    "Device_CPU": "device_cpu",
    "Device_Memory": "device_memory",
    "Device_Storage": "device_storage",
    "Device_BatteryLevel": "device_battery_level",
    "Device_ScreenResolution": "device_screen_resolution",
    "Device_ScreenDensity": "device_screen_density",
    "Device_CameraCount": "device_camera_count",
    "Device_CameraSpecs": "device_camera_specs",
    "Device_Sensors": "device_sensors",
    "Device_Biometrics": "device_biometrics",
    "Device_TPM": "device_tpm",
    "Device_SecureElement": "device_secure_element",
    "Device_EncryptionStatus": "device_encryption_status",
    "Device_RootStatus": "device_root_status",
    "Device_JailbreakStatus": "device_jailbreak_status",
}

# Network & Communication Tags
NETWORK_TAGS = {
    "Network_IPAddress": "network_ip_address",
    "Network_MACAddress": "network_mac_address",
    "Network_Hostname": "network_hostname",
    "Network_Domain": "network_domain",
    "Network_DNS": "network_dns",
    "Network_Gateway": "network_gateway",
    "Network_Subnet": "network_subnet",
    "Network_DHCP": "network_dhcp",
    "Network_WiFi_SSID": "network_wifi_ssid",
    "Network_WiFi_BSSID": "network_wifi_bssid",
    "Network_WiFi_Security": "network_wifi_security",
    "Network_WiFi_SignalStrength": "network_wifi_signal_strength",
    "Network_Bluetooth_Devices": "network_bluetooth_devices",
    "Network_Bluetooth_Paired": "network_bluetooth_paired",
    "Network_Cellular_Carrier": "network_cellular_carrier",
    "Network_Cellular_IMSI": "network_cellular_imsi",
    "Network_Cellular_IMEI": "network_cellular_imei",
    "Network_VPN_Status": "network_vpn_status",
    "Network_Proxy_Status": "network_proxy_status",
    "Network_Firewall_Status": "network_firewall_status",
    "Network_Antivirus_Status": "network_antivirus_status",
    "Network_LastConnection": "network_last_connection",
    "Network_DataUsage": "network_data_usage",
    "Network_ConnectedDevices": "network_connected_devices",
    "Network_SharedFolders": "network_shared_folders",
    "Network_OpenPorts": "network_open_ports",
    "Network_RunningServices": "network_running_services",
}

# Email & Communication Metadata
EMAIL_TAGS = {
    "Email_From": "email_from",
    "Email_To": "email_to",
    "Email_CC": "email_cc",
    "Email_BCC": "email_bcc",
    "Email_Subject": "email_subject",
    "Email_Date": "email_date",
    "Email_MessageID": "email_message_id",
    "Email_InReplyTo": "email_in_reply_to",
    "Email_References": "email_references",
    "Email_ThreadTopic": "email_thread_topic",
    "Email_Headers": "email_headers",
    "Email_Attachments": "email_attachments",
    "Email_AttachmentHashes": "email_attachment_hashes",
    "Email_SPF": "email_spf",
    "Email_DKIM": "email_dkim",
    "Email_DMARC": "email_dmarc",
    "Email_AuthenticationResults": "email_authentication_results",
    "Email_ReceivedHeaders": "email_received_headers",
    "Email_ReturnPath": "email_return_path",
    "Email_ContentType": "email_content_type",
    "Email_Encoding": "email_encoding",
    "Email_Size": "email_size",
    "Email_Priority": "email_priority",
    "Email_Sensitivity": "email_sensitivity",
    "Email_Disposition": "email_disposition",
    "Email_ReadReceipt": "email_read_receipt",
    "Email_Importance": "email_importance",
}

# ULTRA EXPANSION FIELDS
# Additional 25 fields
ULTRA_FORENSIC_FIELDS = {
    "file_hash_md5": "md5_checksum_value",
    "file_hash_sha1": "sha1_checksum_value",
    "file_hash_sha256": "sha256_checksum_value",
    "file_hash_sha512": "sha512_checksum_value",
    "hash_calculation_time": "hash_computation_duration",
    "created_time": "file_creation_timestamp",
    "modified_time": "last_write_timestamp",
    "accessed_time": "last_access_timestamp",
    "entry_modified_time": "mft_entry_change",
    "file_size_changes": "size_modification_history",
    "location_history": "file_path_changes",
    "authorship": "document_author_attribution",
    "software_versions": "application_software_used",
    "print_history": "document_printing_records",
    "email_metadata": "email_headers_addresses",
    "internet_history": "browser_cache_records",
    "download_sources": "file_origin_uris",
    "registry_keys": "windows_registry_artifacts",
    "prefetch_files": "windows_prefetch_analysis",
    "thumbnail_cache": "windows_thumbnail_cache",
    "link_files": "windows_shortcut_files",
    "event_logs": "system_event_logs",
    "memory_dump": "ram_extraction_data",
    "network_artifacts": "network_connection_records",
    "usb_devices": "usb_device_history",
}


# MEGA EXPANSION FIELDS
# Additional 46 fields
MEGA_FORENSIC_FIELDS = {
    "file_carving": "recovered_fragments",
    "slack_space": "unallocated_file_data",
    "deleted_file": "erased_file_recovery",
    "file_timeline": "creation_modification_access",
    "mac_timestamps": "hfs_plus_filesystem_dates",
    "ntfs_timestamps": "windows_filesystem_dates",
    "ext4_timestamps": "linux_filesystem_dates",
    "fat_timestamps": "usb_storage_dates",
    "process_list": "running_processes",
    "network_connections": "active_connections",
    "clipboard_data": "copy_paste_contents",
    "memory_strings": "extracted_text_strings",
    "dump_file": "ram_image_file",
    "memory_artifacts": "allocated_regions",
    "kernel_modules": "loaded_kernel_drivers",
    "registry_hives": "windows_registry_data",
    "device_identifier": "imei_serial_number",
    "operating_system": "ios_android_version",
    "jailbreak_status": "rooted_jailbroken",
    "installed_apps": "application_list",
    "app_usage": "application_activity",
    "location_history": "gps_location_data",
    "call_logs": "phone_call_records",
    "sms_messages": "text_message_content",
    "chat_messages": "instant_messaging_logs",
    "browser_history": "web_browsing_records",
    "wifi_connections": "wireless_network_history",
    "ip_address": "source_destination_ip",
    "mac_address": "hardware_identifier",
    "network_protocol": "tcp_udp_icmp",
    "port_numbers": "source_destination_ports",
    "packet_capture": "pcap_file_data",
    "dns_queries": "domain_name_requests",
    "http_headers": "web_protocol_headers",
    "ssl_certificates": "tls_x509_certs",
    "network_flow": "session_data_transfer",
    "malware_signature": "antivirus_detection",
    "exif_original": "unmodified_exif_data",
    "quantization_table": "jpeg_compression_matrix",
    "thumbnail_original": "embedded_thumbnail_data",
    "image_histogram": "color_distribution",
    "noise_pattern": "sensor_noise_fingerprint",
}

MEGA_FORENSIC_FIELDS.update({
    "compression_artifacts": "image_quality_issues",
    "photo_response": "sensor_response_uniformity",
    "lens_distortion": "geometric_distortion",
    "light_source": "illumination_direction",
})

def extract_filesystem_forensics(filepath: str) -> Dict[str, Any]:
    """Extract filesystem forensic metadata."""
    result = {}

    try:
        stat_info = os.stat(filepath)

        # Basic file times
        result["file_created"] = datetime.fromtimestamp(stat_info.st_birthtime if hasattr(stat_info, 'st_birthtime') else stat_info.st_ctime).isoformat()
        result["file_modified"] = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        result["file_accessed"] = datetime.fromtimestamp(stat_info.st_atime).isoformat()
        result["file_changed"] = datetime.fromtimestamp(stat_info.st_ctime).isoformat()

        # File attributes
        result["file_size"] = stat_info.st_size
        result["file_permissions"] = oct(stat_info.st_mode)[-3:]
        result["file_owner"] = stat_info.st_uid
        result["file_group"] = stat_info.st_gid
        result["file_inode"] = stat_info.st_ino if hasattr(stat_info, 'st_ino') else None
        result["file_device"] = stat_info.st_dev if hasattr(stat_info, 'st_dev') else None
        result["file_hardlinks"] = stat_info.st_nlink

        # Check for anomalies
        if result["file_created"] > result["file_modified"]:
            result["file_timestamps_anomaly"] = True

        # Extended attributes (macOS/Linux)
        try:
            if platform.system() == "Darwin":  # macOS
                import xattr
                extended_attrs = xattr.listxattr(filepath)
                if extended_attrs:
                    result["file_extended_attributes"] = list(extended_attrs)
        except ImportError:
            pass

    except Exception as e:
        result["error"] = str(e)

    return result


def extract_device_metadata(filepath: str) -> Dict[str, Any]:
    """Extract device and hardware metadata."""
    result = {}

    try:
        # Extract from EXIF data
        from .exif import extract_exif_metadata
        exif_data = extract_exif_metadata(filepath)

        if exif_data and "error" not in exif_data:
            # Camera make/model
            if "image" in exif_data:
                image_data = exif_data["image"]
                if "Make" in image_data:
                    result["device_manufacturer"] = image_data["Make"]
                if "Model" in image_data:
                    result["device_model"] = image_data["Model"]
                if "Software" in image_data:
                    result["device_os_version"] = image_data["Software"]

            # Serial numbers and unique IDs
            if "photo" in exif_data:
                photo_data = exif_data["photo"]
                if "BodySerialNumber" in photo_data:
                    result["device_serial_number"] = photo_data["BodySerialNumber"]
                if "SerialNumber" in photo_data:
                    result["device_serial_number"] = photo_data["SerialNumber"]

    except Exception as e:
        result["error"] = str(e)

    return result


def extract_network_metadata(filepath: str) -> Dict[str, Any]:
    """Extract network and communication metadata."""
    result = {}

    try:
        # Extract from EXIF/XMP data that might contain network info
        from .iptc_xmp import extract_iptc_xmp_metadata
        xmp_data = extract_iptc_xmp_metadata(filepath)

        if xmp_data and "error" not in xmp_data:
            # Look for network-related XMP data
            pass  # Placeholder for network metadata extraction

    except Exception as e:
        result["error"] = str(e)

    return result


def extract_email_metadata(filepath: str) -> Dict[str, Any]:
    """Extract email communication metadata."""
    result = {}

    try:
        # Check if file is an email or contains email data
        # This would be expanded for actual email file processing
        pass

    except Exception as e:
        result["error"] = str(e)

    return result


def calculate_file_integrity(filepath: str) -> Dict[str, Any]:
    """Calculate file integrity hashes and metrics."""
    result = {}

    try:
        with open(filepath, 'rb') as f:
            data = f.read()

        # Calculate hashes
        result["file_hash_md5"] = hashlib.md5(data).hexdigest()
        result["file_hash_sha1"] = hashlib.sha1(data).hexdigest()
        result["file_hash_sha256"] = hashlib.sha256(data).hexdigest()
        result["file_hash_sha512"] = hashlib.sha512(data).hexdigest()

        # Calculate entropy (simplified)
        if data:
            entropy = 0
            for byte in range(256):
                p = data.count(byte) / len(data)
                if p > 0:
                    entropy -= p * (p.bit_length() - 1)  # Approximation
            result["file_entropy"] = entropy

        # File size for compression ratio calculation
        result["file_size"] = len(data)

    except Exception as e:
        result["error"] = str(e)

    return result


def extract_forensic_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract comprehensive forensic and security metadata.

    Args:
        filepath: Path to file

    Returns:
        Dictionary with forensic/security metadata
    """
    result = {
        "forensic": {
            "digital_signatures": {},
            "blockchain_nft": {},
            "watermarking": {},
            "c2pa": {},
            "adobe_credentials": {},
            "filesystem": {},
            "device_hardware": {},
            "network_communication": {},
            "email_communication": {}
        },
        "authentication": {
            "is_authenticated": False,
            "confidence_score": 0.0,
            "issues": [],
            "security_flags": []
        },
        "provenance": {},
        "integrity": {},
        "fields_extracted": 0
    }

    try:
        # Extract filesystem metadata
        result["forensic"]["filesystem"] = extract_filesystem_forensics(filepath)

        # Extract device/hardware metadata
        result["forensic"]["device_hardware"] = extract_device_metadata(filepath)

        # Extract network metadata
        result["forensic"]["network_communication"] = extract_network_metadata(filepath)

        # Extract email metadata if applicable
        result["forensic"]["email_communication"] = extract_email_metadata(filepath)

        # Extract from embedded metadata (EXIF, XMP, etc.)
        from .exif import extract_exif_metadata
        from .iptc_xmp import extract_iptc_xmp_metadata

        all_tags = {}

        exif_data = extract_exif_metadata(filepath)
        if exif_data and "error" not in exif_data:
            for category in ["image", "photo", "gps", "interoperability"]:
                if category in exif_data and isinstance(exif_data[category], dict):
                    all_tags.update(exif_data[category])

        iptc_data = extract_iptc_xmp_metadata(filepath)
        if iptc_data and "error" not in iptc_data and isinstance(iptc_data, dict):
            for section in iptc_data.values():
                if isinstance(section, dict):
                    all_tags.update(section)

        # Map tags to forensic categories
        for tag, value in all_tags.items():
            tag_str = str(tag)

            if tag_str in C2PA_TAGS:
                result["forensic"]["c2pa"][C2PA_TAGS[tag_str]] = str(value)

            elif tag_str in DIGITAL_SIGNATURE_TAGS:
                result["forensic"]["digital_signatures"][DIGITAL_SIGNATURE_TAGS[tag_str]] = str(value)

            elif tag_str in BLOCKCHAIN_TAGS:
                result["forensic"]["blockchain_nft"][BLOCKCHAIN_TAGS[tag_str]] = str(value)

            elif tag_str in WATERMARK_TAGS:
                result["forensic"]["watermarking"][WATERMARK_TAGS[tag_str]] = str(value)

            elif tag_str in ADOBE_CREDENTIALS_TAGS:
                result["forensic"]["adobe_credentials"][ADOBE_CREDENTIALS_TAGS[tag_str]] = str(value)

        # Calculate authentication confidence
        has_c2pa = bool(result["forensic"]["c2pa"])
        has_signature = bool(result["forensic"]["digital_signatures"])
        has_blockchain = bool(result["forensic"]["blockchain_nft"])
        has_watermark = bool(result["forensic"]["watermarking"])
        has_adobe = bool(result["forensic"]["adobe_credentials"])

        result["authentication"]["is_authenticated"] = has_c2pa or has_signature or has_blockchain or has_adobe

        confidence = 0.0
        if has_c2pa:
            confidence += 0.4
            if result["forensic"]["c2pa"].get("c2pa_signature_valid") == "true":
                confidence += 0.2
        if has_signature:
            confidence += 0.3
            if result["forensic"]["digital_signatures"].get("digital_signature_valid") == "true":
                confidence += 0.1
        if has_blockchain:
            confidence += 0.3
        if has_adobe:
            confidence += 0.2
            if result["forensic"]["adobe_credentials"].get("adobe_signature_valid") == "true":
                confidence += 0.1

        result["authentication"]["confidence_score"] = min(1.0, confidence)

        # Set security flags and issues
        if not result["authentication"]["is_authenticated"]:
            result["authentication"]["issues"].append("No authentication metadata found")
            result["authentication"]["security_flags"].append("unauthenticated_content")

        if has_watermark:
            result["authentication"]["issues"].append("Watermark detected - content may have been processed")
            result["authentication"]["security_flags"].append("watermarked_content")

        if result["forensic"]["filesystem"].get("file_timestamps_modified"):
            result["authentication"]["issues"].append("File timestamps appear modified")
            result["authentication"]["security_flags"].append("timestamps_modified")

        # Calculate integrity hashes
        result["integrity"] = calculate_file_integrity(filepath)

        # Count total fields extracted
        total_fields = sum(len(v) for v in result["forensic"].values() if isinstance(v, dict))
        result["fields_extracted"] = total_fields

        return result

    except Exception as e:
        return {"error": f"Failed to extract forensic metadata: {str(e)}"}


def analyze_provenance(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Analyze content provenance and editing history.
    
    Args:
        filepath: Path to file
    
    Returns:
        Dictionary with provenance analysis
    """
    result = {
        "provenance_score": 0,
        "editing_history": [],
        "source_determination": "unknown",
        "recommendations": []
    }
    
    forensic_data = extract_forensic_metadata(filepath)
    
    if "error" in forensic_data:
        return {"error": forensic_data["error"]}
    
    c2pa = forensic_data.get("forensic", {}).get("c2pa", {})
    ingredients = c2pa.get("c2pa_ingredients", [])
    actions = c2pa.get("c2pa_actions_taken", [])
    
    if ingredients:
        result["editing_history"].append({
            "type": "ingredient_source",
            "count": len(ingredients) if isinstance(ingredients, list) else 1
        })
        result["provenance_score"] += 20
    
    if actions:
        result["editing_history"].append({
            "type": "editing_actions",
            "actions": actions if isinstance(actions, list) else [actions]
        })
        result["provenance_score"] += 30
    
    blockchain = forensic_data.get("forensic", {}).get("blockchain_nft", {})
    if blockchain:
        result["provenance_score"] += 40
        result["source_determination"] = "blockchain_verified"
    
    watermark = forensic_data.get("forensic", {}).get("watermarking", {})
    if watermark.get("watermark_detected"):
        result["editing_history"].append({
            "type": "watermarking_applied",
            "method": watermark.get("watermark_type", "unknown")
        })
    
    signature = forensic_data.get("forensic", {}).get("digital_signatures", {})
    if signature.get("digital_signature_present"):
        result["provenance_score"] += 30
        result["source_determination"] = "digitally_signed"
    
    if result["provenance_score"] >= 70:
        result["source_determination"] = "high_confidence_provenance"
    elif result["provenance_score"] >= 40:
        result["source_determination"] = "partial_provenance"
    
    if not result["editing_history"]:
        result["recommendations"].append("No editing history available - verify source manually")
    if not blockchain and not signature:
        result["recommendations"].append("Consider adding C2PA credentials for provenance tracking")
    
    return result


def get_forensic_metadata_field_count() -> int:
    """Return total number of forensic_metadata metadata fields."""
    total = 0
    total += len(C2PA_TAGS)
    total += len(DIGITAL_SIGNATURE_TAGS)
    total += len(BLOCKCHAIN_TAGS)
    total += len(WATERMARK_TAGS)
    total += len(ADOBE_CREDENTIALS_TAGS)
    total += len(FILESYSTEM_TAGS)
    total += len(DEVICE_TAGS)
    total += len(NETWORK_TAGS)
    total += len(EMAIL_TAGS)
    total += len(ULTRA_FORENSIC_FIELDS)
    return total


def extract_forensic_metadata_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract comprehensive forensic_metadata metadata from files.

    Args:
        filepath: Path to the file

    Returns:
        Dictionary containing extracted forensic_metadata metadata
    '''
    result = {
        "extracted_fields": {},
        "registry_fields": {},
        "fields_extracted": 0,
        "is_valid_forensic_metadata": False
    }

    try:
        # TODO: Implement specific extraction logic for forensic_metadata
        # This is a template that needs to be customized based on file format

        # Basic file validation
        if not filepath or not os.path.exists(filepath):
            result["error"] = "File path not provided or file doesn't exist"
            return result

        result["is_valid_forensic_metadata"] = True

        # Template structure - customize based on actual format requirements
        try:
            # Add format-specific extraction logic here
            # Examples:
            # - Read file headers
            # - Parse binary structures
            # - Extract metadata fields
            # - Map to registry definitions

            pass  # Replace with actual implementation

        except Exception as e:
            result["error"] = f"forensic_metadata extraction failed: {str(e)[:200]}"

        # Count extracted fields
        total_fields = len(result["extracted_fields"]) + len(result["registry_fields"])
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["error"] = f"forensic_metadata metadata extraction failed: {str(e)[:200]}"

    return result
