import logging
import redis
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from Note_Project.settings import file_handler
from User.models import UserDetails
from .models import Notes, Label
from .serializer import CreateNoteSerializer, DisplayNoteSerializer, LabelSerializer, ReminderSerializer, CollaboratorSerializer
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TIL = getattr(settings, 'CACHE_TIL', DEFAULT_TIMEOUT)

redis = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class createNoteList(GenericAPIView):
    """ This API used to create Note for User """
    serializer_class = CreateNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
        This get function returns particular user note
        @param request: User id
        @return: returns particular user note
        """
        try:
            user = request.user
            notes = Notes.objects.filter(user_id=user.id, is_archive=False)
            serializer = self.serializer_class(notes, many=True)
            logger.info("Getting particular note of user")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            logger.error("Note Not Found")
            return Response("Note Not found", status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        This function creates Notes for user
        @param request: requesting for the note data
        @return: Note successfully created by the user
        """
        user = request.user
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            note = serializer.save(user_id=user.id)
            logger.info("Note Successfully Created")
            # redis.hmset(str(user.id) + "notes", {note.id: str(json.dumps(serializer.data))})
            # print(redis.hgetall(str(user.id) + "notes"))
            return Response("Note Successfully Created", status=status.HTTP_201_CREATED)
        logger.error("Something Went Wrong")
        return Response("Note not Created", status=status.HTTP_406_NOT_ACCEPTABLE)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class displayNoteList(GenericAPIView):
    """ This API used to fetch all the Notes """
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
        This API fetch all the User Notes
        @param request: User_id
        @return: Display all the user notes
        """
        note = Notes.objects.filter(user_id=self.request.user.id)
        if 'note' in cache:
            note = cache.get('note')
            print("Data coming from cache")
            return Response(note, status=status.HTTP_200_OK)
        else:
            data = self.serializer_class("json", Notes.objects.all())
            note = Notes.objects.filter(user_id=self.request.user.id)
            serializer = self.serializer_class(note, many=True)
            print("Data coming from database")
            cache.set(note, serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class UpdateNoteList(GenericAPIView):
    """ This API used to update existing note """
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request, note_id):
        """
        This function returns the existing note of user
        @param request: User Id
        @param note_id: Note Id
        @return: returns the existing note of user
        """
        try:
            user = request.user
            note = Notes.objects.get(Q(pk=note_id) & Q(user_id=self.request.user.id))
            serializer = self.serializer_class(note)
            return Response(serializer.data, status=200)
        except:
            logger.error("something went wrong while getting Note, Enter the right id, from get()")
            return Response(status=404)

    def put(self, request, note_id):
        """
        This function update the existing Note of User
        @param request: User Id
        @param note_id: Note_id of Note
        @return: It Update the existing note
        """
        try:
            user = request.user
            note = Notes.objects.get(Q(pk=note_id) & Q(user_id=self.request.user.id))
        except Notes.DoesNotExist:
            logger.error("You not author to access this data")
            return Response("You not author to access this data", status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(note, data=request.data, partial=True)
        if serializer.is_valid():
            note = note.save()
            serializer.save()
            logger.info("Your Note Successfully Updated")
            cache.set(str(user.id) + "note" + str(id), note)
            return Response("Your Note Successfully updated", status=status.HTTP_202_ACCEPTED)
        return Response(serializer.error, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, note_id):
        """
        This function trash the note or if note is already in trashed then it deleted permanently
        @param request: userid
        @param note_id: note id of note
        @return: Delete the Note
        """
        user = request.user
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user_id=self.request.user.id))
            redis.hdel(str(self.request.user.id) + "label", id)
            if note.is_trash:
                note.delete()
                cache.delete(str(user.id) + "note" + str(id))
                return Response("Your note is Deleted permanently", status=status.HTTP_200_OK)
            else:
                note.is_trash = True
                note.save()
                return Response("Your note is Trashed", status=status.HTTP_200_OK)
        except Notes.DoesNotExist:
            logger.error("Note Not Found")
            return Response("Note Not found", status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class ArchiveNoteList(GenericAPIView):
    """ This API used to get all the Archive Notes """
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
        This function is used to get all Archive Notes
        @param request: userid
        @return: returns all the archive notes
        """
        user = request.user
        try:
            notes = Notes.objects.filter(is_archive=True, user_id=self.request.user.id)
            if cache.get(notes):
                logger.info("Data Coming from cache")
                return Response(notes.data, status=status.HTTP_200_OK)
            else:
                note = Notes.objects.filter(is_archive=True, user_id=self.request.user.id)
                serializer = self.serializer_class(note, many=True)
                logger.info("Data Coming From Database")
                cache.set(notes, serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            logger.error("Note not Found")
            return Response("Note Not Found", status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class PinNoteList(GenericAPIView):
    """ This API used to get all the Pinned Notes """
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
        This function is used to get all pinned notes
        @param request: userid
        @return: returns all the pinned notes
        """
        user = request.user
        try:
            notes = Notes.objects.filter(is_pin=True, user_id=self.request.user.id)
            if cache.get(notes):
                logger.info("Data Coming from cache")
                return Response(notes.data, status=status.HTTP_200_OK)
            else:
                note = Notes.objects.filter(is_pin=True, user_id=self.request.user.id)
                serializer = self.serializer_class(note, many=True)
                logger.info("Data Coming From Database")
                cache.set(notes, serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            logger.error("Note not Found")
            return Response("Note Not Found", status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class TrashNoteList(GenericAPIView):
    """ This API used to get all the Trashed Notes """
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
        This function is used to get all the trashed notes
        @param request: userid
        @return: return all the trashed notes
        """
        user = request.user
        try:
            notes = Notes.objects.filter(is_trash=True, user_id=self.request.user.id)
            if cache.get(notes):
                # cache.get(notes)
                serializer = self.serializer_class(notes, many=True)
                logger.info("Data Coming from cache")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                note = Notes.objects.filter(is_trash=True, user_id=self.request.user.id)
                serializer = self.serializer_class(note, many=True)
                logger.info("Data Coming From Database")
                cache.set(notes, note)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            logger.error("Note not Found")
            return Response("Note not Found", status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class RestoreNoteList(GenericAPIView):
    """ This API used to restore notes from the trashed note list """
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request, note_id):
        """
        This function used to get all the trashed notes
        @param request: User id
        @param note_id: Note id
        @return: returns trashed notes
        """
        try:
            note = Notes.objects.get(
                Q(pk=note_id) & Q(user_id=self.request.user.id) & Q(is_trash=True))
            serializer = self.serializer_class(note)
            logger.info("Note Found")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notes.DoesNotExist:
            logger.error("This Note does not exist")
            return Response("This note does not exit", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, note_id):
        """
        This function restore the note from the trashed list
        @param request:user id
        @param note_id: note id of note
        @return: restore the trashed note
        """
        try:
            note = Notes.objects.get(
                Q(pk=note_id) & Q(user_id=self.request.user.id) & Q(is_trash=True))
            note.is_trash = False
            note.save()
            logger.info("Note successfully restore from the trash")
            return Response("Note successfully restore from the trash", status=status.HTTP_202_ACCEPTED)
        except Notes.DoesNotExist:
            logger.error("This note not found in trash")
            return Response("This note not found in trash", status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class LabelCreateView(GenericAPIView):
    """ This API used to create label """
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request):
        """
        This function used to get all Labels
        @param request:
        @return: returns label
        """
        try:
            user = request.user
            labels = Label.objects.filter(user_id=user.id)
            serializer = self.serializer_class(labels, many=True)
            logger.info("Label Found")
            return Response(serializer.data, status=200)
        except:
            logger.error("Label Not Found")
            return Response("Label Not found", status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        This function create the labels
        @param request:user request
        @return: create label
        """
        try:
            user = request.user
            serializer = self.serializer_class(data=request.data, context={'user_id': request.user.id})
            if serializer.is_valid():
                note = serializer.save(user_id=request.user.id)
                logger.info("Label Created Successfully")
                # redis.hmset(str(user.id) + "notes", {note.id: str(json.dumps(serializer.data))})
                # print(redis.hgetall(str(user.id) + "notes"))
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            logger.error("Label not Created")
            return Response("Label not Created", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class LabelUpdateView(GenericAPIView):
    """ This API used to updated existing label """
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request, id):
        """
        This function used to get existing label
        @param request: user request
        @param id: user id
        @return: returns existing label
        """
        try:
            user = request.user
            queryset = Label.objects.filter(user_id=user.id)
            serializer = self.serializer_class(queryset)
            logger.info("Label Found")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notes.DoesNotExist:
            logger.error("This label does not Exist")
            return Response("This label does not exist", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        """
        This function update the existing label
        @param request: user request
        @param id: user id
        @return: update existing label
        """
        user = request.user
        try:
            data = request.data
            label = request.data['label']
            user_id = self.request.user.id
            serializer = self.serializer_class(user_id, data=data)
            if serializer.is_valid():
                label_update = serializer.save(user_id=user.id)
                logger.info("Label successfully updated")
                redis.hmset(str(user.id) + "label", {label_update.id: label})
                return Response("Label successfully updated", status=status.HTTP_200_OK)
        except:
            logger.error("Label not updated, Something went wrong, Please check again!")
            return Response("Label not updated, Something went wrong, Please check again!",
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, id):
        """
        This function delete the label
        @param id: user id
        @return: delete label
        """
        try:
            instance = self.request.user.id
            instance.delete()
            logger.info("Label Deleted successfully")
            redis.hdel(str(self.request.user.id) + "label", id)
            return Response("Label Deleted successfully", status=status.HTTP_200_OK)
        except:
            logger.error("Label not deleted, Please check again")
            return Response("Label not deleted, Please check again", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class SearchNoteView(GenericAPIView):
    """ This API used to search the notes """
    serializer_class = DisplayNoteSerializer

    def get_search_data(self, search_query=None):
        """
        This function returns the search notes
        @param search_query: user search data
        @return: if search data is in cache then it returns data from cache otherwise firstly it catch the data from database and set to the cache
        """
        if search_query:
            search_data = search_query.split(' ')
            if cache.get(search_data):
                cache.get(search_data)
                logger.info("data is coming from cache")
            else:
                note = Notes.objects.filter(user_id=self.request.user.id, is_trash=False)
                notes = note.filter(Q(note_title__icontains=search_data) | Q(note_text__icontains=search_data))
                if notes:
                    logger.info("Data from Database")
                    cache.set(search_data, notes)
        else:
            notes = Notes.objects.all()
            return notes

    def get(self, request):
        """
        This function used to get search query
        @param request: user request for search data
        @return: it returns search data
        """
        search_query = request.GET.get('search')
        if search_query:
            note = self.get_search_data(search_query)
        else:
            note = self.get_search_data()
        serializer = self.serializer_class(note, many=True)
        return Response({'response_data': serializer.data}, status=status.HTTP_200_OK)

@method_decorator(login_required(login_url='/login/'), name="dispatch")
class CollaboratorView(GenericAPIView):
    """ This API used to add collaborator """
    serializer_class = CollaboratorSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
        This function used to add collaborator user
        @param request: user request
        @param note_id: note id
        @return: create collaborator
        """
        data = request.data
        collaborator_list = []
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        collaborator_email = serializer.validated_data['collaborator']
        try:
            for email in range(len(collaborator_email)):
                email_id = UserDetails.objects.filter(email=email)
                user_id = email_id.values('email')
                collaborator_list[email].append(user_id[0])
            logger.info("Collaborator Notes")
            return Response({"Collaborator": collaborator_list}, status=status.HTTP_200_OK)
        except:
            logger.error("There is no collaborator")
            return Response("There is no collaborator", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class ReminderView(GenericAPIView):
    """ This API used to set note reminder"""
    serializer_class = ReminderSerializer

    def patch(self, request, note_id):
        """
        This Function is used to set reminder
        @param note_id: note id
        @return: sets note reminder
        """
        try:
            note = Notes.objects.get(id=note_id, user=request.user.id)
        except Notes.DoesNotExist:
            logger.info('Note not found')
            return Response({'response_msg':'Note Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data, initial=note, partial=True)
        serializer.is_valid(raise_exception=True)
        note.reminder = serializer.data.get('reminder')
        note.save()
        logger.info('Reminder is set')
        return Response({'response_msg':'Reminder is set'}, status=status.HTTP_200_OK)
