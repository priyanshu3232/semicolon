import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_fitted = False
    
    def extract_features(self, document: Dict[str, Any]) -> List[float]:
        """
        Extract numerical features from document for anomaly detection
        """
        content = document.get('content', '')
        
        features = [
            len(content),  # Document length
            len(content.split()),  # Word count
            len(set(content.split())),  # Unique word count
            content.count('.'),  # Sentence count (rough)
            content.count('\n'),  # Line breaks
            len([w for w in content.split() if len(w) > 10]),  # Long words
            content.count('http'),  # URLs
            content.count('@'),  # Email addresses
            len([w for w in content.split() if w.isupper()]),  # Uppercase words
            content.count('!') + content.count('?'),  # Exclamation/question marks
        ]
        
        return features
    
    def fit(self, documents: List[Dict[str, Any]]) -> None:
        """
        Train the anomaly detector on a set of documents
        """
        if not documents:
            logger.warning("No documents provided for training")
            return
        
        try:
            features = [self.extract_features(doc) for doc in documents]
            features_array = np.array(features)
            
            # Handle case where we have only one document
            if len(features_array) < 2:
                logger.warning("Need at least 2 documents for anomaly detection")
                return
            
            # Standardize features
            self.scaler.fit(features_array)
            features_scaled = self.scaler.transform(features_array)
            
            # Fit isolation forest
            self.isolation_forest.fit(features_scaled)
            self.is_fitted = True
            
            logger.info(f"Anomaly detector trained on {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
    
    def detect_anomaly(self, document: Dict[str, Any]) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Detect if a document is anomalous
        Returns: (is_anomaly, anomaly_score, details)
        """
        if not self.is_fitted:
            logger.warning("Anomaly detector not fitted")
            return False, 0.0, {"error": "Detector not trained"}
        
        try:
            features = self.extract_features(document)
            features_array = np.array([features])
            features_scaled = self.scaler.transform(features_array)
            
            # Get anomaly score (-1 for anomaly, 1 for normal)
            prediction = self.isolation_forest.predict(features_scaled)[0]
            anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
            
            is_anomaly = prediction == -1
            
            # Normalize score to 0-1 range (higher = more anomalous)
            normalized_score = max(0, (0.5 - anomaly_score) / 0.5)
            
            details = {
                "features": features,
                "raw_score": float(anomaly_score),
                "normalized_score": float(normalized_score),
                "feature_names": [
                    "document_length", "word_count", "unique_words", "sentences",
                    "line_breaks", "long_words", "urls", "emails", "uppercase_words", "punctuation"
                ]
            }
            
            return is_anomaly, normalized_score, details
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return False, 0.0, {"error": str(e)}
    
    def batch_detect(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a batch of documents
        """
        results = []
        
        for i, doc in enumerate(documents):
            is_anomaly, score, details = self.detect_anomaly(doc)
            
            result = {
                "document_id": doc.get("file_id", f"doc_{i}"),
                "filename": doc.get("filename", f"document_{i}"),
                "is_anomaly": is_anomaly,
                "anomaly_score": score,
                "details": details
            }
            
            results.append(result)
        
        return results


# Global anomaly detector instance
anomaly_detector = AnomalyDetector()