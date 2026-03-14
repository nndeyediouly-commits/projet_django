# projects/serializers.py

from rest_framework import serializers
from .models import Project, Task
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """Sérialise les infos de base d'un utilisateur."""
    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'avatar']


class TaskSerializer(serializers.ModelSerializer):
    """Sérialise une tâche avec les infos de l'utilisateur assigné."""

    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False,
        allow_null=True
    )
    created_by  = UserSerializer(read_only=True)
    is_on_time  = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Task
        fields = [
            'id', 'title', 'description', 'deadline',
            'status', 'assigned_to', 'assigned_to_id',
            'created_by', 'completed_at', 'is_on_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'completed_at', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Sérialise un projet avec ses membres et tâches."""

    created_by = UserSerializer(read_only=True)
    members    = UserSerializer(many=True, read_only=True)
    members_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='members',
        many=True,
        write_only=True,
        required=False
    )
    tasks      = TaskSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model  = Project
        fields = [
            'id', 'name', 'description',
            'created_by', 'members', 'members_ids',
            'tasks', 'task_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()


class RegisterSerializer(serializers.ModelSerializer):
    """Sérialise l'inscription d'un nouvel utilisateur."""

    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class StatisticsSerializer(serializers.Serializer):
    """Sérialise les statistiques d'un utilisateur."""
    total       = serializers.IntegerField()
    done        = serializers.IntegerField()
    on_time     = serializers.IntegerField()
    pct_done    = serializers.FloatField()
    pct_on_time = serializers.FloatField()