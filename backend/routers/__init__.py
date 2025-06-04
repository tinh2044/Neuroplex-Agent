"""
This file is responsible for importing all the routers and for including them in the main router.
"""
from fastapi import APIRouter
from backend.routers.chat import chat
from backend.routers.data import data
from backend.routers.base import base
from backend.routers.tool import tool
from backend.routers.admin import admin

router = APIRouter()
router.include_router(base, tags=["Base"])
router.include_router(chat, prefix="/chat", tags=["Chat"])
router.include_router(data, prefix="/data", tags=["Data"])
router.include_router(tool, tags=["Tools"])
router.include_router(admin, tags=["Admin"])
