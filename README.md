# Idea Learning Management System

## Configuration

### loca_settings.py

Create `church_app/local_setting.py` with the following code:

```sss
import os

#Celery broker url e.g redis://127.0.0.1:6379/0
CELERY_BROKER_URL = "..."

#MNotify SMS broker api key
MNOTIFY_API = "..."	

SECRET_KEY = '...'
DEBUG = True
ALLOWED_HOSTS = ["*"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
```

NOTE:
SECRET_KEY is the application's secret key

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/dodziraynard/idealms.git
$ cd idealms
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ virtualenv2 --no-site-packages env
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```

Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv2`.

Once `pip` has finished downloading the dependencies, create administrator account for managing the database:

```sh
(env)$ python manage.py createsuperuser
```

Then run the server:

```sh
(env)$ cd project
(env)$ python manage.py runserver
```

And navigate to `http://127.0.0.1:8000` and sign in with the administrator credentials.

You can now test the flow of the application 🙂

# Tests

To run the tests, cd into the directory where manage.py is:

```sh
(env)$ python manage.py test
```