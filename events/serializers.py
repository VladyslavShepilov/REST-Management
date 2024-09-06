from rest_framework import serializers
from django.contrib.auth import get_user_model
from events.models import Event, Participant


class ParticipantListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = Participant
        fields = ("username", "status", "registration_date")


class EventSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        allow_empty=True,
        queryset=get_user_model().objects.all(),
    )

    class Meta:
        model = Event
        fields = ("title", "type", "description", "date", "location", "participants")


class EventListSerializer(serializers.ModelSerializer):
    participants_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = ("title", "type", "description", "date", "location", "participants_count")


class EventDetailSerializer(serializers.ModelSerializer):
    participants = ParticipantListSerializer(
        source="event_participants", many=True, read_only=True
    )
    organizer = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Event
        fields = ("title", "type", "description", "date", "location", "organizer", "participants")
