from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from services.time_table_service import MentorTimeService

time_table_service = MentorTimeService()

time_table_router = APIRouter(
    prefix="/time_table",
    tags=["TimeTable"],
    responses={404: {"description": "Not Found"}},
)