from pydantic import BaseModel, EmailStr
from typing import Union
from datetime import datetime


class PhoneNumberResponse(BaseModel):
    id: int
    phone_number: str

    class Config():
        orm_mode = True

class UserCreateRequest(BaseModel):
    name: str
    password: str
    address: Union[str, None] = None
    email: EmailStr
    phone_numbers: Union[list[str], None] = None

class UserUpdateRequest(BaseModel):
    id: int
    name: Union[str, None] = None
    email: Union[EmailStr, None] = None  # from pydantic
    created_at: Union[datetime, None] = None
    address: Union[str, None] = None
    phone_numbers: Union[list[str], None] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr  # from pydantic
    created_at: datetime
    address: Union[str, None] = None
    phone_numbers: list[PhoneNumberResponse] = []

    class Config():
        orm_mode = True

class NoticeCreateRequest(BaseModel):
    content: str
    user_id: int

class NoticeResponse(BaseModel):
    id:int
    content: str
    created_at: datetime
    user_id: int

    class Config():
        orm_mode = True