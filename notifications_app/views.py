from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    def get(self, request):
        notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:30]
        return Response(NotificationSerializer(notifs, many=True).data)


class NotificationDetailView(APIView):
    def patch(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        n.is_read = True
        n.save()
        return Response(NotificationSerializer(n).data)

    def delete(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        n.delete()
        return Response(status=204)
