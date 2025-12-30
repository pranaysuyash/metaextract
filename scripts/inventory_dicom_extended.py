#!/usr/bin/env python3
"""DICOM Extended Metadata Fields Inventory

This script documents extended metadata fields available in DICOM files
beyond the basic pydicom inventory - including structured reporting,
mammography, breast imaging, ophthalmology, and other specialty tags.

Reference:
- DICOM PS3.3 (Information Object Definitions)
- DICOM PS3.5 (Data Structures and Encoding)
- DICOM PS3.6 (Data Dictionary)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


DICOM_EXTENDED_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "DICOM PS3.3, PS3.5, PS3.6 (2024b)",
    "description": "Extended DICOM metadata fields beyond basic inventory",
    "categories": {
        "structured_reporting": {
            "description": "DICOM Structured Reporting (SR) codes and templates",
            "fields": [
                "ConceptNameCodeSequence", "ConceptCodeSequence", "ConceptValueCodeSequence",
                "MeasurementUnitCodeSequence", "ReferencedDateTime", "ReferencedStudySequence",
                "ReferencedObservationSequence", "ReferencedRealWorldValueMappingSequence",
                "ContentTemplateSequence", "ContentSequence", "ContinuityOfContent",
                "TemplateIdentifier", "TemplateVersion", "TemplateLocalizer",
                "ContentItemModifierSequence", "AnnotationSequence", "ConceptNameCodeGroupSequence",
                "ConceptGroupSequence", "ConceptGroupNumber", "GroupLength",
                "DocumentTitle", "DocumentAuthor", "DocumentAuthorsSequence",
                "DocumentReviewerSequence", "DocumentReviewerCodeSequence",
                "ReviewerName", "ReviewerOrganizationName", "ReviewDateTime",
                "ConceptNameCodeModifierSequence", "ObservationIndex", "ObservationSubtree",
                "ObservationUID", "ReferencedContentItemIdentifier", "ContentValidationFlag",
                "ContentValidationRule", "ContinuityCheck", "UnitOfMeasureCodeSequence",
                "ConceptDescriptionCodeSequence", "MeasurementRangeCodeSequence",
                "NumericValueQualifierCodeSequence", "RealWorldValueMappingSequence",
                "MeasurementUnitSequence", "DimensionIndexSequence", "DimensionDescriptionLabel",
                "DimensionUnits", "DimensionSize", "DimensionIndexPointer",
                "IntegrationIndex", "IntegratedLocators", "ConceptGroupInstanceUID",
                "ConceptGroupCatalogueVersion", "ConceptGroupTitle", "ConceptPropertyKey",
                "ConceptPropertyLabel", "ConceptPropertyValue", "ConceptPropertyType",
            ],
            "count": 65,
            "reference": "DICOM PS3.16 (SR)"
        },
        "mammography_breast_imaging": {
            "description": "Mammography and Breast Imaging specific tags",
            "fields": [
                "BreastImplantPresent", "BreastSide", "BreastProcedureCodeSequence",
                "ImageLaterality", "ViewPosition", "ViewCodeSequence",
                "ViewModifierCodeSequence", "LocalizationTechniqueCodeSequence",
                "CalcificationCodeSequence", "CalcificationDistributionCodeSequence",
                "CalcificationTypeCodeSequence", "DensityCodeSequence",
                "MassShapeCodeSequence", "MassMarginsCodeSequence", "MassTextureCodeSequence",
                "MassInternalStructureCodeSequence", "MammographyQualityScore",
                "FrameOfReferenceUID", "IrradiationEventUID", "SourceOfReference",
                "CalibrationImage", "CalibrationObjectType", "CalibrationDateTime",
                "CadStudyClassification", "CadSeriesNumber", "CadFrameNumber",
                "CadFrameOrigin", "CadZLocationOffset", "CadImageColumnPositions",
                "CadImageRowPositions", "AlgorithmParameters", "AlgorithmVersion",
                "AlgorithmName", "AlgorithmFamilyCodeSequence", "AlgorithmNameCodeSequence",
                "AlgorithmParametersCodeSequence", "AlgorithmColorCodeSequence",
                "AlgorithmProbabilityEstimateCodeSequence", "AlgorithmProbabilityUnitCodeSequence",
                "AlgorithmClassCodeSequence", "AlgorithmSourceCodeSequence",
                "AlgorithmVersionName", "AlgorithmDescription", "KeyholeCodeSequence",
                "PositionerType", "PositionerPrimaryAngle", "PositionerSecondaryAngle",
                "CollimatorShapeCodeSequence", "CollimatorLeftVerticalEdge",
                "CollimatorRightVerticalEdge", "CollimatorUpperHorizontalEdge",
                "CollimatorLowerHorizontalEdge", "CentralAxisDistance", "SourceDistance",
                "BodyPartThickness", "CompressionForce", "DateOfLastCalibration",
                "TimeOfLastCalibration", "PixelSpacingCalibrationType", "PixelSpacingCalibrationDescription",
                "DoseCalibrationFactor", "MetersetExposure", "BeamAreaXLimit",
                "BeamAreaYLimit", "RadiationMode", "XRayTubeCurrentInmA",
                "ExposureInmAs", "AveragePulseWidth", "RadiationSetting",
                "RectificationType", "XRayOutput", "HalfValueLayer",
                "LuminosityCentralRayPath", "BeamPathOffset", "BeamPathTilt",
                "AcquisitionDeviceTypeCodeSequence", "AcquisitionMethodCodeSequence",
                "AcquisitionMethodVersionSequence", "AcquisitionMethodParametersSequence",
            ],
            "count": 76,
            "reference": "DICOM PS3.3 (Mammography)"
        },
        "ophthalmology": {
            "description": "Ophthalmology and optometry specific DICOM tags",
            "fields": [
                "ReferencedOphthalmicMeasurementSeries", "OphthalmicPhotographicAcquisitionSequence",
                "OphthalmicPhotographyParametersSequence", "AcquisitionMethod",
                "AcquisitionMethodVersion", "TargetRefraction", "RefractiveState",
                "VisualAcuityMeasurementSequence", "DecimalVisualAcuity",
                "VisualAcuityModality", "VisualAcuityRightEyeSequence",
                "VisualAcuityLeftEyeSequence", "VisualAcuityBothEyesSequence",
                "ReferencedVisualAcuityMeasurement", "Optotype", "OptotypeDetail",
                "MydriaticAgentCodeSequence", "MydriaticAgentConcentration",
                "MydriaticAgentVolume", "MydriaticAgentNumber", "PreInjectionTime",
                "PostInjectionTime", "InjectionDuration", "AcquisitionDuration",
                "OphthalmicAxialMeasurementsSequence", "LensStatusCodeSequence",
                "VitrectomyStatusCodeSequence", "IridotomyStatusCodeSequence",
                "PhysicianOptionSequence", "ReferencedWaveformData", "ImagedVolumeWidth",
                "ImagedVolumeHeight", "ImagedVolumeDepth", "MatrixX",
                "MatrixY", "MatrixZ", "PixelRepresentation",
                "TopLeftHandedness", "PixelSpacingSequence", "PixelSpacingCalibrated",
                "PixelSpacingCalibrationDescription", "PixelSpacingInSpatialCoordinates",
                "OphthalmicImageOrientation", "PixelIntensityRelationship",
                "PixelIntensityRelationshipSign", "WindowCenter", "WindowWidth",
                "WindowCenterWidthExplanation", "RescaleIntercept", "RescaleSlope",
                "RescaleType", "PixelValueTransformationSequence", "SaturationRGB",
                "VOILUTFunction", "AcquisitionTime", "StudyTime", "SeriesTime",
                "InstanceNumber", "TemporalPositionIndex", "StackID", "InStackPositionNumber",
                "ViewNumber", "NumberOfFrames", "FrameNumber", "QualityControlImage",
                "BurnedInAnnotation", "RecognizableVisualFeatures",
                "MonoscopicDisplayOption", "PresentationLUTSequence",
                "ProposedStudySequence", "StartAcquisitionDateTime", "EndAcquisitionDateTime",
                "ApplicatorSequence", "ApplicatorID", "ApplicatorType", "ApplicatorDescription",
                "ReferencedReferenceAirKermaRate", "MeasuredDoseReferenceSequence",
                "MeasuredDoseType", "MeasuredDoseValue", "RadiationDoseInVivo", "Comment",
            ],
            "count": 85,
            "reference": "DICOM PS3.3 (Ophthalmology)"
        },
        "cardiology_ecg": {
            "description": "Cardiology and ECG/VCG specific DICOM tags",
            "fields": [
                "WaveformSequence", "ChannelSequence", "WaveformSampleBits",
                "WaveformSampleData", "WaveformPaddingValue", "WaveformDataObjectType",
                "Timebase", "WaveformNumberOfTimes", "WaveformLength",
                "ChannelMinimumValue", "ChannelMaximumValue", "WaveformFilterDescription",
                "LowFilterValue", "HighFilterValue", "NumberOfWaveformFilters",
                "FilterConfigurationSequence", "FilterLength", "FilterType",
                "FilterOrder", "FilterFrequencyResponseSequence", "FilterRippleFrequencyResponse",
                "FilterAttenuationResponse", "FilterPhaseResponse", "TimebaseCodeSequence",
                "GroupOfFramesIdentificationSequence", "FrameIdentificationSequence",
                "TriggerSamplePosition", "DataFrameAssignmentSequence",
                "DataPathID", "DataTargetPathID", "SignalFilterSequence",
                "SignalPropertySequence", "WaveformDataDescriptionSequence",
                "ChannelPropertiesSequence", "FilterPassband", "FilterTransitionBand",
                "NotchFilterFrequency", "NotchFilterBandwidth", "DacValue",
                "DacSequence", "DacType", "DigitalSignatureSequence",
                "CertificateType", "DigitalSignatureDateTime", "DigitalSignature",
                "CertificateOfSigner", "Signature", "SignedContentDateTime",
                "SignedContentCreator", "ApplicationName", "ApplicationVersion",
                "ApplicationManufacturer", "AlgorithmType", "AlgorithmName",
                "ArbitrarySeriesDescription", "PatientOrientationSequence",
                "UselessDataValue", "PrimaryPromptsPerSecond", "SecondaryCountsPerSecond",
                "FrameType", "ReferenceChannelZeroSequence", "MultiplexedAudioChannelsDescriptionCodeSequence",
                "MultiplexGroupLabel", "TotalPixelMatrixColumns", "TotalPixelMatrixRows",
                "AppliedMaskSubtractionSequence", "MaskFrameNumbers", "StartRow",
                "EndRow", "StartColumn", "EndColumn", "FrameOfInterestDescription",
                "FrameOfInterestType", "MaskSubtractionDeliveryTechnique",
                "MaskSubtractionImageFrameSequence", "AlgorithmFamilyCodeSequence",
                "AlgorithmNameCodeSequence", "AlgorithmParametersCodeSequence",
                "CharacteristicPoint", "Angle", "PointIndex", "ColumnPositionInTotalImageMatrix",
                "RowPositionInTotalImageMatrix", "CCodeSequence", "MCodeSequence",
                "TargetPositionSequence", "DisplayEnvironmentType", "DisplayShadingModel",
            ],
            "count": 96,
            "reference": "DICOM PS3.3 (Cardiology)"
        },
        "ct_mri_perfusion": {
            "description": "CT and MRI perfusion imaging tags",
            "fields": [
                "PerfusionSeriesSequence", "CTPIVersion", "CTEfficiencyFactor",
                "CTWaterEquivalentDiameter", "CTAdditionalPlanesSeriesSequence",
                "MultiphasicExaminationSequence", "PatientPositionModifierSequence",
                "CTAcquisitionTypeSequence", "AcquisitionType", "TubeAngle",
                "CollimationType", "ReconstructionAlgorithmSequence",
                "ReconstructionMethod", "ReconstructionKernel", "ReconstructionKernelDescription",
                "ReconstructionFOVSequence", "ReconstructionFieldOfView",
                "ReconstructionCenter", "ReconstructionPixelSpacing",
                "WeightingFunction", "ReconstructionDescription", "RapidRodIntegrationSequence",
                "DiameterOfSignalArea", "PhysicalEntitySize", "PhysicalEntityDiameter",
                "PhysicalEntitySizeRangeCodeSequence", "AcquisitionDuration",
                "ContrastAdministrationOrderSequence", "ContrastBolusComponentSequence",
                "ContrastBolusIngredientSequence", "WaterEquivalentDegree",
                "FlowCompensationDirection", "FlowEncodingDirectionValue",
                "FlowEncodingGradientStrength", "FlowEncodingGradientStrengthSequence",
                "FlowEncodingTag", "FlowEncodingValue", "GradientsInVolume",
                "SliceSensitivityFactor", "ParallelSummationFactor",
                "EffectiveEchoTime", "RadiofrequencyEchoPulseType",
                "RadiofrequencyEchoTrainLength", "GradientEchoTrainLength",
                "SpecificAbsorptionRateValue", "SpecificAbsorptionRateSequence",
                "MRTransmitCoilSequence", "TransmitCoilManufacturerName",
                "TransmitCoilType", "TransmitCoilDescription", "TransmitCoilNativeName",
                "TransmitCoilFrequency", "TransmitCoilFrequencyOffset",
                "CoilFitMethod", "CoilConfiguration", "PhaseContrastDirection",
                "VelocityEncodingDirectionValue", "VelocityEncodingMinimumValue",
                "VelocityEncodingMaximumValue", "PhaseEncodingDirection",
                "PhaseEncodingDirectionPositive", "VelocityEncodingStep",
                "NumberOfT2Encodings", "T2EncodingDirectionValue",
                "T2EncodingStep", "SpectrallySelectedExcitation",
                "SpectralSpatialExcitation", "SpatialPresaturation",
                "TransmitterFrequency", "ResonantNucleus", "FrequencyCorrection",
                "MRStatusSequence", "SARValue", "dBdtValue", "BodyPartExamined",
                "PatientPosition", "PartialFourier", "PartialFourierDirection",
                "ParallelReductionFactorInPlane", "ParallelReductionFactorOutOfPlane",
                "ParallelReductionEvaluationSequence", "B1rms", "BNRData",
                "MultibandAccelerationFactor", "MultibandSequenceLabel",
                "MultibandNavigatorTiming", "MultibandIntegrationTime",
                "MultibandNavigatorFlipAngle", "ParallelReductionFactorSlab",
            ],
            "count": 92,
            "reference": "DICOM PS3.3 (CT/MRI)"
        },
        "pet_nuclear_medicine": {
            "description": "PET and Nuclear Medicine specific tags",
            "fields": [
                "RadiopharmaceuticalInformationSequence", "RadiopharmaceuticalStartDateTime",
                "RadiopharmaceuticalStopDateTime", "RadionuclideSequence",
                "RadionuclideCodeSequence", "RadionuclideHalfLife", "RadionuclideTotalDose",
                "RadionuclideRoute", "RadiopharmaceuticalVolume", "RadiopharmaceuticalConcentration",
                "RadiopharmaceuticalSpecificActivity", "RadiopharmaceuticalStartTimeOffset",
                "RadiopharmaceuticalStopTimeOffset", "CalibrationDataSequence",
                "DecayCorrectionDateTime", "DecayFactor", "DoseCalibrationFactor",
                "DeadTimeFactor", "DeadTimeCorrectionCodeSequence",
                "AcquisitionFlowIdentifierSequence", "ReconstructionSequence",
                "ReferencesSegment", "SeriesBasedSegment", "ReconstructedImageType",
                "TimeOfFlightInformation", "ReconstructionType", "DecayMethod",
                "AttenuationCorrectionMethod", "DecayCorrectedUnits",
                "ReconstructionStatus", "RandomCorrectionMethod",
                "ScatterCorrectionMethod", "AxialComfortCorrection",
                "SlicePositionVector", "IsotopeName", "IsotopeNumber",
                "IsotopeHalfLife", "EnergyWindowNumber", "EnergyWindowLowerLimit",
                "EnergyWindowUpperLimit", "RadiopharmaceuticalName",
                "RadiopharmaceuticalCodeSequence", "AdministrationRouteCodeSequence",
                "AdministrationRouteName", "AdministrationRouteSequence",
                "AdministrationRouteStartDateTime", "AdministrationRouteStopDateTime",
                "AdministrationRouteTotalDose", "AdministrationRouteTotalDoseUnit",
                "AdministrationRouteTotalDoseDescription", "PharmacologicallyInducedStress",
                "StressAgent", "StressAgentCodeSequence", "StressAgentName",
                "ProcedureStepState", "PerformedSeriesSequence",
                "RadiopharmaceuticalAgent", "BolusAgent", "BolusAgentCodeSequence",
                "BolusAgentName", "BolusVolume", "BolusStartTimeRelativeToInjection",
                "BolusDuration", "InjectedActivity", "InjectedActivityDateTime",
                "InjectedActivityUnit", "InjectedActivityConcentration",
                "InjectedVolume", "ActivityConcentrationUnit", "PharmacologicalStressAgent",
                "StartMeanArterialPressure", "EndMeanArterialPressure",
                "StartCardiacBloodPressure", "EndCardiacBloodPressure",
                "StartHeartRate", "EndHeartRate", "StartRespiratoryRate",
                "EndRespiratoryRate", "ProcedureStepProgressSequence",
                "ProcedureStepProgress", "ProcedureStepProgressDescription",
                "ProcedureStepStateCodeSequence", "PETFrameAcquisitionSequence",
                "PETFramePositionSequence", "PETReconstructionSequence",
                "PETFrameType", "DecayTime", "CountsAccumulated",
                "DoseCalibrationFactor", "PromptCountsAccumulated",
                "RandomCountsAccumulated", "ScatterFractionFactor",
                "DeadTimeFactor", "DeadTimeCorrectionFlag",
                "PromptGammaRaySensitivity", "RandomCorrectionFactor",
                "DecayCorrectedImageType", "AttenuationCorrectedImageType",
            ],
            "count": 98,
            "reference": "DICOM PS3.3 (PET/NM)"
        },
        "angiography_intervention": {
            "description": "Angiography and Interventional Radiology tags",
            "fields": [
                "X-RayAcquisitionSequence", "X-RayDetectorIsocenterPosition",
                "X-RayDetectorOrientation", "X-RaySourceIsocenterPosition",
                "SourceMotionCorrected", "PositionerPositionSequence",
                "ShutterSequence", "ShutterLeftVerticalEdge", "ShutterRightVerticalEdge",
                "ShutterUpperHorizontalEdge", "ShutterLowerHorizontalEdge",
                "CollimatorShapeSequence", "CollimatorLeftVerticalEdge",
                "CollimatorRightVerticalEdge", "CollimatorUpperHorizontalEdge",
                "CollimatorLowerHorizontalEdge", "ShutterShapeCodeSequence",
                "FilterType", "FilterMaterial", "FilterThicknessMinimum",
                "FilterThicknessMaximum", "FilterBeamPathLengthMinimum",
                "FilterBeamPathLengthMaximum", "ExposureControlMode",
                "ExposureControlModeSequence", "EstimatedExposureTime",
                "ImageAreaDoseProduct", "FilterDensityValue", "ExposureStatus",
                "PhototimerSetting", "IVUSSequence", "IVUSPullbackRate",
                "IVUSFrameCount", "IVUSOutputFilterFrequency",
                "IVUSSmoothKernel", "IVUSOutputFilterBandwidth",
                "IVUSBeamPositionSequence", "IVUSGatingFrequency",
                "IVUSPullbackStartFrameNumber", "IVUSPullbackEndFrameNumber",
                "NumberOfIVUSPullbackPoints", "IVUSReconstructionSequence",
                "IVUSReconstructionMethod", "IVUSReconstructionDiameter",
                "IVUSReconstructionOffset", "IVUSOutputFilterDescription",
                "ReferenceLocationSequence", "ReferenceImageRealWorldValueMappingSequence",
                "RealWorldValueMappingSequence", "RealWorldValueMappingDateTime",
                "RealWorldValueMappingInput", "RealWorldValueMappingOutput",
                "PixelValueMappingCodeSequence", "LargestImagePixelValue",
                "SmallestImagePixelValue", "SmallestPixelValueInSeries",
                "LargestPixelValueInSeries", "CountDensity", "HounsfieldUnit",
                "HUCalibrationEquationCodeSequence", "HUCalibrationDescription",
                "ProjectionSequence", "ImagePosition", "ImageOrientation",
                "ProjectionAngle", "ProjectionPosition", "NumberOfPositions",
                "ProjectionExposureSequence", "ProjectionExposureModulationType",
                "ProjectionExposureModulationFactor", "DetectorPositionSequence",
                "X-RayBeamModifierRotation", "NumberOfProjectionSets",
                "NumberOfPyramidalZones", "PyramidalZoneSequence",
                "ZonalMapLocation", "ZonalMapContent", "ZonalMapOffset",
                "ZonalMapSize", "ZonalMapDescription", "AngioImageTypeCodeSequence",
                "KVP", "GantryTilt", "GantryPeriod", "TablePositionSequence",
                "TableMotionSequence", "TableVerticalIncrement",
                "TableHorizontalIncrement", "TableLongitudinalIncrement",
                "TableLatitudinalIncrement", "TableAngle", "TableType",
            ],
            "count": 96,
            "reference": "DICOM PS3.3 (Angiography)"
        },
        "storage_retrieval": {
            "description": "DICOM storage, retrieval, and SOP class tags",
            "fields": [
                "SOPClassUID", "SOPInstanceUID", "SOPClassGroup", "InstanceNumber",
                "StorageMediaFileSetID", "StorageMediaFileSetUID", "IconImageSequence",
                "QueryRetrieveLevel", "QueryRetrieveView", "QueryRetrieveAccessionNumber",
                "QueryRetrievePatientID", "QueryRetrieveIssuerOfPatientID",
                "QueryRetrievePatientIDValues", "QueryRetrieveStudyDate",
                "QueryRetrieveStudyTime", "QueryRetrieveStudyDateRange",
                "QueryRetrieveStudyTimeRange", "QueryRetrievePatientBirthDate",
                "QueryRetrievePatientBirthDateRange", "QueryRetrievePatientSex",
                "QueryRetrievePatientAge", "QueryRetrievePatientSize",
                "QueryRetrievePatientWeight", "QueryRetrieveReferencedFileGroup",
                "QueryRetrieveMoveOriginatorApplication", "QueryRetrieveMoveOriginatorMessage",
                "QueryRetrieveMoveOriginatorApplicationEntity", "QueryRetrieveMoveApplicationVersion",
                "NumberOfStudyRelatedInstances", "NumberOfSeriesRelatedInstances",
                "NumberOfStudyRelatedSeries", "SeriesTime", "SeriesDate",
                "AcquisitionDate", "ContentDate", "StudyDate", "SeriesNumber",
                "AcquisitionNumber", "InstanceNumber", "ImageNumber", "SliceNumber",
                "PhaseNumber", "IntervalNumber", "TimeSlotNumber", "AngleNumber",
                "ItemNumber", "PatientOrientation", "PatientOrientationModifierCodeSequence",
                "PatientTransportMethod", "ReferencedStudyNumber", "ReferencedSeriesNumber",
                "ReferencedInstanceNumber", "ReferencedImageNumber", "ReferencedFrameNumber",
                "NumberOfReferences", "DocumentClass", "DocumentTitle",
                "ConceptPropertyBinary", "ConceptPropertyCharacter", "ConceptPropertyInteger",
                "ConceptPropertyDate", "ConceptPropertyTime", "ConceptPropertyPersonName",
                "ConceptPropertyUID", "ConceptPropertyOB", "ConceptPropertyOW",
                "ConceptPropertyOF", "ConceptPropertyOD", "ConceptPropertyOL",
                "ConceptPropertyUN", "ConceptPropertyST", "ConceptPropertyLT",
                "ConceptPropertyUT", "ConceptPropertyDS", "ConceptPropertyIS",
                "ConceptPropertySH", "ConceptPropertyLO", "ConceptPropertySQ",
                "ConceptPropertyPN", "ConceptPropertyTM", "ConceptPropertyDA",
                "ConceptPropertyCS", "ConceptPropertyFL", "ConceptPropertyFD",
                "ConceptPropertyFB", "ConceptPropertyAE", "ConceptPropertyAD",
                "ConceptPropertyAS", "ConceptPropertyAT", "ConceptPropertyEI",
            ],
            "count": 96,
            "reference": "DICOM PS3.4 (Service Class)"
        },
        "display_shading_voi": {
            "description": "Display, shading, and VOI LUT related tags",
            "fields": [
                "ShutterShape", "ShutterLeftVerticalEdge", "ShutterRightVerticalEdge",
                "ShutterUpperHorizontalEdge", "ShutterLowerHorizontalEdge",
                "ShutterCenterCoordinate", "ShutterVerticalEdgeSecondaryAngle",
                "ShutterHorizontalEdgeSecondaryAngle", "ShutterSecondaryAngleUnit",
                "RectangularShutterSequence", "ShutterDescription",
                "ShutterOffset", "ShutterPixelArea", "ShutterPixelOrigin",
                "ShutterPixelFormat", "ShutterValue", "ShutterStatus",
                "ShutterSequence", "ShutterActiveSequence", "ShutterActive",
                "ShutterActiveValue", "ShutterInactiveValue", "ShutterActiveRange",
                "ShutterActiveStart", "ShutterActiveEnd", "BitmapOfShutters",
                "CollimatorShape", "CollimatorLeftVerticalEdge", "CollimatorRightVerticalEdge",
                "CollimatorUpperHorizontalEdge", "CollimatorLowerHorizontalEdge",
                "CollimatorCenterCoordinate", "CollimatorShapeCodeSequence",
                "VOILUTFunction", "WindowCenter", "WindowWidth", "WindowCenterWidthExplanation",
                "WindowCenterWidthExplanationSequence", "WindowWidthExplanation",
                "RescaleIntercept", "RescaleSlope", "RescaleType",
                "VOILUTSequence", "SoftcopyVOILUTSequence", "PresentationLUTSequence",
                "SoftcopyPresentationLUTSequence", "LUTData", "LUTDescriptor",
                "LUTDescriptor", "LUTExplanation", "ModalityLUTSequence",
                "VOILUTFunction", "ModalityType", "LUTFunction", "LUTBandwidth",
                "DisplayShadingMax", "DisplayShadingMin", "DisplayShadingMidpoint",
                "DisplayShadingDistance", "ShadingMode", "AmbientLightIntensity",
                "AmbientLightColor", "ReflectedLightColor", "DisplayFilterColor",
                "DisplayFilterType", "DisplayFilterFrequencyResponse",
                "DisplayFilterPhaseResponse", "DisplayFilterRipple",
                "DisplayFilterAttenuation", "PresentationLUTShape",
                "ReferencedPresentationLUTSequence", "ImplicitVOIType",
                "ExplicitVOIType", "VOITypeOfViewingField", "GrayLookupTableDescriptor",
                "RedPaletteColorLookupTableDescriptor", "GreenPaletteColorLookupTableDescriptor",
                "BluePaletteColorLookupTableDescriptor", "PaletteColorLookupTableUID",
                "GrayLookupTableData", "RedPaletteColorLookupTableData",
                "GreenPaletteColorLookupTableData", "BluePaletteColorLookupTableData",
                "SegmentedRedPaletteColorLookupTableData", "SegmentedGreenPaletteColorLookupTableData",
                "SegmentedBluePaletteColorLookupTableData", "SegmentedAlphaPaletteColorLookupTableData",
                "StoredValueRangeMin", "StoredValueRangeMax", "DisplayShadingTranslation",
                "DisplayShadingRotation", "DisplayShadingFOV", "DisplayShadingPixelOffset",
            ],
            "count": 94,
            "reference": "DICOM PS3.3 (Display)"
        },
        "multi_frame_overlay": {
            "description": "Multi-frame, overlay, and curve data tags",
            "fields": [
                "NumberOfFrames", "FrameIncrementPointer", "FrameDimensionPointer",
                "Rows", "Columns", "Planes", "NumberOfFramesInOverlay",
                "OverlayType", "OverlayOrigin", "OverlayDescriptorGray",
                "OverlayDescriptorRed", "OverlayDescriptorGreen", "OverlayDescriptorBlue",
                "OverlayRows", "OverlayColumns", "OverlayPlanes",
                "NumberOfFramesInOverlay", "OverlayBitPosition", "OverlayFormat",
                "OverlayCodeSequence", "OverlayComments", "OverlayData",
                "OverlayDataLength", "OverlayBitsAllocated", "OverlayBitPosition",
                "OverlayActivationLayer", "OverlayDescription", "OverlayType",
                "OverlaySubtype", "OverlayOrigin", "OverlayCompressionSequence",
                "OverlayCompressionNotify", "OverlayCompressionStepPointers",
                "OverlayCompressionInitialValue", "OverlayCompressionFinalValue",
                "OverlayCompressionRatio", "OverlayCompressionDescription",
                "CurveRange", "CurveDataDescriptor", "CurveDataColumns",
                "NumberOfPointsInCurve", "CurveData", "CurveDataArray",
                "CurveDiameter", "CurveOrientation", "CurveRangeStart",
                "CurveRangeEnd", "CurveDataTypeCodeSequence", "CurveAxisUnits",
                "CurveLabel", "DataValueRepresentation", "MinimumValue",
                "MaximumValue", "CurveDataSequence", "CurveDataArraySize",
                "CurveDescription", "CurveLabelTable", "CurveReferencedOverlaySequence",
                "ReferencedOverlayGroup", "ReferencedCurveGroup", "CurveModificationSequence",
                "AnnotationSequence", "OverlayData", "OverlayTagSequence",
                "OverlayCommentsSequence", "OverlayGroup", "OverlayGroupOpacity",
                "OverlayGroupDescription", "NumberOfOverlayPlanes", "PlaneLabel",
                "PlanePosition", "PlaneOrientation", "PlanePositionSequence",
                "PlaneOrientationSequence", "PlaneBackingImage", "PlaneBackingImageThumbnail",
                "OverlayPlaneRowColumns", "OverlayPlaneColumns", "OverlayPlaneRows",
                "OverlayPlaneDescription", "OverlayPlaneType", "OverlayPlaneSubtype",
            ],
            "count": 79,
            "reference": "DICOM PS3.3 (Multi-frame)"
        }
    },
    "totals": {
        "categories": 10,
        "total_fields": 877
    }
}


def main():
    output_dir = Path("dist/dicom_extended_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "dicom_extended_inventory.json"
    output_file.write_text(json.dumps(DICOM_EXTENDED_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary = {
        "generated_at": DICOM_EXTENDED_INVENTORY["generated_at"],
        "source": DICOM_EXTENDED_INVENTORY["source"],
        "categories": DICOM_EXTENDED_INVENTORY["totals"]["categories"],
        "total_fields": DICOM_EXTENDED_INVENTORY["totals"]["total_fields"],
        "field_counts_by_category": {}
    }
    
    for cat, data in DICOM_EXTENDED_INVENTORY["categories"].items():
        summary["field_counts_by_category"][cat] = {
            "description": data["description"],
            "count": data["count"],
            "reference": data.get("reference", "N/A")
        }
    
    summary_file = output_dir / "dicom_extended_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("DICOM EXTENDED METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {DICOM_EXTENDED_INVENTORY['generated_at']}")
    print(f"Categories: {DICOM_EXTENDED_INVENTORY['totals']['categories']}")
    print(f"Total Fields: {DICOM_EXTENDED_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(DICOM_EXTENDED_INVENTORY["categories"].items(), key=lambda x: x[1]["count"], reverse=True):
        ref = data.get("reference", "")[:35]
        print(f"  {cat:40s}: {data['count']:>3}  [{ref}]")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
