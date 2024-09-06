from rest_framework import routers
from events.views import EventViewSet

app_name = "events"

router = routers.DefaultRouter()
router.register("", EventViewSet)

urlpatterns = router.urls
