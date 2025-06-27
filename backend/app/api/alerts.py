from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime, timedelta
from ..core.auth import get_current_user
from ..schemas import AnomalyAlert, DashboardStats
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock alerts storage for demo
MOCK_ALERTS = [
    AnomalyAlert(
        id=str(uuid.uuid4()),
        document_id="doc_1",
        anomaly_type="unusual_length",
        severity="medium",
        description="Document length significantly deviates from normal patterns",
        confidence=0.78,
        detected_at=datetime.utcnow() - timedelta(hours=2),
        metadata={"document_length": 15000, "avg_length": 5000}
    ),
    AnomalyAlert(
        id=str(uuid.uuid4()),
        document_id="doc_2", 
        anomaly_type="suspicious_content",
        severity="high",
        description="Document contains unusual keyword patterns",
        confidence=0.92,
        detected_at=datetime.utcnow() - timedelta(hours=1),
        metadata={"suspicious_keywords": ["urgent", "confidential", "immediate"]}
    )
]


@router.get("/alerts", response_model=List[AnomalyAlert])
async def get_alerts(
    limit: int = 10,
    severity: str = None,
    current_user: str = Depends(get_current_user)
):
    """
    Get anomaly alerts
    """
    try:
        alerts = MOCK_ALERTS.copy()
        
        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        # Sort by detection time (newest first)
        alerts.sort(key=lambda x: x.detected_at, reverse=True)
        
        return alerts[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching alerts: {str(e)}"
        )


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: str = Depends(get_current_user)
):
    """
    Get dashboard statistics
    """
    try:
        stats = DashboardStats(
            total_documents=25,
            total_queries=150,
            avg_processing_time=2.3,
            anomalies_detected=len(MOCK_ALERTS),
            last_processed=datetime.utcnow() - timedelta(minutes=15)
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard stats: {str(e)}"
        )