import requests
import json

# Healthfirst benefit plans data based on benefits_research.md
healthfirst_plans = [
    {
        "id": "medicaid-managed-care",
        "short_name": "Medicaid Managed Care",
        "full_name": "Healthfirst Medicaid Managed Care (includes HARP)",
        "summary_of_benefits": "Full benefit list, behavioral-health coverage, copay rules, provider directory. Includes integrated Medicare-Medicaid rules for dual-eligible MMC members.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_s4dEdrCfKrFE/2025-medicaid-managed-care-member-handbook-english",
        "compressed_summary": "Comprehensive Medicaid coverage including medical, behavioral health, and pharmacy benefits. No copays for most services."
    },
    {
        "id": "medicaid-harp",
        "short_name": "HARP",
        "full_name": "Health and Recovery Plan (HARP)",
        "summary_of_benefits": "Specialized behavioral health services, personal wellness plan, community support benefits. Part of Medicaid Managed Care.",
        "summary_of_benefits_url": "https://healthfirst.org/personal-wellness-plan",
        "compressed_summary": "Enhanced behavioral health coverage for adults with serious mental illness and/or substance use disorders."
    },
    {
        "id": "senior-health-partners",
        "short_name": "MLTC",
        "full_name": "Senior Health Partners Managed Long Term Care (MLTC)",
        "summary_of_benefits": "Long-term care benefits, care-team model, covered/non-covered services for seniors needing long-term care.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_SGMiY8LAUdLp/2025-senior-health-partners-member-handbook-english",
        "compressed_summary": "Managed long-term care services including home care, adult day care, and nursing home care for eligible seniors."
    },
    {
        "id": "ib-dual",
        "short_name": "IB-Dual",
        "full_name": "Integrated Benefits for Dually Eligible Enrollees",
        "summary_of_benefits": "Integrated Medicare-Medicaid coverage for dual-eligible members. Coordinates benefits between both programs.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_cHzS5FJMiUlL/2025-medicaid-managed-care-handbook-addendum-english",
        "compressed_summary": "Combined Medicare and Medicaid benefits for dual-eligible members with coordinated care management."
    }
]

# API endpoint URL
api_url = "http://127.0.0.1:8080/plans/bulk-create"

# Prepare the payload
payload = {
    "plans": healthfirst_plans
}

# Make the API request
try:
    response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! {result['message']}")
        print(f"Created: {result['created']} plans")
        print(f"Updated: {result['updated']} plans")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the Flask server. Make sure it's running on http://127.0.0.1:8080")
except Exception as e:
    print(f"Error: {str(e)}")