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
    prefix="/interactions",
    tags=['Interactions']
)


@router.get("/{id}", response_model=list[NoticeResponse])
def get_notices_from_neighbours(id: int, db: Session = Depends(get_db)):
    user = db.query(UserDao).filter(UserDao.id == id).first()
    street_id = user.street_id
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{id} doesn\'t exist.')
    logging.info(f"fetching user with {user}")
    notices = db.query(NoticeDao).filter(NoticeDao.street_id==street_id).order_by(NoticeDao.created_at.desc()).all()
    return notices


