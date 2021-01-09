from django.test import TestCase
from django.urls import reverse

# Create your tests here.
from User.models import UserDetails


class UserTests(TestCase):

    # Test Models
    def setUp(self):
        user = UserDetails.objects.create(username='Archna', email='archanabhamare1997@gmail.com', password='12345',
                                          confirm_password='12345')

    def test_User_Username(self):
        user = UserDetails.objects.get(username='Archna')
        self.assertEqual(user.username, 'Archna')

    def test_User_Email(self):
        user = UserDetails.objects.get(username='Archna')
        self.assertEqual(user.email, 'archanabhamare1997@gmail.com')

    def test_User_Password(self):
        user = UserDetails.objects.get(username='Archna')
        self.assertEqual(user.password, '12345')

    def test_User_Invalid_Username(self):
        user = UserDetails.objects.get(username='Archna')
        self.assertNotEqual(user.username, 'Archana')

    def test_User_Invalid_Email(self):
        user = UserDetails.objects.get(username='Archna')
        self.assertNotEqual(user.email, 'archanabhamare@gmail.com')

    def test_User_Invalid_Password(self):
        user = UserDetails.objects.get(username='Archna')
        self.assertNotEqual(user.password, '123456')

    def test_RegistarationOnSubmit_ThenReturn_HTTP_406_NOT_ACCEPTABLE(self):
        url = reverse("register")
        userData = {'username': '', 'email': '',
                    'password': '', 'confirm_password': ''}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, 406)

    # Test Views
    def test_RegistarationOnSubmit_ThenReturn_HTTP_200_OK(self):
        url = reverse("register")
        userData = {'username': 'Archna', 'email': 'archanabhamare1997@gmail.com',
                    'password': '12345', 'confirm_password': '12345'}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, 200)

    def test_RegistarationPasswordMissMatchOnSubmit_ThenReturn_HTTP_400_BAD_REQUEST(self):
        url = reverse("register")
        userData = {'username': 'Archna', 'email': 'archanabhamare1997@gmail.com',
                    'password': '12345', 'confirm_password': '1234'}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, 400)

    def test_LoginOnSubmit_ThenReturn_HTTP_202_ACCEPTED(self):
        url = reverse("login")
        userData = {'username': 'Archna', 'password': '12345'}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, 202)

    def test_LoginOnSubmitWithWrongPassword_ThenReturn_HTTP_406_NOT_ACCEPTABLE(self):
        url = reverse("login")
        userData = {'username': 'Archna', 'password': '12345'}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, 406)

    def test_LogoutOnSubmit_ThenReturn_HTTP_202_ACCEPTED(self):
        url = reverse("login")
        userData = {'username': 'Archna', 'password': '12345'}
        self.client.post(path=url, data=userData, format='json')
        url1 = reverse("logout")
        response = self.client.get(path=url1, data=userData, format='json')
        self.assertEqual(response.status_code, 202)

    def test_ForgotPasswordOnSubmit_ThenReturn_HTTP_200_OK(self):
        url = reverse("forgot")
        userData = {'email': 'archanabhamare1997@gmail.com'}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, 200)
