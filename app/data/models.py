from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.data.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

    postings = relationship('Posting', back_populates='owner')


class Posting(Base):
    __tablename__ = 'postings'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    position = Column(String, index=True)
    company = Column(String, index=True)
    url = Column(String, index=False, nullable=True)

    owner = relationship('User', back_populates='postings')
    events = relationship('Event', back_populates='posting')


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(String, index=True)
    posting_id = Column(Integer, ForeignKey('postings.id'))

    posting = relationship('Posting', back_populates='events')
