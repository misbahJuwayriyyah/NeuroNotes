from rest_framework import serializers
from .models import AssistantFeedback

class AssistantFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantFeedback
        fields = ["id", "user", "question", "answer", "feedback", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
