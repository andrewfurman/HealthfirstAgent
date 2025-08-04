# OpenAI Model Requirements

## Standard Models for Text Processing

**REQUIREMENT**: All text-based queries to OpenAI must use **GPT-4.1**.

### Files Using GPT Models

The following files contain OpenAI API calls and should use GPT-4.1 for text processing:

1. **`plans/toc_generator.py`** - Table of contents generation
   - Model: `gpt-4.1`
   - Purpose: Analyzing plan documents and creating enhanced TOCs with copay/deductible/PA annotations

2. **`plans/gpt_summary_generator.py`** - Plan summary generation  
   - Model: `gpt-4.1`
   - Purpose: Creating comprehensive summaries of plan documents for call center agents

3. **`plans/description_generator.py`** - Plan descriptions
   - Model: `gpt-4.1` 
   - Purpose: Generating clear one-sentence descriptions of health plans

### Voice/Realtime API

For voice interactions, continue using the OpenAI Realtime API model:
- **`main.py`** - Voice chat sessions
  - Model: `gpt-4o-realtime-preview`
  - Purpose: Real-time voice conversations with tool calling

### Why GPT-4.1?

- **Consistency**: Ensures consistent behavior across all text-based operations
- **Performance**: Optimized for document analysis and text generation tasks
- **Reliability**: Proven performance for insurance document processing
- **Cost Efficiency**: Better cost-performance ratio for batch text processing

### Implementation Notes

When adding new OpenAI API calls for text processing:

```python
response = client.chat.completions.create(
    model="gpt-4.1",  # Always use GPT-4.1 for text-based queries
    messages=[...],
    temperature=0.1,  # Low temperature for consistency
    max_tokens=3000   # Adjust based on needs
)
```

### Model Update History

- **2025-08-04**: Standardized on GPT-4.1 for all text-based queries
- **2025-08-04**: Enhanced table of contents generation with call center annotations
- **2025-08-04**: Updated description generator from GPT-4o-mini to GPT-4.1

### Verification

To verify all files are using the correct models:

```bash
# Search for any non-compliant model usage
grep -r "gpt-4o\|gpt-3.5\|gpt-4o-mini" plans/ --include="*.py"
```

Should only show the Realtime API usage in main.py using `gpt-4o-realtime-preview`.