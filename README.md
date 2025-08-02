# Healthfirst Agent

AI-powered voice assistant for Healthfirst insurance call center operations, built with Flask and OpenAI's Realtime API.

## Features

- **Voice-Enabled AI Assistant**: Real-time voice conversations using OpenAI's GPT-4o Realtime API
- **Health Plan Management**: Comprehensive database of Healthfirst insurance plans with detailed coverage information
- **Intelligent Document Processing**: Automated extraction and summarization of plan documents
- **Call Center Optimization**: AI agent trained on Healthfirst-specific guidelines for efficient member support

## Project Structure

```
HealthfirstAgent/
├── main.py                    # Main Flask application
├── realtime_functions.py      # OpenAI Realtime API integration
├── call_center_guide.md       # AI assistant instructions
├── CLAUDE.md                  # Development guidelines
├── plans/                     # Plans module
│   ├── plans_model.py        # Database models
│   ├── plans_routes.py       # API endpoints
│   ├── templates/            # HTML templates
│   └── static/               # JavaScript/CSS
├── docs/                      # Documentation
│   ├── research/             # Plan research docs
│   ├── development/          # Development notes
│   └── configuration/        # Config documentation
└── scripts/                   # Utility scripts
    ├── migrations/           # Database migrations
    └── utilities/            # Data management tools
```

## Quick Start

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Set environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: PostgreSQL connection string

3. **Run the application**:
   ```bash
   poetry run python main.py
   ```

4. **Access the application**:
   - Voice Assistant: http://127.0.0.1:8080
   - Plans Management: http://127.0.0.1:8080/plans

## Key Technologies

- **Backend**: Python Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/Voice**: OpenAI Realtime API (GPT-4o)
- **Frontend**: Vanilla JavaScript with WebRTC
- **Styling**: Tailwind CSS

## Documentation

- See `CLAUDE.md` for development guidelines
- See `docs/` for additional documentation
- See `scripts/README.md` for utility script documentation

## License

Proprietary - Healthfirst