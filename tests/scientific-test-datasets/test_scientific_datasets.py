#!/usr/bin/env python3
"""
Test script to verify the generated scientific test datasets work with MetaExtract
"""

import sys
import os
from pathlib import Path

# Add server path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

def test_dicom_datasets():
    """Test DICOM dataset extraction"""
    print("Testing DICOM datasets...")

    try:
        from server.extractor.modules import scientific_medical as sm

        dicom_files = [
            "tests/scientific-test-datasets/scientific-test-datasets/dicom/ct_scan/ct_scan.dcm",
            "tests/scientific-test-datasets/scientific-test-datasets/dicom/mri_scan/mri_scan.dcm",
            "tests/scientific-test-datasets/scientific-test-datasets/dicom/ultrasound/ultrasound.dcm"
        ]

        for dicom_file in dicom_files:
            if os.path.exists(dicom_file):
                print(f"  Testing {dicom_file}...")
                result = sm.extract_dicom_metadata(dicom_file)
                if result.get("success"):
                    print(f"    ✓ Successfully extracted metadata: {result.get('fields_extracted', 0)} fields")
                else:
                    print(f"    ✗ Failed to extract metadata: {result.get('error', 'Unknown error')}")
            else:
                print(f"  ✗ File not found: {dicom_file}")

    except Exception as e:
        print(f"  ✗ Error testing DICOM: {e}")

def test_fits_datasets():
    """Test FITS dataset extraction"""
    print("\nTesting FITS datasets...")

    try:
        from server.extractor.modules import scientific_data as sd

        fits_files = [
            "tests/scientific-test-datasets/scientific-test-datasets/fits/hst_observation/hst_observation.fits",
            "tests/scientific-test-datasets/scientific-test-datasets/fits/chandra_observation/chandra_observation.fits",
            "tests/scientific-test-datasets/scientific-test-datasets/fits/sdss_spectrum/sdss_spectrum.fits"
        ]

        for fits_file in fits_files:
            if os.path.exists(fits_file):
                print(f"  Testing {fits_file}...")
                result = sd.extract_fits_metadata(fits_file)
                if result.get("success"):
                    print(f"    ✓ Successfully extracted metadata: {result.get('fields_extracted', 0)} fields")
                else:
                    print(f"    ✗ Failed to extract metadata: {result.get('error', 'Unknown error')}")
            else:
                print(f"  ✗ File not found: {fits_file}")

    except Exception as e:
        print(f"  ✗ Error testing FITS: {e}")

def test_hdf5_netcdf_datasets():
    """Test HDF5/NetCDF dataset extraction"""
    print("\nTesting HDF5/NetCDF datasets...")

    try:
        from server.extractor.modules import scientific_data as sd

        # Test NetCDF climate model
        nc_file = "tests/scientific-test-datasets/scientific-test-datasets/hdf5_netcdf/climate_model/climate_model.nc"
        if os.path.exists(nc_file):
            print(f"  Testing NetCDF climate model: {nc_file}...")
            result = sd.extract_netcdf_metadata(nc_file)
            if result.get("success"):
                print(f"    ✓ Successfully extracted NetCDF metadata: {result.get('fields_extracted', 0)} fields")
            else:
                print(f"    ✗ Failed to extract NetCDF metadata: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ NetCDF file not found: {nc_file}")

        # Test HDF5 weather radar
        h5_file = "tests/scientific-test-datasets/scientific-test-datasets/hdf5_netcdf/weather_radar/weather_radar.h5"
        if os.path.exists(h5_file):
            print(f"  Testing HDF5 weather radar: {h5_file}...")
            result = sd.extract_hdf5_metadata(h5_file)
            if result.get("success"):
                print(f"    ✓ Successfully extracted HDF5 metadata: {result.get('fields_extracted', 0)} fields")
            else:
                print(f"    ✗ Failed to extract HDF5 metadata: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ HDF5 file not found: {h5_file}")

    except Exception as e:
        print(f"  ✗ Error testing HDF5/NetCDF: {e}")

def main():
    """Run all tests"""
    print("=== Testing Scientific Test Datasets with MetaExtract ===\n")

    test_dicom_datasets()
    test_fits_datasets()
    test_hdf5_netcdf_datasets()

    print("\n=== Test Summary ===")
    print("Scientific test datasets have been generated and are ready for testing.")
    print("Use these datasets to validate MetaExtract's scientific format support.")

if __name__ == "__main__":
    main()