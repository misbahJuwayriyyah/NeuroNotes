import numpy as np
from groq import Groq
import os
from sklearn.metrics.pairwise import cosine_similarity
from core.models import Note, Document

def retrieve_relevant_content(query_embedding, top_n=3, min_similarity=0.5):
    items = []

    notes = Note.objects.exclude(embedding=None)
    docs = Document.objects.exclude(embedding=None)

    for note in notes:
        sim = float(cosine_similarity(
            np.array(query_embedding).reshape(1, -1),
            np.array(note.embedding).reshape(1, -1)
        )[0][0])
        if sim >= min_similarity:
            items.append({
                "type": "note",
                "id": note.id, #type: ignore
                "title": note.title,
                "content": note.content,
                "similarity": sim
            })

    for doc in docs:
        sim = float(cosine_similarity(
            np.array(query_embedding).reshape(1, -1),
            np.array(doc.embedding).reshape(1, -1)
        )[0][0])
        if sim >= min_similarity:
            items.append({
                "type": "document",
                "id": doc.id, #type: ignore
                "title": doc.title,
                "content": doc.extracted_text or "",
                "similarity": sim
            })

    # Sort by similarity
    items = sorted(items, key=lambda x: x["similarity"], reverse=True)
    return items[:top_n]


def query_llm_with_context(question, context):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt = (
        "You are NeuroNotes, a research assistant that first relies on the provided context "
        "(from the user's notes and documents). You may include additional general information "
        "only if it expands or clarifies the context — but you must clearly separate it by starting "
        "that part with the word 'Additionally,'. Always cite any note/document titles from the context you used."
    )

    user_prompt = f"""
Here is the retrieved context from the user's private notes and documents:

{context}

---
Question: {question}

Instructions:
1. Start your answer normally — do not prefix it with 'Context:'.
2. Base your main answer primarily on the above context.
3. If you add general knowledge beyond the context, start that part with 'Additionally,'.
4. Include any relevant note/document titles in parentheses for citations.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=500,
        )
        return completion.choices[0].message.content.strip() #type: ignore

    except Exception as e:
        print(f"[Groq Error] {e}")
        return "The assistant could not generate a response right now."
