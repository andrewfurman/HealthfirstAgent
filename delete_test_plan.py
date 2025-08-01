import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plans.plans_model import Plan

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Find and delete the test plan
        test_plan = session.query(Plan).filter(Plan.id == '1').first()
        if test_plan:
            session.delete(test_plan)
            session.commit()
            print(f"Successfully deleted test plan: {test_plan.full_name}")
        else:
            print("Test plan with ID '1' not found")
            
        # List remaining plans
        remaining_plans = session.query(Plan).all()
        print(f"\nRemaining plans in database: {len(remaining_plans)}")
        for plan in remaining_plans:
            print(f"- {plan.id}: {plan.short_name}")
            
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()
else:
    print("DATABASE_URL not found in environment variables")