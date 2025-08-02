#!/bin/bash
# Script to regenerate summaries for plans with placeholder text

echo "Regenerating summaries for plans with placeholder text..."
echo "Adding 10-second delay between requests to avoid API rate limits"

# Plans that need summary updates: 14, 15, 17, 19, 20, 21, 23, 24, 25, 26, 27
PLAN_IDS=(14 15 17 19 20 21 23 24 25 26 27)

for plan_id in "${PLAN_IDS[@]}"; do
    echo ""
    echo "Processing plan ID: $plan_id"
    curl -X POST http://127.0.0.1:8080/plans/api/generate-summary/$plan_id -H "Content-Type: application/json"
    echo ""
    echo "Waiting 10 seconds before next request..."
    sleep 10
done

echo ""
echo "Summary regeneration complete!"