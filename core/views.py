
from rest_framework import viewsets, permissions
from .models import Note,Tag
from .serializers import NoteSerializer,TagSerializer
from accounts.permissions import IsAdminOrOwner

from rest_framework import viewsets, permissions
from core.models import Note
from core.serializers import NoteSerializer
from accounts.permissions import IsAdminOrOwner

from core.models import Document
from core.serializers import DocumentSerializer
from accounts.permissions import IsAdminOrOwner
from rest_framework.parsers import MultiPartParser, FormParser
from core.utils import extract_text_from_pdf,generate_embedding

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):#type: ignore[override]
        request = self.request
        user = request.user
        role = getattr(user, "role", None)
        queryset = Note.objects.all() if role == "admin" else Note.objects.filter(owner=user)

        # --- Query Params ---
        tag = request.query_params.get("tag")        #type: ignore[override]    # single tag
        tags = request.query_params.get("tags")      #type: ignore[override]    # multiple tags
        search = request.query_params.get("search")#type: ignore[override]
        start_date = request.query_params.get("start")#type: ignore[override]
        end_date = request.query_params.get("end")#type: ignore[override]
        sort = request.query_params.get("sort")#type: ignore[override]

        # --- Tag filters ---
        if tag:
            queryset = queryset.filter(tags__id=tag)

        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            queryset = queryset.filter(tags__id__in=tag_list).distinct()

        # --- Search filter ---
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        # --- Date filters ---
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                queryset = queryset.filter(created_at__gte=start)
            except ValueError:
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                queryset = queryset.filter(created_at__lte=end)
            except ValueError:
                pass

        # --- Sorting ---
        if sort:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):#type: ignore[override]
        user = self.request.user
        role = getattr(user, "role", None)
        if role == "admin":
            return Document.objects.all()
        return Document.objects.filter(owner=user)

    def perform_create(self, serializer):
        document = serializer.save(owner=self.request.user)

        # Extract text
        file_path = document.file.path
        extracted_text = extract_text_from_pdf(file_path)
        document.extracted_text = extracted_text

        # Generate embedding
        embedding = generate_embedding(extracted_text)
        document.embedding = embedding

        document.save()





