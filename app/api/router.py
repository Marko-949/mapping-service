from fastapi import APIRouter
from app.api.controllers import attribute_option, common, mapping_categories, context

api_router = APIRouter()
api_router.include_router(context.router, prefix="/context", tags=["Context"])
api_router.include_router(mapping_categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(attribute_option.router, prefix="/attribute-options", tags=["attribute-options"])
api_router.include_router(common.router, prefix="/common", tags=["Common"])