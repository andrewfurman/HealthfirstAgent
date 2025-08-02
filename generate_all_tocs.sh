#!/bin/bash
# Script to generate table of contents for all plans with document text

echo "Generating table of contents for all plans..."
echo "Adding 10-second delay between requests to avoid API rate limits"

# Get all plan IDs that have document text (we know these from earlier)
PLAN_IDS=(1 2 3 4 5 6 8 9 10 11 14 15 17 19 20 21 23 24 25 26 27)

for plan_id in "${PLAN_IDS[@]}"; do
    echo ""
    echo "Processing plan ID: $plan_id"
    curl -X POST http://127.0.0.1:8080/plans/api/generate-toc/$plan_id -H "Content-Type: application/json"
    echo ""
    echo "Waiting 10 seconds before next request..."
    sleep 10
done

echo ""
echo "Table of contents generation complete!"