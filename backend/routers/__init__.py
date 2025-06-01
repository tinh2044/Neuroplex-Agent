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
router.include_router(base)
router.include_router(chat)
router.include_router(data)
router.include_router(tool)
router.include_router(admin)
