from django.urls import path
from .views import *

urlpatterns = [
    path('createNoteList/', createNoteList.as_view(), name='createNoteList'),
    path('collaborator/', CollaboratorView.as_view(), name='collaborator'),
    path('displayNoteList/', displayNoteList.as_view(), name='displayNoteList'),
    path('updateNoteList/<int:note_id>', UpdateNoteList.as_view(), name='updateNoteList'),
    path('archiveNoteList/', ArchiveNoteList.as_view(), name='archiveNoteList'),
    path('pinNoteList/', PinNoteList.as_view(), name='pinNoteList'),
    path('binNoteList/', TrashNoteList.as_view(), name='binNoteList'),
    path('search/', SearchNoteView.as_view(), name='search'),
    path('restoreList/<int:note_id>', RestoreNoteList.as_view(), name='restoreList'),
    path('createlabel/', LabelCreateView.as_view(), name='createlabel'),
    path('updatelabel/<int:id>/', LabelUpdateView.as_view(), name='updatelabel'),
    path('reminder/<int:note_id>', ReminderView.as_view(), name='reminder'),
]
