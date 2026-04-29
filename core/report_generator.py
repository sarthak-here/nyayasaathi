"""
Report Generator — Generates structured complaints, FIRs, and official reports.
Covers FIR, consumer complaint, cyber crime, labour, RTI, RERA, banking, insurance,
medical negligence, POSH, electricity, and railway complaints.
"""

import os
import ollama

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

REPORT_TYPES = {
    "fir": {
        "label": "FIR / Police Complaint",
        "icon": "fa-shield-halved",
        "color": "#ef4444",
        "desc": "File a First Information Report for crimes — assault, theft, fraud, threats, etc.",
        "authority": "Nearest Police Station (file in person or at citizen.mahapolice.gov.in / state police portal)",
        "laws": ["BNS 2023 (Bharatiya Nyaya Sanhita)", "BNSS 2023 (Criminal Procedure)", "Section 173 BNSS — Right to register FIR"],
        "helplines": ["Police: 100", "Women helpline: 1091", "Emergency: 112"],
        "fields": [
            {"id": "complainant_name", "label": "Your Full Name", "type": "text", "placeholder": "As per Aadhaar"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Full address with PIN"},
            {"id": "complainant_phone", "label": "Your Phone Number", "type": "tel", "placeholder": "10-digit mobile"},
            {"id": "incident_date", "label": "Date of Incident", "type": "date"},
            {"id": "incident_time", "label": "Time of Incident", "type": "text", "placeholder": "e.g. 9:30 PM"},
            {"id": "incident_location", "label": "Location of Incident", "type": "text", "placeholder": "Full address / landmark"},
            {"id": "incident_type", "label": "Nature of Offence", "type": "select", "options": [
                "Theft / Robbery", "Assault / Physical Attack", "Fraud / Cheating",
                "Harassment / Intimidation", "Cybercrime / Online Fraud", "Domestic Violence",
                "Kidnapping / Missing Person", "Murder / Attempt to Murder", "Rape / Sexual Assault",
                "Property Damage", "Stalking", "Other"
            ]},
            {"id": "accused_details", "label": "Accused Person(s) Details", "type": "textarea", "placeholder": "Name, address, description (if known). Write 'Unknown' if not known."},
            {"id": "incident_description", "label": "Detailed Description of Incident", "type": "textarea", "placeholder": "Describe exactly what happened, in chronological order"},
            {"id": "witnesses", "label": "Witnesses (if any)", "type": "text", "placeholder": "Name and contact of witnesses, or 'None'"},
            {"id": "evidence", "label": "Evidence Available", "type": "text", "placeholder": "Photos, CCTV, messages, receipts, etc."},
            {"id": "relief_sought", "label": "Relief / Action Sought", "type": "text", "placeholder": "e.g. Arrest of accused, recovery of property"},
        ],
    },
    "consumer": {
        "label": "Consumer Complaint",
        "icon": "fa-cart-shopping",
        "color": "#f59e0b",
        "desc": "Defective product, service deficiency, unfair trade practice, e-commerce fraud.",
        "authority": "District Consumer Commission (for claims up to ₹50L) — file at edaakhil.gov.in",
        "laws": ["Consumer Protection Act 2019", "Section 35 — Filing complaint", "Section 2(7) — Who is a consumer"],
        "helplines": ["National Consumer Helpline: 1800-11-4000", "consumerhelpline.gov.in", "edaakhil.gov.in (online filing)"],
        "fields": [
            {"id": "complainant_name", "label": "Your Full Name", "type": "text", "placeholder": "As per ID"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Full address with PIN"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Mobile and email"},
            {"id": "company_name", "label": "Company / Seller Name", "type": "text", "placeholder": "e.g. Flipkart Internet Pvt Ltd"},
            {"id": "company_address", "label": "Company Address", "type": "text", "placeholder": "Registered address of company"},
            {"id": "product_service", "label": "Product / Service", "type": "text", "placeholder": "e.g. Samsung Galaxy S24, Home loan, Insurance policy"},
            {"id": "purchase_date", "label": "Date of Purchase / Transaction", "type": "date"},
            {"id": "amount_paid", "label": "Amount Paid (₹)", "type": "number", "placeholder": "0"},
            {"id": "complaint_type", "label": "Nature of Complaint", "type": "select", "options": [
                "Defective product", "Service deficiency", "Unfair trade practice",
                "Overcharging / hidden charges", "Non-delivery of order", "Refund not given",
                "Misleading advertisement", "Warranty / guarantee denial", "Other"
            ]},
            {"id": "incident_description", "label": "Detailed Description", "type": "textarea", "placeholder": "What exactly happened? What defect / issue did you face?"},
            {"id": "steps_taken", "label": "Steps Already Taken", "type": "textarea", "placeholder": "Did you contact customer care? Send email? What was their response?"},
            {"id": "relief_sought", "label": "Relief Sought", "type": "text", "placeholder": "e.g. Full refund of ₹12,000 + compensation of ₹5,000 + cost of complaint"},
        ],
    },
    "cybercrime": {
        "label": "Cyber Crime Report",
        "icon": "fa-bug-slash",
        "color": "#8b5cf6",
        "desc": "UPI fraud, phishing, online scam, hacking, identity theft, sextortion.",
        "authority": "cybercrime.gov.in (National Cyber Crime Reporting Portal) | Call 1930",
        "laws": ["IT Act 2000 — Sections 43, 65, 66, 66C, 66D, 67", "BNS 2023 — Section 318 (Cheating)", "PMLA 2002 (for money laundering)"],
        "helplines": ["Cyber Crime Helpline: 1930", "cybercrime.gov.in", "Email: cybercrime@nic.in"],
        "fields": [
            {"id": "complainant_name", "label": "Your Full Name", "type": "text", "placeholder": "As per Aadhaar"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Your contact details"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Full address with PIN"},
            {"id": "crime_type", "label": "Type of Cyber Crime", "type": "select", "options": [
                "UPI / Bank fraud (money stolen)", "Phishing / Fake call / Vishing",
                "Online shopping fraud", "Social media account hacked",
                "Sextortion / Blackmail with private photos", "Investment / Crypto scam",
                "Job / Loan fraud", "Identity theft / Aadhaar misuse",
                "Ransomware / Hacking", "Child pornography (CSAM)", "Other"
            ]},
            {"id": "incident_date", "label": "Date of Incident", "type": "date"},
            {"id": "platform", "label": "Platform / Website / App", "type": "text", "placeholder": "e.g. WhatsApp, Instagram, Amazon, UPI app name"},
            {"id": "amount_lost", "label": "Amount Lost (₹, if any)", "type": "number", "placeholder": "0"},
            {"id": "transaction_ids", "label": "Transaction IDs / UTR Numbers", "type": "text", "placeholder": "UPI transaction ID, bank reference numbers"},
            {"id": "accused_details", "label": "Accused / Suspect Details", "type": "text", "placeholder": "Phone number, email, website, account number of fraudster (if known)"},
            {"id": "incident_description", "label": "Detailed Description", "type": "textarea", "placeholder": "Exactly what happened? How were you contacted? What did they say? What did you do?"},
            {"id": "evidence", "label": "Evidence Available", "type": "text", "placeholder": "Screenshots, call recordings, emails, bank statements, chat history"},
        ],
    },
    "labour": {
        "label": "Labour / Employment Complaint",
        "icon": "fa-hammer",
        "color": "#0ea5e9",
        "desc": "Unpaid wages, wrongful termination, EPF not deposited, no payslip, illegal deductions.",
        "authority": "Labour Commissioner / Inspector | EPFO Grievance Portal | Labour Court",
        "laws": ["Payment of Wages Act 1936", "Industrial Disputes Act 1947", "EPF & MP Act 1952", "Minimum Wages Act 1948", "Gratuity Act 1972"],
        "helplines": ["Labour Helpline: 14434", "epfigms.gov.in (EPF grievance)", "shramsuvidha.gov.in"],
        "fields": [
            {"id": "complainant_name", "label": "Your Full Name", "type": "text", "placeholder": "As per employment records"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Current residential address"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Contact details"},
            {"id": "employer_name", "label": "Employer / Company Name", "type": "text", "placeholder": "Full registered name"},
            {"id": "employer_address", "label": "Employer Address", "type": "text", "placeholder": "Office / factory address"},
            {"id": "designation", "label": "Your Designation / Job Role", "type": "text", "placeholder": "e.g. Sales Executive, Factory Worker"},
            {"id": "employment_period", "label": "Employment Period", "type": "text", "placeholder": "e.g. 12 Jan 2022 to 30 Mar 2025"},
            {"id": "monthly_salary", "label": "Monthly Salary (₹)", "type": "number", "placeholder": "0"},
            {"id": "complaint_type", "label": "Nature of Complaint", "type": "select", "options": [
                "Unpaid salary / wages", "Wrongful termination / illegal dismissal",
                "EPF not deposited", "Gratuity not paid", "No payslip / appointment letter",
                "Illegal salary deductions", "Maternity benefit denied",
                "Below minimum wage", "Forced overtime without pay", "Other"
            ]},
            {"id": "amount_owed", "label": "Amount Owed (₹)", "type": "number", "placeholder": "0"},
            {"id": "incident_description", "label": "Detailed Description", "type": "textarea", "placeholder": "What happened? Since when? What did employer say when you asked?"},
            {"id": "steps_taken", "label": "Steps Already Taken", "type": "text", "placeholder": "Verbal complaint, written notice, HR email, etc."},
            {"id": "relief_sought", "label": "Relief Sought", "type": "text", "placeholder": "e.g. Payment of ₹45,000 pending wages + reinstatement"},
        ],
    },
    "rti": {
        "label": "RTI Application",
        "icon": "fa-file-lines",
        "color": "#10b981",
        "desc": "Request information from any government department, PSU, or public authority.",
        "authority": "Public Information Officer (PIO) of the concerned department | rtionline.gov.in",
        "laws": ["Right to Information Act 2005", "Section 6 — Filing application", "Section 7 — 30-day response deadline", "Section 19 — First appeal"],
        "helplines": ["RTI Portal: rtionline.gov.in", "Fee: ₹10 (free for BPL)", "Response time: 30 days"],
        "fields": [
            {"id": "complainant_name", "label": "Your Full Name", "type": "text", "placeholder": "As per Aadhaar"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Full postal address"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Contact details"},
            {"id": "department_name", "label": "Public Authority / Department", "type": "text", "placeholder": "e.g. Municipal Corporation of Delhi, Ministry of Railways"},
            {"id": "department_address", "label": "Address of Department", "type": "text", "placeholder": "Office address of PIO"},
            {"id": "subject", "label": "Subject / Topic of Information", "type": "text", "placeholder": "e.g. Status of road repair work in Ward No. 12"},
            {"id": "info_sought", "label": "Information Sought (be specific)", "type": "textarea", "placeholder": "List each piece of information as a numbered point. Be precise — vague RTIs get rejected."},
            {"id": "period", "label": "Time Period of Information", "type": "text", "placeholder": "e.g. Financial year 2023-24, or last 3 years"},
            {"id": "reason", "label": "Reason / Background (optional)", "type": "text", "placeholder": "RTI doesn't require a reason, but brief context helps"},
            {"id": "bpl_status", "label": "Are you BPL (Below Poverty Line)?", "type": "select", "options": ["No — I will pay ₹10 fee", "Yes — BPL card holder (attach copy, fee waived)"]},
        ],
    },
    "banking": {
        "label": "Banking / RBI Ombudsman Complaint",
        "icon": "fa-building-columns",
        "color": "#6366f1",
        "desc": "Bank fraud, loan harassment, wrongful charges, ATM issues, recovery agent misconduct.",
        "authority": "RBI Banking Ombudsman — cms.rbi.org.in | Bank's internal grievance first",
        "laws": ["Banking Regulation Act 1949", "RBI Guidelines on Customer Service", "SARFAESI Act 2002", "Section 138 NI Act (cheque bounce)"],
        "helplines": ["RBI Ombudsman: cms.rbi.org.in", "RBI Helpline: 14448", "Bank grievance portal (check your bank's app)"],
        "fields": [
            {"id": "complainant_name", "label": "Your Full Name", "type": "text", "placeholder": "As per bank records"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Full address with PIN"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Registered with bank"},
            {"id": "bank_name", "label": "Bank Name & Branch", "type": "text", "placeholder": "e.g. HDFC Bank, Connaught Place Branch, Delhi"},
            {"id": "account_number", "label": "Account / Loan Number (last 4 digits)", "type": "text", "placeholder": "XXXX1234"},
            {"id": "complaint_type", "label": "Nature of Complaint", "type": "select", "options": [
                "Unauthorised / fraudulent transaction", "ATM cash not dispensed but debited",
                "Loan recovery agent harassment", "Wrong charges / hidden fees",
                "Account frozen without notice", "Cheque bounce dispute",
                "Credit card fraud", "Net banking hacked", "Home/vehicle loan dispute",
                "Fixed deposit not paid on maturity", "Other"
            ]},
            {"id": "incident_date", "label": "Date of Incident", "type": "date"},
            {"id": "amount_involved", "label": "Amount Involved (₹)", "type": "number", "placeholder": "0"},
            {"id": "incident_description", "label": "Detailed Description", "type": "textarea", "placeholder": "What exactly happened? What did the bank do or fail to do?"},
            {"id": "bank_response", "label": "Bank's Response So Far", "type": "textarea", "placeholder": "Did you complain to bank? What did they say? When? (Must complain to bank first before RBI)"},
            {"id": "relief_sought", "label": "Relief Sought", "type": "text", "placeholder": "e.g. Refund of ₹15,000 + interest + compensation"},
        ],
    },
    "rera": {
        "label": "RERA / Real Estate Complaint",
        "icon": "fa-building",
        "color": "#f97316",
        "desc": "Builder delay, possession not given, quality defects, misleading brochure, refund denied.",
        "authority": "State RERA Authority — check your state's RERA portal (e.g. maharera.mahaonline.gov.in)",
        "laws": ["Real Estate (Regulation & Development) Act 2016", "Section 18 — Delay compensation", "Section 31 — Filing complaint", "Section 12 — False advertisement"],
        "helplines": ["Central RERA: rera.gov.in", "Each state has its own RERA portal", "No court fee for RERA complaints"],
        "fields": [
            {"id": "complainant_name", "label": "Your Full Name", "type": "text", "placeholder": "As per agreement"},
            {"id": "complainant_address", "label": "Your Current Address", "type": "text", "placeholder": "Full address with PIN"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Contact details"},
            {"id": "builder_name", "label": "Builder / Promoter Name", "type": "text", "placeholder": "Full registered name of builder"},
            {"id": "project_name", "label": "Project / Society Name", "type": "text", "placeholder": "Name of the housing project"},
            {"id": "project_address", "label": "Project Location", "type": "text", "placeholder": "Address of the property"},
            {"id": "rera_number", "label": "RERA Registration Number", "type": "text", "placeholder": "Builder's RERA registration no. (from brochure / RERA portal)"},
            {"id": "flat_details", "label": "Flat / Unit Details", "type": "text", "placeholder": "Flat no., tower, carpet area"},
            {"id": "agreement_date", "label": "Date of Agreement / Booking", "type": "date"},
            {"id": "amount_paid", "label": "Total Amount Paid (₹)", "type": "number", "placeholder": "0"},
            {"id": "promised_possession", "label": "Promised Possession Date", "type": "date"},
            {"id": "complaint_type", "label": "Nature of Complaint", "type": "select", "options": [
                "Possession not given on time", "Construction quality defects",
                "Specification mismatch (different from brochure)", "Common amenities not provided",
                "Refund with interest not given", "False / misleading advertisement",
                "Carpet area less than promised", "Other"
            ]},
            {"id": "incident_description", "label": "Detailed Description", "type": "textarea", "placeholder": "What exactly did the builder promise vs what they delivered?"},
            {"id": "relief_sought", "label": "Relief Sought", "type": "text", "placeholder": "e.g. Possession within 3 months + delay compensation + penalty"},
        ],
    },
    "medical": {
        "label": "Medical Negligence Complaint",
        "icon": "fa-user-doctor",
        "color": "#ec4899",
        "desc": "Wrong treatment, misdiagnosis, surgical error, hospital overcharging, drug error.",
        "authority": "State Medical Council (for doctor misconduct) | Consumer Commission (for compensation) | NMC",
        "laws": ["Indian Medical Council Act 1956", "Consumer Protection Act 2019 (medical = service)", "BNS 2023 — Section 106 (death by negligence)", "Clinical Establishments Act 2010"],
        "helplines": ["National Medical Commission: nmc.org.in", "Consumer Helpline: 1800-11-4000", "State Medical Council (state-wise)"],
        "fields": [
            {"id": "complainant_name", "label": "Patient / Complainant Name", "type": "text", "placeholder": "Name of patient or next of kin"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Full address with PIN"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Contact details"},
            {"id": "doctor_name", "label": "Doctor's Name & Qualification", "type": "text", "placeholder": "e.g. Dr. Raj Mehta, MS Surgery"},
            {"id": "hospital_name", "label": "Hospital / Clinic Name & Address", "type": "text", "placeholder": "Full name and address of hospital"},
            {"id": "treatment_period", "label": "Date(s) of Treatment", "type": "text", "placeholder": "e.g. 12 Jan 2025 to 20 Jan 2025"},
            {"id": "complaint_type", "label": "Nature of Negligence", "type": "select", "options": [
                "Wrong diagnosis", "Wrong surgery / wrong site surgery",
                "Wrong medication / dosage error", "Delay in treatment causing harm",
                "Lack of informed consent", "Post-surgical complication due to negligence",
                "Death due to negligence", "Hospital overcharging", "Discharge against will",
                "Refusal to treat emergency patient", "Other"
            ]},
            {"id": "amount_paid", "label": "Total Amount Paid to Hospital (₹)", "type": "number", "placeholder": "0"},
            {"id": "incident_description", "label": "Detailed Description of Negligence", "type": "textarea", "placeholder": "What treatment was received? What went wrong? What harm was caused?"},
            {"id": "evidence", "label": "Medical Evidence Available", "type": "text", "placeholder": "Prescriptions, discharge summary, test reports, bills, death certificate (if applicable)"},
            {"id": "relief_sought", "label": "Relief Sought", "type": "text", "placeholder": "e.g. Compensation of ₹10L + disciplinary action against doctor"},
        ],
    },
    "posh": {
        "label": "POSH / Workplace Harassment",
        "icon": "fa-person-harassed",
        "color": "#e11d48",
        "desc": "Sexual harassment at workplace — complaint to Internal Complaints Committee (ICC).",
        "authority": "ICC of your organisation | Local Complaints Committee (District Collector office if no ICC)",
        "laws": ["POSH Act 2013 (Sexual Harassment of Women at Workplace Act)", "Section 4 — ICC mandatory for 10+ employees", "Section 9 — Filing complaint within 3 months"],
        "helplines": ["SHe-Box Portal: shebox.wcd.gov.in", "Women Helpline: 181", "NCW: ncw.nic.in"],
        "fields": [
            {"id": "complainant_name", "label": "Your Name", "type": "text", "placeholder": "Full name (can request confidentiality)"},
            {"id": "complainant_designation", "label": "Your Designation & Department", "type": "text", "placeholder": "e.g. Software Engineer, IT Department"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Contact details"},
            {"id": "organisation_name", "label": "Organisation / Company Name", "type": "text", "placeholder": "Full name and address of employer"},
            {"id": "accused_name", "label": "Accused Person's Name & Designation", "type": "text", "placeholder": "Full name and position of accused"},
            {"id": "relationship", "label": "Relationship to Accused", "type": "select", "options": [
                "Senior / Manager / Supervisor", "Colleague (same level)",
                "Subordinate", "Client / Vendor", "Other"
            ]},
            {"id": "incident_dates", "label": "Date(s) of Incident(s)", "type": "text", "placeholder": "First incident date to last incident date"},
            {"id": "incident_location", "label": "Location of Incident(s)", "type": "text", "placeholder": "Office, client site, video call, company event, etc."},
            {"id": "complaint_type", "label": "Nature of Harassment", "type": "select", "options": [
                "Unwelcome physical contact", "Sexually coloured remarks / jokes",
                "Showing pornographic material", "Sexual favours demanded for job benefits",
                "Stalking / following at workplace", "Sending inappropriate messages / emails",
                "Hostile work environment due to gender", "Other"
            ]},
            {"id": "incident_description", "label": "Detailed Description", "type": "textarea", "placeholder": "Describe each incident — date, location, exactly what happened, what was said or done"},
            {"id": "witnesses", "label": "Witnesses", "type": "text", "placeholder": "Names of anyone who witnessed the incidents"},
            {"id": "evidence", "label": "Evidence Available", "type": "text", "placeholder": "Messages, emails, call logs, CCTV, colleagues who can testify"},
            {"id": "previous_complaints", "label": "Previous Complaints Filed", "type": "text", "placeholder": "Did you report to HR / manager earlier? What was the response?"},
        ],
    },
    "insurance": {
        "label": "Insurance Complaint",
        "icon": "fa-umbrella",
        "color": "#0891b2",
        "desc": "Claim rejected, policy mis-selling, delay in settlement, premium dispute.",
        "authority": "IRDAI Bima Bharosa Portal — bimabharosa.irdai.gov.in | Insurer's grievance cell first",
        "laws": ["Insurance Act 1938", "IRDAI (Protection of Policyholders' Interests) Regulations 2017", "Consumer Protection Act 2019"],
        "helplines": ["IRDAI Helpline: 155255 / 1800-4254-732", "bimabharosa.irdai.gov.in", "Insurance Ombudsman (state-wise)"],
        "fields": [
            {"id": "complainant_name", "label": "Policyholder Name", "type": "text", "placeholder": "As per policy"},
            {"id": "complainant_address", "label": "Your Address", "type": "text", "placeholder": "Full address with PIN"},
            {"id": "complainant_phone", "label": "Phone / Email", "type": "text", "placeholder": "Registered contact"},
            {"id": "insurer_name", "label": "Insurance Company Name", "type": "text", "placeholder": "e.g. LIC of India, Star Health Insurance"},
            {"id": "policy_number", "label": "Policy Number", "type": "text", "placeholder": "Policy / claim reference number"},
            {"id": "policy_type", "label": "Type of Insurance", "type": "select", "options": [
                "Life Insurance", "Health / Mediclaim", "Motor Insurance",
                "Home / Property Insurance", "Travel Insurance", "Other"
            ]},
            {"id": "complaint_type", "label": "Nature of Complaint", "type": "select", "options": [
                "Claim rejected / repudiated", "Claim underpaid",
                "Delay in claim settlement (beyond 30 days)", "Policy mis-sold (wrong product explained)",
                "Premium charged incorrectly", "Policy cancelled without notice",
                "Agent fraud / forged signature", "Other"
            ]},
            {"id": "claim_amount", "label": "Claim Amount (₹)", "type": "number", "placeholder": "0"},
            {"id": "incident_description", "label": "Detailed Description", "type": "textarea", "placeholder": "What happened? What reason did the insurer give for rejection/underpayment?"},
            {"id": "insurer_response", "label": "Insurer's Response So Far", "type": "textarea", "placeholder": "What did the insurance company say? Any written reply? (Must complain to insurer first)"},
            {"id": "relief_sought", "label": "Relief Sought", "type": "text", "placeholder": "e.g. Full claim payment of ₹2,50,000 + interest + compensation"},
        ],
    },
}


def generate_report(report_type: str, data: dict) -> dict:
    rtype = REPORT_TYPES.get(report_type)
    if not rtype:
        raise ValueError(f"Unknown report type: {report_type}")

    fields_text = "\n".join(
        f"  {k.replace('_', ' ').title()}: {v}"
        for k, v in data.items()
        if v and k not in ("report_type",)
    )

    laws_text = "\n".join(f"  - {l}" for l in rtype["laws"])
    helplines_text = "\n".join(f"  - {h}" for h in rtype["helplines"])

    prompt = f"""You are an expert Indian legal document drafter. Generate a formal, structured {rtype['label']} based on the details below.

REPORT TYPE: {rtype['label']}
FILING AUTHORITY: {rtype['authority']}
APPLICABLE LAWS:
{laws_text}

COMPLAINANT / INCIDENT DETAILS:
{fields_text}

Write a complete, formal {rtype['label']} document with these sections:

1. **TO** — addressed to the correct authority
2. **SUBJECT** — one-line subject
3. **RESPECTFUL SUBMISSION** — opening formal paragraph
4. **FACTS OF THE CASE** — numbered chronological facts
5. **APPLICABLE LAWS / SECTIONS** — which laws apply and why
6. **RELIEF SOUGHT** — numbered list of specific reliefs requested
7. **DECLARATION** — standard declaration of truth
8. **CLOSING** — "Yours faithfully" + blank for signature and date

Rules:
- Use formal legal language with Indian legal conventions
- Reference specific section numbers of applicable laws
- Be specific — include dates, amounts, names from the details provided
- Make it ready to submit as-is (no [PLACEHOLDER] blanks except for signature)
- Do not add any preamble or explanation outside the document itself
- Max 600 words"""

    try:
        resp = ollama.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False)
        report_text = resp.get("response", "").strip()
    except Exception:
        report_text = _fallback_report(report_type, data, rtype)

    return {
        "report_type": report_type,
        "report_label": rtype["label"],
        "authority": rtype["authority"],
        "laws": rtype["laws"],
        "helplines": rtype["helplines"],
        "report_text": report_text,
    }


def _fallback_report(report_type: str, data: dict, rtype: dict) -> str:
    name = data.get("complainant_name", "The Complainant")
    addr = data.get("complainant_address", "")
    desc = data.get("incident_description", "As described in the attached supporting documents.")
    relief = data.get("relief_sought", "Appropriate action as per law.")
    return f"""TO,
The Concerned Authority,
{rtype['authority']}

SUBJECT: {rtype['label']} — {data.get('complaint_type', data.get('incident_type', 'Complaint'))}

Respected Sir/Madam,

I, {name}, residing at {addr}, hereby submit this formal {rtype['label']} for your kind consideration and necessary action.

FACTS OF THE CASE:
1. {desc}

APPLICABLE LAWS:
{chr(10).join('- ' + l for l in rtype['laws'])}

RELIEF SOUGHT:
1. {relief}
2. Initiate appropriate legal proceedings as per applicable law.
3. Keep the complainant informed of action taken.

DECLARATION:
I hereby declare that the information provided above is true and correct to the best of my knowledge and belief.

Yours faithfully,

{name}
{addr}
Date: ___________
Signature: ___________"""


def get_report_types_list():
    return [
        {
            "id": k,
            "label": v["label"],
            "icon": v["icon"],
            "color": v["color"],
            "desc": v["desc"],
        }
        for k, v in REPORT_TYPES.items()
    ]


def get_report_type_fields(report_type: str):
    rtype = REPORT_TYPES.get(report_type)
    if not rtype:
        return None
    return {
        "fields": rtype["fields"],
        "authority": rtype["authority"],
        "laws": rtype["laws"],
        "helplines": rtype["helplines"],
    }
