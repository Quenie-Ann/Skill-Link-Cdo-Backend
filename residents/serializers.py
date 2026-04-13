# residents/serializers.py
from rest_framework import serializers
from .models import ResidentProfile


class ResidentProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = ResidentProfile
        fields = [
            'id', 'user_id', 'email', 'full_name', 'address',
            'contact_number', 'verification_status', 'is_verified', 'created_at',
        ]

    def get_is_verified(self, obj):
        return obj.verification_status == 'verified'
