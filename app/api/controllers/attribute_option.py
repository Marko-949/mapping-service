from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
import os
import shutil
from app.core.config import settings
from app.services.worker import run_attribute_option

router = APIRouter()

@router.post("/attribute_option_mapping")
async def start_mapping(
    provider: str = Form(...),      
    url: str = Form(None),          
    ck: str = Form(None),           
    cs: str = Form(None),           
    token: str = Form(None),        
    shop_name: str = Form(None),    
    excel_file: UploadFile = File(...)
):
    task_id = str(uuid.uuid4())
    
    # šaljemo workeru, on će to proslijediti Factory-ju
    credentials = {
        "url": url,
        "ck": ck,
        "cs": cs,
        "token": token,
        "shop_name": shop_name
    }

    # Sačuvaj fajl
    input_folder = os.path.join(settings.DATA_DIR, "inputMapping")
    os.makedirs(input_folder, exist_ok=True) # Sigurnost na prvom mjestu
    
    input_file_path = os.path.join(input_folder, f"input_{task_id}.xlsx")
    
    try:
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(excel_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri čuvanju fajla: {str(e)}")

    # Pozovi worker 
    run_attribute_option.delay(task_id, provider, credentials, input_file_path, token, shop_name)

    return {
        "message": "Proces mapiranja je započet",
        "task_id": task_id,
        "provider": provider,
        "check_status_url": f"/api/common/status/{task_id}"
    }