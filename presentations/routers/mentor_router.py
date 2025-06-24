from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from loguru import logger

from services.mentor_service import MentorService
from utils.jwt_utils import extract_user_id

mentor_service = MentorService()

mentor_router = APIRouter(
    prefix="/mentor_service",
    tags=["Mentor"],
    responses={404: {"description": "Not Found"}},
)


class MentorDto(BaseModel):
    id: UUID
    telegram_id: str
    name: str
    info: str
    specification: Optional[str] = None


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
    specification: Optional[str] = None


class CreateMentorPostResponse(BaseModel):
    id: UUID


class GetMentorByIdGetResponse(BaseModel):
    telegram_id: str
    name: str
    info: str
    specification: Optional[str] = None


class GetMentorByTelegramIdGetResponse(BaseModel):
    telegram_id: str
    name: str
    info: str
    specification: Optional[str] = None


class CountMentorRequestByIdGetResponse(BaseModel):
    call_requests: int
    message_requests: int


class GetMentorRequestsByIdGetResponse(BaseModel):
    requests: List[RequestDto]


class UpdateMentorInfoRequest(BaseModel):
    info: str


class SyncMentorExternalRequest(BaseModel):
    external_user_id: str


class MentorRespondRequest(BaseModel):
    response: int  # 1 — принять, -1 — отклонить


@mentor_router.get("/", response_model=MentorGetAllResponse)
async def get_all(user_id: UUID = Depends(extract_user_id)):
    """
    Get all mentors.

    Authorization header required with Bearer token containing user_id.

    Returns all mentors' information.
    """
    try:
        logger.info(f"User {user_id} retrieving all mentors")
        mentors = await mentor_service.get_all_mentors()

        return MentorGetAllResponse(
            mentors=[MentorDto(id=mentor.id,
                               telegram_id=mentor.telegram_id,
                               name=mentor.name,
                               info=mentor.info,
                               specification=mentor.specification)
                     for mentor in mentors]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving all mentors: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.post("/", response_model=CreateMentorPostResponse, status_code=201)
async def create(mentor_request: MentorCreatePostRequest, user_id: UUID = Depends(extract_user_id)):
    """
    Create a new mentor.

    - **telegram_id**: tg id of the mentor. Example: @Chuvirla1453.
    - **name**: Name of the mentor.
    - **info**: Information of the mentor. Roles, bio, work experience, etc.

    Authorization header required with Bearer token containing user_id.

    Returns the created mentor.
    """
    try:
        logger.info(f"User {user_id} creating new mentor with telegram_id {mentor_request.telegram_id}")
        mentor_id = await mentor_service.create_mentor(
            mentor_request.telegram_id, mentor_request.name, mentor_request.info)
        return CreateMentorPostResponse(
            id=mentor_id,
        )
    except Exception as e:
        logger.error(f"Error creating mentor: {e}")
        raise HTTPException(status_code=400, detail="Ментор с таким telegram_id уже есть")


@mentor_router.get("/{mentor_id}", response_model=GetMentorByIdGetResponse)
async def get_by_id(mentor_id: UUID, user_id: UUID = Depends(extract_user_id)):
    """
    Get details of a mentor by their ID.

    - **mentor_id**: Unique identifier of the mentor.

    Authorization header required with Bearer token containing user_id.

    Returns all mentor information.
    """
    try:
        logger.info(f"User {user_id} retrieving mentor with ID {mentor_id}")
        mentor = await mentor_service.get_mentor_by_id(mentor_id)
        if not mentor:
            logger.warning(f"Mentor with ID {mentor_id} not found")
            raise HTTPException(status_code=404, detail="Ментор не найден")

        return GetMentorByIdGetResponse(
            telegram_id=mentor.telegram_id,
            name=mentor.name,
            info=mentor.info,
            specification=mentor.specification
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving mentor by ID: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/by_tg/{telegram_id}", response_model=GetMentorByTelegramIdGetResponse)
async def get_by_tg_id(telegram_id: str, user_id: UUID = Depends(extract_user_id)):
    """
    Get details of a mentor by their telegram ID.

    - **telegram_id**: tg id of the mentor. Example: @Chuvirla1453.

    Authorization header required with Bearer token containing user_id.

    Returns all mentor information.
    """
    try:
        logger.info(f"User {user_id} retrieving mentor with telegram ID {telegram_id}")
        mentor = await mentor_service.get_mentor_by_tg_id(telegram_id)
        if not mentor:
            logger.warning(f"Mentor with telegram ID {telegram_id} not found")
            raise HTTPException(status_code=404, detail="Ментор не найден")

        return GetMentorByTelegramIdGetResponse(
            telegram_id=mentor.telegram_id,
            name=mentor.name,
            info=mentor.info,
            specification=mentor.specification
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving mentor by telegram ID: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/count/{mentor_id}", response_model=CountMentorRequestByIdGetResponse)
async def count_by_id(mentor_id: UUID, user_id: UUID = Depends(extract_user_id)):
    """
    Count unanswered requests of a mentor by their ID.

    - **mentor_id**: Unique identifier of the mentor.

    Authorization header required with Bearer token containing user_id.

    Returns number of unanswered requests by their types.
    """
    try:
        logger.info(f"User {user_id} counting requests for mentor with ID {mentor_id}")
        mentor_requests_cnt = await mentor_service.count_requests(mentor_id)
        if not mentor_requests_cnt:
            logger.warning(f"No requests counted for mentor ID {mentor_id}")
            raise HTTPException(status_code=404, detail="Хз что не так, если честно")

        return CountMentorRequestByIdGetResponse(
            call_requests=mentor_requests_cnt[0],
            message_requests=mentor_requests_cnt[1],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error counting mentor requests: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/get_requests/{mentor_id}", response_model=GetMentorRequestsByIdGetResponse)
async def get_all_requests_by_id(mentor_id: UUID, user_id: UUID = Depends(extract_user_id)):
    """
    Get all requests of a mentor by their ID.

    - **mentor_id**: Unique identifier of the mentor.

    Authorization header required with Bearer token containing user_id.

    Returns all mentors' requests information.
    """
    try:
        logger.info(f"User {user_id} retrieving requests for mentor with ID {mentor_id}")
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
        logger.error(f"Error retrieving mentor requests: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.patch("/{mentor_id}/info")
async def update_mentor_info(mentor_id: UUID, req: UpdateMentorInfoRequest, user_id: UUID = Depends(extract_user_id)):
    """
    Обновить markdown-информацию о себе у ментора.
    Требуется авторизация (JWT).
    """
    try:
        logger.info(f"User {user_id} updating info for mentor {mentor_id}")
        await mentor_service.update_mentor_info(mentor_id, req.info)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error updating mentor info: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.post("/{mentor_id}/sync_external")
async def sync_mentor_external(mentor_id: UUID, req: SyncMentorExternalRequest = Body(...), user_id: UUID = Depends(extract_user_id)):
    """
    Синхронизировать данные ментора с внешним сервисом профилей по external_user_id.
    Требуется авторизация (JWT).
    """
    try:
        logger.info(f"User {user_id} syncing mentor {mentor_id} from external user {req.external_user_id}")
        await mentor_service.sync_mentor_from_external(mentor_id, req.external_user_id)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error syncing mentor from external: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/search/by_name", response_model=MentorGetAllResponse)
async def search_by_name(name: str, user_id: UUID = Depends(extract_user_id)):
    """
    Поиск менторов по имени (частичное совпадение, регистронезависимо).
    """
    try:
        logger.info(f"User {user_id} searching mentors by name: {name}")
        mentors = await mentor_service.find_mentors_by_name(name)
        return MentorGetAllResponse(
            mentors=[MentorDto(id=mentor.id,
                               telegram_id=mentor.telegram_id,
                               name=mentor.name,
                               info=mentor.info,
                               specification=mentor.specification)
                     for mentor in mentors]
        )
    except Exception as e:
        logger.error(f"Error searching mentors by name: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.get("/search/by_role", response_model=MentorGetAllResponse)
async def search_by_role(role: str, user_id: UUID = Depends(extract_user_id)):
    """
    Поиск менторов по роли (specification, частичное совпадение, регистронезависимо).
    """
    try:
        logger.info(f"User {user_id} searching mentors by role: {role}")
        mentors = await mentor_service.find_mentors_by_specification(role)
        return MentorGetAllResponse(
            mentors=[MentorDto(id=mentor.id,
                               telegram_id=mentor.telegram_id,
                               name=mentor.name,
                               info=mentor.info,
                               specification=mentor.specification)
                     for mentor in mentors]
        )
    except Exception as e:
        logger.error(f"Error searching mentors by role: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@mentor_router.patch("/request/{request_id}/respond")
async def respond_to_request(request_id: UUID, req: MentorRespondRequest, user_id: UUID = Depends(extract_user_id)):
    """
    Ментор принимает или отклоняет заявку (request). 1 — принять, -1 — отклонить.
    Если отклонено — ячейка времени освобождается, если принято — бронится.
    Требуется авторизация (JWT).
    """
    try:
        logger.info(f"Mentor {user_id} responds to request {request_id} with response {req.response}")
        await mentor_service.response_to_request(user_id, request_id, req.response)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error responding to request: {e}")
        raise HTTPException(status_code=400, detail=str(e))