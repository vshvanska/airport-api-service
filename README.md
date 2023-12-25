# Airport-API-Service
Api service for tracking flights written on DRF

# Installing using GitHub
Install PostgresSQL and create db

- git clone https://github.com/vshvanska/airport-api-service
- cd cinema_API
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- create .env file, inside define variables from .env.sample

- python manage.py migrate
- python manage.py runserver

you can use command python manage.py loaddata airport_service_db_data.json to fill db 

# Run with docker
Docker should be installed

docker-compose build
docker-compose up

# Getting access
create user via /api/user/register/
get access token via /api/user/token/

# Features
 - JWT authenticated
 - Throttling
 - Admin panel /admin/
 - Documentation is located at /api/doc/swagger
 - Managing orders and tickets
 - Creating airplanes, airports, routes, crew
 - Managing flights
 - Adding flights with crew
 - Filtering airports by city
 - Filtering routes by source, destination
 - Filtering flights by routes, date
