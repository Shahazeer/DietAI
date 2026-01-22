from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from app.database.mongodb import mongodb
from app.models.patient import PatientCreate, PatientResponse

router = APIRouter()


@router.post("/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate):
    db = mongodb.get_database()

    existing = await db.patients.find_one({"email": patient.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    doc = patient.model_dump()
    doc["created_at"] = datetime.now()
    doc["updated_at"] = datetime.now()

    result = await db.patients.insert_one(doc)
    doc["id"] = str(result.inserted_id)

    return PatientResponse(**doc)

# IMPORTANT: This must come BEFORE /{patient_id} routes!
@router.get("/search")
async def search_patient(email: str):
    """Search for a patient by email"""
    db = mongodb.get_database()
    doc = await db.patients.find_one({"email": email})
    if not doc:
        raise HTTPException(status_code=404, detail="Patient not found")
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    db = mongodb.get_database()
    doc = await db.patients.find_one({"_id": ObjectId(patient_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Patient not found")
    doc["id"] = str(doc.pop("_id"))
    return PatientResponse(**doc)

@router.get("/{patient_id}/history")
async def get_patient_history(patient_id: str):
    """Get all reports and diet plans for a patient"""
    db = mongodb.get_database()

    reports = await db.lab_reports.find(
        {"patient_id": patient_id}
    ).sort("report_date", -1).to_list(100)

    plans = await db.diet_plans.find(
        {"patient_id": patient_id}
    ).sort("created_at", -1).to_list(100)

    return {
        "reports": [{**r, "id": str(r.pop("_id"))} for r in reports],
        "plans": [{**p, "id": str(p.pop("_id"))} for p in plans]
    }
