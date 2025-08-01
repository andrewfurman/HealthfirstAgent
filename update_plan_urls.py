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

# Plan URL updates mapping
plan_updates = {
    # Essential Plans
    'essential-plan-2': {
        'url': 'https://assets.healthfirst.org/pdf_nyCjuV2DbvuB/2025-essential-plan-2-summary-of-benefits-english', 
        'name': 'Essential Plan 2'
    },
    'essential-plan-3': {
        'url': 'https://assets.healthfirst.org/pdf_p8CIZ0t0wHtK/2025-essential-plan-3-summary-of-benefits-english',
        'name': 'Essential Plan 3'
    },
    'essential-plan-4': {
        'url': 'https://assets.healthfirst.org/pdf_f6sp9sVj26m0/2025-essential-plan-4-summary-of-benefits-english',
        'name': 'Essential Plan 4'
    },
    
    # Leaf Plans  
    'leaf-gold': {
        'url': 'https://assets.healthfirst.org/pdf_obBvPwIKJfV6/2025-gold-leaf-plan-summary-of-benefits-english',
        'name': 'Gold'
    },
    
    'leaf-silver': {
        'url': 'https://assets.healthfirst.org/pdf_fLBJCyMkeqwa/2025-silver-leaf-plan-over-400-fpl-summary-of-benefits-english',
        'name': 'Silver'
    },
    
    'leaf-bronze': {
        'url': 'https://assets.healthfirst.org/pdf_XvuNQ5nmKKlB/2025-bronze-leaf-plan-summary-of-benefits-english',
        'name': 'Bronze'
    },
    
    'leaf-platinum': {
        'url': 'https://assets.healthfirst.org/pdf_dsF5didylWP2/2025-platinum-leaf-plan-summary-of-benefits-english',
        'name': 'Platinum'
    }
}

# Additional plan if needed
# Note: Connection Plan already has the right URL

def update_plan_urls():
    from plans.plans_model import Plan
    
    with session_scope() as session:
        for plan_id, update_info in plan_updates.items():
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if plan:
                old_url = plan.summary_of_benefits_url
                plan.summary_of_benefits_url = update_info['url']
                # All these URLs are PDFs
                plan.document_type = 'pdf'
                print(f"Updated {update_info['name']}:")
                print(f"  Old URL: {old_url}")
                print(f"  New URL: {update_info['url']}")
                print(f"  Document type: pdf")
            else:
                print(f"Plan {plan_id} not found")
        
        print("\nAll plan URLs updated successfully!")

if __name__ == "__main__":
    update_plan_urls()