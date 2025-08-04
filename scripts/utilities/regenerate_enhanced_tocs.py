"""
Regenerate table of contents for all plans with enhanced copay/deductible/PA detection.
This script uses the updated toc_generator.py with call center-focused annotations.
Includes 5-second delays between API calls to avoid rate limits.
"""
import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from plans.plans_model import Plan
from plans.toc_generator import gpt_generate_toc_for_plan
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def regenerate_all_tocs():
    """Regenerate table of contents for all plans with the enhanced prompt."""
    # Set up database connection
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        return
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all plans that have document text
        plans = session.query(Plan).filter(Plan.plan_document_full_text.isnot(None)).all()
        
        print(f"Found {len(plans)} plans with document text")
        print("Regenerating table of contents with enhanced copay/deductible/PA detection...")
        print("-" * 80)
        
        success_count = 0
        error_count = 0
        
        for i, plan in enumerate(plans, 1):
            print(f"Processing {i}/{len(plans)}: {plan.short_name} (ID: {plan.id})")
            
            try:
                success, message = gpt_generate_toc_for_plan(plan.id, session)
                
                if success:
                    print(f"✅ SUCCESS: {message}")
                    success_count += 1
                    # Commit after each successful update
                    session.commit()
                else:
                    print(f"❌ ERROR: {message}")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")
                error_count += 1
                session.rollback()  # Rollback on error
            
            # Add 5-second delay between API calls to avoid rate limits
            if i < len(plans):  # Don't delay after the last plan
                print(f"⏳ Waiting 5 seconds before next API call... ({i}/{len(plans)} completed)")
                time.sleep(5)
            
            print("-" * 40)
        
        print(f"\nSUMMARY:")
        print(f"✅ Successfully updated: {success_count} plans")
        print(f"❌ Errors: {error_count} plans")
        print(f"📊 Total plans processed: {len(plans)}")
        
        if success_count > 0:
            print(f"\n🎉 Enhanced table of contents with copay/deductible/PA annotations generated!")
            print("Call center agents can now easily find pages for:")
            print("  - Copay information")
            print("  - Coinsurance rates") 
            print("  - Deductible amounts")
            print("  - Prior authorization requirements")
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    print("🔄 Enhanced Table of Contents Regenerator")
    print("This will update all plan TOCs with call center annotations")
    print("=" * 60)
    
    response = input("Do you want to proceed? (y/n): ")
    if response.lower() in ['y', 'yes']:
        regenerate_all_tocs()
    else:
        print("Operation cancelled.")