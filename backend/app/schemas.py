from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class FileUploadResponse(BaseModel):
    filename: str
    file_id: str
    size: int
    content_type: str
    upload_time: datetime


class ParsedDocument(BaseModel):
    file_id: str
    filename: str
    content: str
    metadata: Dict[str, Any]
    page_count: Optional[int] = None
    word_count: Optional[int] = None


class ASRRequest(BaseModel):
    audio_file_url: Optional[str] = None
    language: str = "en-US"


class ASRResponse(BaseModel):
    transcript: str
    confidence: float
    duration: Optional[float] = None
    language: str


class QueryRequest(BaseModel):
    question: str
    context_limit: int = 5
    include_sources: bool = True


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float


class AnomalyAlert(BaseModel):
    id: str
    document_id: str
    anomaly_type: str
    severity: str
    description: str
    confidence: float
    detected_at: datetime
    metadata: Dict[str, Any]


class DashboardStats(BaseModel):
    total_documents: int
    total_queries: int
    avg_processing_time: float
    anomalies_detected: int
    last_processed: Optional[datetime] = None