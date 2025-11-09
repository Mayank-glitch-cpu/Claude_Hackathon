# LLM Calls Analysis - Last Run

## Total LLM Calls: **10**

---

## Call Sequence and Details

### **Call 1: Question Type Classification** (Layer 2 - Classification)
**Step**: Question Analysis - Step 1  
**Class**: `QuestionTypeClassifier.classify()`  
**Type**: Generic (works for all question types)

**Input Parameters**:
```python
question_text = "How much water must be added to 10 liters of 30% salt solution to make it 20%?"
options = None
```

**System Prompt**:
```
"You are a question classification expert. Always respond with valid JSON only."
```

**User Prompt**:
```
Analyze the following question and determine its type. 
Question types: coding, math, science, reasoning, application, word_problem, code_completion, fact_recall

Question: How much water must be added to 10 liters of 30% salt solution to make it 20%?
Options: None

Respond with ONLY a JSON object: {"question_type": "type_here"}
```

**Output**:
```json
{
  "question_type": "word_problem"
}
```

---

### **Call 2: Subject Identification** (Layer 2 - Classification)
**Step**: Question Analysis - Step 2  
**Class**: `SubjectIdentifier.identify()`  
**Type**: Generic

**Input Parameters**:
```python
question_text = "How much water must be added to 10 liters of 30% salt solution to make it 20%?"
question_type = "word_problem"  # from Call 1
```

**System Prompt**:
```
"You are an educational content expert. Always respond with valid JSON only."
```

**User Prompt**:
```
Analyze the following question and identify the subject area and specific topic.

Question: How much water must be added to 10 liters of 30% salt solution to make it 20%?
Question Type: word_problem

Respond with ONLY a JSON object: {"subject": "subject_here", "topic": "specific_topic_here"}
```

**Output**:
```json
{
  "subject": "mathematics",
  "topic": "mixture problems"
}
```

---

### **Call 3: Complexity Analysis** (Layer 2 - Classification)
**Step**: Question Analysis - Step 3  
**Class**: `ComplexityAnalyzer.analyze()`  
**Type**: Generic

**Input Parameters**:
```python
question_text = "How much water must be added to 10 liters of 30% salt solution to make it 20%?"
question_type = "word_problem"  # from Call 1
subject = "mathematics"  # from Call 2
```

**System Prompt**:
```
"You are an educational assessment expert. Always respond with valid JSON only."
```

**User Prompt**:
```
Analyze the complexity of the following question and determine its difficulty level.
Difficulty levels: beginner, intermediate, advanced

Question: How much water must be added to 10 liters of 30% salt solution to make it 20%?
Question Type: word_problem
Subject: mathematics

Respond with ONLY a JSON object: {"difficulty": "beginner|intermediate|advanced", "complexity_score": 1-10}
```

**Output**:
```json
{
  "difficulty": "intermediate",
  "complexity_score": 5
}
```

---

### **Call 4: Keyword/Concept Extraction** (Layer 2 - Classification)
**Step**: Question Analysis - Step 4  
**Class**: `KeywordExtractor.extract()`  
**Type**: Generic

**Input Parameters**:
```python
question_text = "How much water must be added to 10 liters of 30% salt solution to make it 20%?"
subject = "mathematics"  # from Call 2
```

**System Prompt**:
```
"You are a content analysis expert. Always respond with valid JSON only."
```

**User Prompt**:
```
Extract the key concepts, keywords, and learning points from the following question.

Question: How much water must be added to 10 liters of 30% salt solution to make it 20%?
Subject: mathematics

Respond with ONLY a JSON object: {"key_concepts": ["concept1", "concept2", ...], "keywords": ["keyword1", "keyword2", ...], "intent": "what this question tests"}
```

**Output**:
```json
{
  "key_concepts": ["percentage concentration", "dilution", "algebraic equations"],
  "keywords": [...],
  "intent": "This question tests the understanding of dilution and concentration changes in solutions using percentage and algebraic equations."
}
```

---

### **Call 5: Template Routing** (Layer 2 - Template Router)
**Step**: Template Routing  
**Class**: `TemplateRouter.route_template()`  
**Type**: Template-Specific (selects from 18 templates)

**Input Parameters**:
```python
question_text = "How much water must be added to 10 liters of 30% salt solution to make it 20%?"
analysis = {
  "question_type": "word_problem",
  "subject": "mathematics",
  "difficulty": "intermediate",
  "key_concepts": ["percentage concentration", "dilution", "algebraic equations"],
  "intent": "This question tests the understanding of dilution and concentration changes..."
}
```

**System Prompt**: (Loaded from `backend/prompts/template_router_system.txt`)
- Contains descriptions of all 18 templates
- Instructions for selecting the best template

**User Prompt**:
```
Question: How much water must be added to 10 liters of 30% salt solution to make it 20%?

Analysis:
- question_type: word_problem
- subject: mathematics
- difficulty: intermediate
- key_concepts: ['percentage concentration', 'dilution', 'algebraic equations']
- intent: This question tests the understanding of dilution and concentration changes in solutions using percentage and algebraic equations.

Choose the best templateType.
```

**Output**:
```json
{
  "templateType": "PARAMETER_PLAYGROUND",
  "confidence": 0.9,
  "rationale": "The question involves understanding how changing the amount of water affects the concentration of a solution, which can be effectively explored through a parametric simulation..."
}
```

---

### **Call 6: Game Format Selection** (Layer 3 - Strategy)
**Step**: Strategy Creation - Step 1  
**Class**: `GameFormatSelector.select_format()`  
**Type**: Generic (selects from 7 game formats)

**Input Parameters**:
```python
question_type = "word_problem"
subject = "mathematics"
difficulty = "intermediate"
key_concepts = ["percentage concentration", "dilution", "algebraic equations"]
```

**System Prompt**:
```
"You are a gamification expert. Always respond with valid JSON only."
```

**User Prompt**:
```
Based on the question characteristics, select the optimal game format.
Available formats: drag_drop, matching, timeline, simulation, puzzle, quiz, interactive_diagram

Question Type: word_problem
Subject: mathematics
Difficulty: intermediate
Key Concepts: percentage concentration, dilution, algebraic equations

Respond with ONLY a JSON object: {"game_format": "format_here", "rationale": "why this format"}
```

**Output**:
```json
{
  "game_format": "simulation",
  "rationale": "A simulation format allows learners to experiment with different scenarios involving percentage concentration and dilution..."
}
```

---

### **Call 7: Storyline Generation** (Layer 3 - Strategy)
**Step**: Strategy Creation - Step 2  
**Class**: `StorylineGenerator.generate_storyline()`  
**Type**: Generic (but influenced by game_format)

**Input Parameters**:
```python
question_text = "How much water must be added to 10 liters of 30% salt solution to make it 20%?"
question_type = "word_problem"
subject = "mathematics"
game_format = "simulation"  # from Call 6
```

**System Prompt**:
```
"You are a creative educational storyteller. Always respond with valid JSON only."
```

**User Prompt**:
```
Create an engaging, educational storyline that makes this question come alive.

Question: How much water must be added to 10 liters of 30% salt solution to make it 20%?
Question Type: word_problem
Subject: mathematics
Game Format: simulation

Respond with ONLY a JSON object: {
    "story_title": "title",
    "story_context": "engaging narrative",
    "characters": ["character1", "character2"],
    "setting": "where the story takes place"
}
```

**Output**:
```json
{
  "story_title": "The Alchemist's Salt Solution Challenge",
  "story_context": "In the mystical village of Aquamira, where alchemy and mathematics intertwine...",
  "characters": ["Luna", "Orion", "Master Alaric"],
  "setting": "The enchanting village of Aquamira, within Master Alaric's potion laboratory"
}
```

---

### **Call 8: Interaction Design** (Layer 3 - Strategy)
**Step**: Strategy Creation - Step 3  
**Class**: `InteractionDesigner.design_interactions()`  
**Type**: Generic (but influenced by game_format)

**Input Parameters**:
```python
game_format = "simulation"  # from Call 6
question_type = "word_problem"
difficulty = "intermediate"
```

**System Prompt**:
```
"You are a UX designer. Always respond with valid JSON only."
```

**User Prompt**:
```
Design the interaction patterns for this game.

Game Format: simulation
Question Type: word_problem
Difficulty: intermediate

Respond with ONLY a JSON object: {
    "interaction_type": "click|drag|swipe|type",
    "feedback_style": "immediate|delayed|progressive",
    "hints_enabled": true/false,
    "animation_style": "smooth|bouncy|minimal"
}
```

**Output**:
```json
{
  "interaction_type": "click",
  "feedback_style": "progressive",
  "hints_enabled": true,
  "animation_style": "smooth"
}
```

---

### **Call 9: Story Generation** (Layer 4 - Generation)
**Step**: Story Generation  
**Class**: `StoryGenerator.generate()`  
**Type**: Template-Specific (uses PARAMETER_PLAYGROUND template supplement)

**Input Parameters**:
```python
question_data = {
  "text": "How much water must be added to 10 liters of 30% salt solution to make it 20%?",
  "options": None,
  "question_type": "word_problem",
  "subject": "mathematics",
  "difficulty": "intermediate",
  "key_concepts": ["percentage concentration", "dilution", "algebraic equations"],
  "intent": "This question tests the understanding of dilution..."
}
prompt_template = <long prompt template from PromptSelector>
strategy = {
  "game_format": "simulation",
  "storyline": {...},  # from Call 7
  "interactions": {...}  # from Call 8
}
template_type = "PARAMETER_PLAYGROUND"  # from Call 5
```

**System Prompt**: 
- Base: `backend/prompts/story_base.md` (generic story generation instructions)
- **Template-Specific Supplement**: `backend/prompts/story_templates/PARAMETER_PLAYGROUND.txt` (template-specific guidance)
- Combined: Base + Template Supplement

**User Prompt**:
```
Generate a story-based visualization for the following question:

Question: How much water must be added to 10 liters of 30% salt solution to make it 20%?
Options: None
Type: word_problem
Subject: mathematics
Difficulty: intermediate
Key Concepts: ['percentage concentration', 'dilution', 'algebraic equations']
Intent: This question tests the understanding of dilution and concentration changes in solutions using percentage and algebraic equations.

Game Format: simulation
Storyline: {
  "story_title": "The Alchemist's Salt Solution Challenge",
  "story_context": "...",
  "characters": ["Luna", "Orion", "Master Alaric"],
  "setting": "..."
}
TemplateType: PARAMETER_PLAYGROUND

Follow the schema and requirements in the system prompt. Respond with ONLY valid JSON matching the output schema.
```

**Output**: (Full story JSON with all fields)
```json
{
  "story_title": "The Alchemist's Salt Solution Challenge",
  "story_context": "...",
  "learning_intuition": "...",
  "visual_metaphor": "...",
  "interaction_design": "...",
  "visual_elements": [...],
  "question_flow": [...],
  "primary_question": "...",
  "learning_alignment": "...",
  "animation_cues": "...",
  ...
}
```

---

### **Call 10: Blueprint Generation** (Layer 4 - Generation)
**Step**: Blueprint Generation  
**Class**: `BlueprintGenerator.generate()`  
**Type**: Template-Specific (uses PARAMETER_PLAYGROUND TypeScript interface)

**Input Parameters**:
```python
story_data = {...}  # Full story from Call 9
template_type = "PARAMETER_PLAYGROUND"  # from Call 5
```

**System Prompt**:
- Base: `backend/prompts/blueprint_base.md` (generic blueprint generation instructions)
- **Template-Specific**: `backend/prompts/blueprint_templates/PARAMETER_PLAYGROUND.ts.txt` (TypeScript interface for PARAMETER_PLAYGROUND)
- Combined: Base + TypeScript Interface

**User Prompt**:
```
TemplateType: PARAMETER_PLAYGROUND

Template Metadata:
{
  "name": "PARAMETER_PLAYGROUND",
  "description": "...",
  ...
}

TypeScript interface for this template:

[Full TypeScript interface from PARAMETER_PLAYGROUND.ts.txt]

Story Data:
[Full story JSON from Call 9]

Generate a blueprint object that conforms EXACTLY to the TypeScript interface.
Do not include any fields that are not defined in the interface.
Do not wrap the response in any additional text.
```

**Output**: (PARAMETER_PLAYGROUND blueprint JSON)
```json
{
  "templateType": "PARAMETER_PLAYGROUND",
  "title": "The Alchemist's Salt Solution Challenge",
  "narrativeIntro": "...",
  "parameters": [{
    "id": "water_volume",
    "label": "Water Volume",
    "type": "slider",
    "min": 0,
    "max": 10,
    "defaultValue": 0,
    "unit": "liters"
  }],
  "visualization": {...},
  "tasks": [...],
  "animationCues": {...}
}
```

---

## Summary

### Template-Specific Calls (2):
1. **Call 5**: Template Routing - Uses template router system prompt with all 18 templates
2. **Call 9**: Story Generation - Uses PARAMETER_PLAYGROUND template supplement
3. **Call 10**: Blueprint Generation - Uses PARAMETER_PLAYGROUND TypeScript interface

### Generic Calls (7):
1. **Call 1**: Question Type Classification
2. **Call 2**: Subject Identification
3. **Call 3**: Complexity Analysis
4. **Call 4**: Keyword/Concept Extraction
5. **Call 6**: Game Format Selection
6. **Call 7**: Storyline Generation
7. **Call 8**: Interaction Design

### No LLM Calls:
- **Asset Planning**: Extracts asset requests from blueprint (no LLM)
- **Asset Generation**: Creates placeholder URLs (no LLM, future: image generation API)

---

## Template-Specific vs Generic Breakdown

**Template-Specific Steps**:
- Template Routing (Call 5) - Selects from 18 templates
- Story Generation (Call 9) - Uses template-specific supplement file
- Blueprint Generation (Call 10) - Uses template-specific TypeScript interface

**Generic Steps**:
- All classification steps (Calls 1-4) - Work for any question type
- Strategy creation (Calls 6-8) - Work for any game format, though influenced by format
- Asset planning/generation - Template-aware but no LLM calls

