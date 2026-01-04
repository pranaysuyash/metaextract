#!/usr/bin/env python3
"""
Healthcare and Medical Metadata Extraction Module - Ultimate Edition

Extracts comprehensive metadata from healthcare and medical data including:
- Electronic Health Records (EHR, EMR, HL7, FHIR)
- Medical Imaging (DICOM, NIfTI, MINC, Analyze, PAR/REC)
- Clinical Trial Data (CDISC, ODM, SAS datasets)
- Laboratory Results (LIS data, pathology reports, lab values)
- Pharmaceutical Data (drug databases, clinical studies, FDA submissions)
- Genomic Medicine (variant calling, pharmacogenomics, precision medicine)
- Telemedicine Data (remote monitoring, wearable devices, mobile health)
- Medical Device Data (pacemakers, insulin pumps, monitoring equipment)
- Public Health Data (epidemiology, surveillance, population health)
- Medical Literature (PubMed, clinical guidelines, systematic reviews)
- Healthcare Analytics (quality metrics, outcomes research, cost analysis)
- Regulatory Data (FDA, EMA, clinical trial registrations, adverse events)

Author: MetaExtract Team
Version: 1.0.0
"""

import os
import json
import struct
import logging
import xml.etree.ElementTree as ET
import csv
import re
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime, timedelta
import hashlib
import base64

logger = logging.getLogger(__name__)

# Library availability checks
try:
    import pandas as pd  # type: ignore[reportMissingImports]
    PANDAS_AVAILABLE = True
except ImportError:
    pd: Any = None
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np: Any = None
    NUMPY_AVAILABLE = False

try:
    import pydicom
    DICOM_AVAILABLE = True
except ImportError:
    pydicom: Any = None
    DICOM_AVAILABLE = False

try:
    import nibabel as nib  # type: ignore[reportMissingImports]
    NIBABEL_AVAILABLE = True
except ImportError:
    nib: Any = None
    NIBABEL_AVAILABLE = False

def extract_healthcare_medical_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive healthcare and medical metadata"""
    
    result: Dict[str, Any] = {
        "available": True,
        "medical_type": "unknown",
        "ehr_emr_data": {},
        "medical_imaging": {},
        "clinical_trial_data": {},
        "laboratory_results": {},
        "pharmaceutical_data": {},
        "genomic_medicine": {},
        "telemedicine_data": {},
        "medical_device_data": {},
        "public_health_data": {},
        "medical_literature": {},
        "healthcare_analytics": {},
        "regulatory_data": {},
        "clinical_standards": {},
        "patient_safety": {}
    }
    
    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()
        
        # Electronic Health Records
        if any(term in filename for term in ['ehr', 'emr', 'hl7', 'fhir', 'cda', 'ccda']):
            result["medical_type"] = "ehr_emr"
            ehr_result = _analyze_ehr_emr_data(filepath, file_ext)
            if ehr_result:
                result["ehr_emr_data"].update(ehr_result)
        
        # Medical Imaging
        elif file_ext in ['.dcm', '.dicom', '.nii', '.nii.gz', '.mnc', '.img', '.hdr', '.par', '.rec']:
            result["medical_type"] = "medical_imaging"
            imaging_result = _analyze_medical_imaging(filepath, file_ext)
            if imaging_result:
                result["medical_imaging"].update(imaging_result)
        
        # Clinical Trial Data
        elif any(term in filename for term in ['clinical', 'trial', 'cdisc', 'odm', 'sdtm', 'adam']):
            result["medical_type"] = "clinical_trial"
            trial_result = _analyze_clinical_trial_data(filepath, file_ext)
            if trial_result:
                result["clinical_trial_data"].update(trial_result)
        
        # Laboratory Results
        elif any(term in filename for term in ['lab', 'laboratory', 'pathology', 'blood', 'urine', 'biopsy']):
            result["medical_type"] = "laboratory"
            lab_result = _analyze_laboratory_results(filepath, file_ext)
            if lab_result:
                result["laboratory_results"].update(lab_result)
        
        # Pharmaceutical Data
        elif any(term in filename for term in ['drug', 'pharmaceutical', 'medication', 'prescription', 'fda']):
            result["medical_type"] = "pharmaceutical"
            pharma_result = _analyze_pharmaceutical_data(filepath, file_ext)
            if pharma_result:
                result["pharmaceutical_data"].update(pharma_result)
        
        # Genomic Medicine
        elif any(term in filename for term in ['genomic', 'genetic', 'dna', 'rna', 'variant', 'snp', 'pharmacogenomic']):
            result["medical_type"] = "genomic_medicine"
            genomic_result = _analyze_genomic_medicine_data(filepath, file_ext)
            if genomic_result:
                result["genomic_medicine"].update(genomic_result)
        
        # Telemedicine Data
        elif any(term in filename for term in ['telemedicine', 'remote', 'wearable', 'mobile_health', 'mhealth']):
            result["medical_type"] = "telemedicine"
            telemedicine_result = _analyze_telemedicine_data(filepath, file_ext)
            if telemedicine_result:
                result["telemedicine_data"].update(telemedicine_result)
        
        # Medical Device Data
        elif any(term in filename for term in ['device', 'pacemaker', 'insulin', 'monitor', 'implant']):
            result["medical_type"] = "medical_device"
            device_result = _analyze_medical_device_data(filepath, file_ext)
            if device_result:
                result["medical_device_data"].update(device_result)
        
        # Public Health Data
        elif any(term in filename for term in ['epidemiology', 'surveillance', 'population', 'outbreak', 'vaccine']):
            result["medical_type"] = "public_health"
            public_health_result = _analyze_public_health_data(filepath, file_ext)
            if public_health_result:
                result["public_health_data"].update(public_health_result)
        
        # Medical Literature
        elif any(term in filename for term in ['pubmed', 'literature', 'guideline', 'review', 'evidence']):
            result["medical_type"] = "medical_literature"
            literature_result = _analyze_medical_literature(filepath, file_ext)
            if literature_result:
                result["medical_literature"].update(literature_result)
        
        # Healthcare Analytics
        elif any(term in filename for term in ['analytics', 'quality', 'outcome', 'cost', 'performance']):
            result["medical_type"] = "healthcare_analytics"
            analytics_result = _analyze_healthcare_analytics(filepath, file_ext)
            if analytics_result:
                result["healthcare_analytics"].update(analytics_result)
        
        # Regulatory Data
        elif any(term in filename for term in ['regulatory', 'adverse', 'safety', 'compliance', 'audit']):
            result["medical_type"] = "regulatory"
            regulatory_result = _analyze_regulatory_data(filepath, file_ext)
            if regulatory_result:
                result["regulatory_data"].update(regulatory_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in healthcare medical analysis: {e}")
        return {"available": False, "error": str(e)}

def _analyze_ehr_emr_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze Electronic Health Records and EMR data"""
    try:
        result: Dict[str, Any] = {
            "ehr_analysis": {
                "record_format": "unknown",
                "patient_data": {},
                "clinical_data": {},
                "administrative_data": {},
                "interoperability": {},
                "privacy_compliance": {},
                "data_quality": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect EHR format
        if 'hl7' in filename:
            result["ehr_analysis"]["record_format"] = "HL7"
            hl7_result = _analyze_hl7_message(filepath)
            if hl7_result:
                result["ehr_analysis"].update(hl7_result)
        elif 'fhir' in filename:
            result["ehr_analysis"]["record_format"] = "FHIR"
            fhir_result = _analyze_fhir_resource(filepath)
            if fhir_result:
                result["ehr_analysis"].update(fhir_result)
        elif 'cda' in filename or 'ccda' in filename:
            result["ehr_analysis"]["record_format"] = "CDA/CCDA"
            cda_result = _analyze_cda_document(filepath)
            if cda_result:
                result["ehr_analysis"].update(cda_result)
        
        # Privacy and compliance indicators
        result["ehr_analysis"]["privacy_compliance"] = {
            "hipaa_relevant": True,
            "phi_detected": True,
            "anonymization_required": True,
            "audit_trail_needed": True
        }
        
        return result
        
    except Exception as e:
        logger.error(f"EHR/EMR analysis error: {e}")
        return {}

def _analyze_hl7_message(filepath: str) -> Dict[str, Any]:
    """Analyze HL7 messages"""
    try:
        result: Dict[str, Any] = {
            "hl7_info": {
                "message_type": "unknown",
                "version": "unknown",
                "segments": [],
                "patient_id": None,
                "encounter_id": None,
                "timestamp": None
            }
        }
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # HL7 messages are typically pipe-delimited
        lines = content.split('\n')
        segments = []
        
        for line in lines:
            if line.strip():
                fields = line.split('|')
                if len(fields) > 0:
                    segment_type = fields[0]
                    segments.append(segment_type)
                    
                    # Extract key information
                    if segment_type == 'MSH':  # Message Header
                        if len(fields) > 8:
                            result["hl7_info"]["message_type"] = fields[8]
                        if len(fields) > 11:
                            result["hl7_info"]["version"] = fields[11]
                    elif segment_type == 'PID':  # Patient Identification
                        if len(fields) > 3:
                            result["hl7_info"]["patient_id"] = "[ANONYMIZED]"  # Don't store actual PID
                    elif segment_type == 'PV1':  # Patient Visit
                        if len(fields) > 19:
                            result["hl7_info"]["encounter_id"] = "[ANONYMIZED]"
        
        result["hl7_info"]["segments"] = list(set(segments))
        result["hl7_info"]["segment_count"] = len(segments)
        
        return result
        
    except Exception as e:
        logger.error(f"HL7 analysis error: {e}")
        return {}

def _analyze_medical_imaging(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze medical imaging files"""
    try:
        result: Dict[str, Any] = {
            "imaging_analysis": {
                "modality": "unknown",
                "anatomy": "unknown",
                "acquisition_params": {},
                "image_properties": {}, 
                "clinical_context": {},
                "quality_metrics": {},
                "processing_history": []
            }
        }
        
        # DICOM analysis
        if file_ext in ['.dcm', '.dicom'] and DICOM_AVAILABLE:
            dicom_result = _analyze_dicom_imaging(filepath)
            if dicom_result:
                result["imaging_analysis"].update(dicom_result)
        
        # NIfTI analysis (neuroimaging)
        elif file_ext in ['.nii', '.nii.gz'] and NIBABEL_AVAILABLE:
            nifti_result = _analyze_nifti_imaging(filepath)
            if nifti_result:
                result["imaging_analysis"].update(nifti_result)
        
        # Analyze/IMG format
        elif file_ext in ['.img', '.hdr']:
            analyze_result = _analyze_img_format(filepath)
            if analyze_result:
                result["imaging_analysis"].update(analyze_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Medical imaging analysis error: {e}")
        return {}

def _analyze_dicom_imaging(filepath: str) -> Dict[str, Any]:
    """Analyze DICOM medical images"""
    try:
        ds = pydicom.dcmread(filepath, force=True)
        
        result: Dict[str, Any] = {
            "modality": getattr(ds, 'Modality', 'Unknown'),
            "anatomy": getattr(ds, 'BodyPartExamined', 'Unknown'),
            "acquisition_params": {
                "study_date": getattr(ds, 'StudyDate', None),
                "study_time": getattr(ds, 'StudyTime', None),
                "series_description": getattr(ds, 'SeriesDescription', None),
                "protocol_name": getattr(ds, 'ProtocolName', None),
                "slice_thickness": getattr(ds, 'SliceThickness', None),
                "pixel_spacing": getattr(ds, 'PixelSpacing', None)
            },
            "image_properties": {
                "rows": getattr(ds, 'Rows', None),
                "columns": getattr(ds, 'Columns', None),
                "bits_allocated": getattr(ds, 'BitsAllocated', None),
                "photometric_interpretation": getattr(ds, 'PhotometricInterpretation', None)
            },
            "clinical_context": {
                "patient_age": getattr(ds, 'PatientAge', None),
                "patient_sex": getattr(ds, 'PatientSex', None),
                "study_description": getattr(ds, 'StudyDescription', None),
                "referring_physician": "[ANONYMIZED]" if hasattr(ds, 'ReferringPhysicianName') else None
            }
        }
        
        # Modality-specific parameters
        modality = result["modality"]
        if modality == 'MR':
            result["acquisition_params"].update({
                "magnetic_field_strength": getattr(ds, 'MagneticFieldStrength', None),
                "repetition_time": getattr(ds, 'RepetitionTime', None),
                "echo_time": getattr(ds, 'EchoTime', None),
                "flip_angle": getattr(ds, 'FlipAngle', None)
            })
        elif modality == 'CT':
            result["acquisition_params"].update({
                "kvp": getattr(ds, 'KVP', None),
                "tube_current": getattr(ds, 'XRayTubeCurrent', None),
                "exposure_time": getattr(ds, 'ExposureTime', None),
                "convolution_kernel": getattr(ds, 'ConvolutionKernel', None)
            })
        elif modality == 'US':
            result["acquisition_params"].update({
                "transducer_frequency": getattr(ds, 'TransducerFrequency', None),
                "mechanical_index": getattr(ds, 'MechanicalIndex', None),
                "thermal_index": getattr(ds, 'ThermalIndex', None)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"DICOM imaging analysis error: {e}")
        return {}

def _analyze_clinical_trial_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze clinical trial data"""
    try:
        result: Dict[str, Any] = {
            "trial_analysis": {
                "study_design": "unknown",
                "data_standard": "unknown",
                "subject_data": {},
                "endpoints": {},
                "adverse_events": {},
                "protocol_deviations": {},
                "data_quality": {},
                "regulatory_compliance": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect CDISC standards
        if any(term in filename for term in ['sdtm', 'send']):
            result["trial_analysis"]["data_standard"] = "SDTM"
        elif 'adam' in filename:
            result["trial_analysis"]["data_standard"] = "ADaM"
        elif 'odm' in filename:
            result["trial_analysis"]["data_standard"] = "ODM"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Look for clinical trial indicators
            clinical_indicators = {
                'demographics': ['age', 'sex', 'race', 'ethnicity', 'dob'],
                'adverse_events': ['ae', 'adverse', 'event', 'sae', 'serious'],
                'efficacy': ['efficacy', 'endpoint', 'response', 'outcome'],
                'safety': ['safety', 'lab', 'vital', 'ecg', 'physical'],
                'dosing': ['dose', 'medication', 'drug', 'treatment', 'therapy']
            }
            
            detected_domains = []
            for domain, indicators in clinical_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_domains.append(domain)
                        break
            
            result["trial_analysis"]["detected_domains"] = list(set(detected_domains))
            
            # Subject data analysis
            subject_columns = [col for col in df.columns if any(subj_term in col.lower() 
                              for subj_term in ['subject', 'patient', 'usubjid', 'subjid'])]
            
            if subject_columns:
                subject_col = subject_columns[0]
                unique_subjects = df[subject_col].nunique()
                result["trial_analysis"]["subject_data"] = {
                    "total_subjects": unique_subjects,
                    "total_records": len(df),
                    "records_per_subject": len(df) / unique_subjects if unique_subjects > 0 else 0
                }
            
            # Data quality assessment
            missing_data = df.isnull().sum()
            result["trial_analysis"]["data_quality"] = {
                "completeness": (1 - missing_data.sum() / (len(df) * len(df.columns))),
                "columns_with_missing": len(missing_data[missing_data > 0]),
                "total_missing_values": int(missing_data.sum())
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Clinical trial analysis error: {e}")
        return {}

def _analyze_laboratory_results(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze laboratory results and pathology data"""
    try:
        result: Dict[str, Any] = {
            "lab_analysis": {
                "test_type": "unknown",
                "specimen_info": {},
                "test_results": {},

                "reference_ranges": {},
                "quality_control": {},
                "critical_values": {},
                "turnaround_time": {}
            }
        }
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Detect laboratory test types
            lab_indicators = {
                'chemistry': ['glucose', 'sodium', 'potassium', 'creatinine', 'bun', 'alt', 'ast'],
                'hematology': ['wbc', 'rbc', 'hemoglobin', 'hematocrit', 'platelet', 'mcv'],
                'microbiology': ['culture', 'sensitivity', 'organism', 'antibiotic', 'gram'],
                'immunology': ['antibody', 'antigen', 'iga', 'igg', 'igm', 'complement'],
                'molecular': ['pcr', 'dna', 'rna', 'mutation', 'gene', 'allele'],
                'pathology': ['biopsy', 'cytology', 'histology', 'malignant', 'benign']
            }
            
            detected_tests = []
            for test_type, indicators in lab_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_tests.append(test_type)
                        break
            
            result["lab_analysis"]["test_type"] = detected_tests
            
            # Analyze test results
            numeric_cols = df.select_dtypes(include=[np.number])
            if not numeric_cols.empty:
                result["lab_analysis"]["test_results"] = {
                    "numeric_tests": len(numeric_cols.columns),
                    "result_ranges": {
                        col: {"min": float(numeric_cols[col].min()), "max": float(numeric_cols[col].max())}
                        for col in numeric_cols.columns
                    }
                }
                
                # Detect critical values (outliers)
                critical_results = {}
                for col in numeric_cols.columns:
                    col_data = numeric_cols[col].dropna()
                    if len(col_data) > 1:
                        q1 = col_data.quantile(0.25)
                        q3 = col_data.quantile(0.75)
                        iqr = q3 - q1
                        outliers = col_data[(col_data < q1 - 1.5*iqr) | (col_data > q3 + 1.5*iqr)]
                        critical_results[col] = len(outliers)
                
                result["lab_analysis"]["critical_values"] = critical_results
            
            # Quality control indicators
            qc_columns = [col for col in df.columns if any(qc_term in col.lower() 
                         for qc_term in ['qc', 'control', 'standard', 'blank'])]
            
            if qc_columns:
                result["lab_analysis"]["quality_control"] = {
                    "qc_samples": len(qc_columns),
                    "qc_ratio": len(qc_columns) / len(df.columns)
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Laboratory analysis error: {e}")
        return {}

def _analyze_pharmaceutical_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze pharmaceutical and drug data"""
    try:
        result: Dict[str, Any] = {
            "pharma_analysis": {
                "data_type": "unknown",
                "drug_info": {},
                "clinical_studies": {}, 
                "adverse_events": {},
                "regulatory_status": {},
                "pharmacokinetics": {},
                "drug_interactions": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect pharmaceutical data type
        if any(term in filename for term in ['ndc', 'rxnorm', 'drug_database']):
            result["pharma_analysis"]["data_type"] = "drug_database"
        elif any(term in filename for term in ['clinical_study', 'phase']):
            result["pharma_analysis"]["data_type"] = "clinical_study"
        elif any(term in filename for term in ['adverse', 'adr', 'side_effect']):
            result["pharma_analysis"]["data_type"] = "adverse_events"
        elif any(term in filename for term in ['pk', 'pharmacokinetic', 'adme']):
            result["pharma_analysis"]["data_type"] = "pharmacokinetics"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Drug information analysis
            drug_columns = [col for col in df.columns if any(drug_term in col.lower() 
                           for drug_term in ['drug', 'medication', 'compound', 'substance'])]
            
            if drug_columns:
                drug_col = drug_columns[0]
                unique_drugs = df[drug_col].nunique()
                result["pharma_analysis"]["drug_info"] = {
                    "unique_drugs": unique_drugs,
                    "total_records": len(df)
                }
            
            # Adverse event analysis
            ae_columns = [col for col in df.columns if any(ae_term in col.lower() 
                         for ae_term in ['adverse', 'side_effect', 'reaction', 'adr'])]
            
            if ae_columns:
                ae_counts = {}
                for col in ae_columns:
                    ae_counts[col] = df[col].value_counts().to_dict()
                result["pharma_analysis"]["adverse_events"] = ae_counts
            
            # Dosing information
            dose_columns = [col for col in df.columns if any(dose_term in col.lower() 
                           for dose_term in ['dose', 'dosage', 'strength', 'concentration'])]
            
            if dose_columns:
                result["pharma_analysis"]["dosing_info"] = {
                    "dose_columns": dose_columns,
                    "dose_variations": len(dose_columns)
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Pharmaceutical analysis error: {e}")
        return {}

def _analyze_telemedicine_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze telemedicine and remote monitoring data"""
    try:
        result: Dict[str, Any] = {
            "telemedicine_analysis": {
                "monitoring_type": "unknown",
                "device_data": {},
                "vital_signs": {},

                "patient_reported": {},
                "connectivity": {},
                "data_transmission": {},
                "alert_thresholds": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect monitoring type
        if any(term in filename for term in ['heart_rate', 'ecg', 'cardiac']):
            result["telemedicine_analysis"]["monitoring_type"] = "cardiac"
        elif any(term in filename for term in ['glucose', 'diabetes', 'cgm']):
            result["telemedicine_analysis"]["monitoring_type"] = "diabetes"
        elif any(term in filename for term in ['blood_pressure', 'hypertension']):
            result["telemedicine_analysis"]["monitoring_type"] = "blood_pressure"
        elif any(term in filename for term in ['activity', 'steps', 'fitness']):
            result["telemedicine_analysis"]["monitoring_type"] = "activity"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Vital signs detection
            vital_indicators = {
                'heart_rate': ['hr', 'heart_rate', 'pulse', 'bpm'],
                'blood_pressure': ['bp', 'systolic', 'diastolic', 'pressure'],
                'temperature': ['temp', 'temperature', 'fever'],
                'oxygen_saturation': ['spo2', 'oxygen', 'saturation'],
                'respiratory_rate': ['rr', 'respiratory', 'breathing'],
                'glucose': ['glucose', 'sugar', 'bg', 'blood_glucose']
            }
            
            detected_vitals = {}
            for vital_type, indicators in vital_indicators.items():
                matching_columns = []
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        matching_columns.append(col)
                
                if matching_columns:
                    detected_vitals[vital_type] = {
                        "columns": matching_columns,
                        "measurements": len(df)
                    }
            
            result["telemedicine_analysis"]["vital_signs"] = detected_vitals
            
            # Time series analysis for continuous monitoring
            time_columns = [col for col in df.columns if any(time_term in col.lower() 
                           for time_term in ['time', 'timestamp', 'date', 'datetime'])]
            
            if time_columns and len(df) > 1:
                result["telemedicine_analysis"]["data_transmission"] = {
                    "continuous_monitoring": True,
                    "data_points": len(df),
                    "monitoring_duration": "unknown"  # Would need to parse timestamps
                }
            
            # Alert threshold analysis
            numeric_cols = df.select_dtypes(include=[np.number])
            if not numeric_cols.empty:
                threshold_analysis = {}
                for col in numeric_cols.columns:
                    col_data = numeric_cols[col].dropna()
                    if len(col_data) > 1:
                        # Simple threshold detection based on outliers
                        mean_val = col_data.mean()
                        std_val = col_data.std()
                        outliers = col_data[(col_data < mean_val - 2*std_val) | (col_data > mean_val + 2*std_val)]
                        threshold_analysis[col] = {
                            "potential_alerts": len(outliers),
                            "alert_rate": len(outliers) / len(col_data)
                        }
                
                result["telemedicine_analysis"]["alert_thresholds"] = threshold_analysis
        
        return result
        
    except Exception as e:
        logger.error(f"Telemedicine analysis error: {e}")
        return {}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_healthcare_medical_metadata(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python healthcare_medical_ultimate.py <medical_file>")

def _analyze_fhir_resource(filepath: str) -> Dict[str, Any]:
    """Analyze FHIR resources"""
    try:
        result: Dict[str, Any] = {
            "fhir_info": {
                "resource_type": "unknown",
                "version": "unknown",
                "patient_references": [],
                "practitioner_references": [],
                "organization_references": [],
                "encounter_references": []
            }
        }
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to parse as JSON (FHIR resources are typically JSON)
        try:
            import json
            fhir_data = json.loads(content)
            
            if isinstance(fhir_data, dict):
                result["fhir_info"]["resource_type"] = fhir_data.get("resourceType", "unknown")
                
                # Extract FHIR version from meta
                if "meta" in fhir_data:
                    meta = fhir_data["meta"]
                    if "versionId" in meta:
                        result["fhir_info"]["version"] = meta["versionId"]
                
                # Extract references (anonymized)
                def extract_references(obj, ref_type):
                    refs = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key == "reference" and isinstance(value, str):
                                if ref_type.lower() in value.lower():
                                    refs.append("[ANONYMIZED_REFERENCE]")
                            elif isinstance(value, (dict, list)):
                                refs.extend(extract_references(value, ref_type))
                    elif isinstance(obj, list):
                        for item in obj:
                            refs.extend(extract_references(item, ref_type))
                    return refs
                
                result["fhir_info"]["patient_references"] = extract_references(fhir_data, "Patient")
                result["fhir_info"]["practitioner_references"] = extract_references(fhir_data, "Practitioner")
                result["fhir_info"]["organization_references"] = extract_references(fhir_data, "Organization")
                result["fhir_info"]["encounter_references"] = extract_references(fhir_data, "Encounter")
        
        except ValueError:
            # Not valid JSON, treat as text
            pass
        except Exception:
            # Fallback: ignore parsing errors and continue
            pass
        
        return result
        
    except Exception as e:
        logger.error(f"FHIR analysis error: {e}")
        return {}

def _analyze_cda_document(filepath: str) -> Dict[str, Any]:
    """Analyze CDA/CCDA documents"""
    try:
        result = {
            "cda_info": {
                "document_type": "unknown",
                "template_ids": [],
                "patient_info": {},
                "author_info": {},
                "sections": []
            }
        }
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse XML structure
        try:
            root = ET.fromstring(content)
            
            # Extract template IDs
            for template in root.findall('.//{urn:hl7-org:v3}templateId'):
                root_attr = template.get('root')
                if root_attr:
                    result["cda_info"]["template_ids"].append(root_attr)
            
            # Extract document type from code
            code_elem = root.find('.//{urn:hl7-org:v3}code')
            if code_elem is not None:
                result["cda_info"]["document_type"] = code_elem.get('displayName', 'unknown')
            
            # Extract sections (anonymized)
            for section in root.findall('.//{urn:hl7-org:v3}section'):
                section_code = section.find('.//{urn:hl7-org:v3}code')
                if section_code is not None:
                    section_name = section_code.get('displayName', 'unknown')
                    result["cda_info"]["sections"].append(section_name)
        
        except ET.ParseError:
            # Not valid XML
            pass
        
        return result
        
    except Exception as e:
        logger.error(f"CDA analysis error: {e}")
        return {}

def _analyze_nifti_imaging(filepath: str) -> Dict[str, Any]:
    """Analyze NIfTI neuroimaging files"""
    try:
        img = nib.load(filepath)
        
        result = {
            "modality": "neuroimaging",
            "anatomy": "brain",
            "image_properties": {
                "shape": img.shape,
                "data_type": str(img.get_fdata().dtype),
                "voxel_size": img.header.get_zooms()[:3] if len(img.header.get_zooms()) >= 3 else None,
                "orientation": str(img.header.get_best_affine())
            },
            "acquisition_params": {
                "tr": img.header.get('pixdim')[4] if len(img.header.get('pixdim')) > 4 else None,
                "slice_thickness": img.header.get_zooms()[2] if len(img.header.get_zooms()) > 2 else None
            },
            "processing_history": {
                "description": img.header.get('descrip', b'').decode('utf-8', errors='ignore'),
                "aux_file": img.header.get('aux_file', b'').decode('utf-8', errors='ignore')
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"NIfTI analysis error: {e}")
        return {}

def _analyze_img_format(filepath: str) -> Dict[str, Any]:
    """Analyze Analyze/IMG format files"""
    try:
        result = {
            "modality": "medical_imaging",
            "format": "analyze_img",
            "image_properties": {},
            "header_info": {}
        }
        
        # Try to read header file (.hdr)
        hdr_path = filepath.replace('.img', '.hdr')
        if os.path.exists(hdr_path):
            with open(hdr_path, 'rb') as f:
                # Read basic header information (simplified)
                header_data = f.read(348)  # Standard Analyze header size
                if len(header_data) >= 348:
                    # Extract key fields (basic implementation)
                    import struct
                    dims = struct.unpack('8h', header_data[40:56])
                    result["image_properties"]["dimensions"] = dims[1:4]  # Skip first element
                    
                    datatype = struct.unpack('h', header_data[70:72])[0]
                    result["image_properties"]["data_type"] = datatype
                    
                    voxel_size = struct.unpack('8f', header_data[76:108])
                    result["image_properties"]["voxel_size"] = voxel_size[1:4]  # Skip first element
        
        return result
        
    except Exception as e:
        logger.error(f"Analyze/IMG analysis error: {e}")
        return {}

def _analyze_genomic_medicine_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze genomic and precision medicine data"""
    try:
        result = {
            "genomic_analysis": {
                "data_type": "unknown",
                "sequence_info": {},
                "variant_data": {},
                "pharmacogenomics": {},
                "population_genetics": {},
                "clinical_significance": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect genomic data type
        if any(term in filename for term in ['vcf', 'variant']):
            result["genomic_analysis"]["data_type"] = "variant_calling"
        elif any(term in filename for term in ['fasta', 'fastq', 'sequence']):
            result["genomic_analysis"]["data_type"] = "sequence_data"
        elif any(term in filename for term in ['gwas', 'snp']):
            result["genomic_analysis"]["data_type"] = "gwas_snp"
        elif any(term in filename for term in ['pharmacogenomic', 'pgx']):
            result["genomic_analysis"]["data_type"] = "pharmacogenomics"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Genomic data indicators
            genomic_indicators = {
                'variants': ['chr', 'chromosome', 'position', 'ref', 'alt', 'variant'],
                'genes': ['gene', 'symbol', 'ensembl', 'entrez'],
                'phenotypes': ['phenotype', 'trait', 'disease', 'condition'],
                'drugs': ['drug', 'medication', 'compound', 'therapeutic'],
                'populations': ['population', 'ancestry', 'ethnicity', 'cohort']
            }
            
            detected_categories = []
            for category, indicators in genomic_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_categories.append(category)
                        break
            
            result["genomic_analysis"]["detected_categories"] = list(set(detected_categories))
            
            # Variant analysis
            if 'variants' in detected_categories:
                variant_columns = [col for col in df.columns if any(var_term in col.lower() 
                                  for var_term in ['chr', 'pos', 'ref', 'alt', 'variant'])]
                
                if variant_columns:
                    result["genomic_analysis"]["variant_data"] = {
                        "total_variants": len(df),
                        "variant_columns": variant_columns
                    }
                    
                    # Chromosome distribution
                    chr_columns = [col for col in df.columns if 'chr' in col.lower()]
                    if chr_columns:
                        chr_dist = df[chr_columns[0]].value_counts().to_dict()
                        result["genomic_analysis"]["variant_data"]["chromosome_distribution"] = chr_dist
            
            # Clinical significance analysis
            clinical_columns = [col for col in df.columns if any(clin_term in col.lower() 
                               for clin_term in ['clinical', 'pathogenic', 'benign', 'significance'])]
            
            if clinical_columns:
                clinical_data = {}
                for col in clinical_columns:
                    clinical_data[col] = df[col].value_counts().to_dict()
                result["genomic_analysis"]["clinical_significance"] = clinical_data
        
        return result
        
    except Exception as e:
        logger.error(f"Genomic medicine analysis error: {e}")
        return {}

def _analyze_medical_device_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze medical device data"""
    try:
        result = {
            "device_analysis": {
                "device_type": "unknown",
                "monitoring_data": {},
                "alerts_alarms": {},
                "device_status": {},
                "patient_interaction": {},
                "maintenance_data": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect device type
        if any(term in filename for term in ['pacemaker', 'icd', 'cardiac']):
            result["device_analysis"]["device_type"] = "cardiac_device"
        elif any(term in filename for term in ['insulin', 'pump', 'cgm', 'diabetes']):
            result["device_analysis"]["device_type"] = "diabetes_management"
        elif any(term in filename for term in ['ventilator', 'respiratory']):
            result["device_analysis"]["device_type"] = "respiratory_support"
        elif any(term in filename for term in ['monitor', 'vital', 'bedside']):
            result["device_analysis"]["device_type"] = "patient_monitor"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Device monitoring indicators
            monitoring_indicators = {
                'cardiac': ['heart_rate', 'rhythm', 'pacing', 'shock', 'atrial', 'ventricular'],
                'diabetes': ['glucose', 'insulin', 'bolus', 'basal', 'carb', 'bg'],
                'respiratory': ['oxygen', 'co2', 'pressure', 'volume', 'flow', 'peep'],
                'vital_signs': ['bp', 'temp', 'spo2', 'pulse', 'respiration']
            }
            
            detected_monitoring = {}
            for monitor_type, indicators in monitoring_indicators.items():
                matching_columns = []
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        matching_columns.append(col)
                
                if matching_columns:
                    detected_monitoring[monitor_type] = {
                        "columns": matching_columns,
                        "data_points": len(df)
                    }
            
            result["device_analysis"]["monitoring_data"] = detected_monitoring
            
            # Alert and alarm analysis
            alert_columns = [col for col in df.columns if any(alert_term in col.lower() 
                            for alert_term in ['alert', 'alarm', 'warning', 'critical', 'emergency'])]
            
            if alert_columns:
                alert_data = {}
                for col in alert_columns:
                    if df[col].dtype == 'object':
                        alert_counts = df[col].value_counts().to_dict()
                        alert_data[col] = alert_counts
                    else:
                        # Numeric alert data
                        col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(col_data) > 0:
                            alert_data[col] = {
                                "total_alerts": int(col_data.sum()),
                                "alert_rate": float(col_data.mean())
                            }
                
                result["device_analysis"]["alerts_alarms"] = alert_data
            
            # Device status tracking
            status_columns = [col for col in df.columns if any(status_term in col.lower() 
                             for status_term in ['status', 'state', 'mode', 'enabled', 'active'])]
            
            if status_columns:
                status_data = {}
                for col in status_columns:
                    status_data[col] = df[col].value_counts().to_dict()
                result["device_analysis"]["device_status"] = status_data
        
        return result
        
    except Exception as e:
        logger.error(f"Medical device analysis error: {e}")
        return {}

def _analyze_public_health_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze public health and epidemiology data"""
    try:
        result = {
            "public_health_analysis": {
                "data_type": "unknown",
                "epidemiology": {},
                "surveillance": {},
                "population_health": {},
                "outbreak_investigation": {},
                "vaccination_data": {},
                "environmental_health": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect public health data type
        if any(term in filename for term in ['outbreak', 'epidemic', 'pandemic']):
            result["public_health_analysis"]["data_type"] = "outbreak_investigation"
        elif any(term in filename for term in ['surveillance', 'monitoring', 'reporting']):
            result["public_health_analysis"]["data_type"] = "disease_surveillance"
        elif any(term in filename for term in ['vaccine', 'vaccination', 'immunization']):
            result["public_health_analysis"]["data_type"] = "vaccination_program"
        elif any(term in filename for term in ['environmental', 'air_quality', 'water']):
            result["public_health_analysis"]["data_type"] = "environmental_health"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Epidemiological indicators
            epi_indicators = {
                'disease': ['disease', 'condition', 'diagnosis', 'icd', 'syndrome'],
                'demographics': ['age', 'sex', 'gender', 'race', 'ethnicity', 'population'],
                'geography': ['county', 'state', 'zip', 'region', 'location', 'address'],
                'temporal': ['date', 'week', 'month', 'year', 'onset', 'report'],
                'outcomes': ['death', 'hospitalization', 'recovery', 'outcome', 'severity']
            }
            
            detected_epi = {}
            for epi_type, indicators in epi_indicators.items():
                matching_columns = []
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        matching_columns.append(col)
                
                if matching_columns:
                    detected_epi[epi_type] = {
                        "columns": matching_columns,
                        "records": len(df)
                    }
            
            result["public_health_analysis"]["epidemiology"] = detected_epi
            
            # Case count analysis
            case_columns = [col for col in df.columns if any(case_term in col.lower() 
                           for case_term in ['case', 'count', 'incidence', 'prevalence', 'rate'])]
            
            if case_columns:
                case_analysis = {}
                for col in case_columns:
                    col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(col_data) > 0:
                        case_analysis[col] = {
                            "total_cases": int(col_data.sum()),
                            "average_cases": float(col_data.mean()),
                            "peak_cases": int(col_data.max()),
                            "case_distribution": col_data.describe().to_dict()
                        }
                
                result["public_health_analysis"]["surveillance"] = case_analysis
            
            # Vaccination analysis
            vaccine_columns = [col for col in df.columns if any(vax_term in col.lower() 
                              for vax_term in ['vaccine', 'vaccination', 'immunization', 'dose', 'shot'])]
            
            if vaccine_columns:
                vaccine_data = {}
                for col in vaccine_columns:
                    if df[col].dtype == 'object':
                        vaccine_data[col] = df[col].value_counts().to_dict()
                    else:
                        col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(col_data) > 0:
                            vaccine_data[col] = {
                                "total_doses": int(col_data.sum()),
                                "coverage_rate": float(col_data.mean())
                            }
                
                result["public_health_analysis"]["vaccination_data"] = vaccine_data
        
        return result
        
    except Exception as e:
        logger.error(f"Public health analysis error: {e}")
        return {}

def _analyze_medical_literature(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze medical literature and research publications"""
    try:
        result = {
            "literature_analysis": {
                "publication_type": "unknown",
                "research_domain": {},
                "methodology": {},
                "evidence_level": {},
                "clinical_relevance": {},
                "citation_data": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect publication type
        if any(term in filename for term in ['systematic_review', 'meta_analysis']):
            result["literature_analysis"]["publication_type"] = "systematic_review"
        elif any(term in filename for term in ['rct', 'randomized', 'clinical_trial']):
            result["literature_analysis"]["publication_type"] = "clinical_trial"
        elif any(term in filename for term in ['guideline', 'recommendation']):
            result["literature_analysis"]["publication_type"] = "clinical_guideline"
        elif any(term in filename for term in ['case_study', 'case_report']):
            result["literature_analysis"]["publication_type"] = "case_report"
        
        # Text analysis for research content
        if file_ext in ['.txt', '.pdf']:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Research domain detection
                medical_domains = {
                    'cardiology': ['heart', 'cardiac', 'cardiovascular', 'coronary', 'myocardial'],
                    'oncology': ['cancer', 'tumor', 'oncology', 'chemotherapy', 'radiation'],
                    'neurology': ['brain', 'neurological', 'stroke', 'seizure', 'dementia'],
                    'infectious_disease': ['infection', 'bacteria', 'virus', 'antibiotic', 'pathogen'],
                    'psychiatry': ['depression', 'anxiety', 'psychiatric', 'mental', 'psychological'],
                    'surgery': ['surgical', 'operation', 'procedure', 'laparoscopic', 'robotic']
                }
                
                detected_domains = []
                content_lower = content.lower()
                for domain, keywords in medical_domains.items():
                    if any(keyword in content_lower for keyword in keywords):
                        detected_domains.append(domain)
                
                result["literature_analysis"]["research_domain"] = {
                    "detected_domains": detected_domains,
                    "primary_domain": detected_domains[0] if detected_domains else "unknown"
                }
                
                # Methodology detection
                methodology_keywords = {
                    'randomized_controlled_trial': ['randomized', 'controlled', 'rct', 'placebo'],
                    'observational_study': ['observational', 'cohort', 'case-control', 'cross-sectional'],
                    'systematic_review': ['systematic review', 'meta-analysis', 'cochrane'],
                    'laboratory_study': ['in vitro', 'laboratory', 'experimental', 'cell culture'],
                    'animal_study': ['animal', 'mouse', 'rat', 'in vivo', 'preclinical']
                }
                
                detected_methods = []
                for method, keywords in methodology_keywords.items():
                    if any(keyword in content_lower for keyword in keywords):
                        detected_methods.append(method)
                
                result["literature_analysis"]["methodology"] = {
                    "study_types": detected_methods,
                    "primary_methodology": detected_methods[0] if detected_methods else "unknown"
                }
                
                # Evidence level indicators
                evidence_indicators = {
                    'high_evidence': ['level i', 'grade a', 'strong recommendation', 'high quality'],
                    'moderate_evidence': ['level ii', 'grade b', 'moderate quality', 'conditional'],
                    'low_evidence': ['level iii', 'grade c', 'low quality', 'weak recommendation'],
                    'expert_opinion': ['expert opinion', 'consensus', 'grade d', 'level v']
                }
                
                evidence_levels = []
                for level, indicators in evidence_indicators.items():
                    if any(indicator in content_lower for indicator in indicators):
                        evidence_levels.append(level)
                
                result["literature_analysis"]["evidence_level"] = {
                    "detected_levels": evidence_levels,
                    "highest_level": evidence_levels[0] if evidence_levels else "unknown"
                }
                
            except Exception as e:
                logger.warning(f"Text analysis failed: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Medical literature analysis error: {e}")
        return {}

def _analyze_healthcare_analytics(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze healthcare analytics and quality metrics"""
    try:
        result = {
            "analytics_analysis": {
                "metrics_type": "unknown",
                "quality_indicators": {},
                "performance_metrics": {},
                "cost_analysis": {},
                "outcome_measures": {},
                "population_health": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect analytics type
        if any(term in filename for term in ['quality', 'hedis', 'cms', 'measure']):
            result["analytics_analysis"]["metrics_type"] = "quality_measures"
        elif any(term in filename for term in ['cost', 'financial', 'revenue', 'billing']):
            result["analytics_analysis"]["metrics_type"] = "financial_analytics"
        elif any(term in filename for term in ['outcome', 'mortality', 'readmission']):
            result["analytics_analysis"]["metrics_type"] = "outcome_analytics"
        elif any(term in filename for term in ['population', 'risk', 'stratification']):
            result["analytics_analysis"]["metrics_type"] = "population_health"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Quality indicator analysis
            quality_indicators = {
                'patient_safety': ['infection', 'fall', 'medication_error', 'adverse_event'],
                'clinical_effectiveness': ['mortality', 'readmission', 'complication', 'outcome'],
                'patient_experience': ['satisfaction', 'experience', 'hcahps', 'cahps'],
                'efficiency': ['length_stay', 'turnaround', 'wait_time', 'throughput'],
                'equity': ['disparity', 'equity', 'access', 'demographic']
            }
            
            detected_quality = {}
            for quality_type, indicators in quality_indicators.items():
                matching_columns = []
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        matching_columns.append(col)
                
                if matching_columns:
                    quality_metrics = {}
                    for col in matching_columns:
                        col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(col_data) > 0:
                            quality_metrics[col] = {
                                "mean": float(col_data.mean()),
                                "median": float(col_data.median()),
                                "std": float(col_data.std()),
                                "min": float(col_data.min()),
                                "max": float(col_data.max())
                            }
                    
                    detected_quality[quality_type] = {
                        "columns": matching_columns,
                        "metrics": quality_metrics
                    }
            
            result["analytics_analysis"]["quality_indicators"] = detected_quality
            
            # Cost analysis
            cost_columns = [col for col in df.columns if any(cost_term in col.lower() 
                           for cost_term in ['cost', 'charge', 'payment', 'revenue', 'price'])]
            
            if cost_columns:
                cost_analysis = {}
                for col in cost_columns:
                    col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(col_data) > 0:
                        cost_analysis[col] = {
                            "total_cost": float(col_data.sum()),
                            "average_cost": float(col_data.mean()),
                            "cost_distribution": {
                                "q25": float(col_data.quantile(0.25)),
                                "q50": float(col_data.quantile(0.50)),
                                "q75": float(col_data.quantile(0.75)),
                                "q95": float(col_data.quantile(0.95))
                            }
                        }
                
                result["analytics_analysis"]["cost_analysis"] = cost_analysis
            
            # Performance benchmarking
            benchmark_columns = [col for col in df.columns if any(bench_term in col.lower() 
                                for bench_term in ['benchmark', 'target', 'goal', 'standard', 'percentile'])]
            
            if benchmark_columns:
                benchmark_data = {}
                for col in benchmark_columns:
                    col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(col_data) > 0:
                        benchmark_data[col] = {
                            "performance_score": float(col_data.mean()),
                            "above_benchmark": int(len(col_data[col_data > col_data.mean()])),
                            "below_benchmark": int(len(col_data[col_data < col_data.mean()]))
                        }
                
                result["analytics_analysis"]["performance_metrics"] = benchmark_data
        
        return result
        
    except Exception as e:
        logger.error(f"Healthcare analytics analysis error: {e}")
        return {}

def _analyze_regulatory_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze regulatory and compliance data"""
    try:
        result = {
            "regulatory_analysis": {
                "regulation_type": "unknown",
                "compliance_status": {},
                "adverse_events": {},
                "audit_findings": {},
                "safety_reporting": {},
                "quality_assurance": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect regulatory type
        if any(term in filename for term in ['fda', 'adverse', 'medwatch', 'faers']):
            result["regulatory_analysis"]["regulation_type"] = "fda_reporting"
        elif any(term in filename for term in ['hipaa', 'privacy', 'breach']):
            result["regulatory_analysis"]["regulation_type"] = "privacy_compliance"
        elif any(term in filename for term in ['audit', 'inspection', 'finding']):
            result["regulatory_analysis"]["regulation_type"] = "regulatory_audit"
        elif any(term in filename for term in ['safety', 'incident', 'report']):
            result["regulatory_analysis"]["regulation_type"] = "safety_reporting"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Adverse event analysis
            ae_indicators = {
                'severity': ['serious', 'severe', 'mild', 'moderate', 'fatal'],
                'causality': ['related', 'unrelated', 'possible', 'probable', 'definite'],
                'outcome': ['recovered', 'fatal', 'hospitalization', 'disability'],
                'product': ['device', 'drug', 'medication', 'product', 'manufacturer']
            }
            
            detected_ae = {}
            for ae_type, indicators in ae_indicators.items():
                matching_columns = []
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        matching_columns.append(col)
                
                if matching_columns:
                    ae_data = {}
                    for col in matching_columns:
                        if df[col].dtype == 'object':
                            ae_data[col] = df[col].value_counts().to_dict()
                        else:
                            col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                            if len(col_data) > 0:
                                ae_data[col] = {
                                    "count": int(col_data.sum()),
                                    "rate": float(col_data.mean())
                                }
                    
                    detected_ae[ae_type] = ae_data
            
            result["regulatory_analysis"]["adverse_events"] = detected_ae
            
            # Compliance status analysis
            compliance_columns = [col for col in df.columns if any(comp_term in col.lower() 
                                 for comp_term in ['compliance', 'violation', 'deficiency', 'corrective'])]
            
            if compliance_columns:
                compliance_data = {}
                for col in compliance_columns:
                    compliance_data[col] = df[col].value_counts().to_dict()
                result["regulatory_analysis"]["compliance_status"] = compliance_data
            
            # Audit findings
            audit_columns = [col for col in df.columns if any(audit_term in col.lower() 
                            for audit_term in ['finding', 'observation', 'citation', 'warning'])]
            
            if audit_columns:
                audit_data = {}
                for col in audit_columns:
                    audit_data[col] = df[col].value_counts().to_dict()
                result["regulatory_analysis"]["audit_findings"] = audit_data
        
        return result
        
    except Exception as e:
        logger.error(f"Regulatory analysis error: {e}")
        return {}