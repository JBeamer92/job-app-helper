from typing import List, Optional

from datetime import date

from pydantic import BaseModel


# EVENTS

class EventBase(BaseModel):
    name: str
    date: date


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    posting_id: int

    class Config:
        orm_mode = True


# POSITIONS

class PositionBase(BaseModel):
    name: str


class PositionCreate(PositionBase):
    pass


class PositionUpdate(PositionBase):
    id: int


class Position(PositionBase):
    id: int

    class Config:
        orm_mode = True


# POSTINGS

class PostingBase(BaseModel):
    company: str
    url: Optional[str] = None


class PostingCreate(PostingBase):
    position: PositionCreate
    # events: Optional[List[EventCreate]] = None


class PostingUpdate(PostingCreate):
    id: int
    position = PositionUpdate


class Posting(PostingBase):
    id: int
    owner_id: int
    position: Position
    # events: List[Event] = None

    class Config:
        orm_mode = True


# USERS

class UserBase(BaseModel):
    email: str


# password is placed here and NOT in the UserBase so that when reading Users, passwords are not passed back
class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    disabled: bool
    postings: List[Posting] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
