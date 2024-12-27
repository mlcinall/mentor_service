from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.student_service import StudentService

student_service = StudentService()

student_router = APIRouter(
    prefix="/student",
    tags=["Student"],
    responses={404: {"description": "Not Found"}},
)


class MentorDto(BaseModel):
    id: UUID
    telegram_id: str
    name: str
    info: str


class RequestDto(BaseModel):
    id: UUID
    call_type: bool
    time_sended: datetime
    mentor_id: UUID
    guest_id: UUID
    description: str
    call_time: Optional[datetime]
    response: int


class RequestGetAllResponse(BaseModel):
    requests: List[RequestDto]


class SendMessageRequestPostRequest(BaseModel):
    mentor_id: UUID
    guest_id: UUID
    description: str


class SendMessageRequestGetResponse(BaseModel):
    id: UUID


class SendCallRequestPostRequest(BaseModel):
    mentor_id: UUID
    guest_id: UUID
    description: str
    call_time: datetime


class SendCallRequestGetResponse(BaseModel):
    id: UUID


class GetRequestByIdGetResponse(BaseModel):
    call_type: bool
    time_sended: datetime
    mentor_id: UUID
    guest_id: UUID
    description: str
    call_time: Optional[datetime]
    response: int


@student_router.get("/", response_model=RequestGetAllResponse)
async def get_all():
    """
    Get all requests.

    Returns all requests' information.
    """
    try:
        requests = await student_service.get_all_requests()

        return RequestGetAllResponse(
            requests=[RequestDto(id=request.id,
                                 call_type=request.call_type,
                                 time_sended=request.time_sended,
                                 mentor_id=request.mentor_id,
                                 guest_id=request.guest_id,
                                 description=request.description,
                                 call_time=request.call_time,
                                 response=request.response,)
                     for request in requests]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@student_router.post("/message/", response_model=SendMessageRequestGetResponse, status_code=201)
async def create_message(request_request: SendMessageRequestPostRequest):
    """
    Create a new message request.

    - **mentor_id**: Unique identifier of the mentor.
    - **guest_id**: Unique identifier of the student.
    - **description**: Description of the request.

    Returns the created request.
    """
    try:
        request_id = await student_service.send_message_request(
            request_request.mentor_id, request_request.guest_id, request_request.description)
        return SendMessageRequestGetResponse(
            id=request_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@student_router.post("/call/", response_model=SendCallRequestGetResponse, status_code=201)
async def create_call(request_request: SendCallRequestPostRequest):
    """
    Create a new call request.

    - **mentor_id**: Unique identifier of the mentor.
    - **guest_id**: Unique identifier of the student.
    - **description**: Description of the request.
    - **call_time**: time of the call.

    Returns the created request.
    """
    try:
        request_id = await student_service.send_call_request(
            request_request.mentor_id, request_request.guest_id,
            request_request.description, call_time=request_request.call_time)
        return SendCallRequestGetResponse(
            id=request_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@student_router.get("/{request_id}", response_model=GetRequestByIdGetResponse)
async def get_by_id(request_id: UUID):
    """
    Get details of a request by ID.

    - **request_id**: Unique identifier of the request.

    Returns all request information.
    """
    try:
        request = await student_service.get_request_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Запрос не найден")

        return GetRequestByIdGetResponse(
            call_type=request.call_type,
            time_sended=request.time_sended,
            mentor_id=request.mentor_id,
            guest_id=request.guest_id,
            description=request.description,
            call_time=request.call_time,
            response=request.response,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
