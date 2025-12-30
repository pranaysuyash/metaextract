**Audio Metadata Roadmap**

Implemented (current)
- ID3v2/v1 parsing with frames, comments, lyrics, pictures, chapters.
- MP3 frame header + Xing/VBRI/LAME tag parsing.
- ADTS AAC header parsing (profile, sample rate, channel config, frame length).
- FLAC STREAMINFO + metadata blocks (Vorbis comments, picture, cuesheet, seektable, application).
- Ogg Opus/Vorbis header + tag parsing (OpusHead/OpusTags, Vorbis id/comment).
- RIFF/WAV chunks (fmt/data/INFO/cue/smpl) + BWF bext + iXML.
- MP4/M4A ilst tag parsing (including freeform mean/name).
- APEv2 tag parsing.
- ASF file properties parsing.

Next milestones
1) Expand MP4 atom parsing for chapter lists and iTunes-specific fields (soundcheck, grouping).
2) Add AIFF/AIFC chunk parsing and embedded ID3 chunks.
3) Parse ASF extended metadata objects (content descriptors, metadata library).
4) Add BWF cart chunk parsing and more loudness history fields.
5) Add integration tests with real fixtures across MP3/FLAC/Ogg/WAV/M4A/ASF.
