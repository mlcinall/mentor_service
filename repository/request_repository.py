from infrastructure.db.connection import pg_connection
from persistent.db.request import Request
from sqlalchemy import insert, select, update, UUID
from datetime import datetime
from persistent.db.request import Request
from typing import cast


class RequestRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def create_request(self,
                             call_type: int,
                             mentor_id: UUID,
                             guest_id: UUID,
                             description: str,
                             call_time: datetime | None = None) -> UUID:
        # if call_type == 0 and not call_time:
        #     raise ValueError("error: no time specified for calling")

        stmt = insert(Request).values({
            "call_type": call_type,
            "mentor_id": mentor_id,
            "guest_id": guest_id,
            "description": description,
            "call_time": call_time})

        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            request_id = result.inserted_primary_key[0]
            await session.commit()

        return request_id

    async def mentor_response(self, request_id: UUID, response: int) -> None:
        stmp = update(Request).where(cast("ColumnElement[bool]", Request.id == request_id)).values(response=response)

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_all_requests(self) -> list[Request]:
        stmt = select(Request)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            requests = [row[0] for row in rows]
            return requests

    async def get_all_requests_by_mentor_id(self, mentor_id: UUID) -> list[Request] | None:
        stmt = select(Request).where(cast("ColumnElement[bool]", Request.mentor_id == mentor_id))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            requests = [row[0] for row in rows]
            return requests

    async def get_request_by_id(self, request_id: UUID) -> Request | None:
        stmp = select(Request).where(cast("ColumnElement[bool]", Request.id == request_id)).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        if row is None:
            return None

        return row[0]
