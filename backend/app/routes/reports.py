import hashlib
import logging
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query, Response
from bson import ObjectId
from bson.errors import InvalidId
from pathlib import Path
from app.database.mongodb import mongodb
from app.config import settings
from app.services.ocr_service import ocr_service
from app.dependencies.auth import get_current_user
from app.utils.serialization import serialize_doc

logger = logging.getLogger(__name__)
router = APIRouter()

PDF_MAGIC = b"%PDF"
MAX_BYTES = settings.max_upload_size_mb * 1024 * 1024
_SAFE_FILENAME = re.compile(r"[^a-zA-Z0-9._\-]")


def _sanitize_filename(name: str) -> str:
    """Strip directory components and allow only safe filename characters."""
    name = Path(name).name
    return _SAFE_FILENAME.sub("_", name) or "upload.pdf"


@router.post("/upload")
async def upload_lab_report(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    # Validate content-type header
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(400, detail="Only PDF files are accepted")

    # Read with hard size limit — reads MAX_BYTES+1 so we can detect oversize files
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, detail=f"File exceeds {settings.max_upload_size_mb} MB limit")

    # Validate PDF magic bytes
    if raw[:4] != PDF_MAGIC:
        raise HTTPException(400, detail="File does not appear to be a valid PDF")

    file_hash = hashlib.sha256(raw).hexdigest()

    db = mongodb.get_database()
    user_id = user["id"]

    # Reject duplicate uploads for the same user
    duplicate = await db.lab_reports.find_one({"user_id": user_id, "file_hash": file_hash})
    if duplicate:
        raise HTTPException(409, detail="This file has already been uploaded")

    pdfs_dir = Path(settings.upload_dir) / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _sanitize_filename(file.filename or "upload.pdf")
    file_name = f"{user_id}_{datetime.now(timezone.utc).timestamp()}_{safe_name}"
    file_path = pdfs_dir / file_name

    with open(file_path, "wb") as f:
        f.write(raw)

    logger.info("Report uploaded by user=%s file=%s hash=%s", user_id, file_name, file_hash[:12])

    preferences = {
        "dietary_preferences": user.get("dietary_preferences", ""),
        "allergies": user.get("allergies", []),
    }

    try:
        extracted_data, health_analysis = await ocr_service.process_report(
            str(file_path), preferences
        )
    except Exception as e:
        logger.error("OCR processing failed for file=%s: %s", file_name, e)
        file_path.unlink(missing_ok=True)  # clean up the saved file on failure
        raise HTTPException(502, detail="Failed to process the PDF. Please ensure the file is a clear, readable lab report.")

    previous_report = await db.lab_reports.find_one(
        {"user_id": user_id},
        sort=[("upload_date", -1)],
    )

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "filename": safe_name,
        "file_hash": file_hash,
        "upload_date": now,
        "file_path": str(file_path),  # internal only — stripped by serialize_doc / never returned
        "extracted_data": {k: v.model_dump() for k, v in extracted_data.items()},
        "health_analysis": health_analysis.model_dump(),
        "previous_report_id": str(previous_report["_id"]) if previous_report else None,
    }

    result = await db.lab_reports.insert_one(doc)
    report_id = str(result.inserted_id)
    logger.info("Report saved report_id=%s", report_id)

    return {
        "id": report_id,
        "filename": safe_name,
        "extracted_data": doc["extracted_data"],
        "health_analysis": doc["health_analysis"],
    }


@router.get("/history")
async def get_report_history(
    user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    db = mongodb.get_database()
    user_id = user["id"]
    skip = (page - 1) * limit

    # Fetch reports page
    report_docs = await (
        db.lab_reports.find({"user_id": user_id})
        .sort("upload_date", -1)
        .skip(skip)
        .limit(limit)
        .to_list(limit)
    )
    if not report_docs:
        return []

    # Batch-fetch the most recent diet plan per report — one query instead of N
    report_ids = [str(doc["_id"]) for doc in report_docs]
    diet_cursor = db.diet_plans.find({"report_id": {"$in": report_ids}}).sort("created_at", -1)
    # Keep only the most recent plan per report_id
    latest_diet: dict[str, dict] = {}
    async for diet in diet_cursor:
        rid = diet.get("report_id", "")
        if rid not in latest_diet:
            latest_diet[rid] = diet

    reports = []
    for doc in report_docs:
        report_id = str(doc["_id"])
        diet = latest_diet.get(report_id)
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
    try:
        oid = ObjectId(report_id)
    except InvalidId:
        raise HTTPException(400, detail="Invalid report ID format")

    db = mongodb.get_database()
    doc = await db.lab_reports.find_one({"_id": oid, "user_id": user["id"]})
    if not doc:
        raise HTTPException(404, detail="Report not found")

    diet = await db.diet_plans.find_one(
        {"report_id": report_id}, sort=[("created_at", -1)]
    )

    serialized = serialize_doc(doc)
    serialized["id"] = str(doc["_id"])
    serialized.pop("_id", None)
    serialized["diet_plan"] = serialize_doc(diet) if diet else None
    if serialized["diet_plan"]:
        serialized["diet_plan"]["id"] = str(diet["_id"])
        serialized["diet_plan"].pop("_id", None)

    return serialized


@router.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str, user: dict = Depends(get_current_user)):
    """
    Hard-delete a report and all associated diet plans.
    Also removes the uploaded PDF file from disk.
    """
    try:
        oid = ObjectId(report_id)
    except InvalidId:
        raise HTTPException(400, detail="Invalid report ID format")

    db = mongodb.get_database()
    user_id = user["id"]

    doc = await db.lab_reports.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        raise HTTPException(404, detail="Report not found")

    # Delete the PDF from disk (best-effort — don't fail if already gone)
    file_path = doc.get("file_path")
    if file_path:
        Path(file_path).unlink(missing_ok=True)
        logger.info("Deleted file from disk: %s", file_path)

    # Delete all diet plans linked to this report
    diet_result = await db.diet_plans.delete_many({"report_id": report_id})

    # Delete the report itself
    await db.lab_reports.delete_one({"_id": oid})

    logger.info(
        "Deleted report_id=%s and %d diet plan(s) for user=%s",
        report_id, diet_result.deleted_count, user_id,
    )
    return Response(status_code=204)
