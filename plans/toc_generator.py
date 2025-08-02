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
Create a detailed, hierarchical table of contents in markdown format that shows the structure and organization of the document.

The table of contents should:
1. Use proper markdown heading hierarchy (##, ###, ####)
2. Include page numbers or section numbers if present in the document
3. Show all major sections and important subsections
4. Maintain the exact structure as it appears in the document
5. Include appendices, glossaries, or reference sections if present

Format the output as a clean markdown outline that can be used for navigation. For example:

## Table of Contents

### 1. Introduction
- Welcome to Your Plan
- How to Use This Document

### 2. Plan Benefits Overview
#### 2.1 Medical Services
- Primary Care
- Specialist Care
- Hospital Services
#### 2.2 Prescription Drugs
- Formulary Tiers
- Mail Order Options

### 3. Cost Sharing
#### 3.1 Deductibles and Out-of-Pocket Maximums
#### 3.2 Copayments and Coinsurance

[Continue with all sections...]

IMPORTANT: Extract the ACTUAL table of contents structure from the document. Do not create a generic structure.

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