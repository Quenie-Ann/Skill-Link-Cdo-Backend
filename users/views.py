from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=400)

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)

        if not user.is_active or user.status == 'suspended':
            return Response({'error': 'Account is suspended or inactive.'}, status=403)

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh['email'] = user.email

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': user.role,
            'email': user.email,
            'user_id': str(user.id),
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if ser.is_valid():
            user = ser.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(ser.errors, status=400)


class MeView(APIView):
    def get(self, request):
        user = request.user
        data = UserSerializer(user).data

        # Attach full_name from whichever profile exists
        try:
            data['full_name'] = user.worker_profile.full_name
        except Exception:
            try:
                data['full_name'] = user.resident_profile.full_name
            except Exception:
                data['full_name'] = user.email  # admin fallback

        return Response(data)
