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
from ..schemas import Reaction as ReactionDao
from ..models import NoticeCreateRequest, NoticeResponse, NoticeUpdateRequest, ReactionCreateRequest, ReactionResponse


router = APIRouter(
    prefix="/interactions",
    tags=['Interactions']
)


@router.get("/view_notices/used/{user_id}", response_model=list[NoticeResponse])
def get_notices_from_neighbours(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDao).filter(UserDao.id == user_id).first()
    street_id = user.street_id
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{id} doesn\'t exist.')
    logging.info(f"fetching user with {user}")
    notices = db.query(NoticeDao).filter(NoticeDao.street_id==street_id).order_by(NoticeDao.created_at.desc()).all()
    return notices

@router.post("/like/{user_id}/notice/{notice_id}", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
def create_reactions_of_notices(reaction:ReactionCreateRequest, db: Session = Depends(get_db)):
    logging.info(f"reacting for notice with id: {reaction.notice_id}")
    reaction_dict = reaction.dict()
    user_from_db = db.query(UserDao).filter(UserDao.id == reaction.user_id).first()
    if not user_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{reaction.user_id} doesn\'t exist.')
    notice_from_db = db.query(NoticeDao).filter(NoticeDao.id == reaction.notice_id).first()
    if not notice_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'notice with id:{reaction.notice_id} doesn\'t exist.')
    # check street for notice and user
    new_reaction = ReactionDao(**reaction_dict)
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)
    return new_reaction

