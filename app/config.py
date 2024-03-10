from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    # db
    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")
    db_pass: str = os.getenv("DB_PASS")
    db_name: str = os.getenv("DB_NAME")
    db_username: str = os.getenv("DB_USERNAME")

    
    # class Config:
    #     cwd = os.getcwd()
    #     env_file = cwd + "\deployment\myapp.env"
    


settings = Settings()
