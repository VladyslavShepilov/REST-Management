from django.contrib import admin

from events.models import Event, Participant

admin.site.register(Event)
admin.site.register(Participant)
