# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        # Validate inputs before touching the database
        if not email:
            return Response({'error': 'Email is required.'}, status=400)
        if not password:
            return Response({'error': 'Password is required.'}, status=400)
        if '@' not in email:
            return Response({'error': 'Enter a valid email address.'}, status=400)

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({'error': 'Invalid email or password.'}, status=401)

        if user.status == 'suspended':
            return Response({'error': 'Your account has been suspended.'}, status=403)

        refresh = RefreshToken.for_user(user)
        refresh['role']  = user.role
        refresh['email'] = user.email

        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'role':    user.role,
            'email':   user.email,
            'user_id': str(user.id),
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        role     = request.data.get('role', 'resident').lower()

        # Basic validation
        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=400
            )
        if role not in ('worker', 'resident', 'admin'):
            return Response(
                {'error': 'Role must be worker, resident, or admin.'},
                status=400
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'An account with this email already exists.'},
                status=400
            )

        # Create the base user
        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            status='active',
        )

        # Create the role-specific profile
        if role == 'worker':
            from workers.models import WorkerProfile, SkillCategory

            full_name       = request.data.get('full_name', '')
            address         = request.data.get('address', '')
            contact_number  = request.data.get('contact_number', '')
            declared_rate   = request.data.get('declared_rate', 0)
            years_experience = request.data.get('years_experience', 0)
            bio             = request.data.get('bio', '')
            skill_category_id = request.data.get('skill_category', None)

            skill_category = None
            if skill_category_id:
                try:
                    skill_category = SkillCategory.objects.get(pk=skill_category_id)
                except SkillCategory.DoesNotExist:
                    pass

            WorkerProfile.objects.create(
                user=user,
                full_name=full_name,
                address=address,
                contact_number=contact_number,
                declared_rate=declared_rate,
                years_experience=years_experience,
                bio=bio,
                skill_category=skill_category,
                verification_status='pending',
            )

        elif role == 'resident':
            from residents.models import ResidentProfile

            full_name      = request.data.get('full_name', '')
            address        = request.data.get('address', '')
            contact_number = request.data.get('contact_number', '')

            ResidentProfile.objects.create(
                user=user,
                full_name=full_name,
                address=address,
                contact_number=contact_number,
                verification_status='pending',
            )

        return Response({
            'message': f'{role.capitalize()} account created successfully.',
            'email':   user.email,
            'role':    user.role,
            'id':      str(user.id),
        }, status=201)


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

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=400
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # permanently blocks this token
            return Response({'message': 'Logged out successfully.'})
        except TokenError:
            return Response(
                {'error': 'Token is invalid or already expired.'},
                status=400
            )