from server.extractor.modules import scientific_data as sd


def test_extract_hdf5_metadata_roundtrip(tmp_path):
    if not sd.HDF5_AVAILABLE:
        result = sd.extract_hdf5_metadata("missing.h5")
        assert result["available"] is False
        return

    import h5py

    path = tmp_path / "sample.h5"
    with h5py.File(path, "w") as hdf:
        hdf.attrs["title"] = "demo"
        dataset = hdf.create_dataset("data", data=[1, 2, 3])
        dataset.attrs["units"] = "count"

    result = sd.extract_hdf5_metadata(str(path))
    assert result["available"] is True
    assert result["file_info"]["total_datasets"] == 1
    assert "data" in result["datasets"]


def test_extract_netcdf_metadata_roundtrip(tmp_path):
    if not sd.NETCDF_AVAILABLE:
        result = sd.extract_netcdf_metadata("missing.nc")
        assert result["available"] is False
        return

    import netCDF4

    path = tmp_path / "sample.nc"
    with netCDF4.Dataset(path, "w") as nc:
        nc.createDimension("time", None)
        temp = nc.createVariable("temperature", "f4", ("time",))
        temp.units = "K"
        temp[:] = [280.1, 281.2]
        nc.title = "demo"

    result = sd.extract_netcdf_metadata(str(path))
    assert result["available"] is True
    assert "temperature" in result["variables"]
    assert result["file_info"]["num_dimensions"] == 1
