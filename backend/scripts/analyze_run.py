#!/usr/bin/env python3
"""Analyze a specific run and show what happened at each stage"""
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db import models
from app.repositories.process_repository import ProcessRepository
from app.repositories.pipeline_step_repository import PipelineStepRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.story_repository import StoryRepository
from app.repositories.game_blueprint_repository import GameBlueprintRepository

def analyze_run(run_id: str = None, process_id: str = None):
    """Analyze a specific run or the latest run"""
    db = SessionLocal()
    
    try:
        # If process_id is provided, use it directly
        if process_id:
            target_process = ProcessRepository.get_by_id(db, process_id)
            if not target_process:
                print(f"Process {process_id} not found in database.")
                return
        else:
            # Get all processes, ordered by start time
            processes = db.query(models.Process).order_by(models.Process.started_at.desc()).all()
            
            if not processes:
                print("No processes found in database.")
                return
            
            # If run_id specified, find matching process
            if run_id:
                # Try to find process that matches the run time
                target_process = None
                for process in processes:
                    # Check if process started around the run time
                    if run_id in str(process.started_at):
                        target_process = process
                        break
                
                if not target_process:
                    print(f"Could not find process matching run {run_id}")
                    print(f"Available processes (showing first 5):")
                    for p in processes[:5]:
                        print(f"  - {p.id} (started: {p.started_at})")
                    return
            else:
                # Use the most recent process
                target_process = processes[0]
        
        print("=" * 80)
        print(f"PROCESS ANALYSIS: {target_process.id}")
        print("=" * 80)
        print(f"Status: {target_process.status}")
        print(f"Progress: {target_process.progress}%")
        print(f"Current Step: {target_process.current_step}")
        print(f"Started: {target_process.started_at}")
        print(f"Completed: {target_process.completed_at}")
        if target_process.error_message:
            print(f"Error: {target_process.error_message}")
        print()
        
        # Get question
        question = QuestionRepository.get_by_id(db, target_process.question_id)
        if question:
            print("=" * 80)
            print("QUESTION")
            print("=" * 80)
            print(f"ID: {question.id}")
            print(f"Text: {question.text[:200]}..." if len(question.text) > 200 else f"Text: {question.text}")
            print(f"Options: {question.options}")
            print()
        
        # Get all steps
        steps = PipelineStepRepository.get_by_process_id(db, target_process.id)
        
        print("=" * 80)
        print(f"PIPELINE STEPS ({len(steps)} total)")
        print("=" * 80)
        
        for i, step in enumerate(steps, 1):
            print(f"\n--- Step {step.step_number}: {step.step_name} ---")
            print(f"Status: {step.status}")
            print(f"Started: {step.started_at}")
            print(f"Completed: {step.completed_at}")
            
            if step.completed_at and step.started_at:
                duration = (step.completed_at - step.started_at).total_seconds()
                print(f"Duration: {duration:.2f} seconds")
            
            if step.error_message:
                print(f"Error: {step.error_message}")
            
            if step.retry_count > 0:
                print(f"Retries: {step.retry_count}")
            
            # Show detailed input data
            if step.input_data:
                print(f"\nINPUT DATA:")
                input_data = step.input_data.copy()
                # Remove large binary data
                if 'file_content' in input_data:
                    input_data['file_content'] = f"<binary data: {len(input_data.get('file_content', ''))} bytes>"
                print(json.dumps(input_data, indent=2, default=str))
            
            # Show detailed output data
            if step.output_data:
                print(f"\nOUTPUT DATA:")
                print(json.dumps(step.output_data, indent=2, default=str))
            
            if step.validation_result:
                print(f"\nVALIDATION RESULT:")
                print(json.dumps(step.validation_result, indent=2))
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        completed_steps = [s for s in steps if s.status == "completed"]
        failed_steps = [s for s in steps if s.status == "error"]
        skipped_steps = [s for s in steps if s.status == "skipped"]
        
        print(f"Total Steps: {len(steps)}")
        print(f"Completed: {len(completed_steps)}")
        print(f"Failed: {len(failed_steps)}")
        print(f"Skipped: {len(skipped_steps)}")
        
        if completed_steps:
            total_duration = sum(
                (s.completed_at - s.started_at).total_seconds()
                for s in completed_steps
                if s.completed_at and s.started_at
            )
            print(f"Total Duration: {total_duration:.2f} seconds")
        
        # Check for visualization
        visualization = db.query(models.Visualization).filter(
            models.Visualization.process_id == target_process.id
        ).first()
        
        # Get story data
        story = StoryRepository.get_by_question_id(db, target_process.question_id)
        if story:
            print("\n" + "=" * 80)
            print("STORY DATA")
            print("=" * 80)
            print(f"Story ID: {story.id}")
            print(f"Story Title: {story.story_title}")
            print(f"\nStory Context:\n{story.story_context}")
            print(f"\nLearning Intuition:\n{story.learning_intuition}")
            print(f"\nVisual Metaphor:\n{story.visual_metaphor}")
            print(f"\nInteraction Design:\n{story.interaction_design}")
            if story.visual_elements:
                print(f"\nVisual Elements: {json.dumps(story.visual_elements, indent=2)}")
            if story.question_flow:
                print(f"\nQuestion Flow: {json.dumps(story.question_flow, indent=2)}")
            print(f"\nPrimary Question: {story.primary_question}")
            if story.learning_alignment:
                print(f"\nLearning Alignment: {json.dumps(story.learning_alignment, indent=2)}")
            if story.animation_cues:
                print(f"\nAnimation Cues: {json.dumps(story.animation_cues, indent=2)}")
        
        # Get blueprint data
        if visualization and visualization.blueprint_id:
            blueprint = db.query(models.GameBlueprint).filter(
                models.GameBlueprint.id == visualization.blueprint_id
            ).first()
            if blueprint:
                print("\n" + "=" * 80)
                print("BLUEPRINT DATA")
                print("=" * 80)
                print(f"Blueprint ID: {blueprint.id}")
                print(f"Template Type: {blueprint.template_type}")
                print(f"\nFull Blueprint JSON:")
                print(json.dumps(blueprint.blueprint_json, indent=2, default=str))
                if blueprint.assets_json:
                    print(f"\nAssets JSON:")
                    print(json.dumps(blueprint.assets_json, indent=2, default=str))
        
        # Find template routing step to show which template was selected
        template_routing_step = next((s for s in steps if s.step_name == "template_routing"), None)
        if template_routing_step and template_routing_step.output_data:
            print("\n" + "=" * 80)
            print("TEMPLATE ROUTING DECISION")
            print("=" * 80)
            routing_output = template_routing_step.output_data
            print(f"Selected Template: {routing_output.get('templateType', 'N/A')}")
            print(f"Confidence: {routing_output.get('confidence', 'N/A')}")
            print(f"Rationale: {routing_output.get('rationale', 'N/A')}")
        
        # Find strategy creation step to show strategy details
        strategy_step = next((s for s in steps if s.step_name == "strategy_creation"), None)
        if strategy_step and strategy_step.output_data:
            print("\n" + "=" * 80)
            print("STRATEGY DETAILS")
            print("=" * 80)
            strategy_output = strategy_step.output_data
            print(f"Game Format: {strategy_output.get('game_format', 'N/A')}")
            print(f"Format Rationale: {strategy_output.get('format_rationale', 'N/A')}")
            print(f"Difficulty: {strategy_output.get('difficulty', 'N/A')}")
            if strategy_output.get('storyline'):
                print(f"\nStoryline: {json.dumps(strategy_output['storyline'], indent=2)}")
            if strategy_output.get('interactions'):
                print(f"\nInteractions: {json.dumps(strategy_output['interactions'], indent=2)}")
            if strategy_output.get('prompt_template'):
                print(f"\nPrompt Template Used: {strategy_output['prompt_template'][:200]}...")
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Check if it's a UUID (process ID) or run ID
        if len(arg) == 36 and arg.count('-') == 4:
            # Looks like a UUID
            analyze_run(process_id=arg)
        else:
            # Treat as run_id
            analyze_run(run_id=arg)
    else:
        analyze_run()

