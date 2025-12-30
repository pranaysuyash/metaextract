from server.extractor.modules import audio_codec_details as acd


def test_get_audio_codec_field_count():
    assert hasattr(acd, 'get_audio_codec_details_field_count')
    c = acd.get_audio_codec_details_field_count()
    assert isinstance(c, int) and c > 0


def test_parse_flac_streaminfo():
    # Construct a minimal valid STREAMINFO block (34 bytes)
    # min_block_size(2), max_block_size(2), min_frame_size(3), max_frame_size(3), sample_rate/channels/bits/total_samples(8), md5(16)
    data = bytearray(34)
    data[0:2] = (4096).to_bytes(2, 'big')  # min block
    data[2:4] = (4096).to_bytes(2, 'big')  # max block
    data[4:7] = (0).to_bytes(3, 'big')
    data[7:10] = (0).to_bytes(3, 'big')
    # sample rate = 44100 -> place into bytes 10..12.. etc (20-bit)
    sample_rate = 44100
    # place sample rate
    data[10] = (sample_rate >> 12) & 0xFF
    data[11] = (sample_rate >> 4) & 0xFF
    data[12] = ((sample_rate & 0xF) << 4) & 0xF0
    # channels = 2 -> bits
    data[12] |= ((2 - 1) << 1) & 0x0E
    # bits per sample = 16 -> place into data[12..13]
    data[12] |= (0 >> 4) & 0x01
    data[13] = (0x00)
    # total samples (36 bits)
    total_samples = 44100 * 10
    data[14:19] = total_samples.to_bytes(5, 'big')
    # md5 (last 16 bytes) leave zero

    info = acd.parse_flac_streaminfo(bytes(data))
    assert info['sample_rate'] == 44100
    assert info['channels'] == 2
    assert info['bits_per_sample'] >= 1
    assert 'md5_signature' in info
