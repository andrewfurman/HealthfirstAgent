#!/usr/bin/env python3
"""
Fix the remaining 4 incomplete plans
"""
import os
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plans.plans_model import Plan

load_dotenv()

def download_and_extract(url, pdf_path):
    """Download PDF and extract text"""
    try:
        # Download with headers to bypass CDN issues
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        print(f"  Downloading...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save PDF
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"  Downloaded {len(response.content)} bytes")
        
        # Check if it's a real PDF
        if response.content[:4] != b'%PDF':
            print("  Warning: File doesn't start with %PDF")
        
        # Extract with PyMuPDF
        text = ""
        doc = fitz.open(pdf_path)
        print(f"  Found {len(doc)} pages")
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        doc.close()
        
        if text and len(text) > 100:
            print(f"  ✓ Extracted {len(text)} characters")
            return text
        else:
            print(f"  ✗ Extraction failed - no text found")
            return None
            
    except Exception as e:
        print(f"  Failed: {e}")
        return None

def main():
    # Remaining incomplete plans
    remaining_plans = [
        (7, "Medicaid Managed Care", "https://assets.healthfirst.org/pdf_s4dEdrCfKrFE/2025-medicaid-managed-care-member-handbook-english"),
        (13, "MLTC", "https://assets.healthfirst.org/pdf_SGMiY8LAUdLp/2025-senior-health-partners-member-handbook-english"),
        (16, "Signature HMO", "https://assets.healthfirst.org/pdf_pSh5lZgSJKCE/2025-signature-hmo-summary-of-benefits-english"),
        (22, "Leaf Platinum", "https://assets.healthfirst.org/pdf_dsF5didylWP2/2025-platinum-leaf-plan-summary-of-benefits-english")
    ]
    
    # Create plan_pdfs directory if it doesn't exist
    os.makedirs("plan_pdfs", exist_ok=True)
    
    # Connect to database
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    success_count = 0
    
    for plan_id, plan_name, url in remaining_plans:
        print(f"\n{'='*60}")
        print(f"Processing {plan_name} (ID: {plan_id})")
        print(f"URL: {url}")
        
        pdf_path = f"plan_pdfs/{plan_name.replace(' ', '_').lower()}.pdf"
        
        # Download and extract
        text = download_and_extract(url, pdf_path)
        
        if text:
            # Save to database
            plan = session.query(Plan).filter_by(id=plan_id).first()
            if plan:
                plan.plan_document_full_text = text
                session.commit()
                print(f"  ✓ Saved to database")
                success_count += 1
                
                # Save text file too
                text_path = pdf_path.replace('.pdf', '_extracted.txt')
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"  ✓ Text saved to {text_path}")
            else:
                print(f"  ✗ Plan not found in database")
    
    session.close()
    
    print(f"\n{'='*60}")
    print(f"Processing complete! Successfully extracted {success_count}/{len(remaining_plans)} plans")
    
    if success_count > 0:
        print("\nNext steps:")
        print("1. Generate summaries for the extracted plans")
        print("2. Generate table of contents for the extracted plans")

if __name__ == "__main__":
    main()