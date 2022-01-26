# from app.db.database import SQLALCHEMY_DATABASE_URL
# from starlette.config import Config
# from starlette.datastructures import Secret
#
# config = Config(".env")
#
# PROJECT_NAME = "phresh"
# VERSION = "1.0.0"
# API_PREFIX = "/api"
#
# SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")
#
# POSTGRES_USER = config("POSTGRES_USER", cast=str)
# POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
# POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
# POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
# POSTGRES_DB = config("POSTGRES_DB", cast=str)
#
# DATABASE_URL = config(
#   "DATABASE_URL",
#   cast=SQLALCHEMY_DATABASE_URL,
#   default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
# )
import os
from dotenv import load_dotenv
PAGE_SIZE = 5

load_dotenv('.env')
FILE_PATH = os.getcwd() +"/db_image/"
# DEFAULT_USER = "400430012"
# HOST_IP = "192.168.45.35"
# PORT = "8000"
# HOST_NAME = "http://"+HOST_IP+":"+PORT
# SQLALCHEMY_DATABASE_URL = "sqlite:///sql_app_20210924.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:88888888@192.168.45.51/fastapi_db_20210924"

DEFAULT_USER = os.getenv('DEFAULT_USER')
HOST_IP = os.getenv('HOST_IP')
PORT = os.getenv('PORT')
HOST_NAME = os.getenv('HOST_NAME')
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
FASTEYES_OUTPUT_PATH = os.getenv('FASTEYES_OUTPUT_PATH')
AREA_PATH = os.getenv('AREA_PATH')
