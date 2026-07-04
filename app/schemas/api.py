from pydantic import BaseModel
from typing import Optional


class UserCreatePayload(BaseModel):
    name: str
    email: str
    password: str


class UserLoginPayload(BaseModel):
    email: str
    password: str


class NotePayload(BaseModel):
    title: str
    description: str
    category: str
    completed: Optional[bool] = False
