import logging
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timedelta
from app.database.mongodb import mongodb
from app.services.diet_planner import diet_planner
from app.services.progress_analyzer import progress_analyzer
from app.models.lab_report import HealthAnalysis
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


def _serialize(doc: dict) -> dict:
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = _serialize(value)
        elif isinstance(value, list):
            result[key] = [_serialize(i) if isinstance(i, dict) else i for i in value]
        else:
            result[key] = value
    return result


@router.post("/generate/{report_id}")
async def generate_diet_plan(report_id: str, user: dict = Depends(get_current_user)):
    db = mongodb.get_database()
    user_id = user["id"]

    report = await db.lab_reports.find_one(
        {"_id": ObjectId(report_id), "user_id": user_id}
    )
    if not report:
        raise HTTPException(404, "Lab report not found")

    preferences = {
        "dietary_preferences": user.get("dietary_preferences", ""),
        "allergies": user.get("allergies", []),
        "age": user.get("age"),
        "gender": user.get("gender"),
    }
    health_analysis = HealthAnalysis(**report["health_analysis"])

    previous_report = None
    if report.get("previous_report_id"):
        previous_report = await db.lab_reports.find_one(
            {"_id": ObjectId(report["previous_report_id"])}
        )

    previous_plan = await db.diet_plans.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )

    progress = None
    if previous_report and previous_plan:
        progress = await progress_analyzer.analyze_progress(
            previous_report=_serialize(previous_report),
            current_report=_serialize(report),
            diet_plan=previous_plan.get("days", []),
        )

    plan_data = await diet_planner.generate_plan(
        health_analysis=health_analysis,
        preferences=preferences,
        progress=progress,
    )

    doc = {
        "user_id": user_id,
        "report_id": report_id,
        "previous_plan_id": str(previous_plan["_id"]) if previous_plan else None,
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow() + timedelta(days=7),
        "days": plan_data.get("days", []),
        "rationale": plan_data.get("rationale", ""),
        "progress_report": progress.model_dump() if progress else None,
        "created_at": datetime.utcnow(),
    }

    result = await db.diet_plans.insert_one(doc)
    logger.info("Diet plan generated plan_id=%s for user=%s", str(result.inserted_id), user_id)

    response = _serialize(doc)
    response["id"] = str(result.inserted_id)
    return response


@router.get("/{plan_id}")
async def get_diet_plan(plan_id: str, user: dict = Depends(get_current_user)):
    db = mongodb.get_database()
    doc = await db.diet_plans.find_one(
        {"_id": ObjectId(plan_id), "user_id": user["id"]}
    )
    if not doc:
        raise HTTPException(404, "Diet plan not found")

    response = _serialize(doc)
    response["id"] = str(doc["_id"])
    response.pop("_id", None)
    return response
