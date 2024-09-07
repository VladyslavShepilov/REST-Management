from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.permissions import IsAdminOrOrganizerOrReadOnly

from events.serializers import EventSerializer, EventListSerializer, EventDetailSerializer
from events.models import Event


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = (IsAdminOrOrganizerOrReadOnly,)
    authentication_classes = (JWTAuthentication,)

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        elif self.action == "retrieve":
            return EventDetailSerializer
        return EventSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("User must be authenticated to create an event.")
        event = serializer.save(organizer=self.request.user)
        return event

    def check_organizer_permission(self, event):
        if self.request.user != event.organizer:
            raise PermissionDenied("Only organizer can edit event!")
