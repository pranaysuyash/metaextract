"""
Filesystem and Extended Attributes Metadata Extraction
"""
import os
import stat
import hashlib
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

def extract_filesystem_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract comprehensive filesystem metadata.
    
    Returns:
        Dictionary with filesystem metadata
    """
    try:
        stat_info = os.stat(filepath)
        path_obj = Path(filepath)
        
        # Get file times
        created = datetime.fromtimestamp(stat_info.st_birthtime if hasattr(stat_info, 'st_birthtime') else stat_info.st_ctime)
        modified = datetime.fromtimestamp(stat_info.st_mtime)
        accessed = datetime.fromtimestamp(stat_info.st_atime)
        changed = datetime.fromtimestamp(stat_info.st_ctime)
        
        # Get permissions
        mode = stat_info.st_mode
        permissions_octal = oct(stat.S_IMODE(mode))
        permissions_human = stat.filemode(mode)
        
        # Get owner/group info
        try:
            import pwd
            import grp
            owner_name = pwd.getpwuid(stat_info.st_uid).pw_name
            group_name = grp.getgrgid(stat_info.st_gid).gr_name
        except (ImportError, KeyError):
            owner_name = str(stat_info.st_uid)
            group_name = str(stat_info.st_gid)
        
        # Determine file type
        file_type = "regular"
        if stat.S_ISDIR(mode):
            file_type = "directory"
        elif stat.S_ISLNK(mode):
            file_type = "symlink"
        elif stat.S_ISFIFO(mode):
            file_type = "fifo"
        elif stat.S_ISSOCK(mode):
            file_type = "socket"
        elif stat.S_ISBLK(mode):
            file_type = "block_device"
        elif stat.S_ISCHR(mode):
            file_type = "char_device"
        
        return {
            "size_bytes": stat_info.st_size,
            "created": created.isoformat(),
            "modified": modified.isoformat(),
            "accessed": accessed.isoformat(),
            "changed": changed.isoformat(),
            "permissions_octal": permissions_octal,
            "permissions_human": permissions_human,
            "owner": owner_name,
            "owner_uid": stat_info.st_uid,
            "group": group_name,
            "group_gid": stat_info.st_gid,
            "inode": stat_info.st_ino,
            "device": stat_info.st_dev,
            "hard_links": stat_info.st_nlink,
            "file_type": file_type,
            "platform": platform.system()
        }
    except Exception as e:
        return {"error": f"Failed to extract filesystem metadata: {e}"}

def extract_extended_attributes(filepath: str) -> Dict[str, Any]:
    """
    Extract extended attributes (xattr) - macOS/Linux only.
    
    Returns:
        Dictionary with extended attributes
    """
    try:
        import xattr
    except ImportError:
        return {
            "available": False,
            "reason": "xattr not available (Windows or not installed)",
            "platform": platform.system()
        }
    
    try:
        attrs = {}
        x = xattr.xattr(filepath)
        
        for key in x.list():
            try:
                value = x.get(key)
                # Try to decode as string, otherwise keep as bytes
                try:
                    attrs[key.decode() if isinstance(key, bytes) else key] = value.decode()
                except (UnicodeDecodeError, AttributeError):
                    import base64
                    attrs[key.decode() if isinstance(key, bytes) else key] = base64.b64encode(value).decode()
            except Exception as e:
                logger.debug(f"Failed to read file statistics: {e}")
        
        return {
            "available": True,
            "attributes": attrs,
            "count": len(attrs)
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "platform": platform.system()
        }
