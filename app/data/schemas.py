from typing import List, Optional

from pydantic import BaseModel


# POSTINGS

class PostingBase(BaseModel):
    position: str
    company: str


class PostingCreate(PostingBase):
    pass


class Posting(PostingBase):
    id: int
    owner_id: int

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
