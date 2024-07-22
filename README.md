## Welcome to the EmptyDjangoApp project

## Setup


``` shell
# Activate the environment
poetry shell
```

``` shell
# Install dependencies
poetry install
```

``` shell
# Create DB
./manage.py migrate
```

``` shell
# Create a superuser
./manage.py createsuperuser --username admin --email admin@example.com
```

``` shell
# Run server
./manage.py runserver localhost:8000
```