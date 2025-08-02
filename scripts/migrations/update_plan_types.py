import requests
import json

# First get existing plans
list_response = requests.get("http://127.0.0.1:8080/plans/api/list")
existing_plans = {}
if list_response.status_code == 200:
    for plan in list_response.json()["plans"]:
        existing_plans[plan["id"]] = plan

# Define plan types for each plan and merge with existing data
plan_type_updates = []

# Map of plan IDs to their types
plan_types_map = {
    # Medicaid plans
    "medicaid-managed-care": "Medicaid",
    "medicaid-harp": "Medicaid", 
    "child-health-plus": "Medicaid",
    "essential-plan-1": "Medicaid",
    "essential-plan-2": "Medicaid",
    "essential-plan-3": "Medicaid",
    "essential-plan-4": "Medicaid",
    
    # Dual Eligible plans
    "completecare-dsnp": "Dual Eligible",
    "senior-health-partners": "Dual Eligible",
    "ib-dual": "Dual Eligible",
    "dsnp-lip-connection": "Dual Eligible",
    "life-improvement-plan": "Dual Eligible",
    "connection-plan": "Dual Eligible",
    
    # Medicare plans
    "increased-benefits-plan": "Medicare",
    "65-plus-hmo": "Medicare",
    "signature-hmo": "Medicare",
    "signature-ppo": "Medicare",
    
    # Marketplace plans
    "leaf-platinum": "Marketplace",
    "leaf-gold": "Marketplace",
    "leaf-silver": "Marketplace",
    "leaf-bronze": "Marketplace",
    "leaf-catastrophic": "Marketplace",
    "pro-epo-platinum": "Marketplace",
    "pro-epo-gold": "Marketplace",
    "pro-epo-silver": "Marketplace",
    "pro-epo-bronze": "Marketplace",
    "hfic-small-group-epo": "Marketplace"
}

# Create updates with all required fields
for plan_id, plan_type in plan_types_map.items():
    if plan_id in existing_plans:
        plan_data = existing_plans[plan_id].copy()
        plan_data["plan_type"] = plan_type
        plan_type_updates.append(plan_data)

# API endpoint URL
api_url = "http://127.0.0.1:8080/plans/bulk-create"

# Prepare the payload - using bulk-create endpoint for updates
payload = {
    "plans": plan_type_updates
}

# Make the API request
try:
    response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! {result['message']}")
        print(f"Created: {result['created']} plans")
        print(f"Updated: {result['updated']} plans")
        
        # Verify the updates
        list_response = requests.get("http://127.0.0.1:8080/plans/api/list")
        if list_response.status_code == 200:
            plans = list_response.json()["plans"]
            
            # Count by type
            type_counts = {}
            for plan in plans:
                plan_type = plan.get('plan_type', 'Unassigned')
                type_counts[plan_type] = type_counts.get(plan_type, 0) + 1
            
            print("\nPlan counts by type:")
            for plan_type, count in sorted(type_counts.items()):
                print(f"- {plan_type}: {count} plans")
                
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the Flask server. Make sure it's running on http://127.0.0.1:8080")
except Exception as e:
    print(f"Error: {str(e)}")