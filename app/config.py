from pydantic import BaseSettings


class Settings(BaseSettings):
    # db
    db_host: str
    db_port: str
    db_pass: str
    db_name: str
    db_username: str

    
    class Config:
        env_file = "C:\prac\\try_proj_002\myapp.env"


settings = Settings()
