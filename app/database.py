"""
Database Connections
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import logging

from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

def retry_connect_to_db():
    for i in range(3):
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            engine.connect()
            return engine
        except:
            logging.info("retrying to connect to database")
        time.sleep(15)

# used for actually talking to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=retry_connect_to_db())

# Define the base class which is used for extending our models
Base = declarative_base()


def get_db():
    """Dependency for using ORM"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
