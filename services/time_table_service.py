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

    async def create_mentor_time(self,
                                 day: int,
                                 time_start: Time,
                                 time_end: Time,
                                 mentor_id: UUID) -> UUID:
        """
        Создаёт новый промежуток свободного времени
        """
        mentor_time_id = await self.mentor_time_repository.create_mentor_time(
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

    async def count_requests_for_time(self, request_time: DateTime) -> int:
        """
        Возвращает количество запросов на определённое время.
        """
        mentor_requests = await self.request_repository.get_all_requests_by_time(time=request_time)

        call_count = 0
        for request in mentor_requests:
            if request.response == 0:
                call_count += 1

        return call_count

    async def check_time_reservation(self, time: DateTime) -> bool:
        """
        Проверка занятости времени. True -- занято, False -- не занято.
        """
        return await self.request_repository.check_time_reservation(time)