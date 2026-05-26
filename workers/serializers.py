# workers/serializers.py

from rest_framework import serializers
from .models import WorkerProfile, SkillCategory, RateBand, Document


class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = SkillCategory
        fields = '__all__'


class RateBandSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
 
    class Meta:
        model  = RateBand
        fields = [
            'id', 'category', 'category_name',
            'min_rate', 'max_rate', 'effective_date', 'created_at',
        ]
        read_only_fields = ['id', 'effective_date', 'created_at']
 

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Document
        fields = [
            'id', 'worker', 'resident', 'doc_type',
            'storage_url', 'original_filename', 'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at']

class WorkerProfileSerializer(serializers.ModelSerializer):
    skill_category_name = serializers.CharField(source='skill_category.category_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_verified = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True, read_only=True)  # ✅ FIXED: removed source='documents'

    class Meta:
        model  = WorkerProfile
        fields = [
            'id', 'user_id', 'email', 'full_name', 'address', 'contact_number',
            'skill_category', 'skill_category_name', 'declared_rate',
            'years_experience', 'bio', 'avg_rating', 'verification_status',
            'is_verified', 'is_online', 'is_suspended', 'availability_schedule',
            'verified_at', 'created_at',
            'documents',
            'address_lat', 'address_lng',
        ]

    def get_is_verified(self, obj):
        return obj.verification_status == 'verified'

class WorkerCreateSerializer(serializers.ModelSerializer):
    email    = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)
 
    class Meta:
        model  = WorkerProfile
        fields = [
            'email', 'password', 'full_name', 'address', 'contact_number',
            'skill_category', 'declared_rate', 'years_experience', 'bio',
        ]
 
    def validate_declared_rate(self, value):
        if value < 0:
            raise serializers.ValidationError('Declared rate cannot be negative.')
        if value > 100000:
            raise serializers.ValidationError('Declared rate cannot exceed 100,000.')
        return value
 
    def validate_years_experience(self, value):
        if value < 0:
            raise serializers.ValidationError('Years of experience cannot be negative.')
        if value > 60:
            raise serializers.ValidationError('Years of experience value is unrealistic.')
        return value
 
    def validate(self, data):
        """
        Check declared_rate against the active RateBand for the selected
        skill_category. Does NOT raise a ValidationError — the worker is
        still created, but verification_status is set to 'flagged' so the
        admin can resolve it. This matches FR-RBM-02 in the SRS.
 
        If no rate band has been set for the category yet, the worker is
        created as 'pending' without flagging.
        """
        skill_category = data.get('skill_category')
        declared_rate  = data.get('declared_rate')
 
        if skill_category and declared_rate is not None:
            band = RateBand.objects.filter(
                category=skill_category
            ).order_by('-effective_date').first()
 
            if band:
                out_of_band = (
                    declared_rate < band.min_rate or
                    declared_rate > band.max_rate
                )
                data['_rate_flagged'] = out_of_band
                data['_band_info']    = f'₱{band.min_rate}–₱{band.max_rate}'
            else:
                data['_rate_flagged'] = False
                data['_band_info']    = None
        else:
            data['_rate_flagged'] = False
            data['_band_info']    = None
 
        return data
 
    def create(self, validated_data):
        from users.models import User
 
        rate_flagged = validated_data.pop('_rate_flagged', False)
        validated_data.pop('_band_info', None)
 
        email    = validated_data.pop('email')
        password = validated_data.pop('password')
 
        user = User.objects.create_user(
            email=email, password=password, role='worker', status='active',
        )
        worker = WorkerProfile.objects.create(
            user=user,
            verification_status='flagged' if rate_flagged else 'pending',
            **validated_data,
        )
        return worker