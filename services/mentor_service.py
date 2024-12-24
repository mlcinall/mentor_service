from datetime import datetime
from collections import defaultdict
from typing import List, Optional
from loguru import logger
from sqlalchemy import UUID

from persistent.db.mentor import Mentor
from persistent.db.mentor_time import MentorTime
from repository.mentors_repository import MentorRepository
from repository.request_repository import RequestRepository


class MentorService:
    def __init__(self) -> None:
        self.mentor_repository = MentorRepository()
        self.request_repository = RequestRepository()

    async def get_all_mentors(self) -> List[Mentor]:
        """
        Возвращает всех менторов.
        """
        mentors = await self.mentor_repository.get_all_mentors()
        if not mentors:
            logger.warning("Менторы не найдены")
        return mentors

    async def create_mentor(
        self,
            tg_id: str,
            name: str,
            info: str) -> UUID:
        """
        Создаёт нового ментора.
        """
        #TODO: Подвязать сюда регу ментора из внешней вебапы

        mentor_id = await self.mentor_repository.create_mentor(
            tg_id=tg_id, name=name, info=info
        )

        logger.info(f"Товарищ {name} успешно посвящён в менторы.")
        return mentor_id

    async def get_mentor_by_id(self, mentor_id: UUID) -> Optional[Mentor]:
        """
        Возвращает ментора по его ID.
        """
        mentor = await self.mentor_repository.get_mentor_by_id(mentor_id)
        if not mentor:
            logger.warning(f"Товарища ментора с ID {mentor_id} не удалось найти.")
        return mentor

    async def get_mentor_by_tg_id(self, tg_id: str) -> Optional[Mentor]:
        """
        Возвращает ментора по его tg.
        """
        mentor = await self.mentor_repository.get_mentor_by_tg_id(tg_id)
        if not mentor:
            logger.warning(f"Товарища ментора с телегой {tg_id} не удалось найти.")
        return mentor

    async def count_requests(self, mentor_id: UUID) -> dict:
        mentor_requests = await self.request_repository.get_all_requests_by_mentor_id(mentor_id)

        catt_type_count = defaultdict(int)
        for request in mentor_requests:
            catt_type_count[request.call_type] += 1

        return dict(catt_type_count)