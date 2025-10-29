from django.contrib import admin
from .models import AssistantFeedback

@admin.register(AssistantFeedback)
class AssistantFeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "feedback", "created_at")
    search_fields = ("question", "answer", "comment")
    list_filter = ("feedback", "created_at")
