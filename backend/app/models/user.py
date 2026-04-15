from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator


class DietType(str, Enum):
    vegetarian = "vegetarian"
    vegan = "vegan"
    eggetarian = "eggetarian"
    non_veg = "non-veg"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    age: int
    gender: str
    dietary_preferences: DietType = DietType.non_veg
    allergies: list[str] = []

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    age: int
    gender: str
    dietary_preferences: DietType
    allergies: list[str]

    @field_validator("dietary_preferences", mode="before")
    @classmethod
    def coerce_diet_type(cls, v: object) -> str:
        """Coerce legacy/unknown values (e.g. empty string) to non-veg."""
        valid = {e.value for e in DietType}
        return v if v in valid else DietType.non_veg.value


class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    gender: str | None = None
    dietary_preferences: DietType | None = None
    allergies: list[str] | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
