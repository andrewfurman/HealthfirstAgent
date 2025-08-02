# OpenAI Realtime API Integration

## Overview
This project integrates OpenAI's Realtime Voice API with function calling to provide interactive voice assistance for Healthfirst insurance plans.

## Key Components

### 1. Voice Session Initialization (`main.py`)
- Creates ephemeral tokens for secure browser-based voice chat
- Configures voice model: `gpt-4o-realtime-preview`
- Sets up function definitions for plan queries
- Preloads plan summaries (<2000 words) for reduced latency

### 2. Function Definitions (`realtime_functions.py`)
Three main functions available to the voice assistant:

#### `get_plan_coverage_summary(plan_name)`
Returns comprehensive coverage details for a specific health plan.

#### `get_plan_table_of_contents(plan_name)` 
Returns TOC with page numbers to help users find specific information.

#### `search_plan_document(plan_name, search_term)`
Searches within plan documents for specific terms like "prior authorization" or "copay".

### 3. WebRTC Implementation (`static/script.js`)
- Handles browser microphone access
- Manages WebRTC peer connection
- Processes voice transcripts
- Displays conversation history

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview
```

### Session Configuration
```python
{
    "model": "gpt-4o-realtime-preview",
    "voice": "alloy",
    "turn_detection": {
        "type": "semantic_vad",
        "eagerness": "high"
    },
    "tools": [...],  # Function definitions
    "tool_choice": "auto"
}
```

## Testing Function Calls
Test endpoint available at `/execute-function`:
```bash
curl -X POST http://127.0.0.1:8080/execute-function \
  -H "Content-Type: application/json" \
  -d '{"name": "get_plan_coverage_summary", "arguments": {"plan_name": "Gold"}}'
```

## Voice Interaction Flow
1. User clicks "Start Voice Chat"
2. Browser requests microphone permission
3. Ephemeral token generated server-side
4. WebRTC connection established with OpenAI
5. Voice assistant loads plan summaries
6. User asks questions
7. Assistant uses functions to query specific plan details
8. Responses synthesized to speech

## Best Practices
- Keep initial context under 2000 words
- Use function calling for detailed queries
- Cache common responses
- Monitor API usage and costs
