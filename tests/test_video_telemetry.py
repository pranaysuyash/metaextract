from server.extractor.modules import video_telemetry as vt


def test_parse_telemetry_summarizes_sources_and_gps():
    raw = {
        "GPMF:GPSLatitude": [37.1, 37.2, 37.3],
        "GPMF:GPSLongitude": [-122.1, -122.2, -122.3],
        "GPMF:GPSAltitude": [10, 12, 9],
        "GoPro:Accelerometer": [[0.1, 0.2, 0.3], [0.0, 0.1, 0.2]],
        "DJI:FlightYawDegree": [1, 2, 3, 4],
        "QuickTime:CreationDate": "2023:01:01 00:00:00",
    }

    telemetry = vt._parse_telemetry(raw)

    assert telemetry["telemetry_present"] is True
    assert set(telemetry["sources"]) == {"gpmf", "gopro", "dji"}
    assert telemetry["gpmf"]["GPSLatitude"]["min"] == 37.1
    assert telemetry["gpmf"]["GPSLongitude"]["max"] == -122.1
    assert telemetry["gopro"]["Accelerometer"]["count"] == 6
    assert telemetry["gps"]["bounds"]["min_lat"] == 37.1
    assert telemetry["gps"]["bounds"]["max_lat"] == 37.3
    assert telemetry["gps"]["bounds"]["min_lon"] == -122.3
    assert telemetry["gps"]["bounds"]["max_lon"] == -122.1
