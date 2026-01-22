from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class Meal(BaseModel):
    name: str
    ingredients: List[str]
    benefits: List[str]
    calories: Optional[int] = None

class DayPlan(BaseModel):
    day: int
    breakfast: Meal
    morning_snack: Optional[Meal] = None
    lunch: Meal
    evening_snack: Optional[Meal] = None
    dinner: Meal

class ProgressReport(BaseModel):
    previous_issues: List[str]
    current_issues: List[str]
    improvements: List[str]
    deteriorations: List[str]
    effectiveness_score: float  # 0-100

class DietPlanResponse(BaseModel):
    id: str
    patient_id: str
    lab_report_id: str
    previous_plan_id: Optional[str] = None
    start_date: datetime
    end_date: datetime
    days: List[DayPlan]
    rationale: str
    progress_report: Optional[ProgressReport] = None
    created_at: datetime