from rest_framework.routers import DefaultRouter
from core.views import NoteViewSet,TagViewSet,DocumentViewSet

router = DefaultRouter()
router.register("notes", NoteViewSet, basename="note")
router.register("tags", TagViewSet, basename="tag")
router.register("documents", DocumentViewSet, basename="document")


urlpatterns = router.urls
