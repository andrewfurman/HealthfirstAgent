#!/usr/bin/env python3
"""
Update Leaf Bronze plan with Summary of Benefits and Coverage text
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plans.plans_model import Plan

# Load environment variables
load_dotenv()

# The full text content for Leaf Bronze
leaf_bronze_text = """Healthfirst: Bronze Leaf
Summary of Benefits and Coverage: What this Plan Covers & What You Pay for Covered Services
Coverage Period: 01/01/2025 – 12/31/2025
Coverage for: All Coverage Types | Plan Type: HMO

The Summary of Benefits and Coverage (SBC) document will help you choose a health plan. The SBC shows you how you and the plan would share the cost for covered health care services. NOTE: Information about the cost of this plan (called the premium) will be provided separately. This is only a summary. For more information about your coverage, or to get a copy of the complete terms of coverage,1-855-789-3668. For general definitions of common terms, such as allowed amount, balance billing, coinsurance, copayment, deductible, provider, or other underlined terms, see the Glossary. You can view the Glossary at www.healthfirst.org or call 1-855-789-3668 to request a copy.

Important Questions Answers Why This Matters:

What is the overall deductible?
$3,800 Individual/ $7,600 Family for In-Network Providers. Does not apply to preventive care visits or services.
Generally, you must pay all of the costs from providers up to the deductible amount before this plan begins to pay. If you have other family members on the plan, each family member must meet their own individual deductible until the total amount of deductible expenses paid by all family members meets the overall family deductible.

Are there services covered before you meet your deductible?
Yes. Preventive care, prenatal care and telemedicine are covered before you meet your deductible
This plan covers some items and services even if you haven't yet met the deductible amount. But a copayment or coinsurance may apply. For example, this plan covers certain preventive services without cost-sharing and before you meet your deductible. See a list of covered preventive services at https://www.healthcare.gov/coverage/preventive-care-benefits/

Are there other deductibles for specific services?
No.
You don't have to meet deductibles for specific services.

What is the out-of-pocket limit for this plan?
Individual $9,200/ Family $18,400
The out-of-pocket limit is the most you could pay in a year for covered services.

What is not included in the out-of-pocket limit?
Premium, Balance Billing charges and the cost of health care services this plan does not cover.
Even though you pay these expenses, they don't count toward the out–of–pocket limit.

Will you pay less if you use a network provider?
Yes. See www.healthfirst.org or call 1-888-250-2220 for a list of network providers.
This plan uses a provider network. You will pay less if you use a provider in the plan's network. You will pay the most if you use an out-of-network provider, and you might receive a bill from a provider for the difference between the provider's charge and what your plan pays (balance billing). Be aware, your network provider might use an out-of-network provider for some services (such as lab work). Check with your provider before you get services.

Do you need a referral to see a specialist?
No.
You can see the specialist you choose without a referral.

(DT - OMB control number: 1545-0047/Expiration Date: 12/31/2019) (DOL - OMB control number: 1210-0147/Expiration date: 5/31/2022)
(HHS - OMB control number: 0938-1146/Expiration date: 10/31/2022)
HF-BSBC-STD-25
Page 1 of 8

All copayment and coinsurance costs shown in this chart are after your deductible has been met, if a deductible applies.

Common Medical Event | Services You May Need | What You Will Pay Network Provider (You will pay the least) | Out-of-Network Provider (You will pay the most) | Limitations, Exceptions, & Other Important Information

If you visit a health care provider's office or clinic:

Primary care visit to treat an injury or illness
**$50 copay not subject to deductible for first 3 visits ** $50 co-pay after deductible for additional visits | Not Covered | Applies to PCP, Specialist, outpatient MH/SUD or combo; $50 copay after deductible for additional visits. In-network primary care visits delivered via Telehealth are subject to $50 co-pay

Specialist visit
** $75 co-pay not subject to deductible for first 3 visits $75 co-pay after deductible for additional visits | Not Covered | Applies to PCP, Specialist, outpatient MH/SUD or combo; $75 copay after deductible for additional visits. In-network specialist visits delivered via Telehealth are subject to $75 co-pay

Preventive care/screening/immunization
No Charge | Not Covered | --------------------None---------------------

If you have a test:

Diagnostic test (x-ray, blood work)
**$75 co-pay after deductible (All places of service) for x-ray/ $50 co-pay after deductible (All places of services) for bloodwork | Not Covered | Preauthorization Required

Imaging (CT/PET scans, MRIs)
**$175 co-pay after deductible | Not Covered | Preauthorization Required

* For more information about limitations and exceptions, see the plan or policy document at www.healthfirst.org
**Cost-share is waived if the primary diagnosis is diabetes
HF-BSBC-STD-25
Page 2 of 8

If you need drugs to treat your illness or condition:
More information about prescription drug coverage is available at www.healthfirst.org

Generic drugs
**$10 co-pay after deductible/30-day prescription (retail) and $25 co-pay after deductible/90-day prescription (mail order) | Not Covered | Covers up to a 30-day supply (retail prescription) or up to a 90-day supply (mail order prescription)

Preferred brand drugs
**$35 co-pay after deductible/30-day prescription (retail) and $87.50 co-pay after deductible/90-day prescription (mail order) | Not Covered

Non-preferred brand drugs
**$70 co-pay after deductible/30-day prescription (retail) and $175 co-pay after deductible/90-day prescription (mail order) | Not Covered

NOTE: Diabetes medication, supplies, equipment, and self-management education are subject to a deductible. The primary care office visit copayment applies after the deductible is met
**Cost-share is waived if the primary diagnosis is diabetes.

Specialty drugs
**$70 co-pay after deductible/30-day prescription (retail) and $175 co-pay after deductible/90-day prescription (mail order) | Not Covered

If you have outpatient surgery:

Facility fee (e.g., ambulatory surgery center)
$150 copayment after deductible | Not Covered | Preauthorization Required

Physician/surgeon fees
$150 copayment after deductible | Not Covered | Applies only to surgery performed in a hospital outpatient facility setting, including freestanding surgicenters, not to office surgery.

* For more information about limitations and exceptions, see the plan or policy document at www.healthfirst.org
**Cost-share is waived if the primary diagnosis is diabetes.
HF-BSBC-STD-25
Page 3 of 8

If you need immediate medical attention:

Emergency room care
$500 co-pay after deductible | $500 co-pay after deductible | Co-pay / Co-insurance waived if Hospital admission

Emergency medical transportation
$300 co-pay after deductible | $300 co-pay after deductible | --------------------None---------------------

Urgent care
**$75 co-pay after deductible | Not Covered | --------------------None---------------------

If you have a hospital stay:

Facility fee (e.g., hospital room)
$1,500 co-pay after deductible per admission | Not Covered | Preauthorization Required. However, Preauthorization is Not Required for Emergency Admissions

Physician/surgeon fees
$150 co-pay after deductible | Not Covered | Applies only to surgery performed in a hospital inpatient or hospital outpatient facility setting, including freestanding surgicenters, not to office surgery.

If you need mental health, behavioral health, or substance abuse services:

Outpatient services
$50 co-pay not subject to deductible for first 3 visits | Not Covered | PCP, Specialist, outpatient MH/SUD or any combo of; $50 copay after deductible for additional visits. Prior authorization required. 20 visits per plan year for Family Counseling

Inpatient services
$1,500 co-pay after deductible per admission | Not Covered | Preauthorization Required. However, Preauthorization is Not Required for Emergency Admissions

If you are pregnant:

Office visits
Covered in full | Not Covered | If Care provided in accordance with the comprehensive guidelines supported by USPSTF and HRSA

Childbirth/delivery professional services
$150 co-pay after deductible | Not Covered | Preauthorization Required

Childbirth/delivery facility services
$1,500 co-pay after deductible per admission | Not Covered | Preauthorization Required

* For more information about limitations and exceptions, see the plan or policy document at www.healthfirst.org
**Cost-share is waived if the primary diagnosis is diabetes
HF-BSBC-STD-25
Page 4 of 8

If you need help recovering or have other special health needs:

Home health care
$50 co-pay after deductible | Not Covered | Preauthorization Required. 40 visits per Plan year

Rehabilitation services
$50 co-pay after deductible | Not Covered | Preauthorization Required; 60 visits per condition, per plan year combined therapies

Habilitation services
$50 co-pay after deductible | Not Covered | Preauthorization Required; 60 visits per condition, per plan year combined therapies

Skilled nursing care
$1,500 co-pay after deductible per admission | Not Covered | Preauthorization Required; 200 days per plan year

Durable medical equipment
**50% co-insurance after deductible | Not Covered | Preauthorization Required

Hospice services
$1,500 copayment after deductible per admission (Inpatient)
$50 copayment after deductible (Outpatient) | Not Covered | Preauthorization Required; 210 days per plan year (inpatient); 5 Visits for Family Bereavement Counseling (outpatient)

If your child needs dental or eye care:

Children's eye exam
$50 co-pay after deductible | Not Covered | One Exam Per 12-Month Period

Children's glasses
50% co-insurance after deductible | Not Covered | One Prescribed Lenses & Frames in a 12-Month Period. $100 Annual Allowance towards purchase of frames or contact lenses.

Children's dental check-up
$50 co-pay after deductible | Not Covered | One Dental Exam & Cleaning Per 6-Month Period

* For more information about limitations and exceptions, see the plan or policy document at www.healthfirst.org
**Cost-share is waived if the primary diagnosis is diabetes
HF-BSBC-STD-25
Page 5 of 8

Excluded Services & Other Covered Services:

Services Your Plan Generally Does NOT Cover (Check your policy or plan document for more information and a list of any other excluded services.)
• Acupuncture
• Cosmetic Surgery
• Long Term Care
• Non-emergency care when traveling outside the U.S.
• Private-duty nursing
• Routine foot care
• Weight loss programs
• Routine eye care (Adult)
• Dental (Adult)

Other Covered Services (Limitations may apply to these services. This isn't a complete list. Please see your plan document.)
• Bariatric Surgery
• Chiropractic Care
• Hearing Aids
• Infertility Treatment
• Abortion Services

Your Rights to Continue Coverage: There are agencies that can help if you want to continue your coverage after it ends. The contact information for those agencies is: New York State Department of Financial Services at 1-800-342-5756 or www.dfs.ny.gov/, HHS, DOL, and/or other applicable agency contact information. Other coverage options may be available to you too, including buying individual insurance coverage through the Health Insurance Marketplace. For more information about the Marketplace, visit www.HealthCare.gov or call 1-800-318-2596 or NY State of Health Marketplace at 1-855-355-5777 or www.nystateofhealth.ny.gov.

Your Grievance and Appeals Rights: There are agencies that can help if you have a complaint against your plan for a denial of a claim. This complaint is called a grievance or appeal. For more information about your rights, look at the explanation of benefits you will receive for that medical claim. Your plan documents also provide complete information to submit a claim, appeal, or a grievance for any reason to your plan. For more information about your rights, this notice, or assistance, contact:

New York State Department of Financial Services
One State Street
New York, NY 10004-1511
800-342-3736

Additionally, a consumer assistance program can help you file your appeal, contact:
Community Health Advocates
633 Third Ave, 10th FL
New York, NY 10017
888-614-5400
cha@cssny.org.

* For more information about limitations and exceptions, see the plan or policy document at www.healthfirst.org
HF-BSBC-STD-25
Page 6 of 8

Does this plan provide Minimum Essential Coverage? Yes
Minimum Essential Coverage generally includes plans, health insurance available through the Marketplace or other individual market policies, Medicare, Medicaid, CHIP, TRICARE, and certain other coverage. If you are eligible for certain types of Minimum Essential Coverage, you may not be eligible for the premium tax credit.

Does this plan meet the Minimum Value Standards? Yes
If your plan doesn't meet the Minimum Value Standards, you may be eligible for a premium tax credit to help you pay for a plan through the Marketplace.

Language Access Services:
Spanish (Español): Para obtener asistencia en Español, llame al 1-888-250-2220
Tagalog (Tagalog): Kung kailangan ninyo ang tulong sa Tagalog tumawag sa 1-888-250-2220.
Chinese (中文): 如果需要中文的帮助，请拨打这个号码 1-888-250-2220.
Navajo (Dine): Dinek'ehgo shika at'ohwol ninisingo, kwiijigo holne' 1-888-250-2220.

**Cost-share is waived if the primary diagnosis is diabetes.

––––––––––––––––––––––To see examples of how this plan might cover costs for a sample medical situation, see the next section. –––––––––––––––––––––

* For more information about limitations and exceptions, see the plan or policy document at www.healthfirst.org
HF-BSBC-STD-25
Page 7 of 8

About these Coverage Examples:
This is not a cost estimator. Treatments shown are just examples of how this plan might cover medical care. Your actual costs will be different depending on the actual care you receive, the prices your providers charge, and many other factors. Focus on the cost-sharing amounts (deductibles, copayments and coinsurance) and excluded services under the plan. Use this information to compare the portion of costs you might pay under different health plans. Please note these coverage examples are based on self-only coverage.

Peg is Having a Baby
(9 months of in-network pre-natal care and a hospital delivery)
■ The plan's overall deductible $3,800
■ Specialist $75
■ Hospital (facility) $1,500
■ Other $75

This EXAMPLE event includes services like:
Specialist office visits (prenatal care)
Childbirth/Delivery Professional Services
Childbirth/Delivery Facility Services
Diagnostic tests (ultrasounds and blood work)
Specialist visit (anesthesia)

Total Example Cost $12,700
In this example, Peg would pay:
Cost Sharing
Deductibles $3,800
Copayments $1,500
Coinsurance $0
What isn't covered
Limits or exclusions $2,700
The total Peg would pay is $8,000

Managing Joe's type 2 Diabetes
(a year of routine in-network care of a well-controlled condition)
■ The plan's overall deductible $3,800
■ Specialist $75
■ Hospital (facility) $1,500
■ Other $75

This EXAMPLE event includes services like:
Primary care physician office visits (including disease education)
Diagnostic tests (blood work)
Prescription drugs
Durable medical equipment (glucose meter)

Total Example Cost $5,600
In this example, Joe would pay:
Cost Sharing
Deductibles $2,300
Copayments $0
Coinsurance $0
What isn't covered
Limits or exclusions $20
The total Joe would pay is $2,320

Mia's Simple Fracture
(in-network emergency room visit and follow up care)
■ The plan's overall deductible $3,800
■ Specialist $75
■ Hospital (facility) $1,500
■ Other $75

This EXAMPLE event includes services like:
Emergency room care (including medical supplies)
Diagnostic test (x-ray)
Durable medical equipment (crutches)
Rehabilitation services (physical therapy)

Total Example Cost $2,800
In this example, Mia would pay:
Cost Sharing
Deductibles $2,800
Copayments $0
Coinsurance $0
What isn't covered
Limits or exclusions $0
The total Mia would pay is $2,800

The plan would be responsible for the other costs of these EXAMPLE covered services
HF-BSBC-STD-25
Page 8 of 8

Notice of Non‑Discrimination
Healthfirst complies with Federal civil rights laws. Healthfirst does not exclude people or treat them differently because of race, color, national origin, age, disability, or sex.

Healthfirst provides the following:
• Free aids and services to people with disabilities to help you communicate with us, such as:
  ◦ Qualified sign language interpreters
  ◦ Written information in other formats (large print, audio, accessible electronic formats, other formats)
• Free language services to people whose first language is not English, such as:
  ◦ Qualified interpreters
  ◦ Information written in other languages

If you need these services, call Healthfirst at 1‑866‑305‑0408.
For TTY services, call 1‑888‑542‑3821.

If you believe that Healthfirst has not given you these services or has treated you differently because of race, color, national origin, age, disability, or sex, you can file a grievance with Healthfirst by:
• Mail: Healthfirst Member Services, P.O. Box 5165, New York, NY 10274‑5165
• Phone: 1‑866‑305‑0408 (for TTY services, call 1‑888‑542‑3821)
• Fax: 1‑212‑801‑3250
• In person: Visit a Healthfirst Community Office. Locations and hours are available at Healthfirst.org/CommunityOffices

You can also file a civil rights complaint with the U.S. Department of Health and Human Services, Office for Civil Rights by:
• Web: Office for Civil Rights Complaint Portal at https://ocrportal.hhs.gov/ocr/portal/lobby.jsf
• Mail: U.S. Department of Health and Human Services
  200 Independence Avenue SW., Room 509F, HHH Building, Washington, DC 20201
  Complaint forms are available at http://www.hhs.gov/ocr/office/file/index.html
• Phone: 1‑800‑368‑1019 (TTY 800‑537‑7697)

1523-18"""

def main():
    # Connect to database
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get Leaf Bronze plan
        plan = session.query(Plan).filter_by(short_name='Leaf Bronze').first()
        
        if not plan:
            print("ERROR: Leaf Bronze plan not found in database")
            return
        
        print(f"Found plan: {plan.short_name} (ID: {plan.id})")
        print(f"Current document text length: {len(plan.plan_document_full_text) if plan.plan_document_full_text else 0}")
        
        # Update the plan with the new text
        plan.plan_document_full_text = leaf_bronze_text
        
        # Commit the changes
        session.commit()
        print(f"Successfully updated Leaf Bronze plan with {len(leaf_bronze_text)} characters of text")
        
    except Exception as e:
        session.rollback()
        print(f"Error updating plan: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()