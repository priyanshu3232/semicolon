import httpx
import asyncio
from typing import Optional, Dict, Any, List
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class GraniteClient:
    def __init__(self):
        self.api_key = settings.granite_api_key
        self.api_url = settings.granite_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def speech_to_text(self, audio_data: bytes, language: str = "en-US") -> Dict[str, Any]:
        """
        Convert speech to text using Granite ASR
        """
        if not self.api_key:
            # Stub for demo - return mock response
            return {
                "transcript": "This is a demo transcript since no Granite API key is configured.",
                "confidence": 0.95,
                "language": language,
                "duration": 5.2
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/octet-stream"
            }
            
            params = {"language": language}
            
            response = await self.client.post(
                f"{self.api_url}/asr",
                headers=headers,
                params=params,
                content=audio_data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error in speech_to_text: {e}")
            # Return mock response on error
            return {
                "transcript": f"Error processing audio: {str(e)}",
                "confidence": 0.0,
                "language": language,
                "duration": 0.0
            }
    
    async def generate_text(self, prompt: str, max_tokens: int = 150) -> Dict[str, Any]:
        """
        Generate text using Granite Instruct model
        """
        if not self.api_key:
            # Stub for demo
            return {
                "generated_text": f"Demo response to: {prompt[:50]}... (Granite API key not configured)",
                "tokens_used": max_tokens // 2,
                "model": "granite-instruct-demo"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = await self.client.post(
                f"{self.api_url}/instruct",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error in generate_text: {e}")
            return {
                "generated_text": f"Error generating text: {str(e)}",
                "tokens_used": 0,
                "model": "granite-instruct-error"
            }
    
    async def create_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        """
        Create embeddings using Granite embedding model
        """
        if not self.api_key:
            # Return mock embeddings
            import numpy as np
            embeddings = [np.random.rand(768).tolist() for _ in texts]
            return {
                "embeddings": embeddings,
                "model": "granite-embeddings-demo",
                "dimension": 768
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {"texts": texts}
            
            response = await self.client.post(
                f"{self.api_url}/embeddings",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error in create_embeddings: {e}")
            # Return mock embeddings on error
            import numpy as np
            embeddings = [np.random.rand(768).tolist() for _ in texts]
            return {
                "embeddings": embeddings,
                "model": "granite-embeddings-error",
                "dimension": 768
            }
    
    async def close(self):
        await self.client.aclose()


# Global client instance
granite_client = GraniteClient()