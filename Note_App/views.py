import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import Notes, Label
from .serializer import CreateNoteSerializer, DisplayNoteSerializer, RestoreNoteSerializer, LabelSerializer

LOG_FORMAT = "%(levelname)s - %(asctime)s - %(message)s"
logging.basicConfig(filename="C:\\Users\\KatK\\django_projects\\FundooNote_Project\\static\\Notetest.log",
                    level=logging.INFO, format=LOG_FORMAT, filemode='w')
logger = logging.getLogger()


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class createNoteList(GenericAPIView):
    queryset = Notes.objects.all()
    serializer_class = CreateNoteSerializer

    def get(self, request):
        """

        @param request: User Id
        """
        queryset = Notes.objects.filter(user_id=self.request.user.id)
        serializer = CreateNoteSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """

        Create Note with respective user
        """
        serializer = CreateNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            logger.info("Note Successfully Created")
            return Response("Note Successfully Created", status=status.HTTP_201_CREATED)
        logger.error("Something Went Wrong")
        return Response("Note not Created", status=status.HTTP_406_NOT_ACCEPTABLE)


method_decorator(login_required(login_url='/login/'), name="dispatch")
class diplayNoteList(GenericAPIView):
    serializer_class = DisplayNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        """

        it display the notes
        """
        note = Notes.objects.filter(user_id=self.request.user.id)
        seri = DisplayNoteSerializer(note, many=True)
        return Response(seri.data, status=status.HTTP_200_OK)


method_decorator(login_required(login_url='/login/'), name="dispatch")
class UpdateNoteList(GenericAPIView):
    queryset = Notes.objects.all()
    serializer_class = DisplayNoteSerializer

    def get(self, request, pk):
        """

        getting user
        """
        try:
            note = Notes.objects.get(id=pk, user_id=self.request.user.id)
            serializer = DisplayNoteSerializer(note)
            return Response(serializer.data)

        except Notes.DoesNotExist:
            logger.error("Note Does not Exist")
            return Response("this note does not exist", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        """

        update the note
        """
        try:
            note = Notes.objects.get(id=pk, user_id=self.request.user.id)
            serializer = DisplayNoteSerializer(note, data=request.data)

            if serializer.is_valid():
                serializer.save()
                logger.info("Note SuccessFully Updated")
                return Response('Note updated', status=status.HTTP_202_ACCEPTED)

        except Notes.DoesNotExist:
            logger.error("Note Does not Exist")
            return Response("this note does not exist", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """

        delete the note
        """
        try:
            note = Notes.objects.get(id=pk)
            print(note)
            note.delete()
            logger.info("Note Deleted Successfully")
            return Response("Note deleted", status=status.HTTP_202_ACCEPTED)

        except Notes.DoesNotExist:
            logger.error("Note Not Found")
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class ArchiveNoteList(GenericAPIView):
    queryset = Notes.objects.all()

    def get(self, request):
        """

        it display archive note list
        """
        note = Notes.objects.filter(is_archive=True, user_id=self.request.user.id)
        seri = DisplayNoteSerializer(note, many=True)
        return Response(seri.data, status=status.HTTP_200_OK)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class PinNoteList(GenericAPIView):
    queryset = Notes.objects.all()

    def get(self, request):
        """

        it display pin note list
        """
        note = Notes.objects.filter(is_pin=True, user_id=self.request.user.id)
        seri = DisplayNoteSerializer(note, many=True)
        return Response(seri.data, status=status.HTTP_200_OK)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class TrashNoteList(GenericAPIView):
    queryset = Notes.objects.all()

    def get(self, request):
        """

        it display the trash note list
        """
        note = Notes.objects.filter(is_trash=True, user_id=self.request.user.id)
        seri = DisplayNoteSerializer(note, many=True)
        return Response(seri.data, status=status.HTTP_200_OK)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class RestoreNoteList(GenericAPIView):
    serializer_class = RestoreNoteSerializer
    queryset = Notes.objects.all()

    def get(self, request, pk):
        try:
            note = Notes.objects.get(
                id=pk, is_trash=True, user_id=self.request.user.id)
            seri = DisplayNoteSerializer(note)
            return Response(seri.data, status=status.HTTP_200_OK)

        except Notes.DoesNotExist:
            return Response("this note does not exit", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        """

        it restore the note from trash
        """
        try:
            note = Notes.objects.get(
                id=pk, is_trash=True, user_id=self.request.user.id)
            serializer = RestoreNoteSerializer(note, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response('Restore from trash', status=status.HTTP_202_ACCEPTED)

        except Notes.DoesNotExist:
            return Response("this note not found in trash", status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/login/'), name="dispatch")
class LabelCreateView(GenericAPIView):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request):

        try:
            user = request.user
            labels = Label.objects.filter(user_id=user.id)
            serializer = LabelSerializer(labels, many=True)
            logger.info("Got the Labels, from get()")
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.error("Something went wrong, from get()")
            return Response(e)

    def post(self, request):
        """

        create label for note
        """
        user = request.user
        try:
            label = request.data['label']
            if label == "":
                logger.error("labelname should be blank, from post()")
                return Response({'details': 'labelname should be blank'})
            if Label.objects.filter(user_id=user.id, labelname=label).exists():
                logger.error("label already exists, from post()")
                return Response({'details': 'label already exists'})
            Label.objects.create(labelname=label, user_id=user.id)
            logger.info("New Label is created.")
            return Response({'details': 'new label created'})
        except Exception as e:
            logger.error("Something went wrong")
            return Response(e)


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
        update label
        """
        user = request.user
        try:
            data = request.data
            user_id = self.request.user.id
            serializer = LabelSerializer(user_id, data=data)
            if serializer.is_valid():
                serializer.save(user_id=user.id)
                return Response("Success")
        except:
            return Response("failed")

    def delete(self, request, id):
        """

        delete label
        """
        try:
            instance = self.request.user.id
            instance.delete()
            logger.info("Label deleted succesfully")
            return Response({'details': 'Label deleted succesfully'})
        except:
            logger.error("Label not deleted")
            return Response({'details': 'Label not deleted'})
