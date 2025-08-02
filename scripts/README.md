# Utility Scripts

This directory contains various utility and migration scripts used during development.

## Directory Structure

### `/migrations`
Database migration scripts used to update schema and data:
- `migrate_to_numeric_ids.py` - Converted plan IDs from strings to numeric primary keys
- `update_plan_types.py` - Added plan type categorization 
- `update_plan_urls.py` - Updated plan document URLs
- `update_plans_with_docs.py` - Bulk update of plan documents

### `/utilities`
General utility scripts for data management:
- `add_all_healthfirst_plans.py` - Initial bulk import of all plans
- `add_healthfirst_plans.py` - Add individual plans
- `delete_test_plan.py` - Remove test data
- `generate_all_summaries.py` - Generate AI summaries for all plans
- `update_harp_url.py` - Update HARP plan document URL
- `update_pro_epo_bronze.py` - Update Pro EPO Bronze plan
- `update_leaf_bronze.py` - Update Leaf Bronze plan details
- `extract_and_save_pdfs.py` - Extract text from PDF documents
- `extract_pdf_alternative.py` - Alternative PDF extraction method
- `fix_problem_pdfs.py` - Handle problematic PDF files
- `qa_check_tocs.py` - Quality check table of contents generation

## Usage

These scripts are primarily for one-time use during development and data setup.
They should not be needed for normal application operation.

To run a script:
```bash
source venv/bin/activate
python scripts/utilities/script_name.py
```