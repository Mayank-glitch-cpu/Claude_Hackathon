# AI-Powered Gamified Learning Platform

Transform educational questions into interactive, story-based visualizations using AI. This platform follows the Brilliant.org design aesthetic and implements a complete template-based blueprint system with 18 game templates.

## Features

- **Brilliant.org-Inspired UI**: Modern, clean design with smooth animations
- **Document Upload**: Support for PDF, DOCX, TXT, and Markdown files
- **Template-Based Game System**: 18 fixed game templates automatically selected based on question analysis
- **AI-Powered Processing**: 
  - Question analysis and classification
  - Template routing (selects best game template)
  - Template-aware story generation
  - Blueprint generation (structured JSON, not HTML)
  - Asset planning and generation
- **Real-time Progress Tracking**: Monitor processing through each pipeline step
- **Interactive Games**: Template-specific React components with rich interactions
- **Score Calculation**: Track performance and provide feedback

## Architecture

This application follows a **4-layer pipeline** with template routing:

### Layer 1: Input Processing
- Document parsing (PDF, DOCX, TXT)
- Question extraction

### Layer 2: Analysis & Routing
- Question analysis (type, subject, difficulty, key concepts, intent)
- **Template routing** - LLM selects best template from 18 options

### Layer 3: Strategy
- Gamification strategy creation
- Storyline generation

### Layer 4: Generation
- **Story generation** - Template-aware story with supplements
- **Blueprint generation** - Creates template-specific JSON blueprint
- **Asset planning** - Identifies required images/assets
- **Asset generation** - Generates asset URLs (currently placeholder)

### Frontend Rendering
- **GameEngine** - Routes to appropriate template component
- **18 Template Components** - Each implements specific game interactions
- TypeScript type safety with blueprint interfaces

## 18 Game Templates

1. **LABEL_DIAGRAM** - Diagram labeling with draggable labels
2. **IMAGE_HOTSPOT_QA** - Interactive image with clickable hotspots
3. **SEQUENCE_BUILDER** - Order steps in correct sequence
4. **TIMELINE_ORDER** - Arrange events chronologically
5. **BUCKET_SORT** - Categorize items into buckets
6. **MATCH_PAIRS** - Match related pairs
7. **MATRIX_MATCH** - Match items across dimensions
8. **PARAMETER_PLAYGROUND** - Interactive parameter manipulation
9. **GRAPH_SKETCHER** - Draw and manipulate graphs
10. **VECTOR_SANDBOX** - Vector operations visualization
11. **STATE_TRACER_CODE** - Step through code execution
12. **SPOT_THE_MISTAKE** - Identify errors in code/content
13. **CONCEPT_MAP_BUILDER** - Build concept relationships
14. **MICRO_SCENARIO_BRANCHING** - Interactive branching scenarios
15. **DESIGN_CONSTRAINT_BUILDER** - Design with constraints
16. **PROBABILITY_LAB** - Probability experiments
17. **BEFORE_AFTER_TRANSFORMER** - Visualize transformations
18. **GEOMETRY_BUILDER** - Geometric construction

## Tech Stack

### Frontend
- Next.js 14+ (App Router) with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- Lucide React for icons
- Zustand for state management

### Backend
- FastAPI (Python)
- SQLAlchemy ORM (SQLite/PostgreSQL)
- OpenAI/Anthropic for LLM calls
- PyPDF2 and python-docx for document parsing

## Quick Start

See [SETUP.md](./SETUP.md) for detailed setup instructions.

### Quick Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env file with your API keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

## Project Structure

```
Claude_Hackathon/
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router pages
│   │   ├── components/    # React components
│   │   │   ├── GameEngine.tsx      # Template router
│   │   │   └── templates/          # 18 game components
│   │   ├── types/         # TypeScript definitions
│   │   │   └── gameBlueprint.ts    # Blueprint types
│   │   └── stores/        # Zustand state management
│   └── package.json
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── db/            # Database models & setup
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   │   ├── template_registry.py    # Template metadata
│   │   │   └── pipeline/  # Pipeline services
│   │   ├── templates/     # 18 template metadata JSON
│   │   └── repositories/  # Data access layer
│   ├── prompts/          # LLM prompt templates
│   │   ├── story_base.md
│   │   ├── story_templates/    # 18 template supplements
│   │   ├── blueprint_base.md
│   │   ├── blueprint_templates/ # 18 TypeScript interfaces
│   │   └── template_router_system.txt
│   ├── scripts/          # Utility scripts
│   │   └── migrate_add_blueprint_id.py
│   └── requirements.txt
└── README.md
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000

# Optional: For PostgreSQL in production
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

## User Flow

1. **Landing Page** → View the Brilliant.org-inspired homepage
2. **Get Started** → Navigate to upload page
3. **Upload** → Upload PDF/DOCX/TXT with questions
4. **Preview** → Review extracted question and analysis
5. **Start Game** → Click "Start Interactive Game" button
6. **Progress** → Watch real-time progress through pipeline:
   - Document parsing
   - Question extraction
   - Question analysis
   - Template routing (selects game template)
   - Strategy creation
   - Story generation (template-aware)
   - Blueprint generation
   - Asset planning
   - Asset generation
7. **Go to Game** → Click button when processing completes
8. **Play** → Interact with template-specific game component
9. **Score** → View results and performance

## API Documentation

### Core Endpoints
- `POST /api/upload` - Upload document
- `GET /api/questions/{id}` - Get question details
- `POST /api/process/{id}` - Start processing pipeline
- `GET /api/progress/{id}` - Get progress status
- `GET /api/visualization/{id}` - Get visualization (returns blueprint or HTML)
- `POST /api/check-answer/{id}` - Check answer correctness

### Pipeline Endpoints
- `GET /api/pipeline/steps/{id}` - Get all steps for a process
- `POST /api/pipeline/retry/{step_id}` - Retry a failed step
- `GET /api/pipeline/history/{question_id}` - Get processing history

### Visualization Endpoints
- `GET /api/visualizations/{id}` - Get visualization with blueprint support

## Database Schema

- **questions**: Uploaded questions
- **question_analyses**: Analysis results
- **stories**: Generated story data
- **game_blueprints**: Template-specific game blueprints (NEW)
- **visualizations**: Links to blueprints or HTML content
- **processes**: Pipeline execution tracking
- **pipeline_steps**: Individual step tracking

## Key Features

### Template System
- 18 fixed game templates with metadata
- Automatic template selection via LLM
- Template-specific story generation
- TypeScript type safety for blueprints

### Blueprint System
- Structured JSON instead of HTML
- Template-specific schemas
- Asset planning and generation
- Validation against TypeScript interfaces

### Frontend Components
- GameEngine routes to correct template
- Each template has dedicated React component
- Rich interactions per template type
- Type-safe blueprint handling

## Migration Guide

If upgrading from an older version:

1. **Run database migration**:
   ```bash
   cd backend
   source venv/bin/activate
   PYTHONPATH=$(pwd) python scripts/migrate_add_blueprint_id.py
   ```

2. **Verify template files exist**:
   - 18 JSON files in `backend/app/templates/`
   - 18 story supplements in `backend/prompts/story_templates/`
   - 18 TS interfaces in `backend/prompts/blueprint_templates/`

3. **Check frontend components**:
   - GameEngine.tsx exists
   - 18 template components in `frontend/src/components/templates/`

## License

MIT
