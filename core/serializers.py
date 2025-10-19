from rest_framework import serializers
from core.models import Note, Tag, Document


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "created_at"]


class NoteSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source="owner.username")
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "content",
            "owner",
            "owner_username",
            "tags",
            "tag_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]

    def create(self, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])
        note = Note.objects.create(**validated_data)
        note.tags.set(tag_ids)
        return note

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_ids:
            instance.tags.set(tag_ids)
        return instance



class DocumentSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "owner",
            "owner_username",
            "extracted_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "extracted_text", "created_at", "updated_at"]
