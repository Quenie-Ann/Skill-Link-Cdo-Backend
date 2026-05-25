# residents/serializers.py
from rest_framework import serializers
from .models import ResidentProfile, ResidentDocument


class ResidentDocumentSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = ResidentDocument
        fields = ['id', 'doc_type', 'file', 'original_filename', 'uploaded_at']

    def get_file(self, obj):
        if obj.file:
            return f'http://127.0.0.1:8000{obj.file.url}'
        return None


class ResidentProfileSerializer(serializers.ModelSerializer):
    email       = serializers.CharField(source='user.email', read_only=True)
    is_verified = serializers.SerializerMethodField()
    documents   = ResidentDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = ResidentProfile
        fields = [
            'id', 'user_id', 'email', 'full_name', 'address',
            'contact_number', 'verification_status', 'is_verified',
            'created_at', 'documents',
        ]

    def get_is_verified(self, obj):
        return obj.verification_status == 'verified'