# Setup Guide

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key OR Anthropic API key

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file in backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

6. Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open http://localhost:3000 in your browser

## Usage Flow

1. **Landing Page**: Visit the homepage to see the Brilliant.org-inspired design
2. **Get Started**: Click "Get started" button to go to upload page
3. **Upload**: Upload a PDF, DOCX, or TXT file containing a question
4. **Preview**: Review the extracted question and story preview
5. **Process**: Click "Start Interactive Game" to begin processing
6. **Progress**: Watch the progress indicator as the system:
   - Analyzes the question
   - Generates a story
   - Creates the HTML visualization
7. **Game**: Play the interactive visualization and answer questions
8. **Score**: View your final score and results

## API Endpoints

- `POST /api/upload` - Upload a document
- `GET /api/questions/{question_id}` - Get question details
- `POST /api/process/{question_id}` - Start processing pipeline
- `GET /api/progress/{process_id}` - Get processing progress
- `GET /api/visualization/{visualization_id}` - Get generated visualization
- `POST /api/check-answer/{visualization_id}` - Check answer correctness

## Troubleshooting

### Backend Issues
- Ensure virtual environment is activated
- Check that API keys are set in `.env` file
- Verify port 8000 is not in use

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that backend is running on port 8000
- Verify Next.js version: `npx next --version`

### LLM API Issues
- Verify API keys are correct
- Check API rate limits
- Ensure sufficient API credits

