#!/bin/bash
# Regenerate all TOCs with improved page number extraction

echo "Regenerating all Tables of Contents with improved page number extraction..."
echo "This will process all plans one by one with delays to avoid API limits."
echo ""

# First regenerate for plans that have no TOC
echo "Step 1: Generating TOCs for plans without any TOC..."
MISSING_TOC_IDS=(7 12 13 16 18 22)

for plan_id in "${MISSING_TOC_IDS[@]}"; do
    echo "Generating TOC for plan ID $plan_id..."
    curl -X POST http://127.0.0.1:8080/plans/api/generate-toc/$plan_id
    echo ""
    sleep 10
done

echo ""
echo "Step 2: Regenerating TOCs for plans without page numbers..."
# Plans with TOC but no page numbers
NO_PAGE_IDS=(2 6 8 9 10 14 15 17 20 23 25 26 27)

for plan_id in "${NO_PAGE_IDS[@]}"; do
    echo "Regenerating TOC for plan ID $plan_id..."
    curl -X POST http://127.0.0.1:8080/plans/api/generate-toc/$plan_id
    echo ""
    sleep 10
done

echo ""
echo "All TOCs regenerated. Please run qa_check_tocs.py to verify results."