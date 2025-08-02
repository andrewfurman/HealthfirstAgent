import requests
import json

# Complete list of all Healthfirst plans from call_center_guide.md
all_healthfirst_plans = [
    # Medicaid Plans (already added medicaid-managed-care, adding the rest)
    {
        "id": "child-health-plus",
        "short_name": "Child Health Plus",
        "full_name": "Healthfirst Child Health Plus",
        "summary_of_benefits": "No deductible, no out-of-pocket max. $0 copays for all services. Includes orthodontics & glasses $0. No PA for dental/vision.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Free or low-cost health insurance for uninsured children under 19. Covers medical, dental, vision, and prescription drugs."
    },
    
    # Essential Plan Tiers
    {
        "id": "essential-plan-1",
        "short_name": "EP-1",
        "full_name": "Essential Plan Tier 1 (151-200% FPL)",
        "summary_of_benefits": "$0 premium, $0 deductible, $360 OOPM. $15 PCP / $25 specialist copays. $150 inpatient / $75 ER copays.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "For income 151-200% FPL. Low copays, $360 annual out-of-pocket maximum."
    },
    {
        "id": "essential-plan-2",
        "short_name": "EP-2",
        "full_name": "Essential Plan Tier 2 (139-150% FPL)",
        "summary_of_benefits": "$0 premium, $0 deductible, $200 OOPM. $0 copays for PCP/specialist, inpatient/ER.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "For income 139-150% FPL. No copays, $200 annual out-of-pocket maximum."
    },
    {
        "id": "essential-plan-3",
        "short_name": "EP-3",
        "full_name": "Essential Plan Tier 3 (≤138% FPL, certain immigrants)",
        "summary_of_benefits": "$0 premium, $0 deductible, $200 OOPM. $0 copays for PCP/specialist, inpatient/ER.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "For ≤138% FPL certain immigrants. No copays, $200 annual out-of-pocket maximum."
    },
    {
        "id": "essential-plan-4",
        "short_name": "EP-4",
        "full_name": "Essential Plan Tier 4 (<138% FPL)",
        "summary_of_benefits": "$0 premium, $0 deductible, $0 OOPM. $0 copays for all services.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "For income <138% FPL. No costs - everything covered at $0."
    },
    
    # Dual Eligible/Long Term Care Plans
    {
        "id": "completecare-dsnp",
        "short_name": "CompleteCare D-SNP",
        "full_name": "Healthfirst CompleteCare (HMO D-SNP)",
        "summary_of_benefits": "$0 deductible and OOPM. $0 copays for all services. $280 OTC/month, meals, dental/vision/hearing. RN team handles all LTC authorization.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Dual Special Needs Plan for Medicare/Medicaid. $280 monthly OTC benefit, comprehensive coverage."
    },
    
    # Medicare Advantage Plans
    {
        "id": "dsnp-lip-connection",
        "short_name": "D-SNPs (LIP/Connection)",
        "full_name": "Healthfirst Life Improvement Plan / Connection Plan (D-SNP)",
        "summary_of_benefits": "$0 deductible and OOPM. $0 copays for all services. OTC $575/170 quarterly, dental/vision/hearing, 28 rides. Medicaid pays cost-share.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Dual Special Needs Plans with OTC benefits up to $575 quarterly, transportation included."
    },
    {
        "id": "increased-benefits-plan",
        "short_name": "Increased Benefits",
        "full_name": "Healthfirst Increased Benefits Plan",
        "summary_of_benefits": "$0 deductible, $9,350 OOPM. $0 PCP / $20 specialist copays. $440×5 inpatient / $110 ER copays. OTC $110 quarterly, 40 rides.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Medicare Advantage with $110 quarterly OTC, 40 rides annually, low copays."
    },
    {
        "id": "65-plus-hmo",
        "short_name": "65 Plus HMO",
        "full_name": "Healthfirst 65 Plus Plan (HMO)",
        "summary_of_benefits": "$0 deductible, $9,350 OOPM. $0 PCP / $25 specialist copays. $460×5 inpatient / $110 ER copays. OTC or rides, dental/vision/hearing.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Medicare Advantage HMO with choice of OTC benefit or transportation, comprehensive coverage."
    },
    {
        "id": "signature-hmo",
        "short_name": "Signature HMO",
        "full_name": "Healthfirst Signature (HMO)",
        "summary_of_benefits": "$0 deductible, $6,700 OOPM. $0 PCP / $30 specialist copays. $430×5 inpatient / $125 ER copays. Fitness, dental/vision/hearing.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Premium Medicare Advantage HMO with fitness benefit, lower out-of-pocket maximum."
    },
    {
        "id": "signature-ppo",
        "short_name": "Signature PPO",
        "full_name": "Healthfirst Signature (PPO)",
        "summary_of_benefits": "$0 deductible, $5k in-network / $8k combined OOPM. $0 PCP / $35 specialist copays. $325×5 inpatient / $125 ER copays. $725 Flex, fitness.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Medicare Advantage PPO with $725 Flex benefit, out-of-network coverage available."
    },
    
    # Marketplace (Leaf) Plans
    {
        "id": "leaf-platinum",
        "short_name": "Platinum",
        "full_name": "Healthfirst Leaf Platinum",
        "summary_of_benefits": "$0 deductible, $4k OOPM. $15 PCP / $30 specialist copays. $500 inpatient / $150 ER copays. Adult dental/vision in Premier.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Highest tier marketplace plan with lowest out-of-pocket costs, Premier includes dental/vision."
    },
    {
        "id": "leaf-gold",
        "short_name": "Gold",
        "full_name": "Healthfirst Leaf Gold",
        "summary_of_benefits": "$600 deductible, $6k OOPM. $25 PCP / $50 specialist copays. $500 inpatient / $350 ER copays. Premier adds dental/vision.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Mid-high tier marketplace plan with moderate deductible and copays."
    },
    {
        "id": "leaf-silver",
        "short_name": "Silver",
        "full_name": "Healthfirst Leaf Silver",
        "summary_of_benefits": "$1,750 deductible, $9,100 OOPM. $30 PCP / $65 specialist copays. $1,500 inpatient / $500 ER copays. CSR variants available.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Standard marketplace plan with cost-sharing reduction variants for eligible members."
    },
    {
        "id": "leaf-bronze",
        "short_name": "Bronze",
        "full_name": "Healthfirst Leaf Bronze",
        "summary_of_benefits": "$5,900 deductible, $9,100 OOPM. $40 PCP / $80 specialist copays. $2,000 inpatient / $800 ER copays. Premier adds dental/vision.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Lower premium marketplace plan with higher deductible and out-of-pocket costs."
    },
    {
        "id": "leaf-catastrophic",
        "short_name": "Catastrophic",
        "full_name": "Healthfirst Leaf Catastrophic",
        "summary_of_benefits": "$9,200 deductible, $9,200 OOPM. 3 PCP visits $0, then deductible. 100% after deductible. Under 30/hardship eligibility.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "High deductible plan for under 30 or hardship exemption. Covers 3 PCP visits before deductible."
    },
    
    # Small-Group Pro EPO Plans
    {
        "id": "pro-epo-platinum",
        "short_name": "Pro EPO Platinum",
        "full_name": "Healthfirst Pro EPO Platinum",
        "summary_of_benefits": "$0 deductible, $2k OOPM. $20 PCP / $35 specialist copays. $500 inpatient / $250 ER copays. 90% actuarial value.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Small group EPO plan with 90% actuarial value, lowest cost-sharing."
    },
    {
        "id": "pro-epo-gold",
        "short_name": "Pro EPO Gold",
        "full_name": "Healthfirst Pro EPO Gold",
        "summary_of_benefits": "$1,350 deductible, $7k OOPM. $25 PCP / $50 specialist copays. $500 inpatient / $350 ER copays. 80% actuarial value.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Small group EPO plan with 80% actuarial value, moderate cost-sharing."
    },
    {
        "id": "pro-epo-silver",
        "short_name": "Pro EPO Silver",
        "full_name": "Healthfirst Pro EPO Silver",
        "summary_of_benefits": "$2,500 deductible, $8,150 OOPM. $30 PCP / $60 specialist copays. $1,000 inpatient / $400 ER copays. 70% actuarial value.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Small group EPO plan with 70% actuarial value, standard cost-sharing."
    },
    {
        "id": "pro-epo-bronze",
        "short_name": "Pro EPO Bronze",
        "full_name": "Healthfirst Pro EPO Bronze",
        "summary_of_benefits": "$5,900 deductible, $9,100 OOPM. $40 PCP / $80 specialist copays. 50% after deductible inpatient / $700 ER copays. 60% actuarial value.",
        "summary_of_benefits_url": "https://healthfirst.org/documents",
        "compressed_summary": "Small group EPO plan with 60% actuarial value, higher cost-sharing."
    }
]

# API endpoint URL
api_url = "http://127.0.0.1:8080/plans/bulk-create"

# Prepare the payload
payload = {
    "plans": all_healthfirst_plans
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