from typing import List, Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


# Used when reading/returning Item
class Item(ItemBase):
    id: int
    owner_id: int

    # Provides configurations to Pydantic
    class Config:
        # Uses = as opposed to : because it's setting a value, not a type
        # This setting allows to access attributes using item.id in addition to item['id']
        orm_mode = True


class UserBase(BaseModel):
    email: str


# password is placed here and NOT in the UserBase so that when reading Users, passwords are not passed back
# https://fastapi.tiangolo.com/tutorial/sql-databases/
class UserCreate(UserBase):
    password: str


# Used when reading/returning User
class User(UserBase):
    id: int
    is_active: bool
    items: List[Item]

    class Config:
        orm_mode = True
