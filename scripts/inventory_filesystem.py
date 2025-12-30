#!/usr/bin/env python3
"""File System and OS metadata field inventory.

This script generates an inventory of file system metadata fields
available from various operating systems and file systems:

- NTFS (Windows)
- APFS/HFS+ (macOS)
- ext4/XFS (Linux)
- Extended attributes (xattr)
- File permissions and ACLs
- Timestamps (birth, mod, access, change, deletion)
"""

import json
from pathlib import Path
from typing import Dict, List


# NTFS-specific fields
NTFS_FIELDS = [
    # MFT attributes
    "$STANDARD_INFORMATION", "$ATTRIBUTE_LIST", "$FILE_NAME", "$OBJECT_ID",
    "$SECURITY_DESCRIPTOR", "$VOLUME_NAME", "$VOLUME_INFORMATION", "$DATA",
    "$INDEX_ROOT", "$INDEX_ALLOCATION", "$BITMAP", "$REPARSE_POINT",
    "$EA_INFORMATION", "$EA", "$LOGGED_UTILITY_STREAM",

    # Standard information attributes
    "CreationTime", "LastAccessTime", "LastWriteTime", "ChangeTime",
    "FileAttributes", "MaximumComponentNameLength", "FileNameLength",
    "FileName", "FileAttributes", "ReparsePointIndex", "NumberOfLinks",
    "DeletePending", "Directory", "IndexPresent", "Encrypted",

    # Extended attributes
    "NTFS.EA", "NTFS.EA_INFORMATION", "NTFS.REPARSE",

    # Alternate data streams
    "Zone.Identifier", "ZoneTransferServer", "ZoneTransferSite",

    # Timestamps (USN Journal)
    "USN", "USN_Reason", "USN_SourceInfo", "USN_Page",
    "USN_Version", "USN_Bytes", "USN_Source",

    # Security
    "Owner", "Group", "DiscretionaryACL", "SystemACL",
    "Sacl", "Dacl", "SecurityDescriptor",

    # Object ID
    "ObjectId", "BirthVolumeId", "BirthObjectId", "ObjectIdBirthTime",
    "Droid", "DroidBirth",

    # NTFS timestamps
    "$MFT_Record", "$MFT_Record_Num", "$MFT_Record_Size",
    "$Log_File_Size", "$Volume_Serial_Number", "$Volume_Version",

    # ADS (Alternate Data Streams)
    ":Encryptable", ":Max", ":NoScrubData", ":Scrub",

    # Special NTFS metadata
    "$Secure", "$UsnJrnl", "$Quota", "$ObjId", "$Reparse",
]

# APFS-specific fields
APFS_FIELDS = [
    # APFS volume header
    "APFS_Block_Size", "APFS_Container_Size", "APFS_Num_Volumes",
    "APFS_Vol_Count", "APFS_Feature_Flags", "APFS_Read_Only",

    # APFS volume metadata
    "Volume_Name", "Volume_UUID", "Volume_Creation_Date",
    "Volume_Mod_Date", "Volume_Quotas", "Volume_Snapshots",

    # APFS timestamps
    "APFS_Creation_Timestamp", "APFS_Modification_Timestamp",
    "APFS_Status_Change_Timestamp", "APFS_Birth_Timestamp",

    # APFS flags
    "APFS_Flag_Encrypted", "APFS_Flag_Unencrypted", "APFS_Flag_Journal",
    "APFS_Flag_Rollover", "APFS_Flag_Reser", "APFS_Flag_Defragment",

    # APFS object types
    "APFS_ObjID", "APFS_ObjType", "APFS_ObjRef", "APFS_Owner_ID",

    # APFS clone/refs
    "APFS_Clone_Source", "APFS_Clone_Dest", "APFS_Clone_Ref",
    "APFS_Hardlink", "APFS_Snapshot", "APFS_Snapshot_Name",
    "APFS_Snapshot_Creation", "APFS_Snapshot_Delete",

    # APFS compression
    "APFS_Compression", "APFS_Compressed_Size", "APFS_Original_Size",

    # HFS+ legacy fields (for compatibility)
    "HFS_Creation_Date", "HFS_Modification_Date", "HFS_Access_Date",
    "HFS_Attribute_Mod_Date", "HFS_Backup_Date", "HFS_Checked_Date",
    "HFS_Parent_ID", "HFS_Child_Count", "HFS_Volume_ID",
    "HFS_Comment", "HFS_Finder_Info", "HFS_Icon_Data",
    "HFS_File_Type", "HFS_Creator_Code", "HFS_Reserved",
    "HFS_Text_Encoding", "HFS_Long_Name", "HFS_Short_Name",
]

# HFS+ specific fields
HFS_PLUS_FIELDS = [
    # Volume info
    "Volume_Name", "Volume_Signature", "Volume_Version",
    "Volume_Creation_Date", "Volume_Modification_Date",
    "Volume_Access_Date", "Volume_Backup_Date", "Volume_Checked_Date",

    # Allocation
    "Allocation_Block_Size", "Total_Blocks", "Free_Blocks",

    # Catalog
    "Catalog_File_ID", "Extents_Overflow_File_ID", "Catalog_File_ID",
    "Allocation_File_ID", "Startup_File_ID", "Attributes_File_ID",
    "Extent_File_ID", "Bad_Block_File_ID", "Active_File_ID",

    # Timestamps
    "Create_Date", "Content_Mod_Date", "Attribute_Mod_Date",
    "Access_Date", "Backup_Date", "Checked_Date",

    # Permissions
    "Owner_ID", "Group_ID", "Mode", "Special_Permissions",

    # Finder info
    "Finder_Info", "Finder_Flags", "Finder_Type", "Finder_Creator",
    "Finder_XYZ", "Finder_Window", "Finder_Position", "Finder_Folder",

    # Extended attributes
    "com.apple.ResourceFork", "com.apple.FinderInfo",
    "com.apple.LaunchServices", "com.apple.quarantine",
    "com.apple.metadata", "com.apple.security",
]

# Linux ext4/XFS fields
LINUX_FIELDS = [
    # ext4 inode fields
    "inode_mode", "inode_uid", "inode_size", "inode_atime",
    "inode_ctime", "inode_mtime", "inode_dtime", "inode_gid",
    "inode_links_count", "inode_blocks", "inode_flags",
    "inode_version", "inode_crtime", "inode_extra_isize",
    "inode_projid", "inode_gen", "inode_checksum",

    # ext4 extended attributes
    "xattr_user", "xattr_system", "xattr_security", "xattr_trusted",
    "xattr", "xattrs", "ea", "ea_value",

    # ext4 journal fields
    "jbd2_inode", "jbd2_blocks", "jbd2_handle", "jbd2_trans",
    "jbd2_commit", "jbd2_revoke", "jbd2_credits",

    # ext4 quota fields
    "quota_grace", "quota_limits", "quota_warnings",
    "quota_usage", "quota_timer", "quota_flags",

    # XFS specific
    "xfs_ino", "xfs_ag", "xfs_agf", "xfs_agi", "xfs_agfl",
    "xfs_btree", "xfs_refcount", "xfs_rmap", "xfs_finobt",

    # ACLs
    "acl_user", "acl_group", "acl_default", "acl_mask",
    "acl_other", "acl_access", "acl_defaulted", "acl_inherited",

    # Linux capabilities
    "cap_effective", "cap_permitted", "cap_inheritable",
    "cap_bset", "capAmbient",
]

# File timestamp fields
TIMESTAMP_FIELDS = [
    # Standard timestamps
    "birthtime", "creation_time", "ctime", "mtime", "atime",
    "deletion_time", "removed_time", "backup_time",

    # Extended timestamps
    "metadata_change_time", "status_change_time", "birthtime_ns",
    "mtime_ns", "atime_ns", "ctime_ns", "deletion_time_ns",

    # Timezone info
    "timezone", "utc_offset", "tzname", "dst",

    # Date formats
    "iso8601", "unix_timestamp", "filetime", "hfs_timestamp",
    "ntfs_timestamp", "fat_timestamp",
]

# Permission fields
PERMISSION_FIELDS = [
    # POSIX permissions
    "mode", "uid", "gid", "permissions", "mode_bits",
    "rwxrwxrwx", "suid", "sgid", "sticky",

    # Extended permissions
    "acl", "acl_count", "acl_type", "acl_qualifier",
    "acl_permset", "acl_flags", "acl_entry",

    # Special permissions
    "setuid", "setgid", "sticky_bit", "capabilities",
    "seLinux_context", "seLinux_label", "seLinux_type",

    # File type
    "file_type", "file_type_str", "is_file", "is_dir",
    "is_symlink", "is_socket", "is_fifo", "is_block",
    "is_char", "is_executable",
]

# Generate complete inventory
def generate_inventory(output_dir: Path) -> None:
    """Generate file system metadata field inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "generated_at": "",
        "source": "OS File System Specifications",
        "categories": {},
    }

    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # NTFS fields
    inventory["categories"]["NTFS"] = {
        "description": "Windows NTFS file system fields",
        "fields": sorted(NTFS_FIELDS),
        "count": len(NTFS_FIELDS),
    }

    # APFS fields
    inventory["categories"]["APFS"] = {
        "description": "Apple APFS file system fields",
        "fields": sorted(APFS_FIELDS),
        "count": len(APFS_FIELDS),
    }

    # HFS+ fields
    inventory["categories"]["HFS_Plus"] = {
        "description": "Apple HFS+ file system fields",
        "fields": sorted(HFS_PLUS_FIELDS),
        "count": len(HFS_PLUS_FIELDS),
    }

    # Linux fields
    inventory["categories"]["Linux_ext4_XFS"] = {
        "description": "Linux ext4/XFS file system fields",
        "fields": sorted(LINUX_FIELDS),
        "count": len(LINUX_FIELDS),
    }

    # Timestamp fields
    inventory["categories"]["Timestamps"] = {
        "description": "File timestamp and time-related fields",
        "fields": sorted(TIMESTAMP_FIELDS),
        "count": len(TIMESTAMP_FIELDS),
    }

    # Permission fields
    inventory["categories"]["Permissions"] = {
        "description": "File permission and access control fields",
        "fields": sorted(PERMISSION_FIELDS),
        "count": len(PERMISSION_FIELDS),
    }

    # Calculate totals
    all_fields = (
        NTFS_FIELDS + APFS_FIELDS + HFS_PLUS_FIELDS +
        LINUX_FIELDS + TIMESTAMP_FIELDS + PERMISSION_FIELDS
    )
    unique_fields = len(set(all_fields))

    inventory["totals"] = {
        "total_fields": len(all_fields),
        "unique_fields": unique_fields,
        "categories": len(inventory["categories"]),
    }

    # Write JSON
    output_path = output_dir / "filesystem_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")

    # Print summary
    print()
    print("=" * 60)
    print("FILE SYSTEM METADATA INVENTORY SUMMARY")
    print("=" * 60)
    print()
    print(f"Total fields: {len(all_fields):,}")
    print(f"Unique fields: {unique_fields:,}")
    print(f"Categories: {len(inventory['categories'])}")
    print()

    for cat_name, cat_data in inventory["categories"].items():
        print(f"  {cat_name}: {cat_data['count']:,} fields")

    print()
    print("=" * 60)
    print("TOTAL FILE SYSTEM FIELDS: {:,}".format(len(all_fields)))
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate file system metadata field inventory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/filesystem_inventory"),
        help="Output directory (default: dist/filesystem_inventory)",
    )
    args = parser.parse_args()

    generate_inventory(args.out_dir)


if __name__ == "__main__":
    main()
