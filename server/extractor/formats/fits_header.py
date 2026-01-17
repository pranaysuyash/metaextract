from __future__ import annotations

from typing import Any


def extract_fits_container_metadata(filepath: str, max_blocks: int = 64) -> dict[str, Any] | None:
    """
    Parse FITS header cards (80-byte records) from the primary header.

    FITS headers are ASCII and padded to 2880-byte blocks. This parser:
    - scans cards until END
    - extracts a small set of common keywords + dimensions
    - does not attempt to parse extensions or binary tables
    """
    try:
        with open(filepath, "rb") as f:
            header_bytes = f.read(2880 * max_blocks)
        if not header_bytes.startswith(b"SIMPLE"):
            return None

        cards: list[str] = []
        for i in range(0, len(header_bytes), 80):
            card = header_bytes[i : i + 80]
            if len(card) != 80:
                break
            try:
                text = card.decode("ascii", errors="replace")
            except Exception:
                break
            cards.append(text)
            if text.startswith("END"):
                break

        def get_value(key: str) -> str | None:
            for c in cards:
                if not c.startswith(key.ljust(8)):
                    continue
                if "=" not in c:
                    return None
                rhs = c.split("=", 1)[1]
                rhs = rhs.split("/", 1)[0].strip()
                return rhs.strip()
            return None

        simple = get_value("SIMPLE")
        bitpix = get_value("BITPIX")
        naxis = get_value("NAXIS")
        extend = get_value("EXTEND")
        date = get_value("DATE")
        object_name = get_value("OBJECT")
        telescope = get_value("TELESCOP")
        instrument = get_value("INSTRUME")

        dims: list[int] | None = None
        try:
            n = int(str(naxis).strip()) if naxis is not None else 0
            if n > 0:
                dims = []
                for idx in range(1, min(n, 8) + 1):
                    v = get_value(f"NAXIS{idx}")
                    if v is None:
                        break
                    dims.append(int(str(v).strip()))
        except Exception:
            dims = None

        return {
            "available": True,
            "format": "FITS",
            "cards_parsed": len(cards),
            "simple": simple,
            "bitpix": bitpix,
            "naxis": naxis,
            "dimensions": dims,
            "extend": extend,
            "date": date,
            "object": object_name,
            "telescope": telescope,
            "instrument": instrument,
        }
    except Exception:
        return None

