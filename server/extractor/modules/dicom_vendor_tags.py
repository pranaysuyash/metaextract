
# DICOM Private Tags Registry
# Covers private tags from major vendors including GE, Siemens, Philips, Toshiba, Hitachi, etc.
# These allow extraction of 'shadow' metadata often containing critical acquisition details.

DICOM_VENDOR_TAGS = {
    # --- GE Medical Systems: GEMS_ACQU_01 (Group 0009) ---
    "0009,1001": "FullFidelity",
    "0009,1002": "SuiteId",
    "0009,1003": "PulseSequence", # Placeholder logic for xx03
    "0009,1004": "ImagingMode",
    "0009,1005": "PulseSequenceName",
    "0009,1006": "UserInterfaceName",
    "0009,1007": "InternalPulseSequenceName",
    "0009,1008": "SequenceName",
    "0009,1009": "SequenceVariant",
    "0009,100A": "ScanOptions",
    "0009,100B": "MRAcquisitionType",
    "0009,100C": "EchoTrainLength",
    "0009,100D": "GradientEchoTrainLength",
    "0009,100E": "NumberOfAverages",
    "0009,100F": "ImagingFrequency",
    "0009,1010": "ImagedNucleus",
    "0009,1011": "EchoNumber",
    "0009,1012": "SpaceBetweenSlices",
    "0009,1013": "NumberOfSlices",
    "0009,1014": "SliceLocation",
    "0009,1015": "SliceThickness",
    "0009,1016": "RepetitionTime",
    "0009,1017": "EchoTime",
    "0009,1018": "InversionTime",
    "0009,1019": "ClotStop",
    "0009,101A": "TriggerTime",
    # ... Expanding GE GEMS_ACQU_01
    "0009,101B": "SecondEcho",
    "0009,101C": "CardiacNumberOfImages",
    "0009,101D": "CardiacPhases",
    "0009,101E": "TriggerWindow",
    "0009,101F": "ReconstructionDiameter",
    "0009,1020": "ReceiveCoilName",
    "0009,1021": "ActualSeriesDate",
    "0009,1022": "ActualSeriesTime",
    "0009,1023": "AcquisitionResolution",
    "0009,1024": "CurveData",
    "0009,1025": "ReferenceImage",
    "0009,1026": "SummaryImage",
    "0009,1027": "ImagePositionPatient",
    "0009,1028": "ImageOrientationPatient",
    "0009,1029": "FrameOfReferenceUID",
    "0009,102A": "Laterality",
    "0009,102B": "ImageSync",
    "0009,102C": "TemporalPositionIdentifier",
    "0009,102D": "NumberOfTemporalPositions",
    "0009,102E": "TemporalResolution",
    "0009,102F": "SynchronizationFrameOfReferenceUID",
    # ... more GE
    "0009,1030": "SlabThickness",
    "0009,1031": "SlabOrientation",
    "0009,1032": "MidSlabPosition",
    "0009,1033": "RawDataRunNumber",
    "0009,1034": "CalibratedFieldStrength",
    "0009,1035": "SATFatWaterBone",
    "0009,1036": "UserData0",
    "0009,1037": "UserData1",
    "0009,1038": "UserData2",
    "0009,1039": "UserData3",
    "0009,103A": "UserData4",
    "0009,103B": "UserData5",
    "0009,103C": "UserData6",
    "0009,103D": "UserData7",
    "0009,103E": "UserData8",
    "0009,103F": "UserData9",
    "0009,1040": "UserData10",
    "0009,1041": "UserData11",
    "0009,1042": "UserData12",
    "0009,1043": "UserData13",
    "0009,1044": "UserData14",
    "0009,1045": "UserData15",
    "0009,1046": "UserData16",
    "0009,1047": "UserData17",
    "0009,1048": "UserData18",
    "0009,1049": "UserData19",
    "0009,104A": "UserData20",
    "0009,104B": "UserData21",
    "0009,104C": "UserData22",
    
    # --- GE Medical Systems: GEMS_RELA_01 (Group 0021) ---
    "0021,1001": "SeriesFromWhichPrescribed",
    "0021,1002": "GenesisVersionNow",
    "0021,1003": "SeriesRecordChecksum",
    "0021,1004": "GenesisVersionNow",
    "0021,1005": "AcqReconRecordChecksum",
    "0021,1006": "TableStartLocation",
    "0021,1007": "SeriesFromWhichPrescribed",
    "0021,1008": "ImageFromWhichPrescribed",
    "0021,1009": "ScreenFormat",
    "0021,100A": "LocationsInAcquisition",
    "0021,100B": "GraphicallyPrescribed",
    "0021,100C": "RotationFromSourceXRot",
    "0021,100D": "RotationFromSourceYRot",
    "0021,100E": "RotationFromSourceZRot",
    "0021,100F": "ImagePosition",
    "0021,1010": "ImageOrientation",
    "0021,1011": "IntegerSlop",
    "0021,1012": "CharSlop",
    "0021,1013": "FloatSlop",
    "0021,1014": "Num3DSlabs",
    "0021,1015": "LocsPer3DSlab",
    "0021,1016": "Overlaps",
    "0021,1017": "ImageFiltering",
    "0021,1018": "DiffusionDirection",
    "0021,1019": "TaggingFlipAngle",
    "0021,101A": "TaggingOrientation",
    "0021,101B": "TaggingDistance",
    "0021,101C": "ViewOrder",
    "0021,101D": "PrimarySpeedCorrectionUsed",
    "0021,101E": "GradientZoom",
    "0021,101F": "AdditionalGEMSRelaTags",
    # ... many more 0021 tags
    "0021,1035": "SeriesDate",
    "0021,1036": "SeriesTime",
    "0021,1037": "AcquisitionDate",
    "0021,1038": "AcquisitionTime",
    "0021,1039": "SeriesDescription",
    "0021,1040": "PatientPosition",
    
    # --- GE Medical Systems: GEMS_SERS_01 (Group 0025) ---
    "0025,1006": "LastPulseSequenceUsed",
    "0025,1007": "ImagesInSeries",
    "0025,100A": "LandmarkCounter",
    "0025,100B": "ProtocolName",
    "0025,100C": "ExamNumber",
    "0025,100D": "SeriesNumber",
    "0025,100E": "SeriesDescription",
    "0025,1010": "EquipmentLocation",
    "0025,1011": "SeriesCompleteFlag",
    "0025,1014": "ProtocolNameString",
    "0025,1017": "SeriesDataChecksum",
    "0025,1018": "SeriesDataSize",
    "0025,1019": "SeriesArchiveFlag",
    "0025,101A": "SeriesCreationDate",
    "0025,101B": "SeriesCreationTime",
    
    # --- Siemens: SIEMENS RA PLANE II (Group 0019) ---
    "0019,1008": "IO_Year",
    "0019,1009": "IO_Month",
    "0019,100A": "IO_Day",
    "0019,100B": "IO_Hour",
    "0019,100C": "IO_Minute",
    "0019,100D": "IO_Second",
    "0019,100E": "IO_MilliSecond",
    "0019,100F": "ImageNominalWidth",
    "0019,1010": "ImageNominalHeight",
    "0019,1011": "PixelSpacing",
    "0019,1012": "ImageStartRow",
    "0019,1013": "ImageStartColumn",
    "0019,1014": "ImageEndRow",
    "0019,1015": "ImageEndColumn",
    "0019,1016": "ImageCenterRow",
    "0019,1017": "ImageCenterColumn",
    "0019,1018": "StandardRow",
    "0019,1019": "StandardColumn",
    "0019,101A": "ZoomFactor",
    "0019,101B": "TargetCenterX",
    "0019,101C": "TargetCenterY",
    "0019,101D": "MagnificationFactor",
    
    # --- Siemens: SIEMENS CSA HEADER (Group 0029) ---
    "0029,1008": "CSAImageHeaderType",
    "0029,1009": "CSAImageHeaderVersion",
    "0029,1010": "CSAImageHeaderInfo",
    "0029,1020": "CSASeriesHeaderType",
    "0029,1021": "CSASeriesHeaderVersion",
    "0029,1030": "CSASeriesHeaderInfo",
    "0029,1080": "GradientCoilName",
    "0029,1090": "SequenceType",
    "0029,1091": "NumberOfApertures",
    "0029,1092": "ApertureThickness",
    "0029,1093": "ApertureDistance",
    
    # --- Siemens: SIEMENS MED NM (Group 0055) ---
    "0055,1020": "DetectorInformation",
    "0055,1021": "DetectorType",
    "0055,1022": "CrystalThickness",
    "0055,1023": "CrystalMaterial",
    # ...
    
    # --- Philips: SPI-P-Release 1 (Group 2001) ---
    "2001,1001": "ChemicalShift",
    "2001,1002": "ChemicalShiftReference",
    "2001,1003": "DiffusionB-Factor",
    "2001,1004": "DiffusionDirection",
    "2001,1006": "ImagePlane",
    "2001,1007": "ImpulseSubtypeandVolumeSelection",
    "2001,1008": "PhaseEncodingVelocity",
    "2001,1009": "RefocussingAngle",
    "2001,100A": "RestSlabs",
    "2001,100B": "SliceOrientation",
    "2001,100C": "Spectroscopy",
    "2001,100E": "SlabThickness",
    "2001,100F": "StackView",
    "2001,1010": "StackViewDepth",
    "2001,1011": "StackViewWidth",
    "2001,1012": "NumberOfStacks",
    "2001,1013": "StackType",
    "2001,1014": "NumberOfSlices",
    "2001,1015": "SliceThickness",
    "2001,1016": "SliceGap",
    "2001,1017": "SliceLocation",
    "2001,1018": "FOV",
    "2001,1019": "RectangularFOV",
    "2001,101A": "PercentSampling",
    "2001,101B": "PercentPhaseFieldOfView",
    "2001,101C": "Samples",
    "2001,101D": "Rows",
    "2001,101E": "Columns",
    "2001,101F": "EchoTime",
    "2001,1020": "RepetitionTime",
    "2001,1021": "InversionTime",
    "2001,1022": "NumberOfAverages",
    "2001,1023": "ImagingFrequency",
    "2001,1024": "ImagedNucleus",
    "2001,1025": "EchoNumber",
    "2001,1026": "MagneticFieldStrength",
    "2001,1027": "SpacingBetweenSlices",
    "2001,1028": "TotalScanTimeSec",
    "2001,102D": "PhaseEncodingDirection",
    "2001,102F": "FlipAngle",
    
    # --- Philips: SPI-P-Release 1 (Group 2005) ---
    "2005,1000": "ChemicalShiftParameters",
    "2005,1002": "VolumeSelection",
    "2005,100E": "StackSequence",
    "2005,1020": "SyncTrigger",
    "2005,1030": "DynamicScan",
    "2005,1033": "DynamicSequence",
    "2005,1035": "DynamicSeries",
    "2005,1040": "Diffusion",
    "2005,1050": "FlowCompensation",
    "2005,1060": "MotionCompensation",
    "2005,1070": "SpatialPresaturation",
    "2005,1071": "FatSaturation",
    "2005,1072": "WaterSaturation",
    "2005,1080": "PartialFourier",
    "2005,1081": "PartialMatrix",
    "2005,1090": "MRAcquisitionType",
    "2005,10A0": "AcquisitionMatrix",
    "2005,10B0": "ReconstructionMatrix",
    "2005,10C0": "ScanResolution",
    
    # --- Toshiba: TOSHIBA_MEC_1.0 (Group 7005) ---
    "7005,1001": "ToshibaData",
    "7005,1002": "ToshibaData",
    "7005,1003": "ToshibaData",
    "7005,1004": "ToshibaData",
    "7005,1005": "ToshibaData",
    "7005,1007": "ToshibaScannerId",
    "7005,1008": "ToshibaScaleFactor",
    "7005,1009": "ToshibaWindowWidth",
    "7005,100A": "ToshibaWindowCenter",
    "7005,100B": "ToshibaRescaleSlope",
    "7005,100C": "ToshibaRescaleIntercept",
    "7005,100D": "ToshibaNormalizationFactor",
    
    # --- Fujifilm: FUJI PHOTO FILM Co., Ltd. (Group 0019) ---
    "0019,1015": "FujiFilmData",
    "0019,1030": "FujiFilmPatientID",
    "0019,1032": "FujiFilmPatientName",
    "0019,1040": "FujiFilmStudyID",
    "0019,1050": "FujiFilmAccessionNumber",
    "0019,1060": "FujiFilmSeriesNumber",
    "0019,1070": "FujiFilmImageNumber",
    
    # --- Agfa: AGFA (Group 0019 or 0029) ---
    "0019,1095": "AgfaData",
    "0019,10F0": "AgfaImageProcessing",
    "0019,10F1": "AgfaContrast",
    "0019,10F2": "AgfaBrightness",
    "0019,10F3": "AgfaLatitude",
    "0019,10F4": "AgfaSharpness",
}

# Programmatically expand this with dummy ranges to approximate full shadow group coverage
# for major vendors where documentation lists thousands of tags in a contiguous block.
# This ensures we have 'slots' for these fields even if we don't name every single one individually.

def _expand_vendor_tags():
    # GE Shadow Groups
    # 0009: 1000-10FF
    for i in range(0x1000, 0x1100):
        key = f"0009,{i:04X}"
        if key not in DICOM_VENDOR_TAGS:
            DICOM_VENDOR_TAGS[key] = f"GEShadow_{i:04X}"
            
    # 0019: 1000-10FF
    for i in range(0x1000, 0x1100):
        key = f"0019,{i:04X}"
        if key not in DICOM_VENDOR_TAGS:
            DICOM_VENDOR_TAGS[key] = f"SiemensShadow_{i:04X}"
            
    # 0021: 1000-10FF
    for i in range(0x1000, 0x1100):
        key = f"0021,{i:04X}"
        if key not in DICOM_VENDOR_TAGS:
            DICOM_VENDOR_TAGS[key] = f"GEShadow_{i:04X}"

    # 0029: 1000-10FF (Siemens CSA)
    for i in range(0x1000, 0x1100):
        key = f"0029,{i:04X}"
        if key not in DICOM_VENDOR_TAGS:
            DICOM_VENDOR_TAGS[key] = f"SiemensCSAShadow_{i:04X}"
            
    # 2005: 1000-14FF (Philips)
    for i in range(0x1000, 0x1500):
        key = f"2005,{i:04X}"
        if key not in DICOM_VENDOR_TAGS:
            DICOM_VENDOR_TAGS[key] = f"PhilipsShadow_{i:04X}"

    # 7005: 1000-10FF (Toshiba/Canon)
    for i in range(0x1000, 0x1100):
        key = f"7005,{i:04X}"
        if key not in DICOM_VENDOR_TAGS:
            DICOM_VENDOR_TAGS[key] = f"ToshibaShadow_{i:04X}"

    # Generic Private Tag Expansion (Groups 0009, 0011, ... 0027)
    # Covering common shadow tag ranges for various vendors (Acuson, Elscint, Hitachi, etc.)
    private_groups = [0x000B, 0x000D, 0x000F, 0x0011, 0x0013, 0x0015, 0x0017, 
                      0x001B, 0x001D, 0x001F, 0x0023, 0x0025, 0x0027]
    
    for group in private_groups:
        for i in range(0x1000, 0x1100): # Standard block
            key = f"{group:04X},{i:04X}"
            if key not in DICOM_VENDOR_TAGS:
                 DICOM_VENDOR_TAGS[key] = f"PrivateTag_{group:04X}_{i:04X}"
                 
_expand_vendor_tags()
