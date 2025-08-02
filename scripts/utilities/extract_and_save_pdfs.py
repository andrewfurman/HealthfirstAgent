#!/usr/bin/env python3
"""
Extract PDFs and save to database automatically
"""
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plans.plans_model import Plan

load_dotenv()

def extract_with_pymupdf(pdf_path):
    """Extract using PyMuPDF (fitz)"""
    try:
        text = ""
        doc = fitz.open(pdf_path)
        print(f"  Found {len(doc)} pages")
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        doc.close()
        return text if text.strip() else None
    except Exception as e:
        print(f"  Extraction failed: {e}")
        return None

def main():
    # Map PDF files to plan names
    pdf_mappings = [
        ("plan_pdfs/lip_plan.pdf", "LIP", 12),
        # Add more mappings as needed
    ]
    
    # Also try to download and extract the other problematic PDFs
    other_plans = [
        (7, "Medicaid Managed Care", "https://assets.healthfirst.org/api/v2/assets/HF-2025-Medicaid-Handbook.pdf/"),
        (13, "MLTC", "https://assets.healthfirst.org/api/v2/assets/HF_2024SHP-Member-Handbook-508-update.pdf/"),
        (16, "Signature HMO", "https://assets.healthfirst.org/pdf_Bz89uoJNB1ZG/2025-signature-hmo-summary-of-benefits-web-english"),
        (22, "Leaf Platinum", "https://assets.healthfirst.org/api/v2/assets/HF-2025-Platinum-Leaf-SBC.pdf/")
    ]
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Process LIP first (already downloaded)
    for pdf_path, plan_name, plan_id in pdf_mappings:
        if os.path.exists(pdf_path):
            print(f"\nProcessing {plan_name} from {pdf_path}")
            text = extract_with_pymupdf(pdf_path)
            
            if text and len(text) > 100:
                print(f"  ✓ Extracted {len(text)} characters")
                
                plan = session.query(Plan).filter_by(id=plan_id).first()
                if plan:
                    plan.plan_document_full_text = text
                    session.commit()
                    print(f"  ✓ Saved to database for {plan_name}")
                else:
                    print(f"  ✗ Plan ID {plan_id} not found")
        else:
            print(f"  File not found: {pdf_path}")
    
    # Try downloading and extracting others
    import requests
    for plan_id, plan_name, url in other_plans:
        print(f"\n{'='*60}")
        print(f"Processing {plan_name} (ID: {plan_id})")
        
        # Download
        pdf_path = f"plan_pdfs/{plan_name.replace(' ', '_').lower()}.pdf"
        try:
            print(f"  Downloading from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"  Downloaded {len(response.content)} bytes")
            
            # Extract
            text = extract_with_pymupdf(pdf_path)
            if text and len(text) > 100:
                print(f"  ✓ Extracted {len(text)} characters")
                
                plan = session.query(Plan).filter_by(id=plan_id).first()
                if plan:
                    plan.plan_document_full_text = text
                    session.commit()
                    print(f"  ✓ Saved to database for {plan_name}")
        except Exception as e:
            print(f"  Failed: {e}")
    
    session.close()
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()