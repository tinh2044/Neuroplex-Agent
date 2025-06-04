import time
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class KnowledgeDatabase(Base):
    """Knowledge database model"""
    __tablename__ = 'knowledge_databases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    embedding = Column(String, nullable=True)
    dimension = Column(Integer, nullable=True)
    metadata_extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

    related_files = relationship("KnowledgeFile", back_populates="database", cascade="all, delete-orphan")

    def as_dict(self):
        data = {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "description": self.description,
            "embedding": self.embedding,
            "dimension": self.dimension,
            "metadata": self.metadata_extra or {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

        data["files"] = {f.uid: f.as_dict() for f in self.related_files} if self.related_files else {}
        return data


class KnowledgeFile(Base):
    """Knowledge file model"""
    __tablename__ = 'knowledge_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String, nullable=False, index=True)
    repo_uid = Column(String, ForeignKey('knowledge_databases.uid'), nullable=False)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    database = relationship("KnowledgeDatabase", back_populates="related_files")
    content_blocks = relationship("KnowledgeNode", back_populates="file", cascade="all, delete-orphan")

    def as_dict(self):
        data = {
            "uid": self.uid,
            "filename": self.filename,
            "path": self.path,
            "type": self.kind,
            "status": self.state,
            "created_at": self.created_at.timestamp() if self.created_at else time.time()
        }

        data["nodes"] = [n.as_dict() for n in self.content_blocks] if self.content_blocks else []
        return data


class KnowledgeNode(Base):
    """Knowledge block model"""
    __tablename__ = 'knowledge_nodes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_uid = Column(String, ForeignKey('knowledge_files.uid'), nullable=False)
    content_text = Column(Text, nullable=False)
    hash = Column(String, nullable=True)
    start_pos = Column(Integer, nullable=True)
    end_pos = Column(Integer, nullable=True)
    metadata_extra = Column(JSON, nullable=True)

    file = relationship("KnowledgeFile", back_populates="content_blocks")

    def as_dict(self):
        return {
            "id": self.id,
            "file_id": self.file_uid,
            "text": self.content_text,
            "hash": self.hash,
            "start_char_idx": self.start_pos,
            "end_char_idx": self.end_pos,
            "metadata": self.metadata_extra or {}
        }
