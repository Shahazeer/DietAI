from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from bson import ObjectId
from datetime import datetime
from pathlib import Path
import shutil
from app.database.mongodb import mongodb
from app.config import settings
from app.services.ocr_service import ocr_service
from app.models.lab_report import LabReportResponse

router = APIRouter()

@router.post("/upload")
async def upload_lab_report(
    patient_id: str = Form(...),
    report_date: str = Form(...),
    file: UploadFile = File(...)
):
    db = mongodb.get_database()

    patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
    if not patient:
        raise HTTPException(404, detail="Patient not found")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)

    file_ext = Path(file.filename).suffix
    file_name = f"{patient_id}_{datetime.now().timestamp()}{file_ext}"
    file_path = upload_dir / file_name

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    extracted_data, health_analysis = await ocr_service.process_report(
        str(file_path),
        patient.get("dietary_preferences", {})
    )

    doc = {
        "patient_id": patient_id,
        "report_date": datetime.fromisoformat(report_date),
        "file_path": str(file_path),
        "extracted_data": {k: v.model_dump() for k, v in extracted_data.items()},
        "health_analysis": health_analysis.model_dump(),
        "created_at": datetime.now()
    }

    result = await db.lab_reports.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return {
        "id": doc["id"],
        "extracted_data": doc["extracted_data"],
        "health_analysis": doc["health_analysis"]
    }

@router.get("/{report_id}")
async def get_report(report_id: str):
    db = mongodb.get_database()
    doc = await db.lab_reports.find_one({"_id": ObjectId(report_id)})

    if not doc:
        raise HTTPException(404, detail="Report not found")
    
    doc["id"] = str(doc.pop("_id"))
    return doc
