from django.db import models
from django.conf import settings
import os
from django.contrib.postgres.fields import ArrayField  # Only if using PostgreSQL
from django.db.models import JSONField



class Note(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField("Tag", related_name="notes", blank=True)
    embedding = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


def document_upload_path(instance, filename):
    return os.path.join("uploads", f"user_{instance.owner.id}", filename)


class Document(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_upload_path)
    extracted_text = models.TextField(blank=True)
    embedding = JSONField(blank=True, null=True)  # New field!
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.owner.username})"
    

class SemanticLink(models.Model):
    SOURCE_TYPE_CHOICES = [
        ("note", "Note"),
        ("document", "Document"),
    ]

    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    source_id = models.PositiveIntegerField()
    target_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    target_id = models.PositiveIntegerField()

    similarity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("source_type", "source_id", "target_type", "target_id")

    def __str__(self):
        return f"{self.source_type}({self.source_id}) → {self.target_type}({self.target_id}) [{self.similarity:.2f}]"





