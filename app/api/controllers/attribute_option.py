from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
import os
import shutil
from app.core.config import settings
from app.services.worker import run_attribute_option, fetch_attribute_options_task
from app.core.context_manager import context_manager

router = APIRouter()

@router.post("/fetch-attribute-options-async")
async def fetch_attribute_options_async():
    active = context_manager.get_active()
    if not active:
        raise HTTPException(status_code=400, detail="Nema aktivnog konteksta. Postavite aktivni kontekst prije pokretanja ovog endpointa.")

    provider = active["provider"]
    shop_name = active["shop_name"]
    credentials = active["credentials"]

    provider_folder = provider.lower()

    task = fetch_attribute_options_task.delay(provider_folder, credentials, shop_name)

    return {
        "task_id": task.id,
        "status": "Processing in background",
        "message": "Podaci se preuzimaju. Provjerite status kasnije."
    }

@router.post("/attribute_option_mapping")
async def attribute_option_mapping(
    token: str = Form(..., example="your_api_token_here")
):
    active = context_manager.get_active()
    if not active:
        raise HTTPException(status_code=400, detail="Nema aktivnog konteksta. Postavite aktivni kontekst prije pokretanja ovog endpointa.")

    provider = active["provider"]
    shop_name = active["shop_name"]
    task_id = str(uuid.uuid4())
    provider_folder = provider.lower()

    json_cache_path = (
        settings.DATA_DIR / 
        "cachedAttributesOptions" / 
        provider_folder / 
        f"{shop_name}_attributes_options.json"
    )

    input_excel_path = (
        settings.DATA_DIR / 
        "mapped_categories" / 
        provider_folder /   
        f"{shop_name}_category_mapping.xlsx"
    )

    if not json_cache_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"JSON keš nije pronađen: {json_cache_path.name}. Prvo pokrenite fetch atributa."
        )

    if not input_excel_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Excel plan kategorija nije pronađen: {input_excel_path.name}. "
                   f"Prvo završite mapiranje kategorija."
        )

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
        "active_shop": f"{shop_name} ({provider})",
        "files_used": {
            "excel_plan": input_excel_path.name,
            "json_cache": json_cache_path.name
        },
        "message": "AI model koristi prethodno izmapirane kategorije za mapiranje atributa."
    }


