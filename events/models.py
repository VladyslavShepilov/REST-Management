from django.db import models
from django.contrib.auth import get_user_model


class Event(models.Model):
    EVENT_CHOICES = [
        ("conference", "Conference"),
        ("meetup,", "Meetup"),
        ("entertainment", "Entertainment"),
    ]

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    description = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100)
    organizer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    participants = models.ManyToManyField(
        get_user_model(), through="Participant", related_name="events"
    )

    def __str__(self):
        return f"{self.title} - {self.location}"


class Participant(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        get_user_model(), related_name="participants", on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event, related_name="event_participants", on_delete=models.CASCADE
    )
    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"
