from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Optional
from loguru import logger
from sqlalchemy import UUID
import httpx

from persistent.db.mentor import Mentor
from persistent.db.request import Request
from persistent.db.mentor_time import MentorTime
from repository.mentors_repository import MentorRepository
from repository.request_repository import RequestRepository
from services.mentor_time_service import MentorTimeService


class MentorService:
    def __init__(self) -> None:
        self.mentor_repository = MentorRepository()
        self.request_repository = RequestRepository()
        self.mentor_time_service = MentorTimeService()

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
        """
        Возвращает количество неотвеченных запросов.

        Возвращает словарь с ключами `call_requests` и `message_requests`.
        """
        mentor_requests = await self.request_repository.get_all_requests_by_mentor_id(mentor_id)

        call_requests = 0
        message_requests = 0
        for request in mentor_requests:
            if request.response == 0:
                if request.call_type == 0:
                    call_requests += 1
                else:
                    message_requests += 1

        return {
            "call_requests": call_requests,
            "message_requests": message_requests,
        }

    async def get_requests(self, mentor_id: UUID) -> List[Request]:
        """
        Возвращает список неотвеченных запросов.
        """
        mentor_requests = await self.request_repository.get_all_requests_by_mentor_id(mentor_id)
        ignored_requests = []
        for request in mentor_requests:
            if request.response == 0:
                ignored_requests.append(request)

        return ignored_requests

    async def response_to_request(self, mentor_id: UUID, request_id: UUID, response: int) -> None:
        """
        Отмечает статус запроса. 1 -- принят, -1 -- отклонён
        Если отклонено — слот времени освобождается (разбивается или удаляется).
        """
        if not await self.mentor_repository.get_mentor_by_id(mentor_id):
            logger.info(f"Ментора с id {mentor_id} не существует")
            return
        request = await self.request_repository.get_request_by_id(request_id)
        if not request:
            logger.info(f"Запроса №{request_id} не существует")
            return
        await self.request_repository.mentor_response(request_id=request_id, response=response)
        if response == 1:
            logger.info(f"Запрос №{request_id} принят")
            # Корректно очищаем слот времени, если заявка подтверждена
            if request.call_time and request.mentor_id:
                mentor_times = await self.mentor_time_service.get_all_mentor_time_by_mentor_id(request.mentor_id)
                req_start = request.call_time.time()
                req_end = (request.call_time + timedelta(minutes=30)).time()
                for mt in mentor_times:
                    if mt.time_start <= req_start and req_end <= mt.time_end and mt.day == request.call_time.isoweekday():
                        # Если заявка занимает весь слот — просто удалить
                        if mt.time_start == req_start and mt.time_end == req_end:
                            await self.mentor_time_service.mentor_time_repository.delete_mentor_time(mt.id)
                            logger.info(f"Слот времени {mt.id} полностью удалён после подтверждения заявки {request_id}")
                        else:
                            # Разбиваем слот на два, если заявка занимает середину
                            old_start = mt.time_start
                            old_end = mt.time_end
                            await self.mentor_time_service.mentor_time_repository.delete_mentor_time(mt.id)
                            if old_start < req_start:
                                await self.mentor_time_service.mentor_time_repository.create_new_mentor_time(
                                    mt.day, old_start, req_start, mt.mentor_id)
                            if req_end < old_end:
                                await self.mentor_time_service.mentor_time_repository.create_new_mentor_time(
                                    mt.day, req_end, old_end, mt.mentor_id)
                            logger.info(f"Слот времени {mt.id} разбит после подтверждения заявки {request_id}")
                        break
        else:
            logger.info(f"Запрос №{request_id} отклонён")

    async def cancel_request(self, mentor_id: UUID, request_id: UUID) -> None:
        """Отменить ранее подтверждённый запрос и вернуть слот времени."""
        if not await self.mentor_repository.get_mentor_by_id(mentor_id):
            logger.info(f"Ментора с id {mentor_id} не существует")
            return
        request = await self.request_repository.get_request_by_id(request_id)
        if not request:
            logger.info(f"Запроса №{request_id} не существует")
            return
        if request.response != 1:
            logger.info(f"Запрос №{request_id} не находится в подтверждённом состоянии")
            return
        await self.request_repository.mentor_response(request_id=request_id, response=2)
        if request.call_time and request.mentor_id:
            await self.mentor_time_service.create_mentor_time(
                request.call_time.isoweekday(),
                request.call_time.time(),
                (request.call_time + timedelta(minutes=30)).time(),
                request.mentor_id,
            )
        logger.info(f"Запрос №{request_id} отменён и слот освобождён")

    async def update_mentor_info(self, mentor_id: UUID, info: str) -> None:
        """
        Обновляет markdown-информацию о себе у ментора.
        """
        await self.mentor_repository.update_mentor_info(mentor_id, info)
        logger.info(f"Ментор {mentor_id} обновил информацию о себе.")

    async def sync_mentor_from_external(self, mentor_id: UUID, external_user_id: str) -> None:
        url = f"http://85.198.82.236/auth/api/get_user/{external_user_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        about = data.get("about")
        specification = data.get("specification")
        name = data.get("name")
        telegram = data.get("telegram")
        await self.mentor_repository.update_mentor_external_fields(mentor_id, about, specification, name, telegram)
        logger.info(f"Mentor {mentor_id} synced from external profile {external_user_id}")

    async def find_mentors_by_name(self, name: str) -> List[Mentor]:
        """Поиск менторов по имени (частичное совпадение, регистронезависимо)."""
        mentors = await self.mentor_repository.get_mentors_by_name(name)
        if not mentors:
            logger.warning(f"Менторы с именем {name} не найдены")
        return mentors

    async def find_mentors_by_specification(self, specification: str) -> List[Mentor]:
        """Поиск менторов по роли (specification, частичное совпадение, регистронезависимо)."""
        mentors = await self.mentor_repository.get_mentors_by_specification(specification)
        if not mentors:
            logger.warning(f"Менторы со специализацией {specification} не найдены")
        return mentors
