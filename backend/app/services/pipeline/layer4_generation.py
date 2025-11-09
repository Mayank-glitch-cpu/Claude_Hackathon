"""Layer 4: Multi-Modal Content Generation"""
from typing import Dict, Any, Optional
from pathlib import Path
from app.services.llm_service import LLMService
from app.services.pipeline.validators import StoryValidator, HTMLValidator, ValidationResult
from app.services.template_registry import get_registry
from app.utils.logger import setup_logger
import json

logger = setup_logger("layer4_generation")

class StoryGenerator:
    """Generate story data from question and strategy"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.validator = StoryValidator()
    
    def generate(
        self,
        question_data: Dict[str, Any],
        prompt_template: str,
        strategy: Dict[str, Any] = None,
        template_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate complete story data"""
        logger.info(f"Generating story data (template: {template_type})")
        
        # Load base story prompt
        base_prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "story_base.md"
        try:
            with open(base_prompt_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
        except Exception as e:
            logger.warning(f"Failed to load story_base.md, using provided template: {e}")
            base_prompt = prompt_template
        
        # Load template-specific supplement if template_type is provided
        system_prompt = base_prompt
        if template_type:
            template_supplement_path = Path(__file__).parent.parent.parent.parent / "prompts" / "story_templates" / f"{template_type}.txt"
            try:
                with open(template_supplement_path, 'r', encoding='utf-8') as f:
                    template_supplement = f.read()
                    system_prompt = base_prompt + "\n\n" + template_supplement
                    logger.info(f"Loaded template supplement for {template_type}")
            except Exception as e:
                logger.warning(f"Failed to load template supplement for {template_type}: {e}")
                # Use base prompt only
        
        user_prompt = f"""Generate a story-based visualization for the following question:

Question: {question_data.get('text', '')}
Options: {question_data.get('options', [])}
Type: {question_data.get('question_type', 'reasoning')}
Subject: {question_data.get('subject', 'General')}
Difficulty: {question_data.get('difficulty', 'intermediate')}
Key Concepts: {question_data.get('key_concepts', [])}
Intent: {question_data.get('intent', '')}

Game Format: {strategy.get('game_format', 'quiz') if strategy else 'quiz'}
Storyline: {json.dumps(strategy.get('storyline', {}), indent=2) if strategy else 'None'}
TemplateType: {template_type if template_type else 'Not specified'}

Follow the schema and requirements in the system prompt. Respond with ONLY valid JSON matching the output schema."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Try OpenAI first, fallback to Anthropic
            try:
                logger.info("Attempting story generation with OpenAI...")
                response = self.llm_service.call_llm(messages, use_anthropic=False)
            except Exception as e:
                logger.warning(f"OpenAI failed, trying Anthropic: {e}")
                response = self.llm_service.call_llm(messages, use_anthropic=True)
            
            # Extract JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            story_data = json.loads(response)
            
            # Log the raw story data for debugging (first 500 chars)
            logger.debug(f"Raw story data received: {json.dumps(story_data, indent=2)[:500]}...")
            
            # Normalize question_flow field names for consistency
            # The prompt schema uses "intuitive_question", but we normalize to "question_text" for consistency
            if "question_flow" in story_data and isinstance(story_data["question_flow"], list):
                for q in story_data["question_flow"]:
                    if isinstance(q, dict):
                        # Normalize field names - use question_text as standard
                        # Priority: intuitive_question (from schema) > question_text > text > question > content
                        if "intuitive_question" in q and "question_text" not in q:
                            q["question_text"] = q.pop("intuitive_question")
                        elif "text" in q and "question_text" not in q:
                            q["question_text"] = q.pop("text")
                        elif "question" in q and "question_text" not in q:
                            q["question_text"] = q.pop("question")
                        elif "content" in q and "question_text" not in q:
                            q["question_text"] = q.pop("content")
            
            # Validate story data
            validation_result = self.validator.validate(story_data)
            
            if not validation_result.is_valid:
                logger.error(f"Story validation failed: {validation_result.errors}")
                raise ValueError(f"Story validation failed: {', '.join(validation_result.errors)}")
            
            if validation_result.warnings:
                logger.warning(f"Story validation warnings: {validation_result.warnings}")
            
            logger.info(f"Story generated successfully - Title: {story_data.get('story_title', 'Untitled')}")
            
            # Log story generation event (if we have question_id context, it would be passed)
            # For now, log with template type
            logger.info(
                f"event=story_generated template_type={template_type or 'unknown'} "
                f"success=True token_count=unknown"
            )
            
            return {
                "success": True,
                "data": story_data,
                "validation": validation_result.to_dict()
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse story JSON: {e}")
            raise ValueError(f"Failed to parse story JSON: {e}")
        except Exception as e:
            logger.error(f"Story generation failed: {e}", exc_info=True)
            raise

class HTMLGenerator:
    """Generate HTML visualization from story data"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.validator = HTMLValidator()
    
    def generate(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HTML visualization"""
        logger.info("Generating HTML visualization")
        
        prompt = f"""Generate a complete, interactive HTML page for the following story-based visualization.

Story Data:
{json.dumps(story_data, indent=2)}

Requirements:
1. Questions must be prominently displayed at the top
2. Answer submission is required before showing results
3. Visual feedback on answers (green for correct, red for incorrect)
4. Interactive animations and visual elements
5. Responsive design
6. Include all CSS and JavaScript inline

Generate ONLY the HTML code, no markdown, no explanations."""
        
        messages = [
            {"role": "system", "content": "You are an expert web developer. Generate complete, functional HTML pages with inline CSS and JavaScript."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Try OpenAI first, fallback to Anthropic
            try:
                logger.info("Attempting HTML generation with OpenAI...")
                response = self.llm_service.call_llm(messages, use_anthropic=False)
            except Exception as e:
                logger.warning(f"OpenAI failed, trying Anthropic: {e}")
                response = self.llm_service.call_llm(messages, use_anthropic=True)
            
            # Extract HTML
            if "```html" in response:
                response = response.split("```html")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            # Validate HTML
            validation_result = self.validator.validate({"html": response})
            
            if not validation_result.is_valid:
                logger.error(f"HTML validation failed: {validation_result.errors}")
                raise ValueError(f"HTML validation failed: {', '.join(validation_result.errors)}")
            
            if validation_result.warnings:
                logger.warning(f"HTML validation warnings: {validation_result.warnings}")
            
            logger.info(f"HTML generated successfully - Length: {len(response)} chars")
            
            return {
                "success": True,
                "data": {"html": response},
                "validation": validation_result.to_dict()
            }
        except Exception as e:
            logger.error(f"HTML generation failed: {e}", exc_info=True)
            raise

class ImageGenerator:
    """Generate images for visualizations (Future: DALL-E integration)"""
    
    def __init__(self):
        # Placeholder for future image generation
        pass
    
    def generate(self, description: str) -> Dict[str, Any]:
        """Generate image from description"""
        logger.info("Image generation not yet implemented")
        # Future implementation
        return {
            "success": False,
            "message": "Image generation not yet implemented"
        }

class AnimationGenerator:
    """Generate animations (Future: Animation creation)"""
    
    def __init__(self):
        # Placeholder for future animation generation
        pass
    
    def generate(self, animation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate animation from specification"""
        logger.info("Animation generation not yet implemented")
        # Future implementation
        return {
            "success": False,
            "message": "Animation generation not yet implemented"
        }

class BlueprintGenerator:
    """Generate game blueprint JSON from story data and template"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.template_registry = get_registry()
        self._load_base_prompt()
    
    def _load_base_prompt(self):
        """Load base blueprint prompt"""
        prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "blueprint_base.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.base_prompt = f.read()
        except Exception as e:
            logger.error(f"Failed to load blueprint_base.md: {e}")
            self.base_prompt = """You are a Game Blueprint Generator. Generate JSON blueprints matching TypeScript interfaces."""
    
    def _load_ts_interface(self, template_type: str) -> str:
        """Load TypeScript interface for template"""
        interface_path = Path(__file__).parent.parent.parent.parent / "prompts" / "blueprint_templates" / f"{template_type}.ts.txt"
        try:
            with open(interface_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load TS interface for {template_type}: {e}")
            return f"// TypeScript interface for {template_type}"
    
    def _normalize_numeric_values(self, blueprint: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """Normalize numeric values: coerce string numbers to actual numbers"""
        def coerce_to_number(value: Any) -> Any:
            """Coerce value to number if it's a numeric string"""
            if isinstance(value, str):
                # Try to parse as float/int
                try:
                    # Check if it's a float
                    if '.' in value or 'e' in value.lower() or 'E' in value:
                        return float(value)
                    else:
                        # Try int first, fallback to float
                        return int(value)
                except (ValueError, TypeError):
                    return value
            return value
        
        def normalize_value(value: Any) -> Any:
            """Normalize a single value recursively"""
            if isinstance(value, dict):
                normalized = {}
                for key, val in value.items():
                    # Normalize numeric fields based on template type
                    if template_type == "PARAMETER_PLAYGROUND":
                        # For parameters: min, max, defaultValue should be numbers
                        if key in ["min", "max", "defaultValue"]:
                            normalized[key] = coerce_to_number(val)
                        # For tasks: targetValues should have numeric values
                        elif key == "targetValues" and isinstance(val, dict):
                            normalized[key] = {k: coerce_to_number(v) for k, v in val.items()}
                        # For parameters array: normalize each parameter
                        elif key == "parameters" and isinstance(val, list):
                            normalized[key] = [
                                {**param, "min": coerce_to_number(param.get("min", 0)),
                                 "max": coerce_to_number(param.get("max", 100)),
                                 "defaultValue": coerce_to_number(param.get("defaultValue", 0))}
                                if isinstance(param, dict) else normalize_value(param)
                                for param in val
                            ]
                        # For tasks array: normalize targetValues
                        elif key == "tasks" and isinstance(val, list):
                            normalized[key] = [
                                {**task, "targetValues": {k: coerce_to_number(v) for k, v in task.get("targetValues", {}).items()}}
                                if isinstance(task, dict) and "targetValues" in task else normalize_value(task)
                                for task in val
                            ]
                        else:
                            normalized[key] = normalize_value(val)
                    else:
                        normalized[key] = normalize_value(val)
                return normalized
            elif isinstance(value, list):
                return [normalize_value(item) for item in value]
            else:
                return value
        
        return normalize_value(blueprint)
    
    def generate(
        self,
        story_data: Dict[str, Any],
        template_type: str
    ) -> Dict[str, Any]:
        """Generate blueprint JSON from story data"""
        logger.info(f"Generating blueprint for template: {template_type}")
        
        # Get template metadata
        template_metadata = self.template_registry.get_template(template_type)
        if not template_metadata:
            raise ValueError(f"Template {template_type} not found in registry")
        
        # Load TypeScript interface
        ts_interface = self._load_ts_interface(template_type)
        
        # Build system prompt
        system_prompt = self.base_prompt + "\n\n" + ts_interface
        
        # Build user prompt
        user_prompt = f"""TemplateType: {template_type}

Template Metadata:
{json.dumps(template_metadata, indent=2)}

TypeScript interface for this template:

{ts_interface}

Story Data:
{json.dumps(story_data, indent=2)}

Generate a blueprint object that conforms EXACTLY to the TypeScript interface.
Do not include any fields that are not defined in the interface.
Do not wrap the response in any additional text."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Try OpenAI first, fallback to Anthropic
            try:
                logger.info("Attempting blueprint generation with OpenAI...")
                response = self.llm_service.call_llm(messages, use_anthropic=False)
            except Exception as e:
                logger.warning(f"OpenAI failed, trying Anthropic: {e}")
                response = self.llm_service.call_llm(messages, use_anthropic=True)
            
            # Extract JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            blueprint = json.loads(response)
            
            # Normalize numeric values: coerce string numbers to actual numbers
            # LLM may return strings like "10.5" instead of 10.5, which causes runtime errors
            blueprint = self._normalize_numeric_values(blueprint, template_type)
            
            # Ensure templateType matches (CRITICAL for frontend routing)
            if "templateType" not in blueprint or blueprint["templateType"] != template_type:
                logger.warning(f"Blueprint templateType mismatch: expected {template_type}, got {blueprint.get('templateType')}. Setting to {template_type}")
            blueprint["templateType"] = template_type
            
            # Validate that templateType is set correctly
            if blueprint.get("templateType") != template_type:
                logger.error(f"CRITICAL: Failed to set templateType in blueprint! Expected {template_type}, got {blueprint.get('templateType')}")
                raise ValueError(f"Failed to set templateType in blueprint: expected {template_type}")
            
            logger.info(f"Blueprint templateType set to: {blueprint['templateType']}")
            
            # Validate blueprint
            is_valid, errors = self.template_registry.validate_blueprint(blueprint, template_type)
            if not is_valid:
                logger.error(f"Blueprint validation failed: {errors}")
                raise ValueError(f"Blueprint validation failed: {', '.join(errors)}")
            
            logger.info(f"Blueprint generated successfully for {template_type}")
            
            return {
                "success": True,
                "data": blueprint,
                "valid": True,
                "error_fields": []
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse blueprint JSON: {e}")
            raise ValueError(f"Failed to parse blueprint JSON: {e}")
        except Exception as e:
            logger.error(f"Blueprint generation failed: {e}", exc_info=True)
            raise

class AssetRequest:
    """Represents an asset generation request"""
    def __init__(self, type: str, purpose: str, prompt: str):
        self.type = type  # "image", "gif", "audio", etc.
        self.purpose = purpose  # "diagram", "background", etc.
        self.prompt = prompt

class AssetPlanner:
    """Plans which assets need to be generated from blueprint"""
    
    def plan_assets(self, blueprint: Dict[str, Any]) -> list[AssetRequest]:
        """Extract asset requests from blueprint"""
        requests = []
        template_type = blueprint.get("templateType")
        
        if template_type == "LABEL_DIAGRAM":
            diagram = blueprint.get("diagram", {})
            if diagram.get("assetPrompt"):
                requests.append(AssetRequest(
                    type="image",
                    purpose="diagram",
                    prompt=diagram["assetPrompt"]
                ))
        
        elif template_type == "IMAGE_HOTSPOT_QA":
            image = blueprint.get("image", {})
            if image.get("assetPrompt"):
                requests.append(AssetRequest(
                    type="image",
                    purpose="image",
                    prompt=image["assetPrompt"]
                ))
        
        elif template_type == "PARAMETER_PLAYGROUND":
            viz = blueprint.get("visualization", {})
            if viz.get("assetPrompt"):
                requests.append(AssetRequest(
                    type="image",
                    purpose="visualization",
                    prompt=viz["assetPrompt"]
                ))
        
        elif template_type == "SPOT_THE_MISTAKE":
            content = blueprint.get("content", {})
            if content.get("assetPrompt"):
                requests.append(AssetRequest(
                    type="image",
                    purpose="content",
                    prompt=content["assetPrompt"]
                ))
        
        elif template_type == "MICRO_SCENARIO_BRANCHING":
            scenarios = blueprint.get("scenarios", [])
            for i, scenario in enumerate(scenarios):
                if scenario.get("assetPrompt"):
                    requests.append(AssetRequest(
                        type="image",
                        purpose=f"scenario_{i}",
                        prompt=scenario["assetPrompt"]
                    ))
        
        elif template_type == "BEFORE_AFTER_TRANSFORMER":
            before = blueprint.get("beforeState", {})
            after = blueprint.get("afterState", {})
            if before.get("assetPrompt"):
                requests.append(AssetRequest(
                    type="image",
                    purpose="before",
                    prompt=before["assetPrompt"]
                ))
            if after.get("assetPrompt"):
                requests.append(AssetRequest(
                    type="image",
                    purpose="after",
                    prompt=after["assetPrompt"]
                ))
        
        logger.info(f"Planned {len(requests)} asset requests for {template_type}")
        return requests

class AssetGenerator:
    """Generates assets (images, etc.) from prompts"""
    
    def __init__(self):
        # Placeholder for image generation API integration
        # Future: integrate with DALL-E, Stable Diffusion, etc.
        pass
    
    def generate_assets(self, requests: list[AssetRequest]) -> Dict[str, str]:
        """Generate assets and return URL map"""
        urls = {}
        
        for req in requests:
            if req.type == "image":
                # TODO: Integrate with image generation API
                # For now, return placeholder URL
                logger.info(f"Generating image asset: {req.purpose} - {req.prompt[:50]}...")
                # Placeholder URL - replace with actual API call
                urls[req.purpose] = f"https://placeholder.com/800x600?text={req.purpose.replace('_', '+')}"
            # Add other asset types as needed
        
        logger.info(f"Generated {len(urls)} asset URLs")
        return urls
    
    def inject_asset_urls(self, blueprint: Dict[str, Any], asset_urls: Dict[str, str]) -> Dict[str, Any]:
        """Inject asset URLs into blueprint"""
        template_type = blueprint.get("templateType")
        
        if template_type == "LABEL_DIAGRAM":
            if "diagram" in blueprint and "diagram" in asset_urls:
                blueprint["diagram"]["assetUrl"] = asset_urls["diagram"]
        
        elif template_type == "IMAGE_HOTSPOT_QA":
            if "image" in blueprint and "image" in asset_urls:
                blueprint["image"]["assetUrl"] = asset_urls["image"]
        
        elif template_type == "PARAMETER_PLAYGROUND":
            if "visualization" in blueprint and "visualization" in asset_urls:
                blueprint["visualization"]["assetUrl"] = asset_urls["visualization"]
        
        elif template_type == "SPOT_THE_MISTAKE":
            if "content" in blueprint and "content" in asset_urls:
                blueprint["content"]["assetUrl"] = asset_urls["content"]
        
        elif template_type == "MICRO_SCENARIO_BRANCHING":
            scenarios = blueprint.get("scenarios", [])
            for i, scenario in enumerate(scenarios):
                key = f"scenario_{i}"
                if key in asset_urls:
                    scenario["imageUrl"] = asset_urls[key]
        
        elif template_type == "BEFORE_AFTER_TRANSFORMER":
            if "beforeState" in blueprint and "before" in asset_urls:
                blueprint["beforeState"]["assetUrl"] = asset_urls["before"]
            if "afterState" in blueprint and "after" in asset_urls:
                blueprint["afterState"]["assetUrl"] = asset_urls["after"]
        
        return blueprint

class GenerationOrchestrator:
    """Orchestrate content generation"""
    
    def __init__(self):
        self.story_generator = StoryGenerator()
        self.html_generator = HTMLGenerator()
        self.blueprint_generator = BlueprintGenerator()
        self.asset_planner = AssetPlanner()
        self.asset_generator = AssetGenerator()
        self.image_generator = ImageGenerator()
        self.animation_generator = AnimationGenerator()
    
    def generate_content(
        self,
        question_data: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate all content for visualization"""
        logger.info("Starting content generation")
        
        try:
            # Step 1: Generate story
            prompt_template = strategy.get("prompt_template", "")
            story_result = self.story_generator.generate(
                question_data,
                prompt_template,
                strategy
            )
            story_data = story_result["data"]
            
            # Step 2: Generate HTML
            html_result = self.html_generator.generate(story_data)
            html_content = html_result["data"]["html"]
            
            logger.info("Content generation complete")
            
            return {
                "success": True,
                "story": story_data,
                "html": html_content,
                "story_validation": story_result.get("validation"),
                "html_validation": html_result.get("validation")
            }
        except Exception as e:
            logger.error(f"Content generation failed: {e}", exc_info=True)
            raise

