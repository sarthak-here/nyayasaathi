"""
NyayaSaathi — Demo Scenarios
5 realistic Indian legal aid test cases.
Run: python demo_scenarios.py [--scenario 1-5]
"""

import sys
import argparse
sys.path.insert(0, ".")

SCENARIOS = [
    {
        "id": 1,
        "title": "Wage Theft",
        "user_input": (
            "Main ek kapda factory mein kaam karta hoon Delhi mein. "
            "Mere malik ne pichle 3 mahine se meri salary nahi di — "
            "Rs. 11,500 per mahine thi meri pay. Woh bol raha hai company "
            "mein paisa nahi hai, lekin factory chal rahi hai. Mujhe kya karna chahiye?"
        ),
        "expected_law": "Payment of Wages Act 1936, Section 15",
        "expected_authority": "Labour Commissioner / Payment of Wages Authority",
        "sample_letter_recipient": "The Authority under Payment of Wages Act, Office of the Labour Commissioner",
    },
    {
        "id": 2,
        "title": "Domestic Violence",
        "user_input": (
            "My husband beats me and my children regularly. "
            "His mother and sister also harass me every day for dowry. "
            "Last week he threw me out of the house. I have a 5-year-old daughter. "
            "I have no money and nowhere to go. What legal help can I get immediately?"
        ),
        "expected_law": "Protection of Women from Domestic Violence Act 2005, Section 12",
        "expected_authority": "Protection Officer / Magistrate Court / Women Helpline 181",
        "sample_letter_recipient": "The Magistrate, Family Court",
    },
    {
        "id": 3,
        "title": "Consumer Fraud (E-commerce)",
        "user_input": (
            "Maine Flipkart se ek refrigerator kharida tha Rs. 28,000 mein. "
            "Delivery ke baad se hi cooling nahi ho rahi. Maine 4 baar complaint "
            "ki — company ka technician aaya, bol gaya 'manufacturing defect hai' "
            "lekin ab 2 mahine ho gaye na refund mila na replacement. "
            "Consumer court mein case kar sakta hoon kya?"
        ),
        "expected_law": "Consumer Protection Act 2019, Section 35 — District Consumer Disputes Redressal Commission",
        "expected_authority": "District Consumer Disputes Redressal Commission (DCDRC)",
        "sample_letter_recipient": "The President, District Consumer Disputes Redressal Commission",
    },
    {
        "id": 4,
        "title": "Caste Discrimination (SC/ST Atrocities)",
        "user_input": (
            "Hamare gaon ke sarpanch ne (jo upper caste se hai) hame (SC community) "
            "panchayat ki baithak mein andar aane se roka. Usne humari jaat ki gaali "
            "di aur bola 'tumhare jaisa neeche ka aadmi yahan nahi aa sakta'. "
            "Yeh sab log sab ke saamne hua. Police FIR likhne se mana kar rahi hai. "
            "Hume kya karna chahiye?"
        ),
        "expected_law": "SC/ST (Prevention of Atrocities) Act 1989, Section 3(1)(r) — Intentional insult in public",
        "expected_authority": "SP Office / Special Court / SC Commission",
        "sample_letter_recipient": "The Superintendent of Police",
    },
    {
        "id": 5,
        "title": "RTI Denial",
        "user_input": (
            "I filed an RTI application 45 days ago to the Municipal Corporation "
            "asking about the contractor who built our broken road and how much money "
            "was paid. The PIO has not replied at all. The 30-day deadline has passed. "
            "What are my options now and how do I file the first appeal?"
        ),
        "expected_law": "Right to Information Act 2005, Section 19(1) — First Appeal",
        "expected_authority": "First Appellate Authority (senior officer, same organization)",
        "sample_letter_recipient": "The First Appellate Authority, Municipal Corporation",
    },
]


def run_scenario(scenario: dict, stream: bool = True):
    """Run a single demo scenario through the full pipeline."""
    from core.legal_agent import LegalAgent
    from core.letter_generator import generate_letter
    from core.pdf_export import export_to_pdf

    print(f"\n{'='*70}")
    print(f"SCENARIO {scenario['id']}: {scenario['title'].upper()}")
    print(f"{'='*70}")
    print(f"\nUser Input:\n{scenario['user_input']}\n")
    print(f"Expected Law: {scenario['expected_law']}")
    print(f"{'─'*70}")

    agent = LegalAgent()

    if stream:
        print("\nStreaming Analysis:\n")
        full = ""
        for token in agent.analyze_stream(scenario["user_input"]):
            print(token, end="", flush=True)
            full += token
        print("\n")
    else:
        print("\nAnalyzing...")
        result = agent.analyze(scenario["user_input"])
        print(f"\nApplicable Law: {result.get('applicable_law', 'N/A')}")
        print(f"\nExplanation:\n{result.get('explanation', 'N/A')}")
        print(f"\nRecommended Actions:\n{result.get('recommended_action', 'N/A')}")

        if result.get("can_generate_letter"):
            print(f"\n{'─'*70}")
            print("Generating sample complaint letter...")
            letter = generate_letter(
                situation=scenario["user_input"],
                user_name="[Your Name]",
                user_address="[Your Address]",
                user_phone="[Your Phone]",
                respondent="[Opposite Party]",
                respondent_address="[Their Address]",
                legal_analysis=result,
            )
            print(f"\n{letter}")

            pdf_path = export_to_pdf(letter, user_name="Demo_User")
            print(f"\nPDF saved to: {pdf_path}")


def run_all_scenarios():
    for scenario in SCENARIOS:
        run_scenario(scenario, stream=False)
        input("\nPress Enter to continue to next scenario...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NyayaSaathi Demo Scenarios")
    parser.add_argument(
        "--scenario", type=int, choices=[1, 2, 3, 4, 5],
        help="Run a specific scenario (1-5)"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all scenarios"
    )
    parser.add_argument(
        "--stream", action="store_true", default=True,
        help="Stream output token by token"
    )
    args = parser.parse_args()

    if args.list:
        print("\nAvailable Demo Scenarios:")
        for s in SCENARIOS:
            print(f"  {s['id']}. {s['title']} — {s['expected_law']}")
    elif args.scenario:
        scenario = next(s for s in SCENARIOS if s["id"] == args.scenario)
        run_scenario(scenario, stream=args.stream)
    else:
        run_all_scenarios()
