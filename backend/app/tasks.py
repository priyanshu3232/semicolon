from celery import Celery
from typing import List, Dict, Any
import logging
from .core.config import settings
from .ml.anomaly import anomaly_detector
from .ml.granite_client import granite_client

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "ml_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "process-documents-hourly": {
            "task": "app.tasks.process_documents_batch",
            "schedule": 3600.0,  # Every hour
        },
    },
)


@celery_app.task
def process_documents_batch():
    """
    Background task to process documents and detect anomalies
    """
    try:
        logger.info("Starting batch document processing")
        
        # Mock documents for processing
        documents = [
            {
                "file_id": "doc_1",
                "filename": "report.pdf",
                "content": "This is a sample business report with normal content length and structure."
            },
            {
                "file_id": "doc_2", 
                "filename": "suspicious.pdf",
                "content": "URGENT!!! CONFIDENTIAL!!! This document has unusual patterns and formatting that might indicate suspicious activity. Please review immediately!!! This is very important!!! Act now!!!"
            }
        ]
        
        # Train anomaly detector if not already trained
        if not anomaly_detector.is_fitted:
            logger.info("Training anomaly detector")
            training_docs = documents + [
                {"content": "Normal document with standard business content and professional formatting."},
                {"content": "Another regular document discussing quarterly performance metrics and business objectives."},
                {"content": "Standard technical documentation covering best practices and implementation guidelines."}
            ]
            anomaly_detector.fit(training_docs)
        
        # Detect anomalies
        anomaly_results = anomaly_detector.batch_detect(documents)
        
        # Process results and create alerts
        alerts_created = 0
        for result in anomaly_results:
            if result["is_anomaly"]:
                logger.warning(f"Anomaly detected in document {result['filename']}: score={result['anomaly_score']:.2f}")
                alerts_created += 1
                
                # In production, save alert to database
                # create_anomaly_alert(result)
        
        logger.info(f"Batch processing completed. {alerts_created} anomalies detected.")
        return {"processed": len(documents), "anomalies": alerts_created}
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise


@celery_app.task
def create_embeddings_task(documents: List[Dict[str, Any]]):
    """
    Background task to create document embeddings
    """
    try:
        logger.info(f"Creating embeddings for {len(documents)} documents")
        
        texts = [doc["content"][:1000] for doc in documents]  # Limit text length
        
        # This would be async in real implementation
        # For demo, we'll just log the action
        logger.info("Embeddings created successfully")
        
        return {"documents_processed": len(documents)}
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise


@celery_app.task
def process_audio_task(audio_file_path: str, language: str = "en-US"):
    """
    Background task to process audio files
    """
    try:
        logger.info(f"Processing audio file: {audio_file_path}")
        
        # In production, read audio file and process with Granite ASR
        # For demo, return mock result
        result = {
            "transcript": "Demo transcript from background processing",
            "confidence": 0.95,
            "language": language
        }
        
        logger.info("Audio processing completed")
        return result
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise