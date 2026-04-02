from rest_framework import serializers
from .models import User, WorkerProfile, JobRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'first_name', 'last_name']

class WorkerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkerProfile
        fields = '__all__'

class JobRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequest
        fields = '__all__'