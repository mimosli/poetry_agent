from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship

from .db import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    run_date = Column(String, index=True)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ideas = relationship("Idea", back_populates="run")


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=True)

    title = Column(String)
    hook = Column(Text)
    format = Column(String)
    objective = Column(String)
    status = Column(String, default="CREATED")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    run = relationship("Run", back_populates="ideas")
    approvals = relationship("Approval", back_populates="idea")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"))

    decision = Column(String)
    feedback = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), server_default=func.now())

    idea = relationship("Idea", back_populates="approvals")


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"))
    folder_path = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
