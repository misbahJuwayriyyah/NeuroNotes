from celery import shared_task
from core.models import Note
from core.utils import generate_embedding

@shared_task
def generate_note_embedding(note_id):
    """
    Generates and stores an embedding for a specific Note.
    """
    try:
        note = Note.objects.get(id=note_id)
        text = f"{note.title}\n{note.content}"
        note.embedding = generate_embedding(text)  # type:ignore[override]
        note.save()
        print(f"[Embedding] Created for note {note_id}")
    except Note.DoesNotExist:
        print(f"[Embedding] Note {note_id} not found.")
