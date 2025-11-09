"""Template Registry - Loads and manages template metadata"""
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from app.utils.logger import setup_logger

logger = setup_logger("template_registry")

class TemplateRegistry:
    """Registry for game template metadata"""
    
    # All 18 template types
    TEMPLATE_TYPES = [
        "LABEL_DIAGRAM",
        "IMAGE_HOTSPOT_QA",
        "SEQUENCE_BUILDER",
        "TIMELINE_ORDER",
        "BUCKET_SORT",
        "MATCH_PAIRS",
        "MATRIX_MATCH",
        "PARAMETER_PLAYGROUND",
        "GRAPH_SKETCHER",
        "VECTOR_SANDBOX",
        "STATE_TRACER_CODE",
        "SPOT_THE_MISTAKE",
        "CONCEPT_MAP_BUILDER",
        "MICRO_SCENARIO_BRANCHING",
        "DESIGN_CONSTRAINT_BUILDER",
        "PROBABILITY_LAB",
        "BEFORE_AFTER_TRANSFORMER",
        "GEOMETRY_BUILDER"
    ]
    
    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize template registry"""
        if templates_dir is None:
            # Default to app/templates relative to this file
            base_dir = Path(__file__).parent.parent
            templates_dir = str(base_dir / "templates")
        
        self.templates_dir = Path(templates_dir)
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all template JSON files"""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory does not exist: {self.templates_dir}")
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for template_type in self.TEMPLATE_TYPES:
            template_file = self.templates_dir / f"{template_type}.json"
            if template_file.exists():
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        self._templates[template_type] = template_data
                        logger.info(f"Loaded template: {template_type}")
                except Exception as e:
                    logger.error(f"Failed to load template {template_type}: {e}")
            else:
                logger.warning(f"Template file not found: {template_file}")
    
    def get_template(self, template_type: str) -> Optional[Dict[str, Any]]:
        """Get template metadata by type"""
        return self._templates.get(template_type)
    
    def list_templates(self) -> List[str]:
        """List all available template types"""
        return list(self._templates.keys())
    
    def validate_blueprint(self, blueprint: Dict[str, Any], template_type: str) -> tuple[bool, List[str]]:
        """Validate blueprint against template schema"""
        template = self.get_template(template_type)
        if not template:
            return False, [f"Template {template_type} not found"]
        
        errors = []
        schema = template.get("blueprintSchema", {})
        required_fields = schema.get("requiredFields", [])
        
        # Check required fields
        for field in required_fields:
            if field not in blueprint:
                errors.append(f"Missing required field: {field}")
        
        # Check templateType matches
        if blueprint.get("templateType") != template_type:
            errors.append(f"templateType mismatch: expected {template_type}, got {blueprint.get('templateType')}")
        
        # CRITICAL: Reject blueprints with UI hints or animationCues (Smart Component, Dumb Blueprint pattern)
        # Blueprints must contain DATA ONLY - no UI hints, no animation descriptions.
        # React components are "smart" and decide how to render and animate based on data.
        
        # Check for animationCues object
        if "animationCues" in blueprint:
            errors.append("Blueprint contains 'animationCues' object. Blueprints must be data-only - components have built-in animations. Remove animationCues and let components handle animations via CSS transitions.")
        
        # Helper function to recursively check for UI hints
        def check_for_ui_hints(obj, path="", depth=0):
            """Recursively check for UI hint fields"""
            if depth > 5:  # Prevent infinite recursion
                return
            
            if isinstance(obj, dict):
                # Check for common UI hint field names
                ui_hint_fields = ["type", "component", "widget", "control", "uiType", "componentType"]
                for field in ui_hint_fields:
                    if field in obj:
                        field_path = f"{path}.{field}" if path else field
                        errors.append(f"Blueprint contains UI hint field '{field_path}'. Blueprints must be data-only - components decide UI rendering. Use data fields like 'initialValue', 'goalValue', 'label', etc. instead.")
                
                # Recursively check nested objects
                for key, value in obj.items():
                    if key not in ["templateType", "title", "narrativeIntro"]:  # Skip top-level metadata
                        new_path = f"{path}.{key}" if path else key
                        check_for_ui_hints(value, new_path, depth + 1)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    check_for_ui_hints(item, new_path, depth + 1)
        
        # Check entire blueprint for UI hints
        check_for_ui_hints(blueprint)
        
        return len(errors) == 0, errors
    
    def get_template_types(self) -> List[str]:
        """Get list of all template types"""
        return self.TEMPLATE_TYPES.copy()

# Global registry instance
_registry_instance: Optional[TemplateRegistry] = None

def get_registry() -> TemplateRegistry:
    """Get global template registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = TemplateRegistry()
    return _registry_instance

