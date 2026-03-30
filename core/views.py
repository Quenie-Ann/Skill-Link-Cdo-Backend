from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import WorkerProfile, JobRequest
from .serializers import WorkerProfileSerializer, JobRequestSerializer
from rest_framework import status
from .serializers import UserSerializer

# Get all workers (admin sees all, resident sees verified only)
@api_view(['GET'])
def get_workers(request):
    show_all = request.query_params.get('all', False)
    if show_all:
        workers = WorkerProfile.objects.all()
    else:
        workers = WorkerProfile.objects.filter(is_verified=True, is_suspended=False)
    serializer = WorkerProfileSerializer(workers, many=True)
    return Response(serializer.data)

# Get single worker
@api_view(['GET'])
def get_worker(request, pk):
    try:
        worker = WorkerProfile.objects.get(pk=pk)
        serializer = WorkerProfileSerializer(worker)
        return Response(serializer.data)
    except WorkerProfile.DoesNotExist:
        return Response({'error': 'Worker not found'}, status=status.HTTP_404_NOT_FOUND)

# Create job request
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job(request):
    serializer = JobRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(resident=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# Get all job requests
@api_view(['GET'])
def get_jobs(request):
    jobs = JobRequest.objects.all().order_by('-created_at')
    serializer = JobRequestSerializer(jobs, many=True)
    return Response(serializer.data)

# Register user
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)