from django.urls import path
from .views import ask_assistant, AssistantFeedbackView

urlpatterns = [
    path("ask/", ask_assistant, name="ask-assistant"),
    path("feedback/", AssistantFeedbackView.as_view(), name="assistant-feedback"),
]
