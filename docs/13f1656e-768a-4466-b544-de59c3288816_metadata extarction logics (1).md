"""  
Comprehensive Metadata Extractor \- Extract ALL metadata from any file

This module extracts the MOST comprehensive metadata possible from any file:  
\- Filesystem metadata (times, size, permissions, owner, extended attributes)  
\- EXIF data (ALL tags including proprietary MakerNote)  
\- GPS coordinates (with decimal conversion)  
\- Image properties (resolution, color space, ICC profiles)  
\- Video properties (ALL ffprobe fields \- format, streams, chapters)  
\- File integrity (MD5, SHA256 hashes)  
\- Thumbnails (embedded or generated)  
\- Calculated/inferred metadata (aspect ratios, file age, time periods, etc.)

Usage:  
    \# Extract all metadata  
    python metadata\_extractor.py photo.jpg  
      
    \# Save to JSON file  
    python metadata\_extractor.py photo.jpg \--output metadata.json  
      
    \# Extract from multiple files  
    python metadata\_extractor.py photo1.jpg video.mp4 \--output-dir metadata/

Author: Antigravity AI Assistant  
Date: 2025-12-06  
"""

import os  
import sys  
import json  
import stat  
import hashlib  
import logging  
import mimetypes  
from pathlib import Path  
from datetime import datetime, timedelta  
from typing import Any, Dict, List, Optional, Sequence, Tuple  
import base64

\# Image processing  
from PIL import Image  
from PIL.ExifTags import TAGS, GPSTAGS  
import exifread

\# Video processing  
import ffmpeg

\# Audio processing  
try:  
    import mutagen  
    from mutagen.mp3 import MP3  
    from mutagen.flac import FLAC  
    from mutagen.oggvorbis import OggVorbis  
    from mutagen.wave import WAVE  
    from mutagen.aac import AAC  
    from mutagen.mp4 import MP4  
    from mutagen.id3 import ID3  
    MUTAGEN\_AVAILABLE \= True  
except ImportError:  
    MUTAGEN\_AVAILABLE \= False

\# HEIC/HEIF support  
try:  
    from pillow\_heif import register\_heif\_opener  
    register\_heif\_opener()  
    HEIF\_AVAILABLE \= True  
except ImportError:  
    HEIF\_AVAILABLE \= False

\# PDF processing  
try:  
    from pypdf import PdfReader  
    PYPDF\_AVAILABLE \= True  
except ImportError:  
    PYPDF\_AVAILABLE \= False

\# Extended attributes (macOS/Linux)  
try:  
    import xattr  
    XATTR\_AVAILABLE \= True  
except ImportError:  
    XATTR\_AVAILABLE \= False

\# MIME type detection  
try:  
    import magic  
    MAGIC\_AVAILABLE \= True  
except ImportError:  
    MAGIC\_AVAILABLE \= False

\# Configure logging  
logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s \- %(name)s \- %(levelname)s \- %(message)s'  
)  
logger \= logging.getLogger(\_\_name\_\_)

def extract\_filesystem\_metadata(filepath: str) \-\> Dict\[str, Any\]:  
    """  
    Extract comprehensive filesystem metadata.  
      
    Args:  
        filepath: Path to file  
          
    Returns:  
        Dictionary with all filesystem metadata  
    """  
    try:  
        stat\_info \= os.stat(filepath)  
        path\_obj \= Path(filepath)  
          
        \# Get file times  
        created \= datetime.fromtimestamp(stat\_info.st\_birthtime if hasattr(stat\_info, 'st\_birthtime') else stat\_info.st\_ctime)  
        modified \= datetime.fromtimestamp(stat\_info.st\_mtime)  
        accessed \= datetime.fromtimestamp(stat\_info.st\_atime)  
        changed \= datetime.fromtimestamp(stat\_info.st\_ctime)  
          
        \# Get permissions  
        mode \= stat\_info.st\_mode  
        permissions\_octal \= oct(stat.S\_IMODE(mode))  
        permissions\_human \= stat.filemode(mode)  
          
        \# Get owner/group info  
        try:  
            import pwd  
            import grp  
            owner\_name \= pwd.getpwuid(stat\_info.st\_uid).pw\_name  
            group\_name \= grp.getgrgid(stat\_info.st\_gid).gr\_name  
        except (ImportError, KeyError):  
            owner\_name \= str(stat\_info.st\_uid)  
            group\_name \= str(stat\_info.st\_gid)  
          
        \# Determine file type  
        file\_type \= "regular"  
        if stat.S\_ISDIR(mode):  
            file\_type \= "directory"  
        elif stat.S\_ISLNK(mode):  
            file\_type \= "symlink"  
        elif stat.S\_ISFIFO(mode):  
            file\_type \= "fifo"  
        elif stat.S\_ISSOCK(mode):  
            file\_type \= "socket"  
        elif stat.S\_ISBLK(mode):  
            file\_type \= "block\_device"  
        elif stat.S\_ISCHR(mode):  
            file\_type \= "char\_device"  
          
        return {  
            "size\_bytes": stat\_info.st\_size,  
            "size\_human": \_human\_readable\_size(stat\_info.st\_size),  
            "created": created.isoformat(),  
            "modified": modified.isoformat(),  
            "accessed": accessed.isoformat(),  
            "changed": changed.isoformat(),  
            "permissions\_octal": permissions\_octal,  
            "permissions\_human": permissions\_human,  
            "owner": owner\_name,  
            "owner\_uid": stat\_info.st\_uid,  
            "group": group\_name,  
            "group\_gid": stat\_info.st\_gid,  
            "inode": stat\_info.st\_ino,  
            "device": stat\_info.st\_dev,  
            "hard\_links": stat\_info.st\_nlink,  
            "file\_type": file\_type  
        }  
    except Exception as e:  
        logger.error(f"Error extracting filesystem metadata: {e}")  
        return {}

def extract\_extended\_attributes(filepath: str) \-\> Dict\[str, Any\]:  
    """  
    Extract extended attributes (xattr) \- macOS/Linux only.  
      
    Args:  
        filepath: Path to file  
          
    Returns:  
        Dictionary with extended attributes  
    """  
    if not XATTR\_AVAILABLE:  
        return {"available": False, "reason": "xattr not available (Windows or not installed)"}  
      
    try:  
        attrs \= {}  
        x \= xattr.xattr(filepath)  
          
        for key in x.list():  
            try:  
                value \= x.get(key)  
                \# Try to decode as string, otherwise keep as bytes  
                try:  
                    attrs\[key.decode() if isinstance(key, bytes) else key\] \= value.decode()  
                except UnicodeDecodeError:  
                    attrs\[key.decode() if isinstance(key, bytes) else key\] \= base64.b64encode(value).decode()  
            except Exception as e:  
                logger.warning(f"Could not read xattr {key}: {e}")  
          
        return {  
            "available": True,  
            "attributes": attrs  
        }  
    except Exception as e:  
        logger.error(f"Error extracting extended attributes: {e}")  
        return {"available": False, "error": str(e)}

def \_dms\_to\_decimal(dms: Sequence\[float | int\], ref: str) \-\> Optional\[float\]:  
    """  
    Convert GPS coordinates from DMS (degrees, minutes, seconds) to decimal.  
      
    Args:  
        dms: Sequence of (degrees, minutes, seconds)  
        ref: Reference (N/S for latitude, E/W for longitude)  
          
    Returns:  
        Decimal coordinate if conversion succeeds, otherwise None  
    """  
    try:  
        if len(dms) \< 3:  
            return None  
          
        degrees \= float(dms\[0\])  
        minutes \= float(dms\[1\])  
        seconds \= float(dms\[2\])  
          
        decimal \= degrees \+ (minutes / 60.0) \+ (seconds / 3600.0)  
          
        if ref in \['S', 'W'\]:  
            decimal \= \-decimal  
          
        return decimal  
    except Exception as e:  
        logger.error(f"Error converting DMS to decimal: {e}")  
        return None

def extract\_exif\_metadata(filepath: str) \-\> Optional\[Dict\[str, Dict\[str, str\]\]\]:  
    """  
    Extract ALL EXIF metadata including MakerNote.  
      
    Args:  
        filepath: Path to image file  
          
    Returns:  
        Dictionary with all EXIF data  
    """  
    try:  
        \# Use exifread for comprehensive EXIF extraction  
        with open(filepath, 'rb') as f:  
            tags \= exifread.process\_file(f, details=True)  
          
        if not tags:  
            return None  
          
        exif\_data: Dict\[str, Dict\[str, str\]\] \= {}  
          
        \# Organize tags by category  
        for tag, value in tags.items():  
            try:  
                \# Convert value to string  
                tag\_value \= str(value)  
                  
                \# Organize into categories  
                if tag.startswith('Image'):  
                    category \= 'image'  
                elif tag.startswith('EXIF'):  
                    category \= 'exif'  
                elif tag.startswith('GPS'):  
                    category \= 'gps'  
                elif tag.startswith('MakerNote'):  
                    category \= 'makernote'  
                elif tag.startswith('Thumbnail'):  
                    category \= 'thumbnail'  
                elif tag.startswith('Interoperability'):  
                    category \= 'interoperability'  
                else:  
                    category \= 'other'  
                  
                if category not in exif\_data:  
                    exif\_data\[category\] \= {}  
                  
                \# Clean tag name  
                clean\_tag \= tag.split(' ', 1)\[1\] if ' ' in tag else tag  
                exif\_data\[category\]\[clean\_tag\] \= tag\_value  
            except Exception as e:  
                logger.warning(f"Could not process EXIF tag {tag}: {e}")  
          
        return exif\_data  
    except Exception as e:  
        logger.error(f"Error extracting EXIF metadata: {e}")  
        return None

def extract\_gps\_metadata(filepath: str) \-\> Optional\[Dict\[str, Any\]\]:  
    """  
    Extract GPS metadata from EXIF.  
      
    Args:  
        filepath: Path to image file  
          
    Returns:  
        Dictionary with GPS data  
    """  
    try:  
        with open(filepath, 'rb') as f:  
            tags \= exifread.process\_file(f, details=False)  
          
        gps\_data: Dict\[str, Any\] \= {}  
          
        \# Extract GPS coordinates  
        if 'GPS GPSLatitude' in tags and 'GPS GPSLatitudeRef' in tags:  
            lat\_dms \= \[float(x.num) / float(x.den) for x in tags\['GPS GPSLatitude'\].values\]  
            lat\_ref \= str(tags\['GPS GPSLatitudeRef'\])  
            gps\_data\['latitude'\] \= \_dms\_to\_decimal(lat\_dms, lat\_ref)  
            gps\_data\['latitude\_ref'\] \= lat\_ref  
          
        if 'GPS GPSLongitude' in tags and 'GPS GPSLongitudeRef' in tags:  
            lon\_dms \= \[float(x.num) / float(x.den) for x in tags\['GPS GPSLongitude'\].values\]  
            lon\_ref \= str(tags\['GPS GPSLongitudeRef'\])  
            gps\_data\['longitude'\] \= \_dms\_to\_decimal(lon\_dms, lon\_ref)  
            gps\_data\['longitude\_ref'\] \= lon\_ref  
          
        \# Extract altitude  
        if 'GPS GPSAltitude' in tags:  
            alt \= tags\['GPS GPSAltitude'\]  
            gps\_data\['altitude'\] \= float(alt.values\[0\].num) / float(alt.values\[0\].den)  
            if 'GPS GPSAltitudeRef' in tags:  
                alt\_ref \= int(str(tags\['GPS GPSAltitudeRef'\]))  
                gps\_data\['altitude\_ref'\] \= 'below\_sea\_level' if alt\_ref \== 1 else 'above\_sea\_level'  
          
        \# Extract other GPS fields  
        gps\_fields \= {  
            'GPS GPSTimeStamp': 'timestamp',  
            'GPS GPSDateStamp': 'datestamp',  
            'GPS GPSSpeed': 'speed',  
            'GPS GPSSpeedRef': 'speed\_ref',  
            'GPS GPSTrack': 'track',  
            'GPS GPSTrackRef': 'track\_ref',  
            'GPS GPSImgDirection': 'image\_direction',  
            'GPS GPSImgDirectionRef': 'image\_direction\_ref',  
            'GPS GPSSatellites': 'satellites',  
            'GPS GPSDOP': 'dop',  
            'GPS GPSMapDatum': 'map\_datum',  
            'GPS GPSProcessingMethod': 'processing\_method'  
        }  
          
        for tag, key in gps\_fields.items():  
            if tag in tags:  
                gps\_data\[key\] \= str(tags\[tag\])  
          
        return gps\_data if gps\_data else None  
    except Exception as e:  
        logger.error(f"Error extracting GPS metadata: {e}")  
        return None

def extract\_image\_properties(filepath: str) \-\> Optional\[Dict\[str, Any\]\]:  
    """  
    Extract image properties using Pillow.  
      
    Args:  
        filepath: Path to image file  
          
    Returns:  
        Dictionary with image properties  
    """  
    try:  
        with Image.open(filepath) as img:  
            return {  
                "width": img.width,  
                "height": img.height,  
                "format": img.format,  
                "mode": img.mode,  
                "dpi": img.info.get('dpi', None),  
                "bits\_per\_pixel": len(img.getbands()) \* 8 if hasattr(img, 'getbands') else None,  
                "color\_palette": "yes" if img.palette else "no",  
                "animation": hasattr(img, 'n\_frames') and img.n\_frames \> 1,  
                "frames": img.n\_frames if hasattr(img, 'n\_frames') else 1,  
                "icc\_profile": "yes" if img.info.get('icc\_profile') else "no"  
            }  
    except Exception as e:  
        logger.error(f"Error extracting image properties: {e}")  
        return None

def extract\_video\_properties(filepath: str) \-\> Optional\[Dict\[str, Any\]\]:  
    """  
    Extract comprehensive video metadata using ffprobe.  
      
    Args:  
        filepath: Path to video file  
          
    Returns:  
        Dictionary with all video metadata  
    """  
    try:  
        \# Get format information  
        probe \= ffmpeg.probe(filepath)  
          
        video\_data \= {  
            "format": probe.get('format', {}),  
            "streams": probe.get('streams', \[\]),  
            "chapters": probe.get('chapters', \[\])  
        }  
          
        return video\_data  
    except Exception as e:  
        logger.error(f"Error extracting video properties: {e}")  
        return None

def extract\_audio\_properties(filepath: str) \-\> Optional\[Dict\[str, Any\]\]:  
    """  
    Extract comprehensive audio metadata using mutagen.  
      
    Supports: MP3, FLAC, OGG, WAV, AAC, M4A, MP4 audio  
      
    Args:  
        filepath: Path to audio file  
          
    Returns:  
        Dictionary with all audio metadata  
    """  
    if not MUTAGEN\_AVAILABLE:  
        return {"error": "mutagen not available"}  
      
    try:  
        audio \= mutagen.File(filepath)  
        if audio is None:  
            return None  
          
        audio\_data: Dict\[str, Any\] \= {  
            "format": type(audio).\_\_name\_\_,  
            "length\_seconds": round(audio.info.length, 2\) if hasattr(audio.info, 'length') else None,  
            "length\_human": None,  
            "bitrate": getattr(audio.info, 'bitrate', None),  
            "sample\_rate": getattr(audio.info, 'sample\_rate', None),  
            "channels": getattr(audio.info, 'channels', None),  
            "bits\_per\_sample": getattr(audio.info, 'bits\_per\_sample', None),  
        }  
          
        \# Format duration  
        length\_seconds \= audio\_data.get("length\_seconds")  
        if isinstance(length\_seconds, (int, float)):  
            mins \= int(length\_seconds // 60\)  
            secs \= int(length\_seconds % 60\)  
            audio\_data\["length\_human"\] \= f"{mins}:{secs:02d}"  
          
        \# Extract tags (ID3, Vorbis Comments, etc.)  
        tags: Dict\[str, Any\] \= {}  
        if hasattr(audio, 'tags') and audio.tags:  
            for key, value in audio.tags.items():  
                \# Clean up tag names and values  
                tag\_name \= str(key).split(':')\[0\] if ':' in str(key) else str(key)  
                if hasattr(value, 'text'):  
                    tags\[tag\_name\] \= str(value.text\[0\]) if value.text else None  
                elif isinstance(value, list):  
                    tags\[tag\_name\] \= str(value\[0\]) if value else None  
                else:  
                    tags\[tag\_name\] \= str(value)  
          
        \# Common tag mapping  
        audio\_data\["tags"\] \= {  
            "title": tags.get('TIT2') or tags.get('TITLE') or tags.get('title'),  
            "artist": tags.get('TPE1') or tags.get('ARTIST') or tags.get('artist'),  
            "album": tags.get('TALB') or tags.get('ALBUM') or tags.get('album'),  
            "year": tags.get('TDRC') or tags.get('DATE') or tags.get('date'),  
            "genre": tags.get('TCON') or tags.get('GENRE') or tags.get('genre'),  
            "track\_number": tags.get('TRCK') or tags.get('TRACKNUMBER') or tags.get('tracknumber'),  
            "composer": tags.get('TCOM') or tags.get('COMPOSER') or tags.get('composer'),  
            "album\_artist": tags.get('TPE2') or tags.get('ALBUMARTIST') or tags.get('albumartist'),  
            "comment": tags.get('COMM') or tags.get('COMMENT') or tags.get('comment'),  
            "lyrics": tags.get('USLT') or tags.get('LYRICS'),  
        }  
          
        \# Check for embedded album art  
        audio\_data\["has\_album\_art"\] \= False  
        if hasattr(audio, 'pictures') and audio.pictures:  
            audio\_data\["has\_album\_art"\] \= True  
            audio\_data\["album\_art\_count"\] \= len(audio.pictures)  
        elif 'APIC' in tags or 'APIC:' in str(audio.tags.keys()) if audio.tags else False:  
            audio\_data\["has\_album\_art"\] \= True  
          
        \# Raw tags for completeness  
        audio\_data\["raw\_tags"\] \= tags  
          
        return audio\_data  
    except Exception as e:  
        logger.error(f"Error extracting audio properties: {e}")  
        return None

def extract\_pdf\_properties(filepath: str) \-\> Optional\[Dict\[str, Any\]\]:  
    """  
    Extract PDF metadata using pypdf.  
      
    Args:  
        filepath: Path to PDF file  
          
    Returns:  
        Dictionary with PDF metadata  
    """  
    if not PYPDF\_AVAILABLE:  
        return {"error": "pypdf not available"}  
      
    try:  
        reader \= PdfReader(filepath)  
          
        \# Get document info  
        info: Dict\[str, Any\] \= dict(reader.metadata or {})  
          
        pdf\_data: Dict\[str, Any\] \= {  
            "page\_count": len(reader.pages),  
            "encrypted": reader.is\_encrypted,  
            "author": info.get('/Author'),  
            "creator": info.get('/Creator'),  
            "producer": info.get('/Producer'),  
            "subject": info.get('/Subject'),  
            "title": info.get('/Title'),  
            "creation\_date": str(info.get('/CreationDate')) if info.get('/CreationDate') else None,  
            "modification\_date": str(info.get('/ModDate')) if info.get('/ModDate') else None,  
            "keywords": info.get('/Keywords'),  
        }  
          
        \# Get page dimensions from first page  
        if reader.pages:  
            first\_page \= reader.pages\[0\]  
            if first\_page.mediabox:  
                pdf\_data\["page\_width"\] \= float(first\_page.mediabox.width)  
                pdf\_data\["page\_height"\] \= float(first\_page.mediabox.height)  
          
        return pdf\_data  
    except Exception as e:  
        logger.error(f"Error extracting PDF properties: {e}")  
        return None

def extract\_svg\_properties(filepath: str) \-\> Optional\[Dict\[str, Any\]\]:  
    """  
    Extract SVG metadata by parsing XML.  
      
    Args:  
        filepath: Path to SVG file  
          
    Returns:  
        Dictionary with SVG metadata  
    """  
    try:  
        import xml.etree.ElementTree as ET  
          
        tree \= ET.parse(filepath)  
        root \= tree.getroot()  
          
        \# Handle namespace  
        ns \= {'svg': 'http://www.w3.org/2000/svg'}  
          
        svg\_data: Dict\[str, Any\] \= {  
            "width": root.get('width'),  
            "height": root.get('height'),  
            "viewBox": root.get('viewBox'),  
            "version": root.get('version'),  
        }  
          
        \# Parse viewBox for dimensions if width/height not specified  
        if svg\_data\["viewBox"\] and not svg\_data\["width"\]:  
            parts \= svg\_data\["viewBox"\].split()  
            if len(parts) \>= 4:  
                svg\_data\["viewBox\_width"\] \= parts\[2\]  
                svg\_data\["viewBox\_height"\] \= parts\[3\]  
          
        \# Count elements  
        svg\_data\["element\_count"\] \= len(list(root.iter()))  
          
        \# Find specific elements  
        path\_count \= len(root.findall('.//{http://www.w3.org/2000/svg}path') or root.findall('.//path'))  
        svg\_data\["path\_count"\] \= path\_count  
          
        \# Check for embedded styles  
        style\_elements \= root.findall('.//{http://www.w3.org/2000/svg}style') or root.findall('.//style')  
        svg\_data\["has\_embedded\_styles"\] \= len(style\_elements) \> 0  
          
        \# Check for scripts (security concern)  
        script\_elements \= root.findall('.//{http://www.w3.org/2000/svg}script') or root.findall('.//script')  
        svg\_data\["has\_scripts"\] \= len(script\_elements) \> 0  
          
        return svg\_data  
    except Exception as e:  
        logger.error(f"Error extracting SVG properties: {e}")  
        return None

def extract\_file\_hashes(filepath: str) \-\> Dict\[str, str\]:  
    """  
    Calculate file hashes for integrity verification.  
      
    Args:  
        filepath: Path to file  
          
    Returns:  
        Dictionary with MD5 and SHA256 hashes  
    """  
    try:  
        md5\_hash \= hashlib.md5()  
        sha256\_hash \= hashlib.sha256()  
          
        with open(filepath, 'rb') as f:  
            \# Read in chunks to handle large files  
            for chunk in iter(lambda: f.read(4096), b""):  
                md5\_hash.update(chunk)  
                sha256\_hash.update(chunk)  
          
        return {  
            "md5": md5\_hash.hexdigest(),  
            "sha256": sha256\_hash.hexdigest()  
        }  
    except Exception as e:  
        logger.error(f"Error calculating file hashes: {e}")  
        return {}

def extract\_thumbnail(filepath: str) \-\> Optional\[Dict\[str, Any\]\]:  
    """  
    Extract or generate thumbnail.  
      
    Args:  
        filepath: Path to image file  
          
    Returns:  
        Dictionary with thumbnail info  
    """  
    try:  
        with Image.open(filepath) as img:  
            \# Check for embedded thumbnail in EXIF  
            has\_embedded \= hasattr(img, '\_getexif') and img.\_getexif() is not None  
              
            \# Generate small thumbnail  
            img.thumbnail((160, 160))  
              
            return {  
                "has\_embedded": has\_embedded,  
                "width": img.width,  
                "height": img.height  
            }  
    except Exception as e:  
        logger.error(f"Error extracting thumbnail: {e}")  
        return None

def \_human\_readable\_size(size\_bytes: float) \-\> str:  
    """Convert bytes to human-readable format."""  
    for unit in \['B', 'KB', 'MB', 'GB', 'TB'\]:  
        if size\_bytes \< 1024.0:  
            return f"{size\_bytes:.1f} {unit}"  
        size\_bytes /= 1024.0  
    return f"{size\_bytes:.1f} PB"

def \_human\_readable\_time\_delta(delta: timedelta) \-\> str:  
    """Convert timedelta to human-readable format."""  
    seconds \= int(delta.total\_seconds())  
      
    if seconds \< 60:  
        return "just now"  
    elif seconds \< 3600:  
        minutes \= seconds // 60  
        return f"{minutes} minute{'s' if minutes \!= 1 else ''} ago"  
    elif seconds \< 86400:  
        hours \= seconds // 3600  
        return f"{hours} hour{'s' if hours \!= 1 else ''} ago"  
    elif seconds \< 2592000:  \# 30 days  
        days \= seconds // 86400  
        return f"{days} day{'s' if days \!= 1 else ''} ago"  
    elif seconds \< 31536000:  \# 365 days  
        months \= seconds // 2592000  
        return f"{months} month{'s' if months \!= 1 else ''} ago"  
    else:  
        years \= seconds // 31536000  
        return f"{years} year{'s' if years \!= 1 else ''} ago"

def calculate\_inferred\_metadata(metadata: Dict\[str, Any\], current\_time: datetime) \-\> Dict\[str, Any\]:  
    """  
    Calculate inferred/derived metadata from extracted data.  
      
    Args:  
        metadata: Extracted metadata dictionary  
        current\_time: Current timestamp for time calculations  
          
    Returns:  
        Dictionary with calculated metadata  
    """  
    calculated: Dict\[str, Any\] \= {}  
      
    try:  
        \# Image calculations  
        if metadata.get('image'):  
            img \= metadata\['image'\] or {}  
            width \= img.get('width')  
            height \= img.get('height')  
            if isinstance(width, (int, float)) and isinstance(height, (int, float)):  
                \# Aspect ratio  
                from math import gcd  
                divisor \= gcd(int(width), int(height)) or 1  
                calculated\['aspect\_ratio'\] \= f"{int(width)//divisor}:{int(height)//divisor}"  
                calculated\['aspect\_ratio\_decimal'\] \= round(float(width) / float(height), 3\)  
                  
                \# Megapixels  
                calculated\['megapixels'\] \= round((float(width) \* float(height)) / 1\_000\_000, 2\)  
                  
                \# Orientation  
                if width \> height:  
                    calculated\['orientation'\] \= 'landscape'  
                elif height \> width:  
                    calculated\['orientation'\] \= 'portrait'  
                else:  
                    calculated\['orientation'\] \= 'square'  
          
        \# Video calculations  
        if metadata.get('video') and metadata\['video'\].get('format'):  
            fmt \= metadata\['video'\]\['format'\] or {}  
            duration\_value \= fmt.get('duration')  
            duration \= float(duration\_value) if duration\_value is not None else None  
            if duration:  
                calculated\['duration\_human'\] \= f"{int(duration // 60)}:{int(duration % 60):02d}"  
                  
                \# Size per second  
                size\_bytes \= metadata.get('filesystem', {}).get('size\_bytes')  
                if isinstance(size\_bytes, (int, float)):  
                    calculated\['size\_per\_second'\] \= \_human\_readable\_size(size\_bytes / duration)  
          
        \# Time-based calculations  
        if metadata.get('filesystem'):  
            fs \= metadata\['filesystem'\]  
              
            if fs.get('created'):  
                created \= datetime.fromisoformat(fs\['created'\])  
                age\_delta \= current\_time \- created  
                calculated\['file\_age'\] \= {  
                    "days": age\_delta.days,  
                    "hours": int(age\_delta.total\_seconds() // 3600),  
                    "human\_readable": \_human\_readable\_time\_delta(age\_delta)  
                }  
              
            if fs.get('modified'):  
                modified \= datetime.fromisoformat(fs\['modified'\])  
                mod\_delta \= current\_time \- modified  
                calculated\['time\_since\_modified'\] \= {  
                    "days": mod\_delta.days,  
                    "hours": int(mod\_delta.total\_seconds() // 3600),  
                    "human\_readable": \_human\_readable\_time\_delta(mod\_delta)  
                }  
              
            if fs.get('accessed'):  
                accessed \= datetime.fromisoformat(fs\['accessed'\])  
                acc\_delta \= current\_time \- accessed  
                calculated\['time\_since\_accessed'\] \= {  
                    "days": acc\_delta.days,  
                    "hours": int(acc\_delta.total\_seconds() // 3600),  
                    "human\_readable": \_human\_readable\_time\_delta(acc\_delta)  
                }  
      
    except Exception as e:  
        logger.error(f"Error calculating inferred metadata: {e}")  
      
    return calculated

def extract\_all\_metadata(filepath: str) \-\> Dict\[str, Any\]:  
    """  
    Extract ALL metadata from a file.  
      
    Args:  
        filepath: Path to file  
          
    Returns:  
        Complete metadata dictionary  
    """  
    current\_time \= datetime.now()  
      
    \# Detect MIME type  
    mime\_type \= mimetypes.guess\_type(filepath)\[0\]  
    if MAGIC\_AVAILABLE:  
        try:  
            mime\_type \= magic.from\_file(filepath, mime=True)  
        except:  
            pass  
      
    metadata: Dict\[str, Any\] \= {  
        "file": {  
            "path": str(Path(filepath).absolute()),  
            "name": Path(filepath).name,  
            "extension": Path(filepath).suffix,  
            "mime\_type": mime\_type  
        },  
        "filesystem": extract\_filesystem\_metadata(filepath),  
        "extended\_attributes": extract\_extended\_attributes(filepath),  
        "image": None,  
        "exif": None,  
        "gps": None,  
        "video": None,  
        "audio": None,  
        "pdf": None,  
        "svg": None,  
        "hashes": extract\_file\_hashes(filepath),  
        "thumbnail": None,  
        "calculated": {}  
    }  
      
    \# Get file extension for additional checks  
    ext \= Path(filepath).suffix.lower()  
      
    \# Extract image-specific metadata  
    if mime\_type and mime\_type.startswith('image'):  
        metadata\['image'\] \= extract\_image\_properties(filepath)  
        metadata\['exif'\] \= extract\_exif\_metadata(filepath)  
        metadata\['gps'\] \= extract\_gps\_metadata(filepath)  
        metadata\['thumbnail'\] \= extract\_thumbnail(filepath)  
      
    \# Extract video-specific metadata  
    elif mime\_type and mime\_type.startswith('video'):  
        metadata\['video'\] \= extract\_video\_properties(filepath)  
      
    \# Extract audio-specific metadata  
    elif mime\_type and mime\_type.startswith('audio'):  
        metadata\['audio'\] \= extract\_audio\_properties(filepath)  
      
    \# Also check by extension for audio files that may have wrong MIME type  
    elif ext in \['.mp3', '.flac', '.ogg', '.wav', '.m4a', '.aac', '.wma', '.opus'\]:  
        metadata\['audio'\] \= extract\_audio\_properties(filepath)  
      
    \# Extract PDF metadata  
    elif mime\_type \== 'application/pdf' or ext \== '.pdf':  
        metadata\['pdf'\] \= extract\_pdf\_properties(filepath)  
      
    \# Extract SVG metadata  
    elif mime\_type \== 'image/svg+xml' or ext \== '.svg':  
        metadata\['svg'\] \= extract\_svg\_properties(filepath)  
      
    \# Calculate inferred metadata  
    metadata\['calculated'\] \= calculate\_inferred\_metadata(metadata, current\_time)  
      
    return metadata

def save\_metadata\_json(metadata: Dict\[str, Any\], output\_file: str):  
    """  
    Save metadata to JSON file.  
      
    Args:  
        metadata: Metadata dictionary  
        output\_file: Output file path  
    """  
    try:  
        \# Create output directory if needed  
        Path(output\_file).parent.mkdir(parents=True, exist\_ok=True)  
          
        with open(output\_file, 'w') as f:  
            json.dump(metadata, f, indent=2, default=str)  
          
        logger.info(f"Metadata saved to {output\_file}")  
    except Exception as e:  
        logger.error(f"Error saving metadata: {e}")

def main():  
    """Main CLI interface."""  
    import argparse  
      
    parser \= argparse.ArgumentParser(  
        description='Comprehensive Metadata Extractor',  
        formatter\_class=argparse.RawDescriptionHelpFormatter,  
        epilog="""  
Examples:  
  \# Extract metadata from single file  
  python metadata\_extractor.py photo.jpg  
    
  \# Save to JSON file  
  python metadata\_extractor.py photo.jpg \--output metadata.json  
    
  \# Extract from multiple files  
  python metadata\_extractor.py photo1.jpg video.mp4  
    
  \# Batch process to directory  
  python metadata\_extractor.py \*.jpg \--output-dir metadata/  
        """  
    )  
      
    parser.add\_argument('files', nargs='+', help='File(s) to extract metadata from')  
    parser.add\_argument('--output', '-o', help='Output JSON file')  
    parser.add\_argument('--output-dir', '-d', help='Output directory for batch processing')  
    parser.add\_argument('--pretty', action='store\_true', default=True, help='Pretty print JSON')  
      
    args \= parser.parse\_args()  
      
    \# Process files  
    for filepath in args.files:  
        \# Convert to Path object for better handling  
        file\_path \= Path(filepath).expanduser().resolve()  
          
        \# Check if file exists  
        if not file\_path.exists():  
            logger.error(f"File not found: {filepath}")  
            logger.debug(f"Tried absolute path: {file\_path}")  
            continue  
          
        if not file\_path.is\_file():  
            logger.error(f"Not a file: {filepath}")  
            continue  
          
        logger.info(f"Extracting metadata from: {filepath}")  
          
        try:  
            metadata \= extract\_all\_metadata(str(file\_path))  
              
            \# Determine output  
            if args.output:  
                save\_metadata\_json(metadata, args.output)  
            elif args.output\_dir:  
                output\_file \= Path(args.output\_dir) / f"{file\_path.stem}\_metadata.json"  
                save\_metadata\_json(metadata, str(output\_file))  
            else:  
                \# Print to console  
                print(json.dumps(metadata, indent=2 if args.pretty else None, default=str))  
        except Exception as e:  
            logger.error(f"Error processing {filepath}: {e}")  
            continue

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()

import os  
from pathlib import Path  
from typing import Union, Tuple, Dict, Any  
from PIL import Image, UnidentifiedImageError  
import requests  
from requests.adapters import HTTPAdapter  
from urllib3.util.retry import Retry  
from io import BytesIO  
import logging

\# Configure logging  
logger \= logging.getLogger(\_\_name\_\_)

\# Create a session with connection pooling and retry strategy  
\_session \= None

def get\_http\_session():  
    """Get a shared HTTP session with connection pooling."""  
    global \_session  
    if \_session is None:  
        \_session \= requests.Session()  
          
        \# Configure retry strategy  
        retry\_strategy \= Retry(  
            total=3,  
            backoff\_factor=1,  
            status\_forcelist=\[429, 500, 502, 503, 504\],  
        )  
          
        \# Configure adapter with connection pooling  
        adapter \= HTTPAdapter(  
            max\_retries=retry\_strategy,  
            pool\_connections=10,  
            pool\_maxsize=20  
        )  
          
        \_session.mount("http://", adapter)  
        \_session.mount("https://", adapter)  
          
        \# Set timeout  
        \_session.timeout \= 10  
          
    return \_session

def load\_image(source: Union\[str, Path\]) \-\> Image.Image:  
    """  
    Load an image from a local path or URL.  
      
    Args:  
        source: File path (str/Path) or URL (str)  
          
    Returns:  
        PIL.Image.Image: Loaded image object  
          
    Raises:  
        FileNotFoundError: If local file doesn't exist  
        ValueError: If URL cannot be fetched or image format is invalid  
    """  
    source\_str \= str(source)  
      
    try:  
        \# Check if URL  
        if source\_str.startswith(('http://', 'https://')):  
            session \= get\_http\_session()  
            response \= session.get(source\_str)  
            response.raise\_for\_status()  
            img \= Image.open(BytesIO(response.content))  
        else:  
            \# Local file  
            path \= Path(source)  
            if not path.exists():  
                raise FileNotFoundError(f"Image not found: {path}")  
            img \= Image.open(path)  
              
        \# Force loading to ensure file is read and verify integrity  
        img.load()  
        return img  
          
    except (UnidentifiedImageError, OSError) as e:  
        raise ValueError(f"Invalid image format or corrupted file: {source}") from e  
    except requests.RequestException as e:  
        raise ValueError(f"Failed to fetch image from URL: {source}") from e

def process\_image(image: Image.Image, target\_size: int \= 512\) \-\> Image.Image:  
    """  
    Resize and normalize image for processing/display.  
    Maintains aspect ratio and converts to RGB.  
      
    Args:  
        image: PIL Image object  
        target\_size: Maximum dimension (width or height)  
          
    Returns:  
        PIL.Image.Image: Processed image  
    """  
    \# Convert to RGB (standardize channels)  
    if image.mode \!= 'RGB':  
        image \= image.convert('RGB')  
          
    \# Resize if larger than target  
    if max(image.size) \> target\_size:  
        image.thumbnail((target\_size, target\_size), Image.Resampling.LANCZOS)  
          
    return image

def get\_image\_metadata(source: Union\[str, Path\]) \-\> Dict\[str, Any\]:  
    """  
    Extract basic metadata from an image file without fully loading pixel data if possible.  
      
    Args:  
        source: File path (str/Path)  
          
    Returns:  
        dict: Metadata including width, height, format, mode, and file size.  
    """  
    source\_path \= Path(source)  
    if not source\_path.exists():  
        raise FileNotFoundError(f"Image not found: {source}")  
          
    metadata \= {  
        "filename": source\_path.name,  
        "path": str(source\_path.absolute()),  
        "size\_bytes": source\_path.stat().st\_size,  
        "created": source\_path.stat().st\_ctime,  
        "modified": source\_path.stat().st\_mtime,  
    }  
      
    try:  
        with Image.open(source\_path) as img:  
            metadata.update({  
                "width": img.width,  
                "height": img.height,  
                "format": img.format,  
                "mode": img.mode,  
                "is\_animated": getattr(img, "is\_animated", False),  
                "n\_frames": getattr(img, "n\_frames", 1\)  
            })  
    except Exception as e:  
        logger.warning(f"Failed to extract image attributes for {source}: {e}")  
        \# Return basic file stats even if image open fails  
          
    return metadata

def extract\_video\_frame(video\_path: Union\[str, Path\]) \-\> Image.Image:  
    """  
    Extract the middle frame from a video file using ffmpeg.  
      
    Args:  
        video\_path: Path to the video file  
          
    Returns:  
        PIL.Image.Image: Extracted frame  
          
    Raises:  
        ValueError: If extraction fails  
    """  
    import subprocess  
    import shutil  
      
    path \= str(video\_path)  
    if not os.path.exists(path):  
        raise FileNotFoundError(f"Video not found: {path}")  
          
    if not shutil.which("ffmpeg"):  
        raise RuntimeError("ffmpeg is not installed or found in PATH")  
          
    try:  
        \# Get duration using ffprobe  
        \# We could use the metadata\_extractor logic, but let's keep it simple here with subprocess  
        \# Or just extract a frame at t=00:00:01 usually safer than 50% for short videos?  
        \# Let's try to get a frame at 1s or 10% mark.  
          
        \# Simple approach: Extract 1 frame at 00:00:01 or start  
        \# pipe:1 outputs to stdout  
        \# \-v error: suppress logs  
        \# \-ss 00:00:01: seek to 1s  
        \# \-vframes 1: get 1 frame  
        \# \-f image2pipe: format  
        \# \-c:v png: codec  
          
        cmd \= \[  
            "ffmpeg",  
            "-ss", "00:00:01",  
            "-i", path,  
            "-vframes", "1",  
            "-f", "image2pipe",  
            "-v", "error",  
            "-c:v", "png",  
            "-"  
        \]  
          
        \# Run command  
        process \= subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
          
        if process.returncode \!= 0:  
            \# Try at 0s if 1s failed (video too short?)  
            cmd\[2\] \= "00:00:00"  
            process \= subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
            if process.returncode \!= 0:  
                raise ValueError(f"ffmpeg error: {process.stderr.decode()}")  
                  
        \# Load image from bytes  
        img \= Image.open(BytesIO(process.stdout))  
        img.load()  
        return img  
          
    except Exception as e:  
        raise ValueError(f"Failed to extract frame from video {path}: {e}")

"""  
Video Content Analysis & Search

Comprehensive video analysis system that provides:  
\- Keyframe extraction for visual analysis  
\- Scene detection and segmentation  
\- Video OCR for text overlay detection  
\- Frame-based semantic search  
\- Video thumbnail generation  
\- Motion analysis and object tracking

This extends the existing photo search capabilities to video content,  
enabling users to search within video files using natural language.  
"""

import os  
import sys  
import json  
import sqlite3  
import hashlib  
import tempfile  
from pathlib import Path  
from typing import List, Dict, Any, Optional, Tuple, Union  
from datetime import datetime, timezone  
import logging

try:  
    import cv2  
    import numpy as np  
    CV2\_AVAILABLE \= True  
except ImportError:  
    CV2\_AVAILABLE \= False  
    print("OpenCV not available \- video analysis will be limited")

try:  
    import ffmpeg  
    FFMPEG\_AVAILABLE \= True  
except ImportError:  
    FFMPEG\_AVAILABLE \= False  
    print("ffmpeg-python not available \- video processing will be limited")

try:  
    from PIL import Image  
    PIL\_AVAILABLE \= True  
except ImportError:  
    PIL\_AVAILABLE \= False  
    print("PIL not available \- image processing will be limited")

\# Import existing modules for integration  
try:  
    from src.ocr\_search import OCRSearch  
    from src.metadata\_extractor import extract\_all\_metadata  
    OCR\_AVAILABLE \= True  
except ImportError:  
    OCR\_AVAILABLE \= False  
    print("OCR modules not available \- text detection will be disabled")

class VideoAnalyzer:  
    """  
    Main video analysis class that orchestrates all video processing tasks.  
    """  
      
    def \_\_init\_\_(self, db\_path: str \= "video\_analysis.db", cache\_dir: str \= "cache/video"):  
        """  
        Initialize the video analyzer.  
          
        Args:  
            db\_path: Path to SQLite database for storing analysis results  
            cache\_dir: Directory for caching extracted frames and thumbnails  
        """  
        self.db\_path \= db\_path  
        self.cache\_dir \= Path(cache\_dir)  
        self.cache\_dir.mkdir(parents=True, exist\_ok=True)  
          
        \# Initialize database  
        self.\_init\_database()  
          
        \# Initialize OCR if available  
        self.ocr\_search \= OCRSearch() if OCR\_AVAILABLE else None  
          
        \# Configure logging  
        self.logger \= logging.getLogger(\_\_name\_\_)  
          
        \# Video processing settings  
        self.keyframe\_interval \= 30  \# Extract keyframe every 30 seconds  
        self.scene\_threshold \= 0.3   \# Scene change detection threshold  
        self.max\_frames\_per\_video \= 100  \# Limit frames to prevent excessive processing  
          
    def \_init\_database(self):  
        """Initialize the video analysis database schema."""  
        conn \= sqlite3.connect(self.db\_path)  
        conn.row\_factory \= sqlite3.Row  
          
        \# Video metadata table  
        conn.execute("""  
            CREATE TABLE IF NOT EXISTS video\_metadata (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                video\_path TEXT UNIQUE NOT NULL,  
                duration\_seconds REAL,  
                fps REAL,  
                width INTEGER,  
                height INTEGER,  
                codec TEXT,  
                bitrate INTEGER,  
                file\_size INTEGER,  
                created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,  
                updated\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP  
            )  
        """)  
          
        \# Keyframes table  
        conn.execute("""  
            CREATE TABLE IF NOT EXISTS video\_keyframes (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                video\_path TEXT NOT NULL,  
                frame\_number INTEGER,  
                timestamp\_seconds REAL,  
                frame\_path TEXT,  
                scene\_id INTEGER,  
                is\_scene\_boundary BOOLEAN DEFAULT FALSE,  
                visual\_hash TEXT,  
                created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,  
                FOREIGN KEY (video\_path) REFERENCES video\_metadata (video\_path)  
            )  
        """)  
          
        \# Video OCR results table  
        conn.execute("""  
            CREATE TABLE IF NOT EXISTS video\_ocr (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                video\_path TEXT NOT NULL,  
                frame\_number INTEGER,  
                timestamp\_seconds REAL,  
                detected\_text TEXT,  
                confidence REAL,  
                bounding\_box TEXT,  \-- JSON: \[x, y, width, height\]  
                language TEXT,  
                created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,  
                FOREIGN KEY (video\_path) REFERENCES video\_metadata (video\_path)  
            )  
        """)  
          
        \# Scene detection table  
        conn.execute("""  
            CREATE TABLE IF NOT EXISTS video\_scenes (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                video\_path TEXT NOT NULL,  
                scene\_number INTEGER,  
                start\_timestamp REAL,  
                end\_timestamp REAL,  
                duration\_seconds REAL,  
                keyframe\_count INTEGER,  
                scene\_description TEXT,  
                created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,  
                FOREIGN KEY (video\_path) REFERENCES video\_metadata (video\_path)  
            )  
        """)  
          
        \# Create indexes for performance  
        conn.execute("CREATE INDEX IF NOT EXISTS idx\_video\_keyframes\_path ON video\_keyframes (video\_path)")  
        conn.execute("CREATE INDEX IF NOT EXISTS idx\_video\_keyframes\_timestamp ON video\_keyframes (timestamp\_seconds)")  
        conn.execute("CREATE INDEX IF NOT EXISTS idx\_video\_ocr\_path ON video\_ocr (video\_path)")  
        conn.execute("CREATE INDEX IF NOT EXISTS idx\_video\_ocr\_text ON video\_ocr (detected\_text)")  
        conn.execute("CREATE INDEX IF NOT EXISTS idx\_video\_scenes\_path ON video\_scenes (video\_path)")  
          
        conn.commit()  
        conn.close()  
          
    def analyze\_video(self, video\_path: str, force\_reprocess: bool \= False) \-\> Dict\[str, Any\]:  
        """  
        Perform comprehensive analysis of a video file.  
          
        Args:  
            video\_path: Path to the video file  
            force\_reprocess: If True, reprocess even if already analyzed  
              
        Returns:  
            Dictionary containing analysis results  
        """  
        video\_path \= str(Path(video\_path).resolve())  
          
        if not os.path.exists(video\_path):  
            raise FileNotFoundError(f"Video file not found: {video\_path}")  
              
        \# Check if already processed  
        if not force\_reprocess and self.\_is\_video\_processed(video\_path):  
            self.logger.info(f"Video already processed: {video\_path}")  
            return self.get\_video\_analysis(video\_path)  
              
        self.logger.info(f"Starting video analysis: {video\_path}")  
          
        try:  
            \# Step 1: Extract basic video metadata  
            metadata \= self.\_extract\_video\_metadata(video\_path)  
              
            \# Step 2: Extract keyframes  
            keyframes \= self.\_extract\_keyframes(video\_path, metadata)  
              
            \# Step 3: Detect scenes  
            scenes \= self.\_detect\_scenes(video\_path, keyframes)  
              
            \# Step 4: Perform OCR on keyframes  
            ocr\_results \= self.\_perform\_video\_ocr(video\_path, keyframes)  
              
            \# Step 5: Store results in database  
            self.\_store\_analysis\_results(video\_path, metadata, keyframes, scenes, ocr\_results)  
              
            analysis\_result \= {  
                "video\_path": video\_path,  
                "metadata": metadata,  
                "keyframes\_count": len(keyframes),  
                "scenes\_count": len(scenes),  
                "ocr\_detections": len(ocr\_results),  
                "status": "completed",  
                "processed\_at": datetime.now(timezone.utc).isoformat()  
            }  
              
            self.logger.info(f"Video analysis completed: {video\_path}")  
            return analysis\_result  
              
        except Exception as e:  
            self.logger.error(f"Video analysis failed for {video\_path}: {str(e)}")  
            return {  
                "video\_path": video\_path,  
                "status": "failed",  
                "error": str(e),  
                "processed\_at": datetime.now(timezone.utc).isoformat()  
            }  
      
    def \_extract\_video\_metadata(self, video\_path: str) \-\> Dict\[str, Any\]:  
        """Extract basic video metadata using ffprobe."""  
        if not FFMPEG\_AVAILABLE:  
            raise RuntimeError("ffmpeg-python not available for video metadata extraction")  
              
        try:  
            probe \= ffmpeg.probe(video\_path)  
            video\_stream \= next((stream for stream in probe\['streams'\] if stream\['codec\_type'\] \== 'video'), None)  
              
            if not video\_stream:  
                raise ValueError("No video stream found in file")  
                  
            metadata \= {  
                "duration": float(probe\['format'\].get('duration', 0)),  
                "fps": eval(video\_stream.get('r\_frame\_rate', '0/1')),  \# Convert fraction to float  
                "width": int(video\_stream.get('width', 0)),  
                "height": int(video\_stream.get('height', 0)),  
                "codec": video\_stream.get('codec\_name', 'unknown'),  
                "bitrate": int(probe\['format'\].get('bit\_rate', 0)),  
                "file\_size": int(probe\['format'\].get('size', 0))  
            }  
              
            return metadata  
              
        except Exception as e:  
            self.logger.error(f"Failed to extract video metadata: {str(e)}")  
            raise  
      
    def \_extract\_keyframes(self, video\_path: str, metadata: Dict\[str, Any\]) \-\> List\[Dict\[str, Any\]\]:  
        """Extract keyframes from video at regular intervals."""  
        if not CV2\_AVAILABLE:  
            self.logger.warning("OpenCV not available \- using ffmpeg for frame extraction")  
            return self.\_extract\_keyframes\_ffmpeg(video\_path, metadata)  
              
        keyframes \= \[\]  
        cap \= cv2.VideoCapture(video\_path)  
          
        if not cap.isOpened():  
            raise RuntimeError(f"Could not open video file: {video\_path}")  
              
        try:  
            fps \= metadata.get('fps', 30\)  
            duration \= metadata.get('duration', 0\)  
            frame\_interval \= int(fps \* self.keyframe\_interval)  \# Frames between keyframes  
              
            frame\_number \= 0  
            extracted\_count \= 0  
              
            while cap.isOpened() and extracted\_count \< self.max\_frames\_per\_video:  
                ret, frame \= cap.read()  
                if not ret:  
                    break  
                      
                \# Extract keyframe at intervals  
                if frame\_number % frame\_interval \== 0:  
                    timestamp \= frame\_number / fps  
                      
                    \# Save frame to cache  
                    frame\_filename \= f"{Path(video\_path).stem}\_frame\_{frame\_number:06d}.jpg"  
                    frame\_path \= self.cache\_dir / frame\_filename  
                      
                    cv2.imwrite(str(frame\_path), frame)  
                      
                    \# Calculate visual hash for similarity detection  
                    visual\_hash \= self.\_calculate\_frame\_hash(frame)  
                      
                    keyframes.append({  
                        "frame\_number": frame\_number,  
                        "timestamp": timestamp,  
                        "frame\_path": str(frame\_path),  
                        "visual\_hash": visual\_hash  
                    })  
                      
                    extracted\_count \+= 1  
                      
                frame\_number \+= 1  
                  
        finally:  
            cap.release()  
              
        self.logger.info(f"Extracted {len(keyframes)} keyframes from {video\_path}")  
        return keyframes  
      
    def \_extract\_keyframes\_ffmpeg(self, video\_path: str, metadata: Dict\[str, Any\]) \-\> List\[Dict\[str, Any\]\]:  
        """Fallback keyframe extraction using ffmpeg."""  
        keyframes: List\[Dict\[str, Any\]\] \= \[\]  
        duration \= metadata.get('duration', 0\)  
          
        if duration \== 0:  
            return keyframes  
              
        \# Calculate timestamps for keyframe extraction  
        timestamps: List\[float\] \= \[\]  
        current\_time \= 0  
        while current\_time \< duration and len(timestamps) \< self.max\_frames\_per\_video:  
            timestamps.append(current\_time)  
            current\_time \+= self.keyframe\_interval  
              
        \# Extract frames at specified timestamps  
        for i, timestamp in enumerate(timestamps):  
            try:  
                frame\_filename \= f"{Path(video\_path).stem}\_frame\_{i:06d}.jpg"  
                frame\_path \= self.cache\_dir / frame\_filename  
                  
                \# Use ffmpeg to extract frame at specific timestamp  
                (  
                    ffmpeg  
                    .input(video\_path, ss=timestamp)  
                    .output(str(frame\_path), vframes=1, format='image2', vcodec='mjpeg')  
                    .overwrite\_output()  
                    .run(quiet=True)  
                )  
                  
                if frame\_path.exists():  
                    keyframes.append({  
                        "frame\_number": i \* int(metadata.get('fps', 30\) \* self.keyframe\_interval),  
                        "timestamp": timestamp,  
                        "frame\_path": str(frame\_path),  
                        "visual\_hash": self.\_calculate\_image\_hash(str(frame\_path))  
                    })  
                      
            except Exception as e:  
                self.logger.warning(f"Failed to extract frame at {timestamp}s: {str(e)}")  
                continue  
                  
        return keyframes  
      
    def \_calculate\_frame\_hash(self, frame: np.ndarray) \-\> str:  
        """Calculate perceptual hash of a video frame."""  
        if not CV2\_AVAILABLE:  
            return ""  
              
        \# Resize to small size for hashing  
        small\_frame \= cv2.resize(frame, (8, 8))  
        gray\_frame \= cv2.cvtColor(small\_frame, cv2.COLOR\_BGR2GRAY)  
          
        \# Calculate average pixel value  
        avg \= gray\_frame.mean()  
          
        \# Create binary hash  
        hash\_bits \= \[\]  
        for pixel in gray\_frame.flatten():  
            hash\_bits.append('1' if pixel \> avg else '0')  
              
        return ''.join(hash\_bits)  
      
    def \_calculate\_image\_hash(self, image\_path: str) \-\> str:  
        """Calculate perceptual hash of an image file."""  
        if not PIL\_AVAILABLE:  
            return ""  
              
        try:  
            with Image.open(image\_path) as img:  
                \# Convert to grayscale and resize  
                img \= img.convert('L').resize((8, 8))  
                pixels \= list(img.getdata())  
                  
                \# Calculate average  
                avg \= sum(pixels) / len(pixels)  
                  
                \# Create binary hash  
                hash\_bits \= \['1' if pixel \> avg else '0' for pixel in pixels\]  
                return ''.join(hash\_bits)  
                  
        except Exception:  
            return ""  
      
    def \_detect\_scenes(self, video\_path: str, keyframes: List\[Dict\[str, Any\]\]) \-\> List\[Dict\[str, Any\]\]:  
        """Detect scene boundaries using frame similarity analysis."""  
        if len(keyframes) \< 2:  
            return \[\]  
              
        scenes \= \[\]  
        current\_scene\_start \= 0  
        scene\_number \= 0  
          
        \# Compare consecutive frames for scene changes  
        for i in range(1, len(keyframes)):  
            prev\_hash \= keyframes\[i-1\]\['visual\_hash'\]  
            curr\_hash \= keyframes\[i\]\['visual\_hash'\]  
              
            \# Calculate Hamming distance between hashes  
            if prev\_hash and curr\_hash:  
                similarity \= self.\_calculate\_hash\_similarity(prev\_hash, curr\_hash)  
                  
                \# If similarity is below threshold, it's a scene boundary  
                if similarity \< self.scene\_threshold:  
                    \# End current scene  
                    scene\_end\_time \= keyframes\[i-1\]\['timestamp'\]  
                    scene\_start\_time \= keyframes\[current\_scene\_start\]\['timestamp'\]  
                      
                    scenes.append({  
                        "scene\_number": scene\_number,  
                        "start\_timestamp": scene\_start\_time,  
                        "end\_timestamp": scene\_end\_time,  
                        "duration": scene\_end\_time \- scene\_start\_time,  
                        "keyframe\_count": i \- current\_scene\_start  
                    })  
                      
                    \# Mark frame as scene boundary  
                    keyframes\[i\]\['is\_scene\_boundary'\] \= True  
                    keyframes\[i\]\['scene\_id'\] \= scene\_number \+ 1  
                      
                    \# Start new scene  
                    current\_scene\_start \= i  
                    scene\_number \+= 1  
                else:  
                    keyframes\[i\]\['scene\_id'\] \= scene\_number  
            else:  
                keyframes\[i\]\['scene\_id'\] \= scene\_number  
          
        \# Add final scene  
        if current\_scene\_start \< len(keyframes) \- 1:  
            scene\_start\_time \= keyframes\[current\_scene\_start\]\['timestamp'\]  
            scene\_end\_time \= keyframes\[-1\]\['timestamp'\]  
              
            scenes.append({  
                "scene\_number": scene\_number,  
                "start\_timestamp": scene\_start\_time,  
                "end\_timestamp": scene\_end\_time,  
                "duration": scene\_end\_time \- scene\_start\_time,  
                "keyframe\_count": len(keyframes) \- current\_scene\_start  
            })  
          
        self.logger.info(f"Detected {len(scenes)} scenes in {video\_path}")  
        return scenes  
      
    def \_calculate\_hash\_similarity(self, hash1: str, hash2: str) \-\> float:  
        """Calculate similarity between two perceptual hashes."""  
        if len(hash1) \!= len(hash2):  
            return 0.0  
              
        \# Calculate Hamming distance  
        different\_bits \= sum(c1 \!= c2 for c1, c2 in zip(hash1, hash2))  
          
        \# Convert to similarity (0 \= completely different, 1 \= identical)  
        similarity \= 1.0 \- (different\_bits / len(hash1))  
        return similarity  
      
    def \_perform\_video\_ocr(self, video\_path: str, keyframes: List\[Dict\[str, Any\]\]) \-\> List\[Dict\[str, Any\]\]:  
        """Perform OCR on extracted keyframes to detect text overlays."""  
        if not self.ocr\_search:  
            self.logger.warning("OCR not available \- skipping text detection")  
            return \[\]  
              
        ocr\_results \= \[\]  
          
        for keyframe in keyframes:  
            frame\_path \= keyframe\['frame\_path'\]  
              
            if not os.path.exists(frame\_path):  
                continue  
                  
            try:  
                \# Use existing OCR system to extract text  
                text\_results \= self.ocr\_search.extract\_text\_from\_images(\[frame\_path\])  
                  
                if frame\_path in text\_results and text\_results\[frame\_path\]\['text'\]:  
                    ocr\_results.append({  
                        "frame\_number": keyframe\['frame\_number'\],  
                        "timestamp": keyframe\['timestamp'\],  
                        "detected\_text": text\_results\[frame\_path\]\['text'\],  
                        "confidence": text\_results\[frame\_path\].get('confidence', 0.0),  
                        "language": text\_results\[frame\_path\].get('language', 'unknown')  
                    })  
                      
            except Exception as e:  
                self.logger.warning(f"OCR failed for frame {frame\_path}: {str(e)}")  
                continue  
                  
        self.logger.info(f"Performed OCR on {len(keyframes)} frames, found text in {len(ocr\_results)} frames")  
        return ocr\_results  
      
    def \_store\_analysis\_results(self, video\_path: str, metadata: Dict\[str, Any\],   
                              keyframes: List\[Dict\[str, Any\]\], scenes: List\[Dict\[str, Any\]\],   
                              ocr\_results: List\[Dict\[str, Any\]\]):  
        """Store all analysis results in the database."""  
        conn \= sqlite3.connect(self.db\_path)  
          
        try:  
            \# Store video metadata  
            conn.execute("""  
                INSERT OR REPLACE INTO video\_metadata   
                (video\_path, duration\_seconds, fps, width, height, codec, bitrate, file\_size, updated\_at)  
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT\_TIMESTAMP)  
            """, (  
                video\_path,  
                metadata.get('duration', 0),  
                metadata.get('fps', 0),  
                metadata.get('width', 0),  
                metadata.get('height', 0),  
                metadata.get('codec', ''),  
                metadata.get('bitrate', 0),  
                metadata.get('file\_size', 0\)  
            ))  
              
            \# Clear existing keyframes for this video  
            conn.execute("DELETE FROM video\_keyframes WHERE video\_path \= ?", (video\_path,))  
              
            \# Store keyframes  
            for keyframe in keyframes:  
                conn.execute("""  
                    INSERT INTO video\_keyframes   
                    (video\_path, frame\_number, timestamp\_seconds, frame\_path, scene\_id, is\_scene\_boundary, visual\_hash)  
                    VALUES (?, ?, ?, ?, ?, ?, ?)  
                """, (  
                    video\_path,  
                    keyframe\['frame\_number'\],  
                    keyframe\['timestamp'\],  
                    keyframe\['frame\_path'\],  
                    keyframe.get('scene\_id', 0),  
                    keyframe.get('is\_scene\_boundary', False),  
                    keyframe.get('visual\_hash', '')  
                ))  
              
            \# Clear existing scenes for this video  
            conn.execute("DELETE FROM video\_scenes WHERE video\_path \= ?", (video\_path,))  
              
            \# Store scenes  
            for scene in scenes:  
                conn.execute("""  
                    INSERT INTO video\_scenes   
                    (video\_path, scene\_number, start\_timestamp, end\_timestamp, duration\_seconds, keyframe\_count)  
                    VALUES (?, ?, ?, ?, ?, ?)  
                """, (  
                    video\_path,  
                    scene\['scene\_number'\],  
                    scene\['start\_timestamp'\],  
                    scene\['end\_timestamp'\],  
                    scene\['duration'\],  
                    scene\['keyframe\_count'\]  
                ))  
              
            \# Clear existing OCR results for this video  
            conn.execute("DELETE FROM video\_ocr WHERE video\_path \= ?", (video\_path,))  
              
            \# Store OCR results  
            for ocr\_result in ocr\_results:  
                conn.execute("""  
                    INSERT INTO video\_ocr   
                    (video\_path, frame\_number, timestamp\_seconds, detected\_text, confidence, language)  
                    VALUES (?, ?, ?, ?, ?, ?)  
                """, (  
                    video\_path,  
                    ocr\_result\['frame\_number'\],  
                    ocr\_result\['timestamp'\],  
                    ocr\_result\['detected\_text'\],  
                    ocr\_result\['confidence'\],  
                    ocr\_result\['language'\]  
                ))  
              
            conn.commit()  
              
        finally:  
            conn.close()  
      
    def \_is\_video\_processed(self, video\_path: str) \-\> bool:  
        """Check if video has already been processed."""  
        conn \= sqlite3.connect(self.db\_path)  
        conn.row\_factory \= sqlite3.Row  
          
        try:  
            cursor \= conn.execute(  
                "SELECT COUNT(\*) as count FROM video\_metadata WHERE video\_path \= ?",  
                (video\_path,)  
            )  
            result \= cursor.fetchone()  
            return result\['count'\] \> 0  
              
        finally:  
            conn.close()  
      
    def get\_video\_analysis(self, video\_path: str) \-\> Dict\[str, Any\]:  
        """Retrieve complete analysis results for a video."""  
        conn \= sqlite3.connect(self.db\_path)  
        conn.row\_factory \= sqlite3.Row  
          
        try:  
            \# Get metadata  
            cursor \= conn.execute(  
                "SELECT \* FROM video\_metadata WHERE video\_path \= ?",  
                (video\_path,)  
            )  
            metadata \= cursor.fetchone()  
              
            if not metadata:  
                return {"error": "Video not found in database"}  
              
            \# Get keyframes  
            cursor \= conn.execute(  
                "SELECT \* FROM video\_keyframes WHERE video\_path \= ? ORDER BY timestamp\_seconds",  
                (video\_path,)  
            )  
            keyframes \= \[dict(row) for row in cursor.fetchall()\]  
              
            \# Get scenes  
            cursor \= conn.execute(  
                "SELECT \* FROM video\_scenes WHERE video\_path \= ? ORDER BY scene\_number",  
                (video\_path,)  
            )  
            scenes \= \[dict(row) for row in cursor.fetchall()\]  
              
            \# Get OCR results  
            cursor \= conn.execute(  
                "SELECT \* FROM video\_ocr WHERE video\_path \= ? ORDER BY timestamp\_seconds",  
                (video\_path,)  
            )  
            ocr\_results \= \[dict(row) for row in cursor.fetchall()\]  
              
            return {  
                "video\_path": video\_path,  
                "metadata": dict(metadata),  
                "keyframes": keyframes,  
                "scenes": scenes,  
                "ocr\_results": ocr\_results,  
                "summary": {  
                    "keyframes\_count": len(keyframes),  
                    "scenes\_count": len(scenes),  
                    "text\_detections": len(ocr\_results),  
                    "duration": metadata\['duration\_seconds'\]  
                }  
            }  
              
        finally:  
            conn.close()  
      
    def search\_video\_content(self, query: str, limit: int \= 50\) \-\> List\[Dict\[str, Any\]\]:  
        """  
        Search video content using text query.  
          
        Searches through:  
        \- OCR detected text in video frames  
        \- Video file names and paths  
        \- Scene descriptions (if available)  
        """  
        conn \= sqlite3.connect(self.db\_path)  
        conn.row\_factory \= sqlite3.Row  
          
        try:  
            \# Search OCR text  
            cursor \= conn.execute("""  
                SELECT DISTINCT   
                    vo.video\_path,  
                    vo.timestamp\_seconds,  
                    vo.detected\_text,  
                    vo.confidence,  
                    vm.duration\_seconds,  
                    vm.width,  
                    vm.height  
                FROM video\_ocr vo  
                JOIN video\_metadata vm ON vo.video\_path \= vm.video\_path  
                WHERE vo.detected\_text LIKE ?  
                ORDER BY vo.confidence DESC, vo.timestamp\_seconds ASC  
                LIMIT ?  
            """, (f"%{query}%", limit))  
              
            results \= \[\]  
            for row in cursor.fetchall():  
                results.append({  
                    "video\_path": row\['video\_path'\],  
                    "timestamp": row\['timestamp\_seconds'\],  
                    "matched\_text": row\['detected\_text'\],  
                    "confidence": row\['confidence'\],  
                    "duration": row\['duration\_seconds'\],  
                    "resolution": f"{row\['width'\]}x{row\['height'\]}",  
                    "match\_type": "ocr\_text"  
                })  
              
            return results  
              
        finally:  
            conn.close()  
      
    def get\_video\_statistics(self) \-\> Dict\[str, Any\]:  
        """Get statistics about processed videos."""  
        conn \= sqlite3.connect(self.db\_path)  
        conn.row\_factory \= sqlite3.Row  
          
        try:  
            \# Total videos processed  
            cursor \= conn.execute("SELECT COUNT(\*) as count FROM video\_metadata")  
            total\_videos \= cursor.fetchone()\['count'\]  
              
            \# Total keyframes extracted  
            cursor \= conn.execute("SELECT COUNT(\*) as count FROM video\_keyframes")  
            total\_keyframes \= cursor.fetchone()\['count'\]  
              
            \# Total scenes detected  
            cursor \= conn.execute("SELECT COUNT(\*) as count FROM video\_scenes")  
            total\_scenes \= cursor.fetchone()\['count'\]  
              
            \# Total OCR detections  
            cursor \= conn.execute("SELECT COUNT(\*) as count FROM video\_ocr")  
            total\_ocr \= cursor.fetchone()\['count'\]  
              
            \# Total duration processed  
            cursor \= conn.execute("SELECT SUM(duration\_seconds) as total FROM video\_metadata")  
            total\_duration \= cursor.fetchone()\['total'\] or 0  
              
            return {  
                "total\_videos": total\_videos,  
                "total\_keyframes": total\_keyframes,  
                "total\_scenes": total\_scenes,  
                "total\_ocr\_detections": total\_ocr,  
                "total\_duration\_hours": round(total\_duration / 3600, 2),  
                "average\_keyframes\_per\_video": round(total\_keyframes / max(total\_videos, 1), 1),  
                "average\_scenes\_per\_video": round(total\_scenes / max(total\_videos, 1), 1\)  
            }  
              
        finally:  
            conn.close()

def main():  
    """Command-line interface for video analysis."""  
    import argparse  
      
    parser \= argparse.ArgumentParser(description="Video Content Analysis Tool")  
    parser.add\_argument("video\_path", help="Path to video file to analyze")  
    parser.add\_argument("--force", action="store\_true", help="Force reprocessing even if already analyzed")  
    parser.add\_argument("--search", help="Search for text in processed videos")  
    parser.add\_argument("--stats", action="store\_true", help="Show video analysis statistics")  
    parser.add\_argument("--db", default="video\_analysis.db", help="Database path")  
    parser.add\_argument("--cache", default="cache/video", help="Cache directory")  
      
    args \= parser.parse\_args()  
      
    \# Configure logging  
    logging.basicConfig(level=logging.INFO, format='%(asctime)s \- %(levelname)s \- %(message)s')  
      
    analyzer \= VideoAnalyzer(db\_path=args.db, cache\_dir=args.cache)  
      
    if args.stats:  
        stats \= analyzer.get\_video\_statistics()  
        print("\\n=== Video Analysis Statistics \===")  
        for key, value in stats.items():  
            print(f"{key.replace('\_', ' ').title()}: {value}")  
        return  
      
    if args.search:  
        results \= analyzer.search\_video\_content(args.search)  
        print(f"\\n=== Search Results for '{args.search}' \===")  
        for result in results:  
            print(f"Video: {result\['video\_path'\]}")  
            print(f"  Time: {result\['timestamp'\]:.1f}s")  
            print(f"  Text: {result\['matched\_text'\]}")  
            print(f"  Confidence: {result\['confidence'\]:.2f}")  
            print()  
        return  
      
    if not os.path.exists(args.video\_path):  
        print(f"Error: Video file not found: {args.video\_path}")  
        return  
      
    \# Analyze video  
    print(f"Analyzing video: {args.video\_path}")  
    result \= analyzer.analyze\_video(args.video\_path, force\_reprocess=args.force)  
      
    if result\['status'\] \== 'completed':  
        print(f"✅ Analysis completed successfully\!")  
        print(f"   Keyframes extracted: {result\['keyframes\_count'\]}")  
        print(f"   Scenes detected: {result\['scenes\_count'\]}")  
        print(f"   Text detections: {result\['ocr\_detections'\]}")  
    else:  
        print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()

"""  
Enhanced Duplicate Detection System

This module provides comprehensive duplicate detection with:  
1\. Multiple hash algorithms for accuracy (MD5, PHash, DHash, AHash, Wavelet)  
2\. Perceptual similarity detection using image analysis  
3\. Smart duplicate grouping with confidence scoring  
4\. Visual comparison and resolution suggestions  
5\. Batch processing with progress tracking  
6\. Integration with metadata and face recognition

Features:  
\- Exact duplicate detection (MD5)  
\- Perceptual duplicate detection (PHash, DHash, AHash)  
\- Wavelet hash for robust similarity  
\- Color histogram analysis  
\- Quality assessment for resolution suggestions  
\- Smart grouping based on similarity thresholds  
\- Batch processing with GPU acceleration  
\- Integration with photo metadata

Usage:  
    duplicate\_detector \= EnhancedDuplicateDetector()

    \# Scan directory for duplicates  
    results \= duplicate\_detector.scan\_directory('/photos', show\_progress=True)

    \# Get duplicate groups for resolution  
    duplicate\_groups \= duplicate\_detector.get\_duplicate\_groups()

    \# Smart resolution suggestions  
    suggestions \= duplicate\_detector.get\_resolution\_suggestions(group\_id)  
"""

import os  
import json  
import sqlite3  
import hashlib  
import numpy as np  
import threading  
import logging  
from typing import List, Dict, Optional, Any, Tuple, Callable  
from pathlib import Path  
from datetime import datetime  
from collections import defaultdict, Counter  
from dataclasses import dataclass, asdict  
from concurrent.futures import ThreadPoolExecutor, as\_completed  
import time  
import cv2  
from PIL import Image, ImageChops, ImageFilter  
import imagehash  
from sklearn.cluster import DBSCAN  
from sklearn.metrics.pairwise import cosine\_similarity

\# Configure logging  
logger \= logging.getLogger(\_\_name\_\_)

\# Image processing libraries  
try:  
    import pywt  \# PyWavelets for wavelet hashing  
    WAVELET\_AVAILABLE \= True  
except ImportError:  
    WAVELET\_AVAILABLE \= False  
    logger.warning("PyWavelets not available. Install with: pip install PyWavelets")

@dataclass  
class DuplicateGroup:  
    """Duplicate group with metadata and suggestions"""  
    id: str  
    group\_type: str  \# exact, near, similar, visual  
    similarity\_threshold: float  
    photos: List\[Dict\[str, Any\]\]  
    total\_size\_mb: float  
    primary\_photo\_id: Optional\[str\]  
    resolution\_strategy: Optional\[str\]  
    auto\_resolvable: bool  
    created\_at: str  
    updated\_at: str

@dataclass  
class PhotoInfo:  
    """Photo information for duplicate analysis"""  
    path: str  
    file\_hash: str  
    size\_bytes: int  
    dimensions: Tuple\[int, int\]  
    phash: Optional\[imagehash.ImageHash\] \= None  
    dhash: Optional\[imagehash.ImageHash\] \= None  
    ahash: Optional\[imagehash.ImageHash\] \= None  
    whash: Optional\[imagehash.ImageHash\] \= None  
    color\_histogram: Optional\[List\[float\]\] \= None  
    quality\_score: float \= 0.0  
    created\_at: Optional\[str\] \= None

class EnhancedDuplicateDetector:  
    """Enhanced duplicate detection with multiple algorithms"""

    def \_\_init\_\_(self,  
                 db\_path: str \= "duplicates.db",  
                 progress\_callback: Optional\[Callable\[\[str\], Any\]\] \= None,  
                 enable\_gpu: bool \= True):  
        """  
        Initialize enhanced duplicate detector.

        Args:  
            db\_path: Path to SQLite database  
            progress\_callback: Callback for progress updates  
            enable\_gpu: Enable GPU acceleration if available  
        """  
        self.db\_path \= db\_path  
        self.progress\_callback: Callable\[\[str\], Any\] \= progress\_callback or (lambda \_msg: None)  
        self.enable\_gpu \= enable\_gpu

        \# Threading and caching  
        self.cache\_lock \= threading.Lock()  
        self.photo\_cache: Dict\[str, PhotoInfo\] \= {}  
        self.hash\_cache: Dict\[str, Dict\[str, Any\]\] \= {}

        \# Configuration  
        self.hash\_thresholds \= {  
            'exact': 0,      \# MD5 identical  
            'near': 2,       \# PHash distance \<= 2  
            'similar': 5,    \# PHash distance \<= 5  
            'visual': 10     \# PHash distance \<= 10  
        }

        \# Performance tracking  
        self.stats: Dict\[str, int | float\] \= {  
            'photos\_processed': 0,  
            'duplicates\_found': 0,  
            'groups\_created': 0,  
            'processing\_time\_ms': 0  
        }

        \# Initialize database  
        self.\_initialize\_database()

    def \_initialize\_database(self):  
        """Initialize database with enhanced schema"""  
        \# Import schema extensions  
        schema\_ext \= Path(\_\_file\_\_).parent.parent / 'server' / 'schema\_extensions.py'  
        if schema\_ext.exists():  
            import sys  
            sys.path.append(str(schema\_ext.parent))  
            from schema\_extensions import SchemaExtensions

            schema \= SchemaExtensions(Path(self.db\_path))  
            schema.extend\_schema()

        self.conn \= sqlite3.connect(self.db\_path)  
        self.conn.row\_factory \= sqlite3.Row

        \# Performance optimizations  
        self.conn.execute("PRAGMA journal\_mode=WAL")  
        self.conn.execute("PRAGMA synchronous=NORMAL")  
        self.conn.execute("PRAGMA cache\_size=20000")

    def \_calculate\_file\_hash(self, file\_path: str) \-\> str:  
        """Calculate MD5 hash for exact duplicate detection"""  
        hash\_md5 \= hashlib.md5()  
        with open(file\_path, "rb") as f:  
            for chunk in iter(lambda: f.read(4096), b""):  
                hash\_md5.update(chunk)  
        return hash\_md5.hexdigest()

    def \_calculate\_perceptual\_hashes(self, image\_path: str) \-\> Dict\[str, imagehash.ImageHash\]:  
        """Calculate multiple perceptual hashes"""  
        try:  
            with Image.open(image\_path) as img:  
                \# Convert to RGB for consistent hashing  
                if img.mode \!= 'RGB':  
                    img \= img.convert('RGB')

                \# Resize for consistent hashing  
                img \= img.resize((256, 256), Image.Resampling.LANCZOS)

                hashes \= {  
                    'phash': imagehash.phash(img, hash\_size=8),  
                    'dhash': imagehash.dhash(img, hash\_size=8),  
                    'ahash': imagehash.average\_hash(img, hash\_size=8)  
                }

                \# Wavelet hash if available  
                if WAVELET\_AVAILABLE:  
                    try:  
                        hashes\['whash'\] \= imagehash.whash(img, hash\_size=8, mode='haar')  \# type: ignore  
                    except:  
                        pass  \# Skip wavelet if it fails

                return hashes

        except Exception as e:  
            logger.error(f"Error calculating hashes for {image\_path}: {e}")  
            return {}

    def \_calculate\_color\_histogram(self, image\_path: str) \-\> List\[float\]:  
        """Calculate normalized color histogram"""  
        try:  
            img \= cv2.imread(image\_path)  
            if img is None:  
                return \[\]

            \# Calculate histogram for each channel  
            hist\_b \= cv2.calcHist(\[img\], \[0\], None, \[64\], \[0, 256\])  
            hist\_g \= cv2.calcHist(\[img\], \[1\], None, \[64\], \[0, 256\])  
            hist\_r \= cv2.calcHist(\[img\], \[2\], None, \[64\], \[0, 256\])

            \# Normalize and concatenate  
            hist\_b \= hist\_b.flatten() / hist\_b.sum()  
            hist\_g \= hist\_g.flatten() / hist\_g.sum()  
            hist\_r \= hist\_r.flatten() / hist\_r.sum()

            return np.concatenate(\[hist\_b, hist\_g, hist\_r\]).tolist()

        except Exception as e:  
            logger.error(f"Error calculating color histogram for {image\_path}: {e}")  
            return \[\]

    def \_calculate\_quality\_score(self, image\_path: str) \-\> float:  
        """Calculate image quality score based on multiple factors"""  
        try:  
            with Image.open(image\_path) as img:  
                quality\_score \= 0.0

                \# Resolution score (0-30 points)  
                width, height \= img.size  
                megapixels \= (width \* height) / 1000000  
                resolution\_score \= min(30, megapixels \* 2\)  \# 2 points per MP, max 30  
                quality\_score \+= resolution\_score

                \# Sharpness score using Laplacian variance (0-40 points)  
                img\_gray \= img.convert('L')  
                laplacian\_var \= cv2.Laplacian(np.array(img\_gray), cv2.CV\_64F).var()  
                sharpness\_score \= min(40, laplacian\_var / 100\)  
                quality\_score \+= sharpness\_score

                \# File size score (0-20 points) \- larger files often indicate less compression  
                file\_size\_mb \= os.path.getsize(image\_path) / (1024 \* 1024\)  
                size\_score \= min(20, file\_size\_mb \* 2\)  \# 2 points per MB, max 20  
                quality\_score \+= size\_score

                \# Aspect ratio bonus (0-10 points) \- standard ratios get bonus  
                aspect\_ratio \= width / height  
                if 0.9 \<= aspect\_ratio \<= 1.1:  \# Nearly square  
                    quality\_score \+= 5  
                elif 1.3 \<= aspect\_ratio \<= 1.4:  \# 4:3  
                    quality\_score \+= 10  
                elif 1.7 \<= aspect\_ratio \<= 1.8:  \# 16:9  
                    quality\_score \+= 8

                return min(100.0, quality\_score)

        except Exception as e:  
            logger.error(f"Error calculating quality score for {image\_path}: {e}")  
            return 0.0

    def \_process\_image(self, image\_path: str) \-\> Optional\[PhotoInfo\]:  
        """Process a single image for duplicate analysis"""  
        try:  
            \# Basic file info  
            stat \= os.stat(image\_path)  
            file\_hash \= self.\_calculate\_file\_hash(image\_path)

            \# Image dimensions  
            with Image.open(image\_path) as img:  
                dimensions \= img.size

            \# Calculate hashes  
            hashes \= self.\_calculate\_perceptual\_hashes(image\_path)  
            color\_histogram \= self.\_calculate\_color\_histogram(image\_path)  
            quality\_score \= self.\_calculate\_quality\_score(image\_path)

            \# Extract creation time from EXIF if available  
            created\_at \= None  
            try:  
                with Image.open(image\_path) as img:  
                    exif \= img.\_getexif()  
                    if exif:  
                        from PIL.ExifTags import TAGS  
                        for tag\_id, value in exif.items():  
                            tag \= TAGS.get(tag\_id, tag\_id)  
                            if tag \== 'DateTimeOriginal':  
                                created\_at \= value  
                                break  
            except:  
                pass

            return PhotoInfo(  
                path=image\_path,  
                file\_hash=file\_hash,  
                size\_bytes=stat.st\_size,  
                dimensions=dimensions,  
                phash=hashes.get('phash'),  
                dhash=hashes.get('dhash'),  
                ahash=hashes.get('ahash'),  
                whash=hashes.get('whash'),  
                color\_histogram=color\_histogram,  
                quality\_score=quality\_score,  
                created\_at=created\_at  
            )

        except Exception as e:  
            logger.error(f"Error processing image {image\_path}: {e}")  
            return None

    def scan\_directory(self,  
                      directory\_path: str,  
                      max\_workers: int \= 4,  
                      show\_progress: bool \= False,  
                      similarity\_threshold: float \= 5.0) \-\> Dict\[str, Any\]:  
        """  
        Scan directory for duplicate images.

        Args:  
            directory\_path: Directory to scan  
            max\_workers: Number of parallel processing threads  
            show\_progress: Show progress updates  
            similarity\_threshold: Threshold for perceptual similarity

        Returns:  
            Dictionary with scan results  
        """  
        start\_time \= time.time()  
        results: Dict\[str, Any\] \= {  
            'total\_images': 0,  
            'processed\_images': 0,  
            'exact\_duplicates': 0,  
            'near\_duplicates': 0,  
            'similar\_images': 0,  
            'groups\_created': 0,  
            'total\_size\_saved\_mb': 0.0,  
            'errors': \[\]  
        }

        \# Get all image files  
        image\_extensions \= {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}  
        image\_files: List\[Path\] \= \[\]  
        for ext in image\_extensions:  
            image\_files.extend(Path(directory\_path).glob(f'\*{ext}'))  
            image\_files.extend(Path(directory\_path).glob(f'\*{ext.upper()}'))

        results\['total\_images'\] \= len(image\_files)

        \_progress\_cb: Callable\[\[str\], None\] \= self.progress\_callback

        if show\_progress:  
            \_progress\_cb(f"Processing {len(image\_files)} images for duplicates...")

        \# Process images in parallel  
        photo\_infos: List\[PhotoInfo\] \= \[\]  
        with ThreadPoolExecutor(max\_workers=max\_workers) as executor:  
            future\_to\_file \= {  
                executor.submit(self.\_process\_image, str(img\_path)): img\_path  
                for img\_path in image\_files  
            }

            for i, future in enumerate(as\_completed(future\_to\_file)):  
                img\_path \= future\_to\_file\[future\]  
                try:  
                    photo\_info \= future.result()  
                    if photo\_info:  
                        photo\_infos.append(photo\_info)  
                        results\['processed\_images'\] \+= 1

                    if show\_progress and (i \+ 1\) % 10 \== 0:  
                        progress \= ((i \+ 1\) / len(image\_files)) \* 100  
                        \_progress\_cb(f"Progress: {progress:.1f}%")

                except Exception as e:  
                    error\_msg \= f"Error processing {img\_path}: {e}"  
                    logger.error(error\_msg)  
                    results\['errors'\].append(error\_msg)

        \# Find duplicates  
        if photo\_infos:  
            if show\_progress:  
                \_progress\_cb("Finding duplicate groups...")  
            duplicate\_results \= self.\_find\_duplicates(photo\_infos, similarity\_threshold)  
            results.update(duplicate\_results)

        \# Store results in database  
        if results\['groups\_created'\] \> 0:  
            if show\_progress:  
                \_progress\_cb("Storing duplicate information...")  
            self.\_store\_duplicate\_results(photo\_infos, results)

        \# Calculate processing time  
        processing\_time \= (time.time() \- start\_time) \* 1000  
        self.stats\['processing\_time\_ms'\] \+= processing\_time  
        results\['processing\_time\_ms'\] \= processing\_time

        if show\_progress:  
            \_progress\_cb(f"Completed: {results\['groups\_created'\]} duplicate groups found")

        return results

    def \_find\_duplicates(self, photo\_infos: List\[PhotoInfo\], similarity\_threshold: float) \-\> Dict\[str, Any\]:  
        """Find duplicate groups using multiple algorithms"""  
        results \= {  
            'exact\_duplicates': 0,  
            'near\_duplicates': 0,  
            'similar\_images': 0,  
            'groups\_created': 0,  
            'total\_size\_saved\_mb': 0.0  
        }

        \# 1\. Find exact duplicates (same file hash)  
        exact\_groups \= self.\_find\_exact\_duplicates(photo\_infos)  
        exact\_count \= sum(len(group) \- 1 for group in exact\_groups.values()) if exact\_groups else 0  
        results\['exact\_duplicates'\] \= exact\_count

        \# 2\. Find perceptual duplicates using PHash  
        near\_groups \= self.\_find\_perceptual\_duplicates(photo\_infos, 'phash', 2\)  
        near\_count \= sum(len(group) \- 1 for group in near\_groups.values()) if near\_groups else 0  
        results\['near\_duplicates'\] \= near\_count

        \# 3\. Find similar images  
        similar\_groups \= self.\_find\_perceptual\_duplicates(photo\_infos, 'phash', int(similarity\_threshold))  
        similar\_count \= sum(len(group) \- 1 for group in similar\_groups.values()) if similar\_groups else 0  
        results\['similar\_images'\] \= similar\_count

        \# Calculate total groups and potential space savings  
        all\_groups \= list(exact\_groups.values()) \+ list(near\_groups.values()) \+ list(similar\_groups.values())  
        results\['groups\_created'\] \= len(all\_groups)

        for group in all\_groups:  
            if len(group) \> 1:  
                \# Calculate potential space savings (keeping highest quality)  
                best\_photo \= max(group, key=lambda x: x.quality\_score)  
                space\_saved \= sum(info.size\_bytes for info in group if info \!= best\_photo)  
                results\['total\_size\_saved\_mb'\] \+= float(space\_saved) / (1024 \* 1024\)

        return results

    def \_find\_exact\_duplicates(self, photo\_infos: List\[PhotoInfo\]) \-\> Dict\[str, List\[PhotoInfo\]\]:  
        """Find exact duplicates using file hash"""  
        hash\_groups \= defaultdict(list)  
        for info in photo\_infos:  
            hash\_groups\[info.file\_hash\].append(info)

        \# Return only groups with duplicates  
        return {h: group for h, group in hash\_groups.items() if len(group) \> 1}

    def \_find\_perceptual\_duplicates(self,  
                                  photo\_infos: List\[PhotoInfo\],  
                                  hash\_type: str,  
                                  threshold: int) \-\> Dict\[str, List\[PhotoInfo\]\]:  
        """Find perceptual duplicates using image hashing"""  
        \# Filter photos that have the required hash  
        valid\_photos \= \[info for info in photo\_infos if getattr(info, hash\_type, None) is not None\]

        if len(valid\_photos) \< 2:  
            return {}

        \# Extract hash values  
        hash\_values: List\[Tuple\[str, PhotoInfo\]\] \= \[\]  
        for info in valid\_photos:  
            hash\_val \= getattr(info, hash\_type, None)  
            if hash\_val:  
                hash\_values.append((str(hash\_val), info))

        \# Group by hash similarity  
        groups: Dict\[str, List\[PhotoInfo\]\] \= defaultdict(list)  
        used\_indices: set\[int\] \= set()

        for i, (hash1, info1) in enumerate(hash\_values):  
            if i in used\_indices:  
                continue

            current\_group: List\[PhotoInfo\] \= \[info1\]  
            used\_indices.add(i)

            \# Compare with other photos  
            for j, (hash2, info2) in enumerate(hash\_values\[i+1:\], i+1):  
                if j in used\_indices:  
                    continue

                \# Calculate hash distance  
                hash1\_obj \= imagehash.hex\_to\_hash(hash1)  
                hash2\_obj \= imagehash.hex\_to\_hash(hash2)  
                distance \= int(hash1\_obj \- hash2\_obj)

                if distance \<= threshold:  
                    current\_group.append(info2)  
                    used\_indices.add(j)

            \# Only keep groups with duplicates  
            if len(current\_group) \> 1:  
                groups\[f"{hash\_type}\_{threshold}\_{len(groups)}"\] \= current\_group

        return groups

    def \_store\_duplicate\_results(self, photo\_infos: List\[PhotoInfo\], results: Dict\[str, Any\]):  
        """Store duplicate detection results in database"""  
        try:  
            \# Store photo hashes  
            for info in photo\_infos:  
                self.conn.execute("""  
                    INSERT OR REPLACE INTO perceptual\_hashes  
                    (photo\_path, phash, dhash, ahash, whash, dominant\_colors, created\_at)  
                    VALUES (?, ?, ?, ?, ?, ?, ?)  
                """, (  
                    info.path,  
                    int(str(info.phash)) if info.phash else None,  
                    int(str(info.dhash)) if info.dhash else None,  
                    int(str(info.ahash)) if info.ahash else None,  
                    int(str(info.whash)) if info.whash else None,  
                    json.dumps(info.color\_histogram\[:10\]) if info.color\_histogram else None,  \# First 10 bins as dominant colors  
                    info.created\_at or datetime.now().isoformat()  
                ))

            self.conn.commit()

        except Exception as e:  
            logger.error(f"Error storing duplicate results: {e}")  
            self.conn.rollback()

    def get\_duplicate\_groups(self,  
                           group\_type: Optional\[str\] \= None,  
                           min\_similarity: Optional\[float\] \= None) \-\> List\[DuplicateGroup\]:  
        """Get duplicate groups with optional filtering"""  
        try:  
            query \= """  
                SELECT  
                    dge.id,  
                    dge.group\_type,  
                    dge.similarity\_threshold,  
                    dge.primary\_photo\_id,  
                    dge.resolution\_strategy,  
                    dge.auto\_resolvable,  
                    dge.created\_at,  
                    dge.updated\_at,  
                    COUNT(dr.photo\_path) as photo\_count,  
                    SUM(fs.size\_bytes) as total\_size  
                FROM duplicate\_groups\_enhanced dge  
                JOIN duplicate\_relationships dr ON dge.id \= dr.group\_id  
                LEFT JOIN perceptual\_hashes fs ON dr.photo\_path \= fs.photo\_path  
            """

            params: List\[Any\] \= \[\]  
            where\_clauses: List\[str\] \= \[\]

            if group\_type:  
                where\_clauses.append("dge.group\_type \= ?")  
                params.append(group\_type)

            if min\_similarity:  
                where\_clauses.append("dge.similarity\_threshold \>= ?")  
                params.append(min\_similarity)

            if where\_clauses:  
                query \+= " WHERE " \+ " AND ".join(where\_clauses)

            query \+= """  
                GROUP BY dge.id  
                ORDER BY dge.similarity\_threshold, photo\_count DESC  
            """

            cursor \= self.conn.execute(query, params)  
            groups: List\[DuplicateGroup\] \= \[\]

            for row in cursor.fetchall():  
                \# Get photos for this group  
                photos\_cursor \= self.conn.execute("""  
                    SELECT dr.photo\_path, dr.similarity\_score, dr.is\_primary, dr.resolution\_action  
                    FROM duplicate\_relationships dr  
                    WHERE dr.group\_id \= ?  
                    ORDER BY dr.is\_primary DESC, dr.similarity\_score DESC  
                """, (row\['id'\],))

                photos \= \[\]  
                for photo\_row in photos\_cursor.fetchall():  
                    photos.append({  
                        'path': photo\_row\['photo\_path'\],  
                        'similarity\_score': photo\_row\['similarity\_score'\],  
                        'is\_primary': bool(photo\_row\['is\_primary'\]),  
                        'resolution\_action': photo\_row\['resolution\_action'\]  
                    })

                group \= DuplicateGroup(  
                    id=row\['id'\],  
                    group\_type=row\['group\_type'\],  
                    similarity\_threshold=row\['similarity\_threshold'\],  
                    photos=photos,  
                    total\_size\_mb=float((row\['total\_size'\] or 0\) / (1024 \* 1024)),  
                    primary\_photo\_id=row\['primary\_photo\_id'\],  
                    resolution\_strategy=row\['resolution\_strategy'\],  
                    auto\_resolvable=bool(row\['auto\_resolvable'\]),  
                    created\_at=row\['created\_at'\],  
                    updated\_at=row\['updated\_at'\]  
                )  
                groups.append(group)

            return groups

        except Exception as e:  
            logger.error(f"Error getting duplicate groups: {e}")  
            return \[\]

    def get\_resolution\_suggestions(self, group\_id: str) \-\> Dict\[str, Any\]:  
        """Get smart resolution suggestions for a duplicate group"""  
        try:  
            \# Get group and photos  
            cursor \= self.conn.execute("""  
                SELECT dge.\*, COUNT(dr.photo\_path) as photo\_count  
                FROM duplicate\_groups\_enhanced dge  
                JOIN duplicate\_relationships dr ON dge.id \= dr.group\_id  
                WHERE dge.id \= ?  
                GROUP BY dge.id  
            """, (group\_id,))

            group\_info \= cursor.fetchone()  
            if not group\_info:  
                return {}

            \# Get photo details with quality info  
            cursor \= self.conn.execute("""  
                SELECT  
                    dr.photo\_path,  
                    dr.similarity\_score,  
                    ph.phash,  
                    ph.dhash,  
                    ph.ahash,  
                    fs.size\_bytes  
                FROM duplicate\_relationships dr  
                LEFT JOIN perceptual\_hashes ph ON dr.photo\_path \= ph.photo\_path  
                LEFT JOIN perceptual\_hashes fs ON dr.photo\_path \= fs.photo\_path  
                WHERE dr.group\_id \= ?  
                ORDER BY dr.similarity\_score DESC  
            """, (group\_id,))

            photos \= \[\]  
            for row in cursor.fetchall():  
                \# Calculate quality score  
                quality\_score \= self.\_calculate\_quality\_score(row\['photo\_path'\])

                photos.append({  
                    'path': row\['photo\_path'\],  
                    'similarity\_score': row\['similarity\_score'\],  
                    'quality\_score': quality\_score,  
                    'size\_bytes': row\['size\_bytes'\],  
                    'phash': row\['phash'\],  
                    'dhash': row\['dhash'\],  
                    'ahash': row\['ahash'\]  
                })

            \# Generate suggestions  
            suggestions \= {  
                'group\_info': dict(group\_info),  
                'photos': photos,  
                'suggestions': self.\_generate\_resolution\_suggestions(photos, group\_info\['group\_type'\])  
            }

            return suggestions

        except Exception as e:  
            logger.error(f"Error getting resolution suggestions for {group\_id}: {e}")  
            return {}

    def \_generate\_resolution\_suggestions(self, photos: List\[Dict\[str, Any\]\], group\_type: str) \-\> List\[Dict\[str, Any\]\]:  
        """Generate intelligent resolution suggestions"""  
        suggestions: List\[Dict\[str, Any\]\] \= \[\]

        if not photos:  
            return suggestions

        \# Sort by quality score  
        sorted\_photos \= sorted(photos, key=lambda x: x\['quality\_score'\], reverse=True)

        \# Suggestion 1: Keep best quality, delete others  
        best\_photo \= sorted\_photos\[0\]  
        total\_space\_saved \= sum(p\['size\_bytes'\] for p in sorted\_photos\[1:\])

        suggestions.append({  
            'type': 'keep\_best\_quality',  
            'description': f'Keep highest quality photo ({best\_photo\["path"\].split("/")\[-1\]})',  
            'action': 'keep',  
            'target\_photo': best\_photo\['path'\],  
            'space\_saved\_mb': total\_space\_saved / (1024 \* 1024),  
            'confidence': 0.9,  
            'reasoning': f'Highest quality score: {best\_photo\["quality\_score"\]:.1f}/100'  
        })

        \# Suggestion 2: Keep largest file (may be less compressed)  
        largest\_photo \= max(photos, key=lambda x: x\['size\_bytes'\])  
        total\_space\_saved \= sum(p\['size\_bytes'\] for p in photos if p \!= largest\_photo)

        suggestions.append({  
            'type': 'keep\_largest',  
            'description': f'Keep largest file ({largest\_photo\["path"\].split("/")\[-1\]})',  
            'action': 'keep',  
            'target\_photo': largest\_photo\['path'\],  
            'space\_saved\_mb': total\_space\_saved / (1024 \* 1024),  
            'confidence': 0.7,  
            'reasoning': f'Largest file: {largest\_photo\["size\_bytes"\] / (1024\*1024):.1f}MB'  
        })

        \# Suggestion 3: Keep all if very similar and small size  
        if group\_type \== 'similar' and len(photos) \<= 3:  
            total\_size\_mb \= sum(p\['size\_bytes'\] for p in photos) / (1024 \* 1024\)  
            if total\_size\_mb \< 50:  \# Less than 50MB total  
                suggestions.append({  
                    'type': 'keep\_all',  
                    'description': 'Keep all photos (small total size)',  
                    'action': 'keep\_all',  
                    'space\_saved\_mb': 0,  
                    'confidence': 0.6,  
                    'reasoning': f'Total size only {total\_size\_mb:.1f}MB, photos may have sentimental value'  
                })

        \# Suggestion 4: Keep based on filename patterns (keep original, keep edited)  
        originals \= \[\]  
        edited \= \[\]  
        for photo in photos:  
            filename \= photo\['path'\].lower()  
            if any(keyword in filename for keyword in \['copy', 'edited', 'modified', 'final'\]):  
                edited.append(photo)  
            else:  
                originals.append(photo)

        if originals and edited:  
            suggestions.append({  
                'type': 'keep\_originals',  
                'description': f'Keep {len(originals)} original(s), move {len(edited)} copy(s) to archive',  
                'action': 'move\_edited',  
                'originals': \[p\['path'\] for p in originals\],  
                'edited': \[p\['path'\] for p in edited\],  
                'confidence': 0.8,  
                'reasoning': 'Identified original and edited versions based on filenames'  
            })

        return suggestions

    def close(self):  
        """Close database connection"""  
        if self.conn:  
            self.conn.close()  
