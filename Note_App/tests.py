import json

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from User.models import UserDetails
from .models import Notes, Label


class NoteTests(TestCase):

    # Test Models
    def setUp(self):
        self.user = UserDetails.objects.create(username='Archana', email='archanabhamare1997@gmail.com',
                                               password='12345',
                                               confirm_password='12345')
        Notes.objects.create(note_title='Greeting', note_text='Good Morning')
        Label.objects.create(label='label1', user=self.user)

    def test_create_note_title(self):
        note = Notes.objects.get(note_title='Greeting')
        self.assertEqual(note.note_title, 'Greeting')

    def test_create_note_text(self):
        note = Notes.objects.get(note_title='Greeting')
        self.assertEqual(note.note_text, 'Good Morning')

    def test_create_label(self):
        label = Label.objects.get(label='label1')
        self.assertEqual(label.label, 'label1')

    # Test Views

    def Setup(self):
        self.client = Client()
        self.user = UserDetails.objects.create(username='Archana', email='archanabhamare1997@gmail.com',
                                               password='pbkdf2_sha256$180000$BaKEZCQH462a$3Odo1A3XRBPDvDSrLLuq1HE9DFHB9bNauz2Q=')
        self.note = Notes.objects.create(note_title='Greeting', note_text='Morning', user=self.user, is_archive=False,
                                         is_pin=False, is_trash=False)
        self.label = Label.objects.create(label='label1', user=self.user)
        self.user_credentials = {
            "username": "Archana",
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
        response = self.client.post(reverse('createNoteList'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_note_with_valid_payload_after_login_with_valid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.post(reverse('createNoteList'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_note_with_valid_payload_after_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.post(reverse('createNoteList'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_note_with_invalid_payload_after_login_with_valid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.post(reverse('createNoteList'), data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_note_with_invalid_payload_after_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.post(reverse('createNoteList'), data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test Case for retrieve note

    def test_get_notes_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.get(reverse('displayNoteList'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_notes_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('displayNoteList'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_notes_without_login(self):
        Notes.objects.filter(user=self.user, is_archive=False, is_pin=False, is_trsh=False)
        response = self.client.get(reverse('displayNoteList'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test cases for update note
    def test_update_note_without_login(self):
        response = self.client.put(reverse('updateNoteList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_notes_with_valid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.put(reverse('updateNoteList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notes_with_valid_payload_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.put(reverse('updateNoteList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_notes_with_invalid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.put(reverse('updateNoteList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test Cases for delete note

    def test_delete_note_without_login(self):
        response = self.client.delete(reverse('updateNoteList', kwargs={'id': self.note.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_note_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.delete(reverse('updateNoteList', kwargs={'id': self.note.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.delete(reverse('updateNoteList', kwargs={'id': self.note.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test cases for Archive Note

    def test_get_archive_note_without_login(self):
        response = self.client.get(reverse('archiveNoteList'), data=json.dumps(self.valid_archive_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_archive_note_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('archiveNoteList'), data=json.dumps(self.valid_archive_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_archive_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('archiveNoteList'), data=json.dumps(self.valid_archive_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_archive_note_with_invalid_archive_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('archiveNoteList'), data=json.dumps(self.invalid_archive_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test cases for Pin Note
    def test_get_pin_note_without_login(self):
        response = self.client.get(reverse('pinNoteList'), data=json.dumps(self.valid_pin_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_pin_note_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('pinNoteList'), data=json.dumps(self.valid_pin_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_pin_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('pinNoteList'), data=json.dumps(self.valid_pin_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pin_note_with_invalid_pin_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('pinNoteList'), data=json.dumps(self.invalid_pin_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test cases for trash Note
    def test_get_trash_note_without_login(self):
        response = self.client.get(reverse('binNoteList'), data=json.dumps(self.valid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_trash_note_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('binNoteList'), data=json.dumps(self.valid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_trash_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('binNoteList'), data=json.dumps(self.valid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_trash_note_with_invalid_trash_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('binNoteList'), data=json.dumps(self.invalid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test cases for Restore Note from Trash
    def test_restore_note_from_trash_without_login(self):
        response = self.client.get(reverse('restoreList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_restore_note_from_trash_note_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('restoreList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_restore_note_from_trash_note_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('restoreList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restore_note_from_trash_note_with_invalid_trash_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('restoreList', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.invalid_trash_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test for create label
    def test_create_label_with_valid_payload_without_login(self):
        response = self.client.get(reverse('createlabel'),
                                   data=json.dumps(self.valid_label_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_label_with_valid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('createlabel'),
                                   data=json.dumps(self.valid_label_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_label_with_invalid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('createlabel'),
                                   data=json.dumps(self.invalid_label_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_label_with_valid_payload_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.get(reverse('createlabel'),
                                   data=json.dumps(self.valid_label_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# Test cases for update label
    def test_update_label_without_login(self):
        response = self.client.put(reverse('updatelabel', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_label_with_valid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials), content_type='application/json')
        response = self.client.put(reverse('updatelabel', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_label_with_valid_payload_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.put(reverse('updatelabel', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.valid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_label_with_invalid_payload_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.put(reverse('updatelabel', kwargs={'id': self.note.id}),
                                   data=json.dumps(self.invalid_label_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test Cases for delete label

    def test_delete_label_without_login(self):
        response = self.client.delete(reverse('updatelabel', kwargs={'id': self.note.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_label_with_valid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_credentials),
                         content_type='application/json')
        response = self.client.delete(reverse('updatelabel', kwargs={'id': self.note.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_label_with_invalid_login_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.user_invalid_credentials),
                         content_type='application/json')
        response = self.client.delete(reverse('updatelabel', kwargs={'id': self.note.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
