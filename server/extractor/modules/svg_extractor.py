#!/usr/bin/env python3
"""
SVG (Scalable Vector Graphics) Metadata Extractor
Extracts comprehensive metadata from SVG files including vector properties, animations, and embedded content.
"""

import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


NAMESPACES = {
    'svg': 'http://www.w3.org/2000/svg',
    'xlink': 'http://www.w3.org/1999/xlink',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'cc': 'http://creativecommons.org/ns#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    'adobe': 'http://ns.adobe.com/AdobeSVGViewerExtensions/3.0/',
}


class SVGExtractor:
    """
    Comprehensive SVG metadata extractor.
    Supports SVG 1.0, 1.1, 2.0 and extracts all standard and custom attributes.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.svg_info: Dict[str, Any] = {}
        self.root: Optional[ET.Element] = None
        self.namespaces: Dict[str, str] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse SVG file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            tree = ET.parse(self.filepath)
            self.root = tree.getroot()
            
            self._extract_namespaces()
            self._extract_root_attributes()
            self._extract_dimensions()
            self._extract_viewport()
            self._extract_metadata()
            self._extract_elements()
            self._extract_animations()
            self._extract_defs()
            self._extract_links()
            self._extract_styles()
            self._extract_accessibility()
            self._build_result()
            
            return self.svg_info
            
        except ET.ParseError as e:
            logger.error(f"Error parsing SVG XML: {e}")
            return {"error": f"XML parse error: {str(e)}", "success": False}
        except Exception as e:
            logger.error(f"Error parsing SVG: {e}")
            return {"error": str(e), "success": False}
    
    def _extract_namespaces(self):
        """Extract declared namespaces"""
        if self.root is None:
            return
        
        for prefix, uri in self.root.nsmap.items():
            if prefix is None:
                self.namespaces['default'] = uri
            else:
                self.namespaces[prefix] = uri
    
    def _extract_root_attributes(self):
        """Extract SVG root element attributes"""
        if self.root is None:
            return
        
        tag = self.root.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        
        self.svg_info["element_name"] = tag
        self.svg_info["namespace"] = self.root.tag.split('}')[0] if '}' in self.root.tag else ''
        
        version = self.root.get('version', '')
        self.svg_info["svg_version"] = version
        
        base_profile = self.root.get('baseProfile', '')
        self.svg_info["base_profile"] = base_profile
        
        xml_lang = self.root.get('{http://www.w3.org/XML/1998/namespace}lang', '')
        self.svg_info["xml_language"] = xml_lang
        
        xml_space = self.root.get('{http://www.w3.org/XML/1998/namespace}space', '')
        self.svg_info["xml_space"] = xml_space
        
        data = self.root.get('data', '')
        if data:
            self.svg_info["data_attributes"] = data
        
        style = self.root.get('style', '')
        if style:
            self.svg_info["inline_style"] = style
    
    def _extract_dimensions(self):
        """Extract width, height, and viewBox"""
        if self.root is None:
            return
        
        width = self.root.get('width', '')
        height = self.root.get('height', '')
        
        self.svg_info["width"] = width
        self.svg_info["height"] = height
        
        if width and height:
            try:
                w = float(re.match(r'^-?\d+\.?\d*', width.replace('px', '')).group()) if re.match(r'-?\d+\.?\d*', width.replace('px', '')) else 0
                h = float(re.match(r'^-?\d+\.?\d*', height.replace('px', '')).group()) if re.match(r'-?\d+\.?\d*', height.replace('px', '')) else 0
                if h > 0:
                    self.svg_info["aspect_ratio"] = round(w / h, 4)
                self.svg_info["total_pixels_equiv"] = int(w * h) if w > 0 and h > 0 else None
            except (ValueError, AttributeError):
                pass
        
        viewbox = self.root.get('viewBox', '')
        if viewbox:
            parts = viewbox.split()
            if len(parts) >= 4:
                self.svg_info["viewbox"] = {
                    "min_x": float(parts[0]),
                    "min_y": float(parts[1]),
                    "width": float(parts[2]),
                    "height": float(parts[3])
                }
        
        preserve_aspect_ratio = self.root.get('preserveAspectRatio', '')
        self.svg_info["preserve_aspect_ratio"] = preserve_aspect_ratio
        
        zoom_and_pan = self.root.get('zoomAndPan', '')
        self.svg_info["zoom_and_pan"] = zoom_and_pan
        
        overflow = self.root.get('overflow', '')
        self.svg_info["overflow"] = overflow
    
    def _extract_viewport(self):
        """Extract viewport and document coordinates"""
        if self.root is None:
            return
        
        x = self.root.get('x', '')
        y = self.root.get('y', '')
        
        self.svg_info["x"] = x
        self.svg_info["y"] = y
    
    def _extract_metadata(self):
        """Extract metadata elements"""
        if self.root is None:
            return
        
        metadata = self.root.find('svg:metadata', NAMESPACES)
        if metadata is None:
            metadata = self.root.find('.//{http://www.w3.org/2000/svg}metadata')
        
        if metadata is not None:
            self.svg_info["has_metadata"] = True
            
            rdf = metadata.find('rdf:RDF', NAMESPACES)
            if rdf is not None:
                self.svg_info["has_rdf"] = True
                self._extract_rdf(rdf)
            
            dc_elements = metadata.findall('.//dc:*', NAMESPACES)
            if dc_elements:
                self.svg_info["has_dublin_core"] = True
                self._extract_dublin_core(dc_elements)
        
        title = self.root.find('svg:title', NAMESPACES)
        if title is None:
            title = self.root.find('.//{http://www.w3.org/2000/svg}title')
        
        if title is not None and title.text:
            self.svg_info["title"] = title.text.strip()
        
        desc = self.root.find('svg:desc', NAMESPACES)
        if desc is None:
            desc = self.root.find('.//{http://www.w3.org/2000/svg}desc')
        
        if desc is not None and desc.text:
            self.svg_info["description"] = desc.text.strip()
        
        keywords = self.root.find('svg:keywords', NAMESPACES)
        if keywords is not None and keywords.text:
            self.svg_info["keywords"] = [k.strip() for k in keywords.text.split(',')]
        
        categories = self.root.find('svg:category', NAMESPACES)
        if categories is not None:
            self.svg_info["categories"] = categories.get('term', '')
    
    def _extract_rdf(self, rdf: ET.Element):
        """Extract RDF metadata"""
        description = rdf.find('rdf:Description', NAMESPACES)
        if description is not None:
            for attr in description.attrib:
                if attr.startswith('{'):
                    ns, local = attr[1:].split('}')
                    self.svg_info[f"rdf_{local}"] = description.get(attr)
    
    def _extract_dublin_core(self, elements: List[ET.Element]):
        """Extract Dublin Core metadata"""
        for elem in elements:
            local = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if elem.text:
                self.svg_info[f"dc_{local}"] = elem.text.strip()
    
    def _extract_elements(self):
        """Count and categorize SVG elements"""
        if self.root is None:
            return
        
        if self.root.tag not in ('{http://www.w3.org/2000/svg}svg', 'svg'):
            return
        
        element_counts: Dict[str, int] = {}
        total_elements = 0
        
        all_elements = self.root.iter()
        
        for elem in all_elements:
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}', 1)[1]
            
            element_counts[tag] = element_counts.get(tag, 0) + 1
            total_elements += 1
        
        self.svg_info["element_counts"] = dict(sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        self.svg_info["total_elements"] = total_elements
        
        self.svg_info["has_paths"] = 'path' in element_counts
        self.svg_info["has_shapes"] = any(s in element_counts for s in ['rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline'])
        self.svg_info["has_text"] = 'text' in element_counts or 'tspan' in element_counts
        self.svg_info["has_images"] = 'image' in element_counts
        self.svg_info["has_groups"] = 'g' in element_counts
        self.svg_info["has_symbols"] = 'symbol' in element_counts
        self.svg_info["has_markers"] = 'marker' in element_counts
        self.svg_info["has_masks"] = 'mask' in element_counts
        self.svg_info["has_filters"] = 'filter' in element_counts
        self.svg_info["has_gradients"] = any(g in element_counts for g in ['linearGradient', 'radialGradient', 'conicalGradient'])
        self.svg_info["has_patterns"] = 'pattern' in element_counts
        self.svg_info["has_links"] = 'a' in element_counts
    
    def _extract_animations(self):
        """Extract animation elements (SMIL)"""
        if self.root is None:
            return
        
        animations = {
            'animate': 0,
            'animateTransform': 0,
            'animateMotion': 0,
            'set': 0,
            'animateColor': 0
        }
        
        all_elements = self.root.iter()
        for elem in all_elements:
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}', 1)[1]
            if tag in animations:
                animations[tag] += 1
        
        self.svg_info["animations"] = animations
        self.svg_info["has_animations"] = sum(animations.values()) > 0
        
        if 'animateMotion' in animations and animations['animateMotion'] > 0:
            motion_path = self.root.find('.//{http://www.w3.org/2000/svg}animateMotion')
            if motion_path is not None:
                self.svg_info["has_motion_path"] = True
    
    def _extract_defs(self):
        """Extract definitions"""
        if self.root is None:
            return
        
        defs = self.root.find('svg:defs', NAMESPACES)
        if defs is None:
            defs = self.root.find('.//{http://www.w3.org/2000/svg}defs')
        
        if defs is not None:
            self.svg_info["has_defs"] = True
            
            def_counts: Dict[str, int] = {}
            for elem in defs.iter():
                tag = elem.tag
                if '}' in tag:
                    tag = tag.split('}', 1)[1]
                def_counts[tag] = def_counts.get(tag, 0) + 1
            
            self.svg_info["def_counts"] = def_counts
    
    def _extract_links(self):
        """Extract hyperlinks and xlink references"""
        if self.root is None:
            return
        
        xlink_href_count = 0
        anchor_count = 0
        use_count = 0
        
        all_elements = self.root.iter()
        for elem in all_elements:
            if elem.get('{http://www.w3.org/1999/xlink}href'):
                xlink_href_count += 1
            
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}', 1)[1]
            
            if tag == 'a':
                anchor_count += 1
            elif tag == 'use':
                use_count += 1
        
        self.svg_info["xlink_href_count"] = xlink_href_count
        self.svg_info["anchor_count"] = anchor_count
        self.svg_info["use_count"] = use_count
        self.svg_info["has_external_links"] = xlink_href_count > 0
    
    def _extract_styles(self):
        """Extract inline styles and CSS"""
        if self.root is None:
            return
        
        style_content = ''
        
        style_elem = self.root.find('svg:style', NAMESPACES)
        if style_elem is not None and style_elem.text:
            style_content = style_elem.text
        
        class_styles: Dict[str, str] = {}
        
        all_elements = self.root.iter()
        for elem in all_elements:
            style_attr = elem.get('style', '')
            class_attr = elem.get('class', '')
            
            if style_attr:
                if 'class' not in self.svg_info:
                    self.svg_info["has_inline_styles"] = True
            
            if class_attr:
                for cls in class_attr.split():
                    if cls and cls not in class_styles:
                        class_styles[cls] = True
        
        if style_content:
            self.svg_info["has_css"] = True
            self.svg_info["css_length"] = len(style_content)
        
        self.svg_info["unique_classes"] = list(class_styles.keys())
    
    def _extract_accessibility(self):
        """Extract accessibility metadata"""
        if self.root is None:
            return
        
        role = self.root.get('role', '')
        self.svg_info["aria_role"] = role
        
        aria_label = self.root.get('aria-label', '')
        self.svg_info["aria_label"] = aria_label
        
        aria_describedby = self.root.get('aria-describedby', '')
        self.svg_info["aria_describedby"] = aria_describedby
        
        tabindex = self.root.get('tabindex', '')
        self.svg_info["tabindex"] = tabindex
        
        focusable = self.root.get('focusable', '')
        self.svg_info["focusable"] = focusable
        
        self.svg_info["has_accessibility_attrs"] = any([
            role, aria_label, aria_describedby, tabindex, focusable
        ])
    
    def _build_result(self):
        """Build the final result dictionary"""
        self.svg_info["is_valid_svg"] = True
        
        self.svg_info["success"] = True


class SVGAnimationExtractor:
    """SVG SMIL animation metadata extractor"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse SVG animations"""
        try:
            from .svg_extractor import SVGExtractor
            svg = SVGExtractor(self.filepath)
            result = svg.parse()
            
            if not result.get("success"):
                return result
            
            return {
                "has_smil_animations": result.get("has_animations", False),
                "animation_details": result.get("animations", {}),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing SVG animations: {e}")
            return {"error": str(e), "success": False}


class SVGGradientExtractor:
    """SVG gradient and pattern metadata extractor"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse SVG gradients and patterns"""
        try:
            from .svg_extractor import SVGExtractor
            svg = SVGExtractor(self.filepath)
            result = svg.parse()
            
            defs = result.get("def_counts", {})
            gradients = sum(1 for g in defs if 'Gradient' in g)
            
            return {
                "gradient_count": gradients,
                "pattern_count": defs.get("pattern", 0),
                "def_counts": defs,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing SVG gradients: {e}")
            return {"error": str(e), "success": False}


class SVGFilterExtractor:
    """SVG filter effects metadata extractor"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse SVG filter effects"""
        try:
            from .svg_extractor import SVGExtractor
            svg = SVGExtractor(self.filepath)
            result = svg.parse()
            
            filters = result.get("def_counts", {})
            filter_count = filters.get("filter", 0)
            
            return {
                "filter_count": filter_count,
                "has_filters": filter_count > 0,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing SVG filters: {e}")
            return {"error": str(e), "success": False}
