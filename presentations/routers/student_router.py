from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from services.student_service import StudentService

student_service = StudentService()

student_router = APIRouter(
    prefix="/student",
    tags=["Student"],
    responses={404: {"description": "Not Found"}},
)