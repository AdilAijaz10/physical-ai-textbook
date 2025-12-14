from typing import List, Dict, Any, Optional
import logging
from openai import OpenAI
from .vector_db import vector_db_service
from .data_privacy import data_privacy_service
from ..config.settings import settings
from .base_service import BaseService


logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.openai_api_key)


class RAGService(BaseService):
    """RAG service for handling queries and generating responses with citations"""

    def __init__(self):
        super().__init__()
        self.vector_db = vector_db_service
        self.data_privacy = data_privacy_service

    def execute(self, query: str, selected_text: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute the RAG query process"""
        try:
            # Step 1: Generate embedding for the query
            query_embedding = self._get_embedding(query)

            # Step 2: Search for relevant content
            relevant_chunks = self._search_relevant_content(query_embedding, selected_text)

            # Step 3: Generate response based on retrieved content
            response = self._generate_response(query, relevant_chunks, selected_text)

            # Step 4: Format response with citations
            formatted_response = self._format_response_with_citations(response, relevant_chunks)

            return formatted_response
        except Exception as e:
            return self.handle_error(e, "RAGService.execute")

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def _search_relevant_content(self, query_embedding: List[float], selected_text: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for relevant content chunks in vector database"""
        # Search for similar content
        results = self.vector_db.search_vectors(query_embedding, limit=5)

        # If selected text is provided, we might want to boost relevance for that context
        relevant_chunks = []
        for result in results:
            chunk_data = {
                "file_path": result["payload"].get("file_path"),
                "chunk_index": result["payload"].get("chunk_index"),
                "content": result["payload"].get("content"),
                "relevance_score": result["score"]
            }
            relevant_chunks.append(chunk_data)

        return relevant_chunks

    def _generate_response(self, query: str, relevant_chunks: List[Dict[str, Any]], selected_text: Optional[str] = None) -> str:
        """Generate response using OpenAI based on relevant content"""
        # Prepare context from relevant chunks
        if relevant_chunks:
            context = "\n\n".join([f"Source: {chunk['file_path']} (Chunk {chunk['chunk_index']})\nContent: {chunk['content'][:500]}..."  # Limit content size
                                  for chunk in relevant_chunks])
        else:
            context = "No relevant content found in the textbook."

        # Include selected text if provided, giving it prominence in the context
        if selected_text:
            # Boost the selected text by putting it first and highlighting it
            enhanced_context = f"USER SELECTED TEXT (HIGHLIGHTED CONTEXT):\n{selected_text}\n\n"
            enhanced_context += f"ADDITIONAL CONTEXT FROM TEXTBOOK:\n{context}"
            context = enhanced_context

        # Create a prompt for the AI
        prompt = f"""
        You are an expert assistant for the Physical AI & Humanoid Robotics textbook.
        Answer the user's question based on the provided context from the textbook.

        The user may have selected specific text which is provided as "USER SELECTED TEXT".
        Pay special attention to this selected text when answering the question.

        If the context doesn't contain enough information to answer the question,
        say so clearly and suggest where the user might find the information in the textbook.

        Always provide specific citations to textbook sections when possible.

        Context:
        {context}

        Question: {query}

        Provide a comprehensive answer based on the textbook content:
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,  # Increased to allow more comprehensive answers
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    def _format_response_with_citations(self, response: str, relevant_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format the response with proper citations"""
        citations = []
        for chunk in relevant_chunks:
            citation = {
                "file_path": chunk["file_path"],
                "chunk_index": chunk["chunk_index"],
                "content_snippet": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "relevance_score": chunk["relevance_score"]
            }
            citations.append(citation)

        return {
            "response": response,
            "citations": citations
        }


# Global instance
rag_service = RAGService()