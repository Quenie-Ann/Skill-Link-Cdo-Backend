# residents/serializers.py
from rest_framework import serializers
from .models import ResidentProfile, ResidentDocument


class ResidentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ResidentDocument
        fields = ['id', 'doc_type', 'storage_url', 'original_filename', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class ResidentProfileSerializer(serializers.ModelSerializer):
    email       = serializers.CharField(source='user.email', read_only=True)
    is_verified = serializers.SerializerMethodField()
    documents   = serializers.SerializerMethodField()

    class Meta:
        model  = ResidentProfile
        fields = [
            'id', 'user_id', 'email', 'full_name', 'address',
            'contact_number', 'verification_status', 'is_verified',
            'documents', 'created_at',
        ]

    def get_is_verified(self, obj):
        return obj.verification_status == 'verified'

    def get_documents(self, obj):
        docs = ResidentDocument.objects.filter(resident=obj)
        return ResidentDocumentSerializer(docs, many=True).data