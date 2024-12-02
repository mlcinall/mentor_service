from persistent.db.base import Base, WithId
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Boolean, Integer, Time, ForeignKey
from sqlalchemy.orm import relationship


class Call(Base, WithId):
    __tablename__ = "calls"

    day = Column(Integer, nullable=True)  # possible call day number (1 -- Monday, 2 -- Tuesday et)
    time = Column(Time, nullable=True)
    reservation = Column(Boolean, default=False)  # is there a time to call
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"))
    mentor = relationship("Mentor", back_populates="calls")
    request = relationship("Request", uselist=False, back_populates="call")
