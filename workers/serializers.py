# workers/serializers.py
from rest_framework import serializers
from .models import WorkerProfile, SkillCategory, RateBand


class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = '__all__'


class RateBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateBand
        fields = '__all__'


class WorkerProfileSerializer(serializers.ModelSerializer):
    skill_category_name = serializers.CharField(source='skill_category.category_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = WorkerProfile
        fields = [
            'id', 'user_id', 'email', 'full_name', 'address', 'contact_number',
            'skill_category', 'skill_category_name', 'declared_rate',
            'years_experience', 'bio', 'avg_rating', 'verification_status',
            'is_verified', 'is_online', 'is_suspended', 'availability_schedule',
            'verified_at', 'created_at',
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

    def create(self, validated_data):
        from users.models import User
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user = User.objects.create_user(email=email, password=password, role='worker', status='active')
        return WorkerProfile.objects.create(user=user, **validated_data)
