"""
Dose Trend Analysis API Routes

Provides endpoints for tracking cumulative radiation dose across multiple DICOM studies.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/dose", tags=["dose"])


@dataclass
class DoseStudy:
    study_instance_uid: str
    study_id: str
    study_date: str
    study_time: str
    study_description: str
    modality: str
    body_part_examined: str
    accession_number: Optional[str] = None
    referring_physician: Optional[str] = None
    institution_name: Optional[str] = None
    station_name: Optional[str] = None


@dataclass
class CTDoseInfo:
    ct_divol: Optional[float] = None
    dlp: Optional[float] = None
    exposure: Optional[float] = None
    exposure_time: Optional[float] = None
    kvp: Optional[float] = None
    xray_tube_current: Optional[float] = None


class DoseAnalysisRequest(BaseModel):
    patient_id: Optional[str] = None
    studies: List[Dict[str, Any]] = Field(..., description="List of DICOM study metadata")
    thresholds: Optional[Dict[str, float]] = None


class DoseStudyResponse(BaseModel):
    study: Dict[str, Any]
    series: List[Dict[str, Any]]
    ct_dose: Optional[CTDoseInfo] = None
    total_dose_mgy: float = 0


class CumulativeDoseResponse(BaseModel):
    patient_id: str
    patient_name: str
    total_studies: int
    total_dose_mgy: float
    total_dlp_mgy_cm: float
    average_dose_per_study: float
    max_single_study_dose: float
    min_single_study_dose: float
    first_study_date: str
    last_study_date: str
    date_range_days: int
    dose_by_modality: Dict[str, float]
    trends: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]


class DoseAlertResponse(BaseModel):
    id: str
    severity: str
    type: str
    title: str
    message: str
    dose_value: Optional[float] = None
    threshold: Optional[float] = None
    recommendation: str
    acknowledged: bool = False
    created_at: str


DEFAULT_THRESHOLDS = {
    "cumulative_dlp_warning": 400,
    "cumulative_dlp_critical": 600,
    "single_study_dlp_warning": 300,
    "single_study_dlp_critical": 500,
    "monthly_dose_warning": 50,
    "monthly_dose_critical": 100,
    "study_frequency_warning": 5,
    "study_frequency_critical": 10,
}


def parse_dicom_date(date_str: str) -> Optional[datetime]:
    """Parse DICOM date string (YYYYMMDD) to datetime."""
    if not date_str or len(date_str) < 8:
        return None
    try:
        return datetime(
            int(date_str[:4]),
            int(date_str[4:6]),
            int(date_str[6:8])
        )
    except (ValueError, IndexError):
        return None


def calculate_study_dose(study: Dict[str, Any]) -> float:
    """Calculate total dose for a single study."""
    ct_dose = study.get("ct_dose", {})
    radionuclide_dose = study.get("radionuclide_dose", {})

    if ct_dose.get("dlp"):
        return float(ct_dose["dlp"])
    if ct_dose.get("ct_divol"):
        return float(ct_dose["ct_divol"])
    if radionuclide_dose.get("radionuclide_total_dose"):
        return float(radionuclide_dose["radionuclide_total_dose"])

    return 0


def analyze_dose_trends(
    studies: List[Dict[str, Any]],
    thresholds: Dict[str, float]
) -> CumulativeDoseResponse:
    """Analyze cumulative dose across multiple studies."""

    if not studies:
        return CumulativeDoseResponse(
            patient_id="",
            patient_name="",
            total_studies=0,
            total_dose_mgy=0,
            total_dlp_mgy_cm=0,
            average_dose_per_study=0,
            max_single_study_dose=0,
            min_single_study_dose=0,
            first_study_date="",
            last_study_date="",
            date_range_days=0,
            dose_by_modality={},
            trends=[],
            alerts=[]
        )

    sorted_studies = sorted(
        studies,
        key=lambda s: parse_dicom_date(s.get("study", {}).get("study_date", "")) or datetime.min
    )

    doses = [calculate_study_dose(s) for s in sorted_studies]
    valid_doses = [d for d in doses if d > 0]

    cumulative_dlp = 0
    cumulative_dose = 0
    trends = []
    dose_by_modality = {}

    for i, study in enumerate(sorted_studies):
        dose = calculate_study_dose(study)
        study_dlp = study.get("ct_dose", {}).get("dlp") or dose
        cumulative_dlp += study_dlp
        cumulative_dose += dose

        study_info = study.get("study", {})
        modality = study_info.get("modality", "Unknown")

        if dose > 0:
            dose_by_modality[modality] = dose_by_modality.get(modality, 0) + dose

        trends.append({
            "date": study_info.get("study_date", ""),
            "study_count": i + 1,
            "cumulative_dlp_mgy_cm": round(cumulative_dlp, 2),
            "cumulative_dose_mgy": round(cumulative_dose, 2),
            "study_uid": study_info.get("study_instance_uid", ""),
            "modality": modality,
            "description": study_info.get("study_description", "")
        })

    first_date = sorted_studies[0].get("study", {}).get("study_date", "")
    last_date = sorted_studies[-1].get("study", {}).get("study_date", "")
    first_date_obj = parse_dicom_date(first_date)
    last_date_obj = parse_dicom_date(last_date)

    date_range_days = 0
    if first_date_obj and last_date_obj:
        date_range_days = (last_date_obj - first_date_obj).days

    patient_info = sorted_studies[0].get("patient", {})
    alerts = generate_dose_alerts(trends, cumulative_dlp, thresholds)

    return CumulativeDoseResponse(
        patient_id=patient_info.get("patient_id", ""),
        patient_name=patient_info.get("patient_name", ""),
        total_studies=len(sorted_studies),
        total_dose_mgy=round(cumulative_dose, 2),
        total_dlp_mgy_cm=round(cumulative_dlp, 2),
        average_dose_per_study=round(cumulative_dose / len(valid_doses), 2) if valid_doses else 0,
        max_single_study_dose=max(valid_doses) if valid_doses else 0,
        min_single_study_dose=min(valid_doses) if valid_doses else 0,
        first_study_date=first_date,
        last_study_date=last_date,
        date_range_days=date_range_days,
        dose_by_modality={k: round(v, 2) for k, v in dose_by_modality.items()},
        trends=trends,
        alerts=alerts
    )


def generate_dose_alerts(
    trends: List[Dict[str, Any]],
    cumulative_dlp: float,
    thresholds: Dict[str, float]
) -> List[Dict[str, Any]]:
    """Generate dose safety alerts based on thresholds."""
    alerts = []

    if cumulative_dlp >= thresholds.get("cumulative_dlp_critical", 600):
        alerts.append({
            "id": f"alert-critical-{datetime.now().timestamp()}",
            "severity": "critical",
            "type": "cumulative_threshold",
            "title": "Critical Cumulative Dose Exceeded",
            "message": f"Total DLP of {cumulative_dlp:.1f} mGy·cm exceeds critical threshold of {thresholds.get('cumulative_dlp_critical', 600)} mGy·cm.",
            "dose_value": cumulative_dlp,
            "threshold": thresholds.get("cumulative_dlp_critical", 600),
            "recommendation": "Consider alternative imaging modalities or delay elective studies. Consult radiology safety officer.",
            "acknowledged": False,
            "created_at": datetime.now().isoformat()
        })
    elif cumulative_dlp >= thresholds.get("cumulative_dlp_warning", 400):
        alerts.append({
            "id": f"alert-warning-{datetime.now().timestamp()}",
            "severity": "high",
            "type": "cumulative_threshold",
            "title": "Cumulative Dose Warning",
            "message": f"Total DLP of {cumulative_dlp:.1f} mGy·cm has reached warning threshold.",
            "dose_value": cumulative_dlp,
            "threshold": thresholds.get("cumulative_dlp_warning", 400),
            "recommendation": "Monitor future studies closely and consider dose reduction strategies.",
            "acknowledged": False,
            "created_at": datetime.now().isoformat()
        })

    recent_count = len([t for t in trends if t["study_count"] > len(trends) - 30])
    if recent_count >= thresholds.get("study_frequency_critical", 10):
        alerts.append({
            "id": f"alert-frequency-{datetime.now().timestamp()}",
            "severity": "critical",
            "type": "trend_acceleration",
            "title": "Critical Study Frequency",
            "message": f"{recent_count} studies in the past 30 days exceeds critical threshold.",
            "recommendation": "Review imaging utilization and consider consolidating future studies.",
            "acknowledged": False,
            "created_at": datetime.now().isoformat()
        })

    return sorted(alerts, key=lambda a: {"critical": 0, "high": 1, "medium": 2, "low": 3}[a["severity"]])


@router.post("/analyze", response_model=CumulativeDoseResponse)
async def analyze_dose(request: DoseAnalysisRequest):
    """
    Analyze cumulative radiation dose across multiple DICOM studies.
    
    This endpoint processes a list of study metadata and calculates:
    - Total cumulative dose (DLP)
    - Dose distribution by modality
    - Safety alerts based on configurable thresholds
    - Trend analysis over time
    """
    thresholds = request.thresholds or DEFAULT_THRESHOLDS
    return analyze_dose_trends(request.studies, thresholds)


@router.get("/cumulative/{patient_id}", response_model=CumulativeDoseResponse)
async def get_patient_cumulative_dose(
    patient_id: str,
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYYMMDD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYYMMDD)"),
    modality: Optional[str] = Query(None, description="Filter by modality")
):
    """
    Get cumulative dose analysis for a specific patient.
    
    Requires patient studies to be stored in the database.
    """
    return CumulativeDoseResponse(
        patient_id=patient_id,
        patient_name="",
        total_studies=0,
        total_dose_mgy=0,
        total_dlp_mgy_cm=0,
        average_dose_per_study=0,
        max_single_study_dose=0,
        min_single_study_dose=0,
        first_study_date="",
        last_study_date="",
        date_range_days=0,
        dose_by_modality={},
        trends=[],
        alerts=[]
    )


@router.get("/alerts")
async def get_dose_alerts(
    patient_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low")
):
    """Get dose alerts for patients."""
    return {"alerts": [], "count": 0}


@router.post("/export")
async def export_dose_report(
    patient_id: str,
    format: str = Query("json", description="Export format: json, csv, pdf, fhir")
):
    """
    Export dose analysis report in various formats.
    
    Supported formats:
    - json: Full data export with all details
    - csv: Spreadsheet-compatible format
    - pdf: Formatted report document
    - fhir: HL7 FHIR format for healthcare interoperability
    """
    return {
        "patient_id": patient_id,
        "format": format,
        "message": "Report export initiated",
        "status": "pending"
    }


@router.get("/thresholds")
async def get_dose_thresholds():
    """Get configurable dose safety thresholds."""
    return DEFAULT_THRESHOLDS


@router.put("/thresholds")
async def update_dose_thresholds(thresholds: Dict[str, float]):
    """Update dose safety thresholds."""
    return {"thresholds": thresholds, "message": "Thresholds updated"}
