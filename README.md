Tää listaa raideja ja silleen

You can get your own Raidikalu by clicking on this magic button:

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/raidikalu/raidikalu)

_default login is_ `admin:defaultpassword`

To set up a local development environment you can follow these out-of-date instructions, or look forward to updated ones.

- Get python and pipenv
- `pipenv install --dev` to set up development environment and install all dependencies
- `pipenv shell` to get access to the development environment and dependencies
- Make a copy of `local_settings.py.tpl` and remove the `.tpl`. You can edit this for your needs
- Append `--settings=local_settings` to all `manage.py` commands **or** set `DJANGO_SETTINGS_MODULE=local_settings` in your environment variables
- `python manage.py migrate` to run initial migrations for your local database
- `python manage.py createsuperuser` to create an admin account for yourself
- `python manage.py runserver` to run the app
- Do your thing
