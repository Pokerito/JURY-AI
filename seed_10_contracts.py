import os
import sys
import json
import sqlite3
import uuid
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend can be imported
sys.path.insert(0, os.path.dirname(__file__))
try:
    from backend.services.rag_service import RAGService
    rag_service_instance = RAGService()
except Exception as e:
    rag_service_instance = None
    print(f"Note: RAGService deferred or unavailable ({e})")

CONTRACTS_DIR = os.path.join(os.path.dirname(__file__), "demo_contracts")
os.makedirs(CONTRACTS_DIR, exist_ok=True)
DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "data", "jury_ai.db")

demo_contracts = [
    {
        "filename": "01_Senior_Software_Engineer_Employment_Agreement.txt",
        "title": "Senior Software Engineer Employment Agreement",
        "date_offset": 6,
        "score": 35,
        "summary": "This Employment Agreement governs the full-time employment of Alex Mercer as Lead Systems Architect at Apex Cloud Solutions Inc. It establishes an annual base salary of $165,000, 20 days paid leave, and comprehensive health benefits. However, it imposes an excessively broad 3-year worldwide non-compete covenant, automatic intellectual property forfeiture for off-hours personal creations, and unilateral employer termination on 24 hours notice.",
        "entities": {
            "parties": ["Apex Cloud Solutions Inc. (Employer)", "Alex Mercer (Employee)"],
            "dates": ["Effective Date: October 1, 2024", "Notice Period: 24 Hours", "Non-Compete Duration: 36 Months"],
            "amounts": ["Base Salary: $165,000 USD/year", "Discretionary Bonus: Up to $25,000 USD", "Liquidated Damages: $50,000 USD"],
            "jurisdictions": ["Delaware Court of Chancery", "State of California (Contested)"]
        },
        "clauses": [
            {
                "clause_name": "Worldwide Non-Compete Restraint",
                "risk_level": "Critical",
                "justification": "Restricts the employee from performing software engineering services for any cloud or SaaS company worldwide for thirty-six (36) months post-termination, severely restraining trade and future livelihood.",
                "safer_alternative": "Employee agrees not to solicit Apex Cloud's active enterprise clients for a period of six (6) months post-termination within a 25-mile radius of the primary office location."
            },
            {
                "clause_name": "Total IP Assignment (Off-Hours Inventions)",
                "risk_level": "Critical",
                "justification": "Assigns all inventions, software code, patents, and writings conceived by the employee during the employment term to the employer, even if developed entirely on personal time without company equipment.",
                "safer_alternative": "Assignment shall apply solely to inventions directly developed during working hours, using Company resources, or directly related to the Company's active proprietary codebase."
            },
            {
                "clause_name": "Unilateral Immediate Termination",
                "risk_level": "High",
                "justification": "Permits employer to terminate the agreement on 24 hours notice without severance, while requiring 60 days advance written notice from the employee.",
                "safer_alternative": "Either party may terminate employment without cause upon thirty (30) days prior written notice, or payment of thirty days base salary in lieu thereof."
            },
            {
                "clause_name": "Standard Confidentiality & Trade Secrets",
                "risk_level": "Low",
                "justification": "Customary protection of proprietary algorithms, customer lists, and internal server credentials.",
                "safer_alternative": None
            }
        ],
        "text": """SENIOR SOFTWARE ENGINEER EMPLOYMENT AGREEMENT

This Senior Software Engineer Employment Agreement ("Agreement") is entered into as of October 1, 2024, by and between Apex Cloud Solutions Inc., a Delaware corporation ("Employer"), and Alex Mercer ("Employee").

1. POSITION AND RESPONSIBILITIES
Employer hereby employs Employee as Senior Lead Systems Architect. Employee shall perform cloud infrastructure management, microservices engineering, and distributed backend scaling.

2. COMPENSATION & BENEFITS
Employer shall pay Employee an annual base salary of $165,000 USD, payable semi-monthly, subject to statutory tax withholdings. Employee shall be eligible for annual discretionary performance bonuses up to $25,000 USD.

3. UNILATERAL TERMINATION NOTICE
Employer may terminate Employee's employment at any time, with or without cause, upon twenty-four (24) hours prior notice. In contrast, Employee must provide at least sixty (60) days advance written notice prior to resignation.

4. COMPREHENSIVE INTELLECTUAL PROPERTY SURRENDER
Employee agrees that all inventions, discoveries, software code, scripts, designs, patents, and copyrightable works created, conceived, or reduced to practice by Employee during the entire duration of employment—whether created during business hours or off-duty hours, on Company property or on personal hardware—shall immediately become the sole and exclusive property of Employer.

5. POST-EMPLOYMENT NON-COMPETE COVENANT
For a period of thirty-six (36) continuous months following cessation of employment for any reason, Employee shall not directly or indirectly engage in, advise, invest in, or provide technical services to any enterprise providing cloud hosting, distributed computing, or SaaS infrastructure anywhere in the world. Violation shall trigger liquidated damages of $50,000 USD.

6. CONFIDENTIAL INFORMATION
Employee shall maintain strict secrecy regarding Employer's technical documentation, source code, and client rosters during and after employment."""
    },
    {
        "filename": "02_Mutual_Non_Disclosure_Agreement_MNDA.txt",
        "title": "Mutual Non-Disclosure and Confidentiality Agreement",
        "date_offset": 5,
        "score": 88,
        "summary": "This Mutual Non-Disclosure Agreement between Quantum BioTech Labs and Helix Pharma Therapeutics facilitates bilateral technical evaluation for drug discovery partnerships. It incorporates standard confidentiality exclusions, a 3-year sunset period, and mutual obligations. The only moderate concern is a mandatory prevailing party attorney fee shift.",
        "entities": {
            "parties": ["Quantum BioTech Labs Inc.", "Helix Pharma Therapeutics Corp."],
            "dates": ["Execution Date: October 2, 2024", "Survival Term: 3 Years from Disclosure", "Evaluation Period: 12 Months"],
            "amounts": ["No direct financial consideration exchanged", "Remedy: Injunctive Relief"],
            "jurisdictions": ["State of New York Supreme Court", "Commercial Arbitration Division"]
        },
        "clauses": [
            {
                "clause_name": "Prevailing Party Fee Shifting",
                "risk_level": "Medium",
                "justification": "Mandates that the non-prevailing party pay all legal and attorney expenses in any enforcement action, which may discourage legitimate dispute defense.",
                "safer_alternative": "Each party shall bear its own respective legal fees and court expenses in connection with any dispute resolution or litigation."
            },
            {
                "clause_name": "Standard Exclusions from Confidentiality",
                "risk_level": "Low",
                "justification": "Properly excludes public knowledge, prior possession, independent development, and legally subpoenaed information.",
                "safer_alternative": None
            },
            {
                "clause_name": "Mutual Non-Use Restriction",
                "risk_level": "Low",
                "justification": "Restricts use of disclosed information strictly to the stated joint scientific evaluation purpose.",
                "safer_alternative": None
            },
            {
                "clause_name": "Equitable Injunctive Relief",
                "risk_level": "Low",
                "justification": "Allows either party to seek immediate injunction in case of imminent trade secret leakage.",
                "safer_alternative": None
            }
        ],
        "text": """MUTUAL NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is executed on October 2, 2024, by and between Quantum BioTech Labs Inc. ("Quantum") and Helix Pharma Therapeutics Corp. ("Helix").

1. PURPOSE
The parties desire to evaluate potential collaboration in molecular sequence synthesis and computational bio-modeling ("Authorized Purpose").

2. CONFIDENTIAL INFORMATION DEFINITION
"Confidential Information" refers to all proprietary scientific data, lab notes, clinical trial summaries, software source code, and chemical formulations marked confidential or reasonably understood to be proprietary.

3. EXCLUSIONS FROM CONFIDENTIALITY
Confidential Information does not include information that: (a) is or becomes publicly known without breach; (b) was already known to the receiving party prior to disclosure; (c) is independently developed without reference to disclosed data; or (d) is required to be disclosed by valid judicial subpoena.

4. NON-DISCLOSURE & CARE STANDARD
Each receiving party shall protect disclosed confidential materials using the same degree of care (not less than reasonable care) utilized for its own trade secrets and shall not use information beyond the Authorized Purpose.

5. TERM AND SUNSET
This Agreement shall govern disclosures for twelve (12) months. The confidentiality duties shall survive for three (3) years following disclosure.

6. ATTORNEYS' FEES
In the event of litigation arising under this Agreement, the prevailing party shall be entitled to recover reasonable attorneys' fees and court expenses from the non-prevailing party."""
    },
    {
        "filename": "03_Enterprise_SaaS_Master_Services_Agreement.txt",
        "title": "Enterprise Cloud SaaS Master Services Agreement",
        "date_offset": 5,
        "score": 45,
        "summary": "This Master Subscription Agreement between Nexus AI Platforms and Global Retail Logistics LLC governs enterprise AI inventory management services at $48,000 annually. It features severe vendor-favored terms including unilateral fee increases of up to 25% on auto-renewal, disclaimer of all performance warranties, and capping vendor liability to the preceding month's fees.",
        "entities": {
            "parties": ["Nexus AI Platforms LLC (Vendor)", "Global Retail Logistics LLC (Customer)"],
            "dates": ["Effective Date: October 3, 2024", "Initial Term: 24 Months", "Auto-Renewal Window: 30 Days Notice"],
            "amounts": ["Annual Subscription: $48,000 USD", "Cap on Unilateral Price Hike: 25%", "Liability Cap: Preceding 1 Month Fee ($4,000 USD)"],
            "jurisdictions": ["State of California, County of San Francisco", "AAA Commercial Rules"]
        },
        "clauses": [
            {
                "clause_name": "Asymmetrical Liability Cap ($4,000 Cap)",
                "risk_level": "Critical",
                "justification": "Caps vendor liability for data breaches, system outages, or negligence to fees paid in the single preceding month ($4,000), leaving customer severely exposed during catastrophic supply chain disruptions.",
                "safer_alternative": "Vendor liability shall be capped at the total cumulative fees paid by Customer during the preceding twelve (12) months under this Agreement."
            },
            {
                "clause_name": "Unilateral 25% Auto-Renewal Price Escalation",
                "risk_level": "High",
                "justification": "Vendor reserves the right to increase annual subscription rates by up to 25% upon each automatic renewal without requiring Customer's affirmative signed consent.",
                "safer_alternative": "Subscription renewal fees shall not increase by more than the annual Consumer Price Index (CPI) adjustment or 5%, whichever is lower."
            },
            {
                "clause_name": "Total Performance Warranty Disclaimer",
                "risk_level": "High",
                "justification": "Disclaims all express and implied warranties of uptime, algorithmic accuracy, and fitness for commercial purpose ('AS-IS' provision).",
                "safer_alternative": "Vendor warrants that the platform shall achieve at least 99.5% monthly service availability, with proportional service credits for downtime."
            },
            {
                "clause_name": "Customer Data Ownership",
                "risk_level": "Low",
                "justification": "Customer maintains full legal ownership and title to all customer inventory data ingested by the platform.",
                "safer_alternative": None
            }
        ],
        "text": """ENTERPRISE CLOUD SAAS MASTER SERVICES AGREEMENT

This Master Services Agreement ("MSA") is entered into as of October 3, 2024, by Nexus AI Platforms LLC ("Vendor") and Global Retail Logistics LLC ("Customer").

1. SUBSCRIPTION SERVICES
Vendor grants Customer a non-exclusive, non-transferable enterprise subscription to access Vendor's cloud-based automated inventory forecasting platform.

2. FEES AND UNILATERAL PRICE ESCALATION
Customer shall pay an initial annual subscription fee of $48,000 USD. This Agreement automatically renews for successive 12-month periods. Vendor reserves the unilateral right to increase subscription fees by up to twenty-five percent (25%) upon each renewal period.

3. DISCLAIMER OF WARRANTIES
THE PLATFORM AND SERVICES ARE PROVIDED STRICTLY "AS-IS" AND "AS-AVAILABLE". VENDOR DISCLAIMS ALL WARRANTIES, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

4. SEVERE LIMITATION OF LIABILITY
IN NO EVENT SHALL VENDOR'S AGGREGATE LIABILITY ARISING OUT OF SYSTEM DOWNTIME, DATA LOSS, OR BREACH EXCEED THE FEES ACTUALLY PAID BY CUSTOMER TO VENDOR IN THE ONE (1) MONTH IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO LIABILITY.

5. CUSTOMER DATA SOVEREIGNTY
All raw telemetry and inventory records uploaded by Customer remain Customer's sole property. Vendor may use anonymized aggregate metadata for system optimization.

6. GOVERNING LAW
Governed by the laws of California, with disputes resolved via binding arbitration in San Francisco."""
    },
    {
        "filename": "04_Commercial_Office_Lease_Agreement.txt",
        "title": "Commercial Real Estate Office Lease Agreement",
        "date_offset": 4,
        "score": 50,
        "summary": "This Commercial Lease Agreement between Skyline Tower Properties and Innovatech Software Studio covers 3,500 sq.ft of prime office space at $14,000 monthly. While standard in premise description, it exposes the tenant to triple-net retroactive maintenance assessments, non-refundable security deposits on minor defaults, and an absolute ban on subletting.",
        "entities": {
            "parties": ["Skyline Tower Properties Inc. (Landlord)", "Innovatech Software Studio LLC (Tenant)"],
            "dates": ["Commencement Date: November 1, 2024", "Lease Term: 36 Months", "Grace Period: 5 Business Days"],
            "amounts": ["Base Rent: $14,000 USD/month", "Security Deposit: $42,000 USD", "Late Fee: 10% of Monthly Rent"],
            "jurisdictions": ["Civil District Court of Dallas County, Texas"]
        },
        "clauses": [
            {
                "clause_name": "Uncapped Retroactive Common Area Assessments",
                "risk_level": "High",
                "justification": "Permits Landlord to pass uncapped structural capital improvement charges and building roof/HVAC replacements onto tenant as retroactive CAM expenses.",
                "safer_alternative": "Tenant's share of operating expenses shall exclude Landlord capital expenditures and be capped at an annual increase of no more than 6% over base year expenses."
            },
            {
                "clause_name": "Full Security Deposit Forfeiture on Minor Default",
                "risk_level": "High",
                "justification": "Enables landlord to retain the entire $42,000 deposit upon any technical lease breach, regardless of actual repair damages.",
                "safer_alternative": "Security deposit deductions shall be strictly restricted to actual out-of-pocket repair costs or unpaid rent, with detailed accounting returned within 30 days."
            },
            {
                "clause_name": "Absolute Prohibition on Assignment & Subletting",
                "risk_level": "Medium",
                "justification": "Completely bars tenant from subletting spare office desks or assigning lease during corporate restructuring or mergers.",
                "safer_alternative": "Subletting shall be permitted subject to Landlord's prior written consent, which consent shall not be unreasonably withheld, delayed, or conditioned."
            },
            {
                "clause_name": "Peaceful Enjoyment & Standard Occupancy",
                "risk_level": "Low",
                "justification": "Guarantees quiet enjoyment and utility access as long as base rent is settled.",
                "safer_alternative": None
            }
        ],
        "text": """COMMERCIAL REAL ESTATE OFFICE LEASE AGREEMENT

This Commercial Office Lease ("Lease") is executed on October 4, 2024, by Skyline Tower Properties Inc. ("Landlord") and Innovatech Software Studio LLC ("Tenant").

1. DEMISED PREMISES
Landlord leases to Tenant Suite 1400 comprising approximately 3,500 rentable square feet at 500 Commerce Boulevard, Dallas, Texas.

2. TERM AND RENT
The initial term is thirty-six (36) months commencing November 1, 2024. Tenant shall pay Base Rent of $14,000 USD per month on or before the first day of each calendar month.

3. SECURITY DEPOSIT & FORFEITURE
Tenant shall deposit $42,000 USD upon execution. If Tenant defaults in any covenant of this Lease, Landlord may retain the entire Security Deposit as liquidated damages without prejudice to other remedies.

4. OPERATING EXPENSES (CAM)
Tenant shall pay its proportionate share (4.2%) of all building operating expenses, taxes, structural roof repairs, elevator overhauls, and capital upgrades without limitation or ceiling cap.

5. ASSIGNMENT AND SUBLETTING
Tenant shall not assign, mortgage, pledge, or sublet any portion of the Demised Premises without Landlord's sole, unfettered discretion. Any unauthorized occupant shall be deemed an unlawful trespasser.

6. SURRENDER OF PREMISES
Upon termination, Tenant shall restore the premises to its original pristine base-building condition at Tenant's sole expense."""
    },
    {
        "filename": "05_Freelance_FullStack_Development_Contract.txt",
        "title": "Independent Contractor Freelance Development Agreement",
        "date_offset": 4,
        "score": 60,
        "summary": "This Independent Contractor Agreement between BlueWave Marketing Agency and freelance engineer David Vance covers custom e-commerce web application development for $22,000. It features milestone deliverables and source code handover upon payment. However, it imposes unlimited contractor liability and delayed net-60 payment terms.",
        "entities": {
            "parties": ["BlueWave Marketing Agency LLC (Client)", "David Vance (Contractor)"],
            "dates": ["Commencement: October 5, 2024", "Target Completion: December 15, 2024", "Payment Term: Net-60 Days"],
            "amounts": ["Total Project Fee: $22,000 USD", "Milestone 1 (UI Wireframes): $6,000 USD", "Final Milestone (Deployment): $10,000 USD"],
            "jurisdictions": ["State of Washington, King County District Court"]
        },
        "clauses": [
            {
                "clause_name": "Unlimited Contractor Indemnification",
                "risk_level": "Critical",
                "justification": "Contractor assumes open-ended, uncapped indemnity for any third-party claims arising from open-source libraries or third-party API dependencies.",
                "safer_alternative": "Contractor liability shall be capped at the total project compensation received ($22,000), excluding willful misconduct or intentional breach."
            },
            {
                "clause_name": "Net-60 Payment Terms with Discretionary Acceptance",
                "risk_level": "High",
                "justification": "Client reserves 60 days to pay invoices and may withhold milestone payments based on subjective dissatisfaction.",
                "safer_alternative": "Invoices shall be payable within Net-15 days following delivery, with milestone acceptance deemed approved if no written objections are provided within 7 days."
            },
            {
                "clause_name": "IP Transfer Conditioned on Full Payment",
                "risk_level": "Low",
                "justification": "Contractor retains ownership of all custom software code until Client pays final invoice balance.",
                "safer_alternative": None
            },
            {
                "clause_name": "Independent Contractor Tax Status",
                "risk_level": "Low",
                "justification": "Correctly establishes non-employee, 1099 contractor relationship with independent tax duties.",
                "safer_alternative": None
            }
        ],
        "text": """INDEPENDENT CONTRACTOR FREELANCE DEVELOPMENT AGREEMENT

This Agreement is made on October 5, 2024, by BlueWave Marketing Agency LLC ("Client") and David Vance ("Contractor").

1. SCOPE OF SERVICES
Contractor shall build a custom Next.js and PostgreSQL e-commerce checkout flow as detailed in Exhibit A ("Deliverables").

2. COMPENSATION & NET-60 PAYMENT
Total contract fee is $22,000 USD, divided into three milestones. Invoices shall be payable by Client within sixty (60) days of receipt ("Net-60"). Client may withhold payment if deliverables fail to satisfy Client's subjective artistic standards.

3. INTELLECTUAL PROPERTY TRANSFER
Upon receipt of full and final compensation, Contractor assigns to Client all right, title, and copyright in and to the custom software code created specifically for this project.

4. INDEMNITY & UNLIMITED LIABILITY
Contractor agrees to indemnify, defend, and hold harmless Client, its officers, and affiliates from all losses, damages, legal fees, or patent disputes arising from Contractor's software deliverables or integrated open-source libraries, without monetary limitation.

5. INDEPENDENT STATUS
Contractor is an independent contractor, solely responsible for self-employment taxes, equipment, and insurance."""
    },
    {
        "filename": "06_Proprietary_Software_IP_Assignment_License.txt",
        "title": "Proprietary Software Technology IP Assignment and Transfer",
        "date_offset": 3,
        "score": 92,
        "summary": "This Software IP Assignment Agreement between Founder Technologies and Veloce Robotics Corp formalizes the acquisition of autonomous navigation algorithms for $320,000. It features comprehensive mutual representations, balanced indemnity caps, clean patent title transfers, and standard escrow provisions.",
        "entities": {
            "parties": ["Founder Technologies LLC (Assignor)", "Veloce Robotics Corp (Assignee)"],
            "dates": ["Closing Date: October 6, 2024", "Patent Filing Window: 90 Days", "Survival of Reps: 24 Months"],
            "amounts": ["Purchase Consideration: $320,000 USD", "Escrow Holdback: $32,000 USD"],
            "jurisdictions": ["United States District Court for Northern District of California"]
        },
        "clauses": [
            {
                "clause_name": "Balanced Mutual Indemnification Cap",
                "risk_level": "Low",
                "justification": "Indemnity is mutually capped at the purchase price ($320,000) with customary carve-outs for intentional fraud.",
                "safer_alternative": None
            },
            {
                "clause_name": "Clear IP Title Warranty",
                "risk_level": "Low",
                "justification": "Assignor warrants clear, unencumbered ownership of all algorithms without third-party lien or GPL viral license contamination.",
                "safer_alternative": None
            },
            {
                "clause_name": "Escrow Holdback Release",
                "risk_level": "Low",
                "justification": "10% escrow holdback ($32,000) releases automatically after 180 days absent verified third-party patent litigation.",
                "safer_alternative": None
            },
            {
                "clause_name": "Cooperation in Further Assurances",
                "risk_level": "Low",
                "justification": "Standard obligation to execute formal patent registry filings before the USPTO upon request.",
                "safer_alternative": None
            }
        ],
        "text": """PROPRIETARY SOFTWARE TECHNOLOGY IP ASSIGNMENT AND TRANSFER

This Software Intellectual Property Assignment Agreement ("Agreement") is dated October 6, 2024, by Founder Technologies LLC ("Assignor") and Veloce Robotics Corp ("Assignee").

1. ASSIGNMENT OF INTELLECTUAL PROPERTY
Assignor hereby irrevocably sells, assigns, and transfers to Assignee all worldwide right, title, and interest in and to the computer vision algorithms, neural weights, and source code entitled "PathFinder v3.2".

2. CONSIDERATION & ESCROW
Assignee shall pay total consideration of $320,000 USD, of which $288,000 USD is delivered at closing, and $32,000 USD is deposited into neutral third-party escrow for 180 days to secure indemnification claims.

3. REPRESENTATIONS AND WARRANTIES
Assignor warrants that: (a) Assignor is the sole legal owner of the code; (b) the software does not contain copyleft (GPL) code; and (c) the technology does not infringe any third-party patent or copyright.

4. LIABILITY CEILING
Except for fraud, each party's aggregate indemnification liability shall not exceed the Total Consideration actually paid ($320,000 USD).

5. GOVERNING LAW
Governed by federal patent law and California state law."""
    },
    {
        "filename": "07_Hardware_Supply_and_Vendor_Procurement.txt",
        "title": "Industrial Equipment Supply & Procurement Master Contract",
        "date_offset": 3,
        "score": 55,
        "summary": "This Master Procurement Contract between Precision Dynamics GmbH and NorthStar Renewable Power covers industrial wind turbine gearboxes for $580,000. It features tight delivery milestones and quality inspection standards, but imposes severe 1% per day liquidated damages for delivery delays and unilateral buyer cancellation rights.",
        "entities": {
            "parties": ["Precision Dynamics GmbH (Supplier)", "NorthStar Renewable Power Inc. (Buyer)"],
            "dates": ["Order Date: October 6, 2024", "Shipment Deadline: January 15, 2025", "Warranty Duration: 24 Months"],
            "amounts": ["Total Purchase Order: $580,000 USD", "Delay Penalty: 1% per calendar day", "Defect Remedy Cap: Up to Full Contract Value"],
            "jurisdictions": ["ICC International Court of Arbitration, Geneva", "Swiss Substantive Law"]
        },
        "clauses": [
            {
                "clause_name": "Aggressive Liquidated Delay Damages (1%/day)",
                "risk_level": "Critical",
                "justification": "Imposes 1% of total contract value ($5,800/day) penalty for any shipment delay, compounding rapidly without a reasonable liability ceiling.",
                "safer_alternative": "Delay liquidated damages shall be 0.1% per business day, capped at a maximum of 5% of the total purchase order, excluding verifiable Force Majeure events."
            },
            {
                "clause_name": "Unilateral Cancellation for Buyer Convenience",
                "risk_level": "High",
                "justification": "Buyer may cancel custom manufactured industrial orders at any time without compensating Supplier for raw materials already acquired.",
                "safer_alternative": "In the event of cancellation for convenience, Buyer shall reimburse Supplier for verifiable labor incurred and customized raw materials purchased."
            },
            {
                "clause_name": "Two-Year Comprehensive Replacement Warranty",
                "risk_level": "Low",
                "justification": "Standard manufacturer warranty to repair or replace mechanical gearboxes exhibiting metal fatigue or manufacturing defects.",
                "safer_alternative": None
            },
            {
                "clause_name": "ICC International Arbitration",
                "risk_level": "Low",
                "justification": "Neutral dispute resolution mechanism under ICC rules in Geneva.",
                "safer_alternative": None
            }
        ],
        "text": """INDUSTRIAL EQUIPMENT SUPPLY & PROCUREMENT MASTER CONTRACT

This Procurement Master Contract is entered into on October 6, 2024, by Precision Dynamics GmbH ("Supplier") and NorthStar Renewable Power Inc. ("Buyer").

1. SCOPE OF PROCUREMENT
Supplier shall manufacture and deliver eight (8) industrial planetary wind turbine gearboxes ("Equipment") according to Buyer's technical specifications.

2. PRICE & INCOTERMS
Total contract price is $580,000 USD. Delivery shall be executed DDP Port of Houston by January 15, 2025.

3. LIQUIDATED DELAY DAMAGES
If Supplier fails to deliver Equipment by the Shipment Deadline, Supplier shall pay Buyer liquidated damages equal to one percent (1%) of the total contract value ($5,800 USD) for each calendar day of delay, without limitation.

4. BUYER CANCELLATION RIGHTS
Buyer reserves the right to terminate this contract in whole or in part at any time for its convenience without liability for work-in-progress or customized raw steel materials acquired.

5. PRODUCT WARRANTY
Supplier warrants Equipment against defects in material and workmanship for twenty-four (24) months from commissioning."""
    },
    {
        "filename": "08_Joint_Venture_and_Strategic_Partnership_MOU.txt",
        "title": "Strategic Joint Venture and Cross-License MOU",
        "date_offset": 2,
        "score": 75,
        "summary": "This Joint Venture Memorandum of Understanding between Solaria Clean Energy and Horizon Grid Systems outlines an 50-50 equity partnership to deploy battery storage infrastructure. It incorporates balanced capital calls and mutual governance representation. The primary area of risk is a mandatory buy-sell Russian Roulette clause in the event of board deadlock.",
        "entities": {
            "parties": ["Solaria Clean Energy Corp.", "Horizon Grid Systems Inc."],
            "dates": ["MOU Date: October 7, 2024", "Definitive Agreement Target: November 30, 2024", "Exclusivity Period: 60 Days"],
            "amounts": ["Initial Joint Capital Contribution: $2,000,000 USD ($1M each)", "Target Project Financing: $10,000,000 USD"],
            "jurisdictions": ["Delaware Court of Chancery", "Bilateral Mediation Requirement"]
        },
        "clauses": [
            {
                "clause_name": "Russian Roulette Shotgun Buy-Sell Deadlock",
                "risk_level": "High",
                "justification": "A board deadlock triggers a sudden mandatory shotgun buy-sell mechanism allowing the larger-capitalized partner to force buy-out of the smaller partner.",
                "safer_alternative": "Deadlocks shall undergo mandatory 30-day mediation with senior executive officers, followed by neutral expert appraisal rather than forced shotgun buy-out."
            },
            {
                "clause_name": "Strict Mutual Exclusivity",
                "risk_level": "Medium",
                "justification": "Restricts both parties from exploring alternative battery grid partnerships in North America for 12 months.",
                "safer_alternative": "Exclusivity shall apply strictly to the named pilot deployment projects rather than the entire North American continent."
            },
            {
                "clause_name": "Equal 50/50 Governance Representation",
                "risk_level": "Low",
                "justification": "Ensures equal board seats and veto power over major expenditures exceeding $100,000.",
                "safer_alternative": None
            },
            {
                "clause_name": "Proportional Capital Contribution",
                "risk_level": "Low",
                "justification": "Establishes transparent 50-50 initial capital calls ($1,000,000 each) in an escrowed project account.",
                "safer_alternative": None
            }
        ],
        "text": """STRATEGIC JOINT VENTURE AND CROSS-LICENSE MOU

This Strategic Joint Venture Memorandum ("MOU") is entered into on October 7, 2024, by Solaria Clean Energy Corp. ("Solaria") and Horizon Grid Systems Inc. ("Horizon").

1. PARTNERSHIP PURPOSE
The parties intend to form a 50/50 Delaware Limited Liability Company ("JV Entity") to construct commercial grid-scale energy storage facilities.

2. CAPITALIZATION
Each party shall contribute $1,000,000 USD in initial cash equity, securing equal 50% voting membership interests.

3. DEADLOCK RESOLUTION (SHOTGUN BUY-SELL)
If the Board of Managers cannot achieve agreement on a Major Decision for forty-five (45) days, either party may invoke a Russian Roulette Buy-Sell notice stating a cash valuation per share. The receiving party must either purchase the initiating party's interest or sell its own interest at that stated price within fifteen (15) days.

4. EXCLUSIVITY
During the term of this MOU and for twelve (12) months following termination, neither party shall participate in competing utility-scale battery initiatives in North America.

5. NON-BINDING NATURE
Except for Sections 3, 4, and Governing Law, this MOU represents an expression of commercial intent."""
    },
    {
        "filename": "09_Cloud_Platform_Terms_of_Service_and_Privacy.txt",
        "title": "Cloud Platform Developer Terms of Service & EULA",
        "date_offset": 1,
        "score": 30,
        "summary": "These Developer Terms of Service govern API access and compute provisioning for TensorCompute AI Cloud. It contains heavily aggressive terms against developers: mandatory binding arbitration, total class action waivers, unilateral modification rights without email notice, and a unilateral waiver of user rights to sue for catastrophic data loss.",
        "entities": {
            "parties": ["TensorCompute AI Cloud Inc. (Platform)", "Individual and Enterprise Developers (User)"],
            "dates": ["Effective: October 8, 2024", "Arbitration Opt-Out: 14 Days from Registration"],
            "amounts": ["Aggregate Liability Limit: $50.00 USD", "Developer Fine for Scraping: $10,000 USD"],
            "jurisdictions": ["JAMS Mandatory Arbitration, Santa Clara County, California"]
        },
        "clauses": [
            {
                "clause_name": "Extreme Liability Limitation ($50.00)",
                "risk_level": "Critical",
                "justification": "Limits total platform liability for permanent database corruption or service outage to fifty US dollars ($50.00), regardless of actual business harm.",
                "safer_alternative": "Platform liability shall be capped at total fees paid by the developer in the preceding six (6) months."
            },
            {
                "clause_name": "Unilateral Terms Modification Without Notice",
                "risk_level": "Critical",
                "justification": "Platform reserves the right to modify pricing, API quotas, and liability terms at any time by posting updates on its website without direct email notice.",
                "safer_alternative": "Material modifications to terms or API pricing shall require at least thirty (30) days prior written notice via registered account email."
            },
            {
                "clause_name": "Mandatory Class Action Waiver",
                "risk_level": "High",
                "justification": "Forces developers into individual private arbitration and forbids participating in consolidated consumer or business class actions.",
                "safer_alternative": "Disputes shall be handled in accordance with standard statutory commercial dispute procedures."
            },
            {
                "clause_name": "Developer License to Platform",
                "risk_level": "Medium",
                "justification": "Grants platform a broad royalty-free license to inspect, process, and extract synthetic data from uploaded AI model weights.",
                "safer_alternative": "License shall be strictly limited to hosting and serving compute inference requests without derivative model training."
            }
        ],
        "text": """CLOUD PLATFORM DEVELOPER TERMS OF SERVICE & EULA

These Terms of Service ("Terms") are effective October 8, 2024, and govern access to TensorCompute AI Cloud ("Platform").

1. ACCEPTANCE & UNILATERAL MODIFICATION
By registering an API key, you accept these Terms. Platform may amend, alter, or replace these Terms at any time without individual notice by updating its website. Continued use constitutes binding consent.

2. DEVELOPER DATA LICENSE
Developer grants Platform a perpetual, irrevocable, worldwide license to host, cache, analyze, and extract generalized statistical embeddings from Developer's input prompts and inference datasets.

3. $50 LIABILITY CAP
TO THE MAXIMUM EXTENT PERMITTED BY LAW, PLATFORM'S MAXIMUM CUMULATIVE LIABILITY UNDER ANY THEORY OF TORT, CONTRACT, OR DATA LOSS SHALL BE LIMITED TO FIFTY US DOLLARS (USD $50.00).

4. MANDATORY ARBITRATION AND CLASS ACTION WAIVER
ALL DISPUTES MUST BE RESOLVED INDIVIDUALLY BEFORE A SINGLE JAMS ARBITRATOR IN SANTA CLARA COUNTY, CALIFORNIA. YOU EXPRESSLY WAIVE ANY RIGHT TO PARTICIPATE IN CLASS ACTION LITIGATION."""
    },
    {
        "filename": "10_Executive_Severance_Release_and_Settlement.txt",
        "title": "Executive Separation Agreement and General Release of Claims",
        "date_offset": 1,
        "score": 70,
        "summary": "This Executive Separation Agreement between Lumina Health Systems and departing Chief Technology Officer Elena Rostova provides a $120,000 lump-sum severance and 6 months health coverage in exchange for an all-inclusive waiver of employment claims, mutual non-disparagement, and 12-month non-solicitation.",
        "entities": {
            "parties": ["Lumina Health Systems Corp. (Company)", "Elena Rostova (Executive)"],
            "dates": ["Separation Date: October 8, 2024", "Revocation Period: 7 Days (ADEA compliance)", "Non-Solicit Duration: 12 Months"],
            "amounts": ["Severance Payment: $120,000 USD lump sum", "COBRA Subsidy: 6 Months ($14,400 value)"],
            "jurisdictions": ["Commonwealth of Massachusetts Superior Court, Suffolk County"]
        },
        "clauses": [
            {
                "clause_name": "Asymmetrical Non-Disparagement Duty",
                "risk_level": "High",
                "justification": "Binds departing executive to perpetual non-disparagement while Company's duty is limited only to designated corporate officers rather than the entire institution.",
                "safer_alternative": "Non-disparagement obligations shall be strictly mutual between the executive and the company's board of directors and senior executives."
            },
            {
                "clause_name": "Worldwide Employee Non-Solicitation (12 Months)",
                "risk_level": "Medium",
                "justification": "Prohibits executive from recruiting former engineering colleagues for twelve months post-departure.",
                "safer_alternative": "Non-solicitation shall apply only to employees with whom executive worked directly in the final 6 months of employment."
            },
            {
                "clause_name": "Comprehensive General Release of Claims",
                "risk_level": "Low",
                "justification": "Customary, statutory ADEA and Title VII waiver of employment claims in exchange for substantial severance consideration.",
                "safer_alternative": None
            },
            {
                "clause_name": "Severance Payout Schedule",
                "risk_level": "Low",
                "justification": "Defines clear $120,000 cash payment within 14 business days following expiration of revocation window.",
                "safer_alternative": None
            }
        ],
        "text": """EXECUTIVE SEPARATION AGREEMENT AND GENERAL RELEASE OF CLAIMS

This Separation Agreement and Release ("Agreement") is entered into as of October 8, 2024, by Lumina Health Systems Corp. ("Company") and Elena Rostova ("Executive").

1. SEPARATION OF EMPLOYMENT
Executive's employment as Chief Technology Officer ceased effective October 8, 2024 ("Separation Date").

2. SEVERANCE CONSIDERATION
In consideration of the general release contained herein, Company shall pay Executive a lump-sum severance payment of $120,000 USD, less applicable withholdings, within fourteen (14) days following the Effective Date. Company shall also reimburse COBRA premiums for six (6) months.

3. COMPLETE GENERAL RELEASE OF CLAIMS
Executive unconditionally releases and discharges Company from all claims, liabilities, demands, and causes of action of any nature arising prior to execution, including claims under ADEA, Title VII, ADA, and state wage laws.

4. NON-DISPARAGEMENT
Executive agrees not to make any disparaging, negative, or uncomplimentary remarks concerning Company, its executives, or clinical services to any third party or media platform.

5. NON-SOLICITATION OF EMPLOYEES
For twelve (12) months following the Separation Date, Executive shall not directly or indirectly recruit, solicit, or induce any Company employee to leave employment."""
    }
]

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow()

    print(f"Connecting to database: {DB_PATH}")
    
    # Check existing documents
    cursor.execute("SELECT filename FROM documents")
    existing_files = set(r[0] for r in cursor.fetchall())

    # Get Gaurav's user_id or first admin id
    cursor.execute("SELECT id FROM users WHERE email = 'gjha5757@gmail.com' LIMIT 1")
    row = cursor.fetchone()
    admin_user_id = row[0] if row else None

    inserted_count = 0

    for item in demo_contracts:
        # Write .txt file to demo_contracts folder
        file_path = os.path.join(CONTRACTS_DIR, item["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(item["text"])
        
        # Calculate date
        created_dt = now - timedelta(days=item["date_offset"], hours=item["date_offset"] * 2)
        created_str = created_dt.isoformat()
        doc_id = str(uuid.uuid4())

        file_size = len(item["text"].encode("utf-8"))

        score_data = {
            "score": item["score"],
            "checklist": [c for c in item["clauses"] if c["risk_level"] in ["Critical", "High"]],
            "all_clauses": item["clauses"]
        }

        # If already in db, delete old version so we replace with polished data
        if item["filename"] in existing_files:
            cursor.execute("DELETE FROM documents WHERE filename = ?", (item["filename"],))

        cursor.execute("""
            INSERT INTO documents (
                id, user_id, filename, file_type, file_size, status, 
                text_content, summary, entities_json, score_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            admin_user_id,
            item["filename"],
            "TXT",
            file_size,
            "analyzed",
            item["text"],
            item["summary"],
            json.dumps(item["entities"]),
            json.dumps(score_data),
            created_str
        ))
        inserted_count += 1

        # Also index into ChromaDB collection so RAG chat responds instantly to questions about this contract
        if rag_service_instance:
            try:
                rag_service_instance.insert_document(doc_id=doc_id, text=item["text"])
            except Exception as e:
                print(f"  [ChromaDB note] {item['filename']}: {e}")

        print(f"  [OK] Seeded: {item['filename']} -> Score: {item['score']} | Date: {created_str[:10]}")

    conn.commit()
    conn.close()
    print(f"\nSuccessfully seeded {inserted_count} demo contracts into {DB_PATH}!")

if __name__ == "__main__":
    seed()
