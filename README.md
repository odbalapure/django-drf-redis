## DRF + Redis

## Starting the containers

Run the command to restart the `django` service

> docker-compose run django django-admin startproject core .

**NOTE**: Comment out the `command` from `docker-compose.yaml`. This has to be done only once.

## Creating inventory setup

Run this command inside the container

> python manage.py startapp inventory

**NOTE**: This works because we have setup docker volumes.

Now go to app/core settings.py, add the `inventory` inside the `INSTALLED_APPS`. Also update the database settings:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "inventory",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": "5432",
    }
}
```

Now run the migrations inside docker, but use `psycopg[binary]`

> python manage.py migrate
