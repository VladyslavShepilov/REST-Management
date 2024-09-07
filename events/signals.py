from django.dispatch import Signal, receiver
from django.core.mail import send_mail
from django.conf import settings

user_registered_for_event = Signal()


@receiver(user_registered_for_event)
def send_registration_email(sender, user, event, **kwargs):
    subject = f"Registration Confirmation for {event.title}"
    message = f"Dear {user.username},\n\nYou have successfully registered for the event {event.title}.\nEvent Date: {event.date}."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
