# Required Sample Files

This is the running list of real-world sample files needed to validate features
that cannot be fully covered by synthetic fixtures or unit tests.

## Video Telemetry (ExifTool -ee / GPMF / DJI)
- GoPro MP4 with GPMF telemetry track (gpmd/gpmf) including GPS + IMU.
- DJI drone MP4 with embedded telemetry (djmd/dbgi protobuf metadata).
- Action-cam MP4 with GPS5 or timed-metadata track (Garmin VIRB/Insta360).

## Video Container / Codec Edge Cases
- MP4/MOV with timecode track (tmcd) and chapters.
- MP4/MOV with `pasp` pixel aspect, `clap` clean aperture, and `colr` (nclx/ICC) boxes.
- MP4/MOV with `chan` channel layout and `st3d`/`sv3d` stereo/360 metadata.
- MKV with chapter tags + attachments (fonts/cover).
- AVI with RIFF INFO tags (INAM/IART/etc) and ODML extension.
- HDR10+ sample with dynamic metadata (SMPTE ST 2094-40 in HEVC).
- Dolby Vision MP4/MOV with DV profile metadata.

## Scientific / Medical Imaging
- DICOM (CT/MR) with populated patient/study/series tags.
- FITS image with WCS keywords.
- OME-TIFF with OME-XML in ImageDescription.
- OME-XML standalone file.
- GeoTIFF with GeoKeyDirectory + PixelScale/TiePoint tags.
- LAS/LAZ point cloud with LASF_Projection VLRs + WKT.

## Scientific Data (HDF5 / NetCDF)
- HDF5 with nested groups, dataset attributes, and compression.
- NetCDF4 with CF-convention attributes and multiple variables.

## Image Metadata (Vendor/MakerNotes)
- Canon/Nikon/Sony RAW with MakerNote fields populated.
- iPhone HEIC/HEIF with Live Photo + HDR/Portrait tags.
- Android Pixel JPEG with GDepth/GImage XMP namespaces.

## Audio Metadata (Professional / Broadcast)
- BWF WAV with bext + iXML chunks.
- Broadcast WAV with CART chunk and post‑timers.
- Broadcast WAV with axml metadata chunk.
- AIFF/AIFC with COMM/NAME/ANNO/COMT chunks.
- RF64 WAV with ds64 chunk and large data size.
- WAV with LIST adtl (labl/ltxt/note) chunks.
- MP3 with ID3v2.4 chapters (CHAP/CTOC).
- MP3 with SYLT (synced lyrics), RVA2 (volume), PRIV, and PCST frames.
- MP3 with ID3 advanced frames: COMR, GRID, SIGN, EQU2, MLLT, SEEK.
- MP3 with ID3 ASPI (audio seek point index).
- MP4/M4A with iTunes tags: stik/hdvd/pcst/so*/tv*.
- MP4/M4A with chpl chapter list atom.
- MP4/M4A with chap track references.
- APEv2 with binary cover art and external items.
- FLAC with PICTURE blocks and ReplayGain tags.
- DSF/DSDIFF (DSD) audio with metadata blocks.
- DSDIFF with PROP/CMPR/CHNL chunks and ID3 tag.

## Document Metadata (PDF/Office)
- PDF with AcroForm fields (text, checkbox, choice) and annotations.
- PDF with digital signature fields and signed revisions.

## Forensics / Security
- PNG/JPEG with C2PA (Content Credentials) manifest.
- EXE/PE with Authenticode signature + version info.

---
Add new entries here whenever an implementation depends on real-world samples.
