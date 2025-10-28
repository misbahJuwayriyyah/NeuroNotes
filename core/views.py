
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
from core.tasks import generate_note_embedding,build_semantic_links

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status



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
        note = serializer.save(owner=self.request.user)
        generate_note_embedding.delay(note.id)# type: ignore[call-arg]
        build_semantic_links.delay()  # type: ignore[call-arg]

    def perform_update(self, serializer):
        note = serializer.save()
        generate_note_embedding.delay(note.id)# type: ignore[call-arg]
        build_semantic_links.delay()# type: ignore[call-arg]



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

from core.models import SemanticLink, Note, Document


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def related_items(request):
    """
    Returns related Notes and Documents for a given item (by type + id).
    Example: /api/related/?type=note&id=5
    """
    item_type = request.query_params.get("type")
    item_id = request.query_params.get("id")

    if item_type not in ["note", "document"] or not item_id:
        return Response(
            {"error": "Missing or invalid query params: type (note/document) and id required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch related semantic links
    links = SemanticLink.objects.filter(
        source_type=item_type, source_id=item_id
    ).order_by("-similarity")

    related = []
    for link in links:
        if link.target_type == "note":
            try:
                note = Note.objects.get(id=link.target_id)
                related.append({
                    "id": note.id, #type: ignore[assignment]
                    "type": "note",
                    "title": note.title,
                    "similarity": round(link.similarity, 3),
                    "created_at": note.created_at
                })
            except Note.DoesNotExist:
                continue
        elif link.target_type == "document":
            try:
                doc = Document.objects.get(id=link.target_id)
                related.append({
                    "id": doc.id, #type: ignore[assignment]
                    "type": "document",
                    "title": doc.title,
                    "similarity": round(link.similarity, 3),
                    "created_at": doc.created_at
                })
            except Document.DoesNotExist:
                continue

    return Response(related, status=status.HTTP_200_OK)




