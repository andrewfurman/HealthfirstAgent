
from flask import Blueprint, render_template, request, jsonify
from contextlib import contextmanager
from sqlalchemy.orm import Session
from plans.document_extractor import update_plan_document_text
from plans.gpt_summary_generator import generate_summary_for_plan
from plans.toc_generator import gpt_generate_toc_for_plan

# Create Blueprint
plans_bp = Blueprint('plans', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/plans')

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    from main import Session
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

@plans_bp.route('/')
def show_plans():
    """Route to display the plans page"""
    from plans.plans_model import Plan
    with session_scope() as session:
        # Sort plans by plan_type alphabetically, then by short_name alphabetically
        plans = session.query(Plan).all()
        
        # Sort plans first by plan_type alphabetically (None values last), then by short_name alphabetically
        plans.sort(key=lambda p: (
            p.plan_type.lower() if p.plan_type else 'zzz',  # None values sort last
            p.short_name.lower() if p.short_name else ''
        ))
        
        return render_template('plans.html', plans=plans)

@plans_bp.route('/<int:plan_id>')
def view_plan(plan_id):
    """Route to display a single plan's details"""
    from plans.plans_model import Plan
    with session_scope() as session:
        plan = session.query(Plan).filter(Plan.id == plan_id).first()
        return render_template('view_plan.html', plan=plan)

@plans_bp.route('/<int:plan_id>/update', methods=['POST'])
def update_plan(plan_id):
    """Route to update a plan's details"""
    from plans.plans_model import Plan
    with session_scope() as session:
        try:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return jsonify({'error': 'Plan not found'}), 404

            data = request.json
            plan.short_name = data.get('short_name', plan.short_name)
            plan.full_name = data.get('full_name', plan.full_name)
            plan.summary_of_benefits = data.get('summary_of_benefits', plan.summary_of_benefits)
            plan.summary_of_benefits_url = data.get('summary_of_benefits_url', plan.summary_of_benefits_url)
            plan.compressed_summary = data.get('compressed_summary', plan.compressed_summary)
            plan.plan_type = data.get('plan_type', plan.plan_type)
            plan.plan_document_full_text = data.get('plan_document_full_text', plan.plan_document_full_text)
            plan.summary_of_benefit_coverage = data.get('summary_of_benefit_coverage', plan.summary_of_benefit_coverage)
            plan.table_of_contents = data.get('table_of_contents', plan.table_of_contents)
            plan.document_type = data.get('document_type', plan.document_type)

            return jsonify({'message': 'Plan updated successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@plans_bp.route('/bulk-create', methods=['POST'])
def bulk_create_plans():
    """Route to create multiple plans at once"""
    from plans.plans_model import Plan
    with session_scope() as session:
        try:
            data = request.json
            plans = data.get('plans', [])
            
            created_count = 0
            updated_count = 0
            
            for plan_data in plans:
                # Check if plan already exists by old_id
                existing_plan = session.query(Plan).filter(Plan.old_id == plan_data.get('id', plan_data.get('old_id'))).first()
                
                if existing_plan:
                    # Update existing plan
                    existing_plan.short_name = plan_data.get('short_name', existing_plan.short_name)
                    existing_plan.full_name = plan_data.get('full_name', existing_plan.full_name)
                    existing_plan.summary_of_benefits = plan_data.get('summary_of_benefits', existing_plan.summary_of_benefits)
                    existing_plan.summary_of_benefits_url = plan_data.get('summary_of_benefits_url', existing_plan.summary_of_benefits_url)
                    existing_plan.compressed_summary = plan_data.get('compressed_summary', existing_plan.compressed_summary)
                    existing_plan.plan_type = plan_data.get('plan_type', existing_plan.plan_type)
                    existing_plan.plan_document_full_text = plan_data.get('plan_document_full_text', existing_plan.plan_document_full_text)
                    existing_plan.summary_of_benefit_coverage = plan_data.get('summary_of_benefit_coverage', existing_plan.summary_of_benefit_coverage)
                    existing_plan.table_of_contents = plan_data.get('table_of_contents', existing_plan.table_of_contents)
                    existing_plan.document_type = plan_data.get('document_type', existing_plan.document_type)
                    updated_count += 1
                else:
                    # Create new plan
                    new_plan = Plan(
                        old_id=plan_data.get('id', plan_data.get('old_id')),
                        short_name=plan_data['short_name'],
                        full_name=plan_data['full_name'],
                        summary_of_benefits=plan_data.get('summary_of_benefits', ''),
                        summary_of_benefits_url=plan_data.get('summary_of_benefits_url', ''),
                        compressed_summary=plan_data.get('compressed_summary', ''),
                        plan_type=plan_data.get('plan_type', ''),
                        plan_document_full_text=plan_data.get('plan_document_full_text', ''),
                        summary_of_benefit_coverage=plan_data.get('summary_of_benefit_coverage', ''),
                        table_of_contents=plan_data.get('table_of_contents', ''),
                        document_type=plan_data.get('document_type')
                    )
                    session.add(new_plan)
                    created_count += 1
            
            return jsonify({
                'message': f'Successfully processed {len(plans)} plans',
                'created': created_count,
                'updated': updated_count
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@plans_bp.route('/api/list', methods=['GET'])
def api_list_plans():
    """API endpoint to list all plans"""
    from plans.plans_model import Plan
    with session_scope() as session:
        try:
            plans = session.query(Plan).all()
            plans_data = []
            for plan in plans:
                plans_data.append({
                    'id': plan.id,
                    'short_name': plan.short_name,
                    'full_name': plan.full_name,
                    'summary_of_benefits': plan.summary_of_benefits,
                    'summary_of_benefits_url': plan.summary_of_benefits_url,
                    'compressed_summary': plan.compressed_summary,
                    'plan_type': plan.plan_type,
                    'plan_document_full_text': plan.plan_document_full_text,
                    'summary_of_benefit_coverage': plan.summary_of_benefit_coverage,
                    'table_of_contents': plan.table_of_contents,
                    'document_type': plan.document_type
                })
            return jsonify({'plans': plans_data}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@plans_bp.route('/<int:plan_id>/delete', methods=['DELETE'])
def delete_plan(plan_id):
    """Route to delete a plan"""
    from plans.plans_model import Plan
    with session_scope() as session:
        try:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return jsonify({'error': 'Plan not found'}), 404
            
            session.delete(plan)
            return jsonify({'message': f'Plan {plan_id} deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@plans_bp.route('/api/extract-document/<int:plan_id>', methods=['POST'])
def extract_single_plan_document(plan_id):
    """Extract document text for a specific plan"""
    with session_scope() as session:
        try:
            success, message = update_plan_document_text(plan_id, session)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500

@plans_bp.route('/api/extract-all-documents', methods=['POST'])
def extract_all_plan_documents():
    """Extract document text for all plans that have URLs"""
    from plans.plans_model import Plan
    
    with session_scope() as session:
        try:
            # Get all plans with URLs
            plans = session.query(Plan).filter(Plan.summary_of_benefits_url.isnot(None)).all()
            
            results = {
                'total_plans': len(plans),
                'successful': 0,
                'failed': 0,
                'results': []
            }
            
            for plan in plans:
                success, message = update_plan_document_text(plan.id, session)
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                results['results'].append({
                    'plan_id': plan.id,
                    'plan_name': plan.short_name,
                    'success': success,
                    'message': message
                })
            
            return jsonify(results), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500

@plans_bp.route('/api/generate-summary/<int:plan_id>', methods=['POST'])
def generate_plan_summary(plan_id):
    """Generate compressed summary for a specific plan using GPT-4"""
    with session_scope() as session:
        try:
            success, message = generate_summary_for_plan(plan_id, session)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500

@plans_bp.route('/api/generate-all-summaries', methods=['POST'])
def generate_all_plan_summaries():
    """Generate compressed summaries for all plans that have extracted document text"""
    from plans.plans_model import Plan
    
    with session_scope() as session:
        try:
            # Get all plans with extracted document text
            plans = session.query(Plan).filter(Plan.plan_document_full_text.isnot(None)).all()
            
            results = {
                'total_plans': len(plans),
                'successful': 0,
                'failed': 0,
                'results': []
            }
            
            for plan in plans:
                print(f"Generating summary for {plan.short_name}...")
                success, message = generate_summary_for_plan(plan.id, session)
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                results['results'].append({
                    'plan_id': plan.id,
                    'plan_name': plan.short_name,
                    'success': success,
                    'message': message
                })
                
                # Commit after each successful generation to save progress
                if success:
                    session.commit()
            
            return jsonify(results), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500

@plans_bp.route('/api/generate-toc/<int:plan_id>', methods=['POST'])
def generate_plan_toc(plan_id):
    """Generate table of contents for a specific plan using GPT-4.1"""
    with session_scope() as session:
        try:
            success, message = gpt_generate_toc_for_plan(plan_id, session)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500

@plans_bp.route('/api/generate-all-tocs', methods=['POST'])
def generate_all_plan_tocs():
    """Generate table of contents for all plans that have extracted document text"""
    from plans.plans_model import Plan
    
    with session_scope() as session:
        try:
            # Get all plans with extracted document text
            plans = session.query(Plan).filter(Plan.plan_document_full_text.isnot(None)).all()
            
            results = {
                'total_plans': len(plans),
                'successful': 0,
                'failed': 0,
                'results': []
            }
            
            for plan in plans:
                print(f"Generating table of contents for {plan.short_name}...")
                success, message = generate_toc_for_plan(plan.id, session)
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                results['results'].append({
                    'plan_id': plan.id,
                    'plan_name': plan.short_name,
                    'success': success,
                    'message': message
                })
                
                # Commit after each successful generation to save progress
                if success:
                    session.commit()
            
            return jsonify(results), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }), 500
