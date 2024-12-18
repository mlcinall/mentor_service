from infrastructure.db.connection import pg_connection
from persistent.db.call import Call
from sqlalchemy import insert, select, update
from datetime import time

class CallRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def add_call(self, day: int, time: time, mentor_id: int) -> None:
        stmp = insert(Call).values({"day": day, "time": time, "mentor_id": mentor_id})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def reserve_call(self, call_id: int) -> None:
        stmp = update(Call).where(Call.id == call_id).values(reservation=True)

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()


