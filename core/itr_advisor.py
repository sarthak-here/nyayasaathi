"""
ITR Advisor — Recommends the best ITR form and calculates tax liability.
Uses rule-based calculations for accuracy + LLM for personalized filing guidance.
"""

import os
from typing import Optional
import ollama

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

# AY 2025-26 tax slabs
_NEW_SLABS = [(300000, 0.00), (700000, 0.05), (1000000, 0.10),
              (1200000, 0.15), (1500000, 0.20), (float('inf'), 0.30)]

_OLD_SLABS = [(250000, 0.00), (500000, 0.05), (1000000, 0.20),
              (float('inf'), 0.30)]


def _tax_from_slabs(income: float, slabs: list) -> float:
    tax, prev = 0.0, 0
    for limit, rate in slabs:
        if income <= prev:
            break
        tax += (min(income, limit) - prev) * rate
        prev = limit
    return tax


def _calculate_tax(taxable: float, regime: str) -> int:
    if taxable <= 0:
        return 0
    slabs = _NEW_SLABS if regime == "new" else _OLD_SLABS
    tax = _tax_from_slabs(taxable, slabs)
    if regime == "new" and taxable <= 700000:
        tax = 0
    elif regime == "old" and taxable <= 500000:
        tax = 0
    return round(tax * 1.04)


def _select_form(salary, business, capital_gains, total, presumptive, foreign, houses):
    if business > 0 and presumptive and total <= 5_000_000:
        return ("ITR-4 (Sugam)",
                "You have business/professional income under presumptive taxation "
                "(Sec 44AD/44ADA) and total income ≤ ₹50 lakh.")
    if business > 0:
        return ("ITR-3",
                "You have income from a business or profession (non-presumptive).")
    if capital_gains > 0 or total > 5_000_000 or foreign or houses > 1:
        return ("ITR-2",
                "You have capital gains, income from multiple house properties, "
                "foreign income, or total income exceeds ₹50 lakh.")
    return ("ITR-1 (Sahaj)",
            "You have salary/pension and simple other income with total ≤ ₹50 lakh. "
            "This is the easiest form to file.")


# All deduction sections with their rules — used for analysis + LLM context
DEDUCTION_RULES = [
    {
        "section": "80C",
        "name": "Investments & Payments",
        "limit": 150000,
        "instruments": "PPF, ELSS mutual funds, LIC premium, EPF/VPF, NSC, 5-year tax-saving FD, ULIP, tuition fees (2 children), home loan principal repayment, Sukanya Samriddhi",
        "regime": "old_only",
    },
    {
        "section": "80CCD(1B)",
        "name": "NPS — Extra Self Contribution",
        "limit": 50000,
        "instruments": "National Pension System — self contribution (additional ₹50K over and above 80C limit)",
        "regime": "old_only",
    },
    {
        "section": "80CCD(2)",
        "name": "NPS — Employer Contribution",
        "limit": None,
        "instruments": "Employer's contribution to NPS — up to 10% of Basic+DA (no upper cap). Available in BOTH regimes.",
        "regime": "both",
    },
    {
        "section": "80D",
        "name": "Health Insurance Premium",
        "limit": 100000,
        "instruments": "Self/family: ₹25,000 (₹50,000 if self is senior citizen). Parents: ₹25,000 (₹50,000 if senior citizen). Preventive health check-up: ₹5,000 within above limit.",
        "regime": "old_only",
    },
    {
        "section": "80E",
        "name": "Education Loan Interest",
        "limit": None,
        "instruments": "Interest paid on loan for higher education (self, spouse, children, or student for whom you are guardian). No upper limit. Available for 8 years from start of repayment.",
        "regime": "old_only",
    },
    {
        "section": "80EEA",
        "name": "Home Loan — Affordable Housing",
        "limit": 150000,
        "instruments": "Extra ₹1.5L interest deduction for first-time home buyers (stamp duty value ≤ ₹45L, loan sanctioned Apr 2019 – Mar 2022). Over and above Sec 24(b).",
        "regime": "old_only",
    },
    {
        "section": "80G",
        "name": "Donations to NGOs / Charitable Funds",
        "limit": None,
        "instruments": "100% deduction: PM Relief Fund, National Defence Fund, CRY, HelpAge, etc. 50% deduction: Jawaharlal Nehru Memorial Fund, PM Drought Relief Fund, etc. 50% with 10%-of-income cap: approved charitable trusts. Cash donations above ₹2,000 NOT allowed — pay by cheque/UPI/NEFT.",
        "regime": "old_only",
    },
    {
        "section": "80GG",
        "name": "Rent Paid (No HRA in Salary)",
        "limit": 60000,
        "instruments": "If you pay rent but don't receive HRA: deduction = least of (a) ₹5,000/month, (b) 25% of total income, (c) actual rent − 10% of income.",
        "regime": "old_only",
    },
    {
        "section": "80TTA",
        "name": "Savings Account Interest",
        "limit": 10000,
        "instruments": "Interest earned on savings bank account (not FD). Max ₹10,000. For senior citizens: Section 80TTB allows ₹50,000 on all bank/post office deposits.",
        "regime": "old_only",
    },
    {
        "section": "80TTB",
        "name": "Interest Income (Senior Citizens ≥ 60 yrs)",
        "limit": 50000,
        "instruments": "Interest from savings account, FD, RD, post-office deposits. Replaces 80TTA for senior citizens.",
        "regime": "old_only",
    },
    {
        "section": "Sec 24(b)",
        "name": "Home Loan Interest",
        "limit": 200000,
        "instruments": "Interest paid on home loan for self-occupied property — max ₹2L. For let-out property: actual interest (no cap), but loss set-off capped at ₹2L against salary.",
        "regime": "old_only",
    },
    {
        "section": "HRA Exemption",
        "name": "House Rent Allowance",
        "limit": None,
        "instruments": "Least of: (a) actual HRA received, (b) rent paid − 10% of basic salary, (c) 50% of basic (metro) or 40% (non-metro). Salaried employees only.",
        "regime": "old_only",
    },
    {
        "section": "Standard Deduction",
        "name": "Flat Deduction for Salaried",
        "limit": 50000,
        "instruments": "₹50,000 flat deduction for all salaried and pensioners. Available in BOTH old and new regime.",
        "regime": "both",
    },
    {
        "section": "87A Rebate",
        "name": "Tax Rebate",
        "limit": None,
        "instruments": "Old regime: full tax rebate if taxable income ≤ ₹5L. New regime: full tax rebate if taxable income ≤ ₹7L (so zero tax up to ₹7L in new regime).",
        "regime": "both",
    },
]

PORTAL_LINKS = [
    {"name": "e-Filing Portal (File ITR)", "url": "https://eportal.incometax.gov.in"},
    {"name": "Annual Information Statement (AIS)", "url": "https://eportal.incometax.gov.in/iec/foservices/#/dashboard"},
    {"name": "Form 26AS / TRACES", "url": "https://www.tdscpc.gov.in/app/login.xhtml"},
    {"name": "Tax Calculator (Official)", "url": "https://incometaxindia.gov.in/pages/tools/income-tax-calculator.aspx"},
    {"name": "Download ITR-1 (Sahaj) PDF", "url": "https://incometaxindia.gov.in/forms/income-tax%20rules/2024/itr1_english.pdf"},
    {"name": "Download ITR-2 PDF", "url": "https://incometaxindia.gov.in/forms/income-tax%20rules/2024/itr2_english.pdf"},
    {"name": "Download ITR-3 PDF", "url": "https://incometaxindia.gov.in/forms/income-tax%20rules/2024/itr3_english.pdf"},
    {"name": "Download ITR-4 (Sugam) PDF", "url": "https://incometaxindia.gov.in/forms/income-tax%20rules/2024/itr4_english.pdf"},
    {"name": "80G Approved Institutions List", "url": "https://incometaxindia.gov.in/Pages/utilities/donee-search.aspx"},
    {"name": "NPS (National Pension System)", "url": "https://www.npscra.nsdl.co.in/"},
    {"name": "EPF Portal (EPFO)", "url": "https://unifiedportal-mem.epfindia.gov.in/memberinterface/"},
    {"name": "Aadhaar-PAN Link Status", "url": "https://eportal.incometax.gov.in/iec/foservices/#/pre-login/link-aadhaar-status"},
]


def analyze_itr(data: dict) -> dict:
    salary      = float(data.get("salary_income", 0))
    business    = float(data.get("business_income", 0))
    cap_gains   = float(data.get("capital_gains", 0))
    other       = float(data.get("other_income", 0))
    # Old-regime deductions
    d_80c       = min(float(data.get("deduction_80c", 0)), 150_000)
    d_80ccd1b   = min(float(data.get("deduction_80ccd1b", 0)), 50_000)
    d_80d       = min(float(data.get("deduction_80d", 0)), 100_000)
    d_80e       = float(data.get("deduction_80e", 0))          # no limit
    d_80g       = float(data.get("deduction_80g", 0))          # % applied below
    d_80g_pct   = float(data.get("deduction_80g_pct", 50))     # 50 or 100
    d_80tta     = min(float(data.get("deduction_80tta", 0)), 10_000)
    d_80gg      = float(data.get("deduction_80gg", 0))
    hra         = float(data.get("hra_exempt", 0))
    hl_interest = min(float(data.get("home_loan_interest", 0)), 200_000)
    d_80eea     = min(float(data.get("deduction_80eea", 0)), 150_000)
    presumptive = bool(data.get("presumptive_business", False))
    foreign     = bool(data.get("foreign_income", False))
    houses      = int(data.get("house_properties", 1))

    std_deduction = 50_000 if salary > 0 else 0
    total = salary + business + cap_gains + other

    # 80G: 50% or 100% of donated amount, capped at 10% of gross for some categories
    d_80g_effective = round(d_80g * d_80g_pct / 100)

    # Old regime
    old_deductions = (std_deduction + d_80c + d_80ccd1b + d_80d + d_80e
                      + d_80g_effective + d_80tta + d_80gg + hra
                      + hl_interest + d_80eea)
    old_taxable = max(0.0, total - old_deductions)
    old_tax = _calculate_tax(old_taxable, "old")

    # New regime (only std deduction from FY 2024-25)
    new_taxable = max(0.0, total - std_deduction)
    new_tax = _calculate_tax(new_taxable, "new")

    rec_regime = "New" if new_tax <= old_tax else "Old"
    rec_form, form_reason = _select_form(salary, business, cap_gains,
                                          total, presumptive, foreign, houses)

    # Deductions that apply
    applicable_deductions = []
    if std_deduction:
        applicable_deductions.append({"sec": "Standard Deduction", "amt": int(std_deduction), "note": "Flat deduction for salaried/pensioners (both regimes)"})
    if d_80c > 0:
        applicable_deductions.append({"sec": "80C", "amt": int(d_80c), "note": "PPF/ELSS/LIC/EPF/NSC/FD/tuition fees"})
    if d_80ccd1b > 0:
        applicable_deductions.append({"sec": "80CCD(1B)", "amt": int(d_80ccd1b), "note": "NPS self contribution (extra ₹50K over 80C)"})
    if d_80d > 0:
        applicable_deductions.append({"sec": "80D", "amt": int(d_80d), "note": "Health insurance premium"})
    if d_80e > 0:
        applicable_deductions.append({"sec": "80E", "amt": int(d_80e), "note": "Education loan interest (no limit)"})
    if d_80g_effective > 0:
        applicable_deductions.append({"sec": "80G", "amt": int(d_80g_effective), "note": f"Donation deduction ({int(d_80g_pct)}% of ₹{int(d_80g):,} donated)"})
    if d_80tta > 0:
        applicable_deductions.append({"sec": "80TTA", "amt": int(d_80tta), "note": "Savings account interest (max ₹10,000)"})
    if d_80gg > 0:
        applicable_deductions.append({"sec": "80GG", "amt": int(d_80gg), "note": "Rent paid (no HRA in salary)"})
    if hra > 0:
        applicable_deductions.append({"sec": "HRA", "amt": int(hra), "note": "House Rent Allowance exemption"})
    if hl_interest > 0:
        applicable_deductions.append({"sec": "Sec 24(b)", "amt": int(hl_interest), "note": "Home loan interest"})
    if d_80eea > 0:
        applicable_deductions.append({"sec": "80EEA", "amt": int(d_80eea), "note": "Affordable housing loan interest (extra ₹1.5L)"})

    # Unused deduction opportunities (for suggestions)
    unused_opportunities = []
    if d_80c < 150_000:
        unused_opportunities.append(f"80C: You can invest ₹{int(150_000 - d_80c):,} more in PPF/ELSS/LIC to max out this deduction")
    if d_80ccd1b == 0:
        unused_opportunities.append("80CCD(1B): Invest up to ₹50,000 in NPS for extra deduction (over 80C limit)")
    if d_80d == 0:
        unused_opportunities.append("80D: Buy health insurance — deduct up to ₹25,000 (₹50,000 if parents are senior citizens)")
    if d_80g == 0:
        unused_opportunities.append("80G: Donations to PM Relief Fund, CRY, HelpAge India etc. give 50–100% deduction (pay by UPI/cheque, not cash)")
    if d_80e == 0 and business == 0:
        unused_opportunities.append("80E: If you have or plan to take an education loan for higher studies, interest is fully deductible for 8 years")
    if d_80tta == 0 and salary > 0:
        unused_opportunities.append("80TTA: Interest up to ₹10,000 from savings account is deductible — check your bank passbook")

    return {
        "total_income": int(total),
        "recommended_form": rec_form,
        "form_reason": form_reason,
        "recommended_regime": rec_regime,
        "regime_savings": abs(old_tax - new_tax),
        "old_regime": {
            "deductions": int(old_deductions),
            "taxable_income": int(old_taxable),
            "tax": old_tax,
        },
        "new_regime": {
            "deductions": int(std_deduction),
            "taxable_income": int(new_taxable),
            "tax": new_tax,
        },
        "applicable_deductions": applicable_deductions,
        "unused_opportunities": unused_opportunities,
        "deduction_rules": DEDUCTION_RULES,
        "portal_links": PORTAL_LINKS,
    }


def get_filing_guidance(data: dict, analysis: dict) -> str:
    ded_summary = "\n".join(
        f"  - {d['sec']}: ₹{d['amt']:,} ({d['note']})"
        for d in analysis["applicable_deductions"]
    ) or "  - None entered"

    unused = "\n".join(f"  - {u}" for u in analysis["unused_opportunities"]) or "  - None"

    all_sections = "\n".join(
        f"  [{r['section']}] {r['name']} — limit: {'₹'+str(r['limit']) if r['limit'] else 'No limit'} — {r['instruments'][:80]}"
        for r in DEDUCTION_RULES
    )

    prompt = f"""You are an expert Indian income tax advisor for AY 2025-26. A taxpayer has the following profile:

INCOME:
- Salary: ₹{int(data.get('salary_income',0)):,}
- Business/Freelance: ₹{int(data.get('business_income',0)):,}
- Capital Gains: ₹{int(data.get('capital_gains',0)):,}
- Other Income: ₹{int(data.get('other_income',0)):,}
- Total Gross Income: ₹{analysis['total_income']:,}

TAX ANALYSIS:
- Recommended ITR Form: {analysis['recommended_form']}
- Best Regime: {analysis['recommended_regime']} Tax Regime (saves ₹{analysis['regime_savings']:,})
- Old Regime Tax: ₹{analysis['old_regime']['tax']:,} (after ₹{analysis['old_regime']['deductions']:,} deductions)
- New Regime Tax: ₹{analysis['new_regime']['tax']:,} (after ₹50,000 standard deduction)

DEDUCTIONS ALREADY ENTERED:
{ded_summary}

UNUSED TAX-SAVING OPPORTUNITIES DETECTED:
{unused}

ALL AVAILABLE DEDUCTION SECTIONS (reference for your advice):
{all_sections}

Give a practical, India-specific response with these sections:

### 1. Why {analysis['recommended_form']}
One short paragraph.

### 2. Step-by-Step Filing on incometax.gov.in
6 numbered steps.

### 3. Documents Checklist
Bullet list of exactly what this taxpayer needs.

### 4. Top Tax-Saving Actions (before July 31)
List 3-5 specific actions this taxpayer can take RIGHT NOW to reduce their tax — reference actual section numbers, amounts, and instruments. If they donated to an NGO, explain how to claim 80G. Be specific.

### 5. Important Deadlines & Penalties
Keep to 2 bullet points.

Be concise and practical. Max 450 words. Use ₹ symbol for all amounts."""

    try:
        resp = ollama.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False)
        return resp.get("response", "").strip()
    except Exception:
        return (
            "**Filing Steps:** 1) Login to eportal.incometax.gov.in. "
            "2) Go to e-File → Income Tax Returns → File ITR. "
            f"3) Select AY 2025-26 and {analysis['recommended_form'].split()[0]}. "
            "4) Verify pre-filled data from Form 26AS and AIS. "
            "5) Choose your tax regime and enter deductions. "
            "6) E-verify using Aadhaar OTP within 30 days. "
            "**Deadline:** July 31, 2025."
        )


def full_itr_analysis(data: dict) -> dict:
    analysis = analyze_itr(data)
    analysis["guidance"] = get_filing_guidance(data, analysis)
    return analysis
