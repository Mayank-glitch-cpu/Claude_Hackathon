from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuestionInput(BaseModel):
    text: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None

class QuestionAnalysis(BaseModel):
    question_type: str
    subject: str
    difficulty: str
    key_concepts: List[str]
    intent: str

class StoryData(BaseModel):
    story_title: str
    story_context: str
    learning_intuition: str
    visual_metaphor: str
    interaction_design: str
    visual_elements: List[str]
    question_flow: List[Dict[str, Any]]
    primary_question: str
    learning_alignment: str
    animation_cues: str
    question_implementation_notes: str

class VisualizationData(BaseModel):
    html: str
    question_data: StoryData

class ProcessStatus(BaseModel):
    process_id: str
    status: str  # "processing", "completed", "error"
    progress: int  # 0-100
    current_step: str
    visualization_id: Optional[str] = None
    error_message: Optional[str] = None

