# AI-Powered Gamified Learning Platform

Transform educational questions into interactive, story-based visualizations using AI. This platform follows the Brilliant.org design aesthetic and implements a complete 6-layer pipeline for question processing and gamification.

## Features

- **Brilliant.org-Inspired UI**: Modern, clean design with smooth animations
- **Document Upload**: Support for PDF, DOCX, TXT, and Markdown files
- **AI-Powered Processing**: 
  - Question analysis and classification
  - Story generation from questions
  - Interactive HTML visualization creation
- **Real-time Progress Tracking**: Monitor processing through each pipeline layer
- **Interactive Games**: Question-driven visualizations with scoring
- **Score Calculation**: Track performance and provide feedback

## Architecture

This application follows a 6-layer pipeline:
1. **Input Processing** - Extract questions from documents
2. **Intent Classification** - Analyze and classify questions using LLM
3. **Story Generation** - Generate engaging stories from questions
4. **HTML Generation** - Create interactive visualizations
5. **Delivery** - Display visualizations to learners
6. **Analytics** - Track scores and performance

## Tech Stack

### Frontend
- Next.js 14+ (App Router) with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- Lucide React for icons

### Backend
- FastAPI (Python)
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
uvicorn app.main:app --reload
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
│   │   └── components/    # React components
│   └── package.json
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   └── models/        # Data models
│   ├── prompts/          # LLM prompt templates
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
```

## User Flow

1. **Landing Page** → View the Brilliant.org-inspired homepage
2. **Get Started** → Navigate to upload page
3. **Upload** → Upload PDF/DOCX/TXT with questions
4. **Preview** → Review extracted question and story
5. **Process** → Watch real-time progress through pipeline
6. **Game** → Play interactive visualization
7. **Score** → View results and performance

## API Documentation

- `POST /api/upload` - Upload document
- `GET /api/questions/{id}` - Get question details
- `POST /api/process/{id}` - Start processing
- `GET /api/progress/{id}` - Get progress status
- `GET /api/visualization/{id}` - Get visualization HTML
- `POST /api/check-answer/{id}` - Check answer correctness

## License

MIT

