from infrastructure.db.connection import pg_connection
from persistent.db.request import Request
from sqlalchemy import insert, select, update, UUID
from datetime import datetime
from persistent.db.request import Request
from typing import cast, Optional


class RequestRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def create_request(self,
                             call_type: int,
                             mentor_id: UUID,
                             guest_id: UUID,
                             description: str,
                             call_time: Optional[datetime] = None) -> Optional[UUID]:
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

    async def get_all_requests_by_mentor_id(self, mentor_id: UUID) -> Optional[list[Request]]:
        stmt = select(Request).where(cast("ColumnElement[bool]", Request.mentor_id == mentor_id))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            requests = [row[0] for row in rows]
            return requests

    async def get_all_requests_by_time(self, mentor_id: UUID, time: datetime) -> Optional[list[Request]]:
        stmt = select(Request).where(cast("ColumnElement[bool]", Request.call_time == time),
                                     cast("ColumnElement[bool]", Request.mentor_id == mentor_id))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            requests = [row[0] for row in rows]
            return requests

    async def get_request_by_id(self, request_id: UUID) -> Optional[Request]:
        stmp = select(Request).where(cast("ColumnElement[bool]", Request.id == request_id)).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        if row is None:
            return None

        return row[0]

    async def check_time_reservation(self, mentor_id: UUID, time: datetime) -> bool:
        """Return True if there is a pending or accepted request at this time.

        Requests with status ``2`` (cancelled) do not count as a reservation.
        """
        stmt = select(Request).where(cast("ColumnElement[bool]", Request.call_time == time),
                                     cast("ColumnElement[bool]", Request.mentor_id == mentor_id))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            requests = [row[0] for row in rows]

            for request in requests:
                if request.response in (0, 1):
                    return True

            return False
