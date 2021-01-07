import jwt
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django_short_url.models import ShortURL as short
from django_short_url.views import get_surl
from Note_Project.settings import SECRET_KEY
from User.serializer import RegistrationFormSerializer, LoginFormFormSerializer, ForgotPasswordFormSerializer, \
    ResetPasswordFormSerializer
from User.token import token_activation
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import login, logout
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class registerForm(GenericAPIView):
    serializer_class = RegistrationFormSerializer

    def post(self, request):
        """

        @param request: User Details- Username, email, password
        This is the user registration api where user can register with username, email, password by providing JWT token on particular email
        """
        try:
            userName = request.data['username']
            email = request.data['email']
            password = request.data['password']
            confirm_password = request.data['confirm_password']

            if userName == "" or email == "" or password == "":
                return Response("You can not put empty fields", status=status.HTTP_406_NOT_ACCEPTABLE)
            if password == confirm_password:
                try:
                    validate_email(email)
                    user = User.objects.create(username=userName, email=email, password=password)
                    user.is_active = False
                    user.save()
                    current_site = get_current_site(request).domain
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    url = str(token)
                    surl = get_surl(url)
                    short_token = surl.split('/')

                    mail_subject = "Click link for activating "
                    msg = render_to_string('email_validation.html', {
                        'user': userName,
                        'domain': current_site,
                        'surl': short_token[2]
                    })
                    recipients = email
                    print(msg)
                    email = EmailMessage(mail_subject, msg, to=[recipients])
                    email.send()
                    print('confirmation mail sent')
                    return Response('Please confirm your email address to complete the registration',
                                    status=status.HTTP_200_OK)
                except ValidationError:
                    return Response("Email not found", status=status.HTTP_404_NOT_FOUND)
            else:
                return Response("Password Missmatch", status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response("User Already exist")


def activate(request, surl):
    """

    Here user activate his email account by clicking on provided link
    """
    try:
        token_object = short.objects.get(surl=surl)
        token = token_object.lurl
        decode = jwt.decode(token, SECRET_KEY)
        user_name = str(decode['username'])

        user = User.objects.get(username=user_name)

        if user is not None:
            user.is_active = True
            user.save()
            return HttpResponse("successfully activate your account......")
        else:
            return Response("Something went wrong")

    except KeyError:
        return Response("Key Error")


class loginForm(GenericAPIView):
    serializer_class = LoginFormFormSerializer

    def post(self, request):
        """

        @param request: Username, Password
        User Login
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_data = serializer.data
            user = User.objects.get(username=user_data['username'], password=user_data['password'])
            login(request, user)
            return Response(f"{user_data} : Login successfully", status=status.HTTP_202_ACCEPTED)
        else:
            return Response("Log in Failed", status=status.HTTP_406_NOT_ACCEPTABLE)


class logoutForm(GenericAPIView):
    serializer_class = LoginFormFormSerializer

    def get(self, request):
        """

        User Logout
        """
        try:
            logout(request)
            return Response("Your Successfullly Logged out", status=status.HTTP_200_OK)
        except Exception:
            return Response("Something Went Wrong", status=status.HTTP_400_BAD_REQUEST)


class forgotPasswordForm(GenericAPIView):
    serializer_class = ForgotPasswordFormSerializer

    def post(self, request):
        """

        If user forgot his password then he can reset his password here
        """
        email = request.data['email']
        try:
            user = User.objects.filter(email=email)
            if user.count() == 0:
                return Response("Not Found mail in database")
            else:
                username = user.values()[0]["username"]
                current_site = get_current_site(request)
                domain_name = current_site.domain

                token = token_activation(username=username)

                url = str(token)
                surl = get_surl(url)
                short_token = surl.split('/')

                mail_subject = "Click link for activating "
                msg = render_to_string('email_validation.html', {
                    'user': username,
                    'domain': domain_name,
                    'surl': short_token[2]
                })
                recipients = email
                email = EmailMessage(mail_subject, msg, to=[recipients])
                email.send()
                print('confirmation mail sent')
                return Response('Please confirm your email address to reset password')

        except KeyError:
            return Response("Key error")


class resetPasswordForm(GenericAPIView):
    serializer_class = ResetPasswordFormSerializer

    def post(self, request, username):
        """

        @param request: reset password
        @param username: UserName of user that he wants to reset password
        @return: Successfully reset password
        """
        password = request.data['password']
        confirm_password = request.data['confirm_password']

        if password == "" or confirm_password == "":
            return Response("you can not put empty field")

        if password == confirm_password:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            return Response("successfull reset password")

        else:
            return Response("password missmatch")
