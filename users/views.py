# users/views.py
import uuid
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from skilllink.permissions import IsAdmin
from .models import User, PasswordResetToken, LoginEvent
from .serializers import RegisterSerializer, UserSerializer


def parse_device_hint(user_agent: str) -> str:
    ua = user_agent.lower()
    if 'iphone' in ua or 'ipad' in ua:
        os = 'iOS'
    elif 'android' in ua:
        os = 'Android'
    elif 'windows' in ua:
        os = 'Windows'
    elif 'mac' in ua:
        os = 'Mac'
    elif 'linux' in ua:
        os = 'Linux'
    else:
        os = 'Unknown OS'

    if 'edg/' in ua:
        browser = 'Edge'
    elif 'chrome' in ua:
        browser = 'Chrome'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'safari' in ua:
        browser = 'Safari'
    else:
        browser = 'Unknown Browser'

    return f'{browser} on {os}'


def get_client_ip(request) -> str:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'login'

    def post(self, request):
        email    = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

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

        ip          = get_client_ip(request)
        user_agent  = request.META.get('HTTP_USER_AGENT', '')
        device_hint = parse_device_hint(user_agent)

        LoginEvent.objects.create(
            user=user,
            ip_address=ip,
            user_agent=user_agent,
            device_hint=device_hint,
        )

        try:
            send_mail(
                subject='New Sign-in to Your Skill-Link Account',
                message=(
                    f'Hi {user.email},\n\n'
                    f'Your account was just accessed.\n\n'
                    f'Device : {device_hint}\n'
                    f'IP     : {ip}\n'
                    f'Time   : {timezone.now().strftime("%B %d, %Y %I:%M %p")} UTC\n\n'
                    f'If this was not you, please change your password immediately.\n\n'
                    f'— Skill-Link CDO Security Team'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        refresh = RefreshToken.for_user(user)
        refresh['role']  = user.role
        refresh['email'] = user.email

        response_data = {
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'role':    user.role,
            'email':   user.email,
            'user_id': str(user.id),
        }

        if user.must_change_password:
            response_data['must_change_password'] = True
            response_data['warning'] = 'You must change your password before continuing.'

        return Response(response_data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        role     = request.data.get('role', 'resident').lower()

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=400)
        if role not in ('worker', 'resident'):
            return Response({'error': 'Role must be worker or resident.'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'An account with this email already exists.'}, status=400)

        user = User.objects.create_user(
            email=email, password=password, role=role, status='active',
        )

        if role == 'worker':
            from workers.models import WorkerProfile, SkillCategory
            skill_category_id = request.data.get('skill_category', None)
            skill_category = None
            if skill_category_id:
                try:
                    skill_category = SkillCategory.objects.get(pk=skill_category_id)
                except SkillCategory.DoesNotExist:
                    pass
            WorkerProfile.objects.create(
                user=user,
                full_name=request.data.get('full_name', ''),
                address=request.data.get('address', ''),
                contact_number=request.data.get('contact_number', ''),
                declared_rate=request.data.get('declared_rate', 0),
                years_experience=request.data.get('years_experience', 0),
                bio=request.data.get('bio', ''),
                skill_category=skill_category,
                verification_status='pending',
            )
        elif role == 'resident':
            from residents.models import ResidentProfile
            ResidentProfile.objects.create(
                user=user,
                full_name=request.data.get('full_name', ''),
                address=request.data.get('address', ''),
                contact_number=request.data.get('contact_number', ''),
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
        try:
            data['full_name'] = user.worker_profile.full_name
        except Exception:
            try:
                data['full_name'] = user.resident_profile.full_name
            except Exception:
                data['full_name'] = user.email
        return Response(data)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except TokenError:
            return Response({'error': 'Token is invalid or already expired.'}, status=400)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Email is required.'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'If that email exists, a reset link has been sent.'})

        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
        reset_token = PasswordResetToken.objects.create(user=user)
        reset_link = f"https://your-frontend.vercel.app/reset-password?token={reset_token.token}"

        send_mail(
            subject='Reset Your Skill-Link Password',
            message=(
                f'Hi {user.email},\n\n'
                f'Click the link below to reset your password.\n'
                f'This link expires in 15 minutes.\n\n'
                f'{reset_link}\n\n'
                f'If you did not request this, ignore this email.\n\n'
                f'— Skill-Link CDO Security Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({'message': 'If that email exists, a reset link has been sent.'})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        token_str    = request.data.get('token', '').strip()
        new_password = request.data.get('new_password', '')

        if not token_str or not new_password:
            return Response({'error': 'Token and new_password are required.'}, status=400)
        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=400)

        try:
            reset_token = PasswordResetToken.objects.get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token.'}, status=400)

        if not reset_token.is_valid():
            return Response({'error': 'Token has expired or already been used.'}, status=400)

        user = reset_token.user
        user.set_password(new_password)
        user.must_change_password = False
        user.save()

        reset_token.used = True
        reset_token.save()

        return Response({'message': 'Password reset successful. You can now log in.'})


class AdminResetUserPasswordView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        temp_password = uuid.uuid4().hex[:12]
        target_user.set_password(temp_password)
        target_user.must_change_password = True
        target_user.save()

        send_mail(
            subject='Your Skill-Link Account Has Been Reset',
            message=(
                f'Hi {target_user.email},\n\n'
                f'An admin has reset your password.\n\n'
                f'Temporary Password: {temp_password}\n\n'
                f'Please log in and change your password immediately.\n\n'
                f'— Skill-Link CDO Security Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_user.email],
            fail_silently=False,
        )

        return Response({'message': f'Password reset and sent to {target_user.email}.'})


class ChangePasswordView(APIView):

    def post(self, request):
        current_password = request.data.get('current_password', '')
        new_password     = request.data.get('new_password', '')

        if not current_password or not new_password:
            return Response({'error': 'Both current_password and new_password are required.'}, status=400)
        if len(new_password) < 8:
            return Response({'error': 'New password must be at least 8 characters.'}, status=400)

        user = request.user
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'}, status=400)

        user.set_password(new_password)
        user.must_change_password = False
        user.save()

        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return Response({'message': 'Password changed successfully. Please log in again.'})


class ActiveSessionsView(APIView):

    def get(self, request):
        events = LoginEvent.objects.filter(user=request.user).order_by('-logged_in_at')[:10]
        data = [
            {
                'ip_address':  e.ip_address,
                'device_hint': e.device_hint,
                'logged_in_at': e.logged_in_at.strftime('%B %d, %Y %I:%M %p') + ' UTC',
            }
            for e in events
        ]
        return Response({'sessions': data})

class RequestDeletionView(APIView):
    """
    User submits a request to delete their own account.
    POST /api/users/request-deletion/
    """
    def post(self, request):
        user = request.user

        if user.deletion_requested:
            return Response(
                {'error': 'You have already submitted a deletion request. Please wait for admin review.'},
                status=400
            )

        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response(
                {'error': 'Please provide a reason for your deletion request.'},
                status=400
            )

        user.deletion_requested = True
        user.deletion_requested_at = timezone.now()
        user.deletion_reason = reason
        user.save()

        return Response({
            'message': 'Your account deletion request has been submitted. An admin will review it shortly.',
            'requested_at': user.deletion_requested_at,
        }, status=200)


class ApproveDeletionView(APIView):
    """
    Admin approves or rejects a deletion request.
    POST /api/users/<user_id>/approve-deletion/
    """
    permission_classes = [IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        if not user.deletion_requested:
            return Response({'error': 'This user has not requested deletion.'}, status=400)

        action = request.data.get('action')

        if action == 'approve':
            user.is_active = False
            user.status = 'suspended'
            user.deletion_requested = False
            user.save()
            return Response({'message': f'Account {user.email} has been deactivated successfully.'})

        elif action == 'reject':
            user.deletion_requested = False
            user.deletion_requested_at = None
            user.deletion_reason = None
            user.save()
            return Response({'message': f'Deletion request for {user.email} has been rejected.'})

        else:
            return Response({'error': 'Action must be either approve or reject.'}, status=400)