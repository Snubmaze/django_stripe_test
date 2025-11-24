python manage.py makemigrations --noinput
python manage.py migrate --noinput

python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: username=admin, password=admin')
END

python management/commands/initdata.py
exec "$@"