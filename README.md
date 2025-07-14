# meetstack_backend

meetstack_backend es la api con drf

## lo básico

```python

pip install -r requirements.txt
django-admin startproject meetstack_backend .
python manage.py startapp core
```

## correr con act

```bash
act push -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 --container-architecture linux/amd64

```

```bash
gunicorn meetstack_backend.wsgi:application --bind 0.0.0.0:8000
```

## Render Manual Deployment

### Start Command

```
python3 -m gunicorn meetstack_backend.wsgi:application --bind 0.0.0.0:$PORT
```

- el endpoint de health en render es

## link a url

[Health Check en Render](https://meetstack-backend.onrender.com/api/v1/health/)

# Documentation

- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django](https://docs.djangoproject.com/en/4.2/)
- [Deploy Django Render](https://render.com/docs/deploy-django)

## Levantar Postgres en local

```bash
docker compose up -d
```
