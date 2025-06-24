from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4
from datetime import time as Time

from fastapi import FastAPI, HTTPException, Path, Response, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from services.mentor_service import MentorService
from services.student_service import StudentService
from services.mentor_time_service import MentorTimeService

from presentations.routers.mentor_router import mentor_router
from presentations.routers.student_router import student_router
from presentations.routers.mentor_time_router import mentor_time_router

from utils.jwt_utils import extract_user_id
from utils.jwt_auth import JWTAuthMiddleware
from settings.settings import settings

# Создаем объект схемы безопасности для Swagger UI
security_scheme = HTTPBearer()

mentor_service = MentorService()
student_service = StudentService()
time_table_service = MentorTimeService()

# Lifespan-событие
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем мента и свободное окно для него
    mentor = await mentor_service.get_mentor_by_tg_id("@sup")
    if not mentor:
        mentor_id = await mentor_service.create_mentor("@sup", "Super Idol", "super idol forever")
        mtt_id = await time_table_service.create_mentor_time(1, Time.fromisoformat('08:00:00'), Time.fromisoformat('12:00:00'), mentor_id)
        mentor_id = mentor_id  # Keep the UUID as is
    else:
        mentor_id = mentor.id  # Use the id from the mentor object
    
    # Проверяем свободные часы
    logger.info(f"Now exist this mentors '{await mentor_service.get_all_mentors()}'")
    logger.info(f"Mentors have '{await time_table_service.get_all_mentor_time()}' free time")
    logger.info(f"Mentor {mentor_id} have free time on '{await time_table_service.get_all_mentor_time_by_mentor_id(mentor_id)}'")
    logger.info(f"Mentor {mentor_id} can call on '{await time_table_service.get_call_times(1, mentor_id)}'")

    # Добавляем студентика и создаем запросы
    user_id = uuid4()
    try:
        message_request_id = await student_service.send_message_request(mentor_id, user_id, "skibidi toilet")
        logger.info(f"Message request created with ID: {message_request_id}")
    except ValueError as e:
        logger.error(f"Error creating request: {e}")
        message_request_id = None
    try:
        call_request_id = await student_service.send_call_request(
            mentor_id, user_id, "sigma boy",
            datetime.strptime("01/01/25 10:00:00", '%d/%m/%y %H:%M:%S'))

        logger.info(f"Call request created with ID: {call_request_id}")
    except ValueError as e:
        logger.error(f"Error creating request: {e}")
        call_request_id = None
    if call_request_id:
        try:
            number = await time_table_service.count_requests_for_time(
                request_time=datetime.strptime("1/1/25 10:00:00", '%d/%m/%y %H:%M:%S'),
                mentor_id=mentor_id
            )
            logger.info(f"Mentor has '{number}' requests on this time '{datetime.strptime('1/1/25 10:00:00', '%d/%m/%y %H:%M:%S')}'")
        except ValueError as e:
            logger.error(f"Error finding any requests: {e}")

    # Проверяем поиск менторов по нику
    try:
        logger.info(f"Here is your mentor: {await mentor_service.get_mentor_by_id(mentor_id)}")
    except ValueError as e:
        logger.error(f"Can't find that mentor: {e}")

    try:
        logger.info(f"Here is your mentor: {await mentor_service.get_mentor_by_tg_id('@sup')}")
    except ValueError as e:
        logger.error(f"Can't find that mentor: {e}")

    # Одобряем запрос и проводим проверку
    try:
        req_counts = await mentor_service.count_requests(mentor_id)
        logger.info(
            f"Mentor has {req_counts['call_requests']} call requests and {req_counts['message_requests']} message requests")
    except ValueError as e:
        logger.error(f"Can't find that mentor: {e}")

    try:
        logger.info(f"Mentors' requests: {await mentor_service.get_requests(mentor_id)}")
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
        stat = await time_table_service.check_time_reservation(
            time=datetime.strptime("01/01/25 10:00:00", '%d/%m/%y %H:%M:%S'),
            mentor_id=mentor_id
        )
        if stat:
            logger.info(f"{datetime.strptime('1/1/25 10:00:00', '%d/%m/%y %H:%M:%S')} already occupied")
        else:
            logger.info(f"{datetime.strptime('1/1/25 10:00:00', '%d/%m/%y %H:%M:%S')} free now")
    except ValueError as e:
        logger.error(f"Can't find that date: {e}")

    yield  # Возвращаем управление приложению

    logger.info("Application shutdown: cleaning up...")  # Действия при завершении приложения


app = FastAPI(
    title="Микросервис для менторства ITAM",
    description="ИСАД — это не детский сад\n\n"
                "Отдельная благодарность Крюкову Александру Михайловичу (https://github.com/Auxxxxx)\n"
                "Без него этого микросервиса не было бы",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

# Add JWT authentication middleware
app.add_middleware(
    JWTAuthMiddleware,
    exclude_paths=["/docs", "/redoc", "/openapi.json"]
)

# Добавляем схему безопасности в спецификацию OpenAPI
app.openapi_components = {
    "securitySchemes": {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer"
        }
    }
}

# Применяем схему безопасности ко всем операциям (routes)
app.openapi_security = [{"HTTPBearer": []}]

# Create dependencies for routers
app.include_router(student_router, prefix="/mentor_service")
app.include_router(mentor_router, prefix="/mentor_service")
app.include_router(mentor_time_router, prefix="/mentor_service")