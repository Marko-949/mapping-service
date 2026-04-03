from fastapi import APIRouter, HTTPException
from app.core.context_manager import context_manager

router = APIRouter()

@router.post("/update-provider-shop")
async def update_context(provider: str, shop_name: str, url: str, ck: str, cs: str):
    creds = {"url": url, "ck": ck, "cs": cs}
    context_manager.add_shop(provider, shop_name, creds)
    return {"message": f"Shop {shop_name} dodat u listu providera {provider}"}

@router.post("/set-active-context")
async def set_active(provider: str, shop_name: str):
    success = context_manager.set_active(provider, shop_name)
    if not success:
        raise HTTPException(status_code=404, detail="Shop ili Provider ne postoji u bazi.")
    return {"message": "Aktivni kontekst postavljen", "active": context_manager.get_active()}

@router.delete("/clear-active-context")
async def clear_active():
    context_manager.clear_active()
    return {"message": "Aktivni kontekst obrisan"}

@router.get("/get-current-context")
async def get_current():
    return context_manager.data # Vraća sve provajdere i ko je aktivan