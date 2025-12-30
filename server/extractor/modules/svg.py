"""
SVG Metadata Extraction
Parse SVG files for element counts, security checks, and properties
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import xml.etree.ElementTree as ET


def extract_svg_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from SVG files.
    
    Args:
        filepath: Path to SVG file
    
    Returns:
        Dictionary with SVG metadata
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Handle SVG namespace
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Basic attributes
        width = root.get('width')
        height = root.get('height')
        viewbox = root.get('viewBox')
        
        # Dimensions
        dimensions = {}
        if width:
            dimensions['width'] = width
        if height:
            dimensions['height'] = height
        if viewbox:
            dimensions['viewBox'] = viewbox
        
        # Count elements
        element_counts = {}
        total_elements = 0
        
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            element_counts[tag] = element_counts.get(tag, 0) + 1
            total_elements += 1
        
        # Check for scripts and external links
        has_scripts = False
        has_external_links = False
        external_links = []
        
        for elem in root.iter():
            # Check scripts
            if elem.tag.endswith('script') or elem.get('onload'):
                has_scripts = True
            
            # Check xlink:href
            href = elem.get('{http://www.w3.org/1999/xlink}href') or elem.get('href')
            if href and href.startswith('http'):
                has_external_links = True
                external_links.append(href)
            
            # Check images
            if elem.tag.endswith('image') and href:
                if href.startswith('http'):
                    has_external_links = True
                    external_links.append(href)
        
        # SVG version
        version = root.get('version')
        
        # Title and description
        title = None
        desc = None
        
        for child in root:
            if child.tag.endswith('title'):
                title = child.text
            elif child.tag.endswith('desc'):
                desc = child.text
        
        # Namespace declarations
        namespaces = {}
        for attr in root.attrib:
            if attr.startswith('xmlns'):
                ns_name = attr.split(':')[-1]
                namespaces[ns_name] = root.attrib[attr]
        
        result = {
            "dimensions": dimensions,
            "element_counts": element_counts,
            "total_elements": total_elements,
            "version": version,
            "namespaces": namespaces,
            "security": {
                "has_scripts": has_scripts,
                "has_external_links": has_external_links,
                "external_link_count": len(external_links),
                "is_safe": not has_scripts
            },
            "title": title,
            "description": desc,
            "fields_extracted": (
                len(dimensions) +
                len(element_counts) +
                len(namespaces) +
                5 +  # security fields
                2  # title, description
            )
        }
        
        return result
        
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except ET.ParseError:
        return {"error": f"Invalid XML in: {filepath}"}
    except Exception as e:
        return {"error": f"Failed to extract SVG metadata: {str(e)}"}


def get_svg_field_count() -> int:
    """Return approximate number of SVG fields."""
    return 20
