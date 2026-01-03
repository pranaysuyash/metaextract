# Scientific Library Research Report

## Executive Summary

This report evaluates optimal Python libraries for extracting metadata from scientific and medical file formats. The research focused on DICOM, FITS, HDF5, NetCDF, and GeoTIFF, comparing key libraries to determine the best choices for the **MetaExtract** engine.

**Key Recommendations:**
1.  **DICOM**: Use **`pydicom`** for deep metadata extraction. (Current implementation is correct).
2.  **FITS**: Use **`astropy`**. `pyfits` is deprecated and should be avoided.
3.  **HDF5/NetCDF**: Use **`h5py`** for raw HDF5 and **`netCDF4`** for NetCDF files. They are complementary.
4.  **GeoTIFF**: Use **`rasterio`** for standard geospatial metadata.

---

## 1. Medical Imaging (DICOM)

### Comparison: `pydicom` vs. `dicom2nifti`

| Feature | `pydicom` | `dicom2nifti` |
| :--- | :--- | :--- |
| **Primary Purpose** | Reading/Writing/Modifying DICOM tags & data | Converting DICOM series to NIfTI format |
| **Metadata Access** | **Full Access** to all public & private tags | Limited (often lost or simplified during conversion) |
| **Manipulation** | Can edit individual tags, sequences, and VRs | Read-only input, output is NIfTI |
| **Use Case** | Metadata extraction, anonymization, QA | Neuroimaging pipelines, MRI processing |

**Conclusion:**
**`pydicom`** is the superior choice for this project. `dicom2nifti` is excellent for its specific purpose (conversion) but is not a metadata extraction tool. `pydicom` provides the granular access required to extract the 4,000+ fields targeted by MetaExtract.

---

## 2. Astronomical Data (FITS)

### Comparison: `astropy` vs. `pyfits`

| Feature | `astropy` (`astropy.io.fits`) | `pyfits` |
| :--- | :--- | :--- |
| **Status** | **Active Standard** | **Deprecated / Discontinued** |
| **Maintenance** | Frequent updates, community-driven | Last release ~2017 |
| **Integration** | Part of the larger Astropy ecosystem (WCS, units) | Standalone (legacy) |
| **Compatibility** | Python 3.10+ compatible | May have issues with modern Python |

**Conclusion:**
**`astropy`** is the only viable option. `pyfits` development has ceased, and its codebase was merged into `astropy.io.fits`. Any legacy `pyfits` code should be migrated to `astropy`.

---

## 3. Scientific Data Formats (HDF5 & NetCDF)

### Comparison: `h5py` vs. `netCDF4`

These libraries are related but serve different abstraction levels.

*   **HDF5 (`h5py`)**:
    *   **Role**: Direct Python interface to the HDF5 binary format.
    *   **Strengths**: Generic, flexible, handles any HDF5 file. Excellent for "raw" data inspection.
    *   **Weakness**: Doesn't natively understand climate/weather conventions (like CF conventions).

*   **NetCDF (`netCDF4`)**:
    *   **Role**: Specialized library for NetCDF format (which often uses HDF5 as a backend).
    *   **Strengths**: Understands "Dimensions", "Variables", and "Coordinates" - key concepts in earth science. Handles **OpenDAP** remote access.
    *   **Weakness**: More specific scope than generic HDF5.

**Conclusion:**
The project should **maintain both dependencies**.
*   Use `netCDF4` for `.nc` / `.cdf` files to extract semantically meaningful dimensions and attributes.
*   Use `h5py` as a fallback or for generic `.h5` / `.hdf5` files that do not follow NetCDF conventions.

---

## 4. Geospatial Data (GeoTIFF)

### Evaluation: `rasterio` vs. `osgeo` (GDAL) vs. `tifffile`

| Library | Strengths | Weaknesses | Verdict |
| :--- | :--- | :--- | :--- |
| **`rasterio`** | **Pythonic**, easy API. Excellent for CRS, bounds, and affine transforms. | Adds GDAL dependency (binary). | **Best for GeoTIFF** |
| **`osgeo`** (GDAL) | The "source of truth". Most powerful. | Non-Pythonic (C++ style API). Hard to install/maintain. | Overkill / Too complex |
| **`tifffile`** | Pure Python (mostly). Great for bio-formats (Ome-TIFF). | Lacks geospatial awareness (projections, CRS). | Best for **Bio-TIFFs** |

**Conclusion:**
**`rasterio`** is the recommended choice for GeoTIFFs due to its developer-friendly API and robust handling of Coordinate Reference Systems (CRS). `tifffile` should be reserved for scientific/microscopy TIFFs (non-geo).

---

## Implementation Action Plan

1.  **Verify Dependencies**: Ensure `requirements.txt` includes:
    *   `pydicom>=2.4.0`
    *   `astropy>=5.0.0`
    *   `h5py>=3.10.0`
    *   `netCDF4>=1.6.0`
    *   `rasterio>=1.3.0`
2.  **Refactor Imports**: Scan codebase for `import pyfits` and replace with `from astropy.io import fits`.
3.  **Module Design**:
    *   **DICOM Module**: Continue using `pydicom`.
    *   **FITS Module**: Build using `astropy.io.fits`.
    *   **HDF5 Module**: Detect if file is NetCDF; if so use `netCDF4`, else `h5py`.
    *   **GeoTIFF Module**: Use `rasterio` to extract CRS and bounds.

