from pydantic import BaseModel


class Meal(BaseModel):
    name: str
    ingredients: list[str]
    benefits: list[str]
    calories: int | None = None


class DayPlan(BaseModel):
    day: int
    breakfast: Meal
    morning_snack: Meal | None = None
    lunch: Meal
    evening_snack: Meal | None = None
    dinner: Meal


class ProgressReport(BaseModel):
    previous_issues: list[str]
    current_issues: list[str]
    improvements: list[str]
    deteriorations: list[str]
    effectiveness_score: float  # 0–100
    summary: str = ""
