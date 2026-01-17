"""
SVG Parser
==========

Extracts metadata from SVG (Scalable Vector Graphics) files.
SVG is XML-based and supports: Dublin Core, RDF, Custom elements.

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import xml.etree.ElementTree as ET


class SvgParser(FormatParser):
    """SVG-specific metadata parser using XML parsing."""
    
    FORMAT_NAME = "SVG"
    SUPPORTED_EXTENSIONS = ['.svg', '.svgz']
    CAN_USE_EXIFTOOL = True
    
    # SVG namespaces
    SVG_NS = 'http://www.w3.org/2000/svg'
    DC_NS = 'http://purl.org/dc/elements/1.1/'
    RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    EXIF_NS = 'http://ns.adobe.com/exif/1.0/'
    XMP_NS = 'http://ns.adobe.com/xap/1.0/'
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract SVG metadata."""
        result = {}
        
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            result = self._parse_with_xml(filepath)
        
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'SVG'),
                mode=result.get('color_mode', 'RGB'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for SVG."""
        metadata = {}
        
        # Core image properties
        metadata['format'] = 'SVG'
        metadata['width'] = self._parse_dimension(data.get('ImageWidth'))
        metadata['height'] = self._parse_dimension(data.get('ImageHeight'))
        
        # SVG-specific
        if data.get('VectorFormat'):
            metadata['vector_format'] = data.get('VectorFormat')
        if data.get('SVGVersion'):
            metadata['version'] = data.get('SVGVersion')
        
        # Dublin Core metadata
        dc = {}
        for field in ['Title', 'Creator', 'Subject', 'Description', 'Publisher',
                     'Contributor', 'Date', 'Type', 'Format', 'Identifier',
                     'Source', 'Language', 'Rights']:
            if data.get(field):
                dc[field.lower()] = data[field]
        
        if dc:
            metadata['dublin_core'] = dc
        
        # XMP
        if data.get('XMP'):
            metadata['xmp'] = {'present': True}
        
        return metadata
    
    def _parse_with_xml(self, filepath: str) -> Dict[str, Any]:
        """Parse SVG using native XML parsing."""
        metadata = {}
        
        try:
            # Handle compressed SVG
            if filepath.endswith('.svgz'):
                import gzip
                with gzip.open(filepath, 'rt') as f:
                    svg_content = f.read()
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
            
            # Parse XML
            root = ET.fromstring(svg_content)
            
            # Register namespaces
            namespaces = {
                'svg': self.SVG_NS,
                'dc': self.DC_NS,
                'rdf': self.RDF_NS,
                'exif': self.EXIF_NS,
                'xmp': self.XMP_NS
            }
            
            for prefix, uri in namespaces.items():
                ET.register_namespace(prefix, uri)
            
            # Extract SVG attributes
            if 'width' in root.attrib:
                metadata['width'] = root.attrib['width']
            if 'height' in root.attrib:
                metadata['height'] = root.attrib['height']
            if 'viewBox' in root.attrib:
                metadata['view_box'] = root.attrib['viewBox']
            if 'version' in root.attrib:
                metadata['version'] = root.attrib['version']
            
            # Extract Dublin Core metadata
            dc_elements = root.findall('.//dc:*', namespaces)
            if dc_elements:
                dc_data = {}
                for elem in dc_elements:
                    tag = elem.tag.split('}')[-1]  # Remove namespace
                    if elem.text and elem.text.strip():
                        dc_data[tag.lower()] = elem.text.strip()
                if dc_data:
                    metadata['dublin_core'] = dc_data
            
            # Extract RDF statements
            rdf_elements = root.findall('.//rdf:*', namespaces)
            if rdf_elements:
                metadata['rdf'] = {'present': True}
            
            # Extract custom metadata elements
            metadata_elem = root.find('.//svg:metadata', namespaces)
            if metadata_elem is not None:
                metadata['has_metadata_element'] = True
            
            # Extract title and desc
            title = root.find('.//svg:title', namespaces)
            if title is not None and title.text:
                metadata['title'] = title.text.strip()
            
            desc = root.find('.//svg:desc', namespaces)
            if desc is not None and desc.text:
                metadata['description'] = desc.text.strip()
            
            # Extract viewbox dimensions
            if 'view_box' in metadata:
                parts = metadata['view_box'].split()
                if len(parts) >= 4:
                    try:
                        width = float(parts[2]) - float(parts[0])
                        height = float(parts[3]) - float(parts[1])
                        metadata['width'] = round(width, 2)
                        metadata['height'] = round(height, 2)
                    except:
                        pass
            
            # Check for embedded images
            image_elements = root.findall('.//svg:image', namespaces)
            if image_elements:
                metadata['embedded_images'] = len(image_elements)
            
            # Check for gradients/defs
            defs = root.find('.//svg:defs', namespaces)
            if defs is not None:
                metadata['has_defs'] = True
                
        except ET.ParseError as e:
            logger.warning(f"SVG XML parsing failed: {e}")
            metadata['error'] = f'XML parse error: {str(e)[:100]}'
        except Exception as e:
            logger.warning(f"Native SVG parsing failed: {e}")
        
        return metadata
    
    def _parse_dimension(self, value: Any) -> Optional[float]:
        """Parse dimension value to float."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Handle "xxxpx", "xxxpt", etc.
            num_str = ''
            for c in value:
                if c.isdigit() or c == '.' or c == '-':
                    num_str += c
            try:
                return float(num_str)
            except:
                pass
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real SVG metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is an SVG."""
        ext = filepath.lower().split('.')[-1]
        return ext in ['svg', 'svgz']


# Convenience function
def parse_svg(filepath: str) -> Dict[str, Any]:
    """Parse SVG file and return metadata."""
    parser = SvgParser()
    return parser.parse(filepath)
