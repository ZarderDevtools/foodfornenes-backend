# config/settings/prod.py
import os
import dj_database_url
from .base import *

from dotenv import load_dotenv

# Carga de variables de entorno
load_dotenv()


print("🌐 Using production settings")

DEBUG = False
LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"

ALLOWED_HOSTS = [
    "foodfornenes.onrender.com",
    "localhost",
    "foodfornenes-backend.onrender.com",
    "127.0.0.1"
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://foodfornenes-backend.onrender.com"
]

INSTALLED_APPS += ["whitenoise.runserver_nostatic"]
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_MAX_AGE = 31536000

DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", ""),  # ← aquí pondrás la del Session Pooler en Render
        conn_max_age=600,
    )
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
