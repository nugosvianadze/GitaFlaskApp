from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///my_first_db.sqlite3")
    UPLOAD_FOLDER = 'app/static/uploads'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    STATIC_FOLDER = "C:\\Users\\STUDENT\\GitaFlakProjects\\GitaFlaskApp\\static"

