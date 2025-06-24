from persistent.db.base import Base, WithId
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Text, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Request(Base, WithId):
    __tablename__ = "requests"

    call_type = Column(Boolean, nullable=False) # 0 -- call, 1 -- question
    time_sended = Column(DateTime, default=datetime.now(), nullable=False)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"))
    guest_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(Text, nullable=False)

    #if call_type == 0:
    call_time = Column(DateTime, nullable=True)

    response = Column(Integer, nullable=False, default=0) # 0 -- not answered, 1 -- accepted, -1 -- rejected, 2 -- cancelled
    mentor = relationship("Mentor", back_populates="requests")

