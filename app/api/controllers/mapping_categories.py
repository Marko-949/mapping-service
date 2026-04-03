from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
import os
import shutil
from app.core.config import settings
from app.services.worker import run_category_mapping_task, fetch_provider_data_task
from app.core.context_manager import context_manager
router = APIRouter()


import json
import os
from fastapi import APIRouter, HTTPException, Query
from app.services.providers.factory import ProviderFactory

router = APIRouter()

@router.post("/fetch-categories-async")
async def fetch_categories_async():
    

    active = context_manager.get_active()
    if not active:
        raise HTTPException(status_code=400, detail="Nema aktivnog konteksta. Postavite aktivni kontekst prije pokretanja ovog endpointa.")

    provider = active["provider"]
    credentials = active["credentials"]    
    shop_name = active["shop_name"]

    task = fetch_provider_data_task.delay(provider, credentials, shop_name)
    
    return {
        "task_id": task.id,
        "status": "Processing in background",
        "message": "Podaci se preuzimaju. Provjerite status kasnije."
    }


@router.post("/categories_mapping")
async def mapping_categories():
    
    active = context_manager.get_active()
    if not active:
        raise HTTPException(status_code=400, detail="Nema aktivnog konteksta. Postavite aktivni kontekst prije pokretanja ovog endpointa.")
    provider = active["provider"]
    shop_name = active["shop_name"]
    task_id = str(uuid.uuid4())

    cache_file_path = (
        settings.DATA_DIR / 
        "cachedCategories" / 
        provider / 
        f"{shop_name}_cache.json"
    )

    if not cache_file_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Keširani podaci za {shop_name} nisu pronađeni. "
                   f"Prvo pokrenite 'Fetch' endpoint za ovaj šop."
        )

    run_category_mapping_task.delay(
        task_id=task_id, 
        input_json_path=str(cache_file_path), 
        shop_name=shop_name, 
        provider=provider
    )

    return {
        "status": "PENDING",
        "task_id": task_id,
        "active_shop": f"{shop_name} ({provider})",
        "using_file": str(cache_file_path.name),
        "message": "Proces AI mapiranja kategorija je pokrenut koristeći keširane podatke.",
        "check_status_url": f"/api/mapping/status/{task_id}"
    }