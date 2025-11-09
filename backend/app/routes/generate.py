from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.llm_service import LLMService
from app.routes.upload import questions_store
from app.routes.progress import process_statuses
from app.utils.logger import setup_logger
import uuid
import asyncio
import json

# Set up logging
logger = setup_logger("generate")

router = APIRouter()

def get_llm_service():
    return LLMService()

# Try to initialize, but allow it to fail gracefully
try:
    llm_service = LLMService()
    logger.info("LLM service initialized successfully")
except ValueError as e:
    llm_service = None
    logger.warning(f"LLM service not initialized: {e}")

async def process_pipeline(process_id: str, question_id: str):
    """Background task to process question through pipeline"""
    logger.info(f"[Pipeline] Starting processing for question_id={question_id}, process_id={process_id}")
    
    try:
        process_statuses[process_id] = {
            "process_id": process_id,
            "status": "processing",
            "progress": 0,
            "current_step": "Initializing",
            "visualization_id": None
        }
        
        if question_id not in questions_store:
            raise ValueError(f"Question {question_id} not found in store")
        
        question = questions_store[question_id]
        logger.info(f"[Pipeline] Question loaded: {question.get('text', '')[:50]}...")
        
        # Step 1: Analyze (if not already done)
        if "analysis" not in question:
            logger.info("-" * 80)
            logger.info("STEP 1: QUESTION ANALYSIS")
            logger.info("-" * 80)
            process_statuses[process_id]["progress"] = 10
            process_statuses[process_id]["current_step"] = "Analyzing question"
            
            # Call analyze endpoint directly (it's not async, so we call it synchronously)
            from app.routes.analyze import get_llm_service, get_prompt_selector
            from app.services.prompt_selector import PromptSelector
            
            service = get_llm_service()
            selector = get_prompt_selector()
            
            logger.info("Calling LLM service for question analysis...")
            analysis = service.analyze_question(
                question["text"],
                question.get("options")
            )
            logger.info(f"Analysis complete - Type: {analysis.get('question_type', 'unknown')}, Subject: {analysis.get('subject', 'unknown')}, Difficulty: {analysis.get('difficulty', 'unknown')}")
            logger.debug(f"Full analysis result: {json.dumps(analysis, indent=2)}")
            
            # Select prompt template
            prompt_template = selector.select_prompt(
                analysis.get("question_type", "reasoning"),
                analysis.get("subject", "General")
            )
            logger.info(f"Prompt template selected - Length: {len(prompt_template)} chars")
            
            # Store analysis and prompt
            questions_store[question_id]["analysis"] = analysis
            questions_store[question_id]["prompt_template"] = prompt_template
            logger.info("Analysis stored successfully in questions_store")
        else:
            logger.info("Analysis already exists, skipping analysis step")
            logger.debug(f"Existing analysis: {question.get('analysis', {})}")
        
        # Step 2: Generate story
        logger.info("-" * 80)
        logger.info("STEP 2: STORY GENERATION")
        logger.info("-" * 80)
        process_statuses[process_id]["progress"] = 30
        process_statuses[process_id]["current_step"] = "Generating story"
        
        analysis = question.get("analysis", {})
        prompt_template = question.get("prompt_template", "")
        
        if not prompt_template:
            error_msg = "Prompt template not found. Analysis may have failed."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        question_data = {
            "text": question["text"],
            "options": question.get("options"),
            **analysis
        }
        logger.debug(f"Question data prepared for story generation: {json.dumps(question_data, indent=2)}")
        
        # Get LLM service (initialize if needed)
        service = llm_service if llm_service is not None else get_llm_service()
        logger.info("Calling LLM service for story generation...")
        
        story_data = service.generate_story(question_data, prompt_template)
        questions_store[question_id]["story"] = story_data
        logger.info(f"Story generated successfully - Title: {story_data.get('story_title', 'Untitled')}")
        logger.debug(f"Story has {len(story_data.get('question_flow', []))} questions in flow")
        logger.debug(f"Story context: {story_data.get('story_context', '')[:200]}...")
        
        # Step 3: Generate HTML
        logger.info("-" * 80)
        logger.info("STEP 3: HTML GENERATION")
        logger.info("-" * 80)
        process_statuses[process_id]["progress"] = 60
        process_statuses[process_id]["current_step"] = "Creating visualization"
        
        logger.info("Calling LLM service for HTML generation...")
        html_content = service.generate_html(story_data)
        logger.info(f"HTML generated successfully - Length: {len(html_content)} characters")
        logger.debug(f"HTML preview (first 1000 chars): {html_content[:1000]}...")
        
        # Step 4: Store visualization
        logger.info("-" * 80)
        logger.info("STEP 4: STORING VISUALIZATION")
        logger.info("-" * 80)
        visualization_id = str(uuid.uuid4())
        from app.routes.progress import visualizations_store
        visualizations_store[visualization_id] = {
            "id": visualization_id,
            "html": html_content,
            "question_data": story_data,
            "question_id": question_id
        }
        logger.info(f"Visualization stored successfully - ID: {visualization_id}")
        logger.debug(f"Visualization store now has {len(visualizations_store)} items")
        
        # Complete
        process_statuses[process_id]["progress"] = 100
        process_statuses[process_id]["status"] = "completed"
        process_statuses[process_id]["current_step"] = "Complete"
        process_statuses[process_id]["visualization_id"] = visualization_id
        
        logger.info("=" * 80)
        logger.info(f"PIPELINE COMPLETE - Process ID: {process_id}, Visualization ID: {visualization_id}")
        logger.info("=" * 80)
        
    except Exception as e:
        error_msg = str(e)
        logger.error("=" * 80)
        logger.error(f"PIPELINE ERROR - Process ID: {process_id}")
        logger.error(f"Error: {error_msg}")
        logger.error("=" * 80, exc_info=True)
        process_statuses[process_id]["status"] = "error"
        process_statuses[process_id]["error_message"] = error_msg
        process_statuses[process_id]["progress"] = 0
        process_statuses[process_id]["current_step"] = f"Error: {error_msg[:50]}"

@router.post("/process/{question_id}")
async def start_processing(question_id: str, background_tasks: BackgroundTasks):
    """Start processing pipeline for a question"""
    logger.info(f"[API] /process/{question_id} - Request received")
    
    if question_id not in questions_store:
        logger.error(f"[API] Question {question_id} not found")
        raise HTTPException(status_code=404, detail="Question not found")
    
    process_id = str(uuid.uuid4())
    logger.info(f"[API] Starting processing pipeline - process_id={process_id}, question_id={question_id}")
    
    # Start background processing
    background_tasks.add_task(process_pipeline, process_id, question_id)
    logger.info(f"[API] Background task added for process_id={process_id}")
    
    return {
        "process_id": process_id,
        "question_id": question_id,
        "message": "Processing started"
    }

@router.get("/visualization/{visualization_id}")
async def get_visualization(visualization_id: str):
    """Get generated visualization"""
    from app.routes.progress import visualizations_store
    
    if visualization_id not in visualizations_store:
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    visualization = visualizations_store[visualization_id]
    
    return {
        "id": visualization["id"],
        "html": visualization["html"],
        "question_data": visualization["question_data"]
    }

@router.post("/check-answer/{visualization_id}")
async def check_answer(visualization_id: str, answer_data: dict):
    """Check if answer is correct"""
    from app.routes.progress import visualizations_store
    
    question_number = answer_data.get("questionNumber")
    selected_answer = answer_data.get("selectedAnswer")
    logger.info(f"Check answer request - Visualization: {visualization_id}, Question: {question_number}, Answer: {selected_answer}")
    
    if visualization_id not in visualizations_store:
        logger.warning(f"Visualization not found: {visualization_id}")
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    visualization = visualizations_store[visualization_id]
    question_data = visualization["question_data"]
    
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

