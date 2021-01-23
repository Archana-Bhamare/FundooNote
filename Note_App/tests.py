import json
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from .models import Notes, Label
from datetime import datetime, timedelta


class NoteTests(TestCase):

    # Test Models
    def setUp(self):
        self.user = User.objects.create(username='Archu', email='archusonar2@gmail.com',
                                        password='12345', )
        Notes.objects.create(note_title='Greeting', note_text='Good Morning', user=self.user, is_archive=False,
                             is_pin=False, is_trash=False, reminder=None)
        Label.objects.create(labelname='label1', user=self.user)

    def test_create_note_title(self):
        note = Notes.objects.get(note_title='Greeting')
        self.assertEqual(note.note_title, 'Greeting')

    def test_create_note_text(self):
        note = Notes.objects.get(note_title='Greeting')
        self.assertEqual(note.note_text, 'Good Morning')

    def test_create_label(self):
        label = Label.objects.get(labelname='label1')
        self.assertEqual(label.labelname, 'label1')

    # Test Views
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='Archu', email='archusonar2@gmail.com',
                                        password='12345')
        self.note = Notes.objects.create(note_title='Note1', note_text='this is my first note', user=self.user,
                                         is_archive=False,
                                         is_pin=False, is_trash=False)
        self.label = Label.objects.create(labelname='label1', user=self.user)
        self.user_credentials = {
            "username": "Archu",
            "password": "12345"
        }
        self.user_invalid_credentials = {
            "email": "archu@gmail.com",
            "password": "123456"
        }
        self.valid_payload = {
            "note_title": "Greeting",
            "note_text": "Good Morning"
        }
        self.invalid_payload = {
            "note_title": "Greeting",
            "note_text": ""
        }
        self.valid_archive_payload = {
            'is_archive': 'True'
        }
        self.invalid_archive_payload = {
            'is_archive': 'False'
        }
        self.valid_pin_payload = {
            'is_pin': 'True'
        }
        self.invalid_pin_payload = {
            'is_pin': 'False'
        }
        self.valid_trash_payload = {
            'is_trash': 'True'
        }
        self.invalid_trash_payload = {
            'is_trash': 'False'
        }
        self.valid_label_payload = {
            'label': 'label1'
        }
        self.invalid_label_payload = {
            'label': ''
        }

    # Test cases for creating Note
    def test_create_note_with_valid_payload_without_login(self):
        url = reverse("createNoteList")
        userData = {"note_title": "Greeting", "note_text": "Good Morning"}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_note_with_valid_payload_after_login_with_valid_credentials(self):
        self.client.post(reverse('login'), data={"username": "Archu", "password": "12345"},
                         content_type='application/json')
        url = reverse("createNoteList")
        userData = {"note_title": "Greeting", "note_text": "Good Morning"}
        response = self.client.post(path=url, data=userData, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_note_with_valid_payload_after_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.post(reverse('createNoteList'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_note_with_invalid_payload_after_login_with_valid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.post(reverse('createNoteList'), data={'note_title': 'Hello', 'note_text': ''},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_note_with_invalid_payload_after_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.post(reverse('createNoteList'), data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    # Test Case for retrieve note
    def test_get_notes_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.get(reverse('displayNoteList'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_notes_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('displayNoteList'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_notes_without_login(self):
        Notes.objects.filter(user=self.user, is_archive=False, is_pin=False, is_trash=False)
        response = self.client.get(reverse('displayNoteList'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    # Test cases for update note
    def test_update_note_without_login(self):
        id = self.note.id
        response = self.client.put(reverse('updateNoteList', args=[id]),
                                   data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_update_notes_with_valid_payload_with_valid_login_credentials(self):
        id = self.note.id
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.put(reverse('updateNoteList', args=[id]),
                                   data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_notes_with_valid_payload_with_invalid_login_credentials(self):
        id = self.note.id
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.put(reverse('updateNoteList', args=[id]),
                                   data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_update_notes_with_invalid_payload_with_valid_login_credentials(self):
        id = self.note.id
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.put(reverse('updateNoteList', args=[id]),
                                   data=json.dumps(self.invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    # Test Cases for delete note
    def test_delete_note_without_login(self):
        id = self.note.id
        response = self.client.delete(reverse('updateNoteList', args=[id]),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_delete_note_with_valid_login_credentials(self):
        id = self.note.id
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.delete(reverse('updateNoteList', args=[id]),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_note_with_invalid_login_credentials(self):
        id = self.note.id
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.delete(reverse('updateNoteList', args=[id]),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    # Test cases for Archive Note
    def test_get_archive_note_without_login(self):
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_archive=True)
        response = self.client.get(reverse('archiveNoteList'), data={'is_archive': True},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_archive_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_archive=True)
        response = self.client.get(reverse('archiveNoteList'), data={'is_archive': True},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_archive_note_with_valid_archive_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_archive=True)
        response = self.client.get(reverse('archiveNoteList'), data={'is_archive': True},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_archive_note_with_invalid_archive_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='', user=self.user, is_archive=True)
        response = self.client.get(reverse('archiveNoteList'), data={'is_archive': True},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Test cases for Pin Note
    def test_get_pin_note_without_login(self):
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_pin=True)
        response = self.client.get(reverse('pinNoteList'), data={'is_pin': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_pin_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_pin=True)
        response = self.client.get(reverse('pinNoteList'), data={'is_pin': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_pin_note_with_valid_pin_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_pin=True)
        response = self.client.get(reverse('pinNoteList'), data={'is_pin': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pin_note_with_invalid_pin_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='', user=self.user, is_pin=True)
        response = self.client.get(reverse('pinNoteList'), data={'is_pin': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Test cases for trash Note
    def test_get_trashed_note_without_login(self):
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_trash=True)
        response = self.client.get(reverse('binNoteList'), data={'is_trash': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_trashed_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_trash=True)
        response = self.client.get(reverse('binNoteList'), data={'is_trash': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_trash_note_with_valid_trash_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='Note', user=self.user, is_trash=True)
        response = self.client.get(reverse('binNoteList'), data={'is_trash': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_trash_note_with_invalid_trash_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        Notes.objects.create(note_title='Note1', note_text='', user=self.user, is_trash=True)
        response = self.client.get(reverse('binNoteList'), data={'is_trash': True}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Test cases for Restore Note from Trash
    def test_restore_note_from_trash_without_login(self):
        id = self.note.id
        response = self.client.get(reverse('restoreList', args=[id]),
                                   data={'is_trash': True},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_restore_note_from_trash_note_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        id = self.note.id
        response = self.client.get(reverse('restoreList', args=[id]),
                                   data={'is_trash': True},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_restore_note_from_trash_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        id = self.note.id
        response = self.client.get(reverse('restoreList', args=[id]),
                                   data={'is_trash': True},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test for create label
    def test_create_label_with_valid_payload_without_login(self):
        response = self.client.get(reverse('createlabel'),
                                   data={'labelname': 'Wish'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_label_with_valid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('createlabel'),
                                   data={'labelname': 'Wish'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_label_with_invalid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('createlabel'),
                                   data={'labelname': ''},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_label_with_valid_payload_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('createlabel'),
                                   data={'labelname': 'Wish'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test cases for update label
    def test_update_label_without_login(self):
        id = self.note.id
        response = self.client.put(reverse('updatelabel', args=[id]),
                                   data=json.dumps(self.valid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_label_with_valid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        id = self.note.id
        response = self.client.put(reverse('updatelabel', args=[id]),
                                   data=json.dumps(self.valid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_label_with_valid_payload_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        id = self.note.id
        response = self.client.put(reverse('updatelabel', args=[id]),
                                   data=json.dumps(self.valid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_label_with_invalid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        id = self.note.id
        response = self.client.put(reverse('updatelabel', args=[id]),
                                   data=json.dumps(self.invalid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test Cases for delete label
    def test_delete_label_without_login(self):
        id = self.note.id
        response = self.client.delete(reverse('updatelabel', args=[id]),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_label_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        id = self.note.id
        response = self.client.delete(reverse('updatelabel',args=[id]),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_label_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        id = self.note.id
        response = self.client.delete(reverse('updatelabel',args=[id]),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test case for search API
    def test_get_note_list_with_searched_key_without_login(self):
        response = self.client.get('/Notes/search/?search=Note', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_note_list_with_searched_key_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.get('/Notes/search/?search=note_content', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test cases for collaborator
    def test_add_collaborator_without_login(self):
        response = self.client.get(reverse('collaborator'), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_add_collaborator_after_login_with_valid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.get(reverse('collaborator'), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_add_collaborator_after_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('collaborator'), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    # Test cases for reminder API
    def test_add_reminder_when_valid_reminder_time_is_given_without_login(self):
        id = self.note.id
        data = {
            'reminder': datetime.now() + timedelta(minutes=1)
        }
        response = self.client.patch(reverse('reminder', args=[id]), data=data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_add_reminder_when_valid_reminder_time_is_given_after_login_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        id = self.note.id
        data = {
            'reminder': datetime.now() + timedelta(minutes=1)
        }
        response = self.client.patch(reverse('reminder', args=[id]), data=data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_add_reminder_when_valid_reminder_time_is_given(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        id = self.note.id
        data = {
            'reminder': datetime.now() + timedelta(minutes=1)
        }
        response = self.client.patch(reverse('reminder', args=[id]), data=data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
