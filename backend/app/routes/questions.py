from fastapi import APIRouter, HTTPException
from app.routes.upload import questions_store
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("questions")

@router.get("/questions/{question_id}")
async def get_question(question_id: str):
    """Get question details by ID"""
    logger.info(f"Get question request - ID: {question_id}")
    
    if question_id not in questions_store:
        logger.warning(f"Question not found: {question_id}")
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = questions_store[question_id]
    logger.debug(f"Question retrieved - Has story: {'story' in question}")
    
    # Check if story data exists
    if "story" in question:
        logger.info("Returning question with story data")
        return {
            "id": question["id"],
            "text": question["text"],
            "options": question.get("options"),
            "story": question.get("story")
        }
    
    logger.info("Returning question without story data")
    return {
        "id": question["id"],
        "text": question["text"],
        "options": question.get("options")
    }

