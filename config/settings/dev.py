# config/settings/dev.py
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from .base import *

# Cargar el .env desde la raíz del proyecto (seguro)
BASE_DIR = Path(__file__).resolve().parent.parent  # .../config
load_dotenv(dotenv_path=BASE_DIR.parent / ".env")

print("🚀 Using development settings")

DEBUG = True
LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

raw_url = os.getenv("DATABASE_URL", "").strip()
# print("DATABASE_URL ->", repr(raw_url))  # TEMP: para ver si tiene espacios/raros

DATABASES = {
    "default": dj_database_url.parse(raw_url, conn_max_age=600)
}
