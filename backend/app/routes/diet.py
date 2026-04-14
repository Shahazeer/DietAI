import logging
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timedelta, timezone
from app.database.mongodb import mongodb
from app.services.diet_planner import diet_planner
from app.services.progress_analyzer import progress_analyzer
from app.models.lab_report import HealthAnalysis
from app.dependencies.auth import get_current_user
from app.utils.serialization import serialize_doc

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate/{report_id}")
async def generate_diet_plan(report_id: str, user: dict = Depends(get_current_user)):
    try:
        report_oid = ObjectId(report_id)
    except InvalidId:
        raise HTTPException(400, detail="Invalid report ID format")

    db = mongodb.get_database()
    user_id = user["id"]

    report = await db.lab_reports.find_one(
        {"_id": report_oid, "user_id": user_id}
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
        try:
            prev_oid = ObjectId(report["previous_report_id"])
            previous_report = await db.lab_reports.find_one({"_id": prev_oid})
        except InvalidId:
            logger.warning("Invalid previous_report_id stored: %s", report["previous_report_id"])

    previous_plan = await db.diet_plans.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )

    progress = None
    if previous_report and previous_plan:
        progress = await progress_analyzer.analyze_progress(
            previous_report=serialize_doc(previous_report),
            current_report=serialize_doc(report),
            diet_plan=previous_plan.get("days", []),
        )

    plan_data = await diet_planner.generate_plan(
        health_analysis=health_analysis,
        preferences=preferences,
        progress=progress,
    )

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "report_id": report_id,
        "previous_plan_id": str(previous_plan["_id"]) if previous_plan else None,
        "start_date": now,
        "end_date": now + timedelta(days=7),
        "days": plan_data.get("days", []),
        "rationale": plan_data.get("rationale", ""),
        "progress_report": progress.model_dump() if progress else None,
        "created_at": now,
    }

    result = await db.diet_plans.insert_one(doc)
    logger.info("Diet plan generated plan_id=%s for user=%s", str(result.inserted_id), user_id)

    response = serialize_doc(doc)
    response["id"] = str(result.inserted_id)
    return response


@router.get("/{plan_id}")
async def get_diet_plan(plan_id: str, user: dict = Depends(get_current_user)):
    try:
        plan_oid = ObjectId(plan_id)
    except InvalidId:
        raise HTTPException(400, detail="Invalid plan ID format")

    db = mongodb.get_database()
    doc = await db.diet_plans.find_one(
        {"_id": plan_oid, "user_id": user["id"]}
    )
    if not doc:
        raise HTTPException(404, "Diet plan not found")

    response = serialize_doc(doc)
    response["id"] = str(doc["_id"])
    response.pop("_id", None)
    return response
