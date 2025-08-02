#!/usr/bin/env python3
"""
Alternative PDF extraction using different methods
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plans.plans_model import Plan

# Try multiple PDF libraries
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("PyMuPDF not installed")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

load_dotenv()

def extract_with_pymupdf(pdf_path):
    """Extract using PyMuPDF (fitz)"""
    if not HAS_PYMUPDF:
        return None
    
    try:
        import fitz
        text = ""
        doc = fitz.open(pdf_path)
        print(f"  PyMuPDF: Found {len(doc)} pages")
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        doc.close()
        return text if text.strip() else None
    except Exception as e:
        print(f"  PyMuPDF failed: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_alternative.py <pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    print(f"Attempting to extract: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")
    
    # Try PyMuPDF first (most reliable)
    if HAS_PYMUPDF:
        text = extract_with_pymupdf(pdf_path)
        if text and len(text) > 100:
            print(f"✓ Successfully extracted {len(text)} characters with PyMuPDF")
            
            # Ask if user wants to save to database
            plan_name = input("Enter plan short name to save to database (or press Enter to skip): ").strip()
            if plan_name:
                database_url = os.environ.get('DATABASE_URL')
                if database_url:
                    engine = create_engine(database_url)
                    Session = sessionmaker(bind=engine)
                    session = Session()
                    
                    plan = session.query(Plan).filter_by(short_name=plan_name).first()
                    if plan:
                        plan.plan_document_full_text = text
                        session.commit()
                        print(f"Saved to database for plan: {plan_name}")
                    else:
                        print(f"Plan '{plan_name}' not found in database")
                    
                    session.close()
            
            # Save to file
            output_file = pdf_path.replace('.pdf', '_extracted.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Text saved to: {output_file}")
            return
    
    print("Failed to extract text from PDF")

if __name__ == "__main__":
    main()