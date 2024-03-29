from fastapi import FastAPI

from .routers import  users, notices, interactions
from . import schemas
from .database import retry_connect_to_db

schemas.Base.metadata.create_all(bind=retry_connect_to_db())


app = FastAPI()

app.include_router(users.router)
app.include_router(notices.router)
app.include_router(interactions.router)
