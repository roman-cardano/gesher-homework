## Welcome to the EmptyDjangoApp project

## Setup


``` shell
# Activate the environment
poetry shell

# Install dependencies
poetry install

# Create DB
./manage.py migrate

# Create a superuser
./manage.py createsuperuser --username admin --email admin@example.com

# Run server
./manage.py runserver localhost:8000
```