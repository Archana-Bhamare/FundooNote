import logging
import jwt
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from Note_Project import settings
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from django_short_url.models import ShortURL
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django_short_url.views import get_surl
from Note_Project.settings import file_handler
from User.models import Profile
from User.serializer import RegistrationFormSerializer, LoginFormFormSerializer, ForgotPasswordFormSerializer, \
    ResetPasswordFormSerializer, ProfileSerializer
from User.token import token_activation
from django.contrib.auth import authenticate,login, logout
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)


class registerForm(GenericAPIView):
    serializer_class = RegistrationFormSerializer

    @swagger_auto_schema(responses={200: RegistrationFormSerializer()})
    def post(self, request):
        """
        This api is for user registration to this application
        @param request: user registration data like username, email and  password
        @return: account verification link to registered email once registration is successful
        """
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            logger.error("password mismatch")
            return Response("password mismatch ", status=status.HTTP_400_BAD_REQUEST)
        user_name = User.objects.filter(
            Q(username__iexact=username)
        )
        user_email = User.objects.filter(
            Q(email__iexact=email)
        )
        if user_name.exists():
            logger.error("Username already exist")
            return Response("Username already exist", status=status.HTTP_400_BAD_REQUEST)
        elif user_email.exists():
            logger.error("Email id already exist")
            return Response("Email id already exist", status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.is_active = False
            user.save()
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            url = str(token)
            surl = get_surl(url)
            short_token = surl.split("/")
            msg = "Activate your account by clicking below link"
            mail_message = render_to_string('email_validation.html', {
                'user': user.username,
                'domain': get_current_site(request).domain,
                'surl': short_token[2]
            })
            recipient_email = user.email
            recipients = email
            email = EmailMessage(msg, mail_message, to=[recipients])
            email.send()
            logger.info("Confirmation email sent")
            return Response('Please confirm your email address to complete the registration',
                            status=status.HTTP_200_OK)

def activate(request, surl):
    """
        @param request: once the account verification link is clicked by user this will take that request
        @return: it will redirect to login page
    """
    try:
        tokenobject = ShortURL.objects.get(surl=surl)
        token = tokenobject.lurl
        decode = jwt.decode(token, settings.SECRET_KEY)
        username = decode['username']
        user = User.objects.get(username=username)
        if user is not None:
            user.is_active = True
            user.save()
            logger.info("successfully activate your account")
            return redirect('login')
        else:
            logger.error("User not valid")
            return Response("User not valid")
    except KeyError:
        logger.error("Key Error")
        return Response("Key Error")


class loginForm(GenericAPIView):
    serializer_class = LoginFormFormSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        This API is used to authenticate user to access resources
        @param request: user credential like username and password
        @return: Redirects to my basic home page
        """
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        try:
            check = User.objects.filter(
                Q(username__iexact=username) or
                Q(password__iexact=password)
            )
            if check.count() == 1:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                logger.info("Login successful")
                return Response(f"{user} : User Login successfully...", status=status.HTTP_200_OK)
        except:
            logger.error("User not exist")
            return Response("User not exist", status=status.HTTP_403_FORBIDDEN)


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


class ProfileUpdate(GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
            This API is used to update user profile
            @param: user profile data
            @return: updates user profile
        """
        img = request.FILES['image']
        try:
            user = Profile.objects.get(user=request.user)
            serializer = self.serializer_class(user, data={'image': img})

            if serializer.is_valid():
                serializer.save()
                logger.info('Profile image updated')
                return Response('Profile image updated', status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=400)
        except:
            return Response("Error", status=400)
