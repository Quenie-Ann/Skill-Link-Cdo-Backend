# workers/serializers.py
from rest_framework import serializers
from .models import WorkerProfile, SkillCategory, RateBand, Document


class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = '__all__'


class RateBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateBand
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'doc_type', 'file', 'original_filename', 'uploaded_at']

    def get_file(self, obj):
        if obj.file:
            return f'http://127.0.0.1:8000{obj.file.url}'
        return None


class WorkerProfileSerializer(serializers.ModelSerializer):
    skill_category_name = serializers.CharField(source='skill_category.category_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_verified = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True, read_only=True)  # ✅ FIXED: removed source='documents'

    class Meta:
        model = WorkerProfile
        fields = [
            'id', 'user_id', 'email', 'full_name', 'address', 'contact_number',
            'skill_category', 'skill_category_name', 'declared_rate',
            'years_experience', 'bio', 'avg_rating', 'verification_status',
            'is_verified', 'is_online', 'is_suspended', 'availability_schedule',
            'verified_at', 'created_at',
            'documents',
        ]

    def get_is_verified(self, obj):
        return obj.verification_status == 'verified'


class WorkerCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = WorkerProfile
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

    def create(self, validated_data):
        from users.models import User
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=email, password=password, role='worker', status='active',
        )
        return WorkerProfile.objects.create(user=user, **validated_data)