#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE = REPO_ROOT / "server" / "extractor" / "comprehensive_metadata_engine.py"

def main() -> int:
    if not ENGINE.exists():
        print("Missing comprehensive_metadata_engine.py", file=sys.stderr)
        return 1

    text = ENGINE.read_text(encoding="utf-8", errors="ignore")

    patterns = [
        re.compile(r"server\.extractor\.modules\.([a-zA-Z0-9_]+)"),
        re.compile(r"from\s+server\.extractor\.modules\s+import\s+([a-zA-Z0-9_,\s]+)"),
        re.compile(r"from\s+server\.extractor\.modules\.([a-zA-Z0-9_]+)\s+import"),
    ]

    modules: set[str] = set()
    for pattern in patterns:
        for match in pattern.findall(text):
            if isinstance(match, tuple):
                match = match[0]
            for item in str(match).split(","):
                name = item.strip()
                if name:
                    modules.add(name)

    for module in sorted(modules):
        print(module)
    return 0

if __name__ == "__main__":
    sys.exit(main())
