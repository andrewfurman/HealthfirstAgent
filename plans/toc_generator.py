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

The table of contents should:
1. Use simple markdown lists and headers without ANY dots, periods, or dashes as separators
2. Put page numbers (if present) right after the section name with just a space
3. Show all major sections and important subsections
4. Maintain the exact structure as it appears in the document
5. Keep section titles concise - use abbreviations where appropriate

Format Rules:
- NO dots (.........) between titles and page numbers
- Just use a space and the page number: "Section Name 42"
- Use markdown headers (##, ###) for main sections
- Use bullet points (-) for subsections
- Keep it clean and minimal

Example format:

## Table of Contents

### A. Disclaimers 2

### B. Frequently asked questions 3

### C. Overview of services 9

### D. Additional services CompleteCare covers 31

### E. Benefits covered outside of CompleteCare 32

### F. Services not covered 33

### G. Your rights and responsibilities 34

### H. How to file a complaint 37

IMPORTANT: 
- Extract the ACTUAL sections from the document
- NO decorative dots or dashes between text and page numbers
- Keep section names short and clear

PLAN DOCUMENT TEXT:
{document_text[:40000]}  # Limit to first 40k characters for context
"""

        # Call GPT-4.1
        response = client.chat.completions.create(
            model="gpt-4.1",  # Using GPT-4.1 as requested
            messages=[
                {"role": "system", "content": "You are an expert at analyzing document structure and creating detailed tables of contents. Extract the exact structure as it appears in the document."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Very low temperature for accuracy
            max_tokens=2000  # Enough for a detailed TOC
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