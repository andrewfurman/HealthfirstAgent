# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask web application that implements a voice-enabled AI assistant for Healthfirst insurance call center operations. The application uses OpenAI's Realtime API with GPT-4o for voice conversations and PostgreSQL for data storage.

## Development Commands

### Install Dependencies
```bash
poetry install
```

### Run Development Server
```bash
poetry run python main.py
```

### Database Management
```bash
# Create database tables
poetry run python -c "from main import app, db; with app.app_context(): db.create_all()"

# Drop all tables (use with caution)
poetry run python -c "from main import app, db; with app.app_context(): db.drop_all()"
```

### Type Checking
```bash
poetry run pyright
```

### Linting
```bash
poetry run ruff check .
poetry run ruff format .
```

## Architecture Overview

The application follows a modular Flask blueprint architecture:

1. **Main Application (`main.py`)**: 
   - Handles Flask app initialization and configuration
   - Manages OpenAI Realtime API sessions for voice chat
   - Configures database connection with PostgreSQL
   - Implements health check endpoints

2. **Plans Module (`plans/`)**: 
   - Separate blueprint for insurance plan management
   - SQLAlchemy model in `plans_model.py` defines Plan schema
   - Routes in `plans_routes.py` handle CRUD operations
   - Has its own templates and static files for UI

3. **Voice Chat System**:
   - Browser-based WebRTC implementation in `static/script.js`
   - Creates ephemeral OpenAI Realtime sessions via `/session` endpoint
   - Handles real-time audio streaming between browser and OpenAI
   - AI agent behavior defined in `call_center_guide.md`

4. **Database Layer**:
   - Uses SQLAlchemy ORM with PostgreSQL
   - Connection pooling configured for production use
   - Context managers ensure proper session cleanup

## Key Technical Details

- **OpenAI Integration**: Uses Realtime API with ephemeral tokens for secure voice sessions
- **Environment Variables Required**:
  - `OPENAI_API_KEY`: For OpenAI API access
  - `DATABASE_URL`: PostgreSQL connection string (defaults to Replit DB if available)
- **WebRTC Configuration**: Browser microphone access required for voice chat
- **AI Instructions**: The AI assistant's behavior is defined by the comprehensive guide in `call_center_guide.md`

## Important Considerations

- The `voice_chat_sessions/voice_chat_session.py` file is currently empty - any voice session logic should be implemented in `main.py` or this module
- No test suite exists - when adding features, consider creating tests in a `tests/` directory
- Database migrations are not set up - schema changes require manual handling
- The application is configured for Replit deployment but can run locally with proper environment setup