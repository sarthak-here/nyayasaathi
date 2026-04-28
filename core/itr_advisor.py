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
    # 87A rebate
    if regime == "new" and taxable <= 700000:
        tax = 0
    elif regime == "old" and taxable <= 500000:
        tax = 0
    # 4% Health & Education cess
    return round(tax * 1.04)


def _select_form(salary: float, business: float, capital_gains: float,
                 total: float, presumptive: bool, foreign: bool, houses: int) -> tuple:
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


def analyze_itr(data: dict) -> dict:
    salary      = float(data.get("salary_income", 0))
    business    = float(data.get("business_income", 0))
    cap_gains   = float(data.get("capital_gains", 0))
    other       = float(data.get("other_income", 0))
    d_80c       = min(float(data.get("deduction_80c", 0)), 150_000)
    d_80d       = min(float(data.get("deduction_80d", 0)), 50_000)
    hra         = float(data.get("hra_exempt", 0))
    hl_interest = min(float(data.get("home_loan_interest", 0)), 200_000)
    presumptive = bool(data.get("presumptive_business", False))
    foreign     = bool(data.get("foreign_income", False))
    houses      = int(data.get("house_properties", 1))

    std_deduction = 50_000 if salary > 0 else 0
    total = salary + business + cap_gains + other

    # Old regime
    old_deductions = std_deduction + d_80c + d_80d + hra + hl_interest
    old_taxable = max(0.0, total - old_deductions)
    old_tax = _calculate_tax(old_taxable, "old")

    # New regime (only std deduction from FY 2024-25)
    new_taxable = max(0.0, total - std_deduction)
    new_tax = _calculate_tax(new_taxable, "new")

    rec_regime = "New" if new_tax <= old_tax else "Old"
    rec_form, form_reason = _select_form(salary, business, cap_gains,
                                          total, presumptive, foreign, houses)

    applicable_deductions = []
    if d_80c > 0:
        applicable_deductions.append(f"Section 80C — ₹{int(d_80c):,} (PPF/ELSS/LIC etc.)")
    if d_80d > 0:
        applicable_deductions.append(f"Section 80D — ₹{int(d_80d):,} (Health Insurance)")
    if hra > 0:
        applicable_deductions.append(f"HRA Exemption — ₹{int(hra):,}")
    if hl_interest > 0:
        applicable_deductions.append(f"Sec 24(b) Home Loan Interest — ₹{int(hl_interest):,}")
    if std_deduction:
        applicable_deductions.append(f"Standard Deduction — ₹{int(std_deduction):,}")

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
    }


def get_filing_guidance(data: dict, analysis: dict) -> str:
    prompt = f"""You are an expert Indian income tax advisor (AY 2025-26).
Given the taxpayer profile below, provide a concise response with:

1. **Why {analysis['recommended_form']}** — 2 sentences
2. **Step-by-step filing guide** (6 numbered steps) on incometax.gov.in
3. **Documents needed** — bullet list (keep it short, 5-6 items)
4. **Deadline reminder** — July 31, 2025 for non-audit cases
5. **One money-saving tip** specific to their situation

Taxpayer:
- Salary: ₹{int(data.get('salary_income',0)):,}  Business: ₹{int(data.get('business_income',0)):,}
- Capital Gains: ₹{int(data.get('capital_gains',0)):,}  Other: ₹{int(data.get('other_income',0)):,}
- Total Income: ₹{analysis['total_income']:,}
- Recommended Form: {analysis['recommended_form']}
- Best Regime: {analysis['recommended_regime']} (saves ₹{analysis['regime_savings']:,} vs the other)
- Old Regime Tax: ₹{analysis['old_regime']['tax']:,}  New Regime Tax: ₹{analysis['new_regime']['tax']:,}

Be practical and India-specific. Max 350 words."""

    try:
        resp = ollama.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False)
        return resp.get("response", "").strip()
    except Exception:
        return (
            "Step-by-step guide: 1) Login to incometax.gov.in with PAN/Aadhaar. "
            "2) Go to e-File → Income Tax Returns → File ITR. "
            f"3) Select AY 2025-26 and Form {analysis['recommended_form'].split()[0]}. "
            "4) Pre-fill data from Form 26AS and AIS — verify it carefully. "
            "5) Enter any remaining income and choose your tax regime. "
            "6) E-verify using Aadhaar OTP within 30 days. "
            "Deadline: July 31, 2025."
        )


def full_itr_analysis(data: dict) -> dict:
    analysis = analyze_itr(data)
    analysis["guidance"] = get_filing_guidance(data, analysis)
    return analysis
