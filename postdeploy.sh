#!/bin/sh

python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', None, 'defaultpassword')" | python manage.py shell
