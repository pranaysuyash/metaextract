#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE = REPO_ROOT / "server" / "extractor" / "comprehensive_metadata_engine.py"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
GENERATED_DIR = FIXTURES_DIR / "generated"

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def write_minimal_pdf(path: Path) -> None:
    content = """%PDF-1.1
1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj
2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj
3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>endobj
4 0 obj<< /Length 44 >>stream
BT /F1 18 Tf 50 150 Td (Hello) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000111 00000 n 
0000000191 00000 n 
trailer<< /Root 1 0 R /Size 5 >>
startxref
275
%%EOF
"""
    path.write_text(content, encoding="ascii")

def write_minimal_svg(path: Path) -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">
  <rect width="120" height="80" fill="#111827"/>
  <text x="10" y="45" fill="#ffffff" font-size="14">MetaExtract</text>
</svg>
"""
    path.write_text(svg, encoding="ascii")

def ensure_media_fixtures() -> dict[str, Path]:
    ensure_dir(GENERATED_DIR)
    mp4_path = GENERATED_DIR / "sample.mp4"
    mp3_path = GENERATED_DIR / "sample.mp3"
    pdf_path = GENERATED_DIR / "sample.pdf"
    svg_path = GENERATED_DIR / "sample.svg"

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found; required to generate mp4/mp3 fixtures")

    if not mp4_path.exists():
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=black:s=320x240:d=1",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=mono:sample_rate=44100",
                "-shortest",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                str(mp4_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    if not mp3_path.exists():
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=mono:sample_rate=44100",
                "-t",
                "1",
                "-q:a",
                "9",
                "-acodec",
                "libmp3lame",
                str(mp3_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    if not pdf_path.exists():
        write_minimal_pdf(pdf_path)

    if not svg_path.exists():
        write_minimal_svg(svg_path)

    image_candidates = [
        FIXTURES_DIR / "test_simple.jpg",
        FIXTURES_DIR / "test.jpg",
        FIXTURES_DIR / "test_image.jpg",
    ]
    image_path = next((p for p in image_candidates if p.exists()), None)
    if not image_path:
        raise RuntimeError("No image fixture found in tests/fixtures")

    audio_path = REPO_ROOT / "server" / "extractor" / "sample-files" / "test_audio.wav"
    if not audio_path.exists():
        raise RuntimeError("Missing audio fixture server/extractor/sample-files/test_audio.wav")

    return {
        "image": image_path,
        "video": mp4_path,
        "audio": audio_path,
        "pdf": pdf_path,
        "svg": svg_path,
    }

def run_engine(file_path: Path) -> dict:
    cmd = [
        sys.executable,
        str(ENGINE),
        str(file_path),
        "--tier",
        "free",
        "--quiet",
        "--max-dim",
        "2048",
    ]
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return json.loads(result.stdout.decode("utf-8"))

def has_meaningful_data(payload: dict, key: str) -> bool:
    section = payload.get(key)
    if section is None:
        return False
    if isinstance(section, dict):
        return any(v not in (None, "", [], {}) for v in section.values())
    if isinstance(section, list):
        return len(section) > 0
    return True

def verify() -> int:
    fixtures = ensure_media_fixtures()
    failures: list[str] = []

    for kind, path in fixtures.items():
        payload = run_engine(path)
        if "error" in payload:
            failures.append(f"{kind}: engine error -> {payload.get('error')}")
            continue

        key = kind
        if kind == "image":
            key = "image"
        elif kind == "video":
            key = "video"
        elif kind == "audio":
            key = "audio"
        elif kind == "pdf":
            key = "pdf"
        elif kind == "svg":
            key = "svg"

        if not has_meaningful_data(payload, key):
            failures.append(f"{kind}: no meaningful data in '{key}' section")

    if failures:
        print("Verification failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("Verification passed for image, video, audio, pdf, svg.")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
