from persistent.db.base import Base, WithId
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Text, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Request(Base, WithId):
    __tablename__ = "requests"

    call_type = Column(Boolean, nullable=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"))
    time = Column(DateTime, default=datetime.now())
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"))
    guest_tg_id = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    mentor = relationship("Mentor", back_populates="requests")
    call = relationship("Call", back_populates="request")

