from pydantic import BaseSettings


class Settings(BaseSettings):
    # db
    db_host: str
    db_port: str
    db_pass: str
    db_name: str
    db_username: str

    
    class Config:
        env_file = "C:\prac\proj_try_002\\neighbourhood_notice_board\myapp.env"


settings = Settings()
