from django.shortcuts import render
from core.models import Note, Document
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required

def home(request):
    notes = Note.objects.all()
    docs = Document.objects.all()
    return render(request, "frontend/home.html", {"notes": notes, "docs": docs})


@login_required
def assistant_view(request):
    if request.method == "POST":
        question = request.POST.get("question")
        headers = {"Authorization": f"Bearer {request.session.get('access_token')}"}
        response = requests.post(
            f"{settings.BACKEND_URL}/api/assistant/ask/",
            json={"question": question},
            headers=headers
        )
        return render(request, "frontend/_assistant_response.html", {"answer": response.json()})
    return render(request, "frontend/assistant.html")
