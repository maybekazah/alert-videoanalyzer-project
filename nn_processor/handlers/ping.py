from configs.logger import setup_logging
setup_logging()
import logging

from fastapi import APIRouter

import os

CONTAINER_ID = os.getenv('CONTAINER_ID')

ping_router = APIRouter(prefix="/ping", tags=["ping"])


@ping_router.get("/ping-nn-processor")
async def health_check():
    return {f"ping-nn-processor CONTAINER_ID: {CONTAINER_ID} , status": "healthy"}
