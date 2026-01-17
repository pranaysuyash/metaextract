from __future__ import annotations

import gzip
from collections import Counter
from typing import Any


def _read_svg_text(filepath: str, max_bytes: int) -> str:
    if filepath.lower().endswith(".svgz"):
        with gzip.open(filepath, "rb") as f:
            data = f.read(max_bytes + 1)
    else:
        with open(filepath, "rb") as f:
            data = f.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("SVG too large")
    return data.decode("utf-8", errors="replace")


def extract_svg_container_metadata(
    filepath: str,
    *,
    max_bytes: int = 2_000_000,
    max_elements: int = 200_000,
) -> dict[str, Any] | None:
    """
    Extract container-level metadata from SVG/SVGZ (XML-based vector images).

    This is not a renderer; it performs safe-ish structural parsing and captures:
    - width/height/viewBox/version
    - element/tag counts (bounded)
    - basic security signals: scripts, on* handlers, external hrefs
    """
    try:
        import xml.etree.ElementTree as ET

        text = _read_svg_text(filepath, max_bytes=max_bytes)
        # Iterative parse so we can cap element traversal and keep memory stable.
        # Still uses ElementTree internals; max_bytes/max_elements are primary defenses.
        element_counts: Counter[str] = Counter()
        has_scripts = False
        has_event_handlers = False
        external_links: set[str] = set()
        embedded_images = 0

        # Parse root attributes via full parse of first element.
        root = ET.fromstring(text)
        width = root.get("width")
        height = root.get("height")
        view_box = root.get("viewBox")
        version = root.get("version")

        # Walk elements with a hard cap (avoid attacker-controlled huge trees).
        count = 0
        for elem in root.iter():
            count += 1
            if count > max_elements:
                break
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            element_counts[tag] += 1

            if tag.lower() == "script":
                has_scripts = True

            for attr, val in (elem.attrib or {}).items():
                if attr.lower().startswith("on"):
                    has_event_handlers = True
                if attr.endswith("href") or attr.lower() == "href":
                    if isinstance(val, str) and (val.startswith("http://") or val.startswith("https://")):
                        external_links.add(val)

            if tag.lower() == "image":
                embedded_images += 1

        view_box_dims: dict[str, float] | None = None
        if view_box and not (width and height):
            parts = view_box.replace(",", " ").split()
            if len(parts) >= 4:
                try:
                    view_box_dims = {
                        "min_x": float(parts[0]),
                        "min_y": float(parts[1]),
                        "width": float(parts[2]),
                        "height": float(parts[3]),
                    }
                except Exception:
                    view_box_dims = None

        return {
            "available": True,
            "format": "SVG",
            "compressed": filepath.lower().endswith(".svgz"),
            "width": width,
            "height": height,
            "viewBox": view_box,
            "viewBox_dims": view_box_dims,
            "version": version,
            "total_elements": min(count, max_elements),
            "element_counts": dict(element_counts),
            "embedded_images": embedded_images,
            "security": {
                "has_scripts": has_scripts,
                "has_event_handlers": has_event_handlers,
                "external_link_count": len(external_links),
                "external_links_sample": sorted(list(external_links))[:10],
                "truncated": count > max_elements,
            },
        }
    except Exception:
        return None

