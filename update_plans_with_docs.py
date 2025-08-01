import requests
import json

# Updates and new plans from additional_plans.md
plans_to_update = [
    # Update existing plans with new documentation URLs
    {
        "id": "completecare-dsnp",
        "short_name": "CompleteCare D-SNP",
        "full_name": "Healthfirst CompleteCare (HMO D-SNP)",
        "summary_of_benefits": "$0 deductible and OOPM. $0 copays for all services. $280 OTC/month, meals, dental/vision/hearing. RN team handles all LTC authorization.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_pnVHJRXSPhoO/2025-completecare-plan-summary-of-benefits-english",
        "compressed_summary": "Dual Special Needs Plan for Medicare/Medicaid. $280 monthly OTC benefit, comprehensive coverage."
    },
    
    # Split D-SNPs into separate plans
    {
        "id": "life-improvement-plan",
        "short_name": "LIP",
        "full_name": "Healthfirst Life Improvement Plan (HMO D-SNP)",
        "summary_of_benefits": "$0 deductible and OOPM. $0 copays for all services. OTC $575 quarterly, dental/vision/hearing, 28 rides. Medicaid pays cost-share.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_4wfk6FGlW6Fh/2025-life-improvement-plan-summary-of-benefits-english",
        "compressed_summary": "Dual Special Needs Plan with highest OTC benefit ($575 quarterly), comprehensive coverage."
    },
    {
        "id": "connection-plan",
        "short_name": "CNX",
        "full_name": "Healthfirst Connection Plan (HMO D-SNP)",
        "summary_of_benefits": "$0 deductible and OOPM. $0 copays for all services. OTC $170 quarterly, dental/vision/hearing, 28 rides. Medicaid pays cost-share.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_K3tpLSAMqCnR/2025-connection-plan-summary-of-benefits-english",
        "compressed_summary": "Dual Special Needs Plan with standard OTC benefit ($170 quarterly), comprehensive coverage."
    },
    
    # Update existing Medicare Advantage plans with new URLs
    {
        "id": "increased-benefits-plan",
        "short_name": "IBP",
        "full_name": "Healthfirst Increased Benefits Plan (HMO)",
        "summary_of_benefits": "$0 deductible, $9,350 OOPM. $0 PCP / $20 specialist copays. $440×5 inpatient / $110 ER copays. OTC $110 quarterly, 40 rides.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_CGLSun3nxred/2025-increased-benefits-plan-summary-of-benefits-english",
        "compressed_summary": "Medicare Advantage with $110 quarterly OTC, 40 rides annually, low copays."
    },
    {
        "id": "65-plus-hmo",
        "short_name": "65+",
        "full_name": "Healthfirst 65 Plus Plan (HMO)",
        "summary_of_benefits": "$0 deductible, $9,350 OOPM. $0 PCP / $25 specialist copays. $460×5 inpatient / $110 ER copays. OTC or rides, dental/vision/hearing.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_8hMkAKJ47jiD/2025-65-plus-plan-summary-of-benefits-english",
        "compressed_summary": "Medicare Advantage HMO with choice of OTC benefit or transportation, comprehensive coverage."
    },
    
    # Update Signature plans with new URLs
    {
        "id": "signature-hmo",
        "short_name": "Signature HMO",
        "full_name": "Healthfirst Signature (HMO)",
        "summary_of_benefits": "$0 deductible, $6,700 OOPM. $0 PCP / $30 specialist copays. $430×5 inpatient / $125 ER copays. Fitness, dental/vision/hearing.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_pSh5lZgSJKCE/2025-signature-hmo-summary-of-benefits-english",
        "compressed_summary": "Premium Medicare Advantage HMO with fitness benefit, lower out-of-pocket maximum."
    },
    {
        "id": "signature-ppo",
        "short_name": "Signature PPO",
        "full_name": "Healthfirst Signature (PPO)",
        "summary_of_benefits": "$0 deductible, $5k in-network / $8k combined OOPM. $0 PCP / $35 specialist copays. $325×5 inpatient / $125 ER copays. $725 Flex, fitness.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_oziqcD6zXBQF/2025-signature-ppo-summary-of-benefits-english",
        "compressed_summary": "Medicare Advantage PPO with $725 Flex benefit, out-of-network coverage available."
    },
    
    # Update Essential Plan with state URL
    {
        "id": "essential-plan-1",
        "short_name": "EP",
        "full_name": "Essential Plan Tier 1 (151-200% FPL)",
        "summary_of_benefits": "$0 premium, $0 deductible, $360 OOPM. $15 PCP / $25 specialist copays. $150 inpatient / $75 ER copays.",
        "summary_of_benefits_url": "https://info.nystateofhealth.ny.gov/sites/default/files/Essential%20Plan%20Benefits%20and%20Cost%20Sharing.pdf",
        "compressed_summary": "For income 151-200% FPL. Low copays, $360 annual out-of-pocket maximum."
    },
    
    # Update Child Health Plus with state URL
    {
        "id": "child-health-plus",
        "short_name": "CHP",
        "full_name": "Healthfirst Child Health Plus",
        "summary_of_benefits": "No deductible, no out-of-pocket max. $0 copays for all services. Includes orthodontics & glasses $0. No PA for dental/vision.",
        "summary_of_benefits_url": "https://info.nystateofhealth.ny.gov/sites/default/files/Child%20Health%20Plus%20At%20A%20Glance%20Card%20-%20English_3.pdf",
        "compressed_summary": "Free or low-cost health insurance for uninsured children under 19. Covers medical, dental, vision, and prescription drugs."
    },
    
    # Update Leaf Platinum with specific URL
    {
        "id": "leaf-platinum",
        "short_name": "Platinum",
        "full_name": "Healthfirst Leaf Platinum",
        "summary_of_benefits": "$0 deductible, $4k OOPM. $15 PCP / $30 specialist copays. $500 inpatient / $150 ER copays. Adult dental/vision in Premier.",
        "summary_of_benefits_url": "https://assets.healthfirst.org/pdf_dsF5didylWP2/2025-platinum-leaf-plan-summary-of-benefits-english",
        "compressed_summary": "Highest tier marketplace plan with lowest out-of-pocket costs, Premier includes dental/vision."
    },
    
    # Update Pro EPO Gold with available URL
    {
        "id": "pro-epo-gold",
        "short_name": "Pro EPO Gold",
        "full_name": "Healthfirst Pro EPO Gold",
        "summary_of_benefits": "$1,350 deductible, $7k OOPM. $25 PCP / $50 specialist copays. $500 inpatient / $350 ER copays. 80% actuarial value.",
        "summary_of_benefits_url": "https://healthpass.com/wp-content/uploads/2022/03/healthfirst-gold-pro-epo.pdf",
        "compressed_summary": "Small group EPO plan with 80% actuarial value, moderate cost-sharing."
    },
    
    # Add new HFIC Small Group EPO plan
    {
        "id": "hfic-small-group-epo",
        "short_name": "HFIC",
        "full_name": "HFIC Small Group EPO",
        "summary_of_benefits": "Small group employer plan with various metal tiers. Product sunsets in 2025.",
        "summary_of_benefits_url": "https://healthpass.com/wp-content/uploads/2022/03/healthfirst-gold-pro-epo.pdf",
        "compressed_summary": "Small group employer EPO plans (Gold, Silver, Bronze) - product ending in 2025."
    }
]

# Delete the test plan first
delete_url = "http://127.0.0.1:8080/plans/1/delete"
try:
    response = requests.delete(delete_url)
    if response.status_code == 200:
        print("Test plan deleted successfully")
    else:
        print(f"Could not delete test plan: {response.status_code}")
except Exception as e:
    print(f"Error deleting test plan: {e}")

# API endpoint URL for bulk create/update
api_url = "http://127.0.0.1:8080/plans/bulk-create"

# Prepare the payload
payload = {
    "plans": plans_to_update
}

# Make the API request
try:
    response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nSuccess! {result['message']}")
        print(f"Created: {result['created']} plans")
        print(f"Updated: {result['updated']} plans")
        
        # List all plans to verify
        list_response = requests.get("http://127.0.0.1:8080/plans/api/list")
        if list_response.status_code == 200:
            plans = list_response.json()["plans"]
            print(f"\nTotal plans in database: {len(plans)}")
            print("\nPlans by category:")
            
            # Categorize plans
            medicaid = [p for p in plans if 'medicaid' in p['id'] or 'child-health' in p['id'] or 'harp' in p['id']]
            essential = [p for p in plans if 'essential-plan' in p['id']]
            medicare = [p for p in plans if any(x in p['id'] for x in ['65-plus', 'signature', 'dsnp', 'completecare', 'life-improvement', 'connection', 'increased-benefits'])]
            marketplace = [p for p in plans if 'leaf' in p['id']]
            commercial = [p for p in plans if 'pro-epo' in p['id'] or 'hfic' in p['id']]
            ltc = [p for p in plans if 'senior-health' in p['id'] or 'mltc' in p['id']]
            other = [p for p in plans if p['id'] == 'ib-dual']
            
            print(f"- Medicaid: {len(medicaid)} plans")
            print(f"- Essential Plan: {len(essential)} plans")
            print(f"- Medicare Advantage: {len(medicare)} plans")
            print(f"- Marketplace (Leaf): {len(marketplace)} plans")
            print(f"- Commercial/Small Group: {len(commercial)} plans")
            print(f"- Long Term Care: {len(ltc)} plans")
            print(f"- Other: {len(other)} plans")
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the Flask server. Make sure it's running on http://127.0.0.1:8080")
except Exception as e:
    print(f"Error: {str(e)}")