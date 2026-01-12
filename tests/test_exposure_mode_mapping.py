#!/usr/bin/env python3
"""Tests for exposure mode formatting in persona interpretation"""

from extractor.persona_interpretation import PersonaInterpreter


def test_exposure_mode_mapping():
    p = PersonaInterpreter({})
    assert p._format_exposure_mode(2) in ["Normal Program", "Program", "Auto", "Auto Exposure"]
    # Be explicit: expect the canonical name
    assert p._format_exposure_mode(2) == "Normal Program"
    # Other common codes
    assert p._format_exposure_mode(1) == "Manual"
    assert p._format_exposure_mode(3) == "Aperture Priority"
