from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import time
import logging
from ..core.auth import get_current_user
from ..ml.granite_client import granite_client
from ..schemas import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock document store for demo
MOCK_DOCUMENTS = [
    {
        "id": "doc_1",
        "filename": "sample_report.pdf",
        "content": "This is a sample business report discussing quarterly performance metrics.",
        "metadata": {"type": "report", "date": "2024-01-15"}
    },
    {
        "id": "doc_2", 
        "filename": "technical_guide.pdf",
        "content": "Technical documentation covering API integration and best practices for developers.",
        "metadata": {"type": "guide", "date": "2024-01-10"}
    },
    {
        "id": "doc_3",
        "filename": "research_paper.pdf", 
        "content": "Research findings on machine learning applications in document processing and analysis.",
        "metadata": {"type": "research", "date": "2024-01-20"}
    }
]


async def semantic_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Perform semantic search using embeddings and vector similarity
    In production, this would use Pinecone vector database
    """
    try:
        # Create embedding for query
        query_embedding_result = await granite_client.create_embeddings([query])
        query_embedding = query_embedding_result["embeddings"][0]
        
        # For demo, return mock relevant documents based on keyword matching
        relevant_docs = []
        query_lower = query.lower()
        
        for doc in MOCK_DOCUMENTS:
            # Simple keyword matching for demo
            content_lower = doc["content"].lower()
            if any(word in content_lower for word in query_lower.split()):
                relevant_docs.append({
                    **doc,
                    "similarity_score": 0.85  # Mock similarity score
                })
        
        # If no keyword matches, return all documents with lower scores
        if not relevant_docs:
            relevant_docs = [
                {**doc, "similarity_score": 0.3} for doc in MOCK_DOCUMENTS
            ]
        
        return relevant_docs[:limit]
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return MOCK_DOCUMENTS[:limit]


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Query documents using RAG (Retrieval-Augmented Generation)
    """
    start_time = time.time()
    
    try:
        # Step 1: Semantic search to find relevant documents
        relevant_docs = await semantic_search(request.question, request.context_limit)
        
        # Step 2: Prepare context from relevant documents
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"Document: {doc['filename']}\nContent: {doc['content'][:500]}...")
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Generate answer using Granite Instruct
        prompt = f"""Based on the following documents, answer the user's question.

Context:
{context}

Question: {request.question}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so.

Answer:"""
        
        generation_result = await granite_client.generate_text(prompt, max_tokens=300)
        answer = generation_result["generated_text"]
        
        # Step 4: Prepare sources if requested
        sources = []
        if request.include_sources:
            sources = [
                {
                    "document_id": doc["id"],
                    "filename": doc["filename"],
                    "similarity_score": doc["similarity_score"],
                    "excerpt": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "metadata": doc["metadata"]
                }
                for doc in relevant_docs
            ]
        
        processing_time = time.time() - start_time
        
        response = QueryResponse(
            answer=answer,
            sources=sources,
            confidence=0.85,  # Mock confidence score
            processing_time=processing_time
        )
        
        logger.info(f"Successfully processed query in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )