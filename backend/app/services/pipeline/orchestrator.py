"""Pipeline Orchestrator - Executes pipeline steps with validation and tracking"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import Process, PipelineStep
from app.repositories.process_repository import ProcessRepository
from app.repositories.pipeline_step_repository import PipelineStepRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.story_repository import StoryRepository
from app.repositories.visualization_repository import VisualizationRepository
from app.repositories.game_blueprint_repository import GameBlueprintRepository
from app.services.pipeline.layer1_input import DocumentParserService, QuestionExtractorService
from app.services.pipeline.layer2_classification import ClassificationOrchestrator
from app.services.pipeline.layer2_template_router import TemplateRouter
from app.services.pipeline.layer3_strategy import StrategyOrchestrator
from app.services.pipeline.layer4_generation import GenerationOrchestrator
from app.services.pipeline.validators import get_validator
from app.services.pipeline.retry_handler import RetryHandler
from app.utils.logger import setup_logger

logger = setup_logger("orchestrator")

class PipelineOrchestrator:
    """Orchestrates the complete pipeline execution"""
    
    # Define pipeline steps
    PIPELINE_STEPS = [
        {"name": "document_parsing", "number": 1, "layer": 1},
        {"name": "question_extraction", "number": 2, "layer": 1},
        {"name": "question_analysis", "number": 3, "layer": 2},
        {"name": "template_routing", "number": 4, "layer": 2},
        {"name": "strategy_creation", "number": 5, "layer": 3},
        {"name": "story_generation", "number": 6, "layer": 4},
        {"name": "blueprint_generation", "number": 7, "layer": 4},
        {"name": "asset_planning", "number": 8, "layer": 4},
        {"name": "asset_generation", "number": 9, "layer": 4},
    ]
    
    def __init__(self, db: Session):
        self.db = db
        self.retry_handler = RetryHandler(max_retries=3, initial_delay=1.0)
        
        # Initialize services
        self.document_parser = DocumentParserService()
        self.question_extractor = QuestionExtractorService()
        self.classifier = ClassificationOrchestrator()
        self.template_router = TemplateRouter()
        self.strategy_orchestrator = StrategyOrchestrator()
        self.generation_orchestrator = GenerationOrchestrator()
    
    def execute_pipeline(
        self,
        process_id: str,
        question_id: str,
        file_content: bytes = None,
        filename: str = None
    ) -> Dict[str, Any]:
        """Execute complete pipeline for a question"""
        logger.info(f"Starting pipeline execution - Process: {process_id}, Question: {question_id}")
        
        try:
            # Update process status
            ProcessRepository.update_status(
                self.db, process_id, "processing", progress=0, current_step="Initializing"
            )
            
            # Get question
            question = QuestionRepository.get_by_id(self.db, question_id)
            if not question:
                raise ValueError(f"Question {question_id} not found")
            
            # Track pipeline state
            pipeline_state = {
                "question_id": question_id,
                "question_text": question.text,
                "question_options": question.options,
                "file_content": file_content,
                "filename": filename,
                "parsed_data": None,
                "extracted_question": None,
                "analysis": None,
                "template_type": None,
                "strategy": None,
                "story": None,
                "blueprint": None,
                "assets": None
            }
            
            # Execute each step
            last_completed_step = PipelineStepRepository.get_last_completed_step(self.db, process_id)
            start_from_step = (last_completed_step.step_number + 1) if last_completed_step else 1
            
            for step_def in self.PIPELINE_STEPS:
                if step_def["number"] < start_from_step:
                    logger.info(f"Skipping step {step_def['number']} - already completed")
                    continue
                
                step_result = self._execute_step(
                    process_id,
                    step_def,
                    pipeline_state
                )
                
                if not step_result["success"]:
                    logger.error(f"Step {step_def['number']} failed: {step_result.get('error')}")
                    ProcessRepository.update_status(
                        self.db,
                        process_id,
                        "error",
                        current_step=step_def["name"],
                        error_message=step_result.get("error")
                    )
                    return step_result
                
                # Update pipeline state with step output
                pipeline_state.update(step_result.get("state_updates", {}))
                
                # Update progress
                progress = int((step_def["number"] / len(self.PIPELINE_STEPS)) * 100)
                ProcessRepository.update_status(
                    self.db,
                    process_id,
                    "processing",
                    progress=progress,
                    current_step=step_def["name"]
                )
            
            # Store final results
            visualization_id = self._store_results(process_id, question_id, pipeline_state)
            
            # Mark process as completed
            ProcessRepository.update_status(
                self.db,
                process_id,
                "completed",
                progress=100,
                current_step="Complete"
            )
            
            logger.info(f"Pipeline completed successfully - Process: {process_id}, Visualization: {visualization_id}")
            
            return {
                "success": True,
                "process_id": process_id,
                "visualization_id": visualization_id
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            ProcessRepository.update_status(
                self.db,
                process_id,
                "error",
                error_message=str(e)
            )
            raise
    
    def _execute_step(
        self,
        process_id: str,
        step_def: Dict[str, Any],
        pipeline_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single pipeline step"""
        step_name = step_def["name"]
        step_number = step_def["number"]
        
        logger.info(f"Executing step {step_number}: {step_name}")
        
        # Create step record
        step = PipelineStepRepository.create(
            self.db,
            process_id,
            step_name,
            step_number,
            input_data=self._sanitize_for_storage(pipeline_state)
        )
        
        try:
            # Update step status to processing
            PipelineStepRepository.update_status(
                self.db, step.id, "processing"
            )
            
            # Execute step based on name
            step_result = None
            state_updates = {}
            
            if step_name == "document_parsing":
                if pipeline_state.get("file_content") and pipeline_state.get("filename"):
                    result = self.document_parser.parse_document(
                        pipeline_state["file_content"],
                        pipeline_state["filename"]
                    )
                    pipeline_state["parsed_data"] = result["data"]
                    step_result = result
                else:
                    # Skip if no file content (question already in DB)
                    PipelineStepRepository.update_status(
                        self.db, step.id, "skipped",
                        output_data={"message": "File content not provided, using existing question"}
                    )
                    return {"success": True, "state_updates": {}}
            
            elif step_name == "question_extraction":
                if pipeline_state.get("parsed_data"):
                    text = pipeline_state["parsed_data"].get("full_text") or pipeline_state["parsed_data"].get("text")
                    result = self.question_extractor.extract_question(
                        text,
                        pipeline_state.get("filename")
                    )
                    pipeline_state["extracted_question"] = result["data"]
                    step_result = result
                else:
                    # Use existing question from DB
                    extracted = {
                        "text": pipeline_state["question_text"],
                        "options": pipeline_state["question_options"],
                        "file_type": "existing"
                    }
                    pipeline_state["extracted_question"] = extracted
                    step_result = {"success": True, "data": extracted}
            
            elif step_name == "question_analysis":
                question_text = pipeline_state.get("extracted_question", {}).get("text") or pipeline_state["question_text"]
                question_options = pipeline_state.get("extracted_question", {}).get("options") or pipeline_state["question_options"]
                result = self.classifier.analyze_question(question_text, question_options)
                analysis_data = result["data"]
                pipeline_state["analysis"] = analysis_data
                
                # Store analysis in database
                from app.db.models import QuestionAnalysis
                question_id = pipeline_state["question_id"]
                existing_analysis = self.db.query(QuestionAnalysis).filter(
                    QuestionAnalysis.question_id == question_id
                ).first()
                
                if existing_analysis:
                    # Update existing
                    existing_analysis.question_type = analysis_data["question_type"]
                    existing_analysis.subject = analysis_data["subject"]
                    existing_analysis.difficulty = analysis_data["difficulty"]
                    existing_analysis.key_concepts = analysis_data.get("key_concepts", [])
                    existing_analysis.intent = analysis_data.get("intent", "")
                else:
                    # Create new
                    analysis = QuestionAnalysis(
                        question_id=question_id,
                        question_type=analysis_data["question_type"],
                        subject=analysis_data["subject"],
                        difficulty=analysis_data["difficulty"],
                        key_concepts=analysis_data.get("key_concepts", []),
                        intent=analysis_data.get("intent", "")
                    )
                    self.db.add(analysis)
                
                self.db.commit()
                step_result = result
            
            elif step_name == "template_routing":
                result = self.template_router.route_template(
                    pipeline_state["question_text"],
                    pipeline_state["analysis"]
                )
                routing_data = result["data"]
                template_type = routing_data.get("templateType")
                confidence = routing_data.get("confidence", 0)
                rationale = routing_data.get("rationale", "")
                pipeline_state["template_type"] = template_type
                
                # Log template routing event
                question_id = pipeline_state.get("question_id", "unknown")
                logger.info(
                    f"event=template_routed question_id={question_id} template_type={template_type} "
                    f"confidence={confidence} rationale={rationale[:100]}"
                )
                
                step_result = result
            
            elif step_name == "strategy_creation":
                question_data = {
                    "text": pipeline_state["question_text"],
                    "options": pipeline_state["question_options"],
                    **pipeline_state["analysis"]
                }
                result = self.strategy_orchestrator.create_strategy(
                    pipeline_state["question_text"],
                    pipeline_state["analysis"]
                )
                pipeline_state["strategy"] = result["data"]
                step_result = result
            
            elif step_name == "story_generation":
                question_data = {
                    "text": pipeline_state["question_text"],
                    "options": pipeline_state["question_options"],
                    **pipeline_state["analysis"]
                }
                result = self.generation_orchestrator.story_generator.generate(
                    question_data,
                    pipeline_state["strategy"]["prompt_template"],
                    pipeline_state["strategy"],
                    pipeline_state.get("template_type")
                )
                pipeline_state["story"] = result["data"]
                step_result = result
            
            elif step_name == "blueprint_generation":
                result = self.generation_orchestrator.blueprint_generator.generate(
                    pipeline_state["story"],
                    pipeline_state["template_type"]
                )
                blueprint_data = result["data"]
                template_type = pipeline_state["template_type"]
                is_valid = result.get("valid", True)
                error_fields = result.get("error_fields", [])
                pipeline_state["blueprint"] = blueprint_data
                
                # Log blueprint generation event
                question_id = pipeline_state.get("question_id", "unknown")
                logger.info(
                    f"event=blueprint_generated question_id={question_id} template_type={template_type} "
                    f"valid={is_valid} error_fields={error_fields}"
                )
                
                step_result = result
            
            elif step_name == "asset_planning":
                asset_requests = self.generation_orchestrator.asset_planner.plan_assets(
                    pipeline_state["blueprint"]
                )
                asset_request_count = len(asset_requests)
                pipeline_state["asset_requests"] = asset_requests
                
                # Log asset planning event
                question_id = pipeline_state.get("question_id", "unknown")
                logger.info(
                    f"event=assets_planned question_id={question_id} "
                    f"asset_request_count={asset_request_count}"
                )
                
                step_result = {
                    "success": True,
                    "data": {"asset_request_count": asset_request_count}
                }
            
            elif step_name == "asset_generation":
                asset_urls = self.generation_orchestrator.asset_generator.generate_assets(
                    pipeline_state["asset_requests"]
                )
                # Inject asset URLs into blueprint
                pipeline_state["blueprint"] = self.generation_orchestrator.asset_generator.inject_asset_urls(
                    pipeline_state["blueprint"],
                    asset_urls
                )
                pipeline_state["assets"] = asset_urls
                
                # Log asset generation events
                question_id = pipeline_state.get("question_id", "unknown")
                for purpose, url in asset_urls.items():
                    logger.info(
                        f"event=asset_generated question_id={question_id} asset_type=image "
                        f"purpose={purpose} url={url[:100]}"
                    )
                
                step_result = {
                    "success": True,
                    "data": {"asset_urls": asset_urls}
                }
            
            # Validate step output
            validator = get_validator(step_name)
            if validator and step_result:
                validation_result = validator.validate(step_result.get("data", {}))
                if not validation_result.is_valid:
                    raise ValueError(f"Step validation failed: {', '.join(validation_result.errors)}")
            
            # Update step as completed
            PipelineStepRepository.update_status(
                self.db,
                step.id,
                "completed",
                output_data=self._sanitize_for_storage(step_result.get("data", {})),
                validation_result=step_result.get("validation") if step_result else None
            )
            
            logger.info(f"Step {step_number} completed successfully: {step_name}")
            
            return {
                "success": True,
                "state_updates": state_updates
            }
            
        except Exception as e:
            logger.error(f"Step {step_number} failed: {e}", exc_info=True)
            
            # Update step as error
            PipelineStepRepository.update_status(
                self.db,
                step.id,
                "error",
                error_message=str(e)
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _store_results(
        self,
        process_id: str,
        question_id: str,
        pipeline_state: Dict[str, Any]
    ) -> str:
        """Store final results in database"""
        logger.info("Storing pipeline results")
        
        # Store story if generated
        story_data = pipeline_state.get("story")
        if story_data:
            StoryRepository.create(self.db, question_id, story_data)
        
        # Store blueprint if generated
        blueprint_data = pipeline_state.get("blueprint")
        assets_data = pipeline_state.get("assets", {})
        blueprint_id = None
        
        if blueprint_data:
            template_type = pipeline_state.get("template_type", "SEQUENCE_BUILDER")
            blueprint = GameBlueprintRepository.create(
                self.db,
                question_id,
                template_type,
                blueprint_data,
                assets_data
            )
            blueprint_id = blueprint.id
            
            # Log blueprint saved event
            logger.info(
                f"event=blueprint_saved blueprint_id={blueprint_id} question_id={question_id} "
                f"template_type={template_type}"
            )
        
        # Store visualization (backward compatibility - may have HTML or blueprint)
        html_content = pipeline_state.get("html", "")
        visualization = VisualizationRepository.create(
            self.db,
            process_id,
            question_id,
            html_content,
            story_data or {}
        )
        
        # Link blueprint to visualization if available
        if blueprint_id:
            visualization.blueprint_id = blueprint_id
            self.db.commit()
        
        return visualization.id
    
    def _sanitize_for_storage(self, data: Any) -> Any:
        """Sanitize data for database storage (remove large binary data, etc.)"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key in ["file_content"]:
                    # Don't store binary data
                    sanitized[key] = f"<binary data: {len(value) if value else 0} bytes>"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_for_storage(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_for_storage(item) for item in data]
        else:
            return data
    
    def retry_step(self, step_id: str) -> Dict[str, Any]:
        """Retry a failed step"""
        logger.info(f"Retrying step: {step_id}")
        
        step = PipelineStepRepository.get_by_id(self.db, step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        if step.status != "error":
            raise ValueError(f"Step {step_id} is not in error state")
        
        # Increment retry count
        PipelineStepRepository.increment_retry(self.db, step_id)
        
        # Get process and question
        process = ProcessRepository.get_by_id(self.db, step.process_id)
        question = QuestionRepository.get_by_id(self.db, process.question_id)
        
        # Rebuild pipeline state from completed steps
        pipeline_state = {
            "question_id": question.id,
            "question_text": question.text,
            "question_options": question.options,
        }
        
        # Get all completed steps to rebuild state
        completed_steps = [
            s for s in PipelineStepRepository.get_by_process_id(self.db, step.process_id)
            if s.status == "completed" and s.step_number < step.step_number
        ]
        
        # Rebuild state from completed steps
        for completed_step in completed_steps:
            if completed_step.output_data:
                pipeline_state.update(completed_step.output_data)
        
        # Find step definition
        step_def = next(
            (s for s in self.PIPELINE_STEPS if s["name"] == step.step_name),
            None
        )
        
        if not step_def:
            raise ValueError(f"Unknown step: {step.step_name}")
        
        # Execute step
        result = self._execute_step(process.id, step_def, pipeline_state)
        
        return result

