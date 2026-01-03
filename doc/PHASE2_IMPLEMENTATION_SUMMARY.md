# Phase 2 Implementation Summary

## Overview

Phase 2 focuses on deep media extraction: video codec internals, container structure, and audio codec details. Implementations favor a pragmatic approach: start with light-weight, robust parsing (heuristics + safe fixed-field parsing), combined with tests and fixtures.

## What was implemented

### Video codec details (`server/extractor/modules/video_codec_details.py`)

- Deep analysis entry `extract_video_codec_details()`
- H.264:
  - `extract_h264_deep_analysis()` produces detailed fields
  - `parse_h264_sps()` implemented with emulation prevention removal, start-code stripping, and extraction of profile/constraint/level
  - Extended SPS parsing with **Exp-Golomb decoding** for seq_parameter_set_id, chroma_format_idc, bit_depth_luma/chroma, log2_max_frame_num_minus4, pic_order_cnt_type
  - Robust BitReader class with EOF handling for bit-level parsing
- HEVC:
  - `extract_hevc_deep_analysis()` remains with heuristics; added `parse_hevc_vps()` minimal VPS parser (profile/tier/level) as safe extraction
- AV1:
  - Lightweight `parse_av1_sequence_header()` to guess `profile` and `level` from OBU-like payload

### Container metadata (`server/extractor/modules/container_metadata.py`)

- MP4 atom parser (`parse_mp4_atoms()`), MP4 metadata extraction, and helpers already in place
- Added tests that write small MP4 fixtures with `ftyp` and `mdat` atoms and embedded NAL/OBU payloads

### Audio codec details (`server/extractor/modules/audio_codec_details.py`)

- MP3/AAC/FLAC/Opus/Vorbis parsing helpers implemented
- FLAC `parse_flac_streaminfo()` implemented and tested

## Tests & Fixtures

- New unit tests:
  - `tests/test_phase2_video.py` (field counts, H.264 deep analysis)
  - `tests/test_phase2_video_sps.py` (SPS parsing)
  - `tests/test_phase2_video_sps_extended.py` (chroma & bit depth Exp-Golomb parsing)
  - `tests/test_phase2_video_sps_edges.py` (edge cases: large UE, chroma 0/3, varying bit depths)
  - `tests/test_phase2_video_sps_fixtures.py` (binary fixture writing and parsing)
  - `tests/test_phase2_video_real_fixtures.py` (real H.264 SPS samples: 1080p High, 4K Main10, Baseline)
  - `tests/test_phase2_hevc_vps.py` (HEVC VPS minimal parsing)
  - `tests/test_phase2_av1.py` (AV1 sequence header heuristics)
  - `tests/test_phase2_hevc_av1_fixtures.py` (HEVC/AV1 binary fixture tests)
  - `tests/test_phase2_container.py` (MP4 atom parsing)
  - `tests/test_phase2_audio.py` (FLAC STREAMINFO parsing)
  - `tests/test_integration_containers_with_nal.py` (integration: write MP4 fixtures that contain H.264 SPS and HEVC VPS NALs and parse them)
- Binary fixtures: `tests/fixtures/h264_sps_samples.py` with real SPS RBSP examples for regression testing
- Tests run successfully locally: `pytest` → all tests pass (38 passed)

## CI

- Added a Phase 2 test step to `.github/workflows/ci.yml` to run fast Phase 2 tests during CI

## Design notes & tradeoffs

- Parsing approach: Start with safe heuristic parsing to extract high-value fields quickly (profile, level, chroma, bit depth)
- Avoiding full bitstream parsing initially (Exp-Golomb parsing, full RBSP decode) to reduce complexity and risk
- For higher fidelity, plan to implement spec-compliant parsing (Exp-Golomb reader) in a follow-up

## Next steps (recommended)

1. Add binary fixtures (real-world SPS/VPS/PPS/OBU samples) for more realistic integration tests
2. Implement full Exp-Golomb parsers for accurate field extraction (H.264 SPS, HEVC VPS/SPS, AV1 sequence header) — increases accuracy for chroma/bit depth and other fields
3. Extract more fields from AV1 and HEVC (tile columns/rows, level constraints, mastering display metadata)
4. Add validation tests comparing against `ffprobe` for real media files

---

Phase 2 progress: foundational deep parsing implemented (H.264 SPS, HEVC VPS, AV1 sequence header heuristics), container integration tests added, audio codec parsing and tests added.
