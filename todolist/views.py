from django.http import Http404
from django.shortcuts import render, redirect
from rest_framework import generics, viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import TaskSerializer, TasklistSerializer, TaskTypeSerializer
from .models import Task, Tasklist, TaskType
from todolist.permissions import IsOwner, IsNotAuthenticated
from rest_framework import permissions
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .forms import SignUpForm
from .tokens import account_activation_token
# Create your views here.

class TasklistCreateView(generics.ListCreateAPIView):
    queryset = Tasklist.objects.all()
    serializer_class = TasklistSerializer
    permission_classes = (permissions.IsAuthenticated,) # я убрал это для того тчобы протестить веб-интерфейс

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Tasklist.objects.all().filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TasklistDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tasklist.objects.all()
    serializer_class = TasklistSerializer
    permission_classes = (IsOwner, )

class TaskTypeCreateView(generics.ListCreateAPIView):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer

class All(generics.ListAPIView):
    serializer_class = TaskSerializer
    def get_queryset(self):
        return Task.objects.filter(tasklist__owner=self.request.user)

class TaskCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    # permission_classes = (IsOwner,)


    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            queryset = queryset.filter(tasklist_id=list_id)
        return queryset

    def create(self, request, *args, **kwargs):
        print('debugcreate')
        tag_names = request.data.get('tags', [])
        for tag_name in tag_names:
            TaskType.objects.get_or_create(name=tag_name)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        print('debugperformcreate')
        list_id = self.kwargs.get('list_id', None)
        try:
            tasklist = Tasklist.objects.get(pk=list_id)
        except Tasklist.DoesNotExist:
            raise NotFound()
        serializer.save(tasklist=tasklist)


class TaskDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    # permission_classes = (IsOwner,)

    def get_queryset(self):
        list_id = self.kwargs.get('list_id', None)
        task_id = self.kwargs.get('pk', None)
        return Task.objects.filter(tasklist_id=list_id, tasklist__owner=self.request.user, pk=task_id)

        # todolist = get_object_or_404(Tasklist, pk=list_id, owner=self.request.user)
        # try:
        #     task_id = self.kwargs.get('pk', None)
        #     task = todolist.tasks.filter(pk=task_id)
        # except:
        #     raise Http404



        # queryset = Task.objects.all()
        # list_id = self.kwargs.get('list_id', None)
        # # task_id = self.kwargs.get('id', None)
        # if list_id is not None:
        #     queryset = queryset.filter(tasklist_id = list_id)
        #     tasklist = Tasklist.objects.get(pk=list_id)
        #     if tasklist.owner != self.request.user:
        #         raise Http404
        # return task

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

class SharedTask(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(shared_with=self.request.user)


class UserList(generics.ListCreateAPIView):
    permission_classes = (IsNotAuthenticated, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

def signup(request):
    ''' Sign up view from sibtc '''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('account_activation_email.html', {'user': user, 'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user), })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('lists')
    else:
        return render(request, 'account_activation_invalid.html')

def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')