import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """Class for users model"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(21), unique=True, nullable=False)
    password = Column(String(200), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
