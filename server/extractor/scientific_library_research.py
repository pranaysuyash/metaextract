#!/usr/bin/env python3
"""
Scientific Library Research Agent

Research and compare optimal libraries for:
- DICOM (medical imaging)
- FITS (astronomical data)
- HDF5/NetCDF (scientific data formats)
- GeoTIFF (geospatial rasters)

Author: MetaExtract Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json


class ScientificDomain(Enum):
    MEDICAL_IMAGING = "medical_imaging"
    ASTRONOMICAL = "astronomical"
    CLIMATE_WEATHER = "climate_weather"
    GEOSPATIAL = "geospatial"
    GENERAL_SCIENTIFIC = "general_scientific"


class LibraryCategory(Enum):
    PRIMARY = "primary"
    SPECIALIZED = "specialized"
    UTILITY = "utility"
    CONVERSION = "conversion"


@dataclass
class LibraryInfo:
    """Information about a scientific library."""
    name: str
    description: str
    primary_domain: ScientificDomain
    category: LibraryCategory
    license: str
    python_native: bool
    maintenance_status: str
    last_updated: str
    popularity_stars: Optional[int] = None
    weekly_downloads: Optional[int] = None
    
    # Capabilities
    read_support: bool = True
    write_support: bool = False
    streaming_support: bool = False
    compression_support: bool = True
    
    # Performance
    performance_rating: str = "unknown"  # excellent, good, moderate, slow
    memory_efficiency: str = "unknown"
    
    # Integration
    numpy_integration: bool = True
    xarray_integration: bool = False
    dask_integration: bool = False
    
    # Key features
    key_features: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    
    # Usage example
    usage_example: str = ""


@dataclass
class LibraryComparison:
    """Comparison between libraries for a specific use case."""
    use_case: str
    domain: ScientificDomain
    libraries: List[LibraryInfo]
    recommendation: str
    alternative: str
    comparison_matrix: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class ScientificLibraryResearchAgent:
    """
    Research agent for scientific libraries.
    Provides recommendations based on comprehensive analysis.
    """

    def __init__(self):
        self.library_registry: Dict[str, LibraryInfo] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        """Initialize the library registry with known libraries."""
        
        # DICOM Libraries
        self.library_registry["pydicom"] = LibraryInfo(
            name="pydicom",
            description="The de facto standard Python library for working with DICOM medical imaging data",
            primary_domain=ScientificDomain.MEDICAL_IMAGING,
            category=LibraryCategory.PRIMARY,
            license="MIT",
            python_native=True,
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=2600,
            weekly_downloads=180000,
            read_support=True,
            write_support=True,
            streaming_support=False,
            compression_support=True,
            performance_rating="good",
            memory_efficiency="moderate",
            numpy_integration=True,
            xarray_integration=False,
            dask_integration=False,
            key_features=[
                "Complete DICOM standard support",
                "Pixel data handling and decompression",
                "Structured Report parsing",
                "De-identification support",
                "VR (Value Representation) validation",
                "Private tag handling"
            ],
            limitations=[
                "Limited image processing capabilities",
                "No built-in visualization",
                "Not optimized for very large datasets"
            ],
            usage_example='''
import pydicom
from pydicom import dcmread

ds = dcmread("scan.dcm")
patient_name = ds.PatientName
arr = ds.pixel_array  # NumPy array
'''
        )

        self.library_registry["simpleitk"] = LibraryInfo(
            name="SimpleITK",
            description="Simplified interface to the Insight Segmentation and Registration Toolkit for medical image processing",
            primary_domain=ScientificDomain.MEDICAL_IMAGING,
            category=LibraryCategory.SPECIALIZED,
            license="Apache 2.0",
            python_native=False,  # C++ wrapper
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=1200,
            weekly_downloads=45000,
            read_support=True,
            write_support=True,
            streaming_support=False,
            compression_support=True,
            performance_rating="excellent",
            memory_efficiency="good",
            numpy_integration=True,
            xarray_integration=False,
            dask_integration=False,
            key_features=[
                "Extensive image processing algorithms",
                "Multi-modal image registration",
                "Segmentation capabilities",
                "Resampling and interpolation",
                "Integration with ITK"
            ],
            limitations=[
                "Larger installation footprint",
                "Steeper learning curve",
                "Limited metadata extraction compared to pydicom"
            ],
            usage_example='''
import SimpleITK as sitk

image = sitk.ReadImage("scan.dcm")
arr = sitk.GetArrayFromImage(image)
filtered = sitk.SmoothingRecursiveGaussian(image, sigma=1.0)
'''
        )

        self.library_registry["dicom2nifti"] = LibraryInfo(
            name="dicom2nifti",
            description="Specialized library for converting DICOM series to NIfTI format for neuroimaging",
            primary_domain=ScientificDomain.MEDICAL_IMAGING,
            category=LibraryCategory.CONVERSION,
            license="BSD 3-Clause",
            python_native=True,
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=350,
            weekly_downloads=12000,
            read_support=True,
            write_support=True,
            streaming_support=False,
            compression_support=True,
            performance_rating="good",
            memory_efficiency="moderate",
            numpy_integration=True,
            xarray_integration=False,
            dask_integration=False,
            key_features=[
                "Automatic slice ordering",
                "Philips private tags handling",
                "GE DICOM conformance",
                "Slice alignment correction"
            ],
            limitations=[
                "Specialized for neuroimaging only",
                "Not for general DICOM handling",
                "Requires complete series for best results"
            ],
            usage_example='''
import dicom2nifti
dicom2nifti.dicom_series_to_nifti("dicom_dir/", "output.nii.gz")
'''
        )

        # FITS Libraries
        self.library_registry["astropy"] = LibraryInfo(
            name="astropy.io.fits",
            description="Part of the Astropy Project, providing FITS file I/O and WCS support for astronomical data",
            primary_domain=ScientificDomain.ASTRONOMICAL,
            category=LibraryCategory.PRIMARY,
            license="BSD 3-Clause",
            python_native=True,
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=1500,  # Astropy overall
            weekly_downloads=250000,
            read_support=True,
            write_support=True,
            streaming_support=False,
            compression_support=True,
            performance_rating="good",
            memory_efficiency="good",
            numpy_integration=True,
            xarray_integration=False,
            dask_integration=False,
            key_features=[
                "Complete FITS 4.0 standard support",
                "World Coordinate System (WCS) handling",
                "Header manipulation and validation",
                "Image compression (RICE, GZIP, HCOMPRESS)",
                "Table operations (ASCII and Binary)",
                "Integration with astropy cosmology and units"
            ],
            limitations=[
                "Memory intensive for very large files",
                "Streaming support limited",
                "API can be verbose"
            ],
            usage_example='''
from astropy.io import fits
from astropy import units as u

with fits.open("observation.fits") as hdul:
    hdul.info()
    data = hdul[0].data
    header = hdul[0].header
    # WCS transformation
    from astropy.wcs import WCS
    w = WCS(header)
'''
        )

        self.library_registry["fitsio"] = LibraryInfo(
            name="fitsio",
            description="Python wrapper around CFITSIO (NASA's C library) providing fast FITS I/O",
            primary_domain=ScientificDomain.ASTRONOMICAL,
            category=LibraryCategory.PRIMARY,
            license="MIT",
            python_native=False,  # C extension
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=500,
            weekly_downloads=35000,
            read_support=True,
            write_support=True,
            streaming_support=True,
            compression_support=True,
            performance_rating="excellent",
            memory_efficiency="excellent",
            numpy_integration=True,
            xarray_integration=False,
            dask_integration=False,
            key_features=[
                "Highest performance FITS I/O",
                "Direct memory mapping for large files",
                "Tile compression support",
                "Variable length arrays",
                "Heap manipulation"
            ],
            limitations=[
                "Less Pythonic than astropy",
                "Limited high-level abstractions",
                "Requires CFITSIO C library"
            ],
            usage_example='''
import fitsio

# Read FITS file
hdr = fitsio.read_header("observation.fits", 0)
data = fitsio.read("observation.fits")

# Write compressed FITS
fitsio.write("output.fits", data, compress=True, tile_size=(1000, 1000))
'''
        )

        # HDF5 Libraries
        self.library_registry["h5py"] = LibraryInfo(
            name="h5py",
            description="Python interface to the HDF5 binary data format for storing large amounts of numerical data",
            primary_domain=ScientificDomain.GENERAL_SCIENTIFIC,
            category=LibraryCategory.PRIMARY,
            license="BSD 3-Clause",
            python_native=False,  # C extension
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=1500,
            weekly_downloads=400000,
            read_support=True,
            write_support=True,
            streaming_support=True,
            compression_support=True,
            performance_rating="excellent",
            memory_efficiency="excellent",
            numpy_integration=True,
            xarray_integration=True,
            dask_integration=True,
            key_features=[
                "Pythonic HDF5 interface",
                "Parallel HDF5 support (with mpi4py)",
                "Chunking and compression",
                "Reference and attribute systems",
                "Dataset selection by hyperslab"
            ],
            limitations=[
                "No built-in data model validation",
                "Complex API for advanced features",
                "File locking on some systems"
            ],
            usage_example='''
import h5py
import numpy as np

with h5py.File("data.h5", "r") as f:
    dataset = f["/measurements/temperature"]
    data = dataset[100:200, :]  # Slicing
    attrs = dataset.attrs

# Write with compression
with h5py.File("output.h5", "w") as f:
    f.create_dataset("data", data=np.random.rand(1000, 1000),
                     chunks=True, compression="gzip", compression_opts=9)
'''
        )

        self.library_registry["netCDF4"] = LibraryInfo(
            name="netCDF4",
            description="Python interface to the netCDF C library with support for netCDF4/HDF5 files",
            primary_domain=ScientificDomain.CLIMATE_WEATHER,
            category=LibraryCategory.PRIMARY,
            license="MIT",
            python_native=False,  # C extension
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=700,
            weekly_downloads=150000,
            read_support=True,
            write_support=True,
            streaming_support=False,
            compression_support=True,
            performance_rating="good",
            memory_efficiency="good",
            numpy_integration=True,
            xarray_integration=True,
            dask_integration=False,
            key_features=[
                "netCDF4 data model",
                "CDF-2, netCDF3, netCDF4 support",
                "HDF5 backend when available",
                "NUD/CDL metadata",
                "Chunking and compression",
                "MFDataset for multi-file datasets"
            ],
            limitations=[
                "More complex than h5py for HDF5",
                "Limited parallel write support",
                "CMIP6 data handling requires care"
            ],
            usage_example='''
from netCDF4 import Dataset
import numpy as np

with Dataset("climate.nc", "r") as nc:
    temp = nc.variables["temperature"]
    time = nc.variables["time"]
    # Read data
    data = temp[:]

# Create netCDF4 file
with Dataset("output.nc", "w") as nc:
    nc.createDimension("time", None)
    nc.createDimension("lat", 180)
    nc.createDimension("lon", 360)
    
    time_var = nc.createVariable("time", "f8", ("time",))
    temp_var = nc.createVariable("temperature", "f4", ("time", "lat", "lon"))
'''
        )

        self.library_registry["xarray"] = LibraryInfo(
            name="xarray",
            description="N-dimensional labeled arrays and datasets with netCDF and Zarr support",
            primary_domain=ScientificDomain.GENERAL_SCIENTIFIC,
            category=LibraryCategory.UTILITY,
            license="Apache 2.0",
            python_native=True,
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=3500,
            weekly_downloads=500000,
            read_support=True,
            write_support=True,
            streaming_support=True,
            compression_support=True,
            performance_rating="good",
            memory_efficiency="good",
            numpy_integration=True,
            xarray_integration=True,
            dask_integration=True,
            key_features=[
                "Labeled dimensions and coordinates",
                "Pandas-like API for N-D arrays",
                "Transparent chunking with Dask",
                "netCDF, Zarr, GRIB support",
                "Lazy evaluation",
                "CF conventions support"
            ],
            limitations=[
                "Wrapper around other libraries",
                "Memory overhead for metadata",
                "Learning curve for advanced features"
            ],
            usage_example='''
import xarray as xr
import numpy as np

# Open netCDF
ds = xr.open_dataset("climate.nc")
temp = ds.temperature

# Create Dataset
ds_new = xr.Dataset(
    {"temperature": (["time", "lat", "lon"], np.random.rand(100, 180, 360))},
    coords={
        "time": np.arange(100),
        "lat": np.linspace(-90, 90, 180),
        "lon": np.linspace(-180, 180, 360)
    }
)
ds_new.to_netcdf("output.nc")

# Lazy loading with Dask
ds_chunked = xr.open_dataset("large.nc", chunks={"time": 100})
'''
        )

        # GeoTIFF Libraries
        self.library_registry["rasterio"] = LibraryInfo(
            name="rasterio",
            description="Pythonic interface to GDAL for geospatial raster data including GeoTIFF",
            primary_domain=ScientificDomain.GEOSPATIAL,
            category=LibraryCategory.PRIMARY,
            license="BSD 3-Clause",
            python_native=False,  # GDAL bindings
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=2000,
            weekly_downloads=200000,
            read_support=True,
            write_support=True,
            streaming_support=True,
            compression_support=True,
            performance_rating="excellent",
            memory_efficiency="good",
            numpy_integration=True,
            xarray_integration=True,
            dask_integration=True,
            key_features=[
                "GeoTIFF and other formats",
                "Multi-band support",
                "Reprojection and warping",
                "Windowed reads",
                "CRS handling with pyproj",
                "COG (Cloud Optimized GeoTIFF) support"
            ],
            limitations=[
                "GDAL dependency",
                "Large binary installation",
                "Complex API for advanced operations"
            ],
            usage_example='''
import rasterio
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling

# Read GeoTIFF
with rasterio.open("dem.tif") as src:
    data = src.read(1)
    transform = src.transform
    crs = src.crs

# Reproject
with rasterio.open("input.tif") as src:
    transform, width, height = calculate_default_transform(
        src.crs, "EPSG:4326", src.width, src.height, *src.bounds
    )
    
# Write new raster
with rasterio.open("output.tif", "w", driver="GTiff",
                   height=height, width=width, count=1,
                   dtype=data.dtype, crs="EPSG:4326",
                   transform=transform) as dst:
    dst.write(data, 1)
'''
        )

        self.library_registry["rioxarray"] = LibraryInfo(
            name="rioxarray",
            description="Xarray extension for geospatial raster data with rio integration",
            primary_domain=ScientificDomain.GEOSPATIAL,
            category=LibraryCategory.UTILITY,
            license="MIT",
            python_native=True,
            maintenance_status="Active",
            last_updated="2024",
            popularity_stars=800,
            weekly_downloads=60000,
            read_support=True,
            write_support=True,
            streaming_support=True,
            compression_support=True,
            performance_rating="good",
            memory_efficiency="good",
            numpy_integration=True,
            xarray_integration=True,
            dask_integration=True,
            key_features=[
                "Xarray integration with rasterio",
                "CRS handling and reprojection",
                "Clip and mask operations",
                "Merge and combine operations",
                "COG detection and creation"
            ],
            limitations=[
                "Requires both rasterio and xarray",
                "Memory overhead from xarray",
                "Version compatibility issues"
            ],
            usage_example='''
import rioxarray
import xarray as xr

# Open GeoTIFF as xarray DataArray
da = rioxarray.open_rasterio("dem.tif")

# Proper xarray Dataset with CRS
ds = xr.open_rasterio("dem.tif")
ds = ds.rio.write_crs("EPSG:4326")
ds = ds.rio.set_spatial_dims(x_dim="x", y_dim="y")

# Clip to geometry
clipped = ds.rio.clip(geometries, from_disk=True)

# Write COG
da.rio.to_raster("output_cog.tif", driver="COG")
'''
        )

    def get_libraries_by_domain(self, domain: ScientificDomain) -> List[LibraryInfo]:
        """Get all libraries for a specific domain."""
        return [
            lib for lib in self.library_registry.values()
            if lib.primary_domain == domain
        ]

    def get_libraries_by_category(self, category: LibraryCategory) -> List[LibraryInfo]:
        """Get all libraries in a category."""
        return [
            lib for lib in self.library_registry.values()
            if lib.category == category
        ]

    def compare_dicom_libraries(self) -> LibraryComparison:
        """Compare DICOM libraries."""
        libraries = [
            self.library_registry["pydicom"],
            self.library_registry["simpleitk"],
            self.library_registry["dicom2nifti"],
        ]

        return LibraryComparison(
            use_case="DICOM Medical Imaging",
            domain=ScientificDomain.MEDICAL_IMAGING,
            libraries=libraries,
            recommendation="pydicom",
            alternative="simpleitk (for image processing)",
            comparison_matrix={
                "pydicom": {
                    "metadata_extraction": "Excellent",
                    "pixel_data": "Good",
                    "image_processing": "Limited",
                    "ease_of_use": "Easy",
                    "performance": "Good",
                    "community": "Large"
                },
                "simpleitk": {
                    "metadata_extraction": "Moderate",
                    "pixel_data": "Excellent",
                    "image_processing": "Excellent",
                    "ease_of_use": "Moderate",
                    "performance": "Excellent",
                    "community": "Large"
                },
                "dicom2nifti": {
                    "metadata_extraction": "Limited",
                    "pixel_data": "Good",
                    "image_processing": "Limited",
                    "ease_of_use": "Easy",
                    "performance": "Good",
                    "community": "Small"
                }
            }
        )

    def compare_fits_libraries(self) -> LibraryComparison:
        """Compare FITS libraries."""
        libraries = [
            self.library_registry["astropy"],
            self.library_registry["fitsio"],
        ]

        return LibraryComparison(
            use_case="FITS Astronomical Data",
            domain=ScientificDomain.ASTRONOMICAL,
            libraries=libraries,
            recommendation="astropy for general use, fitsio for performance",
            alternative="fitsio for large datasets",
            comparison_matrix={
                "astropy": {
                    "WCS_support": "Excellent",
                    "header_handling": "Excellent",
                    "table_operations": "Excellent",
                    "performance": "Good",
                    "ease_of_use": "Easy",
                    "integration": "Best"
                },
                "fitsio": {
                    "WCS_support": "Limited",
                    "header_handling": "Good",
                    "table_operations": "Good",
                    "performance": "Excellent",
                    "ease_of_use": "Moderate",
                    "integration": "Good"
                }
            }
        )

    def compare_hdf5_libraries(self) -> LibraryComparison:
        """Compare HDF5/NetCDF libraries."""
        libraries = [
            self.library_registry["h5py"],
            self.library_registry["netCDF4"],
            self.library_registry["xarray"],
        ]

        return LibraryComparison(
            use_case="HDF5/NetCDF Scientific Data",
            domain=ScientificDomain.GENERAL_SCIENTIFIC,
            libraries=libraries,
            recommendation="h5py for HDF5, xarray for netCDF",
            alternative="xarray for convenience with any format",
            comparison_matrix={
                "h5py": {
                    "HDF5_features": "Complete",
                    "netCDF_features": "None",
                    "ease_of_use": "Moderate",
                    "performance": "Excellent",
                    "dask_integration": "Yes",
                    "best_for": "General HDF5"
                },
                "netCDF4": {
                    "HDF5_features": "Good",
                    "netCDF_features": "Complete",
                    "ease_of_use": "Moderate",
                    "performance": "Good",
                    "dask_integration": "No",
                    "best_for": "Climate/weather data"
                },
                "xarray": {
                    "HDF5_features": "Via h5py",
                    "netCDF_features": "Complete",
                    "ease_of_use": "Easy",
                    "performance": "Good",
                    "dask_integration": "Yes",
                    "best_for": "Analysis workflows"
                }
            }
        )

    def compare_geotiff_libraries(self) -> LibraryComparison:
        """Compare GeoTIFF libraries."""
        libraries = [
            self.library_registry["rasterio"],
            self.library_registry["rioxarray"],
        ]

        return LibraryComparison(
            use_case="GeoTIFF Geospatial Rasters",
            domain=ScientificDomain.GEOSPATIAL,
            libraries=libraries,
            recommendation="rasterio for core operations, rioxarray for xarray integration",
            alternative="Use both together for best results",
            comparison_matrix={
                "rasterio": {
                    "basic_io": "Excellent",
                    "reprojection": "Excellent",
                    "crs_handling": "Good",
                    "xarray_integration": "Requires rioxarray",
                    "performance": "Excellent",
                    "ease_of_use": "Moderate"
                },
                "rioxarray": {
                    "basic_io": "Good",
                    "reprojection": "Excellent",
                    "crs_handling": "Excellent",
                    "xarray_integration": "Native",
                    "performance": "Good",
                    "ease_of_use": "Easy"
                }
            }
        )

    def generate_recommendations(self) -> Dict[str, Any]:
        """Generate comprehensive recommendations."""
        recommendations = {
            "metadata_extraction": {
                "dicom": {
                    "recommended": "pydicom",
                    "reason": "Complete DICOM standard support, excellent metadata extraction, simple API",
                    "install": "pip install pydicom"
                },
                "fits": {
                    "recommended": "astropy",
                    "reason": "Best WCS and header support, active development",
                    "install": "pip install astropy"
                },
                "hdf5": {
                    "recommended": "h5py",
                    "reason": "Standard Python interface, excellent performance",
                    "install": "pip install h5py"
                },
                "netcdf": {
                    "recommended": "netCDF4 or xarray",
                    "reason": "xarray provides best API with netCDF4 backend",
                    "install": "pip install netCDF4 xarray"
                },
                "geotiff": {
                    "recommended": "rasterio",
                    "reason": "Pythonic GDAL interface, excellent performance",
                    "install": "pip install rasterio"
                }
            },
            "performance_priority": {
                "dicom": {
                    "library": "pydicom",
                    "tips": [
                        "Use lazy loading for large series",
                        "Decompress outside pydicom for speed",
                        "Cache parsed files"
                    ]
                },
                "fits": {
                    "library": "fitsio",
                    "tips": [
                        "Use memory mapping for large files",
                        "Enable tile compression for writes",
                        "Use streaming reads for huge datasets"
                    ]
                },
                "hdf5": {
                    "library": "h5py",
                    "tips": [
                        "Use chunked datasets for large data",
                        "Enable compression (gzip level 4-6)",
                        "Use hyperslab selection for partial reads"
                    ]
                },
                "geotiff": {
                    "library": "rasterio",
                    "tips": [
                        "Use windowed reads for large files",
                        "Create COGs for cloud access",
                        "Enable lz4 compression for speed"
                    ]
                }
            },
            "ease_of_use": {
                "dicom": "pydicom",
                "fits": "astropy",
                "hdf5": "xarray",
                "netcdf": "xarray",
                "geotiff": "rioxarray"
            },
            "feature_comparison": {
                "medical_imaging": {
                    "metadata": "pydicom",
                    "processing": "simpleitk",
                    "conversion": "dicom2nifti",
                    "all_in_one": "simpleitk"
                },
                "astronomy": {
                    "metadata": "astropy",
                    "performance": "fitsio",
                    "analysis": "astropy + photutils"
                },
                "climate": {
                    "netcdf": "xarray + netCDF4",
                    "hdf5": "h5py + xarray",
                    "analysis": "xarray"
                },
                "geospatial": {
                    "core": "rasterio",
                    "analysis": "rioxarray + xarray",
                    "visualization": "matplotlib + cartopy"
                }
            }
        }
        return recommendations

    def get_installation_summary(self) -> Dict[str, List[str]]:
        """Get installation commands for all libraries."""
        return {
            "core_dicom": [
                "pip install pydicom",
                "pip install simpleitk",
                "pip install dicom2nifti"
            ],
            "core_fits": [
                "pip install astropy",
                "pip install fitsio"
            ],
            "core_hdf5": [
                "pip install h5py",
                "pip install netCDF4",
                "pip install xarray"
            ],
            "core_geospatial": [
                "pip install rasterio",
                "pip install rioxarray",
                "pip install pyproj"
            ],
            "recommended_metaextract": [
                "pip install pydicom",
                "pip install astropy",
                "pip install h5py",
                "pip install netCDF4",
                "pip install xarray",
                "pip install rasterio",
                "pip install rioxarray"
            ]
        }

    def get_research_report(self) -> Dict[str, Any]:
        """Generate comprehensive research report."""
        return {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "version": "1.0.0",
                "domains_covered": [d.value for d in ScientificDomain]
            },
            "library_overviews": {
                "dicom_libraries": {
                    "pydicom": self._lib_to_dict(self.library_registry["pydicom"]),
                    "simpleitk": self._lib_to_dict(self.library_registry["simpleitk"]),
                    "dicom2nifti": self._lib_to_dict(self.library_registry["dicom2nifti"])
                },
                "fits_libraries": {
                    "astropy": self._lib_to_dict(self.library_registry["astropy"]),
                    "fitsio": self._lib_to_dict(self.library_registry["fitsio"])
                },
                "hdf5_libraries": {
                    "h5py": self._lib_to_dict(self.library_registry["h5py"]),
                    "netCDF4": self._lib_to_dict(self.library_registry["netCDF4"]),
                    "xarray": self._lib_to_dict(self.library_registry["xarray"])
                },
                "geotiff_libraries": {
                    "rasterio": self._lib_to_dict(self.library_registry["rasterio"]),
                    "rioxarray": self._lib_to_dict(self.library_registry["rioxarray"])
                }
            },
            "comparisons": {
                "dicom": self.compare_dicom_libraries().__dict__,
                "fits": self.compare_fits_libraries().__dict__,
                "hdf5": self.compare_hdf5_libraries().__dict__,
                "geotiff": self.compare_geotiff_libraries().__dict__
            },
            "recommendations": self.generate_recommendations(),
            "installation": self.get_installation_summary()
        }

    def _lib_to_dict(self, lib: LibraryInfo) -> Dict[str, Any]:
        """Convert LibraryInfo to dictionary."""
        return {
            "name": lib.name,
            "description": lib.description,
            "domain": lib.primary_domain.value,
            "category": lib.category.value,
            "license": lib.license,
            "python_native": lib.python_native,
            "maintenance": lib.maintenance_status,
            "performance": lib.performance_rating,
            "features": lib.key_features,
            "limitations": lib.limitations
        }

    def print_summary(self):
        """Print human-readable summary."""
        print("\n" + "=" * 80)
        print("SCIENTIFIC LIBRARY RESEARCH REPORT")
        print("=" * 80)

        print("\n📋 DICOM Libraries")
        print("-" * 40)
        print("Primary:     pydicom (metadata extraction)")
        print("Processing:  SimpleITK (image processing)")
        print("Conversion:  dicom2nifti (DICOM → NIfTI)")

        print("\n📋 FITS Libraries")
        print("-" * 40)
        print("Primary:     astropy (WCS, analysis, ease of use)")
        print("Performance: fitsio (speed for large files)")

        print("\n📋 HDF5/NetCDF Libraries")
        print("-" * 40)
        print("HDF5:        h5py (core interface)")
        print("NetCDF:      xarray + netCDF4 (best API)")
        print("Analysis:    xarray (labeled arrays)")

        print("\n📋 GeoTIFF Libraries")
        print("-" * 40)
        print("Core:        rasterio (GDAL interface)")
        print("Integration: rioxarray (xarray integration)")

        print("\n🏆 Recommendations by Priority")
        print("-" * 40)
        recs = self.generate_recommendations()["metadata_extraction"]
        for fmt, info in recs.items():
            print(f"  {fmt.upper()}: {info['recommended']}")

        print("\n📦 Installation")
        print("-" * 40)
        print("  pip install pydicom astropy h5py netCDF4 xarray rasterio rioxarray")
        print("\n" + "=" * 80)


def main():
    """Main entry point for research report generation."""
    agent = ScientificLibraryResearchAgent()

    # Print summary
    agent.print_summary()

    # Generate full report
    report = agent.get_research_report()

    # Save to JSON
    with open("scientific_library_research_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("\nFull report saved to: scientific_library_research_report.json")


if __name__ == "__main__":
    main()
