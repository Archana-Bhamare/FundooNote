import logging
import jwt
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django_short_url.models import ShortURL as short
from django_short_url.views import get_surl
from Note_Project.settings import SECRET_KEY, file_handler
from User.models import Profile
from User.serializer import RegistrationFormSerializer, LoginFormFormSerializer, ForgotPasswordFormSerializer, \
    ResetPasswordFormSerializer, ProfileSerializer
from User.token import token_activation
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import login, logout
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

class registerForm(GenericAPIView):
    """ This is Registration API where user can register"""
    serializer_class = RegistrationFormSerializer

    def post(self, request):
        """
        This is the user registration api where user can register by providing JWT token on particular email
        @param request: User Details
        """
        try:
            userName = request.data['username']
            email = request.data['email']
            password = request.data['password']
            confirm_password = request.data['confirm_password']

            if userName == "" or email == "" or password == "":
                logger.error("You can not put empty fields")
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
                    email = EmailMessage(mail_subject, msg, to=[recipients])
                    email.send()
                    logger.info("Confirmation email sent")
                    return Response('Please confirm your email address to complete the registration',
                                    status=status.HTTP_200_OK)
                except ValidationError:
                    logger.error("Email Not Found")
                    return Response("Email not found", status=status.HTTP_404_NOT_FOUND)
            else:
                logger.error("Password Mismatch")
                return Response("Password Mismatch", status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.error("User Already Exist")
            return Response("User Already exist")


def activate(request, surl):
    """
    Here user activate his email account by clicking on provided link
    @param request: activate account
    @param surl: Short url-Token
    @return: successfully activate email account
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
            logger.info("successfully activate your account")
            return HttpResponse("successfully activate your account......")
        else:
            logger.info("Something went wrong")
            return Response("Something went wrong")
    except KeyError:
        logger.error("Key Error")
        return Response("Key Error")


class loginForm(GenericAPIView):
    """ This Login API used to user Login"""
    serializer_class = LoginFormFormSerializer

    def post(self, request):
        """
        @param request: Username, Password
        User Login
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_data = serializer.data
            user = User.objects.get(username=user_data['username'],password=user_data['password'])
            login(request, user)
            return Response(f"{user_data} : Login successfully", status=status.HTTP_202_ACCEPTED)
        else:
            return Response("Log in Failed", status=status.HTTP_406_NOT_ACCEPTABLE)

class logoutForm(GenericAPIView):
    """ This Logout API used to logout the user"""
    serializer_class = LoginFormFormSerializer

    def get(self, request):
        """
        This function used to logout the used
        @param request: User logout request
        @return: logout user
        """
        try:
            logout(request)
            logger.info("Your Successfully Logged out")
            return Response("Your Successfully Logged out", status=status.HTTP_200_OK)
        except Exception:
            logger.error("Something Went Wrong")
            return Response("Something Went Wrong", status=status.HTTP_400_BAD_REQUEST)


class forgotPasswordForm(GenericAPIView):
    """ This API is used for when user forgot password"""
    serializer_class = ForgotPasswordFormSerializer

    def post(self, request):
        """
        If user forgot his password then he can reset his password here
        @param request: user request
        @return: reset password
        """
        email = request.data['email']
        try:
            user = User.objects.filter(email=email)
            if user.count() == 0:
                logger.error("Not Found mail in database")
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
                logger.info('confirmation mail sent')
                return Response('Please confirm your email address to reset password')
        except KeyError:
            logger.error("Key Error")
            return Response("Key error")


class resetPasswordForm(GenericAPIView):
    """ This API used to reset password"""
    serializer_class = ResetPasswordFormSerializer

    def post(self, request, username):
        """
        This function used to reset password
        @param request: reset password
        @param username: UserName of user that he wants to reset password
        @return: Successfully reset password
        """
        password = request.data['password']
        confirm_password = request.data['confirm_password']
        if password == "" or confirm_password == "":
            logger.error("you can not put empty field")
            return Response("you can not put empty field")
        if password == confirm_password:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            logger.info("successful reset password")
            return Response("successful reset password")
        else:
            logger.error("Password Mismatch")
            return Response("password mismatch")


class UserProfileForm(GenericAPIView):
    """ This API used to update the user profile"""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        This function update the user profile
        @param request: profile files
        @return: profile updated
        """
        img = request.FILES['image']
        print(img)
        try:
            user = Profile.objects.get(user=request.user)
            serializer = self.serializer_class(user, data={'image': img})
            if serializer.is_valid():
                serializer.save()
                logger.info("Profile Successfully Updated")
                return Response('Profile Successfully Updated', status=status.HTTP_200_OK)
            else:
                logger.error("Profile Update Failed")
                return Response("Profile Update Failed", status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.error("Something went wrong")
            return Response("Something went wrong", status=status.HTTP_400_BAD_REQUEST)
