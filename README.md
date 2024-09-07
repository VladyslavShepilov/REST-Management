## Event Management
Application for managing events. Consists of 3 sub apps: 
* config, which is the main app with console commands and settings.
* events, which implements CRUD operations Events and additional functionality such as registration to event, filtering,
email notifications(* note that they are configured to store emails locally in "root_folder"/email).
* User application with JWT endpoints, registration and authentication endpoints.

### Swagger documentation(extended)
    host/api/schema/swagger-ui/

### Credentials

    python manage.py createsuperuser

### For docker
    docker exec -it <container name/id> sh
    python manage.py createsuperuser

### Using Shell Console
    git clone ...
    cd comments
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

### Using Docker
    cp .env_sample .env
    python manage.py makemigrations
    docker-compose build
    docker-compose up

### Will be available on
    http://0.0.0.0:8001/
