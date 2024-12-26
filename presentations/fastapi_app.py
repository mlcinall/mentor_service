from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4
from datetime import time as Time

from fastapi import FastAPI, HTTPException, Path, Response, status
from loguru import logger
from pydantic import BaseModel

from services.mentor_service import MentorService
from services.student_service import StudentService
from services.time_table_service import MentorTimeService

mentor_service = MentorService()
student_service = StudentService()
time_table_service = MentorTimeService()

# Lifespan-событие
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем мента и свободное окно для него
    mentor_id = await mentor_service.create_mentor("@sup", "Super Idol", "super idol forever")
    mtt_id = await time_table_service.create_mentor_time(1, Time.fromisoformat('08:00:00'), Time.fromisoformat('12:00:00'), mentor_id)

    #Проверяем свободные часы
    logger.info(f"Now exist this mentors '{mentor_service.get_all_mentors()}'")
    logger.info(f"Mentors have '{time_table_service.get_all_mentor_time()}' free time")
    logger.info(f"Mentor {mentor_id} have free time on '{time_table_service.get_all_mentor_time_by_mentor_id(mentor_id)}'")
    logger.info(f"Mentor {mentor_id} can call on '{time_table_service.get_call_times(1, mentor_id)}'")

    # Добавляем студентика и создаем запросы
    user_id = uuid4()
    try:
        message_request_id = await student_service.send_message_request(mentor_id, user_id, "skibidi toilet")
        logger.info(f"Message request created with ID: {message_request_id}")
    except ValueError as e:
        logger.error(f"Error creating request: {e}")
        message_request_id = None
    try:
        call_request_id = await student_service.send_call_request(mentor_id, user_id, "sigma boy", datetime.strptime("01/01/25 10:00:00", '%d%m%y %H:%M:%S'))
        logger.info(f"Call request created with ID: {call_request_id}")
    except ValueError as e:
        logger.error(f"Error creating request: {e}")
        call_request_id = None
    if call_request_id:
        try:
            number = await time_table_service.count_requests_for_time(datetime.strptime("1/1/25 10:00:00", '%d/%m/%y %H:%M:%S'))
            logger.info(f"Mentor has '{number}' requests on this time '{datetime.strptime('1/1/25 10:00:00', '%d/%m/%y %H:%M:%S')}'")
        except ValueError as e:
            logger.error(f"Error finding any requests: {e}")

    # Проверяем поиск менторов по нику
    try:
        logger.info(f"Here is your mentor: {mentor_service.get_mentor_by_id(mentor_id)}")
    except ValueError as e:
        logger.error(f"Can't find that mentor: {e}")

    try:
        logger.info(f"Here is your mentor: {mentor_service.get_mentor_by_tg_id('@sup')}")
    except ValueError as e:
        logger.error(f"Can't find that mentor: {e}")

    # Одобряем запрос и проводим проверку
    try:
        logger.info(f"Mentor has: {mentor_service.count_requests(mentor_id)} requests")
    except ValueError as e:
        logger.error(f"Can't find that mentor: {e}")

    try:
        logger.info(f"Mentors' requests: {mentor_service.get_requests(mentor_id)}")
    except ValueError as e:
        logger.error(f"Can't find that mentor: {e}")

    try:
        await mentor_service.response_to_request(mentor_id, call_request_id, 1)
    except ValueError as e:
        logger.error(f"Can't find that request: {e}")

    try:
        await mentor_service.response_to_request(mentor_id, message_request_id, 2)
    except ValueError as e:
        logger.error(f"Can't find that request: {e}")

    try:
        stat = await time_table_service.check_time_reservation(datetime.strptime("01/01/25 10:00:00", '%d%m%y %H:%M:%S'))
        if stat:
            logger.info(f"{datetime.strptime('1/1/25 10:00:00', '%d/%m/%y %H:%M:%S')} already occupied")
        else:
            logger.info(f"{datetime.strptime('1/1/25 10:00:00', '%d/%m/%y %H:%M:%S')} free now")
    except ValueError as e:
        logger.error(f"Can't find that date: {e}")

    yield  # Возвращаем управление приложению

    logger.info("Application shutdown: cleaning up...")  # Действия при завершении приложения




app = FastAPI(
    title="BEST_WEBAPP_EVER",
    description="IDAS IS NOT A KINDERGARTEN",
    lifespan=lifespan,
)

class PutLink(BaseModel):
    link: str


def _service_link_to_real(short_link: str) -> str:
    return f"http://localhost:8000/short/{short_link}"