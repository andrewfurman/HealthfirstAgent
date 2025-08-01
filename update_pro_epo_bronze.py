from contextlib import contextmanager
from main import app, Session

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    with app.app_context():
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

def update_pro_epo_bronze_url():
    from plans.plans_model import Plan
    
    with session_scope() as session:
        # Find Pro EPO Bronze plan
        bronze_plan = session.query(Plan).filter(Plan.id == 'pro-epo-bronze').first()
        
        if bronze_plan:
            old_url = bronze_plan.summary_of_benefits_url
            # Using the standard Bronze 8225 Pro EPO document
            bronze_plan.summary_of_benefits_url = 'https://healthpass.com/wp-content/uploads/2022/03/healthfirst-bronze-8225-pro-2022.pdf'
            bronze_plan.document_type = 'pdf'
            
            print(f"Updated Pro EPO Bronze plan:")
            print(f"  Old URL: {old_url}")
            print(f"  New URL: {bronze_plan.summary_of_benefits_url}")
            print(f"  Document type: pdf")
        else:
            print("Pro EPO Bronze plan not found")
        
        print("\nPro EPO Bronze plan URL updated successfully!")

if __name__ == "__main__":
    update_pro_epo_bronze_url()