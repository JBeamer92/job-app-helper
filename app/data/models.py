from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from data.database import Base


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
    position_id = Column(Integer, ForeignKey('positions.id'))
    company = Column(String, index=True)
    url = Column(String, index=False, nullable=True)

    owner = relationship('User', back_populates='postings')
    position = relationship('Position', back_populates='posting')
    events = relationship('Event', back_populates='posting', cascade='all, delete, delete-orphan')


class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True)

    posting = relationship('Posting', back_populates='position')


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Date, index=True)
    posting_id = Column(Integer, ForeignKey('postings.id'))

    posting = relationship('Posting', back_populates='events', cascade='all, delete')
