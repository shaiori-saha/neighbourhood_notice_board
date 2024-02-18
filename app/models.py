import enum
from pydantic import BaseModel, EmailStr, validator
from typing import Union
from datetime import datetime
from app.database import get_db

from app.schemas import Street

class PhoneNumberResponse(BaseModel):
    id: int
    phone_number: str

    class Config():
        orm_mode = True

class UserCreateRequest(BaseModel):
    name: str
    password: str
    #address: Union[str, None] = None
    email: EmailStr
    phone_numbers: Union[list[str], None] = None
    street_name: Union[str, None] = None
    house_number: Union[str, None] = None
    postal_code: Union[str, None] = None
    city: Union[str, None] = None


class UserUpdateRequest(BaseModel):
    id: int
    name: Union[str, None] = None
    email: Union[EmailStr, None] = None  # from pydantic
    created_at: Union[datetime, None] = None
    #address: Union[str, None] = None
    phone_numbers: Union[list[str], None] = None

def get_street_name(street_id):
    if street_id is None:
        return ""
    return get_db().__next__().query(Street).filter(Street.id == street_id).first().street_name


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr  # from pydantic
    created_at: datetime
    #address: Union[str, None] = None
    phone_numbers: list[PhoneNumberResponse] = []
    street_id: Union[int, None] = None
    street_name: Union[str, None] = None
    house_number: Union[str, None] = None
    postal_code: Union[str, None] = None
    city: Union[str, None] = None

    @validator("street_name", always=True)
    def set_street_name(cls, v, values, **kwargs):
        """Set the eggs field based upon a spam value."""
        return v or get_street_name(values.get("street_id"))

    class Config():
        orm_mode = True

    

class NoticeCreateRequest(BaseModel):
    content: str
    user_id: int

class NoticeUpdateRequest(BaseModel):
    id: int
    content: Union[str, None] = None

class NoticeResponse(BaseModel):
    id:int
    content: str
    created_at: datetime
    user_id: int

    class Config():
        orm_mode = True

class ReactionChoices(str, enum.Enum):
    LIKED = 'LIKED'
    DISLIKED = 'DISLIKED'
    NO_REACTION = 'NO_REACTION'
    
class ReactionCreateRequest(BaseModel):
    user_id: int
    notice_id: int
    reaction: str

class ReactionResponse(BaseModel):
    id: int
    user_id: int
    notice_id: int
    reaction: ReactionChoices
    class Config():
        allow_population_by_field_name = True
        orm_mode = True
        use_enum_values = True

