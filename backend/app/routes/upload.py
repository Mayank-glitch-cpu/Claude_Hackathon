from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_parser import DocumentParser
from app.utils.logger import setup_logger
import uuid
import json

# Set up logging
logger = setup_logger("upload")

router = APIRouter()

# In-memory storage (in production, use a database)
questions_store = {}
files_store = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and parse a document containing a question"""
    logger.info(f"File upload request received - Filename: {file.filename}, Content-Type: {file.content_type}")
    
    try:
        # Read file content
        file_content = await file.read()
        logger.info(f"File read successfully - Size: {len(file_content)} bytes")
        
        # Parse document
        logger.info(f"Parsing document: {file.filename}")
        parser = DocumentParser()
        question_data = parser.parse(file_content, file.filename)
        logger.info(f"Document parsed successfully - Type: {question_data.get('file_type')}, Question length: {len(question_data.get('text', ''))}")
        logger.debug(f"Extracted question: {question_data.get('text', '')[:200]}...")
        logger.debug(f"Extracted options: {question_data.get('options', [])}")
        
        # Generate unique ID
        question_id = str(uuid.uuid4())
        logger.info(f"Generated question ID: {question_id}")
        
        # Store question
        questions_store[question_id] = {
            "id": question_id,
            "text": question_data["text"],
            "options": question_data.get("options"),
            "file_type": question_data.get("file_type"),
            "full_text": question_data.get("full_text", question_data["text"])
        }
        logger.info(f"Question stored successfully - ID: {question_id}")
        
        return {
            "question_id": question_id,
            "text": question_data["text"],
            "options": question_data.get("options"),
            "message": "File uploaded and parsed successfully"
        }
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

