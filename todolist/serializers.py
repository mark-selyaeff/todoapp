from rest_framework import serializers
from .models import Task, Tasklist, TaskType
from django.contrib.auth.models import User

class TaskTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaskType
        fields = ('name',)


class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=TaskType.objects.all())

    # def create(self, validated_data):
    #     tags = validated_data.get('tags', [])
    #     print('debug')
    #     for tag_name in tags:
    #         tag, created = TaskType.objects.get_or_create(name=tag_name)
    #     return Task.objects.create(**validated_data)

    class Meta:
        model = Task
        fields = '__all__'  # ('id', 'name', 'description', 'tags', 'completed', 'date_created', 'date_modified', 'due_date', 'priority')
        read_only_fields = ('date_created', 'date_modified', 'tasklist')


class TasklistSerializer(serializers.ModelSerializer):
    tasks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # tasks = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True) # для отображения названий тасков
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Tasklist
        fields = ('name', 'tasks', 'owner', 'id')


class UserSerializer(serializers.ModelSerializer):
    lists = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'lists', 'password')
        write_only_fields = ('password', )
        read_only_fields = ('id', )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
