import importlib
from server.extractor.modules import video_codec_details as vcd


def test_video_codec_field_count():
    # Ensure field count function is present and returns expected positive integer
    assert hasattr(vcd, 'get_video_codec_details_field_count')
    count = vcd.get_video_codec_details_field_count()
    assert isinstance(count, int) and count > 0


def test_extract_h264_deep_analysis_basic():
    # Mock a simple video stream descriptor for H.264
    stream = {
        'codec_name': 'h264',
        'codec_long_name': 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10',
        'profile': 100,
        'level': 42,
        'pix_fmt': 'yuv420p10le',
        'width': 1920,
        'height': 1080,
        'r_frame_rate': '30000/1001',
        'avg_frame_rate': '30000/1001',
        'has_b_frames': 2,
        'refs': 4,
        'bit_rate': '5000000',
        'duration': '60.0',
    }

    result = vcd.extract_h264_deep_analysis(stream, '/dev/null')

    # Basic assertions on expected keys and value types
    assert result.get('codec_name') == 'h264'
    assert result.get('profile_idc') == 100
    assert result.get('level_idc') == 42
    assert result.get('bit_depth_luma') == 10
    assert result.get('width_pixels') == 1920
    assert result.get('height_pixels') == 1080
    assert result.get('has_b_frames') is True
    assert isinstance(result.get('bit_rate_bps'), int) or result.get('bit_rate_bps') is None


def test_extract_video_codec_details_with_mocked_ffprobe(monkeypatch):
    # Monkeypatch run_ffprobe to return a simple ffprobe-like dict
    fake_probe = {
        'format': {'format_name': 'mov,mp4,m4a,3gp,3g2,mj2', 'duration': '60.0', 'bit_rate': '8000000', 'size': '6000000', 'nb_streams': 2},
        'streams': [
            {
                'codec_type': 'video',
                'codec_name': 'h264',
                'codec_long_name': 'H.264 / AVC',
                'profile': 100,
                'level': 42,
                'pix_fmt': 'yuv420p10le',
                'width': 3840,
                'height': 2160,
                'r_frame_rate': '30000/1001',
                'avg_frame_rate': '30000/1001',
                'nb_frames': '1800',
                'bit_rate': '7000000',
                'tags': {'language': 'eng'}
            }
        ]
    }

    monkeypatch.setattr(vcd, 'run_ffprobe', lambda path: fake_probe)
    res = vcd.extract_video_codec_details('/nonexistent/file.mp4')

    assert 'h264_deep' in res
    assert res['h264_deep'].get('codec_name') == 'h264'
    assert res['hdr_metadata'].get('is_hdr') in (True, False)
    assert isinstance(res['fields_extracted'], int)
