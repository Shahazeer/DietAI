from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class DietaryPreference(BaseModel):
    type: str = Field(..., pattern="^(veg|non-veg|vegan)$")
    allergies: List[str] = []
    cuisines: List[str] = ["Indian"]
    meal_frequency: int = 3

class PatientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    dietary_preference: DietaryPreference

class PatientResponse(PatientCreate):
    id: str
    created_at: datetime
    updated_at: datetime