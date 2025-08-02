# OpenAI Realtime API Function Calling Implementation Plan

## Overview
This document outlines the plan to integrate function calling capabilities with the OpenAI Realtime Voice API for the Healthfirst call center assistant. This will enable the voice assistant to query the database and retrieve real-time information about health plans during voice conversations.

## Current Architecture
- **Voice Interface**: Browser-based WebRTC using OpenAI Realtime API
- **Backend**: Flask application with PostgreSQL database
- **Data Available**: 27 health plans with compressed summaries, table of contents, and full document text
- **Current Flow**: Voice assistant uses static instructions from `call_center_guide.md`

## Proposed Function Calling Architecture

### 1. Available Functions to Implement

#### Priority Functions (Phase 1)

##### `get_plan_coverage_summary`
```python
def get_plan_coverage_summary(plan_name: str) -> dict:
    """
    Retrieve the compressed summary and key details for a specific plan.
    Returns: {
        "plan_id": int,
        "short_name": str,
        "full_name": str,
        "plan_type": str,
        "compressed_summary": str,  # Full markdown summary with all coverage details
        "document_url": str
    }
    """
```

##### `get_plan_table_of_contents`
```python
def get_plan_table_of_contents(plan_name: str) -> dict:
    """
    Retrieve the table of contents to help locate specific information.
    Returns: {
        "plan_id": int,
        "plan_name": str,
        "table_of_contents": str,  # Markdown formatted TOC with page numbers
        "sections": [
            {
                "title": str,
                "page": int,
                "subsections": list
            }
        ]
    }
    """
```

##### `search_plan_document`
```python
def search_plan_document(plan_name: str, search_term: str) -> dict:
    """
    Search within a plan's document for specific terms and return relevant sections.
    Useful for finding specific information like "prior authorization" or "emergency care".
    Returns: {
        "plan_name": str,
        "search_term": str,
        "results": [
            {
                "section": str,
                "page": int,
                "excerpt": str,  # Context around the search term
                "relevance": float
            }
        ]
    }
    """
```

#### Secondary Functions (Phase 2)

##### `get_plan_by_name`
```python
def get_plan_by_name(plan_name: str) -> dict:
    """
    Retrieve basic plan information by short name or full name.
    Returns: plan details including type, premium, key features
    """
```

##### `search_plans_by_type`
```python
def search_plans_by_type(plan_type: str) -> list:
    """
    Search for plans by type (Medicare, Medicaid, Dual Eligible, Marketplace).
    Returns: list of matching plans with basic info
    """
```

##### `compare_plans`
```python
def compare_plans(plan_names: list, comparison_aspects: list) -> dict:
    """
    Compare multiple plans across specified aspects.
    comparison_aspects: ["premium", "deductible", "copays", "coverage"]
    Returns: comparison table
    """
```

### 2. Implementation Steps

#### Phase 1: Backend Function Implementation
1. Create `realtime_functions.py` in the root directory
2. Implement each function to query the PostgreSQL database
3. Add error handling and validation for each function
4. Create unit tests for all functions

#### Phase 2: OpenAI Realtime API Integration
1. Update `/session` endpoint in `main.py` to include function definitions
2. Modify the session configuration to enable function calling:
   ```python
   session_config = {
       "model": "gpt-4o-realtime-preview",
       "voice": "alloy",
       "instructions": instructions_content,
       "tools": [
           {
               "type": "function",
               "name": "get_plan_coverage_summary",
               "description": "Get comprehensive coverage details and benefits for a health plan",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "plan_name": {
                           "type": "string",
                           "description": "The name or partial name of the health plan (e.g., 'Gold', 'CompleteCare', 'Signature HMO')"
                       }
                   },
                   "required": ["plan_name"]
               }
           },
           {
               "type": "function",
               "name": "get_plan_table_of_contents",
               "description": "Get the table of contents to find specific sections and page numbers in plan documents",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "plan_name": {
                           "type": "string",
                           "description": "The name or partial name of the health plan"
                       }
                   },
                   "required": ["plan_name"]
               }
           },
           {
               "type": "function",
               "name": "search_plan_document",
               "description": "Search within a plan's documents for specific information",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "plan_name": {
                           "type": "string",
                           "description": "The name or partial name of the health plan"
                       },
                       "search_term": {
                           "type": "string",
                           "description": "The term or phrase to search for (e.g., 'prior authorization', 'emergency care', 'prescription drugs')"
                       }
                   },
                   "required": ["plan_name", "search_term"]
               }
           }
       ],
       "tool_choice": "auto"  # Let the model decide when to use tools
   }
   ```

#### Phase 3: WebSocket Handler for Function Execution
1. Create WebSocket endpoint to handle function calls from Realtime API
2. Implement function execution router
3. Return results in the format expected by OpenAI Realtime API
4. Add logging for all function calls for debugging

#### Phase 4: Frontend Updates
1. Update `static/script.js` to handle function calling events
2. Add visual indicators when functions are being called
3. Display function results in the transcript
4. Add error handling for failed function calls

#### Phase 5: Enhanced Instructions
1. Update `call_center_guide.md` to reference available functions
2. Add examples of when to use each function
3. Include guidelines for function call decision making

### 3. Technical Considerations

#### Security
- Implement rate limiting for function calls
- Add authentication checks before database queries
- Sanitize all inputs to prevent SQL injection
- Log all function calls for audit purposes

#### Performance
- Implement caching for frequently requested data
- Use database connection pooling
- Add timeouts for long-running queries
- Consider implementing pagination for large result sets

#### Error Handling
- Graceful fallback when functions fail
- Clear error messages for the voice assistant to relay
- Retry logic for transient failures
- Circuit breaker pattern for database issues

### 4. Example Voice Interaction Flows

#### Example 1: Coverage Information
```
User: "What's the copay for a specialist visit with the Gold plan?"
Assistant: [Calls get_plan_coverage_summary("Gold")]
Assistant: "For the Gold Leaf Plan, specialist visits have a $40 copay after you meet your deductible. The plan has a $1,500 individual deductible. Would you like to know about any other coverage details?"
```

#### Example 2: Finding Specific Information in Documents
```
User: "Where can I find the prior authorization requirements in the CompleteCare plan documents?"
Assistant: [Calls get_plan_table_of_contents("CompleteCare")]
Assistant: "In the CompleteCare D-SNP plan documents, prior authorization requirements are covered in Section 4: 'Getting your medical services and supplies' on page 89, and there's also a specific subsection 4.2 'Services that require prior authorization' on page 95. Would you like me to tell you which specific services require prior authorization?"

User: "Yes, what services need prior auth?"
Assistant: [Calls search_plan_document("CompleteCare", "prior authorization")]
Assistant: "Based on the plan documents, these services require prior authorization for CompleteCare D-SNP:
- Inpatient hospital stays
- Skilled nursing facility care beyond 20 days
- Outpatient surgery
- Advanced imaging like MRI and CT scans
- Durable medical equipment over $500
- Non-emergency ambulance services
The full list is on page 95-97 of your member handbook."
```

#### Example 3: Comparing Plans
```
User: "I need help choosing between the Signature HMO and Signature PPO plans"
Assistant: [Calls get_plan_coverage_summary("Signature HMO")]
Assistant: [Calls get_plan_coverage_summary("Signature PPO")]
Assistant: "Let me compare these Medicare Advantage plans for you:

The Signature HMO has:
- $0 monthly premium
- $20 PCP visits, $35 specialist visits
- $3,400 out-of-pocket maximum
- Fitness benefit included
- Must use in-network providers

The Signature PPO has:
- $0 monthly premium  
- $15 PCP visits, $40 specialist visits
- $3,900 out-of-pocket maximum
- $725 annual Flex benefit for dental, vision, or OTC
- Can see out-of-network providers at higher cost

The main difference is the PPO gives you more flexibility to see any doctor, while the HMO has slightly lower copays but requires you to stay in-network."
```

### 5. Initial Context Loading Strategy

#### Approach: Preload Summarized Plan Data at Session Start
Instead of using function calls for basic information, preload a compressed summary of all plans when the Realtime session starts. This will:
- Reduce latency for common questions
- Minimize function calls
- Provide immediate access to basic plan information

#### Implementation
1. Create a `get_all_plans_summary()` function that returns <2000 words:
   ```python
   def get_all_plans_summary() -> str:
       """
       Generate a condensed summary of all health plans.
       Includes: plan names, types, key features, price ranges.
       Returns: Formatted string under 2000 words
       """
   ```

2. Include this summary in the initial instructions:
   ```python
   # In main.py /session endpoint
   plans_summary = get_all_plans_summary()
   instructions_content = f"""
   {original_instructions}
   
   ## Available Health Plans Summary
   {plans_summary}
   
   Use this information for quick answers. For detailed questions, 
   use the available functions to query specific plan details.
   """
   ```

3. Summary Format Example:
   ```
   MEDICARE PLANS:
   • 65+ Plan: HMO, $0 premium, $20 PCP/$40 specialist, $3,900 OOP max
   • Signature HMO: Premium HMO, lower OOP max, fitness benefit included
   • Signature PPO: PPO with out-of-network coverage, $725 Flex benefit
   
   MEDICAID PLANS:
   • Essential Plans (EP1-4): $0-20 premiums, income-based, no deductible
   • Medicaid Managed Care: $0 copays for most services
   
   DUAL ELIGIBLE PLANS:
   • CompleteCare D-SNP: $280/mo OTC benefit, comprehensive coverage
   • Connection Plan: $170 quarterly OTC, standard benefits
   
   MARKETPLACE PLANS:
   • Bronze: Lower premium, higher deductible ($5,300)
   • Silver: Moderate premium/deductible, CSR variants available
   • Gold: Higher premium, lower out-of-pocket costs
   • Platinum: Highest premium, lowest cost-sharing
   ```

### 6. Testing Plan

1. **Unit Tests**: Test each function independently with mock data
2. **Integration Tests**: Test function calls through the Realtime API
3. **Voice Testing**: Manual testing of common scenarios
4. **Load Testing**: Ensure system handles multiple concurrent sessions
5. **Error Scenarios**: Test handling of database outages, invalid inputs

### 7. Deployment Steps

1. Deploy backend functions and test via API
2. Update Realtime session configuration
3. Test in development environment
4. Deploy to staging for user acceptance testing
5. Production deployment with monitoring

### 8. Success Metrics

- Function call success rate > 99%
- Average function response time < 200ms
- Reduction in "I don't know" responses by 80%
- Improved call resolution rate
- Reduced average call duration

### 9. Future Enhancements

- Add member eligibility checking functions
- Integrate with provider network database
- Add claims status checking
- Implement prescription drug interaction checking
- Add multilingual support for function responses