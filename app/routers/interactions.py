from datetime import datetime
from fastapi import Depends, status, HTTPException, APIRouter
from typing import Union
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr
import logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy import func


from ..database import get_db
from ..schemas import User as UserDao
from ..schemas import Notice as NoticeDao
from ..schemas import Reaction as ReactionDao
from ..models import  NoticeResponse, ReactionCreateRequest, ReactionResponse, NoticeReactionStatusResponse


router = APIRouter(
    prefix="/interactions",
    tags=['Interactions']
)


@router.get("/view_notices/user/{user_id}", response_model=list[NoticeResponse])
def get_notices_from_neighbours(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDao).filter(UserDao.id == user_id).first()
    street_id = user.street_id
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id:{id} doesn\'t exist.')
    logging.info(f"fetching user with {user}")
    notices = db.query(NoticeDao).filter(NoticeDao.street_id==street_id).order_by(NoticeDao.created_at.desc()).all()
    return notices

@router.get("/staus/notice/{notice_id}", response_model= NoticeReactionStatusResponse)
def get_count_of_reactions_of_notice(notice_id:int, db:Session = Depends(get_db)):
    notice = db.query(NoticeDao).filter(NoticeDao.id==notice_id).first()
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'notice with id:{notice_id} doesn\'t exist.')
    reaction_counts =db.query(ReactionDao.reaction,
        func.count(ReactionDao.user_id)).filter(ReactionDao.notice_id==notice_id).group_by(ReactionDao.reaction).order_by(ReactionDao.reaction.asc()).all()
    print(dict(reaction_counts))
    reaction_counts_dict = {}
    reaction_counts_dict[reaction_counts[0][0].value]=reaction_counts[0][1]
    reaction_counts_dict[reaction_counts[1][0].value]=reaction_counts[1][1]
    count_status = NoticeReactionStatusResponse()
    count_status.count_liked=reaction_counts[0][1]
    count_status.count_disliked=reaction_counts[1][1]
    print(reaction_counts_dict)
    #return  {"reaction_counts": reaction_counts_dict}

    return count_status


@router.post("/user/{user_id}/notice/{notice_id}", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
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
    # to do check street for notice and user
    combo_user_notice = db.query(ReactionDao).filter(ReactionDao.user_id==reaction.user_id, 
                                                     ReactionDao.notice_id==reaction.notice_id).first()
    print(f"combo user notice: {combo_user_notice}")
    if combo_user_notice :
        combo_user_notice.reaction = reaction_dict["reaction"]
        db.commit()
        db.refresh(combo_user_notice)
        return combo_user_notice
    else:
        new_reaction = ReactionDao(**reaction_dict)
        db.add(new_reaction)
        db.commit()
        db.refresh(new_reaction)
        return new_reaction

