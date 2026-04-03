from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
import os
import shutil
from app.core.config import settings
from app.services.worker import run_attribute_option, fetch_attribute_options_task

router = APIRouter()

@router.post("/attribute_option_mapping")
async def attribute_option_mapping(
    provider: str = Form(..., example="woocommerce"),                
    shop_name: str = Form(..., example="omegashop"),    
    excel_file: UploadFile = File(...),
    token: str = Form(..., example="your_api_token_here")
):
    task_id = str(uuid.uuid4())
    provider_folder = provider.lower()

    json_cache_path = (
        settings.DATA_DIR / 
        "cachedAttributesOptions" / 
        provider_folder / 
        f"{shop_name}_attributes_options.json"
    )

    if not json_cache_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Fajl {shop_name}_cache.json nije pronađen u folderu {provider_folder}. "
                   f"Prvo pokrenite fetch endpoint."
        )

    input_excel_dir = settings.DATA_DIR / "inputMapping" / "excel_plans"
    input_excel_dir.mkdir(parents=True, exist_ok=True)
    input_excel_path = input_excel_dir / f"plan_{task_id}.xlsx"

    with open(input_excel_path, "wb") as buffer:
        shutil.copyfileobj(excel_file.file, buffer)

    run_attribute_option.delay(
        task_id=task_id, 
        provider=provider_folder, 
        json_data_path=str(json_cache_path), 
        input_excel_path=str(input_excel_path), 
        shop_name=shop_name,
        token=token
    )

    return {
        "status": "started",
        "task_id": task_id,
        "using_cache_file": f"{provider_folder}/{shop_name}_cache.json",
        "message": "AI model sada čita podatke direktno iz cache foldera."
    }

@router.post("/fetch-attribute-options-async")
async def fetch_attribute_options_async(
    provider_type: str, 
    shop_name: str, 
    url: str, ck: str, cs: str
):
    credentials = {"url": url, "ck": ck, "cs": cs}
    
    task = fetch_attribute_options_task.delay(provider_type, credentials, shop_name)
    
    return {
        "task_id": task.id,
        "status": "Processing in background",
        "message": "Podaci se preuzimaju. Provjerite status kasnije."
    }
