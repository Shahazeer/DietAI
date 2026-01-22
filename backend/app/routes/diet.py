from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timedelta
from app.database.mongodb import mongodb
from app.services.diet_planner import diet_planner
from app.services.progress_analyzer import progress_analyzer
from app.models.lab_report import HealthAnalysis
from app.models.diet_plan import ProgressReport

router = APIRouter()

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    return result

@router.post("/generate/{report_id}")
async def generate_diet_plan(report_id: str):
    db = mongodb.get_database()

    report = await db.lab_reports.find_one({"_id": ObjectId(report_id)})
    if not report:
        raise HTTPException(404, "Lab report not found")

    patient = await db.patients.find_one({"_id": ObjectId(report["patient_id"])})
    if not patient:
        raise HTTPException(404, "Patient not found")

    preferences = patient.get("dietary_preference", {})
    health_analysis = HealthAnalysis(**report["health_analysis"])

    previous_report = await db.lab_reports.find_one(
        {"patient_id": report["patient_id"], "_id": {"$ne": ObjectId(report_id)}},
        sort=[("report_date", -1)]
    )

    previous_plan = await db.diet_plans.find_one(
        {"patient_id": report["patient_id"]},
        sort=[("created_at", -1)]
    )

    progress = None
    if previous_report and previous_plan:
        prev_report_serialized = serialize_doc(previous_report)
        curr_report_serialized = serialize_doc(report)

        progress = await progress_analyzer.analyze_progress(
            previous_report=prev_report_serialized,
            current_report=curr_report_serialized,
            diet_plan=previous_plan.get("days", [])
        )

    plan_data = await diet_planner.generate_plan(
        health_analysis=health_analysis,
        preferences=preferences,
        progress=progress
    )

    doc = {
        "patient_id": report["patient_id"],
        "lab_report_id": report_id,
        "previous_plan_id": str(previous_plan["_id"]) if previous_plan else None,
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow() + timedelta(days=7),
        "days": plan_data.get("days", []),
        "rationale": plan_data.get("rationale", ""),
        "progress_report": progress.model_dump() if progress else None,
        "created_at": datetime.utcnow()
    }

    result = await db.diet_plans.insert_one(doc)
    
    # Serialize for response
    response = serialize_doc(doc)
    response["id"] = str(result.inserted_id)
    
    return response

@router.get("/{plan_id}")
async def get_diet_plan(plan_id: str):
    db = mongodb.get_database()
    doc = await db.diet_plans.find_one({"_id": ObjectId(plan_id)})

    if not doc:
        raise HTTPException(404, "Diet plan not found")

    response = serialize_doc(doc)
    response["id"] = str(doc.pop("_id"))
    return response