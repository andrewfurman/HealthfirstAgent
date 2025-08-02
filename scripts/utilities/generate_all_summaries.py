#!/usr/bin/env python3
"""
Script to generate compressed summaries for all plans with extracted document text.
Processes plans in batches to avoid timeouts.
"""
import sys
import time
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from plans.plans_model import Plan, Base
from plans.gpt_summary_generator import generate_summary_for_plan
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections before Neon's 5-minute timeout
    pool_pre_ping=True  # Enable connection health checks
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Database error: {str(e)}")
        raise
    finally:
        session.close()

def main():
    """Generate summaries for all plans with extracted document text."""
    with session_scope() as session:
        # Get all plans with extracted document text
        plans = session.query(Plan).filter(
            Plan.plan_document_full_text.isnot(None)
        ).all()
        
        print(f"Found {len(plans)} plans that need summaries")
        
        if not plans:
            # Check if any plans have document text at all
            plans_with_text = session.query(Plan).filter(
                Plan.plan_document_full_text.isnot(None)
            ).all()
            print(f"Total plans with extracted text: {len(plans_with_text)}")
            
            # Show which plans already have summaries
            plans_with_summaries = session.query(Plan).filter(
                Plan.compressed_summary.isnot(None)
            ).all()
            print(f"Plans with summaries: {len(plans_with_summaries)}")
            for plan in plans_with_summaries:
                print(f"  - {plan.short_name}")
            return
        
        successful = 0
        failed = 0
        
        for i, plan in enumerate(plans, 1):
            print(f"\n[{i}/{len(plans)}] Processing {plan.short_name} (ID: {plan.id})...")
            
            try:
                success, message = generate_summary_for_plan(plan.id, session)
                
                if success:
                    successful += 1
                    print(f"  ✓ {message}")
                    # Commit after each successful generation
                    session.commit()
                else:
                    failed += 1
                    print(f"  ✗ {message}")
                
                # Small delay to avoid rate limiting
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Progress has been saved.")
                print(f"Processed {i-1} plans: {successful} successful, {failed} failed")
                break
            except Exception as e:
                failed += 1
                print(f"  ✗ Unexpected error: {str(e)}")
        
        print(f"\n\nSummary generation complete!")
        print(f"Total processed: {successful + failed}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

if __name__ == "__main__":
    main()