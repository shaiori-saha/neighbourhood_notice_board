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
from ..models import NoticeCreateRequest, NoticeResponse, NoticeUpdateRequest


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
        new_notice.street_id = user_from_db.street_id
        print(f"notice has contents: {new_notice}")
        db.add(new_notice)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{user_id} doesn\'t exist.')
        
    db.refresh(new_notice)  # recieve change

    return new_notice

@router.delete("/{id}")
async def delete_notice(id:int, db: Session = Depends(get_db)):
   count_rows_deleted = db.query(NoticeDao).filter(NoticeDao.id==id).delete()
   if count_rows_deleted ==0:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'notice with id:{id} doesn\'t exist.')
   db.commit()
   return 

@router.get("/{id}", response_model=NoticeResponse)
def get_notice(id: int, db: Session = Depends(get_db)):
    notice = db.query(NoticeDao).filter(NoticeDao.id == id).first()
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'notice with id:{id} doesn\'t exist.')
    logging.info(f"fetching notice with {notice}")

    return notice

@router.get("/search/", response_model=list[NoticeResponse])
def search_notices(user: Union[int, None] = "", db: Session = Depends(get_db)):
    notices = db.query(NoticeDao).filter(NoticeDao.user_id==user).all()
    return notices


@router.put("/{id}", response_model=NoticeResponse)
async def update_notice(notice:NoticeUpdateRequest, id: int, db: Session = Depends(get_db)):
    """ Updates an existing Notice"""
    logging.info(f"notice geting updated with id: {notice}")
    if not notice.id == id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='given id does not match with url param')
    notice_from_db = db.query(NoticeDao).filter(NoticeDao.id == id).first()
    if not notice_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'notice with id:{id} doesn\'t exist.')
    
    notice_dict = notice.dict()

    for key, value in notice_dict.items():
        setattr(notice_from_db, key, value) if value else None
    notice_from_db.created_at = datetime.now()
    db.commit()
    
    db.refresh(notice_from_db)
    return notice_from_db


# uvicorn app.main:app --reload
