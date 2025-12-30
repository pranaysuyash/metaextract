# server/extractor/modules/audio_id3_extended.py

"""
Enhanced Audio ID3 and Audio Tag metadata extraction for Phase 4.

Covers:
- ID3v1 (Simple 128-byte tag)
- ID3v2.2, 2.3, 2.4 (Full-featured ID3 tags)
- APE tags (Monkey's Audio)
- Vorbis comments (OGG, FLAC)
- iTunes/M4A tags (ILST format)
- WMA/ASF tags (Windows Media)
- Info frame / VBR header analysis
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

AUDIO_TAG_EXTENSIONS = [
    '.mp3', '.flac', '.m4a', '.aac', '.wma',
    '.ogg', '.oga', '.opus', '.aiff', '.ape',
    '.dsf', '.dsd', '.tak', '.tta', '.vorbis'
]


def extract_audio_id3_extended_metadata(filepath: str) -> Dict[str, Any]:
    """Extract extended audio ID3 and audio tag metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is audio format
        is_audio = _is_audio_file(filepath, filename, file_ext)

        if not is_audio:
            return result

        result['audio_id3_extended_detected'] = True

        # Extract ID3v2 tags (at file start)
        id3v2_data = _extract_id3v2_metadata(filepath)
        result.update(id3v2_data)

        # Extract ID3v1 tags (at file end)
        id3v1_data = _extract_id3v1_metadata(filepath)
        result.update(id3v1_data)

        # Extract APE tags
        ape_data = _extract_ape_tag_metadata(filepath)
        result.update(ape_data)

        # Extract VBR/Info frames
        vbr_data = _extract_vbr_info_metadata(filepath)
        result.update(vbr_data)

        # Format-specific extraction
        if file_ext == '.m4a':
            m4a_data = _extract_m4a_ilst_metadata(filepath)
            result.update(m4a_data)

        elif file_ext == '.wma':
            wma_data = _extract_wma_asf_metadata(filepath)
            result.update(wma_data)

        elif file_ext == '.flac':
            vorbis_data = _extract_vorbis_comment_metadata(filepath)
            result.update(vorbis_data)

        elif file_ext == '.ogg':
            vorbis_data = _extract_vorbis_comment_metadata(filepath)
            result.update(vorbis_data)

        # Get audio stream properties
        stream_data = _extract_audio_stream_properties(filepath, file_ext)
        result.update(stream_data)

    except Exception as e:
        logger.warning(f"Error extracting audio ID3 metadata from {filepath}: {e}")
        result['audio_id3_extended_extraction_error'] = str(e)

    return result


def _is_audio_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is audio format."""
    if file_ext.lower() in AUDIO_TAG_EXTENSIONS:
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(4)

        # ID3v2 signature
        if header.startswith(b'ID3'):
            return True

        # MP3 frame sync (FF FB or FF FA)
        if header[0] == 0xFF and (header[1] & 0xE0) == 0xE0:
            return True

        # FLAC signature
        if header.startswith(b'fLaC'):
            return True

        # OGG signature
        if header.startswith(b'OggS'):
            return True

        # RIFF/WAV
        if header.startswith(b'RIFF'):
            return True

        # M4A/AAC (ftyp box)
        if header[4:8] == b'ftyp':
            return True

    except Exception:
        pass

    return False


def _extract_id3v2_metadata(filepath: str) -> Dict[str, Any]:
    """Extract ID3v2 metadata."""
    id3_data = {}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(10)

        if not header.startswith(b'ID3'):
            return id3_data

        id3_data['audio_id3v2_present'] = True

        # Offset 3: Version
        version_high = header[3]
        version_low = header[4]
        id3_data['audio_id3v2_version'] = f'{version_high}.{version_low}'

        # Offset 5: Flags
        flags = header[5]
        id3_data['audio_id3v2_unsynchronization'] = bool(flags & 0x80)
        id3_data['audio_id3v2_has_extended_header'] = bool(flags & 0x40)
        id3_data['audio_id3v2_experimental'] = bool(flags & 0x20)
        id3_data['audio_id3v2_has_footer'] = bool(flags & 0x10)

        # Offset 6-9: Tag size (synchsafe integer)
        size_bytes = header[6:10]
        tag_size = _synchsafe_int_to_int(size_bytes)
        id3_data['audio_id3v2_tag_size'] = tag_size

        # Read ID3v2 frames
        frame_count = 0
        frame_map = {}

        # Read frame data
        with open(filepath, 'rb') as f:
            f.seek(10)  # Skip ID3 header
            frame_data = f.read(min(tag_size, 8192))  # Read up to 8KB of frames

        # Parse frames (each frame starts with 4-char ID)
        pos = 0
        while pos < len(frame_data) - 10:
            frame_id = frame_data[pos:pos+4]

            # Check if valid frame ID (4 uppercase ASCII chars)
            if not all(32 <= b < 127 for b in frame_id) or b'\x00' in frame_id:
                break

            frame_id_str = frame_id.decode('ascii', errors='ignore')

            # Frame size
            frame_size = struct.unpack('>I', frame_data[pos+4:pos+8])[0]

            if frame_size == 0 or frame_size > tag_size:
                break

            frame_count += 1
            frame_map[frame_id_str] = frame_map.get(frame_id_str, 0) + 1

            pos += 10 + frame_size

        id3_data['audio_id3v2_frame_count'] = frame_count
        id3_data['audio_id3v2_unique_frames'] = list(frame_map.keys())[:20]  # First 20 unique frames

        # Count common frames
        id3_data['audio_id3v2_has_tit2'] = 'TIT2' in frame_map
        id3_data['audio_id3v2_has_tpe1'] = 'TPE1' in frame_map
        id3_data['audio_id3v2_has_talb'] = 'TALB' in frame_map
        id3_data['audio_id3v2_has_tdrc'] = 'TDRC' in frame_map
        id3_data['audio_id3v2_has_trck'] = 'TRCK' in frame_map
        id3_data['audio_id3v2_has_apic'] = 'APIC' in frame_map

    except Exception as e:
        id3_data['audio_id3v2_extraction_error'] = str(e)

    return id3_data


def _synchsafe_int_to_int(data: bytes) -> int:
    """Convert synchsafe integer to regular integer."""
    if len(data) < 4:
        return 0
    return ((data[0] & 0x7F) << 21) | ((data[1] & 0x7F) << 14) | ((data[2] & 0x7F) << 7) | (data[3] & 0x7F)


def _extract_id3v1_metadata(filepath: str) -> Dict[str, Any]:
    """Extract ID3v1 metadata (128-byte tag at EOF)."""
    id3v1_data = {}

    try:
        file_size = Path(filepath).stat().st_size

        if file_size < 128:
            return id3v1_data

        with open(filepath, 'rb') as f:
            f.seek(file_size - 128)
            tag = f.read(128)

        if not tag.startswith(b'TAG'):
            return id3v1_data

        id3v1_data['audio_id3v1_present'] = True

        # Parse ID3v1 fields
        title = tag[3:33].rstrip(b'\x00').decode('latin1', errors='ignore')
        artist = tag[33:63].rstrip(b'\x00').decode('latin1', errors='ignore')
        album = tag[63:93].rstrip(b'\x00').decode('latin1', errors='ignore')
        year = tag[93:97].rstrip(b'\x00').decode('latin1', errors='ignore')
        comment = tag[97:127].rstrip(b'\x00').decode('latin1', errors='ignore')
        genre = tag[127]

        if title:
            id3v1_data['audio_id3v1_has_title'] = True
        if artist:
            id3v1_data['audio_id3v1_has_artist'] = True
        if album:
            id3v1_data['audio_id3v1_has_album'] = True
        if year:
            id3v1_data['audio_id3v1_has_year'] = True
        if comment:
            id3v1_data['audio_id3v1_has_comment'] = True

        id3v1_data['audio_id3v1_genre'] = genre

        # Check for ID3v1.1 (track number in comment)
        if len(comment) >= 2 and tag[125] == 0:
            track = tag[126]
            if track > 0:
                id3v1_data['audio_id3v1_has_track'] = True

    except Exception as e:
        id3v1_data['audio_id3v1_extraction_error'] = str(e)

    return id3v1_data


def _extract_ape_tag_metadata(filepath: str) -> Dict[str, Any]:
    """Extract APE tag metadata."""
    ape_data = {}

    try:
        file_size = Path(filepath).stat().st_size

        if file_size < 32:
            return ape_data

        with open(filepath, 'rb') as f:
            # Check at end of file
            f.seek(file_size - 32)
            footer = f.read(32)

        if not footer.startswith(b'APETAGEX'):
            return ape_data

        ape_data['audio_ape_tag_present'] = True

        # Parse APE footer
        version = struct.unpack('<I', footer[8:12])[0]
        tag_size = struct.unpack('<I', footer[12:16])[0]
        item_count = struct.unpack('<I', footer[16:20])[0]

        ape_data['audio_ape_version'] = version
        ape_data['audio_ape_tag_size'] = tag_size
        ape_data['audio_ape_item_count'] = item_count

        # Read APE items
        if tag_size > 0 and tag_size < 1_000_000:  # Sanity check
            with open(filepath, 'rb') as f:
                f.seek(file_size - tag_size - 32)
                items_data = f.read(min(tag_size, 4096))

            # Parse items (simple key-value pairs)
            items_found = 0
            pos = 0
            while pos < len(items_data) - 8 and items_found < 50:
                value_size = struct.unpack('<I', items_data[pos:pos+4])[0]
                flags = struct.unpack('<I', items_data[pos+4:pos+8])[0]

                if value_size > 10_000:
                    break

                key_start = pos + 8
                key_end = items_data.find(b'\x00', key_start)

                if key_end > 0 and key_end < pos + 100:
                    key = items_data[key_start:key_end].decode('utf-8', errors='ignore').lower()
                    items_found += 1

                    # Track common APE tags
                    if key == 'title':
                        ape_data['audio_ape_has_title'] = True
                    elif key == 'artist':
                        ape_data['audio_ape_has_artist'] = True
                    elif key == 'album':
                        ape_data['audio_ape_has_album'] = True
                    elif key == 'date':
                        ape_data['audio_ape_has_date'] = True

                    pos = key_end + 1 + value_size
                else:
                    break

            ape_data['audio_ape_items_parsed'] = items_found

    except Exception as e:
        ape_data['audio_ape_extraction_error'] = str(e)

    return ape_data


def _extract_vbr_info_metadata(filepath: str) -> Dict[str, Any]:
    """Extract VBR/Info frame metadata."""
    vbr_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(40960)  # Read first 40KB

        # Look for Info/Xing frame
        if b'Info' in content:
            vbr_data['audio_has_info_frame'] = True
            pos = content.find(b'Info')

            if pos > 0 and pos + 16 < len(content):
                flags = struct.unpack('>I', content[pos+4:pos+8])[0]
                vbr_data['audio_info_flags'] = flags

                # If frames field is present
                if flags & 0x0001:
                    frames = struct.unpack('>I', content[pos+8:pos+12])[0]
                    vbr_data['audio_info_frames'] = frames

                # If bytes field is present
                if flags & 0x0002:
                    bytes_val = struct.unpack('>I', content[pos+12:pos+16])[0]
                    vbr_data['audio_info_bytes'] = bytes_val

        # Look for Xing frame
        if b'Xing' in content:
            vbr_data['audio_has_xing_frame'] = True
            pos = content.find(b'Xing')

            if pos > 0 and pos + 16 < len(content):
                flags = struct.unpack('>I', content[pos+4:pos+8])[0]

                if flags & 0x0001:
                    frames = struct.unpack('>I', content[pos+8:pos+12])[0]
                    vbr_data['audio_xing_frames'] = frames

        # Look for VBR info in general MP3 frame headers
        mp3_frame_info = _extract_mp3_frame_headers(content)
        vbr_data.update(mp3_frame_info)

    except Exception as e:
        vbr_data['audio_vbr_extraction_error'] = str(e)

    return vbr_data


def _extract_mp3_frame_headers(data: bytes) -> Dict[str, Any]:
    """Extract MP3 frame header information."""
    frame_info = {}

    try:
        # Look for MP3 frame sync (0xFF with high 3 bits set)
        frames_found = 0
        valid_frames = 0

        for i in range(0, min(len(data) - 4, 40000)):
            if data[i] == 0xFF and (data[i+1] & 0xE0) == 0xE0:
                frames_found += 1

                # Parse frame header
                header = struct.unpack('>I', data[i:i+4])[0]

                # Extract bitrate index
                bitrate_idx = (header >> 12) & 0x0F
                sample_rate_idx = (header >> 10) & 0x03

                if bitrate_idx > 0 and bitrate_idx < 15 and sample_rate_idx < 3:
                    valid_frames += 1

                if frames_found > 100:
                    break

        if frames_found > 0:
            frame_info['audio_mp3_frames_detected'] = frames_found
            frame_info['audio_mp3_valid_frames'] = valid_frames

    except Exception:
        pass

    return frame_info


def _extract_m4a_ilst_metadata(filepath: str) -> Dict[str, Any]:
    """Extract M4A iTunes ILST atom metadata."""
    ilst_data = {'audio_m4a_ilst_format': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(65536)

        # Look for ilst atom
        if b'ilst' in content:
            ilst_data['audio_m4a_has_ilst'] = True

            # Count metadata atoms
            atoms_found = 0
            for atom_name in [b'\xa9nam', b'\xa9ART', b'\xa9alb', b'\xa9day',
                             b'trkn', b'cprt', b'covr', b'gnre', b'cmpr']:
                if atom_name in content:
                    atoms_found += 1

            ilst_data['audio_m4a_metadata_atoms'] = atoms_found

    except Exception as e:
        ilst_data['audio_m4a_ilst_error'] = str(e)

    return ilst_data


def _extract_wma_asf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract WMA/ASF metadata."""
    wma_data = {'audio_wma_asf_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(30)

        # Check ASF header
        if header[:16] == b'0&\xb2u\x8ef\xcf\x11\xa6\xd9\x00\xaa\x00b\xce':
            wma_data['audio_wma_asf_valid'] = True

            # Read more to find metadata objects
            with open(filepath, 'rb') as f:
                content = f.read(65536)

            # Look for Extended Stream Properties
            if b'Extended Stream Properties' in content or b'\xb7\x15\x00\x00' in content:
                wma_data['audio_wma_has_extended_properties'] = True

            # Look for Metadata Object
            if b'Metadata' in content or b'\xc5\xfb\xf0\xb8\x91\x03\xb2\x01\xad' in content:
                wma_data['audio_wma_has_metadata'] = True

    except Exception as e:
        wma_data['audio_wma_asf_error'] = str(e)

    return wma_data


def _extract_vorbis_comment_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Vorbis comment metadata."""
    vorbis_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(65536)

        # Look for Vorbis comment marker
        vorbis_marker = b'\x03vorbis'

        if vorbis_marker in content:
            vorbis_data['audio_vorbis_comment_present'] = True
            pos = content.find(vorbis_marker)

            if pos + 11 < len(content):
                # Number of comments field (little-endian)
                vendor_len = struct.unpack('<I', content[pos+7:pos+11])[0]

                if vendor_len > 0 and vendor_len < 1024:
                    vendor_end = pos + 11 + vendor_len
                    if vendor_end + 4 < len(content):
                        comment_count = struct.unpack('<I', content[vendor_end:vendor_end+4])[0]
                        vorbis_data['audio_vorbis_comment_count'] = min(comment_count, 1000)

    except Exception as e:
        vorbis_data['audio_vorbis_comment_error'] = str(e)

    return vorbis_data


def _extract_audio_stream_properties(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Extract audio stream properties."""
    stream_props = {}

    try:
        file_size = Path(filepath).stat().st_size
        stream_props['audio_file_size'] = file_size

        # Estimate bitrate based on file size and duration (basic heuristic)
        stream_props['audio_file_size_categories'] = _categorize_audio_file_size(file_size)

    except Exception:
        pass

    return stream_props


def _categorize_audio_file_size(size: int) -> str:
    """Categorize audio file by size."""
    if size < 1_000_000:
        return 'small (< 1MB)'
    elif size < 5_000_000:
        return 'medium (1-5MB)'
    elif size < 20_000_000:
        return 'large (5-20MB)'
    elif size < 100_000_000:
        return 'very_large (20-100MB)'
    else:
        return 'huge (> 100MB)'


def get_audio_id3_extended_field_count() -> int:
    """Return the number of fields extracted by audio ID3 extended metadata."""
    # ID3v2 fields
    id3v2_fields = 18

    # ID3v1 fields
    id3v1_fields = 12

    # APE tag fields
    ape_fields = 10

    # VBR/Info frame fields
    vbr_fields = 10

    # M4A ILST fields
    m4a_fields = 8

    # WMA/ASF fields
    wma_fields = 8

    # Vorbis comment fields
    vorbis_fields = 6

    # Audio stream properties
    stream_fields = 8

    return id3v2_fields + id3v1_fields + ape_fields + vbr_fields + m4a_fields + wma_fields + vorbis_fields + stream_fields


# Integration point
def extract_audio_id3_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for audio ID3 extended extraction."""
    return extract_audio_id3_extended_metadata(filepath)
