Tää listaa raideja ja silleen

Omalle koneelle tän saa pystyyn tälleen:

From here on we'll be using English because reasons

- Get python and pipenv
- `pipenv install` to set up development environment and install all dependencies
- `pipenv shell` to get access to the development environment and dependencies
- Make a copy of `local_settings.py.tpl` and remove the `.tpl`. You can edit this for your needs
- Append `--settings=local_settings` to all `manage.py` commands **or** set `DJANGO_SETTINGS_MODULE=local_settings` in your environment variables
- `python manage.py migrate` to run initial migrations for your local database
- `python manage.py createsuperuser` to create an admin account for yourself
- `python manage.py runserver` to run the app
- Do your thing
