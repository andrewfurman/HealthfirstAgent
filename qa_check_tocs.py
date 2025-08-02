#!/usr/bin/env python3
"""
QA script to check all Tables of Contents for page numbers
"""
import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plans.plans_model import Plan

# Load environment variables
load_dotenv()

def check_toc_for_page_numbers(toc_text):
    """
    Check if a TOC contains page numbers
    Returns: (has_numbers, count, sample_lines)
    """
    if not toc_text:
        return False, 0, []
    
    lines = toc_text.split('\n')
    # Look for numbers at the end of lines (with possible whitespace)
    # This matches patterns like "Section 2", "Section Name 42", etc.
    page_number_pattern = r'\s+\d+\s*$'  # Space followed by numbers at end of line
    
    lines_with_numbers = []
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Check if line ends with a number (after some text and a space)
        if re.search(page_number_pattern, line.strip()):
            lines_with_numbers.append(line.strip())
    
    return len(lines_with_numbers) > 0, len(lines_with_numbers), lines_with_numbers[:3]

def main():
    # Connect to database
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all plans
        plans = session.query(Plan).order_by(Plan.id).all()
        
        print("=" * 80)
        print("TABLE OF CONTENTS QA REPORT")
        print("=" * 80)
        print(f"Total plans in database: {len(plans)}")
        print()
        
        # Track statistics
        stats = {
            'has_toc': 0,
            'no_toc': 0,
            'has_page_numbers': 0,
            'no_page_numbers': 0,
            'empty_toc': 0
        }
        
        plans_without_numbers = []
        plans_without_toc = []
        
        # Check each plan
        for plan in plans:
            print(f"\n{'-' * 60}")
            print(f"Plan ID: {plan.id} | Name: {plan.short_name}")
            print(f"Document Type: {plan.document_type or 'Not specified'}")
            
            if not plan.table_of_contents:
                print("❌ NO TABLE OF CONTENTS")
                stats['no_toc'] += 1
                plans_without_toc.append((plan.id, plan.short_name))
            elif plan.table_of_contents.strip() == '':
                print("⚠️  EMPTY TABLE OF CONTENTS")
                stats['empty_toc'] += 1
                plans_without_toc.append((plan.id, plan.short_name))
            else:
                stats['has_toc'] += 1
                has_numbers, count, samples = check_toc_for_page_numbers(plan.table_of_contents)
                
                if has_numbers:
                    print(f"✅ HAS PAGE NUMBERS ({count} lines with numbers)")
                    stats['has_page_numbers'] += 1
                    if samples:
                        print("   Sample lines with page numbers:")
                        for sample in samples:
                            print(f"   - {sample[:80]}...")
                else:
                    print("❌ NO PAGE NUMBERS FOUND")
                    stats['no_page_numbers'] += 1
                    plans_without_numbers.append((plan.id, plan.short_name))
                    
                # Show first few lines of TOC for context
                toc_lines = plan.table_of_contents.split('\n')[:5]
                print("   First few lines of TOC:")
                for line in toc_lines:
                    if line.strip():
                        print(f"   {line[:80]}...")
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        print(f"Total Plans: {len(plans)}")
        print(f"Plans with TOC: {stats['has_toc']}")
        print(f"Plans without TOC: {stats['no_toc']}")
        print(f"Plans with empty TOC: {stats['empty_toc']}")
        print()
        print(f"Of plans with TOC:")
        print(f"  - With page numbers: {stats['has_page_numbers']}")
        print(f"  - Without page numbers: {stats['no_page_numbers']}")
        
        # List problematic plans
        if plans_without_toc:
            print("\n" + "=" * 80)
            print("PLANS NEEDING TOC GENERATION:")
            print("=" * 80)
            for plan_id, plan_name in plans_without_toc:
                print(f"  - ID {plan_id}: {plan_name}")
        
        if plans_without_numbers:
            print("\n" + "=" * 80)
            print("PLANS WITH TOC BUT NO PAGE NUMBERS:")
            print("=" * 80)
            for plan_id, plan_name in plans_without_numbers:
                print(f"  - ID {plan_id}: {plan_name}")
        
        # Calculate success rate
        if stats['has_toc'] > 0:
            success_rate = (stats['has_page_numbers'] / stats['has_toc']) * 100
            print("\n" + "=" * 80)
            print(f"SUCCESS RATE: {success_rate:.1f}% of TOCs have page numbers")
            print("=" * 80)
        
    finally:
        session.close()
        print("\nQA check complete!")

if __name__ == "__main__":
    main()