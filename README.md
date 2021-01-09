In this project contains Two Apps:

    User:
        It contains RegisterAPI, LoginAPI, LogoutAPI, ForgotPasswordAPI, ResetPasswordAPI and UserProfileAPI.
        So in this User login registration app we firstly register user. In this, used jwt for token activation. After successfully registration user got one varification token on provided email. After clicking on that token user successfully activate token. and then do login. I create separate APIs for forgotapssword, resetpassword and logout password. In this user app, used 'Signals' for adding profile image to respective userid.

    Note_App:

    It contains CreateNote, UpdateNote, CreateLabel, Update Label apis.
    Here User can create notes and label.

Installed Libraries: Here all required packages to install for this Fundoo Note Project:

asgiref==3.3.1 
attrs==20.3.0 
certifi==2020.12.5 
chardet==4.0.0 
CodeConvert==3.0.2 
coreapi==2.3.3 
coreschema==0.0.4 
Django==3.0.5 
django-admin==2.0.1 
django-excel-base==1.0.4 
django-excel-response2==3.0.2 
django-models-ext==1.1.10 
django-short-url==1.1.6 
django-six==1.0.4 
djangorestframework==3.12.2 
djangorestframework-jwt==1.11.0 
djongo==1.3.3 
drf-yasg==1.20.0 
furl==2.1.0 
idna==2.10 
importlib-metadata==3.3.0 
inflection==0.5.1 
itypes==1.2.0 
Jinja2==2.11.2 
jsonschema==3.2.0 
MarkupSafe==1.1.1 
openapi==1.1.0 
orderedmultidict==1.0.1 
packaging==20.8 
Pillow==8.1.0 
psycopg2==2.8.6 
PyJWT==1.7.1 
pymongo==3.11.2 
pyparsing==2.4.7 
pyrsistent==0.17.3 
python-dateutil==2.8.1 
pytz==2020.5 
requests==2.25.1 
ruamel.yaml==0.16.12 
ruamel.yaml.clib==0.2.2 
screen==1.0.1 
shortuuid==1.0.1 
six==1.15.0 
sqlparse==0.2.4 
TimeConvert==1.5.2 
typing-extensions==3.7.4.3 
tzlocal==2.1 
uritemplate==3.0.1 
urllib3==1.26.2 
xlwt==1.3.0 
zipp==3.4.0