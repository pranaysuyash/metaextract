import importlib
import types

from server.extractor import metadata_engine as me


def test_tierconfig_has_phase2_flags():
    tc = me.TierConfig()
    assert hasattr(tc, 'video_codec_details')
    assert hasattr(tc, 'container_details')
    assert hasattr(tc, 'audio_codec_details')
    assert not tc.video_codec_details
    assert not tc.container_details
    assert not tc.audio_codec_details


def test_phase2_module_availability():
    # Just ensure functions exist and are importable
    m = importlib.import_module('server.extractor.modules')
    assert hasattr(m, 'get_video_codec_field_count')
    assert hasattr(m, 'get_perceptual_comparison_field_count')

    # Ensure metadata_engine knows about availability flags
    assert hasattr(me, 'VIDEO_CODEC_DETAILS_AVAILABLE')
    assert hasattr(me, 'CONTAINER_METADATA_AVAILABLE')
    assert hasattr(me, 'AUDIO_CODEC_DETAILS_AVAILABLE')
