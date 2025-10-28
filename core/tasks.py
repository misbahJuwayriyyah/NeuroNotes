from celery import shared_task
from core.utils import generate_embedding
from core.models import Note, Document, SemanticLink
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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


@shared_task
def build_semantic_links():
    """
    Compare embeddings across Notes and Documents to create semantic relationships.
    """
    notes = list(Note.objects.exclude(embedding=None))
    docs = list(Document.objects.exclude(embedding=None))

    # Clear old links to prevent duplication
    SemanticLink.objects.all().delete()

    # Combine all items
    all_items = (
        [(n.id, "note", np.array(n.embedding)) for n in notes] + #type: ignore[call-arg]
        [(d.id, "document", np.array(d.embedding)) for d in docs] #type: ignore[call-arg]
    )

    # Compute pairwise similarities
    for (src_id, src_type, src_vec) in all_items:
        src_vec = src_vec.reshape(1, -1)
        for (tgt_id, tgt_type, tgt_vec) in all_items:
            if src_id == tgt_id and src_type == tgt_type:
                continue

            tgt_vec = tgt_vec.reshape(1, -1)
            sim = float(cosine_similarity(src_vec, tgt_vec)[0][0])

            if sim > 0.6:
                SemanticLink.objects.create(
                    source_type=src_type,
                    source_id=src_id,
                    target_type=tgt_type,
                    target_id=tgt_id,
                    similarity=sim,
                )

    print(f"[SemanticLinks] Created semantic connections for {len(all_items)} items.")
    return f"Links built for {len(all_items)} items."
