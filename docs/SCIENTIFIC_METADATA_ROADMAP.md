**Scientific Metadata Roadmap**

Implemented (current)
- DICOM, FITS, OME-TIFF/OME-XML, microscopy (CZI/LIF/ND2), GeoTIFF, LAS/LAZ parsing.
- GeoKeyDirectory parsing for GeoTIFF and LAS projection VLRs.
- LAS header and projection metadata extraction.

Next milestones
1) Expand DICOM private tags and SR (structured report) parsing.
2) FITS WCS keyword normalization.
3) LAS extra bytes VLR decoding and waveform metadata.
4) Add HDF5/NetCDF into the main engine (not just comprehensive engine).
