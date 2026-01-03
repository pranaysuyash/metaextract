#!/usr/bin/env python3
"""
Testing Infrastructure Agent
Creates comprehensive test datasets for scientific formats:
- DICOM (CT, MR, US, CR, XA)
- FITS (astronomical surveys, WCS)
- HDF5/NetCDF (climate, oceanographic)
- GeoTIFF (DEM, satellite imagery)

Author: MetaExtract Team
Version: 1.0.0
"""

import hashlib
import json
import os
import struct
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Type
import logging

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    CT = "CT"   # Computed Tomography
    MR = "MR"   # Magnetic Resonance
    US = "US"   # Ultrasound
    CR = "CR"   # Computed Radiography
    XA = "XA"   # X-Ray Angiography
    MG = "MG"   # Mammography
    NM = "NM"   # Nuclear Medicine
    PT = "PT"   # Positron Emission Tomography


class FITSExtension(Enum):
    PRIMARY = "primary"
    IMAGE = "image"
    BINARY_TABLE = "binary_table"
    ASCII_TABLE = "ascii_table"


class HDF5DatasetType(Enum):
    SCALAR = "scalar"
    ARRAY_1D = "array_1d"
    ARRAY_2D = "array_2d"
    ARRAY_3D = "array_3d"
    COMPRESSED = "compressed"
    CHUNKED = "chunked"


class GeoTIFFType(Enum):
    DEM = "dem"
    SATELLITE = "satellite"
    AERIAL = "aerial"
    MULTISPECTRAL = "multispectral"
    COG = "cog"


@dataclass
class TestDataset:
    """Metadata about a generated test dataset."""
    filename: str
    file_format: str
    modality_type: Optional[str]
    file_size_bytes: int
    file_hash: str
    generated_at: str
    dimensions: Tuple[int, ...]
    metadata_fields: List[str]
    validation_status: str
    notes: str


@dataclass
class TestSuite:
    """Collection of test datasets for a specific format."""
    suite_name: str
    description: str
    formats_covered: List[str]
    total_datasets: int
    datasets: List[TestDataset]
    generated_at: str


class DICOMTestGenerator:
    """Generates synthetic DICOM test files for various modalities."""

    def __init__(self):
        self.uid_counters = {}
        self.patient_names = [
            "Test^Patient001", "Test^Patient002", "Test^Patient003",
            "Demo^Subject^A", "Demo^Subject^B", "QC^Phantom"
        ]
        self.manufacturers = ["GE Healthcare", "Siemens", "Philips", "Canon", "TestManufacturer"]

    def _generate_uid(self, prefix: str = "1.2.840.10008") -> str:
        """Generate a DICOM UID."""
        if prefix not in self.uid_counters:
            self.uid_counters[prefix] = 0
        self.uid_counters[prefix] += 1
        root = "1.2.826.0.1.3680043.10.2024"
        return f"{root}.{self.uid_counters[prefix]}.{uuid.uuid4().int % 1000000}"

    def _generate_header_bytes(
        self,
        modality: str,
        rows: int,
        cols: int,
        bits_allocated: int = 16,
        pixel_representation: int = 0
    ) -> bytes:
        """Generate minimal DICOM header bytes."""
        header = bytearray(1024)

        # DICOM preamble + magic
        header[0:128] = b'\x00' * 128
        header[128:132] = b'DICM'

        # Tag: (0008,0016) SOP Class UID
        header[132:140] = struct.pack('<HH', 0x0008, 0x0016)
        header[140:142] = struct.pack('>H', 24)  # VR length
        header[142:166] = self._generate_uid("1.2.840.10008").encode()

        # Tag: (0008,0018) SOP Instance UID
        header[166:174] = struct.pack('<HH', 0x0008, 0x0018)
        header[174:176] = struct.pack('>H', 24)
        header[176:200] = self._generate_uid().encode()

        # Tag: (0008,0020) Study Date
        header[200:208] = struct.pack('<HH', 0x0008, 0x0020)
        header[208:210] = struct.pack('>H', 8)
        header[210:218] = datetime.now().strftime("%Y%m%d").encode()

        # Tag: (0008,0060) Modality
        header[218:226] = struct.pack('<HH', 0x0008, 0x0060)
        header[226:228] = struct.pack('>H', 2)
        header[228:230] = modality.encode()

        # Tag: (0028,0010) Rows
        header[230:238] = struct.pack('<HH', 0x0028, 0x0010)
        header[238:240] = struct.pack('>H', 2)
        header[240:242] = struct.pack('>H', rows)

        # Tag: (0028,0011) Columns
        header[242:250] = struct.pack('<HH', 0x0028, 0x0011)
        header[250:252] = struct.pack('>H', 2)
        header[252:254] = struct.pack('>H', cols)

        return bytes(header[:512])

    def generate_ct_scan(
        self,
        output_dir: str,
        num_slices: int = 10,
        rows: int = 512,
        cols: int = 512,
        series_description: str = "Test CT Series"
    ) -> List[TestDataset]:
        """Generate synthetic CT scan DICOM files."""
        datasets = []
        series_uid = self._generate_uid()

        for i in range(num_slices):
            filename = f"CT_{series_description.replace(' ', '_')}_{i+1:04d}.dcm"
            filepath = os.path.join(output_dir, filename)

            # Generate header
            header = self._generate_header_bytes("CT", rows, cols)

            # Generate pixel data (simulated CT values)
            pixel_bytes = rows * cols * 2  # 16-bit
            import random
            random.seed(i)
            # Generate random 16-bit integers for CT-like pixel data
            pixels = b''.join(
                struct.pack('<h', random.randint(-1000, 3000))
                for _ in range(rows * cols)
            )

            with open(filepath, 'wb') as f:
                f.write(header)
                f.write(pixels)

            datasets.append(TestDataset(
                filename=filename,
                file_format="dicom",
                modality_type="CT",
                file_size_bytes=len(header) + len(pixels),
                file_hash=hashlib.md5(header + pixels).hexdigest(),
                generated_at=datetime.utcnow().isoformat() + "Z",
                dimensions=(rows, cols),
                metadata_fields=["SOPClassUID", "SOPInstanceUID", "StudyDate", "Modality", "Rows", "Columns"],
                validation_status="generated",
                notes=f"Slice {i+1} of {num_slices} - {series_description}"
            ))

        return datasets

    def generate_mr_sequence(
        self,
        output_dir: str,
        num_slices: int = 20,
        rows: int = 256,
        cols: int = 256,
        sequence_name: str = "T1_AXIAL"
    ) -> List[TestDataset]:
        """Generate synthetic MR sequence DICOM files."""
        datasets = []
        series_uid = self._generate_uid()

        for i in range(num_slices):
            filename = f"MR_{sequence_name}_{i+1:04d}.dcm"
            filepath = os.path.join(output_dir, filename)

            header = self._generate_header_bytes("MR", rows, cols)

            # Generate MR-like pixel data
            import random
            random.seed(i + 1000)
            pixels = b''.join(
                struct.pack('<H', random.randint(0, 4095))
                for _ in range(rows * cols)
            )

            with open(filepath, 'wb') as f:
                f.write(header)
                f.write(pixels)

            datasets.append(TestDataset(
                filename=filename,
                file_format="dicom",
                modality_type="MR",
                file_size_bytes=len(header) + len(pixels),
                file_hash=hashlib.md5(header + pixels).hexdigest(),
                generated_at=datetime.utcnow().isoformat() + "Z",
                dimensions=(rows, cols),
                metadata_fields=["SOPClassUID", "SOPInstanceUID", "Modality", "Rows", "Columns", "Sequence"],
                validation_status="generated",
                notes=f"MR {sequence_name} slice {i+1}"
            ))

        return datasets

    def generate_ultrasound(
        self,
        output_dir: str,
        num_frames: int = 5,
        rows: int = 480,
        cols: int = 640
    ) -> List[TestDataset]:
        """Generate synthetic ultrasound DICOM files."""
        datasets = []

        for i in range(num_frames):
            filename = f"US_Frame_{i+1:04d}.dcm"
            filepath = os.path.join(output_dir, filename)

            header = self._generate_header_bytes("US", rows, cols)

            import random
            random.seed(i + 2000)
            pixels = bytes(random.randint(0, 255) for _ in range(rows * cols))

            with open(filepath, 'wb') as f:
                f.write(header)
                f.write(pixels)

            datasets.append(TestDataset(
                filename=filename,
                file_format="dicom",
                modality_type="US",
                file_size_bytes=len(header) + len(pixels),
                file_hash=hashlib.md5(header + pixels).hexdigest(),
                generated_at=datetime.utcnow().isoformat() + "Z",
                dimensions=(rows, cols),
                metadata_fields=["SOPClassUID", "Modality", "Rows", "Columns"],
                validation_status="generated",
                notes=f"Ultrasound frame {i+1}"
            ))

        return datasets


class FITSTestGenerator:
    """Generates synthetic FITS test files for astronomical data."""

    def generate_primary_hdu(
        self,
        output_dir: str,
        shape: Tuple[int, ...],
        bitpix: int = -64,
        name: str = "primary_test"
    ) -> TestDataset:
        """Generate FITS file with primary HDU."""
        filename = f"{name}.fits"
        filepath = os.path.join(output_dir, filename)

        # FITS header for primary HDU
        header_lines = [
            "SIMPLE  =                    T / conforms to FITS standard",
            f"BITPIX  =                   {bitpix} / number of bits per data pixel",
            f"NAXIS   =                    {len(shape)} / number of data axes",
            f"NAXIS1  =                 {shape[-1]}" if len(shape) >= 1 else "NAXIS1  =                    0",
            f"NAXIS2  =                 {shape[-2]}" if len(shape) >= 2 else "NAXIS2  =                    0",
            f"NAXIS3  =                 {shape[-3]}" if len(shape) >= 3 else "NAXIS3  =                    0",
            f"OBJECT  = '{name}'           / name of observed object",
            f"DATE-OBS= '2024-01-15'       / date of observation",
            "TELESCOP= 'Test Telescope'   / name of telescope",
            "INSTRUME= 'Test Camera'      / name of instrument",
            "END"
        ]

        # Pad header to 2880 bytes
        header_block = ""
        for line in header_lines:
            header_block += line.ljust(80)
        while len(header_block) % 2880 != 0:
            header_block += " " * 80

        header_bytes = header_block.encode('ascii')

        # Generate pixel data without numpy
        import random
        import struct

        total_pixels = 1
        for dim in shape:
            total_pixels *= dim

        # Generate float64 data
        random.seed(42)
        data_bytes = b''.join(
            struct.pack('<d', random.gauss(0, 1))
            for _ in range(total_pixels)
        )

        # Pad data to block boundary
        while len(data_bytes) % 2880 != 0:
            data_bytes += b'\x00'

        with open(filepath, 'wb') as f:
            f.write(header_bytes)
            f.write(data_bytes)

        return TestDataset(
            filename=filename,
            file_format="fits",
            modality_type="primary",
            file_size_bytes=len(header_bytes) + len(data_bytes),
            file_hash=hashlib.md5(header_bytes + data_bytes).hexdigest(),
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=shape,
            metadata_fields=["SIMPLE", "BITPIX", "NAXIS", "OBJECT", "DATE-OBS", "TELESCOP"],
            validation_status="generated",
            notes=f"FITS primary HDU {name}, shape {shape}"
        )

    def generate_with_wcs(
        self,
        output_dir: str,
        shape: Tuple[int, int] = (1024, 1024),
        name: str = "wcs_test"
    ) -> TestDataset:
        """Generate FITS file with World Coordinate System."""
        filename = f"{name}.fits"
        filepath = os.path.join(output_dir, filename)

        # FITS header with WCS
        header_lines = [
            "SIMPLE  =                    T / conforms to FITS standard",
            "BITPIX  =                   -64 / number of bits per data pixel",
            "NAXIS   =                    2 / number of data axes",
            f"NAXIS1  =                 {shape[1]}",
            f"NAXIS2  =                 {shape[0]}",
            "OBJECT  = 'M31'              / Andromeda Galaxy",
            "DATE-OBS= '2024-01-15T02:30:00' / observation date",
            "TELESCOP= 'Test Telescope'",
            "CRPIX1  =                512.0 / reference pixel",
            "CRPIX2  =                512.0 / reference pixel",
            "CRVAL1  =                 10.68 / reference value (RA)",
            "CRVAL2  =                 41.27 / reference value (Dec)",
            "CDELT1  =              -0.00028 / degrees per pixel",
            "CDELT2  =               0.00028 / degrees per pixel",
            "CTYPE1  = 'RA---TAN'         / projection type",
            "CTYPE2  = 'DEC--TAN'         / projection type",
            "CROTA2  =                 0.0 / rotation angle",
            "END"
        ]

        # Pad header
        header_block = ""
        for line in header_lines:
            header_block += line.ljust(80)
        while len(header_block) % 2880 != 0:
            header_block += " " * 80
        header_bytes = header_block.encode('ascii')

        # Generate pixel data with simple pattern (no numpy)
        import random
        import math
        import struct

        random.seed(42)
        center_y, center_x = shape[0] // 2, shape[1] // 2
        data_bytes = b''
        for y in range(shape[0]):
            for x in range(shape[1]):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                value = math.exp(-dist/200) * 1000 + random.gauss(0, 10)
                data_bytes += struct.pack('<d', value)

        while len(data_bytes) % 2880 != 0:
            data_bytes += b'\x00'

        with open(filepath, 'wb') as f:
            f.write(header_bytes)
            f.write(data_bytes)

        return TestDataset(
            filename=filename,
            file_format="fits",
            modality_type="wcs",
            file_size_bytes=len(header_bytes) + len(data_bytes),
            file_hash=hashlib.md5(header_bytes + data_bytes).hexdigest(),
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=shape,
            metadata_fields=["SIMPLE", "BITPIX", "NAXIS", "OBJECT", "CRPIX1", "CRPIX2", "CRVAL1", "CRVAL2", "CDELT1", "CDELT2", "CTYPE1", "CTYPE2"],
            validation_status="generated",
            notes=f"FITS with WCS - Andromeda simulation"
        )

    def generate_binary_table(
        self,
        output_dir: str,
        num_rows: int = 100,
        name: str = "catalog_test"
    ) -> TestDataset:
        """Generate FITS file with binary table extension."""
        filename = f"{name}.fits"
        filepath = os.path.join(output_dir, filename)

        # Primary HDU (empty)
        primary_header = b"SIMPLE  =                    T / conforms to FITS standard                         BITPIX  =                    8 / number of bits per data pixel                     NAXIS   =                    0 / number of data axes                            NAXIS1  =                    0 / length of data axis 1                          NAXIS2  =                    0 / length of data axis 2                          END"
        primary_header = primary_header.ljust(2880, b' ')

        # Create table data without numpy
        import random
        import struct

        random.seed(42)
        table_data = b''
        for i in range(1, num_rows + 1):
            # ID (int32)
            table_data += struct.pack('<i', i)
            # RA (float64)
            table_data += struct.pack('<d', random.uniform(0, 360))
            # Dec (float64)
            table_data += struct.pack('<d', random.uniform(-90, 90))
            # Mag (float32)
            table_data += struct.pack('<f', random.uniform(10, 20))

        header_lines = [
            "XTENSION= 'BINARYTABLE'           / marks beginning of table",
            f"BITPIX  =                    8 / 8-bit bytes",
            f"NAXIS   =                    2 / table is 2-D",
            f"NAXIS1  =                   {4*4} / width of table in bytes",
            f"NAXIS2  =                  {num_rows} / number of rows in table",
            "TFIELDS =                    4 / number of columns",
            "TTYPE1  = 'ID       '           / column name",
            "TFORM1  = '1J       '           / column format",
            "TTYPE2  = 'RA       '           / column name",
            "TFORM2  = '1D       '           / column format",
            "TTYPE3  = 'DEC      '           / column name",
            "TFORM3  = '1D       '           / column format",
            "TTYPE4  = 'MAG      '           / column name",
            "TFORM4  = '1E       '           / column format",
            "EXTNAME = 'CATALOG  '           / table name",
            "END"
        ]

        header_block = ""
        for line in header_lines:
            header_block += line.ljust(80)
        while len(header_block) % 2880 != 0:
            header_block += " " * 80
        table_header = header_block.encode('ascii')

        while len(table_data) % 2880 != 0:
            table_data += b'\x00'

        with open(filepath, 'wb') as f:
            f.write(primary_header)
            f.write(table_header)
            f.write(table_data)

        return TestDataset(
            filename=filename,
            file_format="fits",
            modality_type="binary_table",
            file_size_bytes=2880 + len(table_header) + len(table_data),
            file_hash=hashlib.md5(table_data).hexdigest(),
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=(num_rows, 4),
            metadata_fields=["XTENSION", "NAXIS1", "NAXIS2", "TFIELDS", "TTYPE1-4", "EXTNAME"],
            validation_status="generated",
            notes=f"FITS binary table with {num_rows} star catalog entries"
        )


class HDF5NetCDFTestGenerator:
    """Generates synthetic HDF5 and netCDF test datasets."""

    def generate_hdf5_climate(
        self,
        output_dir: str,
        shape: Tuple[int, int, int] = (365, 180, 360),
        name: str = "climate_data"
    ) -> TestDataset:
        """Generate HDF5 file with climate-like data."""
        try:
            import numpy as np
            import h5py
        except ImportError:
            logger.warning("numpy/h5py not available, skipping HDF5 climate test")
            return None

        filename = f"{name}.h5"
        filepath = os.path.join(output_dir, filename)

        np.random.seed(42)
        data = np.random.randn(*shape).astype(np.float32)

        with h5py.File(filepath, 'w') as f:
            f.create_dataset("temperature", data=data, chunks=True, compression="gzip", compression_opts=4)
            f.create_dataset("time", data=np.arange(shape[0]))
            f.create_dataset("lat", data=np.linspace(-90, 90, shape[1]))
            f.create_dataset("lon", data=np.linspace(-180, 180, shape[2]))
            f["temperature"].attrs["units"] = "kelvin"
            f["temperature"].attrs["long_name"] = "Surface Temperature"
            f["temperature"].attrs["missing_value"] = -9999.0
            f.attrs["title"] = "Synthetic Climate Dataset"

        return TestDataset(
            filename=filename,
            file_format="hdf5",
            modality_type="climate",
            file_size_bytes=os.path.getsize(filepath),
            file_hash="generated",
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=shape,
            metadata_fields=["temperature", "time", "lat", "lon"],
            validation_status="generated",
            notes=f"HDF5 climate data shape {shape}"
        )

    def generate_hdf5_multiscale(
        self,
        output_dir: str,
        base_shape: Tuple[int, int] = (1024, 1024),
        name: str = "multiscale_image"
    ) -> TestDataset:
        """Generate HDF5 with multiscale image data."""
        try:
            import numpy as np
            import h5py
        except ImportError:
            logger.warning("numpy/h5py not available, skipping HDF5 multiscale test")
            return None

        filename = f"{name}.h5"
        filepath = os.path.join(output_dir, filename)

        with h5py.File(filepath, 'w') as f:
            data = np.random.randint(0, 256, base_shape, dtype=np.uint8)
            f.create_dataset("data/level_0", data=data)
            current = data
            for level in range(1, 3):  # Reduced levels for testing
                current = current[::2, ::2]
                f.create_dataset(f"data/level_{level}", data=current)
            f.attrs["num_levels"] = 3
            f.attrs["base_shape"] = base_shape

        return TestDataset(
            filename=filename,
            file_format="hdf5",
            modality_type="multiscale",
            file_size_bytes=os.path.getsize(filepath),
            file_hash="generated",
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=base_shape,
            metadata_fields=["num_levels", "base_shape", "data/level_0"],
            validation_status="generated",
            notes=f"HDF5 image pyramid {base_shape}"
        )

    def generate_netcdf_oceanographic(
        self,
        output_dir: str,
        shape: Tuple[int, int, int] = (100, 180, 360),
        name: str = "ocean_data"
    ) -> TestDataset:
        """Generate netCDF file with oceanographic data."""
        try:
            import numpy as np
            from netCDF4 import Dataset
        except ImportError:
            logger.warning("netCDF4/numpy not available, skipping oceanographic test")
            return None

        filename = f"{name}.nc"
        filepath = os.path.join(output_dir, filename)

        time = np.arange(shape[0])
        lat = np.linspace(-90, 90, shape[1])
        lon = np.linspace(-180, 180, shape[2])

        with Dataset(filepath, 'w') as nc:
            nc.createDimension("time", None)
            nc.createDimension("lat", shape[1])
            nc.createDimension("lon", shape[2])
            time_var = nc.createVariable("time", "f8", ("time",))
            time_var[:] = time
            time_var.units = "days since 2000-01-01"
            lat_var = nc.createVariable("lat", "f8", ("lat",))
            lat_var[:] = lat
            lat_var.units = "degrees_north"
            lon_var = nc.createVariable("lon", "f8", ("lon",))
            lon_var[:] = lon
            lon_var.units = "degrees_east"
            sst = nc.createVariable("sea_surface_temperature", "f4", ("time", "lat", "lon"))
            sst[:] = np.random.rand(*shape).astype(np.float32) * 30
            sst.units = "degrees_C"
            sst.missing_value = -9999.0
            nc.title = "Synthetic Oceanographic Dataset"

        return TestDataset(
            filename=filename,
            file_format="netcdf",
            modality_type="oceanographic",
            file_size_bytes=os.path.getsize(filepath),
            file_hash="generated",
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=shape,
            metadata_fields=["sea_surface_temperature", "time", "lat", "lon"],
            validation_status="generated",
            notes=f"netCDF ocean data shape {shape}"
        )


class GeoTIFFTestGenerator:
    """Generates synthetic GeoTIFF test files."""

    def generate_dem(
        self,
        output_dir: str,
        shape: Tuple[int, int] = (1000, 1000),
        name: str = "dem_test"
    ) -> TestDataset:
        """Generate DEM (Digital Elevation Model) GeoTIFF."""
        try:
            import rasterio
            from rasterio.transform import Affine
        except ImportError:
            logger.warning("rasterio not available, skipping DEM test generation")
            return None

        filename = f"{name}.tif"
        filepath = os.path.join(output_dir, filename)

        # Generate simple elevation data (no numpy/scipy required)
        import random
        random.seed(42)
        elevation_base = 500 + random.randint(0, 1000)  # Base elevation 500-1500m

        # Create a simple height map without numpy
        transform = Affine.translation(-180, 90) * Affine.scale(360/shape[1], -180/shape[0])

        # Create simple data array manually
        try:
            import numpy as np
            base = np.full(shape, elevation_base, dtype=np.float32)
            # Add some variation
            for y in range(shape[0]):
                for x in range(shape[1]):
                    base[y, x] += (y * shape[1] + x) % 100
        except ImportError:
            logger.warning("numpy not available, skipping DEM test generation")
            return None

        with rasterio.open(
            filepath, 'w',
            driver='GTiff',
            height=shape[0],
            width=shape[1],
            count=1,
            dtype=np.float32,
            crs='EPSG:4326',
            transform=transform,
            nodata=-9999,
            compress='lzw'
        ) as dst:
            dst.write(base.astype(np.float32), 1)

        return TestDataset(
            filename=filename,
            file_format="geotiff",
            modality_type="dem",
            file_size_bytes=os.path.getsize(filepath),
            file_hash="generated",
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=shape,
            metadata_fields=["crs", "transform", "nodata", "compression"],
            validation_status="generated",
            notes=f"GeoTIFF DEM shape {shape}"
        )

    def generate_satellite(
        self,
        output_dir: str,
        bands: int = 4,
        shape: Tuple[int, int] = (512, 512),
        name: str = "satellite_test"
    ) -> TestDataset:
        """Generate multi-band satellite imagery GeoTIFF."""
        try:
            import rasterio
            from rasterio.transform import Affine
        except ImportError:
            return None

        try:
            import numpy as np
        except ImportError:
            logger.warning("numpy not available, skipping satellite test")
            return None

        filename = f"{name}.tif"
        filepath = os.path.join(output_dir, filename)

        np.random.seed(42)
        data = np.random.randint(0, 10000, (bands, shape[0], shape[1]), dtype=np.uint16)

        transform = Affine.translation(0, 0) * Affine.scale(0.001, -0.001)

        with rasterio.open(
            filepath, 'w',
            driver='GTiff',
            height=shape[0],
            width=shape[1],
            count=bands,
            dtype=np.uint16,
            crs='EPSG:4326',
            transform=transform,
            compress='lzw',
            photometric='ycbcr'
        ) as dst:
            for i in range(bands):
                dst.write(data[i].astype(np.uint16), i + 1)

        return TestDataset(
            filename=filename,
            file_format="geotiff",
            modality_type="satellite",
            file_size_bytes=os.path.getsize(filepath),
            file_hash="generated",
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=(bands, shape[0], shape[1]),
            metadata_fields=["crs", "transform", "bands", "photometric"],
            validation_status="generated",
            notes=f"GeoTIFF satellite {bands}-band shape {shape}"
        )

    def generate_cog(
        self,
        output_dir: str,
        shape: Tuple[int, int] = (2048, 2048),
        name: str = "cog_test"
    ) -> TestDataset:
        """Generate Cloud Optimized GeoTIFF."""
        filename = f"{name}.tif"
        filepath = os.path.join(output_dir, filename)

        try:
            import rasterio
        except ImportError:
            return None

        import numpy as np

        np.random.seed(42)
        data = np.random.randint(0, 256, shape, dtype=np.uint8)

        transform = Affine.translation(0, 0) * Affine.scale(0.01, -0.01)

        with rasterio.open(
            filepath, 'w',
            driver='GTiff',
            height=shape[0],
            width=shape[1],
            count=1,
            dtype=np.uint8,
            crs='EPSG:4326',
            transform=transform,
            compress='lzw',
            blocksize=512,
            overview_levels=[2, 4, 8]
        ) as dst:
            dst.write(data, 1)
            dst.build_overviews([2, 4, 8])

        return TestDataset(
            filename=filename,
            file_format="cog",
            modality_type="cog",
            file_size_bytes=os.path.getsize(filepath),
            file_hash="generated",
            generated_at=datetime.utcnow().isoformat() + "Z",
            dimensions=shape,
            metadata_fields=["crs", "transform", "blocksize", "overviews"],
            validation_status="generated",
            notes=f"COG shape {shape} with overviews"
        )


class TestInfrastructureAgent:
    """Main agent for managing test infrastructure."""

    def __init__(self, output_dir: str = "test_datasets"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.dicom_gen = DICOMTestGenerator()
        self.fits_gen = FITSTestGenerator()
        self.hdf5_gen = HDF5NetCDFTestGenerator()
        self.geotiff_gen = GeoTIFFTestGenerator()

        self.generated_suites: List[TestSuite] = []

    def generate_dicom_suite(self) -> TestSuite:
        """Generate complete DICOM test suite."""
        datasets = []

        # CT scan
        ct_dir = os.path.join(self.output_dir, "dicom/ct")
        os.makedirs(ct_dir, exist_ok=True)
        datasets.extend(self.dicom_gen.generate_ct_scan(ct_dir, num_slices=5, rows=128, cols=128))

        # MR sequence
        mr_dir = os.path.join(self.output_dir, "dicom/mr")
        os.makedirs(mr_dir, exist_ok=True)
        datasets.extend(self.dicom_gen.generate_mr_sequence(mr_dir, num_slices=3, rows=64, cols=64))

        # Ultrasound
        us_dir = os.path.join(self.output_dir, "dicom/us")
        os.makedirs(us_dir, exist_ok=True)
        datasets.extend(self.dicom_gen.generate_ultrasound(us_dir, num_frames=2, rows=100, cols=100))

        suite = TestSuite(
            suite_name="dicom_test_suite",
            description="Synthetic DICOM files for CT, MR, and Ultrasound modalities",
            formats_covered=["dicom/CT", "dicom/MR", "dicom/US"],
            total_datasets=len(datasets),
            datasets=datasets,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )
        self.generated_suites.append(suite)
        return suite

    def generate_fits_suite(self) -> TestSuite:
        """Generate complete FITS test suite."""
        fits_dir = os.path.join(self.output_dir, "fits")
        os.makedirs(fits_dir, exist_ok=True)

        datasets = [
            self.fits_gen.generate_primary_hdu(fits_dir, (256, 256), name="primary_2d"),
            self.fits_gen.generate_primary_hdu(fits_dir, (50, 256, 256), name="primary_3d"),
            self.fits_gen.generate_with_wcs(fits_dir, (512, 512), name="wcs_astronomy"),
            self.fits_gen.generate_binary_table(fits_dir, num_rows=50, name="binary_catalog"),
        ]

        suite = TestSuite(
            suite_name="fits_test_suite",
            description="Synthetic FITS files for astronomical data including WCS",
            formats_covered=["fits/primary", "fits/wcs", "fits/binary_table"],
            total_datasets=len(datasets),
            datasets=datasets,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )
        self.generated_suites.append(suite)
        return suite

    def generate_hdf5_suite(self) -> TestSuite:
        """Generate HDF5/netCDF test suite."""
        hdf5_dir = os.path.join(self.output_dir, "hdf5")
        os.makedirs(hdf5_dir, exist_ok=True)

        datasets = [
            self.hdf5_gen.generate_hdf5_climate(hdf5_dir, (10, 18, 36), name="climate_small"),
            self.hdf5_gen.generate_hdf5_multiscale(hdf5_dir, (256, 256), name="multiscale"),
        ]

        nc_result = self.hdf5_gen.generate_netcdf_oceanographic(hdf5_dir, (10, 18, 36), name="ocean_small")
        if nc_result:
            datasets.append(nc_result)

        suite = TestSuite(
            suite_name="hdf5_netcdf_test_suite",
            description="Synthetic HDF5 and netCDF files for climate/oceanographic data",
            formats_covered=["hdf5/climate", "hdf5/multiscale", "netcdf/oceanographic"],
            total_datasets=len(datasets),
            datasets=datasets,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )
        self.generated_suites.append(suite)
        return suite

    def generate_geotiff_suite(self) -> TestSuite:
        """Generate GeoTIFF test suite."""
        geotiff_dir = os.path.join(self.output_dir, "geotiff")
        os.makedirs(geotiff_dir, exist_ok=True)

        datasets = []

        dem = self.geotiff_gen.generate_dem(geotiff_dir, (256, 256), name="dem_test")
        if dem:
            datasets.append(dem)

        sat = self.geotiff_gen.generate_satellite(geotiff_dir, bands=3, shape=(128, 128), name="satellite_test")
        if sat:
            datasets.append(sat)

        cog = self.geotiff_gen.generate_cog(geotiff_dir, (512, 512), name="cog_test")
        if cog:
            datasets.append(cog)

        suite = TestSuite(
            suite_name="geotiff_test_suite",
            description="Synthetic GeoTIFF files for DEM, satellite imagery, and COG",
            formats_covered=["geotiff/dem", "geotiff/satellite", "geotiff/cog"],
            total_datasets=len(datasets),
            datasets=datasets,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )
        self.generated_suites.append(suite)
        return suite

    def generate_all_suites(self) -> List[TestSuite]:
        """Generate all test suites."""
        suites = []

        print("Generating DICOM test suite...")
        suites.append(self.generate_dicom_suite())

        print("Generating FITS test suite...")
        suites.append(self.generate_fits_suite())

        print("Generating HDF5/netCDF test suite...")
        suites.append(self.generate_hdf5_suite())

        print("Generating GeoTIFF test suite...")
        suites.append(self.generate_geotiff_suite())

        return suites

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test infrastructure report."""
        return {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "output_directory": self.output_dir
            },
            "suites": [
                {
                    "suite_name": s.suite_name,
                    "description": s.description,
                    "formats": s.formats_covered,
                    "dataset_count": s.total_datasets,
                    "generated_at": s.generated_at,
                    "datasets": [
                        {
                            "filename": d.filename,
                            "format": d.file_format,
                            "modality": d.modality_type,
                            "size_bytes": d.file_size_bytes,
                            "dimensions": d.dimensions,
                            "metadata_fields": d.metadata_fields,
                            "notes": d.notes
                        }
                        for d in s.datasets if d is not None
                    ]
                }
                for s in self.generated_suites
            ],
            "total_datasets": sum(
                len([d for d in s.datasets if d is not None])
                for s in self.generated_suites
            ),
            "total_size_bytes": sum(
                sum(d.file_size_bytes for d in s.datasets if d is not None)
                for s in self.generated_suites
            )
        }

    def print_summary(self):
        """Print human-readable summary."""
        print("\n" + "=" * 80)
        print("TEST INFRASTRUCTURE SUMMARY")
        print("=" * 80)

        total_datasets = 0
        total_size = 0

        for suite in self.generated_suites:
            print(f"\n📁 {suite.suite_name}")
            print(f"   Description: {suite.description}")
            print(f"   Formats: {', '.join(suite.formats_covered)}")

            valid_datasets = [d for d in suite.datasets if d is not None]
            print(f"   Datasets: {len(valid_datasets)}")

            total_datasets += len(valid_datasets)
            suite_size = sum(d.file_size_bytes for d in valid_datasets)
            total_size += suite_size
            print(f"   Size: {suite_size / 1024:.1f} KB")

        print(f"\n📊 TOTAL: {total_datasets} datasets, {total_size / 1024:.1f} KB")
        print(f"📂 Output: {self.output_dir}")
        print("=" * 80)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Infrastructure Agent")
    parser.add_argument("--output", default="test_datasets", help="Output directory")
    parser.add_argument("--suite", choices=["dicom", "fits", "hdf5", "geotiff", "all"],
                        default="all", help="Test suite to generate")

    args = parser.parse_args()

    agent = TestInfrastructureAgent(args.output)

    if args.suite == "all":
        agent.generate_all_suites()
    elif args.suite == "dicom":
        agent.generate_dicom_suite()
    elif args.suite == "fits":
        agent.generate_fits_suite()
    elif args.suite == "hdf5":
        agent.generate_hdf5_suite()
    elif args.suite == "geotiff":
        agent.generate_geotiff_suite()

    agent.print_summary()

    report = agent.generate_report()
    with open("test_infrastructure_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nReport saved to: test_infrastructure_report.json")


if __name__ == "__main__":
    main()
