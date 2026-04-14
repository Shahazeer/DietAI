from pydantic import BaseModel


class LabValue(BaseModel):
    value: float
    unit: str
    reference_range: str | None = None
    status: str | None = None


class HealthAnalysis(BaseModel):
    issues: list[str] = []
    risk_factors: list[str] = []
    recommendations: list[str] = []


class _DataQuality(BaseModel):
    uncertain_readings: list[str] = []
    corrections_made: list[str] = []
    missing_common_tests: list[str] = []


class ContemplationResult(BaseModel):
    """Typed schema for the contemplation model's JSON output."""
    lab_values: dict[str, dict] = {}
    categories: dict[str, list[str]] = {}
    health_analysis: dict = {}
    data_quality: _DataQuality = _DataQuality()
