from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    uploader = relationship("User", back_populates="papers")
    notes = relationship("Note", back_populates="paper", cascade="all, delete-orphan")
