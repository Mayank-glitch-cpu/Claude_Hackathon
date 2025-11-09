"""Generate route - refactored to use orchestrator and database"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.services.pipeline.orchestrator import PipelineOrchestrator
from app.repositories.question_repository import QuestionRepository
from app.repositories.process_repository import ProcessRepository
from app.repositories.visualization_repository import VisualizationRepository
from app.repositories.game_blueprint_repository import GameBlueprintRepository
from app.db.session import get_db
from app.utils.logger import setup_logger
import uuid
import asyncio

# Set up logging
logger = setup_logger("generate")

router = APIRouter()

async def process_pipeline_background(
    process_id: str,
    question_id: str,
    force_fresh: bool = True
):
    """Background task to process question through pipeline"""
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        orchestrator = PipelineOrchestrator(db)
        result = orchestrator.execute_pipeline(process_id, question_id, force_fresh=force_fresh)
        logger.info(f"Background pipeline completed: {process_id}")
        return result
    except Exception as e:
        logger.error(f"Background pipeline failed: {e}", exc_info=True)
        raise
    finally:
        db.close()

@router.post("/process/{question_id}")
async def start_processing(
    question_id: str,
    background_tasks: BackgroundTasks,
    force_fresh: bool = True,  # Default to True to always do fresh runs
    db: Session = Depends(get_db)
):
    """Start processing pipeline for a question
    
    Args:
        question_id: Question ID to process
        force_fresh: If True, start from step 1 regardless of existing steps (default: True)
    """
    logger.info(f"[API] /process/{question_id} - Request received (force_fresh={force_fresh})")
    
    # Check if question exists
    question = QuestionRepository.get_by_id(db, question_id)
    if not question:
        logger.error(f"[API] Question {question_id} not found")
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Create process record
    process = ProcessRepository.create(db, question_id, initial_status="pending")
    process_id = process.id
    
    logger.info(f"[API] Starting processing pipeline - process_id={process_id}, question_id={question_id}, force_fresh={force_fresh}")
    
    # Start background processing
    background_tasks.add_task(process_pipeline_background, process_id, question_id, force_fresh)
    logger.info(f"[API] Background task added for process_id={process_id}")
    
    return {
        "process_id": process_id,
        "question_id": question_id,
        "force_fresh": force_fresh,
        "message": "Processing started"
    }

@router.get("/visualization/{visualization_id}")
async def get_visualization(
    visualization_id: str,
    db: Session = Depends(get_db)
):
    """Get generated visualization"""
    logger.info(f"[API] /visualization/{visualization_id} - Request received")
    
    try:
        visualization = VisualizationRepository.get_by_id(db, visualization_id)
        
        if not visualization:
            logger.warning(f"[API] Visualization {visualization_id} not found")
            raise HTTPException(status_code=404, detail="Visualization not found")
        
        # Get story data from story_data_json
        question_data = visualization.story_data_json if visualization.story_data_json else None
        if question_data:
            logger.debug(f"[API] Found story data for visualization {visualization_id}")
        else:
            logger.warning(f"[API] Visualization {visualization_id} has no story data")
        
        # Get blueprint if available
        blueprint_data = None
        if visualization.blueprint_id:
            blueprint = GameBlueprintRepository.get_by_id(db, visualization.blueprint_id)
            if blueprint:
                blueprint_data = {
                    "id": blueprint.id,
                    "template_type": blueprint.template_type,
                    "blueprint": blueprint.blueprint_json,
                    "assets": blueprint.assets_json or {}
                }
                logger.info(f"[API] Found blueprint for visualization {visualization_id}")
        
        # Return blueprint if available, otherwise HTML (backward compatibility)
        if blueprint_data:
            logger.info(f"[API] Returning blueprint for visualization {visualization_id}")
            return {
                "id": visualization.id,
                "type": "blueprint",
                "blueprint": blueprint_data,
                "question_data": question_data
            }
        else:
            logger.info(f"[API] Returning HTML for visualization {visualization_id}, HTML length: {len(visualization.html_content or '')} chars")
            return {
                "id": visualization.id,
                "type": "html",
                "html": visualization.html_content or "",
                "question_data": question_data
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error getting visualization {visualization_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting visualization: {str(e)}")

@router.post("/check-answer/{visualization_id}")
async def check_answer(
    visualization_id: str,
    answer_data: dict,
    db: Session = Depends(get_db)
):
    """Check if answer is correct"""
    question_number = answer_data.get("questionNumber")
    selected_answer = answer_data.get("selectedAnswer")
    logger.info(f"Check answer request - Visualization: {visualization_id}, Question: {question_number}, Answer: {selected_answer}")
    
    visualization = VisualizationRepository.get_by_id(db, visualization_id)
    if not visualization:
        logger.warning(f"Visualization not found: {visualization_id}")
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    question_data = visualization.story_data_json
    
    # Find the question in question_flow
    question_flow = question_data.get("question_flow", [])
    logger.debug(f"Question flow has {len(question_flow)} questions")
    target_question = None
    
    for q in question_flow:
        if q.get("question_number") == question_number:
            target_question = q
            break
    
    if not target_question:
        logger.warning(f"Question {question_number} not found in flow")
        raise HTTPException(status_code=404, detail="Question not found")
    
    correct_answer = target_question.get("answer_structure", {}).get("correct_answer", "")
    is_correct = str(selected_answer).strip() == str(correct_answer).strip()
    
    logger.info(f"Answer check result - Correct: {is_correct}, Expected: {correct_answer}, Provided: {selected_answer}")
    
    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "feedback": target_question.get("answer_structure", {}).get("feedback", {})
    }
