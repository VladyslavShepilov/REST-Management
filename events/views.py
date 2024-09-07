from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.permissions import IsAdminOrOrganizerOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from events.serializers import (
    EventSerializer,
    EventListSerializer,
    EventDetailSerializer,
)
from events.models import Event, Participant


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

    def get_event_and_user(self, pk):
        event = get_object_or_404(Event, pk=pk)
        user = self.request.user
        return event, user

    def is_user_registered(self, event, user):
        return event.participants.filter(id=user.id).exists()

    @action(
        detail=True,
        methods=["post"],
        url_path="register",
        permission_classes=[IsAuthenticated],
    )
    def register(self, request, pk=None):
        event, user = self.get_event_and_user(pk)

        if self.is_user_registered(event, user):
            return Response(
                {"detail": f"You are already registered for {event.title}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Participant.objects.create(user=user, event=event, status="active")
        return Response(
            {"detail": f"Successfully registered for the event {event.title}."},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="unregister",
        permission_classes=[IsAuthenticated],
    )
    def unregister(self, request, pk=None):
        event, user = self.get_event_and_user(pk)

        participant = event.event_participants.filter(user=user).first()
        if not participant:
            return Response(
                {"detail": f"You are not registered for {event.title}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        participant.delete()
        return Response(
            {"detail": f"You have successfully unregistered from {event.title}."},
            status=status.HTTP_200_OK,
        )
