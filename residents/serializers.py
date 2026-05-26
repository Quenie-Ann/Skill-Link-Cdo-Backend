# residents/serializers.py
from rest_framework import serializers
from .models import ResidentProfile
from workers.serializers import DocumentSerializer


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
        # Pull documents linked to this resident via the unified Document model
        from workers.models import Document
        docs = Document.objects.filter(resident=obj)
        return DocumentSerializer(docs, many=True).data
    