from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    # db
    db_host: str
    db_port: str
    db_pass: str
    db_name: str
    db_username: str

    
    class Config:
        cwd = os.getcwd()
        env_file = cwd + "\deployment\myapp.env"


settings = Settings()
