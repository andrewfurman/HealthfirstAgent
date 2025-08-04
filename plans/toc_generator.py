"""
Generate table of contents for plan documents using OpenAI GPT-4.1
"""
import os
from typing import Optional, Tuple
from openai import OpenAI


def gpt_generate_table_of_contents(plan_id: str, plan_name: str, document_text: str, session) -> Tuple[bool, str]:
    """
    Generate a structured table of contents from a plan document using GPT-4.1.
    
    Args:
        plan_id: The ID of the plan
        plan_name: The name of the plan
        document_text: The full extracted text from the plan document
        session: Database session for updating the plan
        
    Returns:
        Tuple of (success, message/table_of_contents)
    """
    try:
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False, "OPENAI_API_KEY environment variable not set"
        
        client = OpenAI(api_key=api_key)
        
        # Construct the prompt
        prompt = f"""You are analyzing a health insurance plan document for "{plan_name}". 
Create a clean, hierarchical table of contents in markdown format that shows the structure and organization of the document.

CRITICAL REQUIREMENTS:
1. ALWAYS include page numbers when they exist in the document
2. Look for patterns like "page X", "...X", "X" at the end of section titles
3. Extract page numbers from any table of contents already in the document
4. If no explicit TOC exists, look for section headers with page breaks or "Page X of Y" markers

**SPECIAL FOCUS - CALL CENTER REQUIREMENTS:**
You must specifically identify and note pages that contain:
- **COPAYS/COPAYMENTS** - Any pages with copay amounts, copay tables, or copayment information
- **COINSURANCE** - Any pages with coinsurance percentages or coinsurance details
- **DEDUCTIBLES** - Any pages with deductible amounts or deductible information
- **PRIOR AUTHORIZATION** - Any pages listing services requiring prior authorization or PA requirements

When you find these topics, add a note like: "(contains copay info)" or "(contains PA requirements)" after the section title.

The table of contents should:
1. Use simple markdown lists and headers without ANY dots, periods, or dashes as separators
2. Put page numbers (if present) right after the section name with just a space
3. Show all major sections and important subsections
4. Maintain the exact structure as it appears in the document
5. Keep section titles concise - use abbreviations where appropriate
6. **HIGHLIGHT pages with copay, coinsurance, deductible, and prior authorization information**

Format Rules:
- NO dots (.........) between titles and page numbers
- Just use a space and the page number: "Section Name 42"
- Use markdown headers (##, ###) for main sections
- Use bullet points (-) for subsections
- Add special notes for key information: "Section Name 42 (contains copay tables)"
- Keep it clean and minimal

Example format:

## Table of Contents

### A. Disclaimers 2

### B. Frequently asked questions 3

### C. Overview of services 9 (contains copay info)

### D. Additional services CompleteCare covers 31

### E. Benefits covered outside of CompleteCare 32 (contains coinsurance rates)

### F. Services not covered 33 (contains prior authorization requirements)

### G. Your rights and responsibilities 34

### H. How to file a complaint 37

### I. Cost-sharing summary 45 (contains deductible and copay tables)

IMPORTANT: 
- Extract the ACTUAL sections from the document
- NO decorative dots or dashes between text and page numbers
- Keep section names short and clear
- LOOK CAREFULLY for page numbers - they are often present in the original TOC or as "Page X" markers
- If you see patterns like "Section Name.....14" or "Section Name — 14", extract the page number as 14
- **SCAN THE ENTIRE DOCUMENT** for any mention of copays, coinsurance, deductibles, or prior authorization and note which pages contain this information
- Call center agents frequently need to reference these specific pages, so accuracy is critical

PLAN DOCUMENT TEXT:
{document_text[:60000]}  # Increased limit to 60k characters for better coverage of cost-sharing sections
"""

        # Call GPT-4.1 with enhanced instructions
        response = client.chat.completions.create(
            model="gpt-4.1",  # Using GPT-4.1 as required for text-based queries
            messages=[
                {"role": "system", "content": "You are an expert at analyzing health insurance plan documents and creating detailed tables of contents. You specialize in identifying and highlighting pages that contain copay information, coinsurance rates, deductible amounts, and prior authorization requirements for call center agents. Extract the exact structure as it appears in the document and pay special attention to cost-sharing and authorization sections."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Very low temperature for accuracy
            max_tokens=3000  # More tokens for detailed TOC with annotations
        )
        
        toc = response.choices[0].message.content
        
        # Update the plan in the database
        from plans.plans_model import Plan
        plan = session.query(Plan).filter_by(id=plan_id).first()
        if plan:
            plan.table_of_contents = toc
            return True, f"Successfully generated table of contents for {plan_name} ({len(toc)} characters)"
        else:
            return False, f"Plan {plan_id} not found in database"
            
    except Exception as e:
        return False, f"Error generating table of contents: {str(e)}"


def gpt_generate_toc_for_plan(plan_id: str, session) -> Tuple[bool, str]:
    """
    Generate table of contents for a specific plan using its extracted document text.
    """
    from plans.plans_model import Plan
    
    plan = session.query(Plan).filter_by(id=plan_id).first()
    if not plan:
        return False, f"Plan with ID {plan_id} not found"
    
    if not plan.plan_document_full_text:
        return False, f"Plan '{plan.short_name}' has no extracted document text"
    
    return gpt_generate_table_of_contents(
        plan_id=plan.id,
        plan_name=plan.short_name,
        document_text=plan.plan_document_full_text,
        session=session
    )