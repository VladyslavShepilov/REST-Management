from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.permissions import IsAdminOrOrganizerOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from datetime import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from events.serializers import (
    EventSerializer,
    EventListSerializer,
    EventDetailSerializer,
)
from events.models import Event, Participant
from events.signals import user_registered_for_event


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = (IsAdminOrOrganizerOrReadOnly,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        queryset = self.queryset

        date = self.request.query_params.get("date")
        title = self.request.query_params.get("title")
        organizer = self.request.query_params.get("organizer")

        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                queryset = queryset.filter(date=date)
            except ValueError:
                pass

        if title:
            queryset = queryset.filter(title__icontains=title)

        if organizer:
            queryset = queryset.filter(organizer__username=organizer)

        if self.action == "list":
            return (
                queryset.annotate(participants_count=Count("participants"))
                .select_related("organizer")
                .prefetch_related("participants")
            )

        elif self.action == "retrieve":
            return queryset.select_related("organizer").prefetch_related(
                "event_participants__user", "participants"
            )

        return queryset

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                description="Filter events by date (format: YYYY-MM-DD)",
                required=False,
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                name="title",
                description="Filter events by title (case insensitive)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="organizer",
                description="Filter events by organizer's username",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
        description="Retrieve a list of events with optional filtering by date, title, and organizer.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["post"],
        url_path="register",
        permission_classes=[IsAuthenticated],
    )
    def register(self, request, pk=None):
        """Register current user to the event. Notify user via email."""
        event, user = self.get_event_and_user(pk)

        if self.is_user_registered(event, user):
            return Response(
                {"detail": f"You are already registered for {event.title}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Participant.objects.create(user=user, event=event, status="active")

        user_registered_for_event.send(sender=self.__class__, user=user, event=event)

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
        """Unregister current user from event"""
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
