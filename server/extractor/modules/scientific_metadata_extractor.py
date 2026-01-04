#!/usr/bin/env python3
"""
Scientific Metadata Extractor Module

Extracts specialized metadata from scientific file formats including:
- DICOM (Medical Imaging)
- FITS (Astronomical Data)
- HDF5 (Scientific Data)
- NetCDF (Climate/Oceanographic Data)
- TIFF (Scientific Images with GeoTIFF support)
"""

import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_scientific_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract scientific metadata from various scientific file formats.
    
    Args:
        filepath: Path to the file to extract metadata from
        
    Returns:
        Dictionary containing scientific metadata organized by format type
    """
    result = {
        'scientific_metadata': {},
        'format_type': 'unknown',
        'extraction_success': False,
        'errors': []
    }
    
    try:
        file_extension = Path(filepath).suffix.lower()
        
        if file_extension in ['.dcm', '.dicom']:
            result['scientific_metadata'] = extract_dicom_metadata(filepath)
            result['format_type'] = 'dicom'
        elif file_extension in ['.fits', '.fit']:
            result['scientific_metadata'] = extract_fits_metadata(filepath)
            result['format_type'] = 'fits'
        elif file_extension in ['.h5', '.hdf', '.hdf5']:
            result['scientific_metadata'] = extract_hdf5_metadata(filepath)
            result['format_type'] = 'hdf5'
        elif file_extension in ['.nc', '.netcdf']:
            result['scientific_metadata'] = extract_netcdf_metadata(filepath)
            result['format_type'] = 'netcdf'
        elif file_extension in ['.tif', '.tiff']:
            result['scientific_metadata'] = extract_geotiff_metadata(filepath)
            result['format_type'] = 'geotiff'
        else:
            result['errors'].append(f"Unsupported scientific format: {file_extension}")
            return result
        
        result['extraction_success'] = True
        logger.info(f"Successfully extracted scientific metadata from {filepath}")
        
    except Exception as e:
        error_msg = f"Error extracting scientific metadata from {filepath}: {str(e)}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    return result


def extract_dicom_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata from DICOM files (Medical Imaging).
    
    Args:
        filepath: Path to the DICOM file
        
    Returns:
        Dictionary containing DICOM metadata
    """
    dicom_metadata = {
        'patient_info': {},
        'study_info': {},
        'series_info': {},
        'image_info': {},
        'equipment_info': {},
        'acquisition_info': {},
        'image_processing': {},
        'quality_metrics': {}
    }
    
    try:
        # Try to import pydicom - this is the standard library for DICOM
        import pydicom
        from pydicom.errors import InvalidDicomError
        
        try:
            ds = pydicom.dcmread(filepath, force=True)
            
            # Patient Information
            if hasattr(ds, 'PatientName'):
                dicom_metadata['patient_info']['name'] = str(ds.PatientName)
            if hasattr(ds, 'PatientID'):
                dicom_metadata['patient_info']['id'] = ds.PatientID
            if hasattr(ds, 'PatientBirthDate'):
                dicom_metadata['patient_info']['birth_date'] = str(ds.PatientBirthDate)
            if hasattr(ds, 'PatientSex'):
                dicom_metadata['patient_info']['sex'] = ds.PatientSex
            
            # Study Information
            if hasattr(ds, 'StudyDate'):
                dicom_metadata['study_info']['date'] = str(ds.StudyDate)
            if hasattr(ds, 'StudyTime'):
                dicom_metadata['study_info']['time'] = str(ds.StudyTime)
            if hasattr(ds, 'StudyInstanceUID'):
                dicom_metadata['study_info']['instance_uid'] = ds.StudyInstanceUID
            if hasattr(ds, 'StudyDescription'):
                dicom_metadata['study_info']['description'] = ds.StudyDescription
            
            # Series Information
            if hasattr(ds, 'SeriesInstanceUID'):
                dicom_metadata['series_info']['instance_uid'] = ds.SeriesInstanceUID
            if hasattr(ds, 'SeriesNumber'):
                dicom_metadata['series_info']['number'] = ds.SeriesNumber
            if hasattr(ds, 'Modality'):
                dicom_metadata['series_info']['modality'] = ds.Modality
            if hasattr(ds, 'SeriesDescription'):
                dicom_metadata['series_info']['description'] = ds.SeriesDescription
            
            # Image Information
            if hasattr(ds, 'InstanceNumber'):
                dicom_metadata['image_info']['instance_number'] = ds.InstanceNumber
            if hasattr(ds, 'Rows'):
                dicom_metadata['image_info']['rows'] = ds.Rows
            if hasattr(ds, 'Columns'):
                dicom_metadata['image_info']['columns'] = ds.Columns
            if hasattr(ds, 'PixelSpacing'):
                dicom_metadata['image_info']['pixel_spacing'] = list(ds.PixelSpacing)
            if hasattr(ds, 'ImageOrientationPatient'):
                dicom_metadata['image_info']['orientation'] = list(ds.ImageOrientationPatient)
            if hasattr(ds, 'ImagePositionPatient'):
                dicom_metadata['image_info']['position'] = list(ds.ImagePositionPatient)
            
            # Equipment Information
            if hasattr(ds, 'Manufacturer'):
                dicom_metadata['equipment_info']['manufacturer'] = ds.Manufacturer
            if hasattr(ds, 'ManufacturerModelName'):
                dicom_metadata['equipment_info']['model_name'] = ds.ManufacturerModelName
            if hasattr(ds, 'DeviceSerialNumber'):
                dicom_metadata['equipment_info']['serial_number'] = ds.DeviceSerialNumber
            if hasattr(ds, 'SoftwareVersions'):
                dicom_metadata['equipment_info']['software_versions'] = str(ds.SoftwareVersions)
            
            # Acquisition Information
            if hasattr(ds, 'AcquisitionDate'):
                dicom_metadata['acquisition_info']['date'] = str(ds.AcquisitionDate)
            if hasattr(ds, 'AcquisitionTime'):
                dicom_metadata['acquisition_info']['time'] = str(ds.AcquisitionTime)
            if hasattr(ds, 'SliceThickness'):
                dicom_metadata['acquisition_info']['slice_thickness'] = float(ds.SliceThickness)
            if hasattr(ds, 'KVP'):
                dicom_metadata['acquisition_info']['kvp'] = float(ds.KVP)
            if hasattr(ds, 'ExposureTime'):
                dicom_metadata['acquisition_info']['exposure_time'] = float(ds.ExposureTime)
            if hasattr(ds, 'XRayTubeCurrent'):
                dicom_metadata['acquisition_info']['tube_current'] = float(ds.XRayTubeCurrent)
            
            # Image Processing
            if hasattr(ds, 'RescaleIntercept'):
                dicom_metadata['image_processing']['rescale_intercept'] = float(ds.RescaleIntercept)
            if hasattr(ds, 'RescaleSlope'):
                dicom_metadata['image_processing']['rescale_slope'] = float(ds.RescaleSlope)
            if hasattr(ds, 'WindowCenter'):
                dicom_metadata['image_processing']['window_center'] = float(ds.WindowCenter)
            if hasattr(ds, 'WindowWidth'):
                dicom_metadata['image_processing']['window_width'] = float(ds.WindowWidth)
            
            # Quality Metrics
            if hasattr(ds, 'ImageType'):
                dicom_metadata['quality_metrics']['image_type'] = list(ds.ImageType)
            if hasattr(ds, 'PhotometricInterpretation'):
                dicom_metadata['quality_metrics']['photometric_interpretation'] = ds.PhotometricInterpretation
            if hasattr(ds, 'BitsAllocated'):
                dicom_metadata['quality_metrics']['bits_allocated'] = ds.BitsAllocated
            if hasattr(ds, 'BitsStored'):
                dicom_metadata['quality_metrics']['bits_stored'] = ds.BitsStored
            if hasattr(ds, 'HighBit'):
                dicom_metadata['quality_metrics']['high_bit'] = ds.HighBit
            if hasattr(ds, 'PixelRepresentation'):
                dicom_metadata['quality_metrics']['pixel_representation'] = ds.PixelRepresentation
            
        except InvalidDicomError:
            logger.warning(f"File {filepath} is not a valid DICOM file")
            dicom_metadata['errors'] = ['Invalid DICOM file']
        
    except ImportError:
        logger.warning("pydicom not available - DICOM metadata extraction limited")
        dicom_metadata['errors'] = ['pydicom library not available']
    except Exception as e:
        logger.error(f"Error extracting DICOM metadata: {str(e)}")
        dicom_metadata['errors'] = [f'Error: {str(e)}']
    
    return dicom_metadata


def extract_fits_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata from FITS files (Astronomical Data).
    
    Args:
        filepath: Path to the FITS file
        
    Returns:
        Dictionary containing FITS metadata
    """
    fits_metadata = {
        'primary_header': {},
        'image_info': {},
        'world_coordinate_system': {},
        'observation_info': {},
        'instrument_info': {},
        'processing_info': {},
        'quality_metrics': {}
    }
    
    try:
        # Try to import astropy - this is the standard library for FITS
        import astropy.io.fits as fits
        from astropy import units as u
        from astropy.coordinates import SkyCoord
        
        with fits.open(filepath) as hdul:
            # Primary header
            primary_header = hdul[0].header
            for key in primary_header.keys():
                if key not in ['', 'COMMENT', 'HISTORY']:  # Skip empty and comment keys
                    fits_metadata['primary_header'][key] = primary_header[key]
            
            # Image information if available
            if len(hdul) > 0 and hasattr(hdul[0], 'data'):
                data = hdul[0].data
                if data is not None:
                    fits_metadata['image_info']['shape'] = list(data.shape) if hasattr(data, 'shape') else 'N/A'
                    fits_metadata['image_info']['dtype'] = str(data.dtype) if hasattr(data, 'dtype') else 'N/A'
                    if hasattr(data, 'size'):
                        fits_metadata['image_info']['size'] = int(data.size)
            
            # World Coordinate System (WCS) information
            try:
                from astropy.wcs import WCS
                wcs = WCS(hdul[0].header)
                
                fits_metadata['world_coordinate_system']['naxis'] = wcs.naxis
                fits_metadata['world_coordinate_system']['wcs_name'] = wcs.wcs.name
                fits_metadata['world_coordinate_system']['radesys'] = getattr(wcs.wcs, 'radesys', 'N/A')
                fits_metadata['world_coordinate_system']['equinox'] = getattr(wcs.wcs, 'equinox', 'N/A')
                
                # Coordinate information
                if wcs.wcs.crval is not None:
                    fits_metadata['world_coordinate_system']['reference_values'] = wcs.wcs.crval.tolist()
                if wcs.wcs.crpix is not None:
                    fits_metadata['world_coordinate_system']['reference_pixels'] = wcs.wcs.crpix.tolist()
                if wcs.wcs.cdelt is not None:
                    fits_metadata['world_coordinate_system']['coordinate_deltas'] = wcs.wcs.cdelt.tolist()
                
            except Exception as wcs_error:
                logger.warning(f"WCS information not available: {str(wcs_error)}")
            
            # Observation information from header
            obs_keys = ['DATE-OBS', 'DATE', 'OBSERVER', 'OBJECT', 'TELESCOP', 'INSTRUME', 'OBSERVAT']
            for key in obs_keys:
                if key in primary_header:
                    fits_metadata['observation_info'][key.lower().replace('-', '_')] = primary_header[key]
            
            # Instrument information
            instr_keys = ['DETECTOR', 'FILTER', 'EXPTIME', 'AIRMASS', 'GAIN', 'RDNOISE']
            for key in instr_keys:
                if key in primary_header:
                    fits_metadata['instrument_info'][key.lower()] = primary_header[key]
            
            # Processing information
            proc_keys = ['BSCALE', 'BZERO', 'BUNIT', 'CTYPE1', 'CTYPE2', 'CRVAL1', 'CRVAL2', 'CRPIX1', 'CRPIX2']
            for key in proc_keys:
                if key in primary_header:
                    fits_metadata['processing_info'][key.lower()] = primary_header[key]
            
            # Quality metrics
            if 'DATAMIN' in primary_header:
                fits_metadata['quality_metrics']['data_min'] = primary_header['DATAMIN']
            if 'DATAMAX' in primary_header:
                fits_metadata['quality_metrics']['data_max'] = primary_header['DATAMAX']
            if 'DATASEC' in primary_header:
                fits_metadata['quality_metrics']['data_section'] = primary_header['DATASEC']
    
    except ImportError:
        logger.warning("astropy not available - FITS metadata extraction limited")
        fits_metadata['errors'] = ['astropy library not available']
    except Exception as e:
        logger.error(f"Error extracting FITS metadata: {str(e)}")
        fits_metadata['errors'] = [f'Error: {str(e)}']
    
    return fits_metadata


def extract_hdf5_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata from HDF5 files (Hierarchical Data Format).
    
    Args:
        filepath: Path to the HDF5 file
        
    Returns:
        Dictionary containing HDF5 metadata
    """
    hdf5_metadata = {
        'file_info': {},
        'datasets': [],
        'groups': [],
        'attributes': {},
        'structure': {},
        'compression_info': {}
    }
    
    try:
        import h5py
        
        with h5py.File(filepath, 'r') as f:
            # File information
            hdf5_metadata['file_info']['filename'] = f.filename
            hdf5_metadata['file_info']['mode'] = f.mode
            hdf5_metadata['file_info']['driver'] = f.driver if hasattr(f, 'driver') else 'N/A'
            
            # Walk through the file structure
            def visitor_func(name, obj):
                if isinstance(obj, h5py.Dataset):
                    dataset_info = {
                        'name': name,
                        'shape': obj.shape,
                        'dtype': str(obj.dtype),
                        'size': obj.size,
                        'compression': obj.compression,
                        'chunks': obj.chunks,
                        'attributes': dict(obj.attrs)
                    }
                    hdf5_metadata['datasets'].append(dataset_info)
                elif isinstance(obj, h5py.Group):
                    group_info = {
                        'name': name,
                        'keys': list(obj.keys()),
                        'attributes': dict(obj.attrs)
                    }
                    hdf5_metadata['groups'].append(group_info)
            
            f.visititems(visitor_func)
            
            # File-level attributes
            hdf5_metadata['attributes'] = dict(f.attrs)
            
            # Structure information
            hdf5_metadata['structure']['num_datasets'] = len(hdf5_metadata['datasets'])
            hdf5_metadata['structure']['num_groups'] = len(hdf5_metadata['groups'])
            hdf5_metadata['structure']['root_keys'] = list(f.keys())
            
            # Compression information
            compression_types = set()
            for ds in hdf5_metadata['datasets']:
                if ds['compression']:
                    compression_types.add(ds['compression'])
            
            hdf5_metadata['compression_info']['types'] = list(compression_types)
            hdf5_metadata['compression_info']['has_compression'] = len(compression_types) > 0
    
    except ImportError:
        logger.warning("h5py not available - HDF5 metadata extraction limited")
        hdf5_metadata['errors'] = ['h5py library not available']
    except Exception as e:
        logger.error(f"Error extracting HDF5 metadata: {str(e)}")
        hdf5_metadata['errors'] = [f'Error: {str(e)}']
    
    return hdf5_metadata


def extract_netcdf_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata from NetCDF files (Network Common Data Form).
    
    Args:
        filepath: Path to the NetCDF file
        
    Returns:
        Dictionary containing NetCDF metadata
    """
    netcdf_metadata = {
        'file_info': {},
        'dimensions': {},
        'variables': {},
        'global_attributes': {},
        'structure': {}
    }
    
    try:
        import netCDF4
        
        with netCDF4.Dataset(filepath, 'r') as dataset:
            # File information
            netcdf_metadata['file_info']['filename'] = dataset.filepath()
            netcdf_metadata['file_info']['format'] = dataset.data_model
            netcdf_metadata['file_info']['title'] = getattr(dataset, 'title', 'N/A')
            netcdf_metadata['file_info']['institution'] = getattr(dataset, 'institution', 'N/A')
            netcdf_metadata['file_info']['source'] = getattr(dataset, 'source', 'N/A')
            netcdf_metadata['file_info']['history'] = getattr(dataset, 'history', 'N/A')
            netcdf_metadata['file_info']['references'] = getattr(dataset, 'references', 'N/A')
            netcdf_metadata['file_info']['comment'] = getattr(dataset, 'comment', 'N/A')
            
            # Dimensions
            for dim_name, dim in dataset.dimensions.items():
                netcdf_metadata['dimensions'][dim_name] = {
                    'size': len(dim) if dim.isunlimited() == False else 'unlimited',
                    'is_unlimited': dim.isunlimited()
                }
            
            # Variables
            for var_name, var in dataset.variables.items():
                var_info = {
                    'dimensions': var.dimensions,
                    'shape': var.shape,
                    'dtype': str(var.dtype),
                    'attributes': {}
                }
                
                # Get variable attributes
                for attr_name in var.ncattrs():
                    var_info['attributes'][attr_name] = getattr(var, attr_name)
                
                netcdf_metadata['variables'][var_name] = var_info
            
            # Global attributes
            for attr_name in dataset.ncattrs():
                netcdf_metadata['global_attributes'][attr_name] = getattr(dataset, attr_name)
            
            # Structure information
            netcdf_metadata['structure']['num_dimensions'] = len(netcdf_metadata['dimensions'])
            netcdf_metadata['structure']['num_variables'] = len(netcdf_metadata['variables'])
            netcdf_metadata['structure']['dimension_names'] = list(dataset.dimensions.keys())
            netcdf_metadata['structure']['variable_names'] = list(dataset.variables.keys())
    
    except ImportError:
        logger.warning("netCDF4 not available - NetCDF metadata extraction limited")
        netcdf_metadata['errors'] = ['netCDF4 library not available']
    except Exception as e:
        logger.error(f"Error extracting NetCDF metadata: {str(e)}")
        netcdf_metadata['errors'] = [f'Error: {str(e)}']
    
    return netcdf_metadata


def extract_geotiff_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata from GeoTIFF files (Geospatial TIFF).
    
    Args:
        filepath: Path to the GeoTIFF file
        
    Returns:
        Dictionary containing GeoTIFF metadata
    """
    geotiff_metadata = {
        'geospatial_info': {},
        'coordinate_system': {},
        'image_info': {},
        'raster_info': {},
        'metadata': {}
    }
    
    try:
        from osgeo import gdal, osr
        import numpy as np
        
        # Open the dataset
        dataset = gdal.Open(filepath)
        if dataset is None:
            logger.error(f"Could not open GeoTIFF file: {filepath}")
            geotiff_metadata['errors'] = ['Could not open file with GDAL']
            return geotiff_metadata
        
        # Geospatial information
        geotiff_metadata['geospatial_info']['projection'] = dataset.GetProjection()
        
        # Get geotransform (contains georeferencing information)
        geotransform = dataset.GetGeoTransform()
        if geotransform:
            geotiff_metadata['geospatial_info']['geotransform'] = {
                'origin_x': geotransform[0],
                'pixel_width': geotransform[1],
                'rotation_1': geotransform[2],
                'origin_y': geotransform[3],
                'rotation_2': geotransform[4],
                'pixel_height': geotransform[5]
            }
        
        # Coordinate system information
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromWkt(dataset.GetProjection())
        geotiff_metadata['coordinate_system']['authority'] = spatial_ref.GetAuthorityName(None) or 'N/A'
        geotiff_metadata['coordinate_system']['code'] = spatial_ref.GetAuthorityCode(None) or 'N/A'
        geotiff_metadata['coordinate_system']['name'] = spatial_ref.GetName() or 'N/A'
        
        # Image information
        geotiff_metadata['image_info']['width'] = dataset.RasterXSize
        geotiff_metadata['image_info']['height'] = dataset.RasterYSize
        geotiff_metadata['image_info']['bands'] = dataset.RasterCount
        geotiff_metadata['image_info']['data_type'] = gdal.GetDataTypeName(dataset.GetRasterBand(1).DataType)
        
        # Raster information
        geotiff_metadata['raster_info']['block_size'] = dataset.GetRasterBand(1).GetBlockSize()
        geotiff_metadata['raster_info']['no_data_value'] = dataset.GetRasterBand(1).GetNoDataValue()
        geotiff_metadata['raster_info']['scale'] = dataset.GetRasterBand(1).GetScale()
        geotiff_metadata['raster_info']['offset'] = dataset.GetRasterBand(1).GetOffset()
        
        # Metadata from all domains
        metadata_domains = dataset.GetMetadataDomainList() or ['']
        for domain in metadata_domains:
            if domain:
                geotiff_metadata['metadata'][domain] = dataset.GetMetadata(domain)
            else:
                geotiff_metadata['metadata']['default'] = dataset.GetMetadata()
        
        # Band-specific information
        geotiff_metadata['bands'] = {}
        for i in range(1, dataset.RasterCount + 1):
            band = dataset.GetRasterBand(i)
            band_info = {
                'data_type': gdal.GetDataTypeName(band.DataType),
                'color_interpretation': gdal.GetColorInterpretationName(band.GetColorInterpretation()),
                'statistics': None
            }
            
            # Get statistics if available
            try:
                stats = band.GetStatistics(True, True)
                if stats:
                    band_info['statistics'] = {
                        'min': stats[0],
                        'max': stats[1],
                        'mean': stats[2],
                        'std_dev': stats[3]
                    }
            except:
                pass  # Statistics not available for this band
            
            geotiff_metadata['bands'][f'band_{i}'] = band_info
        
        # Calculate bounding box
        gt = geotiff_metadata['geospatial_info'].get('geotransform', {})
        if gt:
            minx = gt['origin_x']
            maxy = gt['origin_y']
            maxx = minx + gt['pixel_width'] * geotiff_metadata['image_info']['width']
            miny = maxy + gt['pixel_height'] * geotiff_metadata['image_info']['height']
            
            geotiff_metadata['geospatial_info']['bounding_box'] = {
                'min_x': minx,
                'min_y': miny,
                'max_x': maxx,
                'max_y': maxy
            }
    
    except ImportError:
        logger.warning("gdal not available - GeoTIFF metadata extraction limited")
        geotiff_metadata['errors'] = ['GDAL library not available']
    except Exception as e:
        logger.error(f"Error extracting GeoTIFF metadata: {str(e)}")
        geotiff_metadata['errors'] = [f'Error: {str(e)}']
    finally:
        try:
            dataset = None  # Clean up GDAL dataset reference
        except:
            pass
    
    return geotiff_metadata


# Module-level function to be called by the extraction engine
def extract_scientific_metadata_extended(filepath: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extended scientific metadata extraction function that integrates with the main extraction engine.
    
    Args:
        filepath: Path to the file to extract metadata from
        result: The main result dictionary to update
        
    Returns:
        Updated result dictionary with scientific metadata
    """
    try:
        scientific_result = extract_scientific_metadata(filepath)
        
        # Add scientific metadata to the main result
        if scientific_result.get('extraction_success', False):
            result['scientific_metadata'] = scientific_result.get('scientific_metadata', {})
            result['scientific_format_type'] = scientific_result.get('format_type', 'unknown')
        
        # Add any errors to the main result
        errors = scientific_result.get('errors', [])
        if errors:
            if 'extraction_errors' not in result:
                result['extraction_errors'] = {}
            result['extraction_errors']['scientific_extraction'] = errors
    
    except Exception as e:
        logger.error(f"Error in extended scientific metadata extraction: {str(e)}")
        if 'extraction_errors' not in result:
            result['extraction_errors'] = {}
        result['extraction_errors']['scientific_extraction'] = [f"Extended extraction error: {str(e)}"]
    
    return result


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_scientific_metadata(filepath)
        import json
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python scientific_metadata_extractor.py <filepath>")