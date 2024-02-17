from datetime import datetime
from fastapi import Depends, status, HTTPException, APIRouter
from typing import Union
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr
import logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


from ..database import get_db
from ..schemas import User as UserDao
from ..schemas import Notice as NoticeDao
from ..models import NoticeCreateRequest, NoticeResponse


router = APIRouter(
    prefix="/notices",
    tags=['Notices']
)


@router.post("/", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_notice(notice:NoticeCreateRequest, db: Session = Depends(get_db)):
    """ Creates a Notice"""
    logging.info(f"notice craeted with id: {notice}")
    notice_dict = notice.dict()
    user_id = notice_dict['user_id']
    del notice_dict['user_id']
    new_notice = NoticeDao(**notice_dict)
    user_from_db = db.query(UserDao).filter(UserDao.id == user_id).first()
    if  user_from_db:
        new_notice.user_id = user_id
        print(f"notice has contents: {new_notice}")
        db.add(new_notice)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{user_id} doesn\'t exist.')
        
    db.refresh(new_notice)  # recieve change

    return new_notice


'''@router.put("/{id}", response_model=UserResponse)
async def update_user(user:UserUpdateRequest, id: int, db: Session = Depends(get_db)):
    """ Updates an existing User"""
    logging.info(f"user craeted with id: {user}")
    if not user.id == id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='given id does not match with url param')
    user_from_db = db.query(UserDao).filter(UserDao.id == id).first()
    if not user_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{id} doesn\'t exist.')
    
    user_dict = user.dict()
    requested_phone_numbers = user_dict['phone_numbers']
    logging.debug(f"requested phone numbers: {requested_phone_numbers}")
    del user_dict['phone_numbers']
    new_phone_numbers = list()
    if user_dict['email']:
        user_with_same_email = db.query(UserDao).filter(UserDao.email == user_dict['email']).all()
        logging.debug(f"user_with_same_email: {user_with_same_email}")
        if len(user_with_same_email)==1 and user_with_same_email[0].id==id:
            del user_dict['email']
        elif len(user_with_same_email)!=0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"email_id {user_dict['email']} already exists")


    try:
        already_existing_phones_tuple = db.query(PhoneNumberDao.phone_number).filter(PhoneNumberDao.user_id == id).all()
        already_existing_phones_numbers = [i[0] for i in already_existing_phones_tuple]
        if requested_phone_numbers:
            phones_to_delete = sorted(set(already_existing_phones_numbers)-set(requested_phone_numbers))
            logging.debug(f"phones to delete: {phones_to_delete}")
            if  phones_to_delete:
                for delete_phone in phones_to_delete:
                    count_rows_deleted = db.query(PhoneNumberDao).filter(PhoneNumberDao.phone_number==delete_phone).delete()
                    if count_rows_deleted ==0:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f'phone with number:{delete_phone} doesn\'t exist.')
                    db.commit()
            phones_to_add = list(set(requested_phone_numbers)-set(already_existing_phones_numbers))
            logging.debug(f"finally added ones will be: {phones_to_add}")
            for phone_number in phones_to_add:
                new_phone_number = PhoneNumberDao()
                #new_phone_number.user_id = new_user.id
                new_phone_number.phone_number = phone_number
                new_phone_number.user_id = user_from_db.id
                db.add(new_phone_number)
                new_phone_numbers.append(new_phone_number)
                db.commit()
                db.refresh(new_phone_number)
                #phone_number.user_id = user_from_db.id
    except IntegrityError as e:
        logging.warn(f"exception is {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"phone_number {new_phone_number.phone_number} already exists")
    


    for key, value in user_dict.items():
        setattr(user_from_db, key, value) if value else None
    db.commit()
    
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
'''