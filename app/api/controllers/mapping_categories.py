from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
import os
import shutil
from app.core.config import settings
from app.services.worker import run_category_mapping_task, fetch_provider_data_task

router = APIRouter()


import json
import os
from fastapi import APIRouter, HTTPException, Query
from app.services.providers.factory import ProviderFactory

router = APIRouter()

@router.post("/fetch-categories-async")
async def fetch_categories_async(
    provider_type: str, 
    shop_name: str, 
    url: str, ck: str, cs: str
):
    credentials = {"url": url, "ck": ck, "cs": cs}
    
    task = fetch_provider_data_task.delay(provider_type, credentials, shop_name)
    
    return {
        "task_id": task.id,
        "status": "Processing in background",
        "message": "Podaci se preuzimaju. Provjerite status kasnije."
    }


@router.post("/categories_mapping")
async def mapping_categories(
    json_file: UploadFile = File(...),
    file_name: str = Form(...),
    provider_type: str = Form("...") 
):
    task_id = str(uuid.uuid4())

    upload_dir = os.path.join(settings.DATA_DIR, "inputMapping")
    os.makedirs(upload_dir, exist_ok=True)

    input_file_path = os.path.join(upload_dir, f"input_{task_id}.xlsx")
    
    try:
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(json_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri čuvanju fajla: {str(e)}")
    finally:
        json_file.file.close() 

    run_category_mapping_task.delay(task_id, input_file_path, file_name, provider_type)

    return {
        "status": "PENDING",
        "task_id": task_id,
        "message": "Proces mapiranja kategorija je uspešno započet.",
        "check_status_url": f"/api/mapping/status/{task_id}"
    }