from typing import Hashable, List
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

'''notice_user_association = Table(
    'notice_users',
    Base.metadata,
    Column('notice_id', Integer, ForeignKey('notice.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)'''



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    address = Column(String)
    phone_numbers = relationship(
        "PhoneNumber",
        back_populates='user',
        cascade='delete, delete-orphan, save-update',
        passive_deletes=True

    ) # type: List[PhoneNumber]

    notices = relationship("Notice", back_populates="notice_writer") # type: List[Notice]


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    phone_number = Column(String, nullable=False, unique=True, index=True)
    user = relationship("User", back_populates="phone_numbers") # type: User

class Notice(Base):
    __tablename__ = "notice"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(String, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    notice_writer = relationship("User", back_populates="notices") # type: User