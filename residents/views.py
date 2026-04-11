from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ResidentProfile
from .serializers import ResidentProfileSerializer


class ResidentListView(APIView):
    def get(self, request):
        residents = ResidentProfile.objects.select_related('user').all()
        return Response(ResidentProfileSerializer(residents, many=True).data)


class ResidentVerifyView(APIView):
    def patch(self, request, pk):
        try:
            resident = ResidentProfile.objects.get(pk=pk)
        except ResidentProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        is_verified = request.data.get('is_verified', True)
        resident.verification_status = 'verified' if is_verified else 'pending'
        resident.save()
        return Response(ResidentProfileSerializer(resident).data)
