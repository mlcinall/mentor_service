from datetime import datetime, timedelta
from typing import List, Optional
from loguru import logger
from sqlalchemy import UUID

from persistent.db.mentor import Mentor
from persistent.db.request import Request
from persistent.db.mentor_time import MentorTime
from repository.mentors_repository import MentorRepository
from repository.request_repository import RequestRepository
from repository.mentor_time_repository import MentorTimeRepository
from datetime import time as Time
from datetime import datetime as DateTime
from utils.utils_checkers import time_checker

class MentorTimeService:
    def __init__(self) -> None:
        self.mentor_time_repository = MentorTimeRepository()
        self.request_repository = RequestRepository()
        self.mentor_repository = MentorRepository()

    async def create_mentor_time(self,
                                 day: int,
                                 time_start: Time,
                                 time_end: Time,
                                 mentor_id: UUID) -> Optional[UUID]:
        """
        Создаёт новый промежуток свободного времени.

        ``day`` должен быть в диапазоне от 0 до 6, где 0 -- понедельник.
        """
        if not (0 <= day <= 6):
            logger.warning("Неверно указан день")
            return

        if not await self.mentor_repository.get_mentor_by_id(mentor_id):
            logger.info(f"Ментора с id {mentor_id} не существует")
            return

        mentor_time_list = await self.mentor_time_repository.get_all_mentor_time_by_mentor_id(mentor_id)

        flag_uuid = None

        for mentor_time in mentor_time_list:
            if mentor_time.day == day:
                if time_checker(day=day, time_start=time_start,
                                time_end=time_end, call_time=mentor_time.time_start):

                    await self.mentor_time_repository.update_mentor_time(
                        mentor_time_id=mentor_time.id,time_start=time_start, time_end=mentor_time.time_end)
                    flag_uuid = mentor_time.id

                if time_checker(day=day, time_start=time_start, time_end=time_end, call_time=mentor_time.time_end):
                    await self.mentor_time_repository.update_mentor_time(
                        mentor_time_id=mentor_time.id, time_start=mentor_time.time_start, time_end=time_end)
                    flag_uuid = mentor_time.id

        if flag_uuid:
            return flag_uuid

        mentor_time_id = await self.mentor_time_repository.create_new_mentor_time(
            day=day, time_start=time_start, time_end=time_end, mentor_id=mentor_id
        )

        logger.info(f"Успешно добавлен промежуток свободного времени с"
                    f" {time_start.strftime('%H:%M')} по {time_end.strftime('%H:%M')}")
        return mentor_time_id

    async def get_all_mentor_time(self) -> List[MentorTime]:
        """
        Возвращает всё свободное время.
        """
        mentor_time = await self.mentor_time_repository.get_all_mentor_time()
        if not mentor_time:
            logger.warning("Свободного времени не найдено")
        return mentor_time

    async def get_all_mentor_time_by_mentor_id(self, mentor_id: UUID) -> Optional[List[MentorTime]]:
        """
        Возвращает всё свободное время у конкретного ментора
        """
        mentor_time_list = await self.mentor_time_repository.get_all_mentor_time_by_mentor_id(mentor_id)
        if not mentor_time_list:
            logger.warning(f"У ментора нет свободного времени")
            return
        return mentor_time_list

    async def get_call_times(self, day: int, mentor_id: UUID) -> List[Time]:
        """
        Возвращает список возможного времени для звонка.
        """
        mentor_time_list = await self.mentor_time_repository.get_all_mentor_time_by_mentor_id(mentor_id)
        day_time_gap_list = []
        for mentor_time in mentor_time_list:
            if day == mentor_time.day:
                day_time_gap_list.append((mentor_time.time_start, mentor_time.time_end))

        times_list = []

        for time_start, time_end in day_time_gap_list:
            start_datetime = datetime.combine(datetime.today(), time_start)
            end_datetime = datetime.combine(datetime.today(), time_end)

            start_minutes = (start_datetime.minute // 30) * 30
            if start_minutes < start_datetime.minute:
                start_minutes += 30
            start_datetime = start_datetime.replace(minute=start_minutes, second=0, microsecond=0)

            end_minutes = (end_datetime.minute // 30) * 30
            if end_minutes > end_datetime.minute:
                end_minutes -= 30
            end_datetime = end_datetime.replace(minute=end_minutes, second=0, microsecond=0)

            current_time = start_datetime
            while current_time <= end_datetime:
                times_list.append(current_time.time())
                current_time += timedelta(minutes=30)

        return times_list

    async def count_requests_for_time(self, mentor_id: UUID, request_time: DateTime) -> int:
        """
        Возвращает количество запросов на определённое время.
        """
        mentor_requests = await self.request_repository.get_all_requests_by_time(time=request_time, mentor_id=mentor_id)

        call_count = 0
        for request in mentor_requests:
            if request.response == 0:
                call_count += 1

        return call_count

    async def check_time_reservation(self, mentor_id: UUID, time: DateTime) -> bool:
        """
        Проверка занятости времени. True -- занято, False -- не занято.
        Занятым считается время с запросами в статусе ``0`` (ожидает ответа)
        или ``1`` (принят). Отменённые запросы (статус ``2``) свободны.
        """
        return await self.request_repository.check_time_reservation(time=time, mentor_id=mentor_id)
