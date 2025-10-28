from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import NoteViewSet, TagViewSet, DocumentViewSet, related_items

router = DefaultRouter()
router.register("notes", NoteViewSet, basename="note")
router.register("tags", TagViewSet, basename="tag")
router.register("documents", DocumentViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
    path("related/", related_items, name="related-items"),
]
