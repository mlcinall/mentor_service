from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from services.mentor_service import MentorService

mentor_service = MentorService()

mentor_router = APIRouter(
    prefix="/mentor",
    tags=["Mentor"],
    responses={404: {"description": "Not Found"}},
)
