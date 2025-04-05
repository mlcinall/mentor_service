import multiprocessing as mp

from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Postgres(BaseModel):
    database: str = "db_main"
    port: int = 5433
    username: str = "db_main"
    password: str = "db_main"


class Uvicorn(BaseModel):
    host: str = "localhost"
    port: int = 8000
    workers: int = 1


class CORS(BaseModel):
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = False
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class _Settings(BaseSettings):
    pg: Postgres = Postgres()
    uvicorn: Uvicorn = Uvicorn()
    cors: CORS = CORS()

    model_config = SettingsConfigDict(env_prefix="app_", env_nested_delimiter="__")


settings = _Settings()
logger.info("settings.inited {}", settings.model_dump_json())