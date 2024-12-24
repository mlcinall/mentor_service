from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Path, Response, status
from loguru import logger
from pydantic import BaseModel

# Lifespan-событие
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Обработчик жизненного цикла приложения.
    Используется для инициализации данных при старте и очистки ресурсов при завершении.
    """
    pass




# Создание приложения FastAPI с lifespan
app = FastAPI(
    title="BEST_WEBAPP_EVER",
    description="IDAS IS NOT A KINDERGARTEN",
    lifespan=lifespan,
)