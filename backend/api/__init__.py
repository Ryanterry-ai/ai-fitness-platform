"""
API Routes Module
"""
from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def api_root():
    return {"message": "Website Cloner API", "version": "1.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}
