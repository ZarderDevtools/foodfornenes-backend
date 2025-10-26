web: bash -c "
python manage.py migrate &&
python manage.py shell -c \"import os; from django.contrib.auth import get_user_model; U=get_user_model(); u=os.getenv('DJANGO_SUPERUSER_USERNAME'); e=os.getenv('DJANGO_SUPERUSER_EMAIL'); p=os.getenv('DJANGO_SUPERUSER_PASSWORD');
import sys;
# si faltan vars, no hacemos nada
print('skip superuser: missing env') if not (u and p) else (
    print('superuser exists') if U.objects.filter(username=u).exists() else (U.objects.create_superuser(u, e or '', p), print('superuser created'))
)\" &&
gunicorn config.wsgi:application --preload --workers=2 --threads=4 --timeout=120
"
