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

## Setting up database init

Copy the init.sql to docker entry for postgres

```sh
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/init.sql
CREATE TABLE
CREATE TABLE
COPY 34
COPY 30
```

## Creating first REST endpoint

Add "rest_framework" to the INSTALLED_APP array.

Then create a serializer

```python
from rest_framework import serialzers
from .models import Product


class ProductSerializer(serialzers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]
```

Add the following in the views.py file

```python
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product
from .serializer import ProductSerializer


# Create your views here.
class ProductListAPIView(APIView):
    def get(self, _):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
```

Create a urls file

```python
from django.urls import path
from .views import ProductListAPIView

urlpatterns = [path("products/", ProductListAPIView.as_view(), name="product-list")]
```

Finally in the core urls.py, add the path for inventory

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [path("admin/", admin.site.urls), path("api/", include("inventory.urls"))]
```

## Creating endpoint for docs

Add `drf_spectacular` to INSTALLED_APPS list. And add the following in the settings.py file as well

```python
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Session based cart",
    "DESCRIPTION": "Redis fast storage for web apps",
    "VERSION": "1.0.0",
}
```

And update the core/urls.py as well

```python
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("inventory.urls")),
]
```
