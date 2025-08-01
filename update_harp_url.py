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

def update_harp_url():
    from plans.plans_model import Plan
    
    with session_scope() as session:
        # Find HARP plan
        harp_plan = session.query(Plan).filter(Plan.short_name == 'HARP').first()
        
        if harp_plan:
            old_url = harp_plan.summary_of_benefits_url
            harp_plan.summary_of_benefits_url = 'https://assets.healthfirst.org/pdf_d5a493f4e40315c97f24b5510fad49cd/2023-personal-wellness-plan-covered-services-english'
            harp_plan.document_type = 'pdf'
            
            print(f"Updated HARP plan:")
            print(f"  Old URL: {old_url}")
            print(f"  New URL: {harp_plan.summary_of_benefits_url}")
            print(f"  Document type: pdf")
        else:
            print("HARP plan not found")
        
        print("\nHARP plan URL updated successfully!")

if __name__ == "__main__":
    update_harp_url()