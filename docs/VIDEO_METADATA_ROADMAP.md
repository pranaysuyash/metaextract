**Video Metadata Roadmap**

Implemented (current)
- Codec deep analysis (H.264/HEVC/VP9/AV1) with profile/level/bit depth details.
- HDR parsing for mastering display and content light side data.
- VR/360 projection hints from ffprobe side data and tags.
- Container parsing for MP4/MKV/AVI (atoms/EBML/RIFF) and ilst tags.
- Timecode + telemetry stream detection (tmcd/data tracks).

Next milestones
1) Dolby Vision config parsing (profile/level/RPU fields).
2) HDR10+ dynamic metadata mapping.
3) Telemetry payload decoding (GoPro GPMF, DJI protobuf).
4) MXF container parsing (SMPTE header metadata sets).
