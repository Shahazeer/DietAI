from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime

class LabValue(BaseModel):
    value: float
    unit: str
    reference_range: Optional[str] = None
    status: Optional[str] = None

class HealthAnalysis(BaseModel):
    issues: List[str] = []
    risk_factors: List[str] = []
    recommendations: List[str] = []

class LabReportCreate(BaseModel):
    patient_id: str
    report_date: datetime

class LabReportResponse(BaseModel):
    id: str
    patient_id: str
    report_date: datetime
    file_path: str
    extracted_data: Dict[str, Any]
    health_analysis: HealthAnalysis
    created_at: datetime