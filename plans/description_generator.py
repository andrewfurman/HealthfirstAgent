"""
Generate clear one-sentence descriptions for health plans using OpenAI GPT
"""
import os
from typing import Optional, Tuple
from openai import OpenAI


def generate_plan_description(plan_id: str, plan_name: str, full_name: str, plan_type: str, compressed_summary: str, session) -> Tuple[bool, str]:
    """
    Generate a clear one-sentence description of what a health plan is for.
    
    Args:
        plan_id: The ID of the plan
        plan_name: The short name of the plan
        full_name: The full name of the plan
        plan_type: The type of plan (Medicare, Medicaid, Dual Eligible, Marketplace)
        compressed_summary: The existing summary with plan details
        session: Database session for updating the plan
        
    Returns:
        Tuple of (success, message/description)
    """
    try:
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False, "OPENAI_API_KEY environment variable not set"
        
        client = OpenAI(api_key=api_key)
        
        # Extract key info from compressed summary if available
        context = f"""
Plan Short Name: {plan_name}
Plan Full Name: {full_name}
Plan Type: {plan_type}

{f'Plan Details: {compressed_summary[:2000]}' if compressed_summary else 'No detailed summary available'}
"""
        
        # Construct the prompt
        prompt = f"""Based on the following health insurance plan information, write ONE clear, simple sentence that explains what this plan is and who it's for. 

The sentence should:
- Be understandable to someone unfamiliar with health insurance
- Mention the target population (seniors, low-income, children, employees, etc.)
- Include the most important distinguishing feature
- Be 20-30 words maximum
- Avoid jargon and acronyms (except well-known ones like HMO, PPO)
- Focus on WHO the plan serves and WHAT makes it unique

Examples of good descriptions:
- "Medicare Advantage HMO plan for seniors 65 and older with $0 monthly premium and comprehensive coverage."
- "Free health insurance for children under 19 from families who earn too much for Medicaid but can't afford private insurance."
- "Medicaid plan with enhanced mental health and addiction services for adults with behavioral health needs."
- "Lower premium marketplace plan with higher deductibles for healthy individuals who mainly want emergency coverage."

PLAN INFORMATION:
{context}

Write only the one-sentence description, nothing else:"""

        # Call GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o-mini for efficiency
            messages=[
                {"role": "system", "content": "You are an expert at writing clear, simple explanations of complex health insurance plans for the general public."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=100  # Limit to ensure concise response
        )
        
        description = response.choices[0].message.content.strip()
        
        # Remove quotes if GPT added them
        description = description.strip('"').strip("'")
        
        # Update the plan in the database
        from plans.plans_model import Plan
        plan = session.query(Plan).filter_by(id=plan_id).first()
        if plan:
            plan.plan_description = description
            return True, description
        else:
            return False, f"Plan {plan_id} not found in database"
            
    except Exception as e:
        return False, f"Error generating description: {str(e)}"


def generate_description_for_plan(plan_id: str, session) -> Tuple[bool, str]:
    """
    Generate description for a specific plan using its existing data.
    """
    from plans.plans_model import Plan
    
    plan = session.query(Plan).filter_by(id=plan_id).first()
    if not plan:
        return False, f"Plan with ID {plan_id} not found"
    
    return generate_plan_description(
        plan_id=plan.id,
        plan_name=plan.short_name,
        full_name=plan.full_name,
        plan_type=plan.plan_type,
        compressed_summary=plan.compressed_summary,
        session=session
    )


def generate_all_descriptions(session) -> dict:
    """
    Generate descriptions for all plans that don't have one.
    """
    from plans.plans_model import Plan
    
    results = {
        'total_plans': 0,
        'successful': 0,
        'failed': 0,
        'results': []
    }
    
    # Get all plans (regenerate all descriptions)
    plans = session.query(Plan).all()
    
    results['total_plans'] = len(plans)
    
    for plan in plans:
        print(f"Generating description for {plan.short_name}...")
        success, message = generate_description_for_plan(plan.id, session)
        
        if success:
            results['successful'] += 1
            print(f"✓ {plan.short_name}: {message}")
        else:
            results['failed'] += 1
            print(f"✗ {plan.short_name}: {message}")
        
        results['results'].append({
            'plan_id': plan.id,
            'plan_name': plan.short_name,
            'success': success,
            'description': message if success else None,
            'error': message if not success else None
        })
        
        # Commit after each successful generation
        if success:
            session.commit()
    
    return results