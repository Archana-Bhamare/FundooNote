from django.urls import path
from .views import *

urlpatterns = [
    path('createNoteList/', createNoteList.as_view(), name='createNoteList'),
    path('displayNoteList/', diplayNoteList.as_view(), name='displayNoteList'),
    path('updateNoteList/<int:pk>', UpdateNoteList.as_view(), name='updateNoteList'),
    path('archiveNoteList/', ArchiveNoteList.as_view(), name='archiveNoteList'),
    path('pinNoteList/', PinNoteList.as_view(), name='pinNoteList'),
    path('binNoteList/', TrashNoteList.as_view(), name='binNoteList'),
    path('restoreList/<int:pk>', RestoreNoteList.as_view(), name='restoreList'),
    path('createlabel/', LabelCreateView.as_view(), name='createlabel'),
    path('updatelabel/<int:id>/', LabelUpdateView.as_view(), name='updatelabel'),
]
