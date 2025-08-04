# Product Requirements Document (PRD)
## Healthfirst AI Voice Assistant & Plan Management System

## Business Purpose

The Healthfirst AI Voice Assistant is a comprehensive call center automation system that provides real-time voice interactions with members using OpenAI's Realtime API, combined with a robust plan management system for Healthfirst's diverse insurance portfolio. The system serves as both a customer-facing voice interface and an internal plan data management platform.

### Key Objectives
1. **Voice-First Customer Experience**: Provide natural, conversational interactions for Healthfirst members
2. **Comprehensive Plan Coverage**: Support all Healthfirst insurance product lines with detailed benefit information
3. **Agent Efficiency**: Reduce call handling time while maintaining high-quality service
4. **Data Centralization**: Unified system for managing complex insurance plan data across multiple product lines

---

## Product Overview

### Core Components

#### 1. Voice Chat System
- **Real-time Audio Processing**: Browser-based WebRTC implementation for seamless voice communication
- **AI-Powered Conversations**: GPT-4o integration via OpenAI Realtime API for natural language understanding
- **Ephemeral Sessions**: Secure, temporary session tokens for each conversation
- **24/7 Availability**: Always-on voice assistance for member inquiries

#### 2. Plan Management System
- **Multi-Product Support**: Comprehensive coverage of Healthfirst's entire insurance portfolio
- **Document Processing**: Automated extraction and processing of PDF plan documents
- **Search & Discovery**: Advanced search capabilities across plan benefits and coverage details
- **Dynamic Content**: Real-time plan information updates and benefit calculations

#### 3. Database Architecture
- **PostgreSQL Backend**: Robust relational database for complex plan relationships
- **SQLAlchemy ORM**: Object-relational mapping for efficient data operations
- **Connection Pooling**: Optimized database performance for high-volume operations
- **Migration Support**: Alembic integration for schema version control

---

## Functions

### Voice Interaction Capabilities
1. **Natural Language Processing**
   - Understand member queries in conversational English
   - Process complex benefit questions with multiple variables
   - Handle interruptions and context switching
   - Support medical terminology and insurance jargon

2. **Response Generation**
   - Follow Healthfirst agent guidelines (H-K-O format: Headline → Key numbers → Offer detail)
   - Provide concise, under 30-second responses
   - Use plain language avoiding legal jargon
   - Include specific cost information and coverage details

3. **Session Management**
   - Generate secure, ephemeral OpenAI session tokens
   - Maintain conversation context throughout interaction
   - Handle session timeouts gracefully
   - Log interactions for quality assurance

### Plan Data Management Functions
- Search and retrieve plan information by name or type
- Compare benefits across multiple plans
- Process and extract data from plan documents
- Update plan information in real-time
- Generate summaries and descriptions of plan benefits

---

## Data Attributes to be Stored

### Core Plan Information
Each insurance plan requires the following data elements:

#### Plan Identification
- Unique plan identifier
- Legacy plan identifier for system compatibility
- Short plan name for quick reference
- Complete official plan name
- Product category classification

#### Plan Documentation
- Complete text extracted from official plan documents
- Structured benefit summary information
- Link to official Summary of Benefits document
- Summary of Benefit Coverage content
- Document table of contents for navigation
- Source document format type

#### Plan Descriptions
- One-sentence plan overview
- Condensed benefit summary for quick reference

### Insurance Product Categories

The system must support the following Healthfirst insurance product lines:

#### 1. Medicaid Products
- **Medicaid Managed Care (MMC)**
  - Including HARP (Health and Recovery Plan) benefits
  - $0 deductible, $0 out-of-pocket maximum
  - Comprehensive medical, behavioral health, vision, and dental coverage
  - Prior authorization requirements for elective inpatient and DME

- **Essential Plan (EP-1 through EP-4)**
  - Income-based tiers (≤138% to 151-200% FPL)
  - Variable cost-sharing based on Federal Poverty Level
  - Adult dental and vision included
  - No premium, varying deductibles and copays

- **Child Health Plus**
  - $0 cost-sharing across all services
  - Orthodontics and glasses included
  - No prior authorization for dental/vision services

#### 2. Dual Eligible Special Needs Plans (D-SNP)
- **CompleteCare (HMO D-SNP)**
  - $0 cost-sharing for all services
  - $280 monthly over-the-counter benefit
  - Comprehensive supplemental benefits (meals, transportation)
  - Registered nurse care team coordination

- **Life Improvement Plan (LIP)**
  - Dual eligible with Low-Income Subsidy
  - $575/$170 quarterly OTC benefits
  - Supplemental transportation (28 rides)
  - Medicaid cost-share coverage

- **Connection Plan**
  - Similar D-SNP structure to LIP
  - Tailored benefit packages for dual eligibles

#### 3. Medicare Advantage Plans
- **Increased Benefits Plan (HMO)**
  - $0 deductible, $9,350 out-of-pocket maximum
  - Enhanced OTC benefits and transportation
  - Low-Income Subsidy drug coverage

- **65 Plus HMO**
  - Traditional Medicare Advantage structure
  - Choice of OTC benefits or transportation rides
  - Comprehensive supplemental benefits

- **Signature HMO**
  - $6,700 out-of-pocket maximum
  - Fitness membership included
  - In-network only coverage model

- **Signature PPO**
  - $5,000/$8,000 in-network/combined MOOP
  - Out-of-network coverage available
  - $725 flexible benefit allowance

#### 4. Marketplace Plans (Leaf Series)
- **Platinum Leaf**
  - $0 deductible, $4,000 out-of-pocket maximum
  - Comprehensive coverage with low cost-sharing
  - Premier version includes adult dental/vision

- **Gold Leaf**
  - $600 deductible, $6,000 out-of-pocket maximum
  - Moderate cost-sharing structure

- **Silver Leaf**
  - $1,750 deductible, $9,100 out-of-pocket maximum
  - Cost-Sharing Reduction (CSR) variants for eligible income levels
  - CSR tiers: 94%, 87%, 73% actuarial value adjustments

- **Bronze Leaf**
  - $5,900 deductible, $9,100 out-of-pocket maximum
  - High-deductible, lower premium structure

- **Catastrophic**
  - $9,200 deductible equals out-of-pocket maximum
  - Limited to under-30 or hardship exemption eligible

#### 5. Small Group Commercial
- **Pro EPO Series (Platinum, Gold, Silver, Bronze)**
  - Employer-sponsored coverage
  - Exclusive Provider Organization structure
  - Actuarial value tiers: 90%, 80%, 70%, 60%

#### 6. Long-Term Care
- **Senior Health Partners (MLTC)**
  - Managed Long-Term Care services
  - Home and nursing home care coordination
  - Transportation and care management services

### Benefit Data Elements

For each plan, the system must store detailed benefit information including:

#### Cost-Sharing Information
- Annual deductible amounts
- Per-service deductibles
- Out-of-pocket maximum limits
- In-network vs. out-of-network maximums
- Fixed dollar copayments for specific services
- Percentage-based coinsurance rates
- Monthly premium costs (where applicable)

#### Service Categories

**Primary Care Services**
- Primary Care Provider visit costs
- Specialist consultation fees
- Preventive care service coverage

**Facility Services**
- Inpatient hospital care costs
- Emergency room visit fees
- Urgent care center charges
- Outpatient surgery expenses

**Prescription Drug Coverage**
- Formulary tier structure
- 30-day supply costs by tier
- 90-day supply pricing options
- Prior authorization drug lists
- Low-Income Subsidy cost variations

**Supplemental Benefits**
- Over-the-counter allowance amounts
- Transportation benefit details
- Fitness membership inclusions
- Dental and vision coverage specifics
- Hearing aid benefits
- Meal delivery program details

#### Authorization Requirements
- Services requiring prior authorization
- HMO/EPO referral requirements
- In-network vs. out-of-network coverage rules
- Step therapy requirements for medications

---

## Success Metrics

### Key Performance Indicators (KPIs)
1. **Voice Interaction Metrics**
   - Average call duration reduction: Target 25%
   - First-call resolution rate: Target 85%
   - Member satisfaction scores: Target 4.5/5.0
   - System uptime: Maintain 99.9%

2. **Plan Management Efficiency**
   - Plan update processing time: <24 hours
   - Data accuracy rate: >99.5%
   - Search result relevance: >95%
   - Document processing automation: 90%

3. **Business Impact**
   - Call center cost reduction: Target 30%
   - Agent productivity improvement: Target 40%
   - Member engagement increase: Target 20%
   - Plan inquiry resolution speed: Target 50% improvement

### Quality Assurance Metrics
- **Voice Recognition Accuracy**: >95%
- **Response Appropriateness**: >90% (human evaluation)
- **Plan Information Accuracy**: >99%
- **System Error Rate**: <0.1%

---

## Risk Management

### Technical Risks
- **API Dependencies**: OpenAI service availability and rate limits
- **Voice Quality**: Network latency affecting user experience
- **Database Performance**: High-volume query optimization
- **Integration Complexity**: Multiple system coordination challenges

### Business Risks
- **Regulatory Changes**: Healthcare regulation updates affecting requirements
- **Member Adoption**: User acceptance of AI voice interactions
- **Data Privacy**: HIPAA compliance and breach prevention
- **Competitive Pressure**: Market demands for enhanced digital services

### Mitigation Strategies
- **Redundancy Planning**: Backup systems and failover procedures
- **Regular Testing**: Continuous quality assurance and monitoring
- **Compliance Reviews**: Periodic regulatory compliance audits
- **User Training**: Member education on system capabilities

