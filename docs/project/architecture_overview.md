# Healthfirst Agent Architecture Overview

## Project Structure

```
HealthfirstAgent/
├── main.py                    # Flask application & OpenAI integration
├── realtime_functions.py      # Voice assistant functions
├── plans/                     # Insurance plans module
│   ├── plans_model.py        # SQLAlchemy models
│   ├── plans_routes.py       # API endpoints
│   ├── document_extractor.py # PDF extraction
│   ├── gpt_summary_generator.py # GPT-4.1 summaries
│   ├── toc_generator.py      # Table of contents generation
│   └── templates/            # HTML templates
├── static/                    # Frontend assets
│   ├── script.js             # WebRTC voice chat
│   └── print_transcript.js   # Conversation display
├── templates/                 # Main app templates
├── plan_pdfs/                # Downloaded PDF documents
└── docs/                     # Documentation
    ├── openai/              # OpenAI integration docs
    ├── project/             # Project documentation
    └── scripts/             # Utility scripts
```

## Database Schema

### Plans Table
- `id`: Primary key
- `old_id`: Legacy identifier
- `short_name`: Brief plan name (e.g., "LIP", "Gold")
- `full_name`: Complete plan name
- `plan_type`: Category (Medicare, Medicaid, Marketplace)
- `summary_of_benefits_url`: PDF document URL
- `plan_document_full_text`: Extracted PDF text
- `compressed_summary`: GPT-4.1 generated summary
- `table_of_contents`: GPT-4.1 generated TOC
- `document_type`: Source type (pdf/website)

## Key Features

### 1. PDF Document Processing
- Automatic extraction from Healthfirst PDFs
- PyMuPDF library for robust extraction
- Handles corrupted/protected PDFs

### 2. AI-Powered Summaries
- GPT-4.1 generates comprehensive plan summaries
- Structured markdown format
- Key benefits and coverage details

### 3. Table of Contents Generation
- Automatic page number extraction
- Hierarchical structure preservation
- 66.7% success rate for page numbers

### 4. Voice Assistant Integration
- Real-time voice interaction
- Function calling for dynamic queries
- Preloaded context for fast responses

### 5. Web Interface
- Browse all 27 health plans
- View summaries and TOCs
- Edit plan details
- Generate/regenerate content

## API Endpoints

### Plans Management
- `GET /plans/` - List all plans
- `GET /plans/<id>` - View plan details
- `POST /plans/<id>/update` - Update plan
- `POST /plans/api/extract-document/<id>` - Extract PDF
- `POST /plans/api/generate-summary/<id>` - Generate summary
- `POST /plans/api/generate-toc/<id>` - Generate TOC

### Voice Chat
- `GET /session` - Create voice session
- `POST /execute-function` - Test function execution

## Technology Stack
- **Backend**: Python Flask, SQLAlchemy
- **Database**: PostgreSQL (Neon)
- **AI/ML**: OpenAI GPT-4.1, GPT-4o Realtime
- **PDF Processing**: PyMuPDF, pdfplumber
- **Frontend**: JavaScript, WebRTC
- **Deployment**: Replit-ready configuration
