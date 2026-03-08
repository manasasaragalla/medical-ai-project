from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
import datetime

class Interaction(Base):
    __tablename__ = "interactions"

    id                  = Column(Integer, primary_key=True, index=True)
    hcp_name            = Column(String(255), nullable=False)
    interaction_type    = Column(String(100), default="Meeting")
    date                = Column(String(50))
    time                = Column(String(50))
    attendees           = Column(Text)
    topics_discussed    = Column(Text)
    materials_shared    = Column(Text)
    samples_distributed = Column(Text)
    sentiment           = Column(String(50), default="Neutral")
    outcomes            = Column(Text)
    follow_up_actions   = Column(Text)
    ai_summary          = Column(Text)
    source              = Column(String(50), default="form")
    created_at          = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.datetime.utcnow,
                                 onupdate=datetime.datetime.utcnow)