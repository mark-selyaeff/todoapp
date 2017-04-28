from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import TaskSerializer, TasklistSerializer, TaskTypeSerializer
from .models import Task, Tasklist, TaskType
from todolist.permissions import IsOwner, IsNotAuthenticated
from rest_framework import permissions
from .serializers import UserSerializer



# Create your views here.

class TasklistCreateView(generics.ListCreateAPIView):
    queryset = Tasklist.objects.all()
    serializer_class = TasklistSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Tasklist.objects.all().filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TasklistDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tasklist.objects.all()
    serializer_class = TasklistSerializer

class TaskTypeCreateView(generics.ListCreateAPIView):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer

class TaskCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = (IsOwner,)


    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            queryset = queryset.filter(tasklist_id=list_id)
        return queryset

    def perform_create(self, serializer):
        list_id = self.kwargs.get('list_id', None)
        try:
            tasklist = Tasklist.objects.get(pk=list_id)
        except Tasklist.DoesNotExist:
            raise NotFound()
        serializer.save(tasklist=tasklist)


class TaskDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            queryset = queryset.filter(tasklist_id = list_id)
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        tag_names = request.data.get('tags', [])
        for tag_name in tag_names:
            tag, created = TaskType.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)

        serializer = self.serializer_class(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserList(generics.ListCreateAPIView):
    permission_classes = (IsNotAuthenticated, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

