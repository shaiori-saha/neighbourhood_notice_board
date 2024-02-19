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
from ..schemas import PhoneNumber as PhoneNumberDao
from ..schemas import Street as StreetDao
from ..models import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    PhoneNumberResponse,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_db)):
    """Creates a User"""
    logging.info(f"user craeted with id: {user}")
    user_dict = user.dict()
    phone_numbers = user_dict["phone_numbers"]
    del user_dict["phone_numbers"]
    street_name = user_dict["street_name"]
    del user_dict["street_name"]
    new_user = UserDao(**user_dict)
    new_phone_numbers = list()

    street_id = (
        db.query(StreetDao.id).filter(StreetDao.street_name == street_name).all()
    )
    if len(street_id) == 0:
        new_street = StreetDao()
        new_street.street_name = street_name
        db.add(new_street)
        db.commit()
        db.refresh(new_street)  # recieve change
        print(f"new street created with id {new_street.id}")
        new_user.street_id = new_street.id
    else:
        new_user.street_id = street_id[0].id

    try:
        for phone_number in phone_numbers:
            new_phone_number = PhoneNumberDao()
            # new_phone_number.user_id = new_user.id
            new_phone_number.phone_number = phone_number
            db.add(new_phone_number)
            new_phone_numbers.append(new_phone_number)
        db.commit()
    except IntegrityError as e:
        logging.warn(f"exception is {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"phone_number {phone_number} already exists",
        )

    db.add(new_user)  # make change
    try:
        db.commit()  # save change
    except IntegrityError as e:
        logging.warn(f"exception is {e}")
        # TODO: delete phone numbers
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"email {user.email} already exists",
        )

    db.refresh(new_user)  # recieve change

    for phone_number in new_phone_numbers:
        db.refresh(phone_number)
        phone_number.user_id = new_user.id
        db.commit()
    # new_user['street_name'] = street_name

    return new_user


@router.put("/{id}", response_model=UserResponse)
async def update_user(user: UserUpdateRequest, id: int, db: Session = Depends(get_db)):
    """Updates an existing User"""
    logging.info(f"user craeted with id: {user}")
    if not user.id == id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="given id does not match with url param",
        )
    user_from_db = db.query(UserDao).filter(UserDao.id == id).first()
    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id:{id} doesn't exist.",
        )

    user_dict = user.dict()
    requested_phone_numbers = user_dict["phone_numbers"]
    logging.debug(f"requested phone numbers: {requested_phone_numbers}")
    del user_dict["phone_numbers"]
    new_phone_numbers = list()
    if user_dict["email"]:
        user_with_same_email = (
            db.query(UserDao).filter(UserDao.email == user_dict["email"]).all()
        )
        logging.debug(f"user_with_same_email: {user_with_same_email}")
        if len(user_with_same_email) == 1 and user_with_same_email[0].id == id:
            del user_dict["email"]
        elif len(user_with_same_email) != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"email_id {user_dict['email']} already exists",
            )

    try:
        already_existing_phones_tuple = (
            db.query(PhoneNumberDao.phone_number)
            .filter(PhoneNumberDao.user_id == id)
            .all()
        )
        already_existing_phones_numbers = [i[0] for i in already_existing_phones_tuple]
        if requested_phone_numbers:
            phones_to_delete = sorted(
                set(already_existing_phones_numbers) - set(requested_phone_numbers)
            )
            logging.debug(f"phones to delete: {phones_to_delete}")
            if phones_to_delete:
                for delete_phone in phones_to_delete:
                    count_rows_deleted = (
                        db.query(PhoneNumberDao)
                        .filter(PhoneNumberDao.phone_number == delete_phone)
                        .delete()
                    )
                    if count_rows_deleted == 0:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"phone with number:{delete_phone} doesn't exist.",
                        )
                    db.commit()
            phones_to_add = list(
                set(requested_phone_numbers) - set(already_existing_phones_numbers)
            )
            logging.debug(f"finally added ones will be: {phones_to_add}")
            for phone_number in phones_to_add:
                new_phone_number = PhoneNumberDao()
                # new_phone_number.user_id = new_user.id
                new_phone_number.phone_number = phone_number
                new_phone_number.user_id = user_from_db.id
                db.add(new_phone_number)
                new_phone_numbers.append(new_phone_number)
                db.commit()
                db.refresh(new_phone_number)
                # phone_number.user_id = user_from_db.id
    except IntegrityError as e:
        logging.warn(f"exception is {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"phone_number {new_phone_number.phone_number} already exists",
        )

    for key, value in user_dict.items():
        setattr(user_from_db, key, value) if value else None
    db.commit()

    db.refresh(user_from_db)  # recieve change
    return user_from_db


@router.delete("/{id}")
async def delete_user(id: int, db: Session = Depends(get_db)):
    count_rows_deleted = db.query(UserDao).filter(UserDao.id == id).delete()
    if count_rows_deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id:{id} doesn't exist.",
        )
    db.commit()
    return


@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(UserDao).filter(UserDao.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id:{id} doesn't exist.",
        )
    logging.info(f"fetching user with {user}")

    return user


@router.get("/search/", response_model=list[UserResponse])
def search_users(
    email: Union[str, None] = "",
    name: Union[str, None] = "",
    db: Session = Depends(get_db),
):
    users = (
        db.query(UserDao)
        .filter(UserDao.email.contains(email), UserDao.name.contains(name))
        .all()
    )
    return users