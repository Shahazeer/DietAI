import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from bson import ObjectId
from datetime import datetime
from pathlib import Path
import shutil
from app.database.mongodb import mongodb
from app.config import settings
from app.services.ocr_service import ocr_service
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


@router.post("/upload")
async def upload_lab_report(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    db = mongodb.get_database()
    user_id = user["id"]

    pdfs_dir = Path(settings.upload_dir) / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(file.filename).suffix
    file_name = f"{user_id}_{datetime.now().timestamp()}{file_ext}"
    file_path = pdfs_dir / file_name

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    logger.info("Report uploaded by user=%s file=%s", user_id, file_name)

    preferences = {
        "dietary_preferences": user.get("dietary_preferences", ""),
        "allergies": user.get("allergies", []),
    }

    extracted_data, health_analysis = await ocr_service.process_report(
        str(file_path), preferences
    )

    # Check for a previous report to compare
    previous_report = await db.lab_reports.find_one(
        {"user_id": user_id},
        sort=[("upload_date", -1)],
    )

    doc = {
        "user_id": user_id,
        "filename": file.filename,
        "upload_date": datetime.utcnow(),
        "file_path": str(file_path),
        "extracted_data": {k: v.model_dump() for k, v in extracted_data.items()},
        "health_analysis": health_analysis.model_dump(),
        "previous_report_id": str(previous_report["_id"]) if previous_report else None,
    }

    result = await db.lab_reports.insert_one(doc)
    report_id = str(result.inserted_id)
    logger.info("Report saved report_id=%s", report_id)

    return {
        "id": report_id,
        "filename": file.filename,
        "extracted_data": doc["extracted_data"],
        "health_analysis": doc["health_analysis"],
    }


@router.get("/history")
async def get_report_history(user: dict = Depends(get_current_user)):
    db = mongodb.get_database()
    user_id = user["id"]

    cursor = db.lab_reports.find({"user_id": user_id}).sort("upload_date", -1)
    reports = []
    async for doc in cursor:
        report_id = str(doc["_id"])
        diet = await db.diet_plans.find_one(
            {"report_id": report_id}, sort=[("created_at", -1)]
        )
        extracted = doc.get("extracted_data", {})
        health = doc.get("health_analysis", {})
        reports.append({
            "id": report_id,
            "filename": doc.get("filename", ""),
            "upload_date": doc["upload_date"].isoformat(),
            "test_count": len(extracted),
            "issues": health.get("issues", []),
            "diet_plan_id": str(diet["_id"]) if diet else None,
        })

    return reports


@router.get("/{report_id}")
async def get_report(report_id: str, user: dict = Depends(get_current_user)):
    db = mongodb.get_database()
    doc = await db.lab_reports.find_one(
        {"_id": ObjectId(report_id), "user_id": user["id"]}
    )
    if not doc:
        raise HTTPException(404, detail="Report not found")

    diet = await db.diet_plans.find_one(
        {"report_id": report_id}, sort=[("created_at", -1)]
    )

    serialized = _serialize(doc)
    serialized["id"] = str(doc["_id"])
    serialized.pop("_id", None)
    serialized["diet_plan"] = _serialize(diet) if diet else None
    if serialized["diet_plan"]:
        serialized["diet_plan"]["id"] = str(diet["_id"])
        serialized["diet_plan"].pop("_id", None)

    return serialized
