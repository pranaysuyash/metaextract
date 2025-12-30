**Video Metadata Deep Dive (8,000+ fields)**

Scope
- Goal: Full video container + codec metadata, HDR/VR, timecode, chapters, and telemetry.
- Primary sources: ffprobe for stream/side data, internal parsers for MP4/MKV/AVI containers.
- Output targets: `video`, `video.codec_details`, `video.exiftool_details`, `container`, `normalized`.

Extraction Sources
- ffprobe: stream codecs, side_data_list (HDR, Dolby Vision), chapters, tags.
- Container parsers: MP4/MOV atoms, MKV EBML, AVI RIFF.

Coverage Map (by category)
- Codec deep analysis: H.264/HEVC/VP9/AV1 profiles, levels, bit depth, GOP/refs.
- HDR metadata: HDR10/HLG detection, mastering display, content light, HDR10+ and Dolby Vision flags.
- VR/360: spherical metadata, stereo mode, projection.
- Container metadata: MP4 atom tree, MKV segment info/tracks/tags/chapters, AVI stream headers.
- Timecode + telemetry: tmcd track detection, data streams (GoPro GPMF, DJI).

Current Implementation Notes
- Stream-level codec extraction via `video_codec_details` with nested field counting.
- HDR side data parsing for mastering display + MaxCLL/MaxFALL when available.
- Container parsing in `container_metadata` for MP4/MKV/AVI, including ilst tags.
- Timecode and metadata streams surfaced via ffprobe stream tags and codec tags.

Gaps to Close (implementation targets)
- Dolby Vision config parsing (profiles/levels/RPU) beyond ffprobe side_data.
- HDR10+ dynamic metadata field mapping.
- Telemetry payload parsing (GoPro GPMF, DJI protobuf) into structured samples.

Acceptance Criteria
- Video files report codec profiles/levels and HDR metadata where present.
- MP4/MKV/AVI containers show track structures, chapters, and metadata tags.
- Timecode and telemetry tracks are detected and surfaced.
