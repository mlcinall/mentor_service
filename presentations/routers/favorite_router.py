from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger

from services.favorite_service import FavoriteMentorService
from utils.jwt_utils import extract_user_id

favorite_service = FavoriteMentorService()

favorite_router = APIRouter(
    prefix="/favorite",
    tags=["Favorite"],
    responses={404: {"description": "Not Found"}},
)


class FavoriteDto(BaseModel):
    id: UUID
    user_id: UUID
    mentor_id: UUID


class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteDto]


class AddFavoriteResponse(BaseModel):
    id: UUID


@favorite_router.post("/{mentor_id}", response_model=AddFavoriteResponse, status_code=201)
async def add_favorite(mentor_id: UUID, user_id: UUID = Depends(extract_user_id)):
    try:
        logger.info(f"User {user_id} adds mentor {mentor_id} to favorites")
        fav_id = await favorite_service.add_favorite(user_id, mentor_id)
        if not fav_id:
            raise HTTPException(status_code=404, detail="Mentor not found")
        return AddFavoriteResponse(id=fav_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@favorite_router.delete("/{mentor_id}")
async def remove_favorite(mentor_id: UUID, user_id: UUID = Depends(extract_user_id)):
    try:
        logger.info(f"User {user_id} removes mentor {mentor_id} from favorites")
        await favorite_service.remove_favorite(user_id, mentor_id)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error removing favorite: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@favorite_router.get("/", response_model=FavoriteListResponse)
async def get_favorites(user_id: UUID = Depends(extract_user_id)):
    try:
        logger.info(f"User {user_id} gets favorite mentors")
        favorites = await favorite_service.get_favorites(user_id)
        return FavoriteListResponse(
            favorites=[FavoriteDto(id=fav.id, user_id=fav.user_id, mentor_id=fav.mentor_id) for fav in favorites]
        )
    except Exception as e:
        logger.error(f"Error fetching favorites: {e}")
        raise HTTPException(status_code=400, detail=str(e))
