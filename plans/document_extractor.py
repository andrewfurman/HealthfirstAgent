"""
Utility for extracting text content from plan documents (PDFs and websites)
"""
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
from typing import Optional, Tuple


def extract_text_from_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract text content from a URL (either PDF or website).
    
    Returns:
        Tuple of (extracted_text, error_message)
    """
    try:
        # Make request with headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/pdf' in content_type:
            return extract_pdf_text(response.content)
        else:
            # Treat as HTML/website
            return extract_website_text(response.text)
            
    except requests.RequestException as e:
        return None, f"Error fetching URL: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def extract_pdf_text(pdf_content: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract text from PDF content.
    """
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text:
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            return None, "PDF appears to be empty or contains no extractable text"
            
        return full_text, None
        
    except Exception as e:
        return None, f"Error extracting PDF text: {str(e)}"


def extract_website_text(html_content: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract text from HTML/website content.
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text.strip():
            return None, "Website appears to be empty or contains no extractable text"
            
        return text, None
        
    except Exception as e:
        return None, f"Error extracting website text: {str(e)}"


def update_plan_document_text(plan_id: int, session) -> Tuple[bool, str]:
    """
    Update a specific plan's document text by fetching from its URL.
    
    Returns:
        Tuple of (success, message)
    """
    from plans.plans_model import Plan
    
    try:
        plan = session.query(Plan).filter_by(id=plan_id).first()
        if not plan:
            return False, f"Plan with ID {plan_id} not found"
        
        if not plan.summary_of_benefits_url:
            return False, f"Plan '{plan.short_name}' has no document URL"
        
        # Extract text from URL
        text, error = extract_text_from_url(plan.summary_of_benefits_url)
        
        if error:
            return False, f"Failed to extract text from '{plan.short_name}': {error}"
        
        # Update the plan
        plan.plan_document_full_text = text
        
        # Auto-detect document type if not set
        if not plan.document_type:
            if plan.summary_of_benefits_url.lower().endswith('.pdf'):
                plan.document_type = 'pdf'
            else:
                # Make a HEAD request to check content type
                try:
                    resp = requests.head(plan.summary_of_benefits_url, timeout=5)
                    if 'application/pdf' in resp.headers.get('Content-Type', '').lower():
                        plan.document_type = 'pdf'
                    else:
                        plan.document_type = 'website'
                except:
                    plan.document_type = 'website'
        
        return True, f"Successfully updated document text for '{plan.short_name}' ({len(text)} characters)"
        
    except Exception as e:
        return False, f"Database error: {str(e)}"