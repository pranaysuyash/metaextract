#!/usr/bin/env python3
"""Music Production/DSP Metadata Field Inventory

Comprehensive inventory of music production/DSP metadata fields covering:
1. DAW Projects - 60 fields (Session info, tempo, time signature, track layout)
2. Audio Effects - 50 fields (EQ, compression, reverb, delay parameters)
3. MIDI Data - 50 fields (Note, velocity, control change, program change)
4. Mastering - 50 fields (Loudness, true peak, dynamic range, EBU R128)
5. Plugin Formats - 50 fields (VST, AU, AAX, CLAP parameters)
6. Stem/Bus Routing - 50 fields (Submix, bus processing, routing matrix)
7. Sample Libraries - 40 fields (Kontakt, Spitfire, EastWest articulations)

Total: 350+ metadata fields

References:
- Digital Audio Workstation project formats
- Audio Effect Processing Standards (DSP)
- MIDI 1.0/2.0 Specifications
- EBU R128 Loudness Standard
- Plugin Format Specifications (VST3, AU, AAX, CLAP)
- Sample Library Documentation
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


def get_daw_project_fields() -> List[Dict[str, Any]]:
    """Get DAW Project metadata fields - 60 fields."""
    return [
        {"name": "daw.project_name", "description": "Project/session name", "type": "text"},
        {"name": "daw.project_path", "description": "Project file path", "type": "text"},
        {"name": "daw.project_format", "description": "Project format (session/proj)", "type": "text"},
        {"name": "daw.daw_name", "description": "DAW software name", "type": "text"},
        {"name": "daw.daw_version", "description": "DAW version number", "type": "text"},
        {"name": "daw.daw_build", "description": "DAW build number", "type": "text"},
        {"name": "daw.sample_rate", "description": "Project sample rate in Hz", "type": "integer"},
        {"name": "daw.bit_depth", "description": "Project bit depth", "type": "integer"},
        {"name": "daw.tempo", "description": "Project tempo in BPM", "type": "float"},
        {"name": "daw.tempo_numerator", "description": "Tempo numerator for automation", "type": "integer"},
        {"name": "daw.tempo_denominator", "description": "Tempo denominator for automation", "type": "integer"},
        {"name": "daw.time_signature_numerator", "description": "Time signature numerator", "type": "integer"},
        {"name": "daw.time_signature_denominator", "description": "Time signature denominator", "type": "integer"},
        {"name": "daw.time_signature", "description": "Time signature (e.g., 4/4, 6/8)", "type": "text"},
        {"name": "daw.key_signature", "description": "Key signature (e.g., C Major, G Minor)", "type": "text"},
        {"name": "daw.metronome_enabled", "description": "Metronome enabled flag", "type": "boolean"},
        {"name": "daw.metronome_click_track", "description": "Metronome click track reference", "type": "text"},
        {"name": "daw.count_in_enabled", "description": "Count-in enabled", "type": "boolean"},
        {"name": "daw.count_in_bars", "description": "Count-in bar count", "type": "integer"},
        {"name": "daw.loop_enabled", "description": "Loop playback enabled", "type": "boolean"},
        {"name": "daw.loop_start", "description": "Loop start position in samples", "type": "integer"},
        {"name": "daw.loop_end", "description": "Loop end position in samples", "type": "integer"},
        {"name": "daw.punch_in_enabled", "description": "Punch-in recording enabled", "type": "boolean"},
        {"name": "daw.punch_in_point", "description": "Punch-in point in samples", "type": "integer"},
        {"name": "daw.punch_out_point", "description": "Punch-out point in samples", "type": "integer"},
        {"name": "daw.track_count", "description": "Total number of tracks", "type": "integer"},
        {"name": "daw.audio_track_count", "description": "Number of audio tracks", "type": "integer"},
        {"name": "daw.midi_track_count", "description": "Number of MIDI tracks", "type": "integer"},
        {"name": "daw.bus_count", "description": "Number of aux/bus tracks", "type": "integer"},
        {"name": "daw.master_track_count", "description": "Number of master outputs", "type": "integer"},
        {"name": "daw.channel_strip_count", "description": "Total channel strips", "type": "integer"},
        {"name": "daw.plugin_count", "description": "Total plugin instances", "type": "integer"},
        {"name": "daw.sends_count", "description": "Total send connections", "type": "integer"},
        {"name": "daw.returns_count", "description": "Total return tracks", "type": "integer"},
        {"name": "daw.vca_count", "description": "VCA track count", "type": "integer"},
        {"name": "daw.group_count", "description": "Track group count", "type": "integer"},
        {"name": "daw.markers_count", "description": "Number of markers", "type": "integer"},
        {"name": "daw.marker_regions", "description": "Marker region data", "type": "array"},
        {"name": "daw.cues_count", "description": "Cue point count", "type": "integer"},
        {"name": "daw.cue_points", "description": "Cue point data", "type": "array"},
        {"name": "daw.timecode_start", "description": "Start timecode (SMPTE)", "type": "text"},
        {"name": "daw.timecode_format", "description": "Timecode format (25fps, 30fps, etc.)", "type": "text"},
        {"name": "daw.smpte_offset", "description": "SMPTE offset", "type": "text"},
        {"name": "daw.sample_offset", "description": "Sample offset value", "type": "integer"},
        {"name": "daw.frames_per_second", "description": "Video frame rate for sync", "type": "float"},
        {"name": "daw.video_frame_rate", "description": "Video frame rate", "type": "float"},
        {"name": "daw.video_track_count", "description": "Number of video tracks", "type": "integer"},
        {"name": "daw.video_resolution", "description": "Video resolution (e.g., 1920x1080)", "type": "text"},
        {"name": "daw.video_codec", "description": "Video codec name", "type": "text"},
        {"name": "daw.project_color", "description": "Project color code", "type": "text"},
        {"name": "daw.creation_date", "description": "Project creation date", "type": "datetime"},
        {"name": "daw.modification_date", "description": "Last modification date", "type": "datetime"},
        {"name": "daw.author", "description": "Project author/creator", "type": "text"},
        {"name": "daw.comments", "description": "Project comments", "type": "text"},
        {"name": "daw.custom_fields", "description": "Custom project fields", "type": "object"},
        {"name": "daw.session_notes", "description": "Session notes text", "type": "text"},
        {"name": "daw.revision_number", "description": "Project revision number", "type": "integer"},
        {"name": "daw.backup_count", "description": "Backup file count", "type": "integer"},
        {"name": "daw.auto_save_enabled", "description": "Auto-save enabled", "type": "boolean"},
        {"name": "daw.auto_save_interval", "description": "Auto-save interval in minutes", "type": "integer"},
    ]


def get_audio_effects_fields() -> List[Dict[str, Any]]:
    """Get Audio Effects metadata fields - 50 fields."""
    return [
        {"name": "fx.eq_enabled", "description": "EQ effect enabled", "type": "boolean"},
        {"name": "fx.eq_bands", "description": "Number of EQ bands", "type": "integer"},
        {"name": "fx.eq_low_shelf_freq", "description": "Low shelf frequency in Hz", "type": "float"},
        {"name": "fx.eq_low_shelf_gain", "description": "Low shelf gain in dB", "type": "float"},
        {"name": "fx.eq_low_shelf_q", "description": "Low shelf Q factor", "type": "float"},
        {"name": "fx.eq_mid_freq", "description": "Mid band frequency in Hz", "type": "float"},
        {"name": "fx.eq_mid_gain", "description": "Mid band gain in dB", "type": "float"},
        {"name": "fx.eq_mid_q", "description": "Mid band Q factor", "type": "float"},
        {"name": "fx.eq_high_shelf_freq", "description": "High shelf frequency in Hz", "type": "float"},
        {"name": "fx.eq_high_shelf_gain", "description": "High shelf gain in dB", "type": "float"},
        {"name": "fx.eq_high_shelf_q", "description": "High shelf Q factor", "type": "float"},
        {"name": "fx.eq_high_pass_freq", "description": "High pass filter frequency", "type": "float"},
        {"name": "fx.eq_low_pass_freq", "description": "Low pass filter frequency", "type": "float"},
        {"name": "fx.eq_band_frequency", "description": "Parametric band frequency", "type": "float"},
        {"name": "fx.eq_band_gain", "description": "Parametric band gain", "type": "float"},
        {"name": "fx.eq_band_q", "description": "Parametric band Q", "type": "float"},
        {"name": "fx.compression_enabled", "description": "Compression effect enabled", "type": "boolean"},
        {"name": "fx.compression_threshold", "description": "Threshold in dB", "type": "float"},
        {"name": "fx.compression_ratio", "description": "Compression ratio (e.g., 4:1)", "type": "float"},
        {"name": "fx.compression_knee", "description": "Knee width in dB", "type": "float"},
        {"name": "fx.compression_attack", "description": "Attack time in ms", "type": "float"},
        {"name": "fx.compression_release", "description": "Release time in ms", "type": "float"},
        {"name": "fx.compression_makeup_gain", "description": "Makeup gain in dB", "type": "float"},
        {"name": "fx.compression_gain_reduction", "description": "Current gain reduction in dB", "type": "float"},
        {"name": "fx.compression_mode", "description": "Compression mode (peak/RMS)", "type": "text"},
        {"name": "fx.compression_detection", "description": "Detection mode (feedforward/feedback)", "type": "text"},
        {"name": "fx.compressor_linked", "description": "Linked channel compression", "type": "boolean"},
        {"name": "fx.reverb_enabled", "description": "Reverb effect enabled", "type": "boolean"},
        {"name": "fx.reverb_type", "description": "Reverb type (hall/room/plate)", "type": "text"},
        {"name": "fx.reverb_decay_time", "description": "Decay time in seconds", "type": "float"},
        {"name": "fx.reverb_pre_delay", "description": "Pre-delay in ms", "type": "float"},
        {"name": "fx.reverb_hi_damp", "description": "High frequency damping %", "type": "float"},
        {"name": "fx.reverb_lo_damp", "description": "Low frequency damping %", "type": "float"},
        {"name": "fx.reverb_diffusion", "description": "Diffusion amount %", "type": "float"},
        {"name": "fx.reverb_size", "description": "Room size parameter", "type": "float"},
        {"name": "fx.reverb_mix", "description": "Reverb mix (dry/wet)", "type": "float"},
        {"name": "fx.reverb_wet_level", "description": "Wet signal level in dB", "type": "float"},
        {"name": "fx.reverb_dry_level", "description": "Dry signal level in dB", "type": "float"},
        {"name": "fx.delay_enabled", "description": "Delay effect enabled", "type": "boolean"},
        {"name": "fx.delay_type", "description": "Delay type (tape/digital)", "type": "text"},
        {"name": "fx.delay_time", "description": "Delay time in ms", "type": "float"},
        {"name": "fx.delay_sync", "description": "Delay synced to tempo", "type": "boolean"},
        {"name": "fx.delay_note_value", "description": "Delay note value (e.g., 1/8)", "type": "text"},
        {"name": "fx.delay_feedback", "description": "Feedback amount %", "type": "float"},
        {"name": "fx.delay_mix", "description": "Delay mix (dry/wet)", "type": "float"},
        {"name": "fx.delay_filter_freq", "description": "Delay filter frequency", "type": "float"},
        {"name": "fx.distortion_enabled", "description": "Distortion effect enabled", "type": "boolean"},
        {"name": "fx.distortion_type", "description": "Distortion type (tube/saturator)", "type": "text"},
        {"name": "fx.distortion_drive", "description": "Drive amount", "type": "float"},
        {"name": "fx.distortion_tone", "description": "Tone control", "type": "float"},
        {"name": "fx.distortion_mix", "description": "Distortion mix", "type": "float"},
    ]


def get_midi_data_fields() -> List[Dict[str, Any]]:
    """Get MIDI Data metadata fields - 50 fields."""
    return [
        {"name": "midi.note_number", "description": "MIDI note number (0-127)", "type": "integer"},
        {"name": "midi.note_name", "description": "MIDI note name (C4, A3, etc.)", "type": "text"},
        {"name": "midi.note_frequency", "description": "Note frequency in Hz", "type": "float"},
        {"name": "midi.velocity", "description": "Note velocity (0-127)", "type": "integer"},
        {"name": "midi.velocity_scaled", "description": "Scaled velocity value", "type": "float"},
        {"name": "midi.channel", "description": "MIDI channel (1-16)", "type": "integer"},
        {"name": "midi.port", "description": "MIDI port number", "type": "integer"},
        {"name": "midi.status", "description": "MIDI status byte", "type": "integer"},
        {"name": "midi.status_message", "description": "MIDI status message type", "type": "text"},
        {"name": "midi.program_number", "description": "Program change number (0-127)", "type": "integer"},
        {"name": "midi.program_name", "description": "Program/instrument name", "type": "text"},
        {"name": "midi.bank_select_msb", "description": "Bank Select MSB (CC 0)", "type": "integer"},
        {"name": "midi.bank_select_lsb", "description": "Bank Select LSB (CC 32)", "type": "integer"},
        {"name": "midi.pitch_bend", "description": "Pitch bend value (-8192 to 8191)", "type": "integer"},
        {"name": "midi.pitch_bend_msb", "description": "Pitch bend MSB", "type": "integer"},
        {"name": "midi.pitch_bend_sensitivity", "description": "Pitch bend sensitivity in semitones", "type": "float"},
        {"name": "midi.cc_1_modulation", "description": "CC1 Modulation Wheel", "type": "integer"},
        {"name": "midi.cc_2_breath", "description": "CC2 Breath Controller", "type": "integer"},
        {"name": "midi.cc_7_volume", "description": "CC7 Volume", "type": "integer"},
        {"name": "midi.cc_10_pan", "description": "CC10 Pan", "type": "integer"},
        {"name": "midi.cc_11_expression", "description": "CC11 Expression", "type": "integer"},
        {"name": "midi.cc_64_sustain", "description": "CC64 Sustain Pedal", "type": "integer"},
        {"name": "midi.cc_66_sostenuto", "description": "CC66 Sostenuto Pedal", "type": "integer"},
        {"name": "midi.cc_67_soft_pedal", "description": "CC67 Soft Pedal", "type": "integer"},
        {"name": "midi.cc_91_reverb", "description": "CC91 Reverb Send", "type": "integer"},
        {"name": "midi.cc_93_chorus", "description": "CC93 Chorus Send", "type": "integer"},
        {"name": "midi.cc_74_cutoff", "description": "CC74 Filter Cutoff", "type": "integer"},
        {"name": "midi.cc_71_resonance", "description": "CC71 Filter Resonance", "type": "integer"},
        {"name": "midi.cc_73_attack_time", "description": "CC73 Attack Time", "type": "integer"},
        {"name": "midi.cc_72_release_time", "description": "CC72 Release Time", "type": "integer"},
        {"name": "midi.cc_76_portamento", "description": "CC76 Portamento Rate", "type": "integer"},
        {"name": "midi.cc_77_portamento_on", "description": "CC77 Portamento On/Off", "type": "integer"},
        {"name": "midi.aftertouch_channel", "description": "Channel aftertouch value", "type": "integer"},
        {"name": "midi.aftertouch_poly", "description": "Poly aftertouch values", "type": "array"},
        {"name": "midi.poly_pressure_note", "description": "Poly pressure note number", "type": "integer"},
        {"name": "midi.poly_pressure_value", "description": "Poly pressure value", "type": "integer"},
        {"name": "midi.note_on_time", "description": "Note on timestamp", "type": "float"},
        {"name": "midi.note_off_time", "description": "Note off timestamp", "type": "float"},
        {"name": "midi.note_duration", "description": "Note duration in beats", "type": "float"},
        {"name": "midi.note_start_bar", "description": "Note start bar number", "type": "integer"},
        {"name": "midi.note_start_beat", "description": "Note start beat number", "type": "float"},
        {"name": "midi.note_tick_position", "description": "Note tick position", "type": "integer"},
        {"name": "midi.tick_length", "description": "Note length in ticks", "type": "integer"},
        {"name": "midi.clock_tempo", "description": "MIDI clock tempo", "type": "integer"},
        {"name": "midi.clock_ticks_per_beat", "description": "Ticks per quarter note (PPQ)", "type": "integer"},
        {"name": "midi.song_position_pointer", "description": "Song position in 16th notes", "type": "integer"},
        {"name": "midi.timing_clock", "description": "Timing clock message", "type": "boolean"},
        {"name": "midi.start_message", "description": "Start message", "type": "boolean"},
        {"name": "midi.stop_message", "description": "Stop message", "type": "boolean"},
        {"name": "midi.continue_message", "description": "Continue message", "type": "boolean"},
    ]


def get_mastering_fields() -> List[Dict[str, Any]]:
    """Get Mastering metadata fields - 50 fields."""
    return [
        {"name": "mastering.integrated_loudness", "description": "Integrated loudness in LUFS (ITU-R BS.1770)", "type": "float"},
        {"name": "mastering.loudness_range", "description": "Loudness Range (LRA) in LU", "type": "float"},
        {"name": "mastering.lra_low", "description": "LRA low threshold in LUFS", "type": "float"},
        {"name": "mastering.lra_high", "description": "LRA high threshold in LUFS", "type": "float"},
        {"name": "mastering.true_peak_level", "description": "True peak level in dBTP", "type": "float"},
        {"name": "mastering.true_peak_peak", "description": "True peak value", "type": "float"},
        {"name": "mastering.shortterm_loudness", "description": "Short-term loudness in LUFS", "type": "float"},
        {"name": "mastering.momentary_loudness", "description": "Momentary loudness in LUFS", "type": "float"},
        {"name": "mastering.maximum_momentary", "description": "Maximum momentary loudness in LUFS", "type": "float"},
        {"name": "mastering.maximum_shortterm", "description": "Maximum short-term loudness in LUFS", "type": "float"},
        {"name": "mastering.target_loudness", "description": "Target loudness in LUFS (e.g., -14, -16)", "type": "float"},
        {"name": "mastering.ebur128_compliant", "description": "EBU R128 compliant flag", "type": "boolean"},
        {"name": "mastering.ebur128_mode", "description": "EBU R128 mode (program/momentary)", "type": "text"},
        {"name": "mastering.measurement_offset", "description": "Measurement offset in samples", "type": "integer"},
        {"name": "mastering.measurement_window", "description": "Measurement window in seconds", "type": "float"},
        {"name": "mastering.absolute_true_peak", "description": "Absolute true peak measurement", "type": "boolean"},
        {"name": "mastering.sample_peak_level", "description": "Sample peak level in dBTP", "type": "float"},
        {"name": "mastering.peak_hold_time", "description": "Peak hold time in seconds", "type": "float"},
        {"name": "mastering.dynamic_range", "description": "Dynamic range in dB", "type": "float"},
        {"name": "mastering.dynamic_range_dr", "description": "DR (Dynamic Range) value", "type": "float"},
        {"name": "mastering.crest_factor", "description": "Crest factor (peak/RMS ratio)", "type": "float"},
        {"name": "mastering.peak_to_loudness", "description": "Peak to loudness ratio", "type": "float"},
        {"name": "mastering.gain_adjustment", "description": "Gain adjustment in dB", "type": "float"},
        {"name": "mastering.linearity_gain", "description": "Linearity gain in dB", "type": "float"},
        {"name": "mastering.limiter_threshold", "description": "Limiter threshold in dB", "type": "float"},
        {"name": "mastering.limiter_release", "description": "Limiter release time", "type": "float"},
        {"name": "mastering.limiter_gain_reduction", "description": "Limiter gain reduction in dB", "type": "float"},
        {"name": "mastering.true_peak_limit", "description": "True peak limiting applied", "type": "boolean"},
        {"name": "mastering.inter_sample_clipping", "description": "Inter-sample clipping detected", "type": "boolean"},
        {"name": "mastering.inter_sample_peak", "description": "Inter-sample peak value", "type": "float"},
        {"name": "mastering.high_pass_filter", "description": "High pass filter frequency", "type": "float"},
        {"name": "mastering.low_pass_filter", "description": "Low pass filter frequency", "type": "float"},
        {"name": "mastering.stereo_width", "description": "Stereo width adjustment", "type": "float"},
        {"name": "mastering.stereo_correlation", "description": "Stereo correlation coefficient", "type": "float"},
        {"name": "mastering.phase_correlation", "description": "Phase correlation value", "type": "float"},
        {"name": "mastering.mono_compatibility", "description": "Mono compatibility check", "type": "boolean"},
        {"name": "mastering.lfe_channel_level", "description": "LFE channel level in dB", "type": "float"},
        {"name": "mastering.downmix_level", "description": "Downmix level in dB", "type": "float"},
        {"name": "mastering.dialogue_level", "description": "Dialogue normalization level", "type": "float"},
        {"name": "mastering.program_level", "description": "Program level in LUFS", "type": "float"},
        {"name": "mastering.anchor_level", "description": "Anchor level in LUFS", "type": "float"},
        {"name": "mastering.relative_peak", "description": "Relative peak threshold", "type": "float"},
        {"name": "mastering.gating_threshold", "description": "Gating threshold in LUFS", "type": "float"},
        {"name": "mastering.measurement_type", "description": "Measurement type (absolute/relative)", "type": "text"},
        {"name": "mastering.channel_configuration", "description": "Channel configuration (5.1, stereo, etc.)", "type": "text"},
        {"name": "mastering.loudness_standard", "description": "Loudness standard (ATSC A/85, EBU R128)", "type": "text"},
        {"name": "mastering.target_region", "description": "Target region (US, EU, etc.)", "type": "text"},
        {"name": "mastering.measured_by", "description": "Measurement tool name", "type": "text"},
        {"name": "mastering.measurement_date", "description": "Measurement date and time", "type": "datetime"},
    ]


def get_plugin_format_fields() -> List[Dict[str, Any]]:
    """Get Plugin Format metadata fields - 50 fields."""
    return [
        {"name": "plugin.vst_id", "description": "VST plugin unique ID", "type": "integer"},
        {"name": "plugin.vst_name", "description": "VST plugin name", "type": "text"},
        {"name": "plugin.vst_version", "description": "VST plugin version", "type": "integer"},
        {"name": "plugin.vst_category", "description": "VST category (effect/instrument)", "type": "text"},
        {"name": "plugin.vst_sub_category", "description": "VST sub-category", "type": "text"},
        {"name": "plugin.vst_sdk_version", "description": "VST SDK version used", "type": "text"},
        {"name": "plugin.vst3_id", "description": "VST3 plugin unique ID", "type": "text"},
        {"name": "plugin.vst3_bundles", "description": "VST3 bundle count", "type": "integer"},
        {"name": "plugin.vst3_audio_in", "description": "VST3 audio inputs count", "type": "integer"},
        {"name": "plugin.vst3_audio_out", "description": "VST3 audio outputs count", "type": "integer"},
        {"name": "plugin.vst3_midi_in", "description": "VST3 MIDI inputs count", "type": "integer"},
        {"name": "plugin.vst3_midi_out", "description": "VST3 MIDI outputs count", "type": "integer"},
        {"name": "plugin.vst3_parameters", "description": "VST3 parameter count", "type": "integer"},
        {"name": "plugin.vst3_bypass", "description": "VST3 bypass supported", "type": "boolean"},
        {"name": "plugin.au_type_id", "description": "AU (Audio Unit) type ID", "type": "integer"},
        {"name": "plugin.au_sub_type", "description": "AU sub-type", "type": "integer"},
        {"name": "plugin.au_manufacturer", "description": "AU manufacturer code", "type": "integer"},
        {"name": "plugin.au_component_type", "description": "AU component type", "type": "integer"},
        {"name": "plugin.au_factory", "description": "AU factory preset count", "type": "integer"},
        {"name": "plugin.au_user", "description": "AU user preset count", "type": "integer"},
        {"name": "plugin.au_latency", "description": "AU latency in samples", "type": "integer"},
        {"name": "plugin.au_tail_time", "description": "AU tail time in seconds", "type": "float"},
        {"name": "plugin.aax_id", "description": "AAX plugin ID", "type": "text"},
        {"name": "plugin.aax_description", "description": "AAX plugin description", "type": "text"},
        {"name": "plugin.aax_category", "description": "AAX category", "type": "text"},
        {"name": "plugin.aax_company", "description": "AAX company name", "type": "text"},
        {"name": "plugin.aax_version", "description": "AAX version", "type": "text"},
        {"name": "plugin.aax_dsp_count", "description": "AAX DSP count", "type": "integer"},
        {"name": "plugin.aax_dsp_mixer", "description": "AAX DSP mixer mode", "type": "text"},
        {"name": "plugin.clap_id", "description": "CLAP plugin ID", "type": "text"},
        {"name": "plugin.clap_name", "description": "CLAP plugin name", "type": "text"},
        {"name": "plugin.clap_version", "description": "CLAP version", "type": "text"},
        {"name": "plugin.clap_vendor", "description": "CLAP vendor name", "type": "text"},
        {"name": "plugin.clap_url", "description": "CLAP vendor URL", "type": "text"},
        {"name": "plugin.clap_features", "description": "CLAP supported features", "type": "array"},
        {"name": "plugin.clap_audio_ports", "description": "CLAP audio port configuration", "type": "array"},
        {"name": "plugin.clap_midi_ports", "description": "CLAP MIDI port configuration", "type": "array"},
        {"name": "plugin.clap_parameters", "description": "CLAP parameter count", "type": "integer"},
        {"name": "plugin.clap_presets", "description": "CLAP preset count", "type": "integer"},
        {"name": "plugin.preset_name", "description": "Current preset name", "type": "text"},
        {"name": "plugin.preset_path", "description": "Preset file path", "type": "text"},
        {"name": "plugin.preset_bank", "description": "Preset bank name", "type": "text"},
        {"name": "plugin.preset_category", "description": "Preset category", "type": "text"},
        {"name": "plugin.bypass", "description": "Plugin bypassed", "type": "boolean"},
        {"name": "plugin.enabled", "description": "Plugin enabled", "type": "boolean"},
        {"name": "plugin.frozen", "description": "Plugin frozen/bounced", "type": "boolean"},
        {"name": "plugin.sidechain_input", "description": "Sidechain input present", "type": "boolean"},
        {"name": "plugin.latency_samples", "description": "Plugin latency in samples", "type": "integer"},
        {"name": "plugin.cpu_usage", "description": "Plugin CPU usage %", "type": "float"},
        {"name": "plugin.memory_usage", "description": "Plugin memory usage in MB", "type": "float"},
    ]


def get_stem_bus_routing_fields() -> List[Dict[str, Any]]:
    """Get Stem/Bus Routing metadata fields - 50 fields."""
    return [
        {"name": "bus.track_bus_name", "description": "Bus track name", "type": "text"},
        {"name": "bus.track_bus_id", "description": "Bus track unique ID", "type": "text"},
        {"name": "bus.bus_type", "description": "Bus type (aux/submaster/main)", "type": "text"},
        {"name": "bus.routing", "description": "Routing destination", "type": "text"},
        {"name": "bus.routing_matrix", "description": "Routing matrix configuration", "type": "array"},
        {"name": "bus.input_source", "description": "Input source type", "type": "text"},
        {"name": "bus.input_channel", "description": "Input channel number", "type": "integer"},
        {"name": "bus.output_destination", "description": "Output destination", "type": "text"},
        {"name": "bus.output_channel", "description": "Output channel number", "type": "integer"},
        {"name": "bus.fader_level", "description": "Fader level in dB", "type": "float"},
        {"name": "bus.pan_position", "description": "Pan position (-1 to 1)", "type": "float"},
        {"name": "bus.pan_law", "description": "Pan law (linear/equal power)", "type": "text"},
        {"name": "bus.stereo_width", "description": "Stereo width control", "type": "float"},
        {"name": "bus.mono_compatible", "description": "Mono compatibility mode", "type": "boolean"},
        {"name": "bus.phase_inverted", "description": "Phase inverted flag", "type": "boolean"},
        {"name": "bus.solo_safe", "description": "Solo safe mode enabled", "type": "boolean"},
        {"name": "bus.mute", "description": "Mute state", "type": "boolean"},
        {"name": "bus.solo", "description": "Solo state", "type": "boolean"},
        {"name": "bus.solo_mode", "description": "Solo mode (simple/latched)", "type": "text"},
        {"name": "bus.send_count", "description": "Number of sends", "type": "integer"},
        {"name": "bus.send_destination", "description": "Send destination bus", "type": "text"},
        {"name": "bus.send_level", "description": "Send level in dB", "type": "float"},
        {"name": "bus.send_pan", "description": "Send pan position", "type": "float"},
        {"name": "bus.send_pre_fader", "description": "Pre-fader send enabled", "type": "boolean"},
        {"name": "bus.send_mute", "description": "Send mute state", "type": "boolean"},
        {"name": "bus.return_count", "description": "Number of returns", "type": "integer"},
        {"name": "bus.return_level", "description": "Return level in dB", "type": "float"},
        {"name": "bus.return_pan", "description": "Return pan position", "type": "float"},
        {"name": "bus.return_source", "description": "Return source bus", "type": "text"},
        {"name": "bus.group_count", "description": "Number of groups", "type": "integer"},
        {"name": "bus.group_member_count", "description": "Group member count", "type": "integer"},
        {"name": "bus.group_linked", "description": "Group link status", "type": "boolean"},
        {"name": "bus.dca_count", "description": "DCA group count", "type": "integer"},
        {"name": "bus.dca_assignment", "description": "DCA assignment", "type": "array"},
        {"name": "bus.vca_count", "description": "VCA count", "type": "integer"},
        {"name": "bus.vca_assignment", "description": "VCA assignment", "type": "array"},
        {"name": "bus.folder_count", "description": "Folder track count", "type": "integer"},
        {"name": "bus.folder_compact", "description": "Folder compact mode", "type": "boolean"},
        {"name": "bus.stem_count", "description": "Number of stems", "type": "integer"},
        {"name": "bus.stem_name", "description": "Stem name", "type": "text"},
        {"name": "bus.stem_path", "description": "Stem file path", "type": "text"},
        {"name": "bus.submix_count", "description": "Submix count", "type": "integer"},
        {"name": "bus.submix_type", "description": "Submix type (drum/bass/vocal)", "type": "text"},
        {"name": "bus.main_output_count", "description": "Main output count", "type": "integer"},
        {"name": "bus.main_output_name", "description": "Main output name", "type": "text"},
        {"name": "bus.main_output_format", "description": "Main output format (stereo/surround)", "type": "text"},
        {"name": "bus.insert_count", "description": "Insert slot count", "type": "integer"},
        {"name": "bus.insert_slot_name", "description": "Insert slot name", "type": "text"},
        {"name": "bus.insert_slot_order", "description": "Insert slot processing order", "type": "integer"},
        {"name": "bus.processing_order", "description": "Processing chain order", "type": "array"},
    ]


def get_sample_library_fields() -> List[Dict[str, Any]]:
    """Get Sample Library metadata fields - 40 fields."""
    return [
        {"name": "sample.library_name", "description": "Sample library name", "type": "text"},
        {"name": "sample.library_version", "description": "Library version", "type": "text"},
        {"name": "sample.instrument_name", "description": "Instrument name", "type": "text"},
        {"name": "sample.instrument_type", "description": "Instrument type (strings/brass)", "type": "text"},
        {"name": "sample.articulation", "description": "Articulation name", "type": "text"},
        {"name": "sample.articulation_id", "description": "Articulation ID number", "type": "integer"},
        {"name": "sample.articulation_switch", "description": "Articulation switch type", "type": "text"},
        {"name": "sample.keyswitch", "description": "Keyswitch note number", "type": "integer"},
        {"name": "sample.keyswitch_name", "description": "Keyswitch name", "type": "text"},
        {"name": "sample.keyswitch_range_low", "description": "Keyswitch range low note", "type": "integer"},
        {"name": "sample.keyswitch_range_high", "description": "Keyswitch range high note", "type": "integer"},
        {"name": "sample.midi_channel", "description": "MIDI channel assignment", "type": "integer"},
        {"name": "sample.midi_program", "description": "MIDI program number", "type": "integer"},
        {"name": "sample.volume_velocity", "description": "Velocity to volume mapping", "type": "float"},
        {"name": "sample.round_robin", "description": "Round robin enabled", "type": "boolean"},
        {"name": "sample.round_robin_count", "description": "Round robin variations count", "type": "integer"},
        {"name": "sample.round_robin_cycle", "description": "Round robin cycle type", "type": "text"},
        {"name": "sample.rrna_enabled", "description": "Round robin note articulation enabled", "type": "boolean"},
        {"name": "sample.rrna_count", "description": "RRNA variation count", "type": "integer"},
        {"name": "sample.legato", "description": "Legato mode enabled", "type": "boolean"},
        {"name": "sample.legato_mode", "description": "Legato mode type (retrig/slide)", "type": "text"},
        {"name": "sample.glide", "description": "Glide/portamento enabled", "type": "boolean"},
        {"name": "sample.glide_time", "description": "Glide time in ms", "type": "float"},
        {"name": "sample.mic_position", "description": "Microphone position (close/mix)", "type": "text"},
        {"name": "sample.mic_count", "description": "Microphone count", "type": "integer"},
        {"name": "sample.mic_mix", "description": "Microphone mix percentage", "type": "float"},
        {"name": "sample.nk7_mode", "description": "Kontakt 7 mode enabled", "type": "boolean"},
        {"name": "sample.nk7_instrument", "description": "Kontakt instrument path", "type": "text"},
        {"name": "sample.nk7_script", "description": "Kontakt script name", "type": "text"},
        {"name": "sample.nk7_group", "description": "Kontakt group name", "type": "text"},
        {"name": "sample.sfz_path", "description": "SFZ file path", "type": "text"},
        {"name": "sample.sfz_region", "description": "SFZ region name", "type": "text"},
        {"name": "sample.sfz_sample", "description": "SFZ sample file", "type": "text"},
        {"name": "sample.spitfire_libraries", "description": "Spitfire library used", "type": "text"},
        {"name": "sample.eastwest_instruments", "description": "EastWest instrument name", "type": "text"},
        {"name": "sample.vel_round", "description": "Velocity rounding amount", "type": "integer"},
        {"name": "sample.vel_threshold", "description": "Velocity threshold", "type": "integer"},
        {"name": "sample.sample_rate", "description": "Sample rate in Hz", "type": "integer"},
        {"name": "sample.bit_depth", "description": "Bit depth", "type": "integer"},
        {"name": "sample.channel_count", "description": "Channel count (mono/stereo)", "type": "integer"},
    ]


def generate_inventory() -> Dict[str, Any]:
    """Generate the complete music production/DSP metadata field inventory."""
    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Music Production/DSP Specifications",
        "description": "Comprehensive inventory of music production and DSP metadata fields",
        "categories": {},
        "totals": {},
    }

    categories = {
        "daw_DAWProjects": {"fields": get_daw_project_fields(), "format": "DAW Projects", "count": 60},
        "effects_AudioEffects": {"fields": get_audio_effects_fields(), "format": "Audio Effects", "count": 50},
        "midi_MIDIData": {"fields": get_midi_data_fields(), "format": "MIDI Data", "count": 50},
        "mastering_Mastering": {"fields": get_mastering_fields(), "format": "Mastering", "count": 50},
        "plugin_PluginFormats": {"fields": get_plugin_format_fields(), "format": "Plugin Formats", "count": 50},
        "bus_StemBusRouting": {"fields": get_stem_bus_routing_fields(), "format": "Stem/Bus Routing", "count": 50},
        "sample_SampleLibraries": {"fields": get_sample_library_fields(), "format": "Sample Libraries", "count": 40},
    }

    total_fields = 0
    for cat_key, cat_data in categories.items():
        inventory["categories"][cat_key] = {
            "format": cat_data["format"],
            "description": f"{cat_data['format']} metadata fields",
            "fields": cat_data["fields"],
            "field_count": len(cat_data["fields"]),
        }
        total_fields += len(cat_data["fields"])

    inventory["totals"] = {
        "categories": len(categories),
        "total_fields": total_fields,
        "field_names": [],
    }

    all_field_names = []
    for cat_data in categories.values():
        for field in cat_data["fields"]:
            all_field_names.append(field["name"])
    inventory["totals"]["field_names"] = sorted(all_field_names)

    return inventory


def generate_summary(inventory: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a summary of the inventory."""
    summary = {
        "generated_at": inventory["generated_at"],
        "source": inventory["source"],
        "description": inventory["description"],
        "categories": len(inventory["categories"]),
        "total_fields": inventory["totals"]["total_fields"],
        "field_counts_by_category": {},
    }

    for cat_key, cat_data in inventory["categories"].items():
        summary["field_counts_by_category"][cat_key] = {
            "format": cat_data["format"],
            "description": cat_data["description"],
            "field_count": cat_data["field_count"],
        }

    return summary


def main():
    output_dir = Path("dist/music_production_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = generate_inventory()

    inventory_file = output_dir / "music_production_inventory.json"
    inventory_file.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")

    summary = generate_summary(inventory)
    summary_file = output_dir / "music_production_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 70)
    print("MUSIC PRODUCTION/DSP METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {inventory['generated_at']}")
    print(f"Total Fields: {inventory['totals']['total_fields']}")
    print(f"Categories: {inventory['totals']['categories']}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat_key, cat_data in sorted(inventory["categories"].items(), key=lambda x: x[1]["field_count"], reverse=True):
        print(f"  {cat_key:25s}: {cat_data['field_count']:>3}  [{cat_data['format']}]")
    print()
    print(f"Wrote: {inventory_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
