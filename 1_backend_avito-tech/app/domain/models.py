from sqlalchemy import Column, Integer, String

from app.db import Base



class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    target = Column(String, nullable=False)
