# Backend Logging Guide

## Overview

The backend uses a comprehensive logging system that writes detailed logs to files for debugging purposes.

## Log File Location

Logs are stored in the `backend/logs/` directory with the following naming pattern:
- `app_YYYYMMDD.log` - Daily log files (e.g., `app_20250108.log`)

## Log Levels

- **DEBUG**: Detailed information for debugging (function names, line numbers, data previews)
- **INFO**: General informational messages (API calls, pipeline steps, successful operations)
- **WARNING**: Warning messages (fallbacks, non-critical issues)
- **ERROR**: Error messages with full stack traces

## What Gets Logged

### API Endpoints
- All API requests and responses
- Request parameters and IDs
- Error details with stack traces

### Pipeline Processing
- Each step of the pipeline (Analysis → Story → HTML → Storage)
- Progress updates
- LLM API calls (OpenAI/Anthropic)
- Full request/response data
- Error details at each step

### LLM Service
- API calls to OpenAI/Anthropic
- Request details (model, temperature, message count)
- Response previews (first 500 chars)
- Token usage information
- Fallback attempts (OpenAI → Anthropic or vice versa)
- JSON parsing attempts and failures

### Document Parsing
- File uploads (filename, size, type)
- Parsing progress (pages, paragraphs)
- Extracted question and options
- Parsing errors

### Question Analysis
- Question text and options
- Analysis results (type, subject, difficulty)
- Full analysis JSON

### Story Generation
- Story generation requests
- Story data (title, context, question flow)
- Full story JSON

### HTML Generation
- HTML generation requests
- Generated HTML length and preview
- HTML extraction from code blocks

## Log Format

Each log entry includes:
```
YYYY-MM-DD HH:MM:SS | LEVEL     | logger_name | function:line | message
```

Example:
```
2025-01-08 14:23:45 | INFO      | llm_service | analyze_question:159 | Attempting question analysis with OpenAI...
2025-01-08 14:23:46 | DEBUG     | llm_service | _call_openai:52 | OpenAI Request - Messages count: 2
2025-01-08 14:23:47 | INFO      | llm_service | _call_openai:64 | OpenAI API call successful - Response length: 234 chars
```

## Viewing Logs

### Real-time Monitoring
```bash
# Watch logs in real-time (Linux/Mac)
tail -f backend/logs/app_$(date +%Y%m%d).log

# Windows PowerShell
Get-Content backend\logs\app_*.log -Wait -Tail 50
```

### Search Logs
```bash
# Find all errors
grep "ERROR" backend/logs/app_*.log

# Find specific process ID
grep "process_id=abc123" backend/logs/app_*.log

# Find all OpenAI calls
grep "OpenAI" backend/logs/app_*.log
```

### Filter by Component
```bash
# LLM service logs
grep "llm_service" backend/logs/app_*.log

# Pipeline logs
grep "PIPELINE" backend/logs/app_*.log

# API endpoint logs
grep "\[API\]" backend/logs/app_*.log
```

## Debugging Workflow

1. **Start the backend server** - Logs begin immediately
2. **Reproduce the issue** - All actions are logged
3. **Check the log file** - Look for ERROR or WARNING entries
4. **Follow the process ID** - Each pipeline run has a unique process_id
5. **Check LLM responses** - Full API responses are logged at DEBUG level

## Example Log Search Patterns

### Find a specific error:
```bash
grep -A 10 "PIPELINE ERROR" backend/logs/app_*.log
```

### Track a specific question processing:
```bash
grep "question_id=your-question-id" backend/logs/app_*.log
```

### See all API calls:
```bash
grep "Calling.*API" backend/logs/app_*.log
```

### Find fallback attempts:
```bash
grep "Falling back" backend/logs/app_*.log
```

## Log File Rotation

Logs are created daily. Old log files are kept for historical debugging. You can manually clean them:

```bash
# Keep only last 7 days
find backend/logs -name "app_*.log" -mtime +7 -delete
```

## Log File Size

Log files can grow large with DEBUG level logging. To reduce size:
- Set log level to INFO in production
- Rotate logs daily
- Archive old logs

## Troubleshooting

### No logs appearing?
- Check that `backend/logs/` directory exists
- Verify file permissions
- Check that logger is initialized in main.py

### Too much logging?
- Adjust log levels in `backend/app/utils/logger.py`
- Change `logger.setLevel(logging.DEBUG)` to `logging.INFO`

### Need more detail?
- Ensure DEBUG level is enabled
- Check that `exc_info=True` is used in error logs

