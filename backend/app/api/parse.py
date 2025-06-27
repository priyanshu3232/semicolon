from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
import aiofiles
import os
import uuid
from datetime import datetime
import pandas as pd
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage
import logging
from ..core.auth import get_current_user
from ..core.config import settings
from ..schemas import FileUploadResponse, ParsedDocument

logger = logging.getLogger(__name__)
router = APIRouter()


async def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return file path"""
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """Parse PDF file and extract content"""
    try:
        # Extract text content
        content = extract_text(file_path)
        
        # Get page count
        with open(file_path, 'rb') as f:
            page_count = len(list(PDFPage.get_pages(f)))
        
        # Basic metadata
        word_count = len(content.split())
        
        return {
            "content": content,
            "page_count": page_count,
            "word_count": word_count,
            "file_type": "pdf"
        }
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")


def parse_csv(file_path: str) -> Dict[str, Any]:
    """Parse CSV file and extract content"""
    try:
        df = pd.read_csv(file_path)
        
        # Convert to string representation
        content = df.to_string()
        
        return {
            "content": content,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "file_type": "csv",
            "preview": df.head().to_dict()
        }
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")


def parse_text(file_path: str) -> Dict[str, Any]:
    """Parse text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        word_count = len(content.split())
        line_count = len(content.split('\n'))
        
        return {
            "content": content,
            "word_count": word_count,
            "line_count": line_count,
            "file_type": "text"
        }
    except Exception as e:
        logger.error(f"Error parsing text file: {e}")
        raise HTTPException(status_code=400, detail=f"Error parsing text file: {str(e)}")


@router.post("/parse", response_model=ParsedDocument)
async def parse_document(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Parse uploaded document and extract content
    """
    # Validate file size
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_file_size / (1024*1024):.1f}MB"
        )
    
    # Save uploaded file
    file_path = await save_uploaded_file(file)
    file_id = str(uuid.uuid4())
    
    try:
        # Determine file type and parse accordingly
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension == '.pdf':
            parsed_data = parse_pdf(file_path)
        elif file_extension == '.csv':
            parsed_data = parse_csv(file_path)
        elif file_extension in ['.txt', '.md']:
            parsed_data = parse_text(file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}"
            )
        
        # Create response
        response = ParsedDocument(
            file_id=file_id,
            filename=file.filename,
            content=parsed_data["content"],
            metadata={
                "file_path": file_path,
                "file_size": file.size,
                "content_type": file.content_type,
                "uploaded_by": current_user,
                "upload_time": datetime.utcnow().isoformat(),
                **{k: v for k, v in parsed_data.items() if k != "content"}
            },
            page_count=parsed_data.get("page_count"),
            word_count=parsed_data.get("word_count")
        )
        
        logger.info(f"Successfully parsed document: {file.filename}")
        return response
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e