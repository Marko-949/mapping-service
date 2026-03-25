from fastapi import APIRouter
from app.api.controllers import attribute_option, common, mapping_categories

api_router = APIRouter()
api_router.include_router(attribute_option.router, prefix="/mapping", tags=["Mapping"])
api_router.include_router(mapping_categories.router, prefix="/mapping", tags=["Mapping"])
api_router.include_router(common.router, prefix="/common", tags=["Common"])