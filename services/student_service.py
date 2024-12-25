from datetime import datetime
from typing import List, Optional
from loguru import logger
from sqlalchemy import UUID

from persistent.db.mentor import Mentor
from persistent.db.request import Request
from repository.mentors_repository import MentorRepository
from repository.request_repository import RequestRepository

from utils.utils_checkers import time_checker

class StudentService:
    # TODO: из внешней вебапы проверить на существование юзеров
    def __init__(self) -> None:
        self.mentor_repository = MentorRepository()
        self.request_repository = RequestRepository()

    async def send_message_request(
            self,
            mentor_id: UUID,
            guest_id: UUID,
            description: str) -> Optional[UUID]:
        """
        Отправляет запрос на переписку
        """
        if not self.mentor_repository.get_mentor_by_id(mentor_id):
            logger.info(f"Ментора с id {mentor_id} не существует")
            return

        request_id = await self.request_repository.create_request(
            call_type=1, mentor_id=mentor_id, guest_id=guest_id, description=description
        )

        logger.info(f"Запрос на перпеписку №{request_id} отправлен")
        return request_id

    async def send_call_request(
            self,
            mentor_id: UUID,
            guest_id: UUID,
            description: str,
            call_time: datetime) -> Optional[UUID]:
        """
        Отправляет запрос на звонок
        """
        if not self.mentor_repository.get_mentor_by_id(mentor_id):
            logger.info(f"Ментора с id {mentor_id} не существует")
            return
        time_list = await self.request_repository.get_all_requests_by_mentor_id(mentor_id=mentor_id)

        if not time_list:
            logger.warning("У данного ментора нет свободного времени")
            return

        for mentor_time in time_list:
            if time_checker(day=mentor_time.day, time_start=mentor_time.time_start,
                            time_end=mentor_time.time_end, call_datetime=call_time):
                break
        else:
            logger.warning("Данное время у ментора занято")
            return

        if self.request_repository.check_time_reservation(call_time):
            logger.warning("Данное время у ментора забронировано")
            return

        request_id = await self.request_repository.create_request(
            call_type=0, mentor_id=mentor_id, guest_id=guest_id,
            description=description, call_time=call_time
        )

        logger.info(f"Запрос на созвон в {call_time.strftime('%H:%M %d/%m/%Y')} отправлен")
        return request_id
