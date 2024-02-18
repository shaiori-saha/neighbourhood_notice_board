from fastapi import FastAPI

from .routers import  users, notices, interactions
from . import schemas
from .database import engine

schemas.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(users.router)
app.include_router(notices.router)
app.include_router(interactions.router)


@ app.get("/")
async def root():
    return {"message": "on going"}
