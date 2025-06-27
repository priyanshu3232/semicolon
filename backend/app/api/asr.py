from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..core.auth import get_current_user
from ..ml.granite_client import granite_client
from ..schemas import ASRResponse
import aiofiles
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/asr", response_model=ASRResponse)
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = "en-US",
    current_user: str = Depends(get_current_user)
):
    """
    Convert speech to text using IBM Granite ASR
    """
    # Validate audio file
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an audio file"
        )
    
    try:
        # Read audio file content
        audio_data = await audio_file.read()
        
        # Call Granite ASR service
        result = await granite_client.speech_to_text(audio_data, language)
        
        response = ASRResponse(
            transcript=result["transcript"],
            confidence=result["confidence"],
            duration=result.get("duration"),
            language=result["language"]
        )
        
        logger.info(f"Successfully transcribed audio file: {audio_file.filename}")
        return response
        
    except Exception as e:
        logger.error(f"Error in speech-to-text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )