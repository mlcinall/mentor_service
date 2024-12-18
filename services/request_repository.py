from infrastructure.db.connection import pg_connection
from persistent.db.request import Request
from sqlalchemy import insert, select, update
from datetime import time
from services.calls_repository import CallRepository

class RequestRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def reserve_call(self, mentor_id: int, student_id: int, description: str, call_id: int) -> None:
        call_rep = CallRepository()
        await call_rep.reserve_call(call_id)
        stmp = insert(Request).values({"call_type": 0, "mentor_id": mentor_id, "guest_id": student_id,
                                       "description": description, "response": 0})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def reserve_question(self, mentor_id: int, student_id: int, description: str) -> None:
        stmp = insert(Request).values(
            {"call_type": 1, "mentor_id": mentor_id, "guest_id": student_id,
             "description": description, "response": 0})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()


    async def mentor_response(self, request_id: int, response: int) -> None:
        stmp = update(Request).where(Request.id == request_id).values(response=response)

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()


    async def get_mentor_response(self, request_id):
        stmp = select(Request.response).where(Request.id == request_id).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        if row is None:
            return None

        return row[0]
