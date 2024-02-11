"""
Database Connections
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# used for actually talking to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base class which is used for extending our models
Base = declarative_base()


def get_db():
    """Dependency for using ORM"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
