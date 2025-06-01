from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AgentToken(Base):
    """Agent access token model"""
    __tablename__   = 'agent_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False, index=True)  # Agent ID
    name = Column(String, nullable=False)  # Token name
    token = Column(String, nullable=False, unique=True)  # Token value
    created_at = Column(DateTime, default=func.now())  # Created time

    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "name": self.name,
            "token": self.token,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }