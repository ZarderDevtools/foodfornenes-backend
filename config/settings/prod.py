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

# Hosts permitidos (configurado por variable de entorno en Render)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# CORS (por si en el futuro hay front web)
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_CREDENTIALS = True

# WhiteNoise para servir estáticos en producción
INSTALLED_APPS += ["whitenoise.runserver_nostatic"]
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_MAX_AGE = 31536000

# Base de datos (Session Pooler de Supabase en Render)
DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", ""),  # ← Render: URL del Session Pooler con sslmode=require
        conn_max_age=600,
    )
}

# -----------------------------
# Seguridad de transporte (HTTPS)
# -----------------------------
# Render pasa X-Forwarded-Proto, le indicamos a Django que se fíe
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Redirigir siempre a HTTPS
SECURE_SSL_REDIRECT = True

# Cookies solo por HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS: decir al navegador que este dominio siempre va por HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
