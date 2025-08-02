"""
Functions for OpenAI Realtime API to query health plan information.
These functions are called by the voice assistant during conversations.
"""
import json
import re
from typing import Dict, List, Optional
from sqlalchemy import or_, func
from plans.plans_model import Plan


def get_plan_coverage_summary(plan_name: str, session) -> Dict:
    """
    Retrieve the compressed summary and key details for a specific plan.
    
    Args:
        plan_name: The name or partial name of the health plan
        session: Database session
        
    Returns:
        Dictionary with plan details and coverage summary
    """
    try:
        # Search for plan by name (case-insensitive partial match)
        plan = session.query(Plan).filter(
            or_(
                func.lower(Plan.short_name).contains(func.lower(plan_name)),
                func.lower(Plan.full_name).contains(func.lower(plan_name))
            )
        ).first()
        
        if not plan:
            return {
                "success": False,
                "error": f"No plan found matching '{plan_name}'. Please try a different name."
            }
        
        # Return plan details with compressed summary
        return {
            "success": True,
            "plan_id": plan.id,
            "short_name": plan.short_name,
            "full_name": plan.full_name,
            "plan_type": plan.plan_type or "Not specified",
            "compressed_summary": plan.compressed_summary or "No summary available",
            "document_url": plan.summary_of_benefits_url or None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving plan information: {str(e)}"
        }


def get_plan_table_of_contents(plan_name: str, session) -> Dict:
    """
    Retrieve the table of contents to help locate specific information.
    
    Args:
        plan_name: The name or partial name of the health plan
        session: Database session
        
    Returns:
        Dictionary with table of contents and parsed sections
    """
    try:
        # Search for plan by name
        plan = session.query(Plan).filter(
            or_(
                func.lower(Plan.short_name).contains(func.lower(plan_name)),
                func.lower(Plan.full_name).contains(func.lower(plan_name))
            )
        ).first()
        
        if not plan:
            return {
                "success": False,
                "error": f"No plan found matching '{plan_name}'. Please try a different name."
            }
        
        if not plan.table_of_contents:
            return {
                "success": False,
                "error": f"No table of contents available for {plan.short_name}"
            }
        
        # Parse the table of contents to extract sections with page numbers
        sections = parse_table_of_contents(plan.table_of_contents)
        
        return {
            "success": True,
            "plan_id": plan.id,
            "plan_name": plan.short_name,
            "table_of_contents": plan.table_of_contents,
            "sections": sections
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving table of contents: {str(e)}"
        }


def search_plan_document(plan_name: str, search_term: str, session) -> Dict:
    """
    Search within a plan's document for specific terms and return relevant sections.
    
    Args:
        plan_name: The name or partial name of the health plan
        search_term: The term or phrase to search for
        session: Database session
        
    Returns:
        Dictionary with search results and relevant excerpts
    """
    try:
        # Search for plan by name
        plan = session.query(Plan).filter(
            or_(
                func.lower(Plan.short_name).contains(func.lower(plan_name)),
                func.lower(Plan.full_name).contains(func.lower(plan_name))
            )
        ).first()
        
        if not plan:
            return {
                "success": False,
                "error": f"No plan found matching '{plan_name}'. Please try a different name."
            }
        
        if not plan.plan_document_full_text:
            # Fall back to searching in compressed summary
            if plan.compressed_summary:
                results = search_in_text(plan.compressed_summary, search_term)
                return {
                    "success": True,
                    "plan_name": plan.short_name,
                    "search_term": search_term,
                    "source": "compressed_summary",
                    "results": results
                }
            else:
                return {
                    "success": False,
                    "error": f"No document text available for {plan.short_name}"
                }
        
        # Search in the full document text
        results = search_in_text(plan.plan_document_full_text, search_term)
        
        return {
            "success": True,
            "plan_name": plan.short_name,
            "search_term": search_term,
            "source": "full_document",
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching document: {str(e)}"
        }


def get_all_plans_summary(session) -> str:
    """
    Generate a condensed summary of all health plans for initial context.
    This is loaded at the start of each voice session.
    
    Args:
        session: Database session
        
    Returns:
        Formatted string under 2000 words with all plan summaries
    """
    try:
        plans = session.query(Plan).order_by(Plan.plan_type, Plan.short_name).all()
        
        # Group plans by type
        plans_by_type = {}
        for plan in plans:
            plan_type = plan.plan_type or "Other"
            if plan_type not in plans_by_type:
                plans_by_type[plan_type] = []
            plans_by_type[plan_type].append(plan)
        
        # Build summary text
        summary_parts = []
        
        for plan_type in ["Medicare", "Medicaid", "Dual Eligible", "Marketplace", "Other"]:
            if plan_type not in plans_by_type:
                continue
                
            summary_parts.append(f"\n{plan_type.upper()} PLANS:")
            
            for plan in plans_by_type[plan_type]:
                # Extract key info from compressed summary if available
                key_info = extract_key_info(plan.compressed_summary) if plan.compressed_summary else {}
                
                plan_summary = f"• {plan.short_name}: {plan.full_name}"
                
                if key_info:
                    details = []
                    if key_info.get('premium'):
                        details.append(f"${key_info['premium']} premium")
                    if key_info.get('pcp_copay'):
                        details.append(f"${key_info['pcp_copay']} PCP")
                    if key_info.get('specialist_copay'):
                        details.append(f"${key_info['specialist_copay']} specialist")
                    if key_info.get('oop_max'):
                        details.append(f"${key_info['oop_max']} OOP max")
                    if key_info.get('special_benefits'):
                        details.append(key_info['special_benefits'])
                    
                    if details:
                        plan_summary += f" - {', '.join(details)}"
                
                summary_parts.append(plan_summary)
        
        full_summary = "\n".join(summary_parts)
        
        # Ensure it's under 2000 words (roughly 12000 characters)
        if len(full_summary) > 12000:
            full_summary = full_summary[:11997] + "..."
        
        return full_summary
        
    except Exception as e:
        return f"Error generating plans summary: {str(e)}"


# Helper functions

def parse_table_of_contents(toc_text: str) -> List[Dict]:
    """
    Parse markdown TOC to extract sections with page numbers.
    """
    sections = []
    lines = toc_text.split('\n')
    
    for line in lines:
        # Look for patterns like "### 1. Section Name (Page 10)"
        match = re.match(r'^(#{2,4})\s*(\d+\.?\d*\.?\d*\.?)?\s*(.+?)(?:\s*\((?:Page|page|p\.)\s*(\d+)\))?$', line.strip())
        if match:
            level = len(match.group(1)) - 1  # Number of # symbols minus 1
            number = match.group(2) or ""
            title = match.group(3).strip()
            page = int(match.group(4)) if match.group(4) else None
            
            sections.append({
                "level": level,
                "number": number,
                "title": title,
                "page": page
            })
    
    return sections


def search_in_text(text: str, search_term: str, context_length: int = 200) -> List[Dict]:
    """
    Search for a term in text and return excerpts with context.
    """
    results = []
    search_term_lower = search_term.lower()
    text_lower = text.lower()
    
    # Find all occurrences
    start = 0
    while True:
        index = text_lower.find(search_term_lower, start)
        if index == -1:
            break
        
        # Extract context around the match
        context_start = max(0, index - context_length)
        context_end = min(len(text), index + len(search_term) + context_length)
        excerpt = text[context_start:context_end]
        
        # Clean up excerpt
        if context_start > 0:
            excerpt = "..." + excerpt
        if context_end < len(text):
            excerpt = excerpt + "..."
        
        # Try to find section heading before this match
        section = find_section_heading(text, index)
        
        # Try to find page number near this match
        page = find_page_number(text, index)
        
        results.append({
            "section": section,
            "page": page,
            "excerpt": excerpt.strip(),
            "position": index
        })
        
        start = index + 1
        
        # Limit to 5 results
        if len(results) >= 5:
            break
    
    return results


def find_section_heading(text: str, position: int) -> Optional[str]:
    """
    Find the nearest section heading before a position in text.
    """
    # Look backwards for a heading pattern
    text_before = text[:position]
    lines = text_before.split('\n')
    
    for line in reversed(lines[-10:]):  # Check last 10 lines
        if re.match(r'^(#{1,4}|\d+\.)\s+', line):
            return line.strip()
    
    return None


def find_page_number(text: str, position: int) -> Optional[int]:
    """
    Find the nearest page number reference near a position.
    """
    # Look for page number within 500 characters
    context_start = max(0, position - 250)
    context_end = min(len(text), position + 250)
    context = text[context_start:context_end]
    
    # Look for patterns like "Page 10", "page 10", "p. 10"
    match = re.search(r'(?:Page|page|p\.)\s*(\d+)', context)
    if match:
        return int(match.group(1))
    
    return None


def extract_key_info(summary: str) -> Dict:
    """
    Extract key information from a compressed summary for quick reference.
    """
    info = {}
    
    if not summary:
        return info
    
    # Extract premium
    premium_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:monthly\s*)?premium', summary, re.IGNORECASE)
    if premium_match:
        info['premium'] = premium_match.group(1).replace(',', '')
    
    # Extract PCP copay
    pcp_match = re.search(r'(?:PCP|Primary\s*Care).*?\$(\d+)', summary, re.IGNORECASE)
    if pcp_match:
        info['pcp_copay'] = pcp_match.group(1)
    
    # Extract specialist copay
    specialist_match = re.search(r'Specialist.*?\$(\d+)', summary, re.IGNORECASE)
    if specialist_match:
        info['specialist_copay'] = specialist_match.group(1)
    
    # Extract out-of-pocket maximum
    oop_match = re.search(r'(?:out-of-pocket|OOP).*?\$(\d+(?:,\d{3})*)', summary, re.IGNORECASE)
    if oop_match:
        info['oop_max'] = oop_match.group(1).replace(',', '')
    
    # Extract special benefits (OTC, Flex, etc.)
    otc_match = re.search(r'\$(\d+)\s*(?:monthly|quarterly)?\s*OTC', summary, re.IGNORECASE)
    if otc_match:
        info['special_benefits'] = f"${otc_match.group(1)} OTC benefit"
    
    flex_match = re.search(r'\$(\d+)\s*(?:annual)?\s*Flex', summary, re.IGNORECASE)
    if flex_match:
        info['special_benefits'] = f"${flex_match.group(1)} Flex benefit"
    
    return info