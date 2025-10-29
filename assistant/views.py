from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from core.utils import generate_embedding
from .models import AssistantQuery
from .utils import retrieve_relevant_content, query_llm_with_context
from rest_framework import generics
from .models import AssistantFeedback
from .serializers import AssistantFeedbackSerializer


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def ask_assistant(request):
    question = request.data.get("question", "")
    if not question:
        return Response({"error": "Question is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Step 1: Embed the question
    query_embedding = generate_embedding(question)

    # Step 2: Retrieve relevant items
    top_items = retrieve_relevant_content(query_embedding, top_n=3)

    # Step 3: Build context
    context = "\n\n".join(
    [f"[{i['title']}]\n{i['content'][:400]}" for i in top_items]
)

    # Step 4: Query Groq LLM
    answer = query_llm_with_context(question, context)


    # Step 5: Save query
    entry = AssistantQuery.objects.create(
        user=request.user,
        question=question,
        answer=answer,
        sources=top_items
    )

    return Response({
        "answer": answer,
        "sources": top_items,
        "id": entry.id #type: ignore
    }, status=status.HTTP_200_OK)


class AssistantFeedbackView(generics.CreateAPIView):
    queryset = AssistantFeedback.objects.all()
    serializer_class = AssistantFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
