# Utility Scripts Documentation

## PDF Extraction Scripts

### `extract_pdf_alternative.py`
Alternative PDF extraction using PyMuPDF when standard tools fail.
```bash
python extract_pdf_alternative.py path/to/file.pdf
```

### `extract_and_save_pdfs.py`
Batch extraction and database saving for multiple PDFs.

### `fix_remaining_plans.py`
Downloads and extracts the final 4 problematic plans using correct URLs.

## Generation Scripts

### `regenerate_summaries.sh`
Regenerates GPT-4.1 summaries for all plans with 10-second delays to avoid rate limits.

### `regenerate_all_tocs.sh`
Regenerates table of contents for all plans, focusing on page number extraction.

## QA Scripts

### `qa_check_tocs.py`
Quality assurance script that verifies:
- Which plans have TOCs
- Which TOCs contain page numbers
- Success rate statistics
- Lists problematic plans

## Update Scripts

### `update_leaf_bronze.py`
Manually updates Leaf Bronze plan with full Summary of Benefits text.

## Usage Notes

1. Always activate virtual environment first:
   ```bash
   source venv/bin/activate
   ```

2. Ensure DATABASE_URL is set in .env file

3. Run scripts with appropriate delays to avoid API rate limits

4. Check logs for extraction errors - common issues:
   - Corrupted PDFs (missing /Root object)
   - Protected/encrypted PDFs
   - Non-standard encoding

5. PyMuPDF (`fitz`) is most reliable for Healthfirst PDFs
