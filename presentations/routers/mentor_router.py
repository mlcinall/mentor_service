from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.mentor_service import MentorService

mentor_service = MentorService()

mentor_router = APIRouter(
    prefix="/mentor",
    tags=["Mentor"],
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

class MentorGetAllResponse(BaseModel):
    mentors: List[MentorDto]


class MentorCreatePostRequest(BaseModel):
    telegram_id: str
    name: str
    info: str


class CreateMentorPostResponse(BaseModel):
    id: UUID


class GetMentorByIdGetResponse(BaseModel):
    telegram_id: str
    name: str
    info: str


class GetMentorByTelegramIdGetResponse(BaseModel):
    telegram_id: str
    name: str
    info: str


class CountMentorRequestByIdGetResponse(BaseModel):
    call_requests: int
    message_requests: int


class GetMentorRequestsByIdGetResponse(BaseModel):
    requests: List[RequestDto]


@mentor_router.get("/", response_model=MentorGetAllResponse)
async def get_all():
    """
    Get all mentors.

    Returns all mentors' information.
    """
    try:
        mentors = await mentor_service.get_all_mentors()

        return MentorGetAllResponse(
            mentors=[MentorDto(id=mentor.id,
                               telegram_id=mentor.telegram_id,
                               name=mentor.name,
                               info=mentor.info)
                     for mentor in mentors]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.post("/", response_model=CreateMentorPostResponse, status_code=201)
async def create(mentor_request: MentorCreatePostRequest):
    """
    Create a new mentor.

    - **telegram_id**: tg id of the mentor. Example: @Chuvirla1453.
    - **name**: Name of the mentor.
    - **info**: Information of the mentor. Roles, bio, work experience, etc.

    Returns the created mentor.
    """
    try:
        mentor_id = await mentor_service.create_mentor(
            mentor_request.telegram_id, mentor_request.name, mentor_request.info)
        return CreateMentorPostResponse(
            id=mentor_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Ментор с таким telegram_id уже есть")


@mentor_router.get("/{mentor_id}", response_model=GetMentorByIdGetResponse)
async def get_by_id(mentor_id: UUID):
    """
    Get details of a mentor by their ID.

    - **mentor_id**: Unique identifier of the mentor.

    Returns all mentor information.
    """
    try:
        mentor = await mentor_service.get_mentor_by_id(mentor_id)
        if not mentor:
            raise HTTPException(status_code=404, detail="Ментор не найден")

        return GetMentorByIdGetResponse(
            telegram_id=mentor.telegram_id,
            name=mentor.name,
            info=mentor.info,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/{telegram_id}", response_model=GetMentorByTelegramIdGetResponse)
async def get_by_tg_id(telegram_id: str):
    """
    Get details of a mentor by their telegram ID.

    - **telegram_id**: tg id of the mentor. Example: @Chuvirla1453.

    Returns all mentor information.
    """
    try:
        mentor = await mentor_service.get_mentor_by_tg_id(telegram_id)
        if not mentor:
            raise HTTPException(status_code=404, detail="Ментор не найден")

        return GetMentorByTelegramIdGetResponse(
            telegram_id=mentor.telegram_id,
            name=mentor.name,
            info=mentor.info,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/count/{mentor_id}", response_model=CountMentorRequestByIdGetResponse)
async def count_by_id(mentor_id: UUID):
    """
    Count unanswered requests of a mentor by their ID.

    - **mentor_id**: Unique identifier of the mentor.

    Returns number of unanswered requests by their types.
    """
    try:
        mentor_requests_cnt = await mentor_service.count_requests(mentor_id)
        if not mentor_requests_cnt:
            raise HTTPException(status_code=404, detail="Хз что не так, если честно")

        return CountMentorRequestByIdGetResponse(
            call_requests=mentor_requests_cnt[0],
            message_requests=mentor_requests_cnt[1],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/get_requests/{mentor_id}", response_model=GetMentorRequestsByIdGetResponse)
async def get_all_requests_by_id(mentor_id: UUID):
    """
    Get all requests of a mentor by their ID.

    - **mentor_id**: Unique identifier of the mentor.

    Returns all mentors' requests information.
    """
    try:
        requests = await mentor_service.get_requests(mentor_id)

        return GetMentorRequestsByIdGetResponse(
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