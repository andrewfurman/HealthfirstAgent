#!/usr/bin/env python3
"""
Try different PDF extraction methods for problematic plans
"""
import os
import requests
import PyPDF2
import pdfplumber
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plans.plans_model import Plan

# Load environment variables
load_dotenv()

def try_pypdf2_extraction(pdf_path):
    """Try extracting with PyPDF2"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"  PyPDF2: Found {len(pdf_reader.pages)} pages")
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
        return text if text.strip() else None
    except Exception as e:
        print(f"  PyPDF2 failed: {e}")
        return None

def try_pdfplumber_extraction(pdf_path):
    """Try extracting with pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            print(f"  pdfplumber: Found {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                    
                # Also try extracting tables
                tables = page.extract_tables()
                for table in tables:
                    text += "\n[TABLE]\n"
                    for row in table:
                        text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
            
        return text if text.strip() else None
    except Exception as e:
        print(f"  pdfplumber failed: {e}")
        return None

def download_pdf(url, filename):
    """Download PDF from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filepath = f"/tmp/{filename}"
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"  Downloaded {len(response.content)} bytes to {filepath}")
        return filepath
    except Exception as e:
        print(f"  Download failed: {e}")
        return None

def main():
    # Connect to database
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found")
        return
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get problematic plans
    problem_plans = [
        (7, "Medicaid Managed Care"),
        (12, "LIP"),
        (13, "MLTC"),
        (16, "Signature HMO"),
        (22, "Leaf Platinum")
    ]
    
    for plan_id, plan_name in problem_plans:
        print(f"\n{'='*60}")
        print(f"Processing {plan_name} (ID: {plan_id})")
        print('='*60)
        
        plan = session.query(Plan).filter_by(id=plan_id).first()
        if not plan or not plan.summary_of_benefits_url:
            print(f"  Plan not found or no URL")
            continue
        
        # Download the PDF
        pdf_path = download_pdf(plan.summary_of_benefits_url, f"plan_{plan_id}.pdf")
        if not pdf_path:
            continue
        
        # Try different extraction methods
        print("\nTrying extraction methods:")
        
        # Method 1: PyPDF2
        text = try_pypdf2_extraction(pdf_path)
        if text and len(text) > 100:
            print(f"  ✓ PyPDF2 extracted {len(text)} characters")
            plan.plan_document_full_text = text
            session.commit()
            print(f"  Saved to database!")
            continue
        
        # Method 2: pdfplumber
        text = try_pdfplumber_extraction(pdf_path)
        if text and len(text) > 100:
            print(f"  ✓ pdfplumber extracted {len(text)} characters")
            plan.plan_document_full_text = text
            session.commit()
            print(f"  Saved to database!")
            continue
        
        print(f"  ✗ All extraction methods failed for {plan_name}")
    
    session.close()
    print("\n" + "="*60)
    print("Processing complete!")

if __name__ == "__main__":
    main()