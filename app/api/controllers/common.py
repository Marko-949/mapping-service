from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from celery.result import AsyncResult
import os
from app.core.config import settings

router = APIRouter()


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "info": task_result.info if task_result.ready() else "Radimo na tome..."
    }

@router.get("/download/{task_id}")
async def download_result(task_id: str):
    file_path = os.path.join(settings.DATA_DIR, f"final_mapping_{task_id}.xlsx")
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=f"mapiranje_rezultat_{task_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    raise HTTPException(status_code=404, detail="Fajl nije spreman ili ne postoji.")