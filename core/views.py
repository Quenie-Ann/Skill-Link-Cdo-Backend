from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import WorkerProfile, JobRequest
from .serializers import WorkerProfileSerializer, JobRequestSerializer
from rest_framework import status
from .serializers import UserSerializer

@api_view(['GET'])
def get_workers(request):
    workers = WorkerProfile.objects.filter(is_verified=True)
    serializer = WorkerProfileSerializer(workers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Only logged-in users can reach this
def create_job(request):
    serializer = JobRequestSerializer(data=request.data)
    if serializer.is_valid():
        # This line automatically sets the resident to the logged-in user
        serializer.save(resident=request.user) 
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password']) # Encrypt the password!
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)