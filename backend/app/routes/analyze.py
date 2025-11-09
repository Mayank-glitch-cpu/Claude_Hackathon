from fastapi import APIRouter, HTTPException
from app.services.llm_service import LLMService
from app.services.prompt_selector import PromptSelector
from app.routes.upload import questions_store
from app.utils.logger import setup_logger

# Set up logging
logger = setup_logger("analyze")

router = APIRouter()

# Lazy initialization - create instances when needed
def get_llm_service():
    return LLMService()

def get_prompt_selector():
    return PromptSelector()

# Initialize at module level but allow it to fail gracefully
try:
    llm_service = LLMService()
    prompt_selector = PromptSelector()
    logger.info("LLM service and prompt selector initialized")
except ValueError as e:
    # Service will be initialized on first use
    llm_service = None
    prompt_selector = None
    logger.warning(f"LLM service not initialized: {e}")

@router.post("/analyze/{question_id}")
async def analyze_question(question_id: str):
    """Analyze question and select appropriate prompt template"""
    logger.info(f"[API] /analyze/{question_id} - Request received")
    
    if question_id not in questions_store:
        logger.error(f"[API] Question {question_id} not found")
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Initialize services if not already done
    if llm_service is None:
        logger.info("[API] Initializing LLM service...")
        service = get_llm_service()
    else:
        service = llm_service
    
    if prompt_selector is None:
        logger.info("[API] Initializing prompt selector...")
        selector = get_prompt_selector()
    else:
        selector = prompt_selector
    
    question = questions_store[question_id]
    logger.info(f"[API] Analyzing question: {question['text'][:50]}...")
    
    try:
        # Analyze question
        logger.info("[API] Calling LLM for question analysis...")
        analysis = service.analyze_question(
            question["text"],
            question.get("options")
        )
        logger.info(f"[API] Analysis result: type={analysis.get('question_type')}, subject={analysis.get('subject')}")
        
        # Select prompt template
        prompt_template = selector.select_prompt(
            analysis.get("question_type", "reasoning"),
            analysis.get("subject", "General")
        )
        logger.info(f"[API] Prompt template selected (length: {len(prompt_template)} chars)")
        
        # Store analysis and prompt
        questions_store[question_id]["analysis"] = analysis
        questions_store[question_id]["prompt_template"] = prompt_template
        
        logger.info(f"[API] Analysis stored successfully for question_id={question_id}")
        return {
            "question_id": question_id,
            "analysis": analysis,
            "prompt_selected": True
        }
    except Exception as e:
        logger.error(f"[API] Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

