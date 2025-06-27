import pytest
from app.ml.anomaly import AnomalyDetector
from app.ml.granite_client import GraniteClient


def test_anomaly_detector():
    detector = AnomalyDetector()
    
    # Test feature extraction
    doc = {"content": "This is a test document with some content."}
    features = detector.extract_features(doc)
    
    assert len(features) == 10
    assert all(isinstance(f, (int, float)) for f in features)


def test_granite_client_initialization():
    client = GraniteClient()
    assert client.api_url is not None
    assert hasattr(client, 'speech_to_text')
    assert hasattr(client, 'generate_text')
    assert hasattr(client, 'create_embeddings')