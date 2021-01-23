##Description:
- This is django project which create rest APIs for user authentication and note creation.
- In this project contains Two Apps:
   1. __User__
   2. __Notes__ 

***1.User:***

- It contains RegisterAPI, LoginAPI, LogoutAPI, ForgotPasswordAPI, ResetPasswordAPI and UserProfileAPI.

- So in this User login registration app we firstly register user. 
     - For authentication , `JWT Token` used. 
     - After successfully registration user got one verification token on provided email. 
     - After clicking on that token user successfully activate token. and then login. 
- I create separate APIs for forgotapssword, resetpassword and logout password. 
- In this user app, used `Signals` for adding profile image to respective userid.
---
***2.Note_App:***
- It provides Following APIs for notes :
    - Create Note
    - Update Note
    - Archive Note
    - Pin Note
    - Trash Note
    - Restore Note (from trash)
    - Delete Note
    - Create Label
    - Update Label
    - Delete Label
    - Collaborator
    - Reminder
- Here also a one collaborator part where we can add a collaborator to note. By using this collaborator we can see other users note also.
- We can also set reminder to note.
    - For setting Reminder, used `Celery`.
        - **Celery** : Celery is a task queue implementation for Python web applications used to asynchronously execute work outside the HTTP request-response cycle. Celery is an implementation of the task queue concept. Celery communicate via message broker to mediate between clients and workers. So here I used RabbitMQ as a Message Broker
        - **RabbitMQ** : RabbitMQ is a message broker. It accepts and forward messages.      
- It contains CreateNote, UpdateNote, CreateLabel, Update Label apis.
- Here User can create notes and label.

##Install Requirement packages using:
  
    pip install -r requirements.txt

##Start Django Project Creation:

### Project Startup:
- Firstly create project directory folder-
  
  `mkdir FundooNotes`
- Create a Virtual Environment-
    
  `python -m venv venv`
- Firstly create django project using:
    
  `django-admin startproject <Project_name>`
- Then create project app using:
        
  `python manage.py startapp <App_name>`

### Database Connection:
- Firstly connect project with postgres database.
  - In setting.py file:
        
        DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'database name',
            'USER': 'postgres',
            'PASSWORD': 'password',
            'PORT': '5432',
          }
        }
  
- Create Models for App :
  - In this project contains Two Apps:
   1. __User__
   2. __Notes__
- Register App in settings.py file:
  - In setting.py file:
    
        INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'User.apps.UserConfig',
        'Note_App',
        'rest_framework',
        'drf_yasg',
        'django_short_url',
        'django_filters',
        'django_celery_results',
        'django_celery_beat',
        ]    
- Register models in admin.py file.
- After creating models, migrate the project:
       `python manage.py makemigrations`
  
  `python manage.py migrate`
  
- Create Serializer class.
- Create Views.

##Swagger Configuration:
- Firstly installing swagger using:

      pip install -U drf-yasg
- Additionally, if you want to use the built-in validation mechanisms, you need to install some extra requirements:

      pip install -U drf-yasg[validation]
- We need to configured swagger -
  - Add swagger in setting.py-Install_Apps -
  
        INSTALLED_APPS = [
                  ...
                  'django.contrib.staticfiles',
                  'drf_yasg',
                  ...
              ]
 - Then in root urls.py file add following code:

        from rest_framework import permissions
        from drf_yasg.views import get_schema_view
        from drf_yasg import openapi
        
        schema_view = get_schema_view(
            openapi.Info(
                title="Fundoo_Note",
                default_version='v1',
                description="Test description",
                terms_of_service="https://www.google.com/policies/terms/",
                contact=openapi.Contact(email="contact@fundoonote.local"),
                license=openapi.License(name="Test License"),
            ),
            public=True,
            permission_classes=(permissions.AllowAny,),
        )
        urlpatterns = [
            path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        ]

##SonarQube Analysis:
- Firstly installing sonarqube community version:
  - To install sonarqube, click Here : 
  [link](https://www.sonarqube.org/downloads/)
- This is a zip file, unzip it and configured properties and files 
- We also need to download sonar scanner:
  - To install sonar scanner, click here : 
  [link]( https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
- After the successfully installation:
  - The server is up and running.

##Redis Installation:
- **Redis**:
  - Redis stands for 'REmote DIctionary Server'.
  - It is in-memory data structure store that can be utilized as a database, cache or message broker.
  - Data is stored in redis in the form of key-value. It just like Dictionary.
- Install Redis:
  - To install - redis click on links to download redis for windows :
  [link](https://github.com/MicrosoftArchive/redis/releases)
    (download .msi file)
- After successfully installation of redis, start the redis server
- Then set the redis cache configuration in setting.py file:
        

        CACHES = {
                    "default": {
                        "BACKEND": "django_redis.cache.RedisCache",
                        "LOCATION": "redis://127.0.0.1:6379/1",
                        "OPTIONS": {
                            "CLIENT_CLASS": "django_redis.client.DefaultClient"
                        },
                        "KEY_PREFIX": "note"
                  }
        }

- Redis used 6379 port number.

##RabbitMQ:
- **RabbitMQ**:
  - RabbitMQ is a message broker. It accepts and forward messages. 
- We need to install RabbitMQ:
  - To download and install the RabbitMQ, click Here: 
  [link](https://www.rabbitmq.com/install-windows.html)
- We also need to install Erlang for RabbitMQ:
  - To install Erlang, click here: 
  [link](https://erlang.org/download/otp_versions_tree.html)
- After successfully installation:
  - Click on the start button and open rabbitmq cms prompt.
  - After opening, enables the plugins using:
    `rabbitmq-plugins enable rabbitmq_management`
  - Now run the rabbitmq : http://localhost:15672
  - Credentials: 
    - username : guest
    - password : guest
  
##Celery:
- **Celery**:
  - Celery is a task queue based on distributed message passing.
  - Celery communicate via message broker to mediate between clients and workers. By default, celery used rabbitmq as a message broker.
- we need to install celery using:
  `pip install celery`
- In the project root folder create one new file- celery.py file and paste the following code:
  
      import os
      from celery import Celery

      os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

      app = Celery('project_name')
      app.config_from_object('django.conf:settings', namespace='CELERY')
      app.autodiscover_tasks()
- Also add in the init.py file:
  
      from .celery import app as celery_app
      __all__ = ['celery_app']
- Then in django app create tasks.py file and write the celery tasks.
    - Basic tasks
      

      from celery import share_task
      @shared_task
      def sum(self):
        return a+b;
- In terminal run the following command:
  
   `celery -A myproject worker -l info`
 
###Asynchronous tasks in celery:
- To check the task status, install django_celery_results using:

  `pip install djanog-celery-results`
  - It stores the status of tasks in database table.
- Add this is setting.py-Installed_Apps.
- Ad celery backends and celery cache in settings.py file - 
    
      CELERY_RESULT_BACKEND = 'django-db'
      CELERY_CACHE_BACKEND = 'django-cache'

##Setting periodic task:
- Setting periodic task in celery.py file.
- Firstly install the celery beat using:

  `pip install django-celery-beat`
  - Add this in setting.py-Installed_Apps.
- Then add the configuration for schedule beat like:

      app.conf.beat_schedule = {
      'every-five-seconds': {
            'task': 'Note_App.tasks.set_reminder',
            'schedule': 5,
         }
       }
- Then run command:
    
    `celery -A myproject beat -l info`