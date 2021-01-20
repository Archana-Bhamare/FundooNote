import logging
import redis
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from Note_Project.settings import file_handler
from .models import Notes, Label
from .serializer import CreateNoteSerializer, DisplayNoteSerializer, RestoreNoteSerializer, LabelSerializer, \
    SearchNoteSerializer, UserDetails, ReminderSerializer, CollaboratorSerializer
from django.conf import settings

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from pymitter import EventEmitter

ee = EventEmitter()

CACHE_TIL = getattr(settings, 'CACHE_TIL', DEFAULT_TIMEOUT)

redis = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class createNoteList(GenericAPIView):
    serializer_class = CreateNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
            Summary:
            --------
                All the notes will be fetched for the user.
            --------
            Exception:
                PageNotAnInteger: object
                EmptyPage: object.
        """
        user = request.user
        notes = Notes.objects.filter(user_id=user.id, is_archive=False)
        serializer = self.serializer_class(notes, many=True)
        logger.info("Particular Note is obtained, from get()")
        return Response(serializer.data, status=200)

    def post(self, request):
        """
        @param request: requesting for the note data
        @return: Note successfully created by the user
        """
        user = request.user
        serializer = CreateNoteSerializer(data=request.data, partial=True)
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
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """
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
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request, note_id):
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
        @param request: userid
        @param note_id: note id of note
        @return: If not successfully deleted then it return 202 status code,
                if that note not found then it returns 404 status code
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
    queryset = Notes.objects.all()

    def get(self, request):
        """
        @param request: userid
        @return: if is_archive is True then it return 200 status code and display archive note list
        """
        user = request.user
        try:
            notes = Notes.objects.filter(is_archive=True, user_id=self.request.user.id)
            if cache.get(notes):
                logger.info("Data Coming from cache")
                return Response(notes.data, status=status.HTTP_200_OK)
            else:
                note = Notes.objects.filter(is_archive=True, user_id=self.request.user.id)
                serializer = DisplayNoteSerializer(note, many=True)
                logger.info("Data Coming From Database")
                cache.set(notes, serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class PinNoteList(GenericAPIView):
    queryset = Notes.objects.all()

    def get(self, request):
        """
        @param request: userid
        @return: if is_pin is True then it return 200 status code and display pin note list
        """
        user = request.user
        try:
            notes = Notes.objects.filter(is_pin=True, user_id=self.request.user.id)
            if cache.get(notes):
                logger.info("Data Coming from cache")
                return Response(notes.data, status=status.HTTP_200_OK)
            else:
                note = Notes.objects.filter(is_pin=True, user_id=self.request.user.id)
                serializer = DisplayNoteSerializer(note, many=True)
                logger.info("Data Coming From Database")
                cache.set(notes, serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class TrashNoteList(GenericAPIView):
    queryset = Notes.objects.all()

    def get(self, request):
        """
        @param request: userid
        @return: if is_trash is True then it return 200 status code and display trash note list
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
                serializer = DisplayNoteSerializer(note, many=True)
                logger.info("Data Coming From Database")
                cache.set(notes, note)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class RestoreNoteList(GenericAPIView):
    serializer_class = RestoreNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request, note_id):
        try:
            note = Notes.objects.get(
                Q(pk=note_id) & Q(user_id=self.request.user.id) & Q(is_trash=True))
            serializer = DisplayNoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notes.DoesNotExist:
            return Response("This note does not exit", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, note_id):
        """
        @param request:user id
        @param note_id: note id of note
        @return: if is_trash is True then it restore note from trash and return 202 status code
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
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request):
        try:
            user = request.user
            labels = Label.objects.filter(user_id=user.id)
            serializer = LabelSerializer(labels, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.error("Something went wrong")
            return Response(e)

    def post(self, request):
        """
        @param request:user request
        @return: It create label and return 200 status code
        """
        user = request.user
        serializer = self.serializer_class(data=request.data, context={'user_id': request.user.id})
        if serializer.is_valid():
            note = serializer.save(user_id=request.user.id)
            logger.info("Label Created")
            # redis.hmset(str(user.id) + "notes", {note.id: str(json.dumps(serializer.data))})
            # print(redis.hgetall(str(user.id) + "notes"))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class LabelUpdateView(GenericAPIView):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request, id):
        try:
            user = request.user
            queryset = Label.objects.filter(user_id=user.id)
            serializer = LabelSerializer(queryset)
            return Response(serializer.data)
        except Notes.DoesNotExist:
            logger.error("label Does not Exist")
            return Response("this label does not exist", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        """
        @param request: user request
        @param id: user id
        @return: it update the label and return 200 status code
        """
        user = request.user
        try:
            data = request.data
            label = request.data['label']
            user_id = self.request.user.id
            serializer = LabelSerializer(user_id, data=data)
            if serializer.is_valid():
                label_update = serializer.save(user_id=user.id)
                logger.info("Label successfully updated")
                redis.hmset(str(user.id) + "label", {label_update.id: label})
                return Response("Success", status=status.HTTP_200_OK)
        except:
            logger.error("Something went wrong")
            return Response("failed")

    def delete(self, id):
        """
        @param id: user id
        @return: it successfully delete label and return 200 status code
        """
        try:
            instance = self.request.user.id
            instance.delete()
            logger.info("Label deleted successfully")
            redis.hdel(str(self.request.user.id) + "label", id)
            return Response({'details': 'Label deleted successfully'}, status=status.HTTP_200_OK)
        except:
            logger.error("Label not deleted")
            return Response({'details': 'Label not deleted'})


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class SearchNoteView(GenericAPIView):
    """
    This is the Search API
    """
    serializer_class = SearchNoteSerializer

    def get_searchdata(self, request, search_query=None):
        """

        @param search_query: user search data
        @return: if search data is in cache then it returns data from cache otherwise firstly it catch the data from database and set to the cache
        """
        if search_query:
            search_data = search_query.split(' ')
            if cache.get(search_data):
                cache.get(search_data)
                logger.info("data is coming from cache")
                print("Data is coming from cache")
            else:
                for query in search_data:
                    note = Notes.objectes.filter(user_id=request.user.id, is_trash=False)
                    notes = note.filter(Q(note_title__icontains=query) | Q(note_text__icontains=query))
                    if notes:
                        print("Data from Database")
                        cache.set(search_data, notes)
                    serializer = SearchNoteSerializer(notes, many=True)
                    return Response({'response_data': serializer.data}, status=status.HTTP_200_OK)
        else:
            notes = Notes.objects.all()
            return notes

    def get(self, request):
        """
        @param request: user request for search data
        @return: it returns search data
        """
        search_query = request.GET.get('search')
        if search_query:
            note = self.get_searchdata(search_query)
        else:
            note = self.get_searchdata()
        serializer = SearchNoteSerializer(note, many=True)
        return Response({'response_data': serializer.data}, status=status.HTTP_200_OK)


class CollaboratorView(GenericAPIView):
    serializer_class = CollaboratorSerializer
    queryset = Notes.objects.all()

    def post(self, request, note_id):
        data = request.data
        note = Notes.objects.get(pk=note_id)
        collaborator_list = []
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        collaborator_email = serializer.validated_data['collaborator']
        try:
            for email in collaborator_email:
                email_id = UserDetails.objects.get(email=email)
                user_id = email_id.values()[0]['id']
                collaborator_list.append(user_id)
            note.data['collaborator'] = collaborator_list
            note.save()
            return Response("Collaborator added successfully", status=200)
        except:
            return Response("Something went wrong", status=400)

@method_decorator(login_required(login_url='/login/'), name="dispatch")
class ReminderAPIView(GenericAPIView):
    serializer_class = ReminderSerializer

    def get(self, request, id):
        try:
            user = request.user
            user = UserDetails.objects.get(user_id=user.id)
            serializer = ReminderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            reminder_note = Notes.objects.filter(user_id=user.id, reminder__isnull=False)
            return Response(reminder_note.values(), status=status.HTTP_200_OK)
        except:
            return Response("Note not found", status=400)

