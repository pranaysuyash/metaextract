**Audio Metadata Deep Dive (3,500+ fields)**

Scope
- Goal: Full, forensically reliable audio metadata extraction across ID3, Vorbis, Opus, FLAC blocks, RIFF/BWF/iXML, MP4 iTunes tags, APEv2, and ASF.
- Primary sources of truth: mutagen + ffprobe for baseline stream info; direct binary parsers for codec/container headers.
- Output targets: `audio`, `audio.codec_details`, `audio.exiftool_details`, `normalized` (when mapped).

Extraction Sources
- mutagen: tags, container fields, embedded images, ReplayGain fields.
- ffprobe: stream-level codec info (bitrate, sample rate, channels, duration).
- Direct parsing: ID3v2/ID3v1, ADTS headers, FLAC metadata blocks, Ogg Opus/Vorbis headers, RIFF/BWF/iXML chunks, MP4 ilst tags, ASF file properties, APEv2 tags.

Coverage Map (by category)
- ID3v2/v1 (~1,200+): frames, text/URL/comment/lyrics/chapters/pictures, versions and flags.
- Vorbis Comments (~300+): vendor string, key/value tags, ReplayGain.
- Opus (~30+): OpusHead fields, pre-skip, output gain, channel mapping, OpusTags.
- FLAC (~50+ blocks/fields): STREAMINFO, VORBIS_COMMENT, PICTURE, CUESHEET, SEEKTABLE, APPLICATION, MD5.
- RIFF/WAV (~200+): fmt/data chunks, INFO tags, cue points, smpl loops, bext, iXML.
- MP4/M4A (~400+): iTunes ilst tags (title/artist/album/track/disc/cover art/freeform).
- APEv2 (~150+): tag items, ReplayGain, custom text/binary.
- ASF/WMA (~30+): file properties (duration, packets, bitrate).

Current Implementation Notes
- ID3v2 is parsed from file header; text frames, comments, lyrics, pictures, UFID/PRIV/POPM/PCNT, CHAP/CTOC.
- ID3v1 parsed from trailing 128 bytes with genre mapping.
- ADTS header parsing provides profile, sample rate, channel config, frame length.
- Ogg packets are reassembled to parse OpusHead/OpusTags and Vorbis identification/comment headers.
- FLAC parser extracts STREAMINFO, Vorbis comments (map + raw list), PICTURE blocks, CUESHEET, SEEKTABLE, APPLICATION, padding.
- RIFF parser extracts fmt, data size, LIST/INFO tags, BWF bext, iXML XML tags, cue points, smpl fields.
- MP4 ilst tags are parsed (including freeform mean/name keys).
- ASF file properties are parsed for header-level metadata.

Normalization Targets
- Standardized tag names (title/artist/album/date/track/disc) across ID3/Vorbis/MP4/APE.
- ReplayGain fields consolidated under `audio.codec_details.replaygain`.
- Uniform album art metadata (size/mime/hash) across ID3/FLAC/MP4.

Gaps to Close (implementation targets)
- MP4 chapters/atoms (chpl, chap) and additional ilst tags (lyrics, grouping, rating).
- ASF extended content descriptors and metadata library objects.
- AIFF/AIFC chunk parsing (COMM, NAME, ANNO) and embedded ID3 chunks.
- BWF cart chunk parsing and extended loudness history.

Acceptance Criteria
- MP3/FLAC/Ogg/WAV/M4A files report codec-level headers plus tags with no silent loss.
- ReplayGain, album art, and chapters are surfaced when present.
- RIFF/BWF and iXML metadata are preserved and countable.
