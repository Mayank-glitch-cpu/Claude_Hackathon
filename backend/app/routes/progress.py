from fastapi import APIRouter, HTTPException
from app.models.question import ProcessStatus
from app.utils.logger import setup_logger

# Set up logging
logger = setup_logger("progress")

router = APIRouter()

# In-memory storage for process statuses
process_statuses = {}
visualizations_store = {}

@router.get("/progress/{process_id}")
async def get_progress(process_id: str):
    """Get progress status for a process"""
    logger.debug(f"[API] /progress/{process_id} - Request received")
    
    if process_id not in process_statuses:
        logger.warning(f"[API] Process {process_id} not found")
        raise HTTPException(status_code=404, detail="Process not found")
    
    status = process_statuses[process_id]
    logger.debug(f"[API] Returning status: {status['status']}, progress: {status['progress']}%")
    
    return {
        "process_id": process_id,
        "status": status["status"],
        "progress": status["progress"],
        "current_step": status["current_step"],
        "visualization_id": status.get("visualization_id"),
        "error_message": status.get("error_message")
    }

