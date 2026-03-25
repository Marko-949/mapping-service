from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
import os
import shutil
from app.core.config import settings
from app.services.worker import run_category_mapping_task

router = APIRouter()

@router.post("/categories_mapping")
async def mapping_categories(
    json_file: UploadFile = File(...),
    file_name: str = Form(...),
    source_type: str = Form("standard") 
):
    task_id = str(uuid.uuid4())

    upload_dir = os.path.join(settings.DATA_DIR, "inputMapping")
    os.makedirs(upload_dir, exist_ok=True)

    input_file_path = os.path.join(upload_dir, f"input_{task_id}.xlsx")
    
    try:
        # 3. Čuvanje fajla
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(json_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri čuvanju fajla: {str(e)}")
    finally:
        json_file.file.close() 

    run_category_mapping_task.delay(task_id, input_file_path, file_name, source_type)

    return {
        "status": "PENDING",
        "task_id": task_id,
        "message": "Proces mapiranja kategorija je uspešno započet.",
        "check_status_url": f"/api/mapping/status/{task_id}"
    }