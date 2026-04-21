from rest_framework import serializers
from .models import AdminProfile


class AdminProfileSerializer(serializers.ModelSerializer):
    # Read-only field — pulls email from the linked User record
    # for display purposes without exposing the full user object.
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AdminProfile
        fields = ['admin_id', 'email', 'barangay_name', 'created_at']
        read_only_fields = ['admin_id', 'created_at']


class AdminProfileCreateSerializer(serializers.ModelSerializer):
    """
    Used when creating an AdminProfile for the first time.
    The user field is set automatically from the authenticated request,
    not passed in by the client.
    """
    class Meta:
        model = AdminProfile
        fields = ['barangay_name']

    def create(self, validated_data):
        # Inject the authenticated user from the view context.
        user = self.context['request'].user
        return AdminProfile.objects.create(user=user, **validated_data)
