from datetime import datetime
from fastapi import Depends, status, HTTPException, APIRouter
from typing import Union
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr
import logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import text



from ..database import get_db
from ..models import User as UserDao
from ..models import PhoneNumber as PhoneNumberDao



router = APIRouter(
    prefix="/users",
    tags=['Users']
)

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


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr  # from pydantic
    created_at: datetime
    address: Union[str, None] = None
    phone_numbers: list[PhoneNumberResponse] = []

    class Config():
        orm_mode = True

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user:UserCreateRequest, db: Session = Depends(get_db)):
    """ Creates a User"""
    logging.info(f"user craeted with id: {user}")
    user_dict = user.dict()
    phone_numbers = user_dict['phone_numbers']
    del user_dict['phone_numbers']
    new_user = UserDao(**user_dict)
    new_phone_numbers = list()
    try:
        for phone_number in phone_numbers:
            new_phone_number = PhoneNumberDao()
            #new_phone_number.user_id = new_user.id
            new_phone_number.phone_number = phone_number
            db.add(new_phone_number)
            new_phone_numbers.append(new_phone_number)
        db.commit()
    except IntegrityError as e:
        logging.warn(f"exception is {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"phone_number {phone_number} already exists")
    
    db.add(new_user)  # make change
    try:
        db.commit()  # save change
    except IntegrityError as e:
        logging.warn(f"exception is {e}")
        # TODO: delete phone numbers
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"email {user.email} already exists")
        
    db.refresh(new_user)  # recieve change
            
    for phone_number in new_phone_numbers:
        db.refresh(phone_number)
        phone_number.user_id = new_user.id
        db.commit()

    return new_user


@router.put("/{id}", response_model=UserResponse)
async def update_user(user:UserUpdateRequest, id: int, db: Session = Depends(get_db)):
    """ Updates an existing User"""
    logging.info(f"user craeted with id: {user}")
    if not user.id == id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='given id does not match with url param')
    user_from_db = db.query(UserDao).filter(UserDao.id == id).first()
    if not user_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{id} doesn\'t exist.')
    
    
    for key, value in user.dict().items():
        setattr(user_from_db, key, value) if value else None
    db.commit()
    
    print(user_from_db.id)
    db.refresh(user_from_db)  # recieve change
    return user_from_db


@router.delete("/{id}")
async def delete_user(id:int, db: Session = Depends(get_db)):
   count_rows_deleted = db.query(UserDao).filter(UserDao.id==id).delete()
   if count_rows_deleted ==0:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{id} doesn\'t exist.')
   db.commit()
   return 



@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(UserDao).filter(UserDao.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{id} doesn\'t exist.')
    logging.info(f"fetching user with {user}")

    return user

@router.get("/search/", response_model=list[UserResponse])
def search_users(email: Union[str, None] = "", name: Union[str, None] = "", db: Session = Depends(get_db)):
    users = db.query(UserDao).filter(UserDao.email.contains(email), UserDao.name.contains(name)).all()
    return users






# uvicorn app.main:app --reload
