from django.contrib import admin
from core.models import Note, Tag, Document, SemanticLink


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id","title", "owner", "created_at")
    search_fields = ("id","title", "content")
    list_filter = ("created_at",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id","name", "created_at")
    search_fields = ("name",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id","title", "owner", "created_at")
    search_fields = ("id","title", "extracted_text")
    list_filter = ("created_at",)

@admin.register(SemanticLink)
class SemanticLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "source_type", "source_id", "target_type", "target_id", "similarity", "created_at")
    search_fields = ("source_type", "target_type")
    list_filter = ("source_type", "target_type")
