from typing import List, Optional
from sqlalchemy import UUID
from loguru import logger

from persistent.db.favorite_mentor import FavoriteMentor
from repository.favorite_mentor_repository import FavoriteMentorRepository
from repository.mentors_repository import MentorRepository


class FavoriteMentorService:
    def __init__(self) -> None:
        self.favorite_repository = FavoriteMentorRepository()
        self.mentor_repository = MentorRepository()

    async def add_favorite(self, user_id: UUID, mentor_id: UUID) -> Optional[UUID]:
        if not await self.mentor_repository.get_mentor_by_id(mentor_id):
            logger.info(f"Mentor with id {mentor_id} does not exist")
            return None
        fav_id = await self.favorite_repository.add_favorite(user_id, mentor_id)
        logger.info(f"User {user_id} added mentor {mentor_id} to favorites")
        return fav_id

    async def remove_favorite(self, user_id: UUID, mentor_id: UUID) -> None:
        if not await self.mentor_repository.get_mentor_by_id(mentor_id):
            logger.info(f"Mentor with id {mentor_id} does not exist")
            return
        await self.favorite_repository.remove_favorite(user_id, mentor_id)
        logger.info(f"User {user_id} removed mentor {mentor_id} from favorites")

    async def get_favorites(self, user_id: UUID) -> List[FavoriteMentor]:
        favorites = await self.favorite_repository.get_favorites(user_id)
        if not favorites:
            logger.warning(f"User {user_id} has no favorite mentors")
        return favorites
