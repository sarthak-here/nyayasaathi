"""
NyayaSaathi — Complaint Letter Generator
Drafts formal Indian legal complaint letters using Gemma 4.
"""

import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

LETTER_SYSTEM_PROMPT = """You are a legal drafting assistant specializing in formal Indian legal complaint letters.

Draft a formal complaint letter following standard Indian legal format. The letter must be:
- Professional and formal in tone
- Factually precise — only use the facts given, do NOT invent details
- Legally grounded — cite the specific Act and Sections provided
- Actionable — include a clear Prayer/Relief section
- Structured in the standard Indian complaint letter format

Format the letter exactly as follows:
[City], [Date]

To,
[Recipient Name/Designation]
[Recipient Address]

Subject: [Clear, specific subject line]

Sir/Madam,

1. FACTS OF THE CASE:
[Numbered factual paragraphs]

2. LEGAL BASIS:
[The applicable law and sections]

3. PRAYER/RELIEF SOUGHT:
[Numbered list of reliefs requested]

I therefore pray that you may kindly take appropriate action in the matter.

Thanking you,

Yours faithfully,

[Complainant Name]
[Address]
[Phone]
[Date]

Do not add any commentary or explanation outside the letter. Output only the letter."""


def generate_letter(
    situation: str,
    user_name: str,
    user_address: str,
    user_phone: str,
    respondent: str,
    respondent_address: str,
    legal_analysis: dict,
) -> str:
    """
    Draft a formal complaint letter using Gemma 4.

    Args:
        situation: User's description of the problem
        user_name: Full name of complainant
        user_address: Address of complainant
        user_phone: Phone number of complainant
        respondent: Name/entity being complained against
        respondent_address: Address of respondent
        legal_analysis: Dict from LegalAgent.analyze() with applicable_law, etc.

    Returns:
        The complaint letter as a formatted string.
    """
    import ollama
    from datetime import date

    today = date.today().strftime("%B %d, %Y")
    applicable_law = legal_analysis.get("applicable_law", "Relevant Indian law")
    letter_recipient = legal_analysis.get("letter_recipient", respondent)
    recommended_action = legal_analysis.get("recommended_action", "")

    prompt = f"""Draft a formal complaint letter with these details:

COMPLAINANT:
Name: {user_name}
Address: {user_address}
Phone: {user_phone}
Date: {today}

RESPONDENT/OPPOSITE PARTY:
Name: {respondent}
Address: {respondent_address}

SITUATION (in complainant's own words):
{situation}

APPLICABLE LAW:
{applicable_law}

LETTER RECIPIENT (who to address):
{letter_recipient}

RECOMMENDED ACTIONS from legal analysis:
{recommended_action}

Draft the complete formal complaint letter now:"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": LETTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.2, "num_predict": 1200},
    )

    letter = response["message"]["content"].strip()
    return letter


def generate_letter_stream(
    situation: str,
    user_name: str,
    user_address: str,
    user_phone: str,
    respondent: str,
    respondent_address: str,
    legal_analysis: dict,
):
    """Streaming version of generate_letter — yields tokens as they arrive."""
    import ollama
    from datetime import date

    today = date.today().strftime("%B %d, %Y")
    applicable_law = legal_analysis.get("applicable_law", "Relevant Indian law")
    letter_recipient = legal_analysis.get("letter_recipient", respondent)
    recommended_action = legal_analysis.get("recommended_action", "")

    prompt = f"""Draft a formal complaint letter with these details:

COMPLAINANT: {user_name}, {user_address}, Phone: {user_phone}, Date: {today}
RESPONDENT: {respondent}, {respondent_address}
SITUATION: {situation}
APPLICABLE LAW: {applicable_law}
LETTER RECIPIENT: {letter_recipient}
RECOMMENDED ACTIONS: {recommended_action}

Draft the complete formal complaint letter now:"""

    stream = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": LETTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.2, "num_predict": 1200},
        stream=True,
    )

    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            yield token


if __name__ == "__main__":
    # Quick test
    sample_analysis = {
        "applicable_law": "Payment of Wages Act 1936, Section 15 — Authority for hearing claims",
        "recommended_action": "1. File complaint before Payment of Wages Authority\n2. Attach salary slips and bank statements",
        "can_generate_letter": True,
        "letter_recipient": "The Authority under Payment of Wages Act, Office of Labour Commissioner",
    }

    letter = generate_letter(
        situation="My employer has not paid my salary for 3 months. I work as a security guard and my monthly salary is Rs. 12,000.",
        user_name="Ramesh Kumar",
        user_address="123 MG Road, Patna, Bihar - 800001",
        user_phone="9876543210",
        respondent="ABC Security Services Pvt Ltd",
        respondent_address="456 Industrial Area, Patna, Bihar - 800002",
        legal_analysis=sample_analysis,
    )

    print(letter)
