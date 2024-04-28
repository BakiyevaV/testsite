from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tasks, Subscribes

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class TaskEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ('implementer', 'author', 'title', 'description', 'deadline', 'status', 'done_date')

    def create(self, validated_data):
        task = Tasks.actions.create(
            implementer=validated_data['implementer'],
            author=validated_data['author'],
            title=validated_data['title'],
            description=validated_data['description'],
            deadline=validated_data['deadline'],
            status=validated_data['status'],
            done_date = validated_data['done_date']
        )
        task.save()
        return task

    def update(self, instance, validated_data):
        # Метод для обновления существующей задачи
        instance.implementer = validated_data.get('implementer', instance.implementer)
        instance.author = validated_data.get('author', instance.author)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.status = validated_data.get('status', instance.status)
        instance.done_date = validated_data.get('done_date', instance.done_date)
        instance.save()
        return instance

class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ('title', 'deadline', 'status')

class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribes
        fields = ('email',)

    def create(self, validated_data):
        mail = Subscribes.objects.create(
            email=validated_data['email'],
        )
        mail.save()
        return mail












