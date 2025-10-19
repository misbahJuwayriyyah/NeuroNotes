from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str):
    """
    Generates an embedding vector for the given text.
    """
    if not text.strip():
        return []
    try:
        embedding = embedding_model.encode(text, show_progress_bar=False)
        return embedding.tolist()
    except Exception as e:
        print(f"[ERROR] Failed to generate embedding: {e}")
        return []


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyPDF2.
    """
    try:
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to extract PDF text: {e}")
        return ""
