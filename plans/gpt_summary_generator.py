"""
Generate compressed summaries of plan documents using OpenAI GPT-4
"""
import os
from typing import Optional, Tuple
from openai import OpenAI


def generate_compressed_summary(plan_id: str, plan_name: str, document_text: str, session) -> Tuple[bool, str]:
    """
    Generate a compressed summary of a plan document using GPT-4.
    
    Args:
        plan_id: The ID of the plan
        plan_name: The name of the plan
        document_text: The full extracted text from the plan document
        session: Database session for updating the plan
        
    Returns:
        Tuple of (success, message/summary)
    """
    try:
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False, "OPENAI_API_KEY environment variable not set"
        
        client = OpenAI(api_key=api_key)
        
        # Construct the prompt
        prompt = f"""You are a health insurance expert creating a reference guide for call center agents at Healthfirst, a New York health insurance company.

Given the following health insurance plan document for "{plan_name}", create a comprehensive but compact summary in markdown format.

The summary MUST include ALL of the following information if available in the document:

## Plan Overview
- Full plan name and plan type
- Premium information (monthly costs)
- Annual deductible amounts
- Out-of-pocket maximum amounts

## Medical Services Coverage
For each service type, include copay/coinsurance amounts and any limitations:
- **Primary Care Visits**: Copay amount, any visit limits
- **Specialist Visits**: Copay amount, referral requirements
- **Preventive Care**: Coverage details (should typically be $0)
- **Emergency Room**: Copay amount, when waived
- **Urgent Care**: Copay amount
- **Hospital Inpatient**: Copay/coinsurance per admission or per day
- **Hospital Outpatient**: Copay/coinsurance
- **Mental Health Services**: Inpatient and outpatient copays
- **Substance Abuse Treatment**: Inpatient and outpatient copays

## Prescription Drug Coverage
- Drug tiers and copay/coinsurance for each tier:
  - Tier 1 (Generic)
  - Tier 2 (Preferred Brand)
  - Tier 3 (Non-Preferred Brand)
  - Tier 4 (Specialty)
  - Mail order options
- Deductible if applicable

## Additional Benefits
- **Vision**: Coverage details, copays
- **Dental**: Coverage details, copays
- **Hearing**: Coverage details, hearing aid allowance
- **Over-the-Counter (OTC)**: Allowance amount and frequency
- **Fitness Benefits**: Gym membership or fitness programs
- **Transportation**: Number of trips, limitations

## Prior Authorization Requirements
- List all services requiring prior authorization
- Any referral requirements

## Network and Coverage Area
- Network type (HMO, PPO, EPO)
- Out-of-network coverage (if applicable)
- Coverage area/counties

## Important Limitations and Exclusions
- Key services not covered
- Important limits or maximums
- Cost-sharing waivers (if any)

Format the summary using clear markdown headers, bullet points, and tables where appropriate. Make it scannable for call center agents who need quick answers.

PLAN DOCUMENT TEXT:
{document_text[:50000]}  # Limit to first 50k characters to avoid token limits
"""

        # Call GPT-4
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Using gpt-4-turbo-preview as gpt-4.1 doesn't exist
            messages=[
                {"role": "system", "content": "You are an expert at analyzing health insurance documents and creating clear, comprehensive summaries for call center use."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=4000  # Generous token limit for detailed summary
        )
        
        summary = response.choices[0].message.content
        
        # Update the plan in the database
        from plans.plans_model import Plan
        plan = session.query(Plan).filter_by(id=plan_id).first()
        if plan:
            plan.compressed_summary = summary
            return True, f"Successfully generated summary for {plan_name} ({len(summary)} characters)"
        else:
            return False, f"Plan {plan_id} not found in database"
            
    except Exception as e:
        return False, f"Error generating summary: {str(e)}"


def generate_summary_for_plan(plan_id: str, session) -> Tuple[bool, str]:
    """
    Generate compressed summary for a specific plan using its extracted document text.
    """
    from plans.plans_model import Plan
    
    plan = session.query(Plan).filter_by(id=plan_id).first()
    if not plan:
        return False, f"Plan with ID {plan_id} not found"
    
    if not plan.plan_document_full_text:
        return False, f"Plan '{plan.short_name}' has no extracted document text"
    
    return generate_compressed_summary(
        plan_id=plan.id,
        plan_name=plan.short_name,
        document_text=plan.plan_document_full_text,
        session=session
    )