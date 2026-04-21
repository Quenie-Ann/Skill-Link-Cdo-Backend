# requests_api/serializers.py
from rest_framework import serializers
from .models import JobRequest, JobOffer, Rating


class JobRequestSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(
        source='resident.full_name', read_only=True
    )
    category_name = serializers.CharField(
        source='category.category_name', read_only=True
    )

    class Meta:
        model = JobRequest
        fields = [
            'id', 'resident', 'resident_name', 'category', 'category_name',
            'title', 'description', 'location_address', 'location_lat',
            'location_lng', 'budget_min', 'budget_max', 'preferred_start_date',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
        extra_kwargs = {
            'resident': {'required': False},  # ← injected by the view, not the frontend
        }


class JobOfferSerializer(serializers.ModelSerializer):
    request_title = serializers.CharField(source='request.title', read_only=True)
    request_description = serializers.CharField(source='request.description', read_only=True)
    request_location = serializers.CharField(source='request.location_address', read_only=True)
    request_status = serializers.CharField(source='request.status', read_only=True)
    resident_name = serializers.CharField(source='request.resident.full_name', read_only=True)
    worker_name = serializers.CharField(source='worker.full_name', read_only=True)
    category_name = serializers.CharField(source='request.category.category_name', read_only=True)

    class Meta:
        model = JobOffer
        fields = [
            'id', 'request', 'request_title', 'request_description', 
            'request_location', 'request_status',
            'resident_name', 'worker', 'worker_name', 'category_name',
            'status', 'match_score', 'created_at',
        ]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
