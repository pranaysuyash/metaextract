#!/usr/bin/env python3
"""
Testing Infrastructure Agent for Scientific Formats
Creates comprehensive test datasets for DICOM, FITS, and HDF5/NetCDF formats
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np

# Add server path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

logger = logging.getLogger(__name__)

class ScientificTestDatasetGenerator:
    """
    Comprehensive test dataset generator for scientific formats.
    Creates sample files for DICOM, FITS, and HDF5/NetCDF testing.
    """

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or Path(__file__).parent / "scientific-test-datasets")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track generated datasets
        self.datasets = {
            "dicom": {},
            "fits": {},
            "hdf5_netcdf": {}
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def generate_all_datasets(self) -> Dict[str, Any]:
        """Generate all scientific test datasets"""
        logger.info("Starting comprehensive scientific test dataset generation...")

        # Generate DICOM datasets
        self._generate_dicom_datasets()

        # Generate FITS datasets
        self._generate_fits_datasets()

        # Generate HDF5/NetCDF datasets
        self._generate_hdf5_netcdf_datasets()

        # Save dataset manifest
        self._save_manifest()

        logger.info(f"Generated test datasets in {self.output_dir}")
        return self.datasets

    def _generate_dicom_datasets(self):
        """Generate DICOM test datasets for different modalities"""
        logger.info("Generating DICOM test datasets...")

        dicom_dir = self.output_dir / "dicom"
        dicom_dir.mkdir(exist_ok=True)

        # CT Scan dataset
        ct_dataset = self._create_ct_dataset(dicom_dir / "ct_scan")
        self.datasets["dicom"]["ct_scan"] = ct_dataset

        # MRI dataset
        mri_dataset = self._create_mri_dataset(dicom_dir / "mri_scan")
        self.datasets["dicom"]["mri_scan"] = mri_dataset

        # Ultrasound dataset
        us_dataset = self._create_ultrasound_dataset(dicom_dir / "ultrasound")
        self.datasets["dicom"]["ultrasound"] = us_dataset

    def _generate_fits_datasets(self):
        """Generate FITS test datasets from astronomical surveys"""
        logger.info("Generating FITS test datasets...")

        fits_dir = self.output_dir / "fits"
        fits_dir.mkdir(exist_ok=True)

        # Hubble Space Telescope dataset
        hst_dataset = self._create_hst_fits_dataset(fits_dir / "hst_observation")
        self.datasets["fits"]["hst_observation"] = hst_dataset

        # Chandra X-ray dataset
        chandra_dataset = self._create_chandra_fits_dataset(fits_dir / "chandra_observation")
        self.datasets["fits"]["chandra_observation"] = chandra_dataset

        # SDSS spectroscopic dataset
        sdss_dataset = self._create_sdss_fits_dataset(fits_dir / "sdss_spectrum")
        self.datasets["fits"]["sdss_spectrum"] = sdss_dataset

    def _generate_hdf5_netcdf_datasets(self):
        """Generate HDF5/NetCDF test datasets for climate/meteorological data"""
        logger.info("Generating HDF5/NetCDF test datasets...")

        hdf5_dir = self.output_dir / "hdf5_netcdf"
        hdf5_dir.mkdir(exist_ok=True)

        # Climate model dataset
        climate_dataset = self._create_climate_model_dataset(hdf5_dir / "climate_model")
        self.datasets["hdf5_netcdf"]["climate_model"] = climate_dataset

        # Weather radar dataset
        radar_dataset = self._create_weather_radar_dataset(hdf5_dir / "weather_radar")
        self.datasets["hdf5_netcdf"]["weather_radar"] = radar_dataset

        # Oceanographic dataset
        ocean_dataset = self._create_oceanographic_dataset(hdf5_dir / "oceanographic")
        self.datasets["hdf5_netcdf"]["oceanographic"] = ocean_dataset

    def _create_ct_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic CT scan DICOM dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            import pydicom
            from pydicom.dataset import Dataset
            from pydicom.uid import ExplicitVRLittleEndian, CTImageStorage
        except ImportError:
            logger.warning("pydicom not available, creating mock CT dataset")
            return self._create_mock_dataset(output_path, "ct_scan", "DICOM CT Scan")

        # Create synthetic CT scan data
        ct_data = np.random.randint(0, 4096, (512, 512), dtype=np.uint16)

        # Create DICOM dataset
        ds = Dataset()

        # File meta information (required for proper DICOM)
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = CTImageStorage
        file_meta.MediaStorageSOPInstanceUID = "1.2.3.4.5.6.7.8.9.12"
        file_meta.ImplementationClassUID = "1.2.3.4.5.6.7.8.9.10"
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.file_meta = file_meta
        ds.is_implicit_VR = False
        ds.is_little_endian = True

        # Patient Information
        ds.PatientName = "DOE^JOHN"
        ds.PatientID = "123456"
        ds.PatientBirthDate = "19800101"
        ds.PatientSex = "M"
        ds.PatientAge = "045Y"

        # Study Information
        ds.StudyInstanceUID = "1.2.3.4.5.6.7.8.9.10"
        ds.StudyDate = "20240101"
        ds.StudyTime = "120000"
        ds.StudyDescription = "CT ABDOMEN PELVIS WITH CONTRAST"
        ds.AccessionNumber = "ACC123456"

        # Series Information
        ds.SeriesInstanceUID = "1.2.3.4.5.6.7.8.9.11"
        ds.SeriesNumber = 1
        ds.SeriesDescription = "CT ABDOMEN PELVIS"
        ds.Modality = "CT"
        ds.Manufacturer = "SIEMENS"
        ds.ManufacturerModelName = "SOMATOM Definition AS"

        # Image Information
        ds.SOPClassUID = CTImageStorage
        ds.SOPInstanceUID = "1.2.3.4.5.6.7.8.9.12"
        ds.InstanceNumber = 1
        ds.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]
        ds.SliceThickness = 5.0
        ds.KVP = 120.0
        ds.XRayTubeCurrent = 300
        ds.ExposureTime = 500
        ds.SliceLocation = 0.0

        # Image dimensions
        ds.Rows = 512
        ds.Columns = 512
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelData = ct_data.tobytes()

        # Save DICOM file
        dicom_file = output_path / "ct_scan.dcm"
        ds.save_as(str(dicom_file), write_like_original=False)

        return {
            "type": "dicom",
            "modality": "CT",
            "files": [str(dicom_file)],
            "description": "Synthetic CT abdomen/pelvis scan with contrast",
            "metadata": {
                "patient": "DOE^JOHN",
                "study_date": "20240101",
                "modality": "CT",
                "manufacturer": "SIEMENS",
                "slice_thickness": 5.0,
                "kvp": 120.0
            }
        }

    def _create_mri_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic MRI DICOM dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            import pydicom
            from pydicom.dataset import Dataset
            from pydicom.uid import ExplicitVRLittleEndian, MRImageStorage
        except ImportError:
            logger.warning("pydicom not available, creating mock MRI dataset")
            return self._create_mock_dataset(output_path, "mri_scan", "DICOM MRI Scan")

        # Create synthetic MRI data (T1-weighted)
        mri_data = np.random.randint(0, 4096, (256, 256), dtype=np.uint16)

        # Create DICOM dataset
        ds = Dataset()

        # File meta information (required for proper DICOM)
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = MRImageStorage
        file_meta.MediaStorageSOPInstanceUID = "1.2.3.4.5.6.7.8.9.22"
        file_meta.ImplementationClassUID = "1.2.3.4.5.6.7.8.9.10"
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.file_meta = file_meta
        ds.is_implicit_VR = False
        ds.is_little_endian = True

        # Patient Information
        ds.PatientName = "SMITH^JANE"
        ds.PatientID = "789012"
        ds.PatientBirthDate = "19900101"
        ds.PatientSex = "F"
        ds.PatientAge = "035Y"

        # Study Information
        ds.StudyInstanceUID = "1.2.3.4.5.6.7.8.9.20"
        ds.StudyDate = "20240102"
        ds.StudyTime = "140000"
        ds.StudyDescription = "MRI BRAIN WITH CONTRAST"
        ds.AccessionNumber = "ACC789012"

        # Series Information
        ds.SeriesInstanceUID = "1.2.3.4.5.6.7.8.9.21"
        ds.SeriesNumber = 1
        ds.SeriesDescription = "T1 AXIAL"
        ds.Modality = "MR"
        ds.Manufacturer = "GE MEDICAL SYSTEMS"
        ds.ManufacturerModelName = "SIGNA Premier"
        ds.MagneticFieldStrength = 3.0
        ds.ScanningSequence = "GR"
        ds.SequenceVariant = "SP"
        ds.ScanOptions = "FAST_GEMS"
        ds.RepetitionTime = 500.0
        ds.EchoTime = 15.0
        ds.InversionTime = 0.0
        ds.FlipAngle = 90.0

        # Image Information
        ds.SOPClassUID = MRImageStorage
        ds.SOPInstanceUID = "1.2.3.4.5.6.7.8.9.22"
        ds.InstanceNumber = 1
        ds.ImageType = ["ORIGINAL", "PRIMARY", "OTHER"]
        ds.SliceThickness = 5.0
        ds.SliceLocation = 0.0

        # Image dimensions
        ds.Rows = 256
        ds.Columns = 256
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelData = mri_data.tobytes()

        # Save DICOM file
        dicom_file = output_path / "mri_scan.dcm"
        ds.save_as(str(dicom_file), write_like_original=False)

        return {
            "type": "dicom",
            "modality": "MR",
            "files": [str(dicom_file)],
            "description": "Synthetic MRI brain T1-weighted scan",
            "metadata": {
                "patient": "SMITH^JANE",
                "study_date": "20240102",
                "modality": "MR",
                "manufacturer": "GE MEDICAL SYSTEMS",
                "magnetic_field": 3.0,
                "repetition_time": 500.0,
                "echo_time": 15.0
            }
        }

    def _create_ultrasound_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic Ultrasound DICOM dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            import pydicom
            from pydicom.dataset import Dataset
            from pydicom.uid import ExplicitVRLittleEndian, UltrasoundImageStorage
        except ImportError:
            logger.warning("pydicom not available, creating mock ultrasound dataset")
            return self._create_mock_dataset(output_path, "ultrasound", "DICOM Ultrasound")

        # Create synthetic ultrasound data
        us_data = np.random.randint(0, 256, (512, 512), dtype=np.uint8)

        # Create DICOM dataset
        ds = Dataset()

        # File meta information (required for proper DICOM)
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = UltrasoundImageStorage
        file_meta.MediaStorageSOPInstanceUID = "1.2.3.4.5.6.7.8.9.32"
        file_meta.ImplementationClassUID = "1.2.3.4.5.6.7.8.9.10"
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.file_meta = file_meta
        ds.is_implicit_VR = False
        ds.is_little_endian = True

        # Patient Information
        ds.PatientName = "JOHNSON^BOB"
        ds.PatientID = "345678"
        ds.PatientBirthDate = "19750101"
        ds.PatientSex = "M"
        ds.PatientAge = "050Y"

        # Study Information
        ds.StudyInstanceUID = "1.2.3.4.5.6.7.8.9.30"
        ds.StudyDate = "20240103"
        ds.StudyTime = "160000"
        ds.StudyDescription = "ULTRASOUND ABDOMEN"
        ds.AccessionNumber = "ACC345678"

        # Series Information
        ds.SeriesInstanceUID = "1.2.3.4.5.6.7.8.9.31"
        ds.SeriesNumber = 1
        ds.SeriesDescription = "LIVER"
        ds.Modality = "US"
        ds.Manufacturer = "PHILIPS"
        ds.ManufacturerModelName = "EPIQ 7"

        # Image Information
        ds.SOPClassUID = UltrasoundImageStorage
        ds.SOPInstanceUID = "1.2.3.4.5.6.7.8.9.32"
        ds.InstanceNumber = 1
        ds.ImageType = ["ORIGINAL", "PRIMARY"]
        ds.BodyPartExamined = "ABDOMEN"
        ds.ScanOptions = "B_MODE"

        # Image dimensions
        ds.Rows = 512
        ds.Columns = 512
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelData = us_data.tobytes()

        # Save DICOM file
        dicom_file = output_path / "ultrasound.dcm"
        ds.save_as(str(dicom_file), write_like_original=False)

        return {
            "type": "dicom",
            "modality": "US",
            "files": [str(dicom_file)],
            "description": "Synthetic ultrasound abdomen/liver scan",
            "metadata": {
                "patient": "JOHNSON^BOB",
                "study_date": "20240103",
                "modality": "US",
                "manufacturer": "PHILIPS",
                "body_part": "ABDOMEN",
                "scan_options": "B_MODE"
            }
        }

    def _create_hst_fits_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic Hubble Space Telescope FITS dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            from astropy.io import fits
            import astropy.wcs as wcs
        except ImportError:
            logger.warning("astropy not available, creating mock FITS dataset")
            return self._create_mock_dataset(output_path, "hst_observation", "FITS HST Observation")

        # Create synthetic astronomical image data
        image_data = np.random.normal(1000, 100, (1024, 1024)).astype(np.float32)

        # Create WCS (World Coordinate System) for astronomical coordinates
        w = wcs.WCS(naxis=2)
        w.wcs.crpix = [512.0, 512.0]  # Reference pixel
        w.wcs.cdelt = [-0.066667, 0.066667]  # Pixel scale in degrees
        w.wcs.crval = [150.0, 2.0]  # Reference coordinate (RA, Dec in degrees)
        w.wcs.ctype = ["RA---TAN", "DEC--TAN"]  # Coordinate types

        # Create primary HDU
        primary = fits.PrimaryHDU(data=image_data, header=w.to_header())

        # Add extensive header information
        primary.header['TELESCOP'] = 'HST'
        primary.header['INSTRUME'] = 'ACS'
        primary.header['FILTER'] = 'F606W'
        primary.header['EXPTIME'] = 1200.0
        primary.header['DATE-OBS'] = '2024-01-01T12:00:00'
        primary.header['TIME-OBS'] = '12:00:00'
        primary.header['OBSERVER'] = 'Test Observer'
        primary.header['PROPOSAL'] = '12345'
        primary.header['TARGET'] = 'NGC 1234'
        primary.header['RA_TARG'] = 150.0
        primary.header['DEC_TARG'] = 2.0
        primary.header['PA_V3'] = 45.0
        primary.header['SUNANGLE'] = 120.0
        primary.header['MOONANGL'] = 60.0
        primary.header['FGSLOCK'] = 'FINE'
        primary.header['GYROMODE'] = 'FINE'
        primary.header['SAA_MODE'] = 'DISABLED'

        # Create HDU list and save
        hdul = fits.HDUList([primary])
        fits_file = output_path / "hst_observation.fits"
        hdul.writeto(fits_file, overwrite=True)

        return {
            "type": "fits",
            "survey": "HST",
            "files": [str(fits_file)],
            "description": "Synthetic Hubble Space Telescope ACS F606W observation",
            "metadata": {
                "telescope": "HST",
                "instrument": "ACS",
                "filter": "F606W",
                "exposure_time": 1200.0,
                "target": "NGC 1234",
                "ra": 150.0,
                "dec": 2.0,
                "date_obs": "2024-01-01T12:00:00"
            }
        }

    def _create_chandra_fits_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic Chandra X-ray FITS dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            from astropy.io import fits
            import astropy.wcs as wcs
        except ImportError:
            logger.warning("astropy not available, creating mock Chandra dataset")
            return self._create_mock_dataset(output_path, "chandra_observation", "FITS Chandra Observation")

        # Create synthetic X-ray image data
        xray_data = np.random.poisson(50, (512, 512)).astype(np.float32)

        # Create WCS for Chandra coordinates
        w = wcs.WCS(naxis=2)
        w.wcs.crpix = [256.0, 256.0]
        w.wcs.cdelt = [-0.492, 0.492]  # Chandra pixel scale ~0.492 arcsec
        w.wcs.crval = [12.5, -5.0]  # Reference coordinate
        w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

        # Create primary HDU
        primary = fits.PrimaryHDU(data=xray_data, header=w.to_header())

        # Add Chandra-specific header information
        primary.header['TELESCOP'] = 'CHANDRA'
        primary.header['INSTRUME'] = 'ACIS'
        primary.header['GRATING'] = 'NONE'
        primary.header['EXPTIME'] = 50000.0  # 50 ks exposure
        primary.header['DATE-OBS'] = '2024-01-02T06:00:00'
        primary.header['TIME-OBS'] = '06:00:00'
        primary.header['OBSERVER'] = 'Chandra Test'
        primary.header['OBJECT'] = 'CXOU J123456.7+123456'
        primary.header['RA_OBJ'] = 12.5
        primary.header['DEC_OBJ'] = -5.0
        primary.header['RA_NOM'] = 12.5
        primary.header['DEC_NOM'] = -5.0
        primary.header['ROLL_NOM'] = 0.0
        primary.header['DATAMODE'] = 'FAINT'
        primary.header['READMODE'] = 'TIMED'
        primary.header['GAINFILE'] = 'acisD2000-01-29gainN0006.fits'
        primary.header['CTIFILE'] = 'acisD2000-01-29ctiN0005.fits'

        # Create HDU list and save
        hdul = fits.HDUList([primary])
        fits_file = output_path / "chandra_observation.fits"
        hdul.writeto(fits_file, overwrite=True)

        return {
            "type": "fits",
            "survey": "Chandra",
            "files": [str(fits_file)],
            "description": "Synthetic Chandra ACIS X-ray observation",
            "metadata": {
                "telescope": "CHANDRA",
                "instrument": "ACIS",
                "exposure_time": 50000.0,
                "target": "CXOU J123456.7+123456",
                "ra": 12.5,
                "dec": -5.0,
                "date_obs": "2024-01-02T06:00:00"
            }
        }

    def _create_sdss_fits_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic SDSS spectroscopic FITS dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            from astropy.io import fits
        except ImportError:
            logger.warning("astropy not available, creating mock SDSS dataset")
            return self._create_mock_dataset(output_path, "sdss_spectrum", "FITS SDSS Spectrum")

        # Create synthetic spectroscopic data
        wavelength = np.linspace(3800, 9200, 4000)  # Angstroms
        flux = np.random.normal(100, 10, 4000) + 50 * np.sin(2 * np.pi * wavelength / 1000)
        flux_err = np.random.normal(5, 1, 4000)

        # Create HDUs for spectroscopic data
        col1 = fits.Column(name='wavelength', format='E', array=wavelength)
        col2 = fits.Column(name='flux', format='E', array=flux)
        col3 = fits.Column(name='flux_err', format='E', array=flux_err)

        cols = fits.ColDefs([col1, col2, col3])
        spectrum_hdu = fits.BinTableHDU.from_columns(cols)

        # Create primary HDU with header
        primary = fits.PrimaryHDU()
        primary.header['TELESCOP'] = 'SDSS 2.5-M'
        primary.header['INSTRUME'] = 'SDSS Spectrograph'
        primary.header['PLATEID'] = 1234
        primary.header['MJD'] = 56789
        primary.header['FIBERID'] = 567
        primary.header['RAOBJ'] = 180.0
        primary.header['DECOBJ'] = 0.0
        primary.header['OBJTYPE'] = 'GALAXY'
        primary.header['Z'] = 0.05
        primary.header['Z_ERR'] = 0.001
        primary.header['RCHI2'] = 1.2
        primary.header['DOF'] = 3876
        primary.header['VDISP'] = 150.0
        primary.header['VDISP_ERR'] = 10.0

        # Create HDU list and save
        hdul = fits.HDUList([primary, spectrum_hdu])
        fits_file = output_path / "sdss_spectrum.fits"
        hdul.writeto(fits_file, overwrite=True)

        return {
            "type": "fits",
            "survey": "SDSS",
            "files": [str(fits_file)],
            "description": "Synthetic SDSS spectroscopic observation of a galaxy",
            "metadata": {
                "telescope": "SDSS 2.5-M",
                "instrument": "SDSS Spectrograph",
                "plate_id": 1234,
                "mjd": 56789,
                "fiber_id": 567,
                "ra": 180.0,
                "dec": 0.0,
                "object_type": "GALAXY",
                "redshift": 0.05
            }
        }

    def _create_climate_model_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic climate model HDF5/NetCDF dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            import netCDF4
        except ImportError:
            logger.warning("netCDF4 not available, creating mock climate dataset")
            return self._create_mock_dataset(output_path, "climate_model", "NetCDF Climate Model")

        # Create NetCDF file
        nc_file = output_path / "climate_model.nc"
        with netCDF4.Dataset(str(nc_file), 'w', format='NETCDF4') as nc:

            # Dimensions
            nc.createDimension('time', None)
            nc.createDimension('lat', 180)
            nc.createDimension('lon', 360)

            # Coordinate variables
            time_var = nc.createVariable('time', 'f8', ('time',))
            time_var.units = 'days since 2000-01-01'
            time_var.calendar = 'standard'
            time_var[:] = np.arange(0, 365*10, 30)  # 10 years monthly

            lat_var = nc.createVariable('lat', 'f4', ('lat',))
            lat_var.units = 'degrees_north'
            lat_var[:] = np.linspace(-89.5, 89.5, 180)

            lon_var = nc.createVariable('lon', 'f4', ('lon',))
            lon_var.units = 'degrees_east'
            lon_var[:] = np.linspace(-179.5, 179.5, 360)

            # Data variables
            temp_var = nc.createVariable('temperature', 'f4', ('time', 'lat', 'lon'))
            temp_var.units = 'K'
            temp_var.long_name = 'Surface Temperature'
            temp_var.missing_value = -999.0

            precip_var = nc.createVariable('precipitation', 'f4', ('time', 'lat', 'lon'))
            precip_var.units = 'mm/day'
            precip_var.long_name = 'Precipitation Rate'
            precip_var.missing_value = -999.0

            # Generate synthetic climate data
            for t in range(len(time_var)):
                # Temperature with seasonal cycle and latitude dependence
                temp_base = 288 - 25 * np.cos(2 * np.pi * t / 12)  # Seasonal cycle
                lat_factor = np.cos(np.radians(lat_var[:]))  # Latitude dependence
                temp_data = temp_base + 10 * lat_factor[:, np.newaxis] + np.random.normal(0, 2, (180, 360))
                temp_var[t, :, :] = temp_data

                # Precipitation with some spatial patterns
                precip_data = 5 + 3 * np.sin(2 * np.pi * lon_var[:] / 180) + np.random.exponential(2, (180, 360))
                precip_var[t, :, :] = precip_data

            # Global attributes
            nc.title = 'Synthetic Climate Model Output'
            nc.institution = 'Test Climate Research Institute'
            nc.source = 'Climate Model v2.0'
            nc.history = f'Created on {datetime.now().isoformat()}'
            nc.references = 'Synthetic data for testing purposes'
            nc.Conventions = 'CF-1.8'

        return {
            "type": "netcdf",
            "domain": "climate",
            "files": [str(nc_file)],
            "description": "Synthetic climate model output with temperature and precipitation",
            "metadata": {
                "title": "Synthetic Climate Model Output",
                "institution": "Test Climate Research Institute",
                "variables": ["temperature", "precipitation"],
                "dimensions": {"time": "unlimited", "lat": 180, "lon": 360},
                "time_range": "10 years monthly",
                "conventions": "CF-1.8"
            }
        }

    def _create_weather_radar_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic weather radar HDF5 dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            import h5py
        except ImportError:
            logger.warning("h5py not available, creating mock radar dataset")
            return self._create_mock_dataset(output_path, "weather_radar", "HDF5 Weather Radar")

        # Create HDF5 file
        hdf_file = output_path / "weather_radar.h5"
        with h5py.File(str(hdf_file), 'w') as hdf:

            # Radar data attributes
            hdf.attrs['title'] = 'Synthetic Weather Radar Data'
            hdf.attrs['institution'] = 'Test Meteorological Service'
            hdf.attrs['source'] = 'Radar Simulator v1.0'
            hdf.attrs['history'] = f'Created on {datetime.now().isoformat()}'
            hdf.attrs['radar_type'] = 'Doppler Weather Radar'
            hdf.attrs['frequency'] = 2.7e9  # S-band
            hdf.attrs['wavelength'] = 0.11  # meters
            hdf.attrs['beamwidth'] = 1.0  # degrees

            # Dimensions
            hdf.create_dataset('latitude', data=np.linspace(35.0, 45.0, 100))
            hdf.create_dataset('longitude', data=np.linspace(-85.0, -75.0, 100))
            hdf.create_dataset('altitude', data=np.linspace(0, 10000, 50))
            hdf.create_dataset('time', data=np.arange(0, 3600, 300))  # 1 hour, 5-min intervals

            # Radar variables
            reflectivity = np.random.exponential(20, (12, 50, 100, 100))  # dBZ
            velocity = np.random.normal(0, 5, (12, 50, 100, 100))  # m/s
            spectrum_width = np.random.exponential(2, (12, 50, 100, 100))  # m/s

            hdf.create_dataset('reflectivity', data=reflectivity)
            hdf['reflectivity'].attrs['units'] = 'dBZ'
            hdf['reflectivity'].attrs['long_name'] = 'Radar Reflectivity'

            hdf.create_dataset('radial_velocity', data=velocity)
            hdf['radial_velocity'].attrs['units'] = 'm/s'
            hdf['radial_velocity'].attrs['long_name'] = 'Radial Velocity'

            hdf.create_dataset('spectrum_width', data=spectrum_width)
            hdf['spectrum_width'].attrs['units'] = 'm/s'
            hdf['spectrum_width'].attrs['long_name'] = 'Spectrum Width'

            # Quality flags
            quality = np.random.randint(0, 4, (12, 50, 100, 100))  # 0=good, 1=range_folded, 2=below_threshold, 3=no_data
            hdf.create_dataset('quality_flag', data=quality)
            hdf['quality_flag'].attrs['flag_values'] = [0, 1, 2, 3]
            hdf['quality_flag'].attrs['flag_meanings'] = 'good range_folded below_threshold no_data'

        return {
            "type": "hdf5",
            "domain": "meteorological",
            "files": [str(hdf_file)],
            "description": "Synthetic weather radar data with reflectivity, velocity, and quality flags",
            "metadata": {
                "title": "Synthetic Weather Radar Data",
                "institution": "Test Meteorological Service",
                "radar_type": "Doppler Weather Radar",
                "frequency": 2.7e9,
                "variables": ["reflectivity", "radial_velocity", "spectrum_width", "quality_flag"],
                "dimensions": {"time": 12, "altitude": 50, "latitude": 100, "longitude": 100}
            }
        }

    def _create_oceanographic_dataset(self, output_path: Path) -> Dict[str, Any]:
        """Create a synthetic oceanographic NetCDF dataset"""
        output_path.mkdir(exist_ok=True)

        try:
            import netCDF4
        except ImportError:
            logger.warning("netCDF4 not available, creating mock oceanographic dataset")
            return self._create_mock_dataset(output_path, "oceanographic", "NetCDF Oceanographic")

        # Create NetCDF file
        nc_file = output_path / "oceanographic.nc"
        with netCDF4.Dataset(str(nc_file), 'w', format='NETCDF4') as nc:

            # Dimensions
            nc.createDimension('time', None)
            nc.createDimension('depth', 50)
            nc.createDimension('lat', 100)
            nc.createDimension('lon', 120)

            # Coordinate variables
            time_var = nc.createVariable('time', 'f8', ('time',))
            time_var.units = 'hours since 2024-01-01 00:00:00'
            time_var.calendar = 'standard'
            time_var[:] = np.arange(0, 24*30, 6)  # 30 days, 6-hourly

            depth_var = nc.createVariable('depth', 'f4', ('depth',))
            depth_var.units = 'meters'
            depth_var.positive = 'down'
            depth_var[:] = np.linspace(0, 5000, 50)

            lat_var = nc.createVariable('lat', 'f4', ('lat',))
            lat_var.units = 'degrees_north'
            lat_var[:] = np.linspace(-30, 30, 100)

            lon_var = nc.createVariable('lon', 'f4', ('lon',))
            lon_var.units = 'degrees_east'
            lon_var[:] = np.linspace(-20, 20, 120)

            # Ocean variables
            temp_var = nc.createVariable('temperature', 'f4', ('time', 'depth', 'lat', 'lon'))
            temp_var.units = 'degrees_C'
            temp_var.long_name = 'Sea Water Temperature'
            temp_var.missing_value = -999.0

            salinity_var = nc.createVariable('salinity', 'f4', ('time', 'depth', 'lat', 'lon'))
            salinity_var.units = 'PSU'
            salinity_var.long_name = 'Sea Water Salinity'
            salinity_var.missing_value = -999.0

            u_var = nc.createVariable('u', 'f4', ('time', 'depth', 'lat', 'lon'))
            u_var.units = 'm/s'
            u_var.long_name = 'Eastward Sea Water Velocity'
            u_var.missing_value = -999.0

            v_var = nc.createVariable('v', 'f4', ('time', 'depth', 'lat', 'lon'))
            v_var.units = 'm/s'
            v_var.long_name = 'Northward Sea Water Velocity'
            v_var.missing_value = -999.0

            # Generate synthetic ocean data
            lat_data = lat_var[:]
            lon_data = lon_var[:]
            for t in range(len(time_var)):
                for d in range(len(depth_var)):
                    # Temperature decreases with depth, varies with latitude
                    temp_base = 25 - 0.005 * depth_var[d] - 0.1 * abs(lat_data)
                    temp_data = temp_base[:, np.newaxis] + np.random.normal(0, 1, (100, 120))
                    temp_var[t, d, :, :] = temp_data

                    # Salinity varies with depth and latitude
                    salinity_base = 35 - 0.001 * depth_var[d] + 0.05 * abs(lat_data)
                    salinity_data = salinity_base[:, np.newaxis] + np.random.normal(0, 0.5, (100, 120))
                    salinity_var[t, d, :, :] = salinity_data

                    # Currents with some spatial patterns
                    u_data = 0.1 * np.sin(2 * np.pi * lon_data / 10) + np.random.normal(0, 0.05, (100, 120))
                    v_data = 0.05 * np.cos(2 * np.pi * lat_data[:, np.newaxis] / 10) + np.random.normal(0, 0.05, (100, 120))
                    u_var[t, d, :, :] = u_data
                    v_var[t, d, :, :] = v_data

            # Global attributes
            nc.title = 'Synthetic Oceanographic Model Output'
            nc.institution = 'Test Ocean Research Institute'
            nc.source = 'Ocean Model v3.0'
            nc.history = f'Created on {datetime.now().isoformat()}'
            nc.references = 'Synthetic data for testing purposes'
            nc.Conventions = 'CF-1.8'

        return {
            "type": "netcdf",
            "domain": "oceanographic",
            "files": [str(nc_file)],
            "description": "Synthetic oceanographic model with temperature, salinity, and currents",
            "metadata": {
                "title": "Synthetic Oceanographic Model Output",
                "institution": "Test Ocean Research Institute",
                "variables": ["temperature", "salinity", "u", "v"],
                "dimensions": {"time": "unlimited", "depth": 50, "lat": 100, "lon": 120},
                "time_range": "30 days 6-hourly",
                "conventions": "CF-1.8"
            }
        }

    def _create_mock_dataset(self, output_path: Path, name: str, description: str) -> Dict[str, Any]:
        """Create a mock dataset when libraries are not available"""
        output_path.mkdir(exist_ok=True)

        # Create a simple JSON file with metadata
        mock_file = output_path / f"{name}_metadata.json"
        mock_data = {
            "mock": True,
            "description": f"Mock {description} - libraries not available",
            "name": name,
            "created": datetime.now().isoformat(),
            "note": "Install required libraries to generate real test data"
        }

        with open(mock_file, 'w') as f:
            json.dump(mock_data, f, indent=2)

        return {
            "type": "mock",
            "name": name,
            "files": [str(mock_file)],
            "description": description,
            "mock": True
        }

    def _save_manifest(self):
        """Save a manifest of all generated datasets"""
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "generator": "ScientificTestDatasetGenerator",
            "version": "1.0.0",
            "datasets": self.datasets,
            "summary": {
                "total_datasets": sum(len(v) for v in self.datasets.values()),
                "dicom_datasets": len(self.datasets["dicom"]),
                "fits_datasets": len(self.datasets["fits"]),
                "hdf5_netcdf_datasets": len(self.datasets["hdf5_netcdf"])
            }
        }

        manifest_file = self.output_dir / "dataset_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Saved dataset manifest to {manifest_file}")


def main():
    """Main entry point for the testing infrastructure agent"""
    generator = ScientificTestDatasetGenerator()
    datasets = generator.generate_all_datasets()

    print("\n=== Scientific Test Datasets Generated ===")
    for category, category_datasets in datasets.items():
        print(f"\n{category.upper()}:")
        for name, info in category_datasets.items():
            print(f"  - {name}: {info['description']}")
            print(f"    Files: {len(info['files'])}")

    print(f"\nDatasets saved to: {generator.output_dir}")
    print("Manifest: dataset_manifest.json")


if __name__ == "__main__":
    main()