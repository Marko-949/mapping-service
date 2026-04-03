from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings

def get_application() -> FastAPI:
    application = FastAPI(
        title="E-commerce Mapping Service",
        description="API za mapiranje atributa između različitih platformi koristeći Gemini",
        version="1.0.0",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api")

    return application

app = get_application()

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Mapping Service is running"}